"""Controller helpers for the conversational assistant surface."""

from models.chat_types import ChatRequest, ChatResponse
from services.prompt_service import PromptService


class ChatController:
    """Coordinates validated chat requests for the UI layer."""

    @classmethod
    def build_request(cls, user_message: str) -> ChatRequest:
        """Create a validated chat request using the active prompt."""
        return ChatRequest(
            system_prompt=PromptService.load_active_prompt(),
            user_message=user_message.strip(),
        )

    @classmethod
    def build_response(cls, reply: str) -> ChatResponse:
        """Wrap a model reply in a typed response object."""
        return ChatResponse(reply=reply.strip())
