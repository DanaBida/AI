"""Tests for prompt run logging (file-based, no network calls)."""

import json

from services.prompt_logging_service import PromptLoggingService


def test_log_chat_run_appends_jsonl(tmp_path, monkeypatch) -> None:
    """Logging should append a JSON object line without raising."""
    # Patch the private log path resolver to isolate filesystem writes.
    monkeypatch.setattr(PromptLoggingService, "_log_path", classmethod(lambda cls: tmp_path / "runs.jsonl"))

    PromptLoggingService.log_chat_run(
        system_prompt="system",
        user_message="user",
        assistant_reply="assistant",
        raw_response={"message": {"content": "assistant"}},
    )

    content = (tmp_path / "runs.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(content) == 1
    parsed = json.loads(content[0])
    assert parsed["user_message"] == "user"
    assert parsed["assistant_reply"] == "assistant"

