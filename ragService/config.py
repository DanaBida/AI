"""Centralized configuration for the RAG property listing service."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _get_env(name: str, default: str) -> str:
    """Read a string environment variable with whitespace trimmed."""
    return os.getenv(name, default).strip()


def _get_int_env(name: str, default: int) -> int:
    """Read an integer environment variable with a helpful error message."""
    raw_value = os.getenv(name, str(default))
    try:
        return int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Environment variable {name} must be an integer, got {raw_value!r}") from exc


def _get_bool_env(name: str, default: bool) -> bool:
    """Read a boolean environment variable from common true/false spellings."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(
        f"Environment variable {name} must be a boolean value, got {raw_value!r}"
    )


class Config:
    """Single source of truth for all environment-backed settings."""

    PROJECT_ROOT = Path(__file__).resolve().parent
    DATA_DIR = PROJECT_ROOT / "data"
    PROMPTS_DIR = PROJECT_ROOT / "prompts"
    MODELS_DIR = PROJECT_ROOT / "artifacts" / "models"
    DEFAULT_CHROMA_PATH = PROJECT_ROOT / "artifacts" / "chroma_db"

    # Llama.cpp configuration.
    LLAMA_MODEL_NAME = _get_env(
        "LLAMA_MODEL_NAME",
        "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
    )
    LLAMA_MODEL_FILE = _get_env(
        "LLAMA_MODEL_FILE",
        "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    )
    LLAMA_N_GPU_LAYERS = _get_int_env("LLAMA_N_GPU_LAYERS", 0)

    # ChromaDB configuration.
    CHROMA_DB_PATH = _get_env("CHROMA_DB_PATH", str(DEFAULT_CHROMA_PATH))
    CHROMA_COLLECTION_NAME = _get_env("CHROMA_COLLECTION_NAME", "properties")
    CHROMA_ANONYMIZED_TELEMETRY = _get_bool_env("CHROMA_ANONYMIZED_TELEMETRY", False)

    # Embedding and retrieval configuration.
    EMBEDDING_MODEL = _get_env("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    TOP_K_LISTINGS = _get_int_env("TOP_K_LISTINGS", 3)

    # Gemini API configuration.
    GEMINI_API_KEY = _get_env("GEMINI_API_KEY", "")
    GEMINI_BASE_URL = _get_env("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/models")
    GEMINI_MODEL = _get_env("GEMINI_MODEL", "gemini-pro")

    # LLM Provider selection: "gemini" or "llama"
    LLM_PROVIDER = _get_env("LLM_PROVIDER", "gemini").lower()

    # Server configuration.
    SERVER_HOST = _get_env("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = _get_int_env("SERVER_PORT", 8001)
    LOG_LEVEL = _get_env("LOG_LEVEL", "INFO").upper()


def validate_config() -> Config:
    """Validate the configuration and create required local directories."""
    if Config.TOP_K_LISTINGS < 1:
        raise ValueError("TOP_K_LISTINGS must be at least 1")

    if Config.SERVER_PORT < 1:
        raise ValueError("SERVER_PORT must be a positive integer")

    Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    Config.PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    Config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    Path(Config.CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)

    logger.info("Configuration validated")
    logger.info("ChromaDB path: %s", Config.CHROMA_DB_PATH)
    logger.info("ChromaDB anonymized telemetry enabled: %s", Config.CHROMA_ANONYMIZED_TELEMETRY)
    logger.info("Embedding model: %s", Config.EMBEDDING_MODEL)
    logger.info("LLM Provider: %s", Config.LLM_PROVIDER)
    if Config.LLM_PROVIDER == "llama":
        logger.info("Llama model: %s/%s", Config.LLAMA_MODEL_NAME, Config.LLAMA_MODEL_FILE)
    else:
        logger.info("Gemini model: %s", Config.GEMINI_MODEL)
    logger.info("Top-K retrievals: %s", Config.TOP_K_LISTINGS)

    return Config
