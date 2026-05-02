"""Llama.cpp helper utilities with download and fallback support."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import requests

from config import Config

logger = logging.getLogger(__name__)


def get_model_output_path(model_file: str) -> Path:
    """Resolve the local model path inside the configured models directory."""
    return Config.MODELS_DIR / model_file


def build_prompt(context: str, query: str, prompt_template: Optional[str] = None) -> str:
    """Build the final prompt sent to the LLM."""
    template = prompt_template or (
        "You are a real-estate analysis assistant.\n"
        "Use only the retrieved listings below.\n"
        "Do not invent facts.\n"
        "When making a claim, cite the property id.\n\n"
        "Retrieved listings:\n{context}\n\n"
        "User query:\n{query}\n\n"
        "Write a concise market insight with citations."
    )
    return template.format(context=context, query=query)


def download_model_if_needed(model_name: str, model_file: str, output_path: Path) -> Path:
    """Download the configured GGUF model from Hugging Face when missing."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        logger.info("Using existing GGUF model at %s", output_path)
        return output_path

    download_url = f"https://huggingface.co/{model_name}/resolve/main/{model_file}"
    logger.info("Downloading GGUF model from %s", download_url)

    with requests.get(download_url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with output_path.open("wb") as model_file_handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    model_file_handle.write(chunk)

    logger.info("Downloaded GGUF model to %s", output_path)
    return output_path


def initialize_llama_model(model_name: str, model_file: str) -> Optional[Any]:
    """Initialize the Llama.cpp model, returning None when unavailable."""
    try:
        from llama_cpp import Llama
    except ImportError:
        logger.exception("llama-cpp-python is not available")
        return None

    model_path = get_model_output_path(model_file)
    try:
        download_model_if_needed(model_name, model_file, model_path)
    except Exception:
        logger.exception("Model download failed; insight generation will use fallback mode")
        return None

    try:
        return Llama(
            model_path=str(model_path),
            n_gpu_layers=Config.LLAMA_N_GPU_LAYERS,
            verbose=False,
        )
    except Exception:
        logger.exception("Failed to initialize Llama.cpp model from %s", model_path)
        return None


def _fallback_insight(context: str, query: str) -> str:
    """Generate a deterministic fallback response when Llama is unavailable."""
    del context
    return (
        "Model inference is currently unavailable, so this response is based on retrieved listing metadata only. "
        f"Relevant matches were found for: {query}"
    )


def generate_insight(
    model: Optional[Any],
    context: str,
    query: str,
    prompt_template: Optional[str] = None,
) -> str:
    """Generate an insight string from the LLM, or fall back gracefully."""
    if model is None:
        return _fallback_insight(context=context, query=query)

    prompt = build_prompt(context=context, query=query, prompt_template=prompt_template)

    try:
        response = model(
            prompt,
            max_tokens=256,
            temperature=0.2,
            stop=["</s>"],
        )
    except Exception:
        logger.exception("Llama inference failed; returning fallback insight")
        return _fallback_insight(context=context, query=query)

    choices = response.get("choices", [])
    if not choices:
        return _fallback_insight(context=context, query=query)

    text = choices[0].get("text", "").strip()
    return text or _fallback_insight(context=context, query=query)
