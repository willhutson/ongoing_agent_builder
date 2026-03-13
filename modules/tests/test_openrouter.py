"""Tests for OpenRouter client — tool conversion, message normalization."""

import json
from shared.openrouter import OpenRouterClient


def test_client_init(llm_client):
    assert llm_client.api_key == "test-key-not-real"
    assert "openrouter.ai" in llm_client.base_url


def test_convert_tools_anthropic_to_openai(llm_client):
    anthropic_tools = [
        {
            "name": "search",
            "description": "Search the web",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        }
    ]
    result = llm_client._convert_tools(anthropic_tools)
    assert len(result) == 1
    assert result[0]["type"] == "function"
    assert result[0]["function"]["name"] == "search"
    assert result[0]["function"]["parameters"]["properties"]["query"]["type"] == "string"


def test_normalize_simple_message(llm_client):
    msg = {"role": "user", "content": "hello"}
    result = llm_client._normalize_message(msg)
    assert result == {"role": "user", "content": "hello"}


def test_normalize_tool_result_message(llm_client):
    msg = {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": "call_123", "content": "result data"}
        ],
    }
    result = llm_client._normalize_message(msg)
    assert result["role"] == "tool"
    assert result["tool_call_id"] == "call_123"
    assert result["content"] == "result data"


def test_normalize_none_content(llm_client):
    msg = {"role": "assistant", "content": None}
    result = llm_client._normalize_message(msg)
    assert result["content"] == ""


def test_build_payload_includes_system(llm_client):
    payload = llm_client._build_payload(
        model="test/model",
        messages=[{"role": "user", "content": "hi"}],
        system="You are helpful.",
        tools=None,
        max_tokens=100,
        stream=False,
    )
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][0]["content"] == "You are helpful."
    assert payload["messages"][1]["content"] == "hi"
    assert payload["model"] == "test/model"
    assert payload["stream"] is False
    assert "tools" not in payload


def test_build_payload_with_tools(llm_client):
    tools = [{"name": "test", "description": "test tool", "input_schema": {"type": "object", "properties": {}}}]
    payload = llm_client._build_payload(
        model="test/model",
        messages=[{"role": "user", "content": "hi"}],
        system=None,
        tools=tools,
        max_tokens=100,
        stream=True,
    )
    assert "tools" in payload
    assert payload["tools"][0]["type"] == "function"
    assert payload["stream"] is True
