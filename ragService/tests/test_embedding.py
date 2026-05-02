"""Tests for embedding-related retrieval behavior."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.retrieval import format_context


class RetrievalFormattingTests(unittest.TestCase):
    def test_format_context_returns_fallback_for_empty_results(self):
        self.assertEqual(format_context([]), "No similar listings were retrieved.")

    def test_format_context_includes_property_metadata(self):
        results = [
            {
                "id": "prop_001",
                "metadata": {
                    "id": "prop_001",
                    "price": 2500000,
                    "rooms": 5,
                    "bedrooms": 3,
                    "bathrooms": 2,
                    "location": "Haifa Downtown",
                    "condition": "Good",
                    "description": "Sea views",
                },
            }
        ]

        context = format_context(results)
        self.assertIn("Property prop_001", context)
        self.assertIn("Haifa Downtown", context)


if __name__ == "__main__":
    unittest.main()
