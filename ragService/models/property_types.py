"""Pydantic models for the RAG property listing service."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ListingResult(BaseModel):
    """Retrieved property listing result."""

    id: str
    price: int
    bedrooms: int
    bathrooms: float
    rooms: int
    location: str
    condition: str
    description: str
    distance: Optional[float] = None


class QueryRequest(BaseModel):
    """Request model for /query endpoint."""

    description: str = Field(..., min_length=10, description="Natural-language property description")


class QueryResponse(BaseModel):
    """Response model for /query endpoint."""

    similar_listings: List[ListingResult]
    insight: str


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""

    status: str
    embedding_model_loaded: bool
    chroma_db_initialized: bool
    llama_model_loaded: bool
    collection_count: int = 0
