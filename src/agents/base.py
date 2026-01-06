from abc import ABC, abstractmethod
from typing import Any, AsyncIterator
from dataclasses import dataclass, field
import anthropic


@dataclass
class AgentContext:
    """Context passed to agent during execution."""
    tenant_id: str
    user_id: str
    task: str
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent execution."""
    success: bool
    output: str
    artifacts: list[dict] = field(default_factory=list)  # Documents, assets, etc.
    metadata: dict = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all agents following Think → Act → Create paradigm.
    """

    def __init__(self, client: anthropic.AsyncAnthropic, model: str):
        self.client = client
        self.model = model
        self.tools = self._define_tools()

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent identifier."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt defining agent behavior."""
        pass

    @abstractmethod
    def _define_tools(self) -> list[dict]:
        """Define tools available to this agent."""
        pass

    @abstractmethod
    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute a tool and return result."""
        pass

    async def run(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent loop: Think → Act → Create
        """
        messages = [{"role": "user", "content": context.task}]
        all_outputs = []

        while True:
            # THINK: Get Claude's response
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self._build_system_prompt(context),
                tools=self.tools,
                messages=messages,
            )

            # Check if we're done (no more tool calls)
            if response.stop_reason == "end_turn":
                # CREATE: Extract final output
                final_text = self._extract_text(response)
                all_outputs.append(final_text)
                break

            # ACT: Process tool calls
            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    result = await self._execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })
                elif block.type == "text":
                    all_outputs.append(block.text)

            if tool_results:
                messages.append({"role": "user", "content": tool_results})

        return AgentResult(
            success=True,
            output="\n\n".join(all_outputs),
            metadata={"agent": self.name, "tenant_id": context.tenant_id},
        )

    async def stream(self, context: AgentContext) -> AsyncIterator[str]:
        """Stream agent responses for real-time updates."""
        messages = [{"role": "user", "content": context.task}]

        while True:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=4096,
                system=self._build_system_prompt(context),
                tools=self.tools,
                messages=messages,
            ) as stream:
                collected_content = []

                async for event in stream:
                    if hasattr(event, "type"):
                        if event.type == "content_block_delta":
                            if hasattr(event.delta, "text"):
                                yield event.delta.text

                response = await stream.get_final_message()

            if response.stop_reason == "end_turn":
                break

            # Handle tool calls
            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    result = await self._execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })

            if tool_results:
                messages.append({"role": "user", "content": tool_results})

    def _build_system_prompt(self, context: AgentContext) -> str:
        """Build system prompt with context."""
        return f"""{self.system_prompt}

## Context
- Tenant ID: {context.tenant_id}
- User ID: {context.user_id}
- Additional context: {context.metadata}

## Approach
Follow the Think → Act → Create paradigm:
1. THINK: Analyze the request, understand requirements
2. ACT: Use tools to gather data, validate, iterate
3. CREATE: Synthesize findings into actionable output
"""

    def _extract_text(self, response) -> str:
        """Extract text content from response."""
        texts = []
        for block in response.content:
            if hasattr(block, "text"):
                texts.append(block.text)
        return "\n".join(texts)
