"""Utility helpers for local file handling."""

from pathlib import Path


def ensure_text_file(path: Path) -> Path:
    """Validate that the provided path points to a text file."""
    if path.suffix.lower() not in {".txt", ".md"}:
        raise ValueError(f"Unsupported text file type: {path.suffix}")
    return path
