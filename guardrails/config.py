"""Centralized configuration for the guardrails service."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _get_env(name: str, default: str) -> str:
    """Read a string environment variable with surrounding whitespace removed."""
    return os.getenv(name, default).strip()


def _get_int_env(name: str, default: int) -> int:
    """Read an integer environment variable with a consistent error message."""
    raw_value = os.getenv(name, str(default))
    try:
        return int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Environment variable {name} must be an integer, got {raw_value!r}") from exc


def _get_bool_env(name: str, default: bool) -> bool:
    """Read a boolean environment variable from common true/false spellings."""
    raw_value = os.getenv(name, str(default)).strip().lower()
    if raw_value in {"1", "true", "yes", "on"}:
        return True
    if raw_value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Environment variable {name} must be a boolean, got {raw_value!r}")


class Config:
    """Single source of truth for environment-backed settings."""

    PROJECT_ROOT = Path(__file__).resolve().parent
    PROMPTS_DIR = PROJECT_ROOT / "prompts"
    RAILS_DIR = PROJECT_ROOT / "rails"
    TESTS_DIR = PROJECT_ROOT / "tests"

    APP_NAME = _get_env("APP_NAME", "guardrails-service")
    APP_ENV = _get_env("APP_ENV", "development")
    APP_HOST = _get_env("APP_HOST", "0.0.0.0")
    APP_PORT = _get_int_env("APP_PORT", 8011)
    LOG_LEVEL = _get_env("LOG_LEVEL", "INFO").upper()

    NEMO_MODEL_PROVIDER = _get_env("NEMO_MODEL_PROVIDER", "google")
    NEMO_MODEL_NAME = _get_env("NEMO_MODEL_NAME", "gemini-2.5-flash")
    NEMO_API_KEY = _get_env("NEMO_API_KEY", "")
    NEMO_API_BASE = _get_env("NEMO_API_BASE", "")
    NEMO_CONFIG_ROOT = _get_env("NEMO_CONFIG_ROOT", str(RAILS_DIR))
    INPUT_RAILS_DIR = _get_env("INPUT_RAILS_DIR", str(RAILS_DIR / "input"))
    OUTPUT_RAILS_DIR = _get_env("OUTPUT_RAILS_DIR", str(RAILS_DIR / "output"))

    PROMPT_TEST_FILE = _get_env("PROMPT_TEST_FILE", str(TESTS_DIR / "test_prompts.json"))
    PROMPT_LOG_FILE = _get_env("PROMPT_LOG_FILE", str(PROMPTS_DIR / "ENGINEERING_LOG.md"))

    INPUT_STRICT_MODE = _get_bool_env("INPUT_STRICT_MODE", True)
    OUTPUT_STRICT_MODE = _get_bool_env("OUTPUT_STRICT_MODE", True)
    NORMALIZE_SAFE_OUTPUT = _get_bool_env("NORMALIZE_SAFE_OUTPUT", True)


def validate_config() -> Config:
    """Validate configuration values and ensure expected local directories exist."""
    if Config.APP_PORT < 1:
        raise ValueError("APP_PORT must be a positive integer")

    Config.PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    Config.RAILS_DIR.mkdir(parents=True, exist_ok=True)
    Path(Config.INPUT_RAILS_DIR).mkdir(parents=True, exist_ok=True)
    Path(Config.OUTPUT_RAILS_DIR).mkdir(parents=True, exist_ok=True)
    Config.TESTS_DIR.mkdir(parents=True, exist_ok=True)

    return Config
