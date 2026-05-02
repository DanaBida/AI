"""Property controller for handling API endpoints."""

from fastapi import APIRouter

from models.property_types import HealthResponse, QueryRequest, QueryResponse
from services.health_service import HealthService
from services.query_service import QueryService


# Create router for property endpoints
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint - verify all components are initialized.

    Returns:
        HealthResponse: Status of service components
    """
    return HealthService.check_health()


@router.post("/query", response_model=QueryResponse)
async def query_properties(request: QueryRequest):
    """
    RAG Query Endpoint.

    Takes a property description and:
    1. Embeds the query
    2. Retrieves top-K similar properties from ChromaDB
    3. Generates insights using Llama.cpp

    Args:
        request: Property description query

    Returns:
        QueryResponse: Similar listings + AI-generated insight
    """
    return QueryService.query_properties(request)
