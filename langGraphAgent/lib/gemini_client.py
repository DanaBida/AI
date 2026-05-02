"""
Gemini API wrapper for LangGraph Agent.
"""
from __future__ import annotations

import logging
import time

from config import Config


logger = logging.getLogger(__name__)


class GeminiAPIError(Exception):
    """Raised when the Gemini API call fails."""


class GeminiClient:
    """Thin wrapper around the Gemini generateContent endpoint."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.base_url = (
            f"{Config.GEMINI_BASE_URL.rstrip('/')}/"
            f"{Config.GEMINI_MODEL}:generateContent"
        )

    def call(self, prompt: str, temperature: float = 0.7) -> str:
        if not self.api_key:
            raise GeminiAPIError("Gemini API key is not configured.")
        try:
            import requests
        except ModuleNotFoundError as exc:
            raise GeminiAPIError("The 'requests' package is not installed.") from exc

        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }

        logger.debug("Gemini prompt: %s", prompt)
        for attempt in range(3):
            started_at = time.perf_counter()
            response = requests.post(
                self.base_url,
                params=params,
                json=data,
                headers=headers,
                timeout=15,
            )
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.debug(
                "Gemini response status=%s attempt=%s elapsed_ms=%.2f",
                response.status_code,
                attempt + 1,
                elapsed_ms,
            )
            if response.status_code == 429 and attempt < 2:
                time.sleep(0.25 * (attempt + 1))
                continue
            if not response.ok:
                raise GeminiAPIError(
                    f"Gemini API error: {response.status_code} {response.text}"
                )

            payload = response.json()
            logger.debug("Gemini payload: %s", payload)
            return (
                payload.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )

        raise GeminiAPIError("Gemini API failed after 3 attempts.")
