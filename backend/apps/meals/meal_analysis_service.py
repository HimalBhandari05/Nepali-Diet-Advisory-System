from core.ai_service.client import analyze_food


def analyze_meal_image(meal):

    if not meal.image:
        raise ValueError("Meal does not have an image.")

    with meal.image.open("rb") as image_file:
        return analyze_food(image_file)
