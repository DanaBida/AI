"""Text helpers shared by future guardrail flows."""

from __future__ import annotations


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving the user's original wording."""
    return " ".join(text.split())
