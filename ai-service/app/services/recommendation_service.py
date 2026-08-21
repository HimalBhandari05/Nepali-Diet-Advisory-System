import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.schemas.recommendation import (
    RecommendationDetail,
    RecommendationRequest,
    RecommendationResponse,
)

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
DEFAULT_OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "300.0"))


class RecommendationService:
    """
    Orchestrates personalized dietary recommendation generation using a local Ollama LLM.
    Ensures prompt guardrails, strict JSON output compliance, and Pydantic schema validation.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.base_url = base_url or DEFAULT_OLLAMA_BASE_URL
        self.model_name = model_name or DEFAULT_OLLAMA_MODEL
        self.timeout = timeout or DEFAULT_OLLAMA_TIMEOUT

    def _build_prompt(self, req: RecommendationRequest) -> str:
        """Construct a compact, structured, culturally authentic prompt with strict nutritional constraints."""
        profile = req.user_profile
        prof_parts = []
        if profile:
            if profile.age:
                prof_parts.append(f"Age {profile.age}")
            if profile.fitness_goal:
                prof_parts.append(f"Goal: {profile.fitness_goal}")
            if profile.medical_conditions:
                prof_parts.append(f"Conditions: {', '.join(profile.medical_conditions)}")
            if profile.allergies:
                prof_parts.append(f"Allergies: {', '.join(profile.allergies)}")
            if profile.dietary_restrictions:
                prof_parts.append(f"Restrictions: {', '.join(profile.dietary_restrictions)}")
        prof_str = "; ".join(prof_parts) if prof_parts else "None"

        food_parts = []
        for item in req.food_items:
            warn = f" ({', '.join(item.health_warnings)})" if item.health_warnings else ""
            food_parts.append(f"{item.quantity_grams}g {item.name}{warn}")
        food_str = ", ".join(food_parts) if food_parts else "Meal items"

        tot = req.nutrition_summary
        tot_str = f"{tot.total_calories} kcal, {tot.total_protein}g P, {tot.total_carbs}g C, {tot.total_fats}g F"

        prompt = (
            f"Evaluate this Nepali meal: {food_str} (Total: {tot_str}). "
            f"User profile: {prof_str}. "
            f"Respond in JSON with keys: "
            f"overall_verdict (one of 'ALIGNED', 'MODERATELY_ALIGNED', 'NEEDS_IMPROVEMENT', 'RESTRICTED'), "
            f"summary (1 short sentence), "
            f"macro_assessment (calories_evaluation, protein_evaluation, carbs_evaluation, fats_evaluation), "
            f"health_and_dietary_alerts (list of {{\"type\": \"MEDICAL_RESTRICTION\"|\"GOAL_ALIGNMENT\", \"severity\": \"WARNING\"|\"INFO\", \"message\": \"short alert\"}}), "
            f"actionable_suggestions (list of 2 short strings for Nepali diet), "
            f"alternative_foods (list of 1 {{\"recommended_food\": \"food\", \"replaces\": \"food\", \"reason\": \"reason\"}}). "
            f"Be very concise."
        )
        return prompt

    def _clean_json_string(self, raw_text: str) -> str:
        """Strip markdown code blocks, extract valid JSON, and repair minor trailing truncation if needed."""
        text = raw_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        start_idx = text.find("{")
        if start_idx == -1:
            return text

        sub = text[start_idx:]

        # If already valid JSON
        try:
            json.loads(sub)
            return sub
        except Exception:
            pass

        # Try closing open quotes and brackets
        repaired = sub
        # Check unclosed quotes
        quotes_count = repaired.count('"') - repaired.count('\\"')
        if quotes_count % 2 != 0:
            repaired += '"'

        open_square = repaired.count("[") - repaired.count("]")
        open_curly = repaired.count("{") - repaired.count("}")

        for _ in range(max(0, open_square)):
            repaired += "]"
        for _ in range(max(0, open_curly)):
            repaired += "}"

        try:
            json.loads(repaired)
            return repaired
        except Exception:
            pass

        # Fallback to standard substring between first { and last }
        end_idx = text.rfind("}")
        if end_idx != -1 and end_idx > start_idx:
            return text[start_idx : end_idx + 1]

        return text

    async def generate_recommendation(
        self, request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Send formatted prompt to Ollama, parse JSON output, and return validated RecommendationResponse.
        """
        prompt = self._build_prompt(request)
        ollama_url = f"{self.base_url.rstrip('/')}/api/generate"

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 380,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(ollama_url, json=payload)
        except httpx.ConnectError as exc:
            logger.error(f"Cannot connect to Ollama at '{ollama_url}': {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Ollama service is unavailable at '{self.base_url}'. Ensure Ollama is running.",
            ) from exc
        except httpx.TimeoutException as exc:
            logger.error(f"Ollama request timed out after {self.timeout}s: {exc}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Ollama request timed out after {self.timeout} seconds.",
            ) from exc
        except Exception as exc:
            logger.error(f"Unexpected error communicating with Ollama: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error communicating with Ollama: {str(exc)}",
            ) from exc

        if response.status_code != 200:
            logger.error(f"Ollama returned status {response.status_code}: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Ollama returned error status {response.status_code}: {response.text}",
            )

        try:
            ollama_response = response.json()
            raw_response_text = ollama_response.get("response", "")
        except Exception as exc:
            logger.error(f"Failed to parse Ollama wrapper response: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to parse response from Ollama engine.",
            ) from exc

        cleaned_json_str = self._clean_json_string(raw_response_text)

        try:
            parsed_data = json.loads(cleaned_json_str)
        except json.JSONDecodeError as exc:
            logger.error(f"Model generated invalid JSON: {cleaned_json_str}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Model output is not valid JSON: {str(exc)}",
            ) from exc

        # Inject server-controlled metadata
        parsed_data["meal_id"] = request.meal_id
        parsed_data["model_name"] = self.model_name
        parsed_data["generated_at"] = datetime.now(timezone.utc).isoformat()

        # Handle overall_verdict formatting flexibility
        if "overall_verdict" in parsed_data:
            val = str(parsed_data["overall_verdict"]).upper().replace(" ", "_")
            if val in ["OPTIMAL", "ALIGNED", "MODERATELY_ALIGNED", "NEEDS_IMPROVEMENT", "RESTRICTED"]:
                parsed_data["overall_verdict"] = val
            elif "MODERATE" in val:
                parsed_data["overall_verdict"] = "MODERATELY_ALIGNED"
            elif "IMPROVE" in val or "POOR" in val or "HIGH" in val or "NOT" in val or "UNALIGNED" in val:
                parsed_data["overall_verdict"] = "NEEDS_IMPROVEMENT"
            elif "RESTRICT" in val:
                parsed_data["overall_verdict"] = "RESTRICTED"
            else:
                parsed_data["overall_verdict"] = "ALIGNED"

        try:
            recommendation_detail = RecommendationDetail.model_validate(parsed_data)
        except ValidationError as exc:
            logger.error(f"Recommendation schema validation error: {exc.errors()}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Model output does not match expected recommendation schema: {exc.errors()}",
            ) from exc

        return RecommendationResponse(
            success=True,
            recommendation=recommendation_detail,
        )
