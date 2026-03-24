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

from ..services.openrouter import OpenRouterClient
from ..skills.platform_skills import get_platform_skill_tools, PLATFORM_SKILLS
from ..protocols.state import AgentState, AgentStateUpdate, StateProgress, StateCompletion, StateError
from ..protocols.work import (
    AgentWorkState, AgentWorkModule, AgentAction, AgentActionType,
    CreatedEntity, WorkStartEvent, WorkActionEvent,
    EntityCreatedEvent, WorkCompleteEvent, WorkErrorEvent,
)
from ..protocols.artifacts import ArtifactEvent, ArtifactEventType, Artifact, ArtifactType, ArtifactPreview, ARTIFACT_DATA_SCHEMAS, validate_artifact_data
from ..protocols.events import MessageWithAttachments
from ..tools.erp_tool_definitions import (
    ERP_READ_TOOLS, ERP_WRITE_TOOLS, AGENT_WRITE_TOOL_MAP,
    ERP_TOOL_NAMES,
    VIDEO_STUDIO_TOOLS, AGENT_VIDEO_TOOL_MAP, VIDEO_TOOL_NAMES,
)
from ..tools.creative_tool_definitions import (
    CREATIVE_TOOLS, AGENT_CREATIVE_TOOL_MAP, CREATIVE_TOOL_NAMES,
)


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

    # Module context (subdomain architecture)
    module_subdomain: Optional[str] = None
    module_display_name: Optional[str] = None

    # Attachments (vision support, spec Section 11.8)
    attachments: list[dict] = field(default_factory=list)

    # Format-aware creation (Mission Control routing)
    artifact_format: Optional[str] = None  # e.g., "calendar", "deck", "brief"

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

    # Platform skill names for dispatch routing
    _platform_skill_names: set[str] = set(PLATFORM_SKILLS.keys())

    def __init__(self, client: OpenRouterClient, model: str,
                 erp_base_url: str = "", erp_api_key: str = "",
                 erp_toolkit=None, creative_registry=None):
        self.client = client
        self.model = model
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.erp_toolkit = erp_toolkit  # ERPToolkit for real ERP data access
        self.creative_registry = creative_registry  # CreativeRegistry for asset generation

        # Merge agent-specific tools + platform skills (Layer 2) + universal emit_artifact
        self.tools = self._define_tools() + get_platform_skill_tools() + [self._emit_artifact_tool_def()]

        agent_type = self._get_agent_type_key()

        # Inject ERP read tools (available to ALL agents when toolkit is present)
        if self.erp_toolkit:
            self.tools.extend(ERP_READ_TOOLS)
            # Inject write tools selectively based on agent type
            write_tool_names = AGENT_WRITE_TOOL_MAP.get(agent_type, [])
            if write_tool_names:
                for tool_def in ERP_WRITE_TOOLS:
                    if tool_def["function"]["name"] in write_tool_names:
                        self.tools.append(tool_def)

        # Inject creative tools selectively based on agent type
        if self.creative_registry:
            creative_tool_names = AGENT_CREATIVE_TOOL_MAP.get(agent_type, [])
            if creative_tool_names:
                for tool_def in CREATIVE_TOOLS:
                    if tool_def["function"]["name"] in creative_tool_names:
                        self.tools.append(tool_def)

        # Inject video studio tools selectively based on agent type
        if self.erp_toolkit:
            video_tool_names = AGENT_VIDEO_TOOL_MAP.get(agent_type, [])
            if video_tool_names:
                for tool_def in VIDEO_STUDIO_TOOLS:
                    if tool_def["function"]["name"] in video_tool_names:
                        self.tools.append(tool_def)

        # State tracking
        self._state = AgentState.IDLE
        self._work_state: Optional[AgentWorkState] = None
        self._created_entities: list[CreatedEntity] = []
        self._artifacts: list[Artifact] = []

        # Token usage tracking (accumulated across tool loops)
        self._input_tokens = 0
        self._output_tokens = 0

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

    def _get_agent_type_key(self) -> str:
        """Derive the agent registry key from the agent name (e.g. 'brief_agent' -> 'brief')."""
        n = self.name
        return n.removesuffix("_agent") if n.endswith("_agent") else n

    def _creative_capabilities_note(self) -> str:
        """Return system prompt note about creative capabilities if available."""
        if not self.creative_registry:
            return ""
        agent_type = self._get_agent_type_key()
        tools = AGENT_CREATIVE_TOOL_MAP.get(agent_type, [])
        if not tools:
            return ""
        return (
            "\n## Creative Asset Generation\n"
            f"You have access to these creative tools: {', '.join(tools)}.\n"
            "Quality tiers: draft (cheapest, fast), standard (balanced), premium (highest quality).\n"
            "Generated assets are temporary URLs — the ERP persists them to storage.\n"
            "For video compositions, generate individual assets first (images, voiceovers) "
            "then assemble them into a composition spec.\n"
        )

    # ============================================
    # ERP Toolkit Tool Handling
    # ============================================

    async def _handle_erp_tool(self, tool_name: str, args: dict,
                               context: "AgentContext") -> str:
        """Route ERP tool calls to ERPToolkit methods. Returns JSON string."""
        org_id = context.organization_id or context.tenant_id
        user_id = context.user_id
        tk = self.erp_toolkit

        try:
            # ── Read tools ──
            if tool_name == "get_client_context":
                data = await tk.get_client(org_id, args["client_id"])
            elif tool_name == "list_briefs":
                data = await tk.list_briefs(org_id, **args)
            elif tool_name == "list_content_posts":
                data = await tk.list_content_posts(org_id, **args)
            elif tool_name == "list_projects":
                data = await tk.list_projects(org_id, **args)
            elif tool_name == "get_analytics":
                data = await tk.get_analytics(org_id, **args)
            elif tool_name == "get_pending_reviews":
                data = await tk.get_pending_reviews(org_id, args["user_id"])
            elif tool_name == "get_workload":
                data = await tk.get_workload(org_id, **args)
            elif tool_name == "search_modules":
                data = await tk.search(org_id, **args)
            # ── Write tools ──
            elif tool_name == "create_brief":
                data = await tk.create_brief(org_id, user_id, args)
            elif tool_name == "create_content_posts":
                data = await tk.create_content_posts(org_id, user_id, args)
            elif tool_name == "create_project":
                data = await tk.create_project(org_id, user_id, args)
            elif tool_name == "create_media_plan":
                data = await tk.create_media_plan(org_id, user_id, args)
            elif tool_name == "update_post":
                post_id = args.pop("post_id")
                data = await tk.update_post(org_id, user_id, post_id, args)
            # ── Video Studio tools ──
            elif tool_name == "get_video_project":
                data = await tk.get_video_project(org_id, args["project_id"])
            elif tool_name == "create_video_project":
                data = await tk.create_video_project(org_id, user_id, args)
            elif tool_name == "update_video_composition":
                project_id = args.pop("project_id")
                data = await tk.update_video_composition(org_id, user_id, project_id, args)
            elif tool_name == "trigger_video_render":
                data = await tk.trigger_video_render(
                    org_id, user_id, args["project_id"], args.get("resolution", "1080p"),
                )
            elif tool_name == "get_video_templates":
                data = await tk.get_video_templates(org_id)
            else:
                data = {"error": f"Unknown ERP tool: {tool_name}"}
            return json.dumps(data)
        except Exception as e:
            return json.dumps({"error": f"ERP tool '{tool_name}' failed: {str(e)}"})

    # ============================================
    # Creative Registry Tool Handling
    # ============================================

    async def _handle_creative_tool(self, tool_name: str, args: dict) -> str:
        """Route creative tool calls to CreativeRegistry. Returns JSON string."""
        from ..providers.creative_registry import (
            GenerationRequest, AssetType, QualityTier,
        )

        try:
            tier = QualityTier(args.get("quality_tier", "standard"))

            if tool_name == "generate_image":
                req = GenerationRequest(
                    prompt=args["prompt"],
                    asset_type=AssetType.IMAGE,
                    quality_tier=tier,
                    resolution=args.get("resolution"),
                    aspect_ratio=args.get("aspect_ratio"),
                    reference_image_url=args.get("reference_image_url"),
                    num_variants=args.get("num_variants", 1),
                )
            elif tool_name == "generate_video":
                req = GenerationRequest(
                    prompt=args["prompt"],
                    asset_type=AssetType.VIDEO,
                    quality_tier=tier,
                    duration_seconds=args.get("duration_seconds", 5),
                    aspect_ratio=args.get("aspect_ratio", "16:9"),
                    reference_image_url=args.get("reference_image_url"),
                )
            elif tool_name == "generate_voiceover":
                req = GenerationRequest(
                    prompt=args["text"],
                    asset_type=AssetType.VOICE,
                    quality_tier=tier,
                    voice_id=args.get("voice_id"),
                )
            elif tool_name == "generate_presentation":
                req = GenerationRequest(
                    prompt=args["prompt"],
                    asset_type=AssetType.PRESENTATION,
                    quality_tier=tier,
                    num_slides=args.get("num_slides", 10),
                    style=args.get("style"),
                )
            elif tool_name == "generate_video_composition":
                req = GenerationRequest(
                    prompt="",
                    asset_type=AssetType.VIDEO_COMPOSITION,
                    scenes=args.get("scenes", []),
                )
            else:
                return json.dumps({"error": f"Unknown creative tool: {tool_name}"})

            result = await self.creative_registry.generate(req)
            return json.dumps({
                "asset_url": result.asset_url,
                "provider": result.provider_id,
                "model": result.model_id,
                "cost_usd": result.cost_usd,
                "duration_ms": result.duration_ms,
                "variants": result.variants,
                "metadata": result.metadata,
            })
        except Exception as e:
            return json.dumps({"error": f"Creative tool '{tool_name}' failed: {str(e)}"})

    # ============================================
    # Platform Skills (Layer 2)
    # ============================================

    async def _execute_platform_skill(
        self, skill_name: str, skill_input: dict, context: AgentContext
    ) -> str:
        """
        Execute a platform skill (Layer 2).

        Platform skills are processed by sending the structured input to the LLM
        with a skill-specific system prompt. The LLM applies agency expertise
        encoded in the skill definition to produce structured output.

        For skills that need ERP data (e.g., smart_assigner checking team availability),
        the agent should fetch that data via its own tools first and include it in the
        skill input.
        """
        import httpx

        skill = PLATFORM_SKILLS.get(skill_name)
        if not skill:
            return json.dumps({"error": f"Unknown platform skill: {skill_name}"})

        # Build a focused skill prompt
        skill_prompts = {
            "brief_quality_scorer": (
                "You are a brief quality assessment expert with 15+ years in professional services agencies.\n"
                "Score the following brief on a 0-100 scale.\n"
                "Return a JSON object with: score (int), grade (A/B/C/D/F), "
                "missing_fields (list), weak_areas (list of {field, issue, suggestion}), "
                "strengths (list), and overall_feedback (string)."
            ),
            "smart_assigner": (
                "You are a resource allocation expert for professional services agencies.\n"
                "Given the task description and requirements, recommend optimal team member assignments.\n"
                "Return a JSON object with: recommendations (list of {role, skills_needed, priority, "
                "estimated_hours}), assignment_rationale (string), risk_factors (list), "
                "and alternatives (list)."
            ),
            "scope_creep_detector": (
                "You are a scope management expert who protects agency profitability.\n"
                "Compare the current work against the original scope.\n"
                "Return a JSON object with: risk_level (low/medium/high/critical), "
                "deviations (list of {area, original, current, impact}), "
                "estimated_cost_impact (string), recommended_actions (list), "
                "and change_order_needed (bool)."
            ),
            "timeline_estimator": (
                "You are a project timeline estimation expert for creative and professional services.\n"
                "Estimate the project timeline with confidence intervals.\n"
                "Return a JSON object with: estimated_days (int), confidence (low/medium/high), "
                "range_optimistic_days (int), range_pessimistic_days (int), "
                "phases (list of {name, days, dependencies}), risks (list), "
                "and assumptions (list)."
            ),
        }

        system_prompt = skill_prompts.get(skill_name, f"Execute the {skill_name} skill.")

        # Use the agent's own LLM client to run the skill
        try:
            response = await self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": json.dumps(skill_input)}],
                system=system_prompt,
                max_tokens=2048,
            )
            # Track token usage from skill call
            usage = response.get("usage", {})
            self._input_tokens += usage.get("prompt_tokens", 0)
            self._output_tokens += usage.get("completion_tokens", 0)

            return self._extract_text(response) or json.dumps({"error": "Empty skill response"})
        except Exception as e:
            return json.dumps({"error": f"Platform skill '{skill_name}' failed: {str(e)}"})

    # ============================================
    # Universal Artifact Tool
    # ============================================

    @staticmethod
    def _emit_artifact_tool_def() -> dict:
        """Tool definition for the universal emit_artifact tool."""
        return {
            "type": "function",
            "function": {
                "name": "emit_artifact",
                "description": "Emit a structured artifact for display in Mission Control. Use this instead of including full artifact content as inline text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "artifact_type": {
                            "type": "string",
                            "enum": [t.value for t in ArtifactType],
                            "description": "Type of artifact being created",
                        },
                        "title": {
                            "type": "string",
                            "description": "Human-readable title for the artifact",
                        },
                        "data": {
                            "type": "object",
                            "description": "Structured artifact data matching the schema for this type",
                        },
                        "preview_type": {
                            "type": "string",
                            "enum": ["html", "markdown", "json"],
                            "description": "Format of the preview content",
                        },
                        "preview_content": {
                            "type": "string",
                            "description": "Short preview/summary for UI card display",
                        },
                    },
                    "required": ["artifact_type", "title", "data"],
                },
            },
        }

    async def _handle_emit_artifact(self, tool_input: dict, context: "AgentContext") -> dict:
        """Handle the emit_artifact tool call."""
        # Validate artifact data against schema
        artifact_type = ArtifactType(tool_input["artifact_type"])
        is_valid, errors = validate_artifact_data(artifact_type, tool_input["data"])
        if not is_valid:
            return {"status": "validation_error", "errors": errors}

        artifact = Artifact(
            id=str(uuid4()),
            type=ArtifactType(tool_input["artifact_type"]),
            title=tool_input["title"],
            data=tool_input["data"],
            status="final",
            preview=ArtifactPreview(
                type=tool_input.get("preview_type", "markdown"),
                content=tool_input.get("preview_content", ""),
            ) if tool_input.get("preview_content") else None,
            client_id=context.client_id,
            project_id=context.project_id,
        )
        await self._emit_artifact_create(context, artifact)
        await self._emit_artifact_complete(context, artifact)
        return {"status": "artifact_emitted", "artifact_id": artifact.id}

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
        artifact_emitted = False

        while True:
            # Force emit_artifact on first call when artifact_format is set
            tc = {"type": "function", "function": {"name": "emit_artifact"}} if (context.artifact_format and not artifact_emitted) else None

            # THINK: Get response via OpenRouter
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                system=self._build_system_prompt(context),
                tools=self.tools,
                max_tokens=4096,
                tool_choice=tc,
            )

            # Track token usage
            usage = response.get("usage", {})
            self._input_tokens += usage.get("prompt_tokens", 0)
            self._output_tokens += usage.get("completion_tokens", 0)

            choice = response["choices"][0]
            message = choice["message"]
            finish_reason = choice.get("finish_reason", "stop")

            # Check if we're done (no tool calls)
            tool_calls = message.get("tool_calls", [])
            text_content = message.get("content", "") or ""

            if not tool_calls:
                if text_content:
                    all_outputs.append(text_content)
                break

            # Capture any text before tool calls
            if text_content:
                all_outputs.append(text_content)

            # ACT: Process tool calls -> transition to WORKING
            messages.append({
                "role": "assistant",
                "content": text_content,
                "tool_calls": tool_calls,
            })

            for tc in tool_calls:
                func = tc.get("function", {})
                tool_name = func.get("name", "")
                try:
                    tool_input = json.loads(func.get("arguments", "{}"))
                except json.JSONDecodeError:
                    tool_input = {}

                # Transition to WORKING on first tool call
                if self._state != AgentState.WORKING:
                    await self._set_state(AgentState.WORKING, context)

                # Route: emit_artifact, ERP toolkit, platform skill, or agent-specific tool
                if tool_name == "emit_artifact":
                    result = await self._handle_emit_artifact(tool_input, context)
                    artifact_emitted = True
                elif self.erp_toolkit and tool_name in ERP_TOOL_NAMES:
                    result = await self._handle_erp_tool(tool_name, tool_input, context)
                elif self.creative_registry and tool_name in CREATIVE_TOOL_NAMES:
                    result = await self._handle_creative_tool(tool_name, tool_input)
                elif tool_name in self._platform_skill_names:
                    result = await self._execute_platform_skill(tool_name, tool_input, context)
                else:
                    result = await self._execute_tool(tool_name, tool_input)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(result) if not isinstance(result, str) else result,
                })

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
            metadata={
                "agent": self.name,
                "tenant_id": context.tenant_id,
                "input_tokens": self._input_tokens,
                "output_tokens": self._output_tokens,
            },
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

        # Wire up SSE callback so artifact events flow into the stream
        event_queue: asyncio.Queue[str] = asyncio.Queue()

        async def sse_callback(event: dict):
            await event_queue.put(f"data: {json.dumps(event)}\n\n")

        context._sse_callback = sse_callback

        messages = [self._build_user_message(context)]
        artifact_emitted = False

        while True:
            # Accumulate the full response from streaming chunks
            full_text = ""
            tool_calls_accum: dict[int, dict] = {}  # index -> {id, function: {name, arguments}}

            # Force emit_artifact on first call when artifact_format is set
            tc = {"type": "function", "function": {"name": "emit_artifact"}} if (context.artifact_format and not artifact_emitted) else None

            async for chunk in self.client.stream(
                model=self.model,
                messages=messages,
                system=self._build_system_prompt(context),
                tools=self.tools,
                max_tokens=4096,
                tool_choice=tc,
            ):
                choices = chunk.get("choices", [])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})

                # Stream text content
                if delta.get("content"):
                    full_text += delta["content"]
                    yield f"data: {json.dumps({'type': 'message:stream', 'text': delta['content']})}\n\n"

                # Accumulate tool calls from deltas
                for tc_delta in delta.get("tool_calls", []):
                    idx = tc_delta.get("index", 0)
                    if idx not in tool_calls_accum:
                        tool_calls_accum[idx] = {
                            "id": tc_delta.get("id", ""),
                            "type": "function",
                            "function": {"name": "", "arguments": ""},
                        }
                    if tc_delta.get("id"):
                        tool_calls_accum[idx]["id"] = tc_delta["id"]
                    func_delta = tc_delta.get("function", {})
                    if func_delta.get("name"):
                        tool_calls_accum[idx]["function"]["name"] = func_delta["name"]
                    if func_delta.get("arguments"):
                        tool_calls_accum[idx]["function"]["arguments"] += func_delta["arguments"]

            # No tool calls — we're done
            if not tool_calls_accum:
                break

            # Handle tool calls
            tool_calls = [tool_calls_accum[i] for i in sorted(tool_calls_accum)]
            messages.append({
                "role": "assistant",
                "content": full_text,
                "tool_calls": tool_calls,
            })

            for tc in tool_calls:
                func = tc.get("function", {})
                tool_name = func.get("name", "")
                try:
                    tool_input = json.loads(func.get("arguments", "{}"))
                except json.JSONDecodeError:
                    tool_input = {}
                if tool_name == "emit_artifact":
                    result = await self._handle_emit_artifact(tool_input, context)
                    artifact_emitted = True
                elif self.erp_toolkit and tool_name in ERP_TOOL_NAMES:
                    result = await self._handle_erp_tool(tool_name, tool_input, context)
                elif self.creative_registry and tool_name in CREATIVE_TOOL_NAMES:
                    result = await self._handle_creative_tool(tool_name, tool_input)
                elif tool_name in self._platform_skill_names:
                    result = await self._execute_platform_skill(tool_name, tool_input, context)
                else:
                    result = await self._execute_tool(tool_name, tool_input)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(result) if not isinstance(result, str) else result,
                })

            # Drain any SSE events queued during tool execution (e.g. artifact events)
            while not event_queue.empty():
                yield await event_queue.get()

        # Drain any remaining queued SSE events
        while not event_queue.empty():
            yield await event_queue.get()

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
        """Build system prompt with context including module scope and artifact protocol."""
        module_line = ""
        if context.module_subdomain:
            module_line = f"\n- Module: {context.module_display_name or context.module_subdomain} ({context.module_subdomain}.spokestack.app)"

        # Format-aware creation: inject schema when artifact_format is specified
        format_section = ""
        if context.artifact_format:
            try:
                artifact_type = ArtifactType(context.artifact_format)
                schema = ARTIFACT_DATA_SCHEMAS.get(artifact_type, {})
            except ValueError:
                schema = {}
            schema_str = json.dumps(schema, indent=2) if schema else "No specific schema defined."
            format_section = f"""

## Output Format
The user's request should be delivered as a {context.artifact_format} artifact.
Expected data structure:
{schema_str}

Emit the result using the emit_artifact tool with type="{context.artifact_format}"."""

        # Canvas context injection (Phase 3: multi-step workflow context from upstream nodes)
        canvas_section = ""
        project_context = context.metadata.get("project_context")
        if project_context:
            ctx_lines = []
            for key, value in project_context.items():
                val_str = json.dumps(value, indent=2) if isinstance(value, (dict, list)) else str(value)
                ctx_lines.append(f"- {key}: {val_str[:2000]}")
            canvas_section = (
                "\n\n## Project Context (from previous steps)\n"
                + "\n".join(ctx_lines)
                + "\n\nUse this context to inform your work. "
                "Do not ask for information that's already provided above.\n"
            )

        return f"""{self.system_prompt}

## Context
- Tenant ID: {context.tenant_id}
- User ID: {context.user_id}
- Chat ID: {context.chat_id}{module_line}
- Additional context: {context.metadata}{canvas_section}

## Approach
Follow the Think → Act → Create paradigm:
1. THINK: Analyze the request, understand requirements
2. ACT: Use tools to gather data, validate, iterate
3. CREATE: Synthesize findings into actionable output

## Artifact Output Protocol
When you produce a deliverable (brief, calendar, deck, report, table, chart,
contract, document, etc.), you MUST emit it as a structured artifact using the
`emit_artifact` tool rather than including the full content as inline text.

Steps:
1. Call emit_artifact with the artifact_type, title, and structured data
2. Continue with a brief text summary in your response
3. Do NOT dump the full artifact content as text

Available artifact types: calendar, brief, document, deck, moodboard, script,
storyboard, shot_list, report, table, chart, contract, survey, course, workflow{format_section}
{self._creative_capabilities_note()}
"""

    def _extract_text(self, response: dict) -> str:
        """Extract text content from OpenRouter response dict."""
        choices = response.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "") or ""
        return ""
