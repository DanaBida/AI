"""Pydantic models for the conversational assistant surface."""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Represents a single chat message shown in the WebUI."""

    role: str = Field(..., description="Message role such as user or assistant.")
    content: str = Field(..., min_length=1, description="Message body text.")


class ChatRequest(BaseModel):
    """Validated request payload for an assistant interaction."""

    system_prompt: str = Field(..., min_length=1)
    user_message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    """Validated assistant response returned to the UI."""

    reply: str = Field(..., min_length=1)
