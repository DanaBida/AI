"""HTTP controllers for the guardrails service."""

from __future__ import annotations

from fastapi import APIRouter

from models.guardrail_types import CheckRequest, CheckResponse, HealthResponse
from services.guardrails_service import GuardrailsService
from services.health_service import HealthService

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Return service liveness and runtime readiness details."""
    return HealthService.check_health()


@router.post("/check/input", response_model=CheckResponse, tags=["guardrails"])
async def check_input(request: CheckRequest):
    """Validate incoming listing text against the input rail set."""
    return await GuardrailsService.check_input(request)


@router.post("/check/output", response_model=CheckResponse, tags=["guardrails"])
async def check_output(request: CheckRequest):
    """Validate generated report text against the output rail set."""
    return await GuardrailsService.check_output(request)
