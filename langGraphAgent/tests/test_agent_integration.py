"""
Integration-style tests for the end-to-end agent flow using stubs.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from controllers.agent_controller import run_agent
from models.agent_types import AgentQuery, AgentResponse
from services.agent_service import AgentService


class AgentIntegrationTests(unittest.TestCase):
    """Integration coverage using predictable local doubles."""

    def test_agent_completes_happy_path(self) -> None:
        response = run_agent(AgentQuery(query="What renovation is needed to improve condition?"))

        self.assertIsInstance(response, AgentResponse)
        self.assertTrue(response.answer)
        self.assertGreaterEqual(len(response.reasoning_steps), 3)

    def test_agent_handles_timeout_as_gateway_timeout(self) -> None:
        with patch(
            "controllers.agent_controller.AgentService.run_agent",
            side_effect=TimeoutError("Agent execution exceeded the configured timeout."),
        ):
            with self.assertRaises(HTTPException) as context:
                run_agent(AgentQuery(query="What is the condition of the kitchen?"))

        self.assertEqual(context.exception.status_code, 504)
        self.assertIn("timeout", context.exception.detail.lower())

    def test_agent_handles_unexpected_failure_gracefully(self) -> None:
        with patch(
            "controllers.agent_controller.AgentService.run_agent",
            side_effect=RuntimeError("downstream failed"),
        ):
            with self.assertRaises(HTTPException) as context:
                run_agent(AgentQuery(query="Compare two properties by location and price."))

        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(
            context.exception.detail,
            "Unexpected error while running the LangGraph agent.",
        )

    def test_agent_response_contains_all_used_tools(self) -> None:
        response = AgentService.run_agent("What renovation work would increase property value most?")

        self.assertIn("rag_search", response.tools_used)
        self.assertIn("image_analysis", response.tools_used)

    def test_agent_response_schema_is_consistent(self) -> None:
        response = AgentService.run_agent("How does this property compare to market average?")

        self.assertIsInstance(response.answer, str)
        self.assertIsInstance(response.tools_used, list)
        self.assertIsInstance(response.reasoning_steps, list)
        self.assertIsInstance(response.execution_time_ms, float)


if __name__ == "__main__":
    unittest.main()
