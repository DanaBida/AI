"""Lightweight run logging for prompt engineering traceability."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import Config
from services.prompt_service import PromptService


class PromptLoggingService:
    """Appends prompt-run events to a JSONL log under prompts/."""

    @classmethod
    def _log_path(cls) -> Path:
        surface = Config.DEFAULT_PROMPT_SURFACE
        return Config.PROMPTS_DIR / f"runs_surface_{surface}.jsonl"

    @classmethod
    def log_chat_run(
        cls,
        system_prompt: str,
        user_message: str,
        assistant_reply: str,
        raw_response: dict[str, Any],
    ) -> None:
        """Record one assistant run for later prompt engineering analysis."""
        event = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "surface": Config.DEFAULT_PROMPT_SURFACE,
            "prompt_version": Config.DEFAULT_PROMPT_VERSION,
            "prompt_path": str(PromptService.get_prompt_path()),
            "ollama_model": Config.OLLAMA_MODEL,
            "system_prompt_sha1": cls._sha1(system_prompt),
            "user_message": user_message,
            "assistant_reply": assistant_reply,
            "raw_response": raw_response,
        }

        log_path = cls._log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=True) + "\n")

    @classmethod
    def _sha1(cls, text: str) -> str:
        import hashlib

        return hashlib.sha1(text.encode("utf-8")).hexdigest()

