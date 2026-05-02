"""Health service for checking service status and component initialization."""

from __future__ import annotations

import logging

from config import Config
from lib.chromadb_client import ChromaDBClient
from models.property_types import HealthResponse
from utils.llama_handler import get_model_output_path

logger = logging.getLogger(__name__)

_db_client: ChromaDBClient | None = None


def get_db_client() -> ChromaDBClient:
    """Create and cache the ChromaDB client for service health checks."""
    global _db_client
    if _db_client is None:
        _db_client = ChromaDBClient(
            db_path=Config.CHROMA_DB_PATH,
            collection_name=Config.CHROMA_COLLECTION_NAME,
            embedding_model_name=Config.EMBEDDING_MODEL,
            anonymized_telemetry=Config.CHROMA_ANONYMIZED_TELEMETRY,
        )
    return _db_client


class HealthService:
    """Service for health check operations."""

    @staticmethod
    def check_health() -> HealthResponse:
        """
        Perform health check on all service components.

        Returns:
            HealthResponse: Status of all components
        """
        embedding_model_loaded = False
        chroma_db_initialized = False
        collection_count = 0

        try:
            db_client = get_db_client()
            embedding_model_loaded = db_client.embedding_model is not None
            collection_count = db_client.get_count()
            chroma_db_initialized = True
        except Exception:
            logger.exception("Health check failed while initializing ChromaDB components")

        llama_model_loaded = get_model_output_path(Config.LLAMA_MODEL_FILE).exists()
        status = "operational" if chroma_db_initialized else "degraded"

        return HealthResponse(
            status=status,
            embedding_model_loaded=embedding_model_loaded,
            chroma_db_initialized=chroma_db_initialized,
            llama_model_loaded=llama_model_loaded,
            collection_count=collection_count,
        )
