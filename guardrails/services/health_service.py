"""Health checks for the guardrails service."""

from __future__ import annotations

from config import Config
from lib.nemo_guardrails_client import NeMoGuardrailsClient
from models.guardrail_types import HealthResponse


class HealthService:
    """Service for liveness and runtime readiness checks."""

    @staticmethod
    def check_health() -> HealthResponse:
        """Report whether config is valid and the runtime wrapper is initialized."""
        runtime_status = NeMoGuardrailsClient.get_status()
        return HealthResponse(
            status="operational" if runtime_status["runtime_initialized"] else "degraded",
            config_valid=True,
            runtime_initialized=runtime_status["runtime_initialized"],
            input_rails_dir=Config.INPUT_RAILS_DIR,
            output_rails_dir=Config.OUTPUT_RAILS_DIR,
        )
