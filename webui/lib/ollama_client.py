"""Ollama HTTP client wrapper used by the WebUI service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from config import Config


@dataclass(frozen=True)
class OllamaChatResult:
    """Structured chat result returned by the Ollama client."""

    content: str
    raw: dict[str, Any]


class OllamaClient:
    """Client for interacting with a local Ollama server via its HTTP API."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        model: str | None = None,
        chat_endpoint: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self._host = host or Config.OLLAMA_HOST
        self._port = port or Config.OLLAMA_PORT
        self._model = model or Config.OLLAMA_MODEL
        self._chat_endpoint = chat_endpoint or Config.OLLAMA_CHAT_ENDPOINT
        self._timeout_seconds = timeout_seconds or Config.REQUEST_TIMEOUT_SECONDS

        base = self._host.rstrip("/")
        self._base_url = f"{base}:{self._port}"

    def chat(self, system_prompt: str, user_message: str) -> OllamaChatResult:
        """Send a single-turn chat request to Ollama and return the assistant message."""
        url = f"{self._base_url}{self._chat_endpoint}"
        payload = {
            "model": self._model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }

        resp = requests.post(url, json=payload, timeout=self._timeout_seconds)
        resp.raise_for_status()

        data = resp.json()
        # Ollama /api/chat returns {"message": {"role": "...", "content": "..."}, ...}
        content = (data.get("message") or {}).get("content") or ""
        if not content.strip():
            content = "[No response]"

        return OllamaChatResult(content=content, raw=data)
