"""Service layer for conversational assistant interactions."""

from lib.ollama_client import OllamaClient
from models.chat_types import ChatRequest, ChatResponse
from services.prompt_logging_service import PromptLoggingService


class ChatService:
    """Business logic for sending chat requests and recording runs."""

    @classmethod
    def chat(cls, request: ChatRequest) -> ChatResponse:
        """Send a validated request to Ollama and return a typed response."""
        client = OllamaClient()
        result = client.chat(system_prompt=request.system_prompt, user_message=request.user_message)
        response = ChatResponse(reply=result.content)

        PromptLoggingService.log_chat_run(
            system_prompt=request.system_prompt,
            user_message=request.user_message,
            assistant_reply=response.reply,
            raw_response=result.raw,
        )
        return response

