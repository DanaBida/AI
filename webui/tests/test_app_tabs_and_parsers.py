"""Tests for app tab orchestration and listing URL parser helpers."""

from __future__ import annotations

import app


class _TabCtx:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_parse_image_urls_splits_and_trims() -> None:
    parsed = app._parse_image_urls(" https://a.jpg, ,https://b.jpg ,https://c.jpg ")
    assert parsed == ["https://a.jpg", "https://b.jpg", "https://c.jpg"]


def test_parse_uploaded_urls_supports_csv_and_newlines() -> None:
    payload = b"https://a.jpg,https://b.jpg\r\nhttps://c.jpg\n"
    parsed = app._parse_uploaded_urls(payload)
    assert parsed == ["https://a.jpg", "https://b.jpg", "https://c.jpg"]


def test_initialize_session_state_migrates_legacy_tuple_history(monkeypatch) -> None:
    monkeypatch.setattr(app.st, "session_state", {"chat_history": [("user", "hello"), ("assistant", "hi")]})

    app.initialize_session_state()

    assert app.st.session_state["chat_history"] == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]


def test_render_app_shell_calls_both_tabs(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(app.st, "title", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(app.st, "caption", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(app.st, "tabs", lambda _labels: (_TabCtx(), _TabCtx()))
    monkeypatch.setattr(app, "render_chat_tab", lambda: calls.append("chat"))
    monkeypatch.setattr(app, "render_listing_tab", lambda: calls.append("listing"))

    app.render_app_shell()

    assert calls == ["chat", "listing"]
