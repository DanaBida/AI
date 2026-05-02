"""
Business logic for LangGraph Agent.
"""
import time

from config import Config
from models.agent_types import AgentResponse
from lib.langgraph_agent import PropertyAgent


class AgentService:
    """Application service for executing the property agent."""

    MAX_QUERY_LENGTH = 2000

    @classmethod
    def _validate_query(cls, query: str) -> str:
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")

        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("Query must not be empty.")

        if len(normalized_query) > cls.MAX_QUERY_LENGTH:
            raise ValueError(
                f"Query must be {cls.MAX_QUERY_LENGTH} characters or fewer."
            )

        return normalized_query

    @classmethod
    def run_agent(cls, query: str) -> AgentResponse:
        validated_query = cls._validate_query(query)
        start = time.time()
        agent = PropertyAgent()
        result = agent.invoke(validated_query)
        end = time.time()
        execution_time_ms = (end - start) * 1000

        if execution_time_ms > Config.AGENT_TIMEOUT_SECONDS * 1000:
            raise TimeoutError("Agent execution exceeded the configured timeout.")

        return AgentResponse(
            answer=result.get("final_answer", ""),
            tools_used=result.get("tools_used", []),
            reasoning_steps=result.get("reasoning_steps", []),
            execution_time_ms=execution_time_ms,
        )
