"""Query service for RAG property listing operations."""

from __future__ import annotations

import logging

from fastapi import HTTPException

from config import Config
from lib.chromadb_client import ChromaDBClient
from models.property_types import ListingResult, QueryRequest, QueryResponse
from utils.llama_handler import generate_insight, initialize_llama_model
from utils.retrieval import format_context

logger = logging.getLogger(__name__)

_db_client: ChromaDBClient | None = None
_llama_model = None


def get_db_client() -> ChromaDBClient:
    """Create and cache the ChromaDB client for query handling."""
    global _db_client
    if _db_client is None:
        _db_client = ChromaDBClient(
            db_path=Config.CHROMA_DB_PATH,
            collection_name=Config.CHROMA_COLLECTION_NAME,
            embedding_model_name=Config.EMBEDDING_MODEL,
            anonymized_telemetry=Config.CHROMA_ANONYMIZED_TELEMETRY,
        )
    return _db_client


def get_llama_model():
    """Create and cache the Llama model instance."""
    global _llama_model
    if _llama_model is None:
        _llama_model = initialize_llama_model(
            model_name=Config.LLAMA_MODEL_NAME,
            model_file=Config.LLAMA_MODEL_FILE,
        )
    return _llama_model


def preload_llama_model():
    """Warm the Llama model cache during app startup."""
    return get_llama_model()


def _map_listing_result(raw_result: dict) -> ListingResult:
    """Convert a Chroma search result into the API response model."""
    metadata = raw_result.get("metadata", {})
    return ListingResult(
        id=str(metadata.get("id", raw_result.get("id", ""))),
        price=int(metadata.get("price", 0)),
        bedrooms=int(metadata.get("bedrooms", 0)),
        bathrooms=float(metadata.get("bathrooms", 0)),
        rooms=int(metadata.get("rooms", 0)),
        location=str(metadata.get("location", "")),
        condition=str(metadata.get("condition", "")),
        description=str(metadata.get("description", raw_result.get("text", ""))),
        distance=raw_result.get("distance"),
    )


class QueryService:
    """Service for property query operations using RAG."""

    @staticmethod
    def query_properties(request: QueryRequest) -> QueryResponse:
        """
        Execute RAG pipeline for property queries.

        Args:
            request: Query request containing property description

        Returns:
            QueryResponse: Similar listings and AI-generated insights

        Raises:
            HTTPException: If query processing fails
        """
        try:
            db_client = get_db_client()
            retrieved_results = db_client.search(
                query_text=request.description,
                top_k=Config.TOP_K_LISTINGS,
            )
        except Exception as exc:
            logger.exception("Failed during vector retrieval")
            raise HTTPException(status_code=500, detail="Failed to retrieve similar properties") from exc

        similar_listings = [_map_listing_result(result) for result in retrieved_results]
        context = format_context(retrieved_results)

        try:
            insight = generate_insight(
                model=get_llama_model(),
                context=context,
                query=request.description,
            )
        except Exception as exc:
            logger.exception("Failed during insight generation")
            raise HTTPException(status_code=500, detail="Failed to generate property insight") from exc

        return QueryResponse(similar_listings=similar_listings, insight=insight)
