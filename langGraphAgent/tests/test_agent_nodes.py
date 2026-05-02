"""
Unit tests for PropertyAgent node behavior.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lib.langgraph_agent import PropertyAgent


class PropertyAgentNodeTests(unittest.TestCase):
    """Tests for planner, executor, and synthesizer behavior."""

    def setUp(self) -> None:
        self.agent = PropertyAgent()

    def test_planner_selects_both_tools_for_renovation_query(self) -> None:
        state = {"query": "What renovation is needed to improve condition?", "reasoning_steps": []}

        updated_state = self.agent._planner_node(state)

        self.assertIn("rag_search", updated_state["selected_tools"])
        self.assertIn("image_analysis", updated_state["selected_tools"])
        self.assertEqual(len(updated_state["reasoning_steps"]), 1)

    def test_executor_handles_selected_tool_results(self) -> None:
        state = {
            "query": "What is the condition of the kitchen?",
            "reasoning_steps": [],
            "selected_tools": ["image_analysis"],
        }

        updated_state = self.agent._executor_node(state)

        self.assertIn("image_analysis", updated_state["tool_results"])
        self.assertIn(
            "Photo-based condition analysis",
            updated_state["tool_results"]["image_analysis"]["summary"],
        )
        self.assertEqual(len(updated_state["reasoning_steps"]), 1)

    def test_synthesizer_combines_multi_tool_results(self) -> None:
        state = {
            "query": "What renovation work is needed?",
            "reasoning_steps": [],
            "selected_tools": ["rag_search", "image_analysis"],
            "tool_results": {
                "rag_search": {"summary": "Listing facts"},
                "image_analysis": {"summary": "Visible wear"},
            },
        }

        updated_state = self.agent._synthesizer_node(state)

        self.assertIn("listing retrieval", updated_state["final_answer"])
        self.assertEqual(len(updated_state["reasoning_steps"]), 1)

    def test_invoke_records_multiple_reasoning_steps(self) -> None:
        result = self.agent.invoke("Compare two properties by location and price.")

        self.assertGreaterEqual(len(result["reasoning_steps"]), 3)
        self.assertEqual(result["reasoning_steps"][0]["step_number"], 1)


if __name__ == "__main__":
    unittest.main()
