"""Utilities for formatting retrieved property listings into LLM context."""

from __future__ import annotations

from typing import Dict, List


def format_context(retrieved_listings: List[Dict]) -> str:
    """Convert retrieved listings into a deterministic prompt context string."""
    if not retrieved_listings:
        return "No similar listings were retrieved."

    context_lines = []
    for index, listing in enumerate(retrieved_listings, start=1):
        metadata = listing.get("metadata", {})
        context_lines.append(
            (
                f"{index}. Property {metadata.get('id', listing.get('id', 'unknown'))}: "
                f"price {metadata.get('price', 'unknown')}, "
                f"rooms {metadata.get('rooms', 'unknown')}, "
                f"bedrooms {metadata.get('bedrooms', 'unknown')}, "
                f"bathrooms {metadata.get('bathrooms', 'unknown')}, "
                f"location {metadata.get('location', 'unknown')}, "
                f"condition {metadata.get('condition', 'unknown')}. "
                f"Description: {metadata.get('description', listing.get('text', ''))}"
            )
        )

    return "\n".join(context_lines)
