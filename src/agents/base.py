"""
Base Agent with Integration Spec v2.0 Support

Implements:
- Think → Act → Create paradigm
- Agent State Machine (spec Section 1)
- Agent Work Protocol with SSE events (spec Section 11)
- Vision/attachment support (spec Section 11.8)
- Artifact creation and streaming (spec Section 2)
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4
import asyncio
import json
import anthropic

from ..protocols.state import AgentState, AgentStateUpdate, StateProgress, StateCompletion, StateError
from ..protocols.work import (
    AgentWorkState, AgentWorkModule, AgentAction, AgentActionType,
    CreatedEntity, WorkStartEvent, WorkActionEvent,
    EntityCreatedEvent, WorkCompleteEvent, WorkErrorEvent,
)
from ..protocols.artifacts import ArtifactEvent, ArtifactEventType, Artifact, ArtifactType
from ..protocols.events import MessageWithAttachments


@dataclass
class AgentContext:
    """Context passed to agent during execution."""
    tenant_id: str
    user_id: str
    task: str
    metadata: dict = field(default_factory=dict)

    # Integration spec additions
    chat_id: str = field(default_factory=lambda: str(uuid4()))
    organization_id: Optional[str] = None
    api_token: Optional[str] = None
    client_id: Optional[str] = None
    project_id: Optional[str] = None
    session_id: Optional[str] = None

    # Attachments (vision support, spec Section 11.8)
    attachments: list[dict] = field(default_factory=list)

    # SSE callback for emitting events
    _sse_callback: Optional[Callable] = field(default=None, repr=False)

    async def emit_sse(self, event: dict) -> None:
        """Emit an SSE event to the client."""
        if self._sse_callback:
            await self._sse_callback(event)


@dataclass
class AgentResult:
    """Result from agent execution."""
    success: bool
    output: str
    artifacts: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    # Integration spec additions
    suggested_actions: list[dict] = field(default_factory=list)
    created_entities: list[dict] = field(default_factory=list)
    state: str = "complete"
    completion: Optional[dict] = None


class BaseAgent(ABC):
    """
    Base class for all agents following Think → Act → Create paradigm.

    Now supports:
    - Agent State Machine (idle -> thinking -> working -> complete/error)
    - Agent Work Protocol (SSE events for 3-column Mission Control UI)
    - Vision/attachment support
    - Artifact creation and streaming
    """

    def __init__(self, client: anthropic.AsyncAnthropic, model: str,
                 erp_base_url: str = "", erp_api_key: str = ""):
        self.client = client
        self.model = model
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.tools = self._define_tools()

        # State tracking
        self._state = AgentState.IDLE
        self._work_state: Optional[AgentWorkState] = None
        self._created_entities: list[CreatedEntity] = []
        self._artifacts: list[Artifact] = []

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

    async def close(self) -> None:
        """Clean up resources."""
        pass

    # ============================================
    # State Machine
    # ============================================

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    async def _set_state(self, state: AgentState, context: AgentContext, **kwargs) -> None:
        """Update agent state and emit SSE event."""
        self._state = state
        update = AgentStateUpdate(
            chat_id=context.chat_id,
            agent_id=self.name,
            agent_type=self.name,
            timestamp=self._now_iso(),
            state=state,
            **kwargs,
        )
        await context.emit_sse({"type": "state:update", "payload": update.model_dump(exclude_none=True)})

    # ============================================
    # Work Protocol Helpers
    # ============================================

    async def _emit_work_start(self, context: AgentContext, module: AgentWorkModule,
                               route: str, pending_fields: list[str] = None) -> None:
        """Emit work_start SSE event."""
        self._work_state = AgentWorkState(
            chat_id=context.chat_id,
            is_working=True,
            current_module=module,
            current_route=route,
            pending_fields=pending_fields or [],
        )
        event = WorkStartEvent(
            module=module,
            route=route,
            pending_fields=pending_fields or [],
        )
        await context.emit_sse(event.model_dump())

    async def _emit_work_action(self, context: AgentContext, action_type: AgentActionType,
                                module: Optional[AgentWorkModule] = None,
                                route: Optional[str] = None,
                                field_name: Optional[str] = None,
                                field_label: Optional[str] = None,
                                value: Any = None,
                                display_value: Optional[str] = None,
                                status: str = "filled",
                                message: Optional[str] = None) -> None:
        """Emit an action SSE event."""
        action = AgentAction(
            id=f"act_{uuid4().hex[:8]}",
            type=action_type,
            timestamp=self._now_iso(),
            module=module or (self._work_state.current_module if self._work_state else None),
            route=route or (self._work_state.current_route if self._work_state else None),
            field=field_name,
            field_label=field_label,
            value=value,
            display_value=display_value,
            status=status,
            message=message,
        )
        if self._work_state:
            self._work_state.actions.append(action)
            if field_name and status == "filled":
                self._work_state.completed_fields.append(field_name)
                if field_name in self._work_state.pending_fields:
                    self._work_state.pending_fields.remove(field_name)

        event = WorkActionEvent(action=action)
        await context.emit_sse(event.model_dump())

    async def _emit_entity_created(self, context: AgentContext, entity_id: str,
                                    entity_type: str, title: str,
                                    module: AgentWorkModule, url: str) -> None:
        """Emit entity_created SSE event."""
        entity = CreatedEntity(
            id=entity_id,
            type=entity_type,
            title=title,
            module=module,
            url=url,
        )
        self._created_entities.append(entity)
        if self._work_state:
            self._work_state.created_entities.append(entity)

        event = EntityCreatedEvent(entity=entity)
        await context.emit_sse(event.model_dump())

    async def _emit_work_complete(self, context: AgentContext) -> None:
        """Emit work_complete SSE event."""
        state_snapshot = {
            "isWorking": False,
            "createdEntities": [e.model_dump() for e in self._created_entities],
        }
        if self._work_state:
            self._work_state.is_working = False

        event = WorkCompleteEvent(state=state_snapshot)
        await context.emit_sse(event.model_dump())

    async def _emit_work_error(self, context: AgentContext, error: str) -> None:
        """Emit work_error SSE event."""
        if self._work_state:
            self._work_state.error = error
            self._work_state.is_working = False

        event = WorkErrorEvent(error=error)
        await context.emit_sse(event.model_dump())

    # ============================================
    # Artifact Helpers
    # ============================================

    async def _emit_artifact_create(self, context: AgentContext, artifact: Artifact) -> None:
        """Emit artifact:create SSE event."""
        self._artifacts.append(artifact)
        event = ArtifactEvent(
            event=ArtifactEventType.CREATE,
            chat_id=context.chat_id,
            agent_id=self.name,
            artifact=artifact,
        )
        await context.emit_sse({"type": "artifact:create", "payload": event.model_dump(exclude_none=True)})

    async def _emit_artifact_update(self, context: AgentContext, artifact: Artifact) -> None:
        """Emit artifact:update SSE event."""
        event = ArtifactEvent(
            event=ArtifactEventType.UPDATE,
            chat_id=context.chat_id,
            agent_id=self.name,
            artifact=artifact,
        )
        await context.emit_sse({"type": "artifact:update", "payload": event.model_dump(exclude_none=True)})

    async def _emit_artifact_complete(self, context: AgentContext, artifact: Artifact) -> None:
        """Emit artifact:complete SSE event."""
        event = ArtifactEvent(
            event=ArtifactEventType.COMPLETE,
            chat_id=context.chat_id,
            agent_id=self.name,
            artifact=artifact,
        )
        await context.emit_sse({"type": "artifact:complete", "payload": event.model_dump(exclude_none=True)})

    # ============================================
    # Message Building (Vision Support)
    # ============================================

    def _build_user_message(self, context: AgentContext) -> dict:
        """Build user message with optional vision/attachment support."""
        if context.attachments:
            msg = MessageWithAttachments(
                content=context.task,
                attachments=[],
            )
            for att in context.attachments:
                from ..protocols.events import Attachment
                msg.attachments.append(Attachment(**att))
            return msg.to_claude_message()
        return {"role": "user", "content": context.task}

    # ============================================
    # Core Execution
    # ============================================

    async def run(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent loop: Think → Act → Create
        With state machine transitions and work event emission.
        """
        # THINKING
        await self._set_state(AgentState.THINKING, context)

        messages = [self._build_user_message(context)]
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
                final_text = self._extract_text(response)
                all_outputs.append(final_text)
                break

            # ACT: Process tool calls -> transition to WORKING
            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    # Transition to WORKING on first tool call
                    if self._state != AgentState.WORKING:
                        await self._set_state(AgentState.WORKING, context)
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

        # COMPLETE
        completion = StateCompletion(
            summary=all_outputs[-1][:200] if all_outputs else "Task completed",
            artifact_ids=[a.id for a in self._artifacts],
        )
        await self._set_state(
            AgentState.COMPLETE, context,
            completion=completion,
        )

        return AgentResult(
            success=True,
            output="\n\n".join(all_outputs),
            artifacts=[a.model_dump() for a in self._artifacts],
            metadata={"agent": self.name, "tenant_id": context.tenant_id},
            created_entities=[e.model_dump() for e in self._created_entities],
            state="complete",
            completion=completion.model_dump(),
        )

    async def stream(self, context: AgentContext) -> AsyncIterator[str]:
        """
        Stream agent responses for real-time updates.
        Emits SSE events for state changes, work actions, and artifacts.
        """
        # THINKING
        state_event = AgentStateUpdate(
            chat_id=context.chat_id,
            agent_id=self.name,
            agent_type=self.name,
            timestamp=self._now_iso(),
            state=AgentState.THINKING,
        )
        yield state_event.to_sse()

        messages = [self._build_user_message(context)]

        while True:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=4096,
                system=self._build_system_prompt(context),
                tools=self.tools,
                messages=messages,
            ) as stream:
                async for event in stream:
                    if hasattr(event, "type"):
                        if event.type == "content_block_delta":
                            if hasattr(event.delta, "text"):
                                yield f"data: {json.dumps({'type': 'message:stream', 'text': event.delta.text})}\n\n"

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

        # Emit completion
        completion_event = AgentStateUpdate(
            chat_id=context.chat_id,
            agent_id=self.name,
            agent_type=self.name,
            timestamp=self._now_iso(),
            state=AgentState.COMPLETE,
            completion=StateCompletion(
                summary="Task completed",
                artifact_ids=[a.id for a in self._artifacts],
            ),
        )
        yield completion_event.to_sse()

    def _build_system_prompt(self, context: AgentContext) -> str:
        """Build system prompt with context."""
        return f"""{self.system_prompt}

## Context
- Tenant ID: {context.tenant_id}
- User ID: {context.user_id}
- Chat ID: {context.chat_id}
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
