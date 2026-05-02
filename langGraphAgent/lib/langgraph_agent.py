"""
Property agent implementation for complex property queries.
"""
from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, List, TypedDict

from config import Config
from lib.gemini_client import GeminiAPIError, GeminiClient
from utils.external_apis import ExternalAPIError, ImageAnalyzerClient, RAGClient


logger = logging.getLogger(__name__)


TOOL_DESCRIPTIONS: Dict[str, str] = {
    "rag_search": (
        "Search structured property knowledge and listing text. Use this tool for "
        "listing facts, bedrooms, bathrooms, price, location, market comparisons, "
        "renovation history, and any request that depends on textual listing data. "
        "Prefer this tool when the answer can be grounded in listing attributes or "
        "retrieved documents."
    ),
    "image_analysis": (
        "Analyze property photos to identify visible rooms, surface wear, damage, "
        "cleanliness, and estimated condition scores. Use this tool only for claims "
        "that depend on visual evidence from images. Do not use it for hidden "
        "structural issues or non-visible listing attributes."
    ),
}

SURFACE_PROMPTS: Dict[int, str] = {
    1: (
        "Choose tools conservatively. Use rag_search for listing facts, counts, "
        "comparisons, location, price, and market context. Use image_analysis only "
        "when the user asks about visible rooms, visible damage, room condition, or "
        "issues detectable from photos. Use both tools when the request needs listing "
        "facts plus visual condition evidence. If information is missing, say so "
        "instead of guessing."
    ),
    2: (
        "Rewrite the user's request into a retrieval query that preserves the core "
        "constraints: property type, city, neighborhood, price band, comparison "
        "target, time or market context, and requested outcome. Keep the query short, "
        "specific, and noun-heavy. Do not introduce details that were not asked for."
    ),
    3: (
        "Interpret image-analysis results using only visible evidence. Explain what a "
        "condition score means in plain language, note confidence, and separate minor "
        "cosmetic wear from potential safety or structural concerns. Never claim hidden "
        "defects unless the evidence clearly shows them."
    ),
    4: (
        "Synthesize multi-source results into one grounded answer. Lead with the direct "
        "answer, then connect listing facts and image findings. Call out conflicts, "
        "state which source supports each conclusion, and end with practical next "
        "steps or follow-up data needed."
    ),
    5: (
        "Recover gracefully from missing or conflicting tool data. If one tool is "
        "unavailable, continue with the other and label the limitation. If sources "
        "conflict, report the conflict explicitly, prefer the more direct evidence, "
        "and suggest the smallest next action needed to resolve uncertainty."
    ),
}


class AgentState(TypedDict):
    """State carried through the agent flow."""

    query: str
    reasoning_steps: List[Dict[str, Any]]
    selected_tools: List[str]
    tool_results: Dict[str, Any]
    final_answer: str


class PropertyAgent:
    """Agent facade with planner, executor, and synthesizer nodes."""

    def __init__(self) -> None:
        logging.basicConfig(level=getattr(logging, Config.AGENT_LOG_LEVEL.upper(), logging.INFO))
        self.tool_descriptions = TOOL_DESCRIPTIONS
        self.surface_prompts = SURFACE_PROMPTS
        self.rag_client = RAGClient()
        self.image_client = ImageAnalyzerClient()
        self.gemini_client = GeminiClient()

    @staticmethod
    def _append_reasoning(
        state: AgentState,
        description: str,
        tool_used: str | None = None,
    ) -> None:
        step_number = len(state["reasoning_steps"]) + 1
        state["reasoning_steps"].append(
            {
                "step_number": step_number,
                "description": description,
                "tool_used": tool_used,
            }
        )

    @staticmethod
    def _heuristic_tool_selection(query: str) -> List[str]:
        lowered = query.lower()
        has_url = bool(re.search(r"https?://\S+", query, flags=re.IGNORECASE))
        image_terms = {
            "image",
            "images",
            "photo",
            "photos",
            "visible",
            "damage",
            "structural",
        }
        rag_terms = {
            "price",
            "location",
            "bedroom",
            "bedrooms",
            "bathroom",
            "bathrooms",
            "compare",
            "market",
            "listing",
            "value",
            "haifa",
            "property",
            "average",
            "cost",
            "renovation",
            "upgrade",
            "upgrades",
        }

        selected_tools: List[str] = []
        if any(term in lowered for term in rag_terms):
            selected_tools.append("rag_search")
        if has_url and any(term in lowered for term in image_terms):
            selected_tools.append("image_analysis")
        if not selected_tools:
            selected_tools.append("rag_search")
        return list(dict.fromkeys(selected_tools))

    @staticmethod
    def _extract_first_url(text: str) -> str | None:
        match = re.search(r"https?://\S+", text, flags=re.IGNORECASE)
        if not match:
            return None
        return match.group(0).rstrip(").,;!?")

    def _planner_node(self, state: AgentState) -> AgentState:
        started_at = time.perf_counter()
        logger.info("Entering planner node")
        planner_prompt = (
            f"{self.surface_prompts[1]}\n\n"
            f"Available tools: {list(self.tool_descriptions.keys())}\n"
            f"Query: {state['query']}"
        )
        logger.debug("Planner prompt: %s", planner_prompt)

        selected_tools = self._heuristic_tool_selection(state["query"])
        try:
            planner_response = self.gemini_client.call(planner_prompt, temperature=0.1)
            logger.debug("Planner raw Gemini response: %s", planner_response)
            parsed_tools = [
                tool_name
                for tool_name in self.tool_descriptions
                if tool_name in planner_response.lower()
            ]
            if parsed_tools:
                selected_tools = list(dict.fromkeys(parsed_tools))
        except GeminiAPIError as exc:
            logger.info("Planner fallback to heuristic selection: %s", exc)

        state["selected_tools"] = selected_tools
        self._append_reasoning(
            state,
            "Planner selected tools using the optimized tool-selection surface.",
        )
        logger.info(
            "Planner selected tools=%s in %.2fms",
            selected_tools,
            (time.perf_counter() - started_at) * 1000,
        )
        return state

    def _executor_node(self, state: AgentState) -> AgentState:
        started_at = time.perf_counter()
        logger.info("Entering executor node with tools=%s", state["selected_tools"])
        tool_results: Dict[str, Any] = {}

        for tool_name in state["selected_tools"]:
            try:
                if tool_name == "rag_search":
                    retrieval_query = state["query"]
                    tool_results[tool_name] = {
                        "query": retrieval_query,
                        "summary": "Listing knowledge retrieved or attempted.",
                        "description": self.tool_descriptions[tool_name],
                        "results": self.rag_client.search(retrieval_query, top_k=3),
                    }
                elif tool_name == "image_analysis":
                    image_url = self._extract_first_url(state["query"])
                    if not image_url:
                        raise ExternalAPIError(
                            "No image URL found in query for image analysis."
                        )
                    tool_results[tool_name] = {
                        "query": image_url,
                        "summary": "Photo-based condition analysis retrieved or attempted.",
                        "description": self.tool_descriptions[tool_name],
                        "results": self.image_client.analyze(image_url),
                    }
                logger.info("Executor completed tool=%s", tool_name)
            except ExternalAPIError as exc:
                tool_results[tool_name] = {
                    "error": str(exc),
                    "summary": (
                        "Listing knowledge retrieval failed."
                        if tool_name == "rag_search"
                        else "Photo-based condition analysis failed."
                    ),
                    "description": self.tool_descriptions.get(tool_name, ""),
                    "results": [],
                }
                logger.info("Executor captured tool failure for %s: %s", tool_name, exc)

            self._append_reasoning(
                state,
                f"Executed {tool_name} and captured structured results.",
                tool_used=tool_name,
            )

        state["tool_results"] = tool_results
        logger.info(
            "Executor completed in %.2fms",
            (time.perf_counter() - started_at) * 1000,
        )
        logger.debug("Executor tool results: %s", tool_results)
        return state

    def _synthesizer_node(self, state: AgentState) -> AgentState:
        started_at = time.perf_counter()
        logger.info("Entering synthesizer node")
        synthesis_prompt = (
            f"{self.surface_prompts[4]}\n\n"
            f"{self.surface_prompts[5]}\n\n"
            f"Query: {state['query']}\n"
            f"Tool results: {state['tool_results']}"
        )
        logger.debug("Synthesizer prompt: %s", synthesis_prompt)

        final_answer = ""
        try:
            final_answer = self.gemini_client.call(synthesis_prompt, temperature=0.2).strip()
        except GeminiAPIError as exc:
            logger.info("Synthesizer fallback used: %s", exc)

        if not final_answer:
            final_answer = self._fallback_synthesis(state)

        state["final_answer"] = final_answer
        self._append_reasoning(
            state,
            "Synthesized a final answer using the optimized result-synthesis surface.",
        )
        logger.info(
            "Synthesizer completed in %.2fms",
            (time.perf_counter() - started_at) * 1000,
        )
        return state

    def _fallback_synthesis(self, state: AgentState) -> str:
        tools = state["selected_tools"]
        tool_results = state["tool_results"]
        if all("error" in result for result in tool_results.values()):
            return (
                "The agent could not reach its external tools, so this answer is limited. "
                "Please verify the RAG and image-analysis services and retry the request."
            )
        if "image_analysis" in tools and "rag_search" in tools:
            return (
                "This request likely needs both listing retrieval and photo analysis. "
                "Use listing data for facts and comparisons, then use images for visible "
                "condition findings before giving a final recommendation."
            )
        if "image_analysis" in tools:
            return (
                "This request is primarily visual. Base the answer on what is visible in "
                "the property photos and clearly note any uncertainty."
            )
        return (
            "This request is primarily about listing facts or market context, so the "
            "answer should be grounded in retrieved property data."
        )

    def invoke(self, query: str) -> Dict[str, Any]:
        started_at = time.perf_counter()
        state: AgentState = {
            "query": query,
            "reasoning_steps": [],
            "selected_tools": [],
            "tool_results": {},
            "final_answer": "",
        }
        logger.info("Invoking PropertyAgent")
        state = self._planner_node(state)
        state = self._executor_node(state)
        state = self._synthesizer_node(state)

        elapsed_seconds = time.perf_counter() - started_at
        if elapsed_seconds > Config.AGENT_TIMEOUT_SECONDS:
            raise TimeoutError("Agent execution exceeded the configured timeout.")

        result: Dict[str, Any] = dict(state)
        result["tools_used"] = state["selected_tools"]
        logger.info("PropertyAgent completed in %.2fms", elapsed_seconds * 1000)
        return result
