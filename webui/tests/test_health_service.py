"""Tests for basic service health metadata."""

from services.health_service import HealthService


def test_health_service_returns_ok_status() -> None:
    """Health metadata should expose the expected baseline state."""
    payload = HealthService.get_status()

    assert payload["status"] == "ok"
    assert payload["service"] == "webui"
