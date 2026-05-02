"""Contract tests for the Phase 1 guardrails scaffold."""

from __future__ import annotations

from config import Config, validate_config
from models.guardrail_types import CheckRequest, CheckResponse


def test_check_request_requires_text():
    """The shared request model should preserve the public text field."""
    payload = CheckRequest(text="Sample property listing")
    assert payload.text == "Sample property listing"


def test_check_response_uses_public_pass_field():
    """The response model should serialize the public pass field name."""
    payload = CheckResponse(pass_=True, reason="", safe_text="")
    assert payload.model_dump(by_alias=True)["pass"] is True


def test_validate_config_creates_expected_paths():
    """Config validation should succeed with the default development settings."""
    validated = validate_config()
    assert validated.APP_NAME == Config.APP_NAME
