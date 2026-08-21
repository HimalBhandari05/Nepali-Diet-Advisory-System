import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from rapidfuzz import fuzz

from app.services.food_matching_service import FoodMatchingService

logger = logging.getLogger(__name__)


class TextFoodAnalysisService:
    """
    Service for text-based food analysis.
    Identifies food items from natural language user text, extracts consumption quantities,
    retrieves canonical food data from FoodMatchingService, and calculates aggregated nutritional totals.
    """

    def __init__(
        self,
        food_matching_service: Optional[FoodMatchingService] = None,
        default_plate_gram: float = 150.0,
    ):
        self.matching_service = (
            food_matching_service
            if food_matching_service is not None
            else FoodMatchingService()
        )
        self.default_plate_gram = default_plate_gram

        # Preload food dictionary and alias index from FoodMatchingService
        self.foods_data = self.matching_service.get_all_foods()

        self.alias_to_id: Dict[str, str] = {}
        self.all_aliases: List[str] = []

        for food_id, food_record in self.foods_data.items():
            other_names = food_record.get("other_names", [])
            for alias in other_names:
                norm_alias = str(alias).lower().strip()
                if norm_alias:
                    self.alias_to_id[norm_alias] = food_id
                    self.all_aliases.append(norm_alias)

        # Sort aliases by length descending so longer compound phrases match first
        self.all_aliases.sort(key=len, reverse=True)

    def _has_fuzzy_match(self, text: str, alias: str) -> bool:
        """Check if any token in the text matches the alias with high fuzzy similarity."""
        words = text.split()
        for word in words:
            if len(word) >= 3 and fuzz.ratio(word, alias) >= 82:
                return True
        return False

    def _extract_quantity_for_alias(
        self,
        sentence: str,
        alias: str,
        default_gram: float,
    ) -> Tuple[float, str]:
        """
        Extract numerical quantity and unit preceding a matched food alias.
        Supports grams, kilograms, plates, bowls, cups, and standalone numbers.
        """
        idx = sentence.find(alias)
        if idx == -1:
            idx = 0

        prefix = sentence[:idx].strip()
        words = prefix.split()
        lookback = " ".join(words[-3:]) if words else ""

        # 1. Exact weight (kg, g, gm, mg)
        kg_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilogram|kilograms)", lookback)
        if kg_match:
            return float(kg_match.group(1)) * 1000.0, "g"

        gram_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:gram|grams|gm|gms|g)\b", lookback)
        if gram_match:
            return float(gram_match.group(1)), "g"

        # 2. Plate / Bowl / Katora portions
        plate_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:plate|plates|katora|bowl|bowls)", lookback)
        if plate_match:
            return float(plate_match.group(1)) * default_gram, "g"

        # 3. Cup / Glass portions
        cup_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:cup|cups|glass|glasses|mug|mugs)", lookback)
        if cup_match:
            return float(cup_match.group(1)) * 200.0, "g"

        # 4. Piece / Roti portions
        piece_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:piece|pieces|slice|slices|roti|rotis)", lookback)
        if piece_match:
            return float(piece_match.group(1)) * 50.0, "g"

        # 5. Standalone number preceding food e.g. "2 bhat" -> 2 plates
        num_match = re.search(r"(\d+(?:\.\d+)?)\b", lookback)
        if num_match:
            return float(num_match.group(1)) * default_gram, "g"

        return default_gram, "g"

    def analyze(
        self,
        text: str,
        default_plate_gram: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a natural language food consumption sentence.

        Args:
            text: User input sentence describing foods eaten.
            default_plate_gram: Optional fallback gram weight per portion (default: 150.0g).

        Returns:
            Structured dictionary containing list of itemized foods with individual macros
            and total aggregated meal nutrition.
        """
        effective_default_gram = (
            default_plate_gram if default_plate_gram is not None else self.default_plate_gram
        )

        if not text or not str(text).strip():
            return {
                "foods": [],
                "total": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
            }

        sentence_clean = str(text).lower().strip()
        matched_foods: Dict[str, Dict[str, Any]] = {}

        # 1. Exact & Fuzzy matching across sentence substrings using alias index
        for alias in self.all_aliases:
            food_id = self.alias_to_id[alias]

            if food_id in matched_foods:
                continue

            if alias in sentence_clean or self._has_fuzzy_match(sentence_clean, alias):
                grams, unit = self._extract_quantity_for_alias(
                    sentence_clean, alias, effective_default_gram
                )
                matched_foods[food_id] = {
                    "matched_alias": alias,
                    "quantity": grams,
                    "unit": unit,
                }

        # 2. Fallback to ChromaDB vector search if no alias matched
        if not matched_foods:
            matches = self.matching_service.search_food(sentence_clean, k=1)
            if matches and matches[0]["score"] < 25.0:
                top_match = matches[0]
                matched_foods[top_match["id"]] = {
                    "matched_alias": top_match["name"],
                    "quantity": effective_default_gram,
                    "unit": "g",
                }

        # 3. Compute itemized and aggregated nutrition
        itemized_results: List[Dict[str, Any]] = []
        total_nutrition = {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
        }

        for food_id, match_info in matched_foods.items():
            # Retrieve canonical food record from preloaded cache or service lookup
            food_obj = self.foods_data.get(food_id) or self.matching_service.get_food_by_id(food_id)
            if not food_obj:
                continue

            grams = match_info["quantity"]
            macros = food_obj.get("nutrition_per_gram", {})

            item_cal = round(macros.get("calories", 0.0) * grams, 2)
            item_prot = round(macros.get("protein", 0.0) * grams, 2)
            item_carbs = round(macros.get("carbs", 0.0) * grams, 2)
            item_fat = round(macros.get("fat", 0.0) * grams, 2)

            total_nutrition["calories"] += item_cal
            total_nutrition["protein"] += item_prot
            total_nutrition["carbs"] += item_carbs
            total_nutrition["fat"] += item_fat

            itemized_results.append(
                {
                    "food_id": food_id,
                    "name": food_obj.get("name", food_id),
                    "matched_alias": match_info["matched_alias"],
                    "quantity": grams,
                    "unit": match_info["unit"],
                    "calories": item_cal,
                    "protein": item_prot,
                    "carbs": item_carbs,
                    "fat": item_fat,
                    "veg_or_nonveg": food_obj.get("veg_or_nonveg", ""),
                    "fitness_direction": food_obj.get("fitness_direction", ""),
                    "health_restrictions": food_obj.get("health_restrictions", {}),
                    "social_restrictions": food_obj.get("social_restrictions", {}),
                }
            )

        return {
            "foods": itemized_results,
            "total": {
                "calories": round(total_nutrition["calories"], 2),
                "protein": round(total_nutrition["protein"], 2),
                "carbs": round(total_nutrition["carbs"], 2),
                "fat": round(total_nutrition["fat"], 2),
            },
        }
