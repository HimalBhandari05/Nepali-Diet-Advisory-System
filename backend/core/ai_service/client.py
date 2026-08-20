import httpx
import mimetypes

AI_SERVICE_URL = "http://localhost:8001"


def check_ai_service_health():
    """
    Check the health of the AI service.
    """
    try:
        response = httpx.get(
            f"{AI_SERVICE_URL}/health",
            timeout=5.0,
        )

        if response.status_code == 200:
            return {
                "response": response.json(),
                "status": "healthy",
                "message": "The AI service is accessible and healthy.",
            }

        return {
            "status": "unhealthy",
            "message": f"AI service returned status {response.status_code}.",
        }

    except httpx.RequestError:
        return {
            "status": "unhealthy",
            "message": "The AI service is not accessible.",
        }


def analyze_food(image_file):
    """
    Send a meal image to the AI service for food analysis.
    """

    content_type, _ = mimetypes.guess_type(image_file.name)

    if content_type is None:
        content_type = "application/octet-stream"

    response = httpx.post(
        f"{AI_SERVICE_URL}/api/food/analyze",
        files={
            "image": (
                image_file.name,
                image_file,
                content_type,
            )
        },
        timeout=60.0,
    )

    response.raise_for_status()

    return response.json()
