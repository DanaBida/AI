"""Gemini API handler utilities for RAG Service."""

from __future__ import annotations
import logging
from typing import Any, Optional

from config import Config
from lib.gemini_client import GeminiClient, GeminiAPIError

logger = logging.getLogger(__name__)

def get_gemini_model() -> GeminiClient:
    """Create and cache the Gemini client instance."""
    if not hasattr(get_gemini_model, "_client"):
        get_gemini_model._client = GeminiClient()
    return get_gemini_model._client

def generate_gemini_insight(
    model: Optional[GeminiClient],
    context: str,
    query: str,
    prompt_template: Optional[str] = None,
) -> str:
    """Generate an insight string from Gemini API, or fall back gracefully."""
    if model is None:
        return _fallback_insight(context=context, query=query)

    prompt = build_prompt(context=context, query=query, prompt_template=prompt_template)
    try:
        return model.call(prompt, temperature=0.2)
    except GeminiAPIError:
        logger.exception("Gemini inference failed; returning fallback insight")
        return _fallback_insight(context=context, query=query)

def build_prompt(context: str, query: str, prompt_template: Optional[str] = None) -> str:
    template = prompt_template or (
        "You are a real-estate analysis assistant.\n"
        "Use only the retrieved listings below.\n"
        "Do not invent facts.\n"
        "When making a claim, cite the property id.\n\n"
        "Retrieved listings:\n{context}\n\n"
        "User query:\n{query}\n\n"
        "Write a concise market insight with citations."
    )
    return template.format(context=context, query=query)

def _fallback_insight(context: str, query: str) -> str:
    del context
    return (
        "Model inference is currently unavailable, so this response is based on retrieved listing metadata only. "
        f"Relevant matches were found for: {query}"
    )
