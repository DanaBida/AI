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

    @staticmethod
    def _extract_all_urls(text: str) -> List[str]:
        """Extract all URLs from text, handling comma-separated or space-separated URLs."""
        # Find all URLs in the text
        matches = re.findall(r"https?://\S+", text, flags=re.IGNORECASE)
        if not matches:
            return []
        
        # Clean each URL and handle comma-separated URLs
        urls = []
        for match in matches:
            cleaned = match.rstrip(").,;!?")
            # Split by comma if multiple URLs are comma-separated
            for url in cleaned.split(","):
                url = url.strip()
                if url:
                    urls.append(url)
        return urls

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
                    image_urls = self._extract_all_urls(state["query"])
                    if not image_urls:
                        raise ExternalAPIError(
                            "No image URL found in query for image analysis."
                        )
                    
                    # Analyze each image and concatenate results
                    analysis_results = []
                    for idx, image_url in enumerate(image_urls, 1):
                        logger.info(
                            "Analyzing image %d/%d: %s", idx, len(image_urls), image_url
                        )
                        analysis_result = self.image_client.analyze(image_url)
                        analysis_results.append({
                            "image_url": image_url,
                            "analysis": analysis_result
                        })
                    
                    tool_results[tool_name] = {
                        "query": ", ".join(image_urls),
                        "summary": "Photo-based condition analysis retrieved or attempted.",
                        "description": self.tool_descriptions[tool_name],
                        "results": analysis_results,
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

    def _format_tool_results_for_prompt(self, tool_results: Dict[str, Any]) -> str:
        """Format tool results into a readable string for the synthesis prompt."""
        formatted = []
        for tool_name, result in tool_results.items():
            formatted.append(f"\n{tool_name.upper()}:")
            if "error" in result:
                formatted.append(f"  Error: {result['error']}")
            else:
                formatted.append(f"  Summary: {result.get('summary', 'N/A')}")
                
                # Handle image analysis results with multiple images
                if tool_name == "image_analysis" and isinstance(result.get("results"), list):
                    if result["results"] and isinstance(result["results"][0], dict) and "image_url" in result["results"][0]:
                        # Multiple images case
                        for idx, img_result in enumerate(result["results"], 1):
                            formatted.append(f"\n  Image {idx}: {img_result.get('image_url', 'N/A')}")
                            analysis = img_result.get('analysis', {})
                            if isinstance(analysis, dict):
                                for key, value in analysis.items():
                                    formatted.append(f"    {key}: {value}")
                    else:
                        # Single image case (backwards compatibility)
                        formatted.append(f"  Results: {result.get('results', [])}")
                else:
                    # RAG or other tool results
                    results = result.get("results", [])
                    if isinstance(results, list) and results:
                        formatted.append(f"  Found {len(results)} results")
                        for item in results[:3]:  # Show first 3 results
                            formatted.append(f"    - {item}")
                    else:
                        formatted.append(f"  Results: {results}")
        
        return "\n".join(formatted)

    def _synthesizer_node(self, state: AgentState) -> AgentState:
        started_at = time.perf_counter()
        logger.info("Entering synthesizer node")
        formatted_results = self._format_tool_results_for_prompt(state["tool_results"])
        synthesis_prompt = (
            f"{self.surface_prompts[4]}\n\n"
            f"{self.surface_prompts[5]}\n\n"
            f"Query: {state['query']}\n"
            f"Tool results: {formatted_results}"
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
        """Generate a synthesized answer by analyzing tool results directly."""
        tools = state["selected_tools"]
        tool_results = state["tool_results"]
        
        if all("error" in result for result in tool_results.values()):
            return (
                "The agent could not reach its external tools, so this answer is limited. "
                "Please verify the RAG and image-analysis services and retry the request."
            )
        
        answer_parts = []
        
        # Process image analysis results
        if "image_analysis" in tool_results and "error" not in tool_results["image_analysis"]:
            image_results = tool_results["image_analysis"].get("results", [])
            if image_results:
                answer_parts.append("Image Analysis Findings:")
                for idx, img_result in enumerate(image_results, 1):
                    if isinstance(img_result, dict):
                        analysis = img_result.get("analysis", {})
                        room_type = analysis.get("room_type", "Unknown")
                        condition = analysis.get("condition_score", "N/A")
                        confidence = analysis.get("confidence", "N/A")
                        answer_parts.append(
                            f"  Image {idx}: {room_type} - Condition Score: {condition} "
                            f"(Confidence: {confidence})"
                        )
        
        # Process RAG search results
        if "rag_search" in tool_results and "error" not in tool_results["rag_search"]:
            rag_results = tool_results["rag_search"].get("results", [])
            if rag_results:
                answer_parts.append("\nListing Data Retrieved:")
                for idx, item in enumerate(rag_results[:3], 1):
                    answer_parts.append(f"  {idx}. {item}")
        
        # Synthesize a combined conclusion
        if answer_parts:
            answer_parts.append("\nSynthesis:")
            if "image_analysis" in tools and "rag_search" in tools:
                answer_parts.append(
                    "Based on both visual inspection and listing data, the property "
                    "appears to align with the analyzed characteristics. Review the image "
                    "condition scores against comparable listings for a full assessment."
                )
            elif "image_analysis" in tools:
                answer_parts.append(
                    "Based on visual analysis, the property shows the identified room types "
                    "and condition levels. Consider these findings when making a decision."
                )
            else:
                answer_parts.append(
                    "Based on the retrieved listing data, these are the comparable properties "
                    "and market factors relevant to your query."
                )
            
            return "\n".join(answer_parts)
        
        return (
            "Analysis completed but results are limited. Please verify the external "
            "services are functioning properly and retry."
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
