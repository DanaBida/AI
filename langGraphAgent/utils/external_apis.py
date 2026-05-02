"""
HTTP clients for RAG and Image Analyzer services.
"""
from __future__ import annotations

import logging

from config import Config


logger = logging.getLogger(__name__)


class ExternalAPIError(Exception):
    """Raised when an external service call fails."""


class RAGClient:
    @staticmethod
    def search(query: str, top_k: int = 3):
        try:
            import requests
        except ModuleNotFoundError as exc:
            raise ExternalAPIError("The 'requests' package is not installed.") from exc

        url = f"{Config.RAG_SERVICE_URL}/query"
        payload = {"description": query}
        try:
            logger.debug("Calling RAG service url=%s payload=%s", url, payload)
            response = requests.post(
                url,
                json=payload,
                timeout=Config.EXTERNAL_API_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            body = response.json()
            results = body.get("similar_listings", [])
            logger.info("RAG service returned %s results", len(results))
            return results[:top_k] if top_k > 0 else results
        except requests.RequestException as exc:
            raise ExternalAPIError(f"RAG service call failed: {exc}") from exc

class ImageAnalyzerClient:
    @staticmethod
    def analyze(image_url: str):
        try:
            import requests
        except ModuleNotFoundError as exc:
            raise ExternalAPIError("The 'requests' package is not installed.") from exc

        url = f"{Config.IMAGE_ANALYZER_URL}/analyse"
        payload = {"image_url": image_url}
        try:
            logger.debug("Calling image analyzer url=%s payload=%s", url, payload)
            response = requests.post(
                url,
                json=payload,
                timeout=Config.EXTERNAL_API_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            body = response.json()
            logger.info("Image analyzer returned keys=%s", list(body.keys()))
            return body
        except requests.RequestException as exc:
            raise ExternalAPIError(f"Image analyzer call failed: {exc}") from exc
