from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from services.yolo_service import YOLOService
from services.quantity_service import QuantityService
from io import BytesIO
from PIL import Image

router = APIRouter(prefix="/api/food", tags=["Food"])

# Initialize the YOLOService and QuantityService instances
yolo_service = YOLOService()
quantity_service = QuantityService()


@router.post("/analyze")
async def analyze_food(image: UploadFile = File(...)):
    image_bytes = await image.read()

    pil_image = Image.open(BytesIO(image_bytes)).convert("RGB")

    image_width, image_height = pil_image.size

    detections = yolo_service.analyze(pil_image)

    foods = []

    for detection in detections:
        weight = quantity_service.estimate_weight(
            mask=detection["mask"],
            food_name=detection["name"],
            image_width=image_width,
            image_height=image_height,
        )

        foods.append(
            {
                "name": detection["name"],
                "confidence": detection["confidence"],
                "estimated_weight_g": round(weight, 2),
            }
        )

    return {
        "success": True,
        "foods": foods,
    }
