import os
import django
from fastapi import FastAPI
from pydantic import BaseModel
from api.routes.food import router as food_router

# point to the django settings module

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", ".settings")

app = FastAPI(
    title="Nepali Diet Advisory System",
    description="An AI-powered diet advisory system for Nepali users, providing personalized dietary recommendations based on user preferences and health data.",
    version="1.0.0",
)


@app.get("/health")
def read_root():
    return {
        "status": "healthy",
        "message": "The Nepali Diet Advisory System is running smoothly.",
    }


app.include_router(food_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
