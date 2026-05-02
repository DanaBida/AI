"""LangChain-compatible chat model backed by the `google.genai` SDK."""

from __future__ import annotations

from typing import Any, List, Sequence

from google import genai
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class GoogleGenAIChatModel(BaseChatModel):
    """Minimal adapter for NeMo/LangChain chat generation using `google.genai`."""

    model: str
    api_key: str | None = None
    api_base: str | None = None

    @property
    def _llm_type(self) -> str:
        return "google_genai"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Sequence[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        client_kwargs: dict[str, Any] = {}
        if self.api_key:
            client_kwargs["api_key"] = self.api_key

        if self.api_base:
            client_kwargs["http_options"] = {"base_url": self.api_base}

        client = genai.Client(**client_kwargs)
        prompt_text = self._messages_to_text(messages)
        response = client.models.generate_content(
            model=self.model,
            contents=prompt_text,
        )

        content = (response.text or "").strip()
        generation = ChatGeneration(message=AIMessage(content=content))
        return ChatResult(generations=[generation])

    def _messages_to_text(self, messages: List[BaseMessage]) -> str:
        parts: list[str] = []
        for message in messages:
            role = self._normalize_role(getattr(message, "type", "user"))
            content = self._normalize_content(message.content)
            parts.append(f"{role}: {content}")
        return "\n\n".join(parts)

    @staticmethod
    def _normalize_role(role: str) -> str:
        if role == "ai":
            return "assistant"
        return role

    @staticmethod
    def _normalize_content(content: Any) -> str:
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            chunks: list[str] = []
            for item in content:
                if isinstance(item, str):
                    chunks.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if text:
                        chunks.append(str(text))
            return "\n".join(chunks)

        return str(content)
