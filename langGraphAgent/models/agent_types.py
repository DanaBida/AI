"""
Pydantic models for LangGraph Agent API.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class AgentQuery(BaseModel):
    query: str

class ReasoningStep(BaseModel):
    step_number: int
    description: str
    tool_used: Optional[str] = None

class AgentResponse(BaseModel):
    answer: str
    tools_used: List[str]
    reasoning_steps: List[ReasoningStep]
    execution_time_ms: float

class ToolDescription(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
