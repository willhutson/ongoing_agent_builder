"""
Base Agent — OpenRouter edition.

Follows the same Think → Act → Create paradigm but talks to OpenRouter
instead of the Anthropic SDK directly. Works with any model on OpenRouter.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4
import json

from .openrouter import OpenRouterClient


@dataclass
class AgentContext:
    """Context passed to agent during execution."""
    tenant_id: str
    user_id: str
    task: str
    metadata: dict = field(default_factory=dict)
    chat_id: str = field(default_factory=lambda: str(uuid4()))
    client_id: Optional[str] = None
    project_id: Optional[str] = None
    attachments: list[dict] = field(default_factory=list)


@dataclass
class AgentResult:
    """Result from agent execution."""
    success: bool
    output: str
    agent: str = ""
    artifacts: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all module agents.

    Uses OpenRouter for LLM calls — any model, one API key.
    Subclasses implement: name, system_prompt, _define_tools, _execute_tool.
    """

    def __init__(self, llm: OpenRouterClient, model: str):
        self.llm = llm
        self.model = model
        self.tools = self._define_tools()

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        pass

    @abstractmethod
    def _define_tools(self) -> list[dict]:
        pass

    @abstractmethod
    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        pass

    async def run(self, context: AgentContext) -> AgentResult:
        """Execute agent: Think → Act → Create."""
        system = self._build_system(context)
        messages = [{"role": "user", "content": context.task}]
        all_outputs = []

        for _ in range(10):  # max iterations
            response = await self.llm.chat(
                model=self.model,
                messages=messages,
                system=system,
                tools=self.tools if self.tools else None,
                max_tokens=4096,
            )

            choice = response["choices"][0]
            message = choice["message"]
            finish_reason = choice.get("finish_reason", "stop")

            # Collect text output
            if message.get("content"):
                all_outputs.append(message["content"])

            # No tool calls — done
            tool_calls = message.get("tool_calls", [])
            if not tool_calls or finish_reason == "stop":
                break

            # Process tool calls
            messages.append(message)
            for tc in tool_calls:
                fn = tc["function"]
                tool_name = fn["name"]
                try:
                    tool_input = json.loads(fn["arguments"])
                except json.JSONDecodeError:
                    tool_input = {}

                result = await self._execute_tool(tool_name, tool_input)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result) if isinstance(result, dict) else str(result),
                })

        return AgentResult(
            success=True,
            output="\n\n".join(all_outputs),
            agent=self.name,
            metadata={"tenant_id": context.tenant_id, "model": self.model},
        )

    async def stream(self, context: AgentContext) -> AsyncIterator[str]:
        """Stream agent response as SSE events."""
        system = self._build_system(context)
        messages = [{"role": "user", "content": context.task}]

        yield f"data: {json.dumps({'type': 'agent:start', 'agent': self.name})}\n\n"

        for _ in range(10):
            full_content = ""
            tool_calls_acc: dict[int, dict] = {}

            async for chunk in self.llm.stream(
                model=self.model,
                messages=messages,
                system=system,
                tools=self.tools if self.tools else None,
                max_tokens=4096,
            ):
                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})

                # Stream text
                if delta.get("content"):
                    full_content += delta["content"]
                    yield f"data: {json.dumps({'type': 'message:stream', 'text': delta['content']})}\n\n"

                # Accumulate tool calls
                if delta.get("tool_calls"):
                    for tc in delta["tool_calls"]:
                        idx = tc.get("index", 0)
                        if idx not in tool_calls_acc:
                            tool_calls_acc[idx] = {
                                "id": tc.get("id", ""),
                                "function": {"name": "", "arguments": ""},
                            }
                        if tc.get("id"):
                            tool_calls_acc[idx]["id"] = tc["id"]
                        fn = tc.get("function", {})
                        if fn.get("name"):
                            tool_calls_acc[idx]["function"]["name"] = fn["name"]
                        if fn.get("arguments"):
                            tool_calls_acc[idx]["function"]["arguments"] += fn["arguments"]

                finish = choices[0].get("finish_reason")
                if finish == "stop":
                    break

            # No tool calls — done
            if not tool_calls_acc:
                break

            # Execute tool calls
            assistant_msg = {"role": "assistant", "content": full_content or ""}
            assistant_msg["tool_calls"] = [
                {"id": tc["id"], "type": "function", "function": tc["function"]}
                for tc in tool_calls_acc.values()
            ]
            messages.append(assistant_msg)

            for tc in tool_calls_acc.values():
                fn = tc["function"]
                try:
                    tool_input = json.loads(fn["arguments"])
                except json.JSONDecodeError:
                    tool_input = {}

                yield f"data: {json.dumps({'type': 'tool:call', 'tool': fn['name']})}\n\n"
                result = await self._execute_tool(fn["name"], tool_input)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result) if isinstance(result, dict) else str(result),
                })

        yield f"data: {json.dumps({'type': 'agent:complete', 'agent': self.name})}\n\n"

    def _build_system(self, context: AgentContext) -> str:
        return f"""{self.system_prompt}

## Context
- Tenant: {context.tenant_id}
- User: {context.user_id}
- Chat: {context.chat_id}

Follow Think → Act → Create:
1. THINK: Analyze the request
2. ACT: Use tools to gather data and execute
3. CREATE: Synthesize into actionable output"""

    async def close(self):
        pass
