"""FastAPI server for the RAG property listing service."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import Config, validate_config
from controllers.property_controller import router as property_router
from middlewares.logging_middleware import LoggingMiddleware
from services.query_service import preload_models


logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Validate configuration and warm critical dependencies on startup."""
    validate_config()
    preload_models()
    logger.info("RAG property listing service startup complete")
    yield
    logger.info("RAG property listing service shutdown complete")


app = FastAPI(
    title="RAG Property Listing Service",
    description="Retrieval-Augmented Generation for property market insights",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)
app.include_router(property_router)


@app.get("/", tags=["meta"])
async def root():
    """Return a small service metadata payload."""
    return {
        "service": "rag-property-listing-service",
        "status": "ready",
        "health_endpoint": "/health",
        "query_endpoint": "/query",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
    )
