"""Tests for prompt file resolution."""

from services.prompt_service import PromptService


def test_get_prompt_path_points_to_existing_v1_prompt() -> None:
    """The default configured prompt should exist in the prompts directory."""
    assert PromptService.get_prompt_path().exists()
