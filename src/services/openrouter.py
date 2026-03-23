"""
OpenRouter LLM Client for SpokeStack Agent Service.

Consolidates all Claude API calls through OpenRouter, replacing direct
Anthropic SDK usage. One API key, any model.

Usage:
    client = OpenRouterClient(api_key="sk-or-...")
    response = await client.chat("anthropic/claude-sonnet-4-20250514", messages, tools)
    async for chunk in client.stream("anthropic/claude-sonnet-4-20250514", messages):
        print(chunk)
"""

import json
from typing import Any, AsyncIterator, Optional
import httpx
import logging

logger = logging.getLogger(__name__)

# Map Anthropic model IDs (with date suffixes) to OpenRouter model IDs
OPENROUTER_MODEL_MAP = {
    # Sonnet
    "claude-sonnet-4-20250514": "anthropic/claude-sonnet-4",
    "claude-sonnet-4.5": "anthropic/claude-sonnet-4.5",
    "claude-sonnet-4.6": "anthropic/claude-sonnet-4.6",
    # Opus
    "claude-opus-4-20250514": "anthropic/claude-opus-4",
    "claude-opus-4-5-20250514": "anthropic/claude-opus-4.5",
    "claude-opus-4.6": "anthropic/claude-opus-4.6",
    # Haiku
    "claude-3-5-haiku-20241022": "anthropic/claude-3.5-haiku",
    "claude-haiku-3-5-20241022": "anthropic/claude-3.5-haiku",
    "claude-haiku-4.5": "anthropic/claude-haiku-4.5",
}

# Models that need the anthropic/ prefix on OpenRouter
ANTHROPIC_MODEL_PREFIXES = (
    "claude-opus-",
    "claude-sonnet-",
    "claude-haiku-",
    "claude-3",
    "claude-4",
)


def ensure_openrouter_model(model: str) -> str:
    """Map Anthropic model names to OpenRouter model IDs."""
    # Check explicit mapping first (handles date-suffixed names)
    if model in OPENROUTER_MODEL_MAP:
        return OPENROUTER_MODEL_MAP[model]
    # Already has provider prefix
    if "/" in model:
        return model
    # Fallback: add anthropic/ prefix
    for prefix in ANTHROPIC_MODEL_PREFIXES:
        if model.startswith(prefix):
            return f"anthropic/{model}"
    return model


class OpenRouterClient:
    """Unified LLM client via OpenRouter — drop-in replacement for Anthropic SDK."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        app_name: str = "SpokeStack",
        timeout: float = 120.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.app_name = app_name
        self.http = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://spokestack.app",
                "X-Title": app_name,
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def chat(
        self,
        model: str,
        messages: list[dict],
        system: Optional[str] = None,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
        tool_choice: Optional[dict] = None,
    ) -> dict:
        """
        Non-streaming chat completion.

        Returns OpenAI-compatible response dict:
        {
            "choices": [{"message": {"role": "assistant", "content": "...", "tool_calls": [...]}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": N, "completion_tokens": N, "total_tokens": N}
        }
        """
        model = ensure_openrouter_model(model)
        payload = self._build_payload(model, messages, system, tools, max_tokens, stream=False, tool_choice=tool_choice)
        response = await self.http.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    async def stream(
        self,
        model: str,
        messages: list[dict],
        system: Optional[str] = None,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
        tool_choice: Optional[dict] = None,
    ) -> AsyncIterator[dict]:
        """Streaming chat completion. Yields parsed SSE chunks."""
        model = ensure_openrouter_model(model)
        payload = self._build_payload(model, messages, system, tools, max_tokens, stream=True, tool_choice=tool_choice)
        async with self.http.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue

    def _build_payload(
        self,
        model: str,
        messages: list[dict],
        system: Optional[str],
        tools: Optional[list[dict]],
        max_tokens: int,
        stream: bool,
        tool_choice: Optional[dict] = None,
    ) -> dict:
        """Build the OpenRouter API payload."""
        all_messages = []
        if system:
            all_messages.append({"role": "system", "content": system})

        for msg in messages:
            normalized = self._normalize_message(msg)
            # Tool results may expand to multiple messages
            if isinstance(normalized, list):
                all_messages.extend(normalized)
            else:
                all_messages.append(normalized)

        payload: dict[str, Any] = {
            "model": model,
            "messages": all_messages,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        if tools:
            payload["tools"] = self._convert_tools(tools)

        if tool_choice:
            payload["tool_choice"] = tool_choice

        return payload

    def _normalize_message(self, msg: dict) -> dict | list[dict]:
        """Normalize message format for OpenRouter (OpenAI-compatible)."""
        role = msg.get("role", "user")
        content = msg.get("content")

        # Already in OpenAI format (tool role)
        if role == "tool":
            return msg

        # Assistant message with tool_calls already in OpenAI format
        if role == "assistant" and "tool_calls" in msg:
            return msg

        # Handle list content (Anthropic-style content blocks or tool results)
        if isinstance(content, list):
            # Anthropic-style tool results: [{"type": "tool_result", ...}, ...]
            if content and isinstance(content[0], dict) and content[0].get("type") == "tool_result":
                return [
                    {
                        "role": "tool",
                        "tool_call_id": item.get("tool_use_id", ""),
                        "content": str(item.get("content", "")),
                    }
                    for item in content
                ]

            # Anthropic-style vision content blocks
            converted_content = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        converted_content.append({"type": "text", "text": block.get("text", "")})
                    elif block.get("type") == "image":
                        # Convert Anthropic image format to OpenAI image_url format
                        source = block.get("source", {})
                        if source.get("type") == "base64":
                            media_type = source.get("media_type", "image/jpeg")
                            data = source.get("data", "")
                            converted_content.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:{media_type};base64,{data}"},
                            })
                    elif block.get("type") == "image_url":
                        converted_content.append(block)  # Already OpenAI format
                    else:
                        converted_content.append({"type": "text", "text": str(block)})

            return {"role": role, "content": converted_content if converted_content else ""}

        return {"role": role, "content": str(content) if content else ""}

    def _convert_tools(self, anthropic_tools: list[dict]) -> list[dict]:
        """Convert Anthropic-style tools to OpenAI-style for OpenRouter."""
        openai_tools = []
        for tool in anthropic_tools:
            # Already OpenAI format
            if tool.get("type") == "function":
                openai_tools.append(tool)
                continue
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", tool.get("parameters", {})),
                },
            })
        return openai_tools

    async def close(self):
        await self.http.aclose()
