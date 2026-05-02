"""Tests for Llama prompt composition helpers."""

from pathlib import Path
import sys
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

fake_requests = types.ModuleType("requests")
sys.modules.setdefault("requests", fake_requests)

from utils.llama_handler import build_prompt, generate_insight


class LlamaHandlerTests(unittest.TestCase):
    def test_build_prompt_contains_context_and_query(self):
        prompt = build_prompt(context="Property prop_001", query="Need a good match")
        self.assertIn("Property prop_001", prompt)
        self.assertIn("Need a good match", prompt)

    def test_generate_insight_uses_fallback_when_model_missing(self):
        insight = generate_insight(model=None, context="ctx", query="sample query")
        self.assertIn("sample query", insight)


if __name__ == "__main__":
    unittest.main()
