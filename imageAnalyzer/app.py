"""
FastAPI application entrypoint for the image analyzer service.
"""

from fastapi import FastAPI

from config import Config
from controllers.image_controller import router as image_router


app = FastAPI(title=Config.APP_NAME)
app.include_router(image_router)


@app.get("/")
def root():
    return {
        "service": Config.APP_NAME,
        "environment": Config.APP_ENV,
        "health_endpoint": "/health",
    }
