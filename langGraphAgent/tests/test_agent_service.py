"""
Unit tests for AgentService.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from models.agent_types import AgentResponse
from services.agent_service import AgentService


class AgentServiceTests(unittest.TestCase):
    """Tests for service-level validation and response shaping."""

    def test_run_agent_returns_agent_response(self) -> None:
        mocked_result = {
            "final_answer": "Grounded answer",
            "tools_used": ["rag_search"],
            "reasoning_steps": [
                {
                    "step_number": 1,
                    "description": "Planner selected tools.",
                    "tool_used": None,
                }
            ],
        }
        with patch("services.agent_service.PropertyAgent.invoke", return_value=mocked_result):
            response = AgentService.run_agent("What is the condition of the kitchen?")

        self.assertIsInstance(response, AgentResponse)
        self.assertEqual(response.answer, "Grounded answer")
        self.assertEqual(response.tools_used, ["rag_search"])
        self.assertGreaterEqual(response.execution_time_ms, 0)

    def test_execution_time_ms_is_recorded(self) -> None:
        mocked_result = {
            "final_answer": "Timed answer",
            "tools_used": ["rag_search"],
            "reasoning_steps": [],
        }
        with patch("services.agent_service.PropertyAgent.invoke", return_value=mocked_result):
            response = AgentService.run_agent("How many bedrooms does the listing have?")

        self.assertIsInstance(response.execution_time_ms, float)
        self.assertGreaterEqual(response.execution_time_ms, 0.0)

    def test_empty_query_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            AgentService.run_agent("   ")

    def test_too_long_query_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            AgentService.run_agent("x" * (AgentService.MAX_QUERY_LENGTH + 1))


if __name__ == "__main__":
    unittest.main()
