"""Service helpers for prompt file selection and loading."""

from pathlib import Path

from config import Config


class PromptService:
    """Handles prompt file resolution for the assistant surface."""

    @classmethod
    def get_prompt_path(cls) -> Path:
        """Resolve the currently configured prompt file."""
        return Config.PROMPTS_DIR / (
            f"iteration_surface_{Config.DEFAULT_PROMPT_SURFACE}_{Config.DEFAULT_PROMPT_VERSION}.txt"
        )

    @classmethod
    def load_active_prompt(cls) -> str:
        """Load the active prompt text from disk."""
        return cls.get_prompt_path().read_text(encoding="utf-8").strip()
