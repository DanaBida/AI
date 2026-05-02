"""Pydantic models for the listing submission surface."""

from typing import List

from pydantic import BaseModel, Field


class ListingSubmissionRequest(BaseModel):
    """Validated payload for a listing triage submission."""

    agent_name: str = Field(..., min_length=1)
    listing_description: str = Field(..., min_length=1)
    image_urls: List[str] = Field(default_factory=list)


class ListingImageScore(BaseModel):
    """Per-image scoring details returned by the triage workflow."""

    image_url: str = Field(default="")
    score: float | None = None
    reason: str = Field(default="")


class ListingRecommendation(BaseModel):
    """Structured recommendation returned by the triage workflow."""

    summary: str = Field(default="No summary returned.")
    recommendations: List[str] = Field(default_factory=list)
    image_scores: List[ListingImageScore] = Field(default_factory=list)
