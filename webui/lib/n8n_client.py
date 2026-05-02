"""n8n webhook client wrapper used by the WebUI service."""

from __future__ import annotations

from typing import Any

import requests

from config import Config


class N8NClient:
    """Client for posting listing submissions to an n8n webhook."""

    def __init__(
        self,
        webhook_url: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self._webhook_url = webhook_url or Config.N8N_WEBHOOK_URL
        self._timeout_seconds = timeout_seconds or Config.REQUEST_TIMEOUT_SECONDS

    def submit_listing(
        self,
        agent_name: str,
        listing_description: str,
        image_urls: list[str],
    ) -> dict[str, Any]:
        """Submit listing metadata to n8n and return the JSON response."""
        payload = {
            "agent_name": agent_name,
            "listing_description": listing_description,
            "image_urls": image_urls,
        }

        resp = requests.post(
            self._webhook_url,
            json=payload,
            timeout=self._timeout_seconds,
        )
        resp.raise_for_status()
        return resp.json()
