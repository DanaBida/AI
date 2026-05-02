
"""
Image analysis endpoints: POST /analyse, GET /health
"""

from fastapi import APIRouter, HTTPException
from models.image_types import ImageAnalysisRequest, ImageAnalysisResponse
from services.image_service import ImageService

router = APIRouter()

@router.get("/health")
def health_check():
	return {"status": "ok"}

@router.post("/analyse", response_model=ImageAnalysisResponse)
def analyse_image(request: ImageAnalysisRequest):
	try:
		return ImageService.analyse(request.image_url)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
