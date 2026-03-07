"""Tests for vLLM provider (mocked OpenAI-compatible API)."""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.llm.vllm_provider import VLLMProvider


@pytest.fixture
def provider():
    return VLLMProvider(base_url="http://localhost:8100/v1", model_name="voicebook")


def _mock_response(content="", tool_calls=None):
    """Build a mock OpenAI-style response."""
    message = MagicMock()
    message.content = content
    if tool_calls:
        mock_tcs = []
        for tc in tool_calls:
            mock_tc = MagicMock()
            mock_tc.id = tc["id"]
            mock_tc.function.name = tc["name"]
            mock_tc.function.arguments = json.dumps(tc["arguments"])
            mock_tcs.append(mock_tc)
        message.tool_calls = mock_tcs
    else:
        message.tool_calls = None

    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.mark.asyncio
async def test_basic_chat(provider):
    mock_resp = _mock_response(content="Здравствуйте! Чем могу помочь?")

    with patch.object(provider.client.chat.completions, "create", new_callable=AsyncMock, return_value=mock_resp):
        result = await provider.chat(messages=[{"role": "user", "content": "Привет"}])

    assert result.content == "Здравствуйте! Чем могу помочь?"
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_tool_call_extract_intent(provider):
    mock_resp = _mock_response(
        content="Конечно! Какую стрижку хотите?",
        tool_calls=[{
            "id": "call_123",
            "name": "extract_intent",
            "arguments": {"intent": "book"},
        }],
    )

    with patch.object(provider.client.chat.completions, "create", new_callable=AsyncMock, return_value=mock_resp):
        result = await provider.chat(
            messages=[{"role": "user", "content": "Хочу записаться"}],
            tools=[{"type": "function", "function": {"name": "extract_intent"}}],
        )

    assert result.content == "Конечно! Какую стрижку хотите?"
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0]["name"] == "extract_intent"
    assert result.tool_calls[0]["arguments"]["intent"] == "book"


@pytest.mark.asyncio
async def test_multiple_tool_calls(provider):
    mock_resp = _mock_response(
        content="",
        tool_calls=[
            {"id": "call_1", "name": "extract_intent", "arguments": {"intent": "book", "service_name": "стрижка"}},
            {"id": "call_2", "name": "check_slots", "arguments": {"staff_id": 10, "service_id": 1, "date": "2026-03-10"}},
        ],
    )

    with patch.object(provider.client.chat.completions, "create", new_callable=AsyncMock, return_value=mock_resp):
        result = await provider.chat(messages=[{"role": "user", "content": "test"}], tools=[])

    assert len(result.tool_calls) == 2
    assert result.tool_calls[0]["name"] == "extract_intent"
    assert result.tool_calls[1]["name"] == "check_slots"


@pytest.mark.asyncio
async def test_malformed_tool_args(provider):
    """vLLM sometimes returns invalid JSON in tool args."""
    message = MagicMock()
    message.content = "Попробуем ещё раз"
    mock_tc = MagicMock()
    mock_tc.id = "call_bad"
    mock_tc.function.name = "extract_intent"
    mock_tc.function.arguments = "{invalid json}"
    message.tool_calls = [mock_tc]

    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]

    with patch.object(provider.client.chat.completions, "create", new_callable=AsyncMock, return_value=response):
        result = await provider.chat(messages=[{"role": "user", "content": "test"}])

    assert len(result.tool_calls) == 1
    assert result.tool_calls[0]["arguments"] == {}  # graceful fallback
