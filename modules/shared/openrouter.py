"""
OpenRouter LLM Client — replaces all 14 provider clients.

One API key. Any model. Simple.

Usage:
    client = OpenRouterClient(api_key="sk-or-...")
    response = await client.chat("anthropic/claude-sonnet-4-20250514", messages, tools)
    async for chunk in client.stream("anthropic/claude-sonnet-4-20250514", messages):
        print(chunk)
"""

import json
from typing import Any, AsyncIterator, Optional
import httpx


class OpenRouterClient:
    """Unified LLM client via OpenRouter."""

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
    ) -> dict:
        """Non-streaming chat completion."""
        payload = self._build_payload(model, messages, system, tools, max_tokens, stream=False)
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
    ) -> AsyncIterator[dict]:
        """Streaming chat completion. Yields parsed SSE chunks."""
        payload = self._build_payload(model, messages, system, tools, max_tokens, stream=True)
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
    ) -> dict:
        """Build the OpenRouter API payload."""
        # Convert Anthropic-style system prompt to OpenAI-style
        all_messages = []
        if system:
            all_messages.append({"role": "system", "content": system})

        for msg in messages:
            all_messages.append(self._normalize_message(msg))

        payload: dict[str, Any] = {
            "model": model,
            "messages": all_messages,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        if tools:
            payload["tools"] = self._convert_tools(tools)

        return payload

    def _normalize_message(self, msg: dict) -> dict:
        """Normalize message format for OpenRouter (OpenAI-compatible)."""
        role = msg.get("role", "user")
        content = msg.get("content")

        # Handle Anthropic-style tool results
        if isinstance(content, list):
            # Check if it's tool results
            if content and isinstance(content[0], dict) and content[0].get("type") == "tool_result":
                return {
                    "role": "tool",
                    "tool_call_id": content[0].get("tool_use_id", ""),
                    "content": str(content[0].get("content", "")),
                }
            # Handle Anthropic-style content blocks (text + tool_use)
            tool_calls = []
            text_parts = []
            for block in content:
                if hasattr(block, "type"):
                    if block.type == "text":
                        text_parts.append(block.text)
                    elif block.type == "tool_use":
                        tool_calls.append({
                            "id": block.id,
                            "type": "function",
                            "function": {
                                "name": block.name,
                                "arguments": json.dumps(block.input),
                            },
                        })
                elif isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif block.get("type") == "tool_use":
                        tool_calls.append({
                            "id": block.get("id", ""),
                            "type": "function",
                            "function": {
                                "name": block.get("name", ""),
                                "arguments": json.dumps(block.get("input", {})),
                            },
                        })

            result = {"role": role, "content": "\n".join(text_parts) if text_parts else ""}
            if tool_calls:
                result["tool_calls"] = tool_calls
            return result

        return {"role": role, "content": str(content) if content else ""}

    def _convert_tools(self, anthropic_tools: list[dict]) -> list[dict]:
        """Convert Anthropic-style tools to OpenAI-style for OpenRouter."""
        openai_tools = []
        for tool in anthropic_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {}),
                },
            })
        return openai_tools

    async def close(self):
        await self.http.aclose()
