"""Service layer for mapping guardrail decisions to the public API contract."""

from __future__ import annotations

from config import Config
from lib.nemo_guardrails_client import NeMoGuardrailsClient
from models.guardrail_types import CheckRequest, CheckResponse, GuardrailResult
from utils.text_normalizer import normalize_text


def _map_result(result: GuardrailResult) -> CheckResponse:
    """Translate the internal result object into the public response model."""
    return CheckResponse(
        pass_=result.passed,
        reason=result.reason,
        safe_text=result.safe_text,
    )


class GuardrailsService:
    """Thin service facade for guardrail execution."""

    @staticmethod
    async def check_input(request: CheckRequest) -> CheckResponse:
        """Validate input text through the NeMo input rail configuration."""
        result = await NeMoGuardrailsClient.evaluate_input(
            text=normalize_text(request.text),
            strict_mode=Config.INPUT_STRICT_MODE,
        )
        return _map_result(result)

    @staticmethod
    async def check_output(request: CheckRequest) -> CheckResponse:
        """Validate generated output through the NeMo output rail configuration."""
        result = await NeMoGuardrailsClient.evaluate_output(
            text=normalize_text(request.text),
            strict_mode=Config.OUTPUT_STRICT_MODE,
            normalize_safe_output=Config.NORMALIZE_SAFE_OUTPUT,
        )
        return _map_result(result)
