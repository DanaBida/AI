"""Simple service-level health metadata for the WebUI."""


class HealthService:
    """Provides lightweight service metadata for diagnostics."""

    @classmethod
    def get_status(cls) -> dict:
        """Return a minimal health payload for local diagnostics."""
        return {
            "status": "ok",
            "service": "webui",
            "phase": 1,
        }
