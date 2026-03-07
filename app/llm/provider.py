"""
LLM Provider abstraction — allows switching between OpenAI and YandexGPT.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMResponse:
    """Unified response from any LLM provider."""

    def __init__(
        self,
        content: str = "",
        tool_calls: Optional[list[dict]] = None,
    ):
        self.content = content
        self.tool_calls = tool_calls or []


class LLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        tool_choice: str = "auto",
        temperature: float = 0.3,
        max_tokens: int = 300,
    ) -> LLMResponse:
        ...


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4o-mini", api_key: str = ""):
        from openai import AsyncOpenAI

        self.model = model
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)

    async def chat(self, messages, tools=None, tool_choice="auto", temperature=0.3, max_tokens=300) -> LLMResponse:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        response = await self.client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        tc_list = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tc_list.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                })

        return LLMResponse(content=message.content or "", tool_calls=tc_list)


class YandexGPTProvider(LLMProvider):
    """
    YandexGPT provider via REST API.
    Docs: https://cloud.yandex.ru/docs/yandexgpt/api-ref/v1/TextGeneration/completion

    NOTE: YandexGPT function calling support is limited.
    This provider handles basic chat; function calls are extracted from text.
    """

    def __init__(self, model: str = "yandexgpt", api_key: str = "", folder_id: str = ""):
        import httpx

        self.model = model
        self.api_key = api_key or settings.yandex_cloud_api_key
        self.folder_id = folder_id or settings.yandex_cloud_folder_id
        self._client = httpx.AsyncClient(timeout=15.0)

    async def chat(self, messages, tools=None, tool_choice="auto", temperature=0.3, max_tokens=300) -> LLMResponse:
        # Convert OpenAI message format to YandexGPT format
        yandex_messages = []
        for msg in messages:
            role = msg["role"]
            if role == "tool":
                role = "system"
            elif role == "assistant" and "tool_calls" in msg:
                # Skip tool_call messages, YandexGPT doesn't support them
                continue
            content = msg.get("content", "")
            if content:
                yandex_messages.append({"role": role, "text": content})

        payload = {
            "modelUri": f"gpt://{self.folder_id}/{self.model}",
            "completionOptions": {
                "stream": False,
                "temperature": temperature,
                "maxTokens": str(max_tokens),
            },
            "messages": yandex_messages,
        }

        resp = await self._client.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            json=payload,
            headers={
                "Authorization": f"Api-Key {self.api_key}",
                "x-folder-id": self.folder_id,
            },
        )
        resp.raise_for_status()
        data = resp.json()

        text = ""
        alternatives = data.get("result", {}).get("alternatives", [])
        if alternatives:
            text = alternatives[0].get("message", {}).get("text", "")

        # YandexGPT doesn't natively support function calling,
        # so we return text only. Intent extraction falls back to UNCLEAR
        # and the agent will use the text response directly.
        return LLMResponse(content=text)


def create_provider(provider_name: str = "") -> LLMProvider:
    """Factory function to create LLM provider based on config."""
    name = provider_name or settings.llm_provider

    if name == "yandexgpt":
        return YandexGPTProvider()
    elif name == "vllm":
        from app.llm.vllm_provider import VLLMProvider
        return VLLMProvider()
    else:
        return OpenAIProvider()
