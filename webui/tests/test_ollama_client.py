"""Tests for the Ollama client wrapper (no real HTTP calls)."""

from lib.ollama_client import OllamaClient


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_chat_parses_message_content(monkeypatch) -> None:
    """Ollama /api/chat content should be read from data['message']['content']."""

    def fake_post(url, json, timeout):
        assert url.endswith("/api/chat")
        assert json["stream"] is False
        return _FakeResponse({"message": {"role": "assistant", "content": "hello"}})

    import requests

    monkeypatch.setattr(requests, "post", fake_post)

    client = OllamaClient(host="http://127.0.0.1", port=11434, model="llama3", chat_endpoint="/api/chat", timeout_seconds=1)
    result = client.chat(system_prompt="sys", user_message="hi")
    assert result.content == "hello"

