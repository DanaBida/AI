# Pydantic models for image analysis requests/responses

"""
Pydantic models for image analysis requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, HttpUrl, Field

class ImageAnalysisRequest(BaseModel):
	"""Request model for image analysis endpoint."""
	image_url: HttpUrl = Field(..., description="URL of the image to analyze.")

class ImageAnalysisResponse(BaseModel):
	"""Response model for image analysis endpoint."""
	room_type: str = Field(..., description="Predicted room type or 'uncertain'.")
	condition_score: Optional[int] = Field(None, description="Predicted condition score (1-5) or null if uncertain.")
	confidence: float = Field(..., description="Model confidence score (0-1).")
