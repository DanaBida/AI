"""Centralized configuration for the WebUI service."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


class Config:
    """Single source of truth for WebUI environment configuration."""

    BASE_DIR = BASE_DIR
    PROMPTS_DIR = BASE_DIR / "prompts"
    TESTS_DIR = BASE_DIR / "tests"

    APP_TITLE = os.getenv("WEBUI_APP_TITLE", "aiPropertyTriage WebUI")
    STREAMLIT_HOST = os.getenv("WEBUI_HOST", "0.0.0.0")
    STREAMLIT_PORT = int(os.getenv("WEBUI_SERVER_PORT", "8501"))
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("WEBUI_REQUEST_TIMEOUT_SECONDS", "60"))

    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1")
    OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_CHAT_ENDPOINT = os.getenv("OLLAMA_CHAT_ENDPOINT", "/api/chat")

    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://127.0.0.1:5678/webhook/listing-triage")

    DEFAULT_PROMPT_SURFACE = int(os.getenv("PROMPT_SURFACE", "1"))
    DEFAULT_PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1")

    WEBUI_TABS = (
        "Conversational Assistant",
        "Listing Submission",
    )
