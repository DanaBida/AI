"""FastAPI entrypoint for the guardrails service."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import Config, validate_config
from controllers.guardrail_controller import router as guardrail_router
from lib.nemo_guardrails_client import NeMoGuardrailsClient

logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Validate configuration when the application starts."""
    validate_config()
    NeMoGuardrailsClient.initialize()
    logger.info("Guardrails service startup complete")
    yield
    logger.info("Guardrails service shutdown complete")


app = FastAPI(
    title=Config.APP_NAME,
    description="Input and output safety checks for property-listing workflows",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(guardrail_router)


@app.get("/", tags=["meta"])
async def root():
    """Return small metadata for local smoke checks."""
    return {
        "service": Config.APP_NAME,
        "status": "ready",
        "health_endpoint": "/health",
        "input_endpoint": "/check/input",
        "output_endpoint": "/check/output",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=Config.APP_HOST,
        port=Config.APP_PORT,
    )
