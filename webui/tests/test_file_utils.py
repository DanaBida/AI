"""Tests for utility helper functions."""

from pathlib import Path

import pytest

from utils.file_utils import ensure_text_file


def test_ensure_text_file_accepts_txt_and_md() -> None:
    assert ensure_text_file(Path("notes.txt")) == Path("notes.txt")
    assert ensure_text_file(Path("README.md")) == Path("README.md")


def test_ensure_text_file_rejects_other_extensions() -> None:
    with pytest.raises(ValueError):
        ensure_text_file(Path("image.png"))
