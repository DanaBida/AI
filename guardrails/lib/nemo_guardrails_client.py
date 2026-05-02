"""Wrapper for NeMo Guardrails runtime initialization and execution."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

from config import Config
from lib.google_genai_chat_model import GoogleGenAIChatModel
from models.guardrail_types import GuardrailResult

logger = logging.getLogger(__name__)


class NeMoGuardrailsClient:
    """Single-purpose wrapper around NeMo Guardrails configuration loading and execution."""

    _initialized = False
    _import_error = ""
    _clients: Dict[str, Any] = {}
    _config_paths = {
        "input": Path(Config.INPUT_RAILS_DIR),
        "output": Path(Config.OUTPUT_RAILS_DIR),
    }

    @classmethod
    def initialize(cls) -> None:
        """Prepare rail configs and record whether the runtime can be used."""
        cls._write_runtime_configs()
        cls._apply_provider_environment()

        try:
            import nemoguardrails  # noqa: F401
        except ImportError as exc:
            cls._initialized = False
            cls._import_error = str(exc)
            logger.warning("NeMo Guardrails runtime unavailable: %s", exc)
            return

        cls._initialized = True
        cls._import_error = ""

    @classmethod
    def is_initialized(cls) -> bool:
        """Return whether the runtime wrapper has been initialized."""
        return cls._initialized

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Return a small runtime health snapshot."""
        return {
            "runtime_initialized": cls._initialized,
            "import_error": cls._import_error,
            "configured_paths": {name: str(path) for name, path in cls._config_paths.items()},
        }

    @classmethod
    async def evaluate_input(cls, text: str, strict_mode: bool) -> GuardrailResult:
        """Execute the input validation rail set."""
        if not text:
            return GuardrailResult(
                passed=False,
                reason="Input text is required.",
                safe_text="",
                policy_hits=["empty_input"],
            )
        return await cls._execute_rail(
            rail_name="input",
            text=text,
            strict_mode=strict_mode,
            fallback_safe_text="",
        )

    @classmethod
    async def evaluate_output(
        cls,
        text: str,
        strict_mode: bool,
        normalize_safe_output: bool,
    ) -> GuardrailResult:
        """Execute the output validation rail set."""
        if not text:
            return GuardrailResult(
                passed=False,
                reason="Output text is required.",
                safe_text="",
                policy_hits=["empty_output"],
            )

        result = await cls._execute_rail(
            rail_name="output",
            text=text,
            strict_mode=strict_mode,
            fallback_safe_text=text if normalize_safe_output else "",
        )

        if result.passed and normalize_safe_output and not result.safe_text:
            result.safe_text = text

        return result

    @classmethod
    async def _execute_rail(
        cls,
        rail_name: str,
        text: str,
        strict_mode: bool,
        fallback_safe_text: str,
    ) -> GuardrailResult:
        """Run one rail set and parse the JSON response contract."""
        if not cls._initialized:
            return GuardrailResult(
                passed=not strict_mode,
                reason="NeMo Guardrails runtime is not available." if strict_mode else "",
                safe_text="" if strict_mode else fallback_safe_text,
                policy_hits=["runtime_unavailable"] if strict_mode else [],
            )

        try:
            raw_response = await cls.run(rail_name, {"text": text})
            result = cls._parse_result(raw_response)
        except Exception as exc:
            logger.exception("Guardrails execution failed for %s rail", rail_name)
            return GuardrailResult(
                passed=not strict_mode,
                reason=f"Guardrails execution failed: {exc}" if strict_mode else "",
                safe_text="" if strict_mode else fallback_safe_text,
                policy_hits=["runtime_error"] if strict_mode else [],
            )

        if result.passed and not result.safe_text and fallback_safe_text:
            result.safe_text = fallback_safe_text

        return result

    @classmethod
    async def run(cls, rail_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run a configured NeMo rail set against the supplied payload."""
        rails = cls._get_rails_client(rail_name)
        response = await rails.generate_async(
            messages=[{"role": "user", "content": payload["text"]}],
        )
        return response

    @classmethod
    def _get_rails_client(cls, rail_name: str):
        """Load and cache an `LLMRails` instance for a rail set."""
        if rail_name in cls._clients:
            return cls._clients[rail_name]

        from nemoguardrails import LLMRails, RailsConfig

        config = RailsConfig.from_path(str(cls._config_paths[rail_name]))
        llm = cls._build_llm()
        rails = LLMRails(config, llm=llm, verbose=False) if llm is not None else LLMRails(config, verbose=False)
        cls._clients[rail_name] = rails
        return rails

    @classmethod
    def _build_llm(cls):
        """Build an optional provider-specific chat model for NeMo to use."""
        provider = Config.NEMO_MODEL_PROVIDER.lower()

        if provider == "google":
            return GoogleGenAIChatModel(
                model=Config.NEMO_MODEL_NAME,
                api_key=Config.NEMO_API_KEY or None,
                api_base=Config.NEMO_API_BASE or None,
            )

        return None

    @classmethod
    def _apply_provider_environment(cls) -> None:
        """Project config-backed credentials into provider env vars expected by SDKs."""
        if Config.NEMO_MODEL_PROVIDER.lower() == "google" and Config.NEMO_API_KEY:
            os.environ["GOOGLE_API_KEY"] = Config.NEMO_API_KEY
            os.environ["GEMINI_API_KEY"] = Config.NEMO_API_KEY

    @classmethod
    def _write_runtime_configs(cls) -> None:
        """Render provider-aware config files from checked-in templates."""
        replacements = {
            "__ENGINE__": "openai",
            "__MODEL__": "gpt-4o-mini",
        }

        for path in cls._config_paths.values():
            template_path = path / "config.template.yml"
            output_path = path / "config.yml"
            if not template_path.exists():
                continue

            rendered = template_path.read_text(encoding="utf-8")
            for placeholder, value in replacements.items():
                rendered = rendered.replace(placeholder, value)
            output_path.write_text(rendered, encoding="utf-8")

    @classmethod
    def _parse_result(cls, raw_response: Any) -> GuardrailResult:
        """Parse the JSON result returned by the rail set."""
        content = cls._extract_content(raw_response)
        cleaned = content.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").replace("json\n", "", 1).strip()

        parsed = json.loads(cleaned)
        policy_hits = parsed.get("policy_hits") or []
        if not isinstance(policy_hits, list):
            policy_hits = [str(policy_hits)]

        return GuardrailResult(
            passed=bool(parsed.get("passed")),
            reason=str(parsed.get("reason", "")),
            safe_text=str(parsed.get("safe_text", "")),
            policy_hits=[str(item) for item in policy_hits],
        )

    @classmethod
    def _extract_content(cls, raw_response: Any) -> str:
        """Extract assistant text content from common NeMo response shapes."""
        if isinstance(raw_response, dict):
            if "content" in raw_response and isinstance(raw_response["content"], str):
                return raw_response["content"]
            if "messages" in raw_response and raw_response["messages"]:
                last_message = raw_response["messages"][-1]
                return str(last_message.get("content", ""))

        if hasattr(raw_response, "content"):
            return str(raw_response.content)

        return str(raw_response)
