"""Pydantic models for guardrail request and response payloads."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class CheckRequest(BaseModel):
    """Request model shared by input and output validation endpoints."""

    text: str = Field(..., min_length=1, description="Text content to validate")


class GuardrailResult(BaseModel):
    """Internal result shape used between rail execution and API mapping."""

    passed: bool
    reason: str = ""
    safe_text: str = ""
    policy_hits: List[str] = Field(default_factory=list)


class CheckResponse(BaseModel):
    """Public response model shared by input and output validation endpoints."""

    model_config = ConfigDict(populate_by_name=True)

    pass_: bool = Field(..., alias="pass", description="Whether the content passed validation")
    reason: str = Field(default="", description="Explanation for a failed validation")
    safe_text: str = Field(default="", description="Sanitized text when applicable")


class HealthResponse(BaseModel):
    """Response model for the health endpoint."""

    status: str
    config_valid: bool
    runtime_initialized: bool
    input_rails_dir: str
    output_rails_dir: str
