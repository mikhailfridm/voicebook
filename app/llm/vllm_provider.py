"""
vLLM Provider — self-hosted Qwen2.5 inference via OpenAI-compatible API.

vLLM exposes an API identical to OpenAI, so we reuse the openai SDK
with a different base_url pointing to the local vLLM server.
"""

import json
import logging
from typing import Optional

from openai import AsyncOpenAI
from app.llm.provider import LLMProvider, LLMResponse
from config.settings import settings

logger = logging.getLogger(__name__)


class VLLMProvider(LLMProvider):
    def __init__(
        self,
        base_url: str = "",
        model_name: str = "",
    ):
        self.model = model_name or settings.vllm_model_name
        self.client = AsyncOpenAI(
            base_url=base_url or settings.vllm_base_url,
            api_key="not-needed",  # vLLM doesn't require an API key
        )

    async def chat(
        self,
        messages,
        tools=None,
        tool_choice="auto",
        temperature=0.3,
        max_tokens=300,
    ) -> LLMResponse:
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
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse tool call args: {tc.function.arguments}")
                    args = {}
                tc_list.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": args,
                })

        return LLMResponse(content=message.content or "", tool_calls=tc_list)
