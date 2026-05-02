"""
Smoke tests for FastAPI endpoints.
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

from app import app, root
from controllers.agent_controller import run_agent
from models.agent_types import AgentQuery, AgentResponse


class AgentEndpointTests(unittest.TestCase):
    """Smoke tests for the HTTP API."""

    def test_root_endpoint_exposes_agent_route(self) -> None:
        response = root()

        self.assertEqual(response["agent_endpoint"], "/agent/run")

    def test_agent_route_is_registered(self) -> None:
        paths = [route.path for route in app.routes]

        self.assertIn("/agent/run", paths)

    def test_run_agent_controller_returns_response_schema(self) -> None:
        mocked_response = AgentResponse(
            answer="A synthesized answer",
            tools_used=["rag_search", "image_analysis"],
            reasoning_steps=[
                {
                    "step_number": 1,
                    "description": "Planner selected tools.",
                    "tool_used": None,
                }
            ],
            execution_time_ms=12.5,
        )
        with patch("controllers.agent_controller.AgentService.run_agent", return_value=mocked_response):
            response = run_agent(AgentQuery(query="What is the condition of the kitchen?"))

        self.assertIsInstance(response, AgentResponse)
        self.assertEqual(response.answer, "A synthesized answer")

    def test_run_agent_controller_returns_400_for_empty_query(self) -> None:
        with patch(
            "controllers.agent_controller.AgentService.run_agent",
            side_effect=ValueError("Query must not be empty."),
        ):
            with self.assertRaises(HTTPException) as context:
                run_agent(AgentQuery(query="   "))

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Query must not be empty.")


if __name__ == "__main__":
    unittest.main()
