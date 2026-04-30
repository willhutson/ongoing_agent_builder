"""
Core Router — API endpoints for spokestack-core organizations.

Phase 3 additions:
- Auto-inject ContextEntry records into agent system prompts
- Context-aware intent classification (usage patterns + entity name matching)
- Agent handoff detection (delegate_to_agent tool call → structured response)
"""

import json
import logging
import os
import uuid
from typing import Any, Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.agents.base import AgentContext
from src.services.openrouter import OpenRouterClient
from src.services.core_config_builder import (
    build_agent_config, get_available_agents, CORE_AGENT_TYPES,
    AGENT_MODEL_MAP, tier_has_access, AGENT_TIER_REQUIREMENTS,
)
from src.services.context_injector import inject_context_into_prompt
from src.tools.core_tool_definitions import (
    CORE_INTENT_PATTERNS, ENTERPRISE_INTENT_PATTERNS,
    DAM_INTENT_PATTERNS, EVENT_INTENT_PATTERNS,
)
from src.tools.core_toolkit import CoreToolkit
from src.tools.spokestack_handoff import is_handoff_tool_call, build_handoff_response
from src.modules import registry_store
from src.modules.module_checker import get_installed_modules
from src.modules.upsell_messages import get_upsell_message
from src.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/core", tags=["spokestack-core"])


# ══════════════════════════════════════════════════════════════
# Module Agent Type Mapping
# ══════════════════════════════════════════════════════════════

CORE_AGENT_BYPASS = {
    "core_onboarding", "core_tasks", "core_projects",
    "core_briefs", "core_orders",
}

MODULE_AGENT_TYPES: dict[str, str] = {
    "crm": "CRM",
    "social_publishing": "SOCIAL_PUBLISHING",
    "content_studio": "CONTENT_STUDIO",
    "analytics": "ANALYTICS",
    "surveys": "SURVEYS",
    "listening": "LISTENING",
    "media_buying": "MEDIA_BUYING",
    "lms": "LMS",
    "nps": "NPS",
    "time_leave": "TIME_LEAVE",
    "boards": "BOARDS",
    "finance": "FINANCE",
    "workflows": "WORKFLOWS",
    # Enterprise modules
    "spokechat": "SPOKECHAT",
    "delegation": "DELEGATION",
    "access_control": "ACCESS_CONTROL",
    "api_management": "API_MANAGEMENT",
    "builder": "BUILDER",
}

# Enterprise module → primary agent routing (no new agent types — use existing)
ENTERPRISE_MODULE_AGENT_MAP: dict[str, str] = {
    "SPOKECHAT": "gateway_slack",
    "DELEGATION": "resource",
    "ACCESS_CONTROL": "instance_onboarding",
    "API_MANAGEMENT": "instance_onboarding",
    "BUILDER": "prompt_helper",
}


# ══════════════════════════════════════════════════════════════
# Request / Response Models
# ══════════════════════════════════════════════════════════════


class CoreExecuteRequest(BaseModel):
    """Request to execute a core agent.

    Accepts both org_id and tenant_id for compatibility —
    spokestack-core sends tenant_id, some clients send org_id.
    """
    task: str
    agent_type: Optional[str] = None
    org_id: Optional[str] = None
    tenant_id: Optional[str] = None  # Alias for org_id (spokestack-core compat)
    org_name: str = ""
    org_tier: str = "FREE"
    user_id: str = "system"  # Default to system if not provided
    session_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    stream: bool = False
    context_entries: list[dict] = Field(default_factory=list)  # ContextEntry records from core
    integrations: list[dict] = Field(default_factory=list)     # Active integration records
    recent_events: list[dict] = Field(default_factory=list)    # Last N org events
    conversation_history: Optional[list[dict]] = None  # Accepted, not used in core path

    @property
    def resolved_org_id(self) -> str:
        """Return org_id, falling back to tenant_id."""
        return self.org_id or self.tenant_id or ""


class HandoffMetadata(BaseModel):
    """Structured handoff data when an agent delegates to another."""
    type: Literal["handoff"] = "handoff"
    target_agent: str
    context_summary: str
    reason: str


class CoreExecuteResponse(BaseModel):
    """Response from core agent execution."""
    execution_id: str
    status: str  # "completed", "streaming", "gated", "module_required", "handoff"
    output: Optional[str] = None
    agent_type: Optional[str] = None
    upgrade_message: Optional[str] = None
    upsell: bool = False
    handoff: Optional[HandoffMetadata] = None
    token_usage: Optional[dict] = None


class ModuleAgentDefinition(BaseModel):
    """Serialized module agent definition from marketplace installer."""
    name: str
    slug: str
    system_prompt: str = ""
    tools: list[dict] = Field(default_factory=list)
    intent_patterns: list[str] = Field(default_factory=list)
    context_read_categories: list[str] = Field(default_factory=list)
    context_write_categories: list[str] = Field(default_factory=list)


class RegisterAgentRequest(BaseModel):
    """Request to register a marketplace module agent (legacy endpoint)."""
    org_id: str
    agent: ModuleAgentDefinition


# ══════════════════════════════════════════════════════════════
# Core Agent Registry
#
# CORE_AGENT_CLASSES: 22 agents directly callable via /api/v1/core/execute
# Additional 50+ agents in src/agents/ are served via:
#   - ERP integration (/api/v1/agent/execute) — see src/api/erp_integration.py
#   - Module registration (/api/v1/core/modules/register) — persistent registry
#   - Dynamic agent loading — see src/services/dynamic_module_registry.py
# See: src/agents/README.md for the full registry of all agent classes
# ══════════════════════════════════════════════════════════════

CORE_AGENT_CLASSES = {
    # Canonical routing types (MC translation targets — use CoreTasksAgent as base)
    "assistant":        "src.agents.core_tasks_agent.CoreTasksAgent",
    "brief_writer":     "src.agents.core_briefs_agent.CoreBriefsAgent",
    "project_manager":  "src.agents.core_projects_agent.CoreProjectsAgent",
    "analyst":          "src.agents.core_tasks_agent.CoreTasksAgent",
    "content_creator":  "src.agents.core_briefs_agent.CoreBriefsAgent",
    "crm_manager":      "src.agents.core_orders_agent.CoreOrdersAgent",
    "order_manager":    "src.agents.core_orders_agent.CoreOrdersAgent",
    # Core agents
    "core_onboarding": "src.agents.core_onboarding_agent.CoreOnboardingAgent",
    "core_tasks":      "src.agents.core_tasks_agent.CoreTasksAgent",
    "core_projects":   "src.agents.core_projects_agent.CoreProjectsAgent",
    "core_briefs":     "src.agents.core_briefs_agent.CoreBriefsAgent",
    "core_orders":     "src.agents.core_orders_agent.CoreOrdersAgent",
    # PR / Communications agents
    "media_relations_manager": "src.agents.comms_pr_agents.MediaRelationsAgent",
    "press_release_writer":    "src.agents.comms_pr_agents.PressReleaseAgent",
    "crisis_manager":          "src.agents.comms_pr_agents.CrisisManagerAgent",
    "client_reporter":         "src.agents.comms_pr_agents.ClientReporterAgent",
    "influencer_manager":      "src.agents.comms_pr_agents.InfluencerManagerAgent",
    "event_planner":           "src.agents.comms_pr_agents.EventPlannerAgent",
    # Marketplace module agents
    "board_manager":           "src.agents.marketplace_agents.BoardManagerAgent",
    "workflow_designer":       "src.agents.marketplace_agents.WorkflowDesignerAgent",
    "social_listener":         "src.agents.marketplace_agents.SocialListenerAgent",
    "nps_analyst":             "src.agents.marketplace_agents.NpsAnalystAgent",
    "chat_operator":           "src.agents.marketplace_agents.ChatOperatorAgent",
    "portal_manager":          "src.agents.marketplace_agents.PortalManagerAgent",
    "delegation_coordinator":  "src.agents.marketplace_agents.DelegationCoordinatorAgent",
    "access_admin":            "src.agents.marketplace_agents.AccessAdminAgent",
    "module_builder":          "src.agents.marketplace_agents.ModuleBuilderAgent",
    "module_reviewer":         "src.agents.review_agents.ModuleReviewerAgent",
    # Operations agents
    "workflow_selector":       "src.agents.workflow_selector_agent.WorkflowSelectorAgent",
}


def _load_agent_class(agent_type: str):
    """Dynamically import and return the agent class."""
    class_path = CORE_AGENT_CLASSES.get(agent_type)
    if not class_path:
        raise ValueError(f"Unknown core agent type: {agent_type}")

    module_path, class_name = class_path.rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


# ══════════════════════════════════════════════════════════════
# Cached Integrations Fetcher (5-minute TTL)
# ══════════════════════════════════════════════════════════════

import time as _time

_integrations_cache: dict[str, tuple[list[dict], float]] = {}
_INTEGRATIONS_TTL = 300  # 5 minutes

_events_cache: dict[str, tuple[list[dict], float]] = {}
_EVENTS_TTL = 120  # 2 minutes


async def _get_cached_integrations(org_id: str, toolkit) -> list[dict]:
    """Fetch integrations with 5-minute TTL cache."""
    now = _time.monotonic()
    cached = _integrations_cache.get(org_id)
    if cached and now < cached[1]:
        return cached[0]

    try:
        result = await toolkit.list_integrations()
        connections = result.get("connections", result.get("data", []))
        if isinstance(connections, list):
            _integrations_cache[org_id] = (connections, now + _INTEGRATIONS_TTL)
            return connections
    except Exception as e:
        logger.debug(f"Failed to fetch integrations for {org_id}: {e}")
        if cached:
            return cached[0]
    return []


async def _get_cached_events(org_id: str, toolkit) -> list[dict]:
    """Fetch recent events (last 15 min) with 2-minute TTL cache."""
    now = _time.monotonic()
    cached = _events_cache.get(org_id)
    if cached and now < cached[1]:
        return cached[0]

    try:
        from datetime import datetime, timedelta, timezone as tz
        since = (datetime.now(tz.utc) - timedelta(minutes=15)).isoformat()
        result = await toolkit.list_recent_events(limit=10, since=since)
        events = result.get("data", result) if isinstance(result, dict) else result
        if isinstance(events, list):
            _events_cache[org_id] = (events, now + _EVENTS_TTL)
            return events
    except Exception as e:
        logger.debug(f"Failed to fetch events for {org_id}: {e}")
        if cached:
            return cached[0]
    return []


# ══════════════════════════════════════════════════════════════
# Context-Aware Intent Classification
# ══════════════════════════════════════════════════════════════


def score_intent_from_context(
    message: str,
    context_entries: list[dict],
    keyword_scores: dict[str, float],
) -> dict[str, float]:
    """
    Adjust intent scores based on:
    1. Recent agent usage patterns (PATTERN entries with category="agent.usage")
    2. Active entity name matches in the message
    """
    adjusted = dict(keyword_scores)
    message_lower = message.lower()

    for entry in (context_entries or []):
        entry_type = entry.get("entryType", "")
        category = entry.get("category", "")
        value = entry.get("value") or {}

        # Boost for recent usage pattern
        if entry_type == "PATTERN" and category == "agent.usage":
            if isinstance(value, dict):
                agent_type = value.get("agent_type", "")
                usage_count = value.get("count_7d", 0)
                if agent_type and usage_count >= 10:
                    adjusted[agent_type] = adjusted.get(agent_type, 0.0) + 0.3

        # Boost for entity name match
        if entry_type == "ENTITY":
            entity_value = value if isinstance(value, dict) else {}
            entity_name = (
                entity_value.get("name", "")
                or entity_value.get("title", "")
                or entry.get("key", "")
            ).lower()
            if entity_name and len(entity_name) > 3 and entity_name in message_lower:
                category_prefix = category.split(".")[0] if "." in category else category
                CATEGORY_AGENT_MAP = {
                    "crm": "core_orders",
                    "project": "core_projects",
                    "brief": "core_briefs",
                    "task": "core_tasks",
                    "order": "core_orders",
                }
                for prefix, agent in CATEGORY_AGENT_MAP.items():
                    if prefix in category_prefix:
                        adjusted[agent] = adjusted.get(agent, 0.0) + 0.5
                        break

    return adjusted


async def classify_intent(
    task: str,
    org_tier: str,
    context_entries: list[dict] = None,
) -> str:
    """
    Classify user message intent to route to the appropriate core agent.
    Uses keyword match + context-aware scoring.
    """
    task_lower = task.lower()

    # Keyword scoring — core agents
    scores: dict[str, float] = {}
    for agent_type, patterns in CORE_INTENT_PATTERNS.items():
        score = sum(1 for p in patterns if p in task_lower)
        if score > 0:
            scores[agent_type] = float(score)

    # Enterprise module keyword scoring
    for module_type, patterns in ENTERPRISE_INTENT_PATTERNS.items():
        score = sum(1 for p in patterns if p in task_lower)
        if score > 0:
            agent_name = module_type.lower()
            scores[agent_name] = float(score)

    # DAM queries → route to content_studio module
    dam_score = sum(1 for p in DAM_INTENT_PATTERNS if p in task_lower)
    if dam_score > 0:
        scores["content_studio"] = scores.get("content_studio", 0.0) + float(dam_score)

    # Event/activity queries — don't reroute, just let the current agent use
    # list_recent_events tool. But if it's purely an activity query with no
    # other match, route to core_tasks (the universal catch-all with event tools).
    event_score = sum(1 for p in EVENT_INTENT_PATTERNS if p in task_lower)
    if event_score > 0 and not scores:
        scores["core_tasks"] = float(event_score)

    # Context-aware adjustment
    if context_entries:
        scores = score_intent_from_context(task, context_entries, scores)

    if scores:
        best = max(scores, key=scores.get)
        if tier_has_access(org_tier, AGENT_TIER_REQUIREMENTS.get(best, "FREE")):
            return best
        return best  # still return — config builder handles upgrade message

    # Onboarding cues
    onboarding_cues = ["get started", "set up", "new here", "onboard", "first time", "hello", "hi"]
    if any(cue in task_lower for cue in onboarding_cues):
        return "core_onboarding"

    return "core_tasks"


# ══════════════════════════════════════════════════════════════
# Handoff Detection
# ══════════════════════════════════════════════════════════════


def extract_handoff_from_result(result, agent=None) -> Optional[dict]:
    """
    Check if the agent's response contains a delegate_to_agent tool call.
    Uses _tool_call_records (which stores both name and input) for reliable extraction.
    Returns the handoff payload dict, or None.
    """
    # Primary: check _tool_call_records on the agent (has full input data)
    if agent and hasattr(agent, "_tool_call_records"):
        for record in reversed(agent._tool_call_records):
            if is_handoff_tool_call(record.get("name", "")):
                return build_handoff_response(record.get("input", {}))

    # Fallback: check metadata tool_calls list (names only)
    tool_calls = getattr(result, "metadata", {}).get("tool_calls", [])
    for tc_name in reversed(tool_calls):
        if is_handoff_tool_call(tc_name):
            # Try to parse from output text
            try:
                output_text = getattr(result, "output", "") or ""
                for line in output_text.split("\n"):
                    line = line.strip()
                    if line.startswith("{") and "target_agent" in line:
                        data = json.loads(line)
                        return build_handoff_response(data)
            except (json.JSONDecodeError, AttributeError):
                pass
            return {
                "type": "handoff",
                "target_agent": "",
                "context_summary": "",
                "reason": "Agent requested a handoff",
            }
    return None


# ══════════════════════════════════════════════════════════════
# Shared Secret Auth Helper
# ══════════════════════════════════════════════════════════════


def _validate_agent_secret(x_agent_secret: Optional[str]):
    """Validate the X-Agent-Secret header from spokestack-core."""
    expected = os.environ.get("AGENT_RUNTIME_SECRET", "")
    if not expected:
        logger.warning("AGENT_RUNTIME_SECRET not configured — core endpoints unprotected")
        return
    if not x_agent_secret or x_agent_secret != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Agent-Secret")


# ══════════════════════════════════════════════════════════════
# Endpoints
# ══════════════════════════════════════════════════════════════


@router.post("/execute", response_model=CoreExecuteResponse)
async def execute_core_agent(
    request: CoreExecuteRequest,
    background_tasks: BackgroundTasks,
    x_agent_secret: Optional[str] = Header(default=None, alias="X-Agent-Secret"),
):
    """
    Execute a spokestack-core agent.

    Phase 3 enhancements:
    - context_entries in request body → auto-injected into system prompt
    - Context-aware intent classification (usage patterns + entity names)
    - Handoff detection: delegate_to_agent → status="handoff" response
    - [SYNTHESIS] prefix → minimal JSON-focused system prompt
    """
    _validate_agent_secret(x_agent_secret)

    org_id = request.resolved_org_id

    # ── MC Type Translation ──
    from src.services.agent_registry import resolve_agent_type as translate_mc_type
    agent_type = request.agent_type
    if agent_type:
        agent_type = translate_mc_type(agent_type)
    else:
        agent_type = await classify_intent(
            request.task, request.org_tier, request.context_entries,
        )

    execution_id = str(uuid.uuid4())

    # ── Module Guard ──
    if agent_type not in CORE_AGENT_BYPASS:
        module_type = MODULE_AGENT_TYPES.get(agent_type)
        if module_type:
            installed = await get_installed_modules(org_id)
            if module_type not in installed:
                return CoreExecuteResponse(
                    execution_id=execution_id,
                    status="module_required",
                    agent_type=agent_type,
                    output=get_upsell_message(module_type, request.org_tier),
                    upsell=True,
                )

    # ── Build tier-scoped config ──
    org_registrations = await registry_store.get_org_modules(org_id)
    module_tools = []
    for reg in org_registrations:
        if reg.agent_definition and isinstance(reg.agent_definition, dict):
            tools = reg.agent_definition.get("tools", [])
            module_tools.extend(tools)

    config = await build_agent_config(
        org_id=org_id,
        org_name=request.org_name,
        org_tier=request.org_tier,
        agent_type=agent_type,
        user_id=request.user_id,
        module_tools=module_tools if module_tools else None,
    )

    # Check if agent is tier-gated
    if not config["available"]:
        return CoreExecuteResponse(
            execution_id=execution_id,
            status="gated",
            agent_type=agent_type,
            upgrade_message=config["upgrade_message"],
        )

    # Instantiate agent
    settings = get_settings()
    client = OpenRouterClient(api_key=settings.openrouter_api_key)
    agent_cls = _load_agent_class(agent_type)
    agent = agent_cls(client=client, model=config["model"])

    # Inject CoreToolkit
    toolkit_config = config["core_toolkit_config"]
    agent.core_toolkit = CoreToolkit(
        org_id=toolkit_config["org_id"],
        user_id=toolkit_config["user_id"],
    )

    # Inject tier-scoped tools
    agent.tools.extend(config["tools"])

    # ── Phase 10B: Inject CRUD tools based on agent type ──
    from src.tools.agent_tool_assignment import get_openai_tools_for_agent
    crud_tools = get_openai_tools_for_agent(agent_type)
    if crud_tools:
        agent.tools.extend(crud_tools)

    # ── Context + Integration + Event Injection ──
    if request.task.startswith("[SYNTHESIS]"):
        agent._synthesis_prompt = (
            "You are a data analyst. When asked, return ONLY a valid JSON array. "
            "Do not include markdown fences, preamble, or explanation — just the raw JSON array."
        )
    else:
        # Prefer request-provided data; fall back to HTTP fetch if empty
        integrations = request.integrations or await _get_cached_integrations(org_id, agent.core_toolkit)
        events = request.recent_events or await _get_cached_events(org_id, agent.core_toolkit)

        original_prompt = agent.system_prompt
        injected_prompt = inject_context_into_prompt(
            original_prompt,
            request.context_entries,
            integrations=integrations,
            events=events,
        )
        agent._injected_system_prompt = injected_prompt

        if request.context_entries:
            logger.info(
                f"[context-injection] org={org_id} "
                f"entries={len(request.context_entries)} "
                f"injected={len([e for e in request.context_entries if e.get('entryType') in ('PREFERENCE', 'INSIGHT', 'ENTITY')])}"
            )

    # Build context
    context = AgentContext(
        tenant_id=org_id,
        user_id=request.user_id,
        task=request.task,
        session_id=request.session_id or str(uuid.uuid4()),
        metadata={
            "org_tier": request.org_tier,
            "agent_type": agent_type,
            "product": "spokestack-core",
            **request.metadata,
        },
    )

    if request.stream:
        async def event_stream():
            try:
                async for event in agent.stream(context):
                    yield f"data: {event}\n\n"
                # Check for handoff in the agent's tool call records
                if hasattr(agent, '_tool_call_records'):
                    for record in reversed(agent._tool_call_records):
                        if is_handoff_tool_call(record.get("name", "")):
                            handoff_data = build_handoff_response(record.get("input", {}))
                            yield f"data: {json.dumps(handoff_data)}\n\n"
                            break
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            finally:
                await agent.close()
                await client.http.aclose()

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "X-Chat-Id": context.chat_id,
                "X-Agent-Type": agent_type,
                "X-Execution-Id": execution_id,
            },
        )

    # Non-streaming: run and return
    try:
        result = await agent.run(context)

        # ── Phase 3: Handoff Detection ──
        handoff_data = extract_handoff_from_result(result, agent=agent)
        if handoff_data:
            target = handoff_data.get("target_agent", "")
            reason = handoff_data.get("reason", "")
            target_label = target.replace("core_", "").title() if target else "another"
            return CoreExecuteResponse(
                execution_id=execution_id,
                status="handoff",
                output=f"I'm suggesting you switch to the {target_label} agent — {reason}",
                agent_type=agent_type,
                handoff=HandoffMetadata(**handoff_data),
                token_usage={
                    "input_tokens": result.metadata.get("input_tokens", 0),
                    "output_tokens": result.metadata.get("output_tokens", 0),
                },
            )

        return CoreExecuteResponse(
            execution_id=execution_id,
            status="completed",
            output=result.output,
            agent_type=agent_type,
            token_usage={
                "input_tokens": result.metadata.get("input_tokens", 0),
                "output_tokens": result.metadata.get("output_tokens", 0),
            },
        )
    except Exception as e:
        logger.error(f"Core agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")
    finally:
        await agent.close()
        await client.http.aclose()


@router.get("/agents")
async def list_core_agents(
    org_tier: str = "FREE",
    x_agent_secret: Optional[str] = Header(default=None, alias="X-Agent-Secret"),
):
    """List available core agents for a given tier."""
    _validate_agent_secret(x_agent_secret)
    available = get_available_agents(org_tier)
    return {
        "agents": [
            {
                "type": a,
                "model": AGENT_MODEL_MAP.get(a, "deepseek/deepseek-chat"),
                "available": a in available,
                "required_tier": AGENT_TIER_REQUIREMENTS.get(a, "FREE"),
            }
            for a in CORE_AGENT_TYPES
        ],
        "org_tier": org_tier,
    }


@router.post("/agents/register")
async def register_module_agent(
    request: RegisterAgentRequest,
    x_agent_secret: Optional[str] = Header(default=None, alias="X-Agent-Secret"),
):
    """
    Legacy endpoint: Register a marketplace module agent for an organization.
    Persists to module_registrations table via registry_store.
    """
    _validate_agent_secret(x_agent_secret)

    agent_def = request.agent
    registration = await registry_store.register_module(
        org_id=request.resolved_org_id,
        module_type=agent_def.slug.upper(),
        agent_definition=agent_def.model_dump(),
    )

    from src.modules.module_checker import invalidate_cache
    invalidate_cache(request.resolved_org_id)

    logger.info(f"Registered module agent '{agent_def.slug}' for org {request.resolved_org_id}")

    return {
        "status": "registered",
        "slug": agent_def.slug,
        "org_id": request.resolved_org_id,
        "module_type": agent_def.slug.upper(),
    }


@router.delete("/agents/register/{slug}")
async def unregister_module_agent(
    slug: str,
    org_id: str,
    x_agent_secret: Optional[str] = Header(default=None, alias="X-Agent-Secret"),
):
    """Legacy endpoint: Unregister a marketplace module agent."""
    _validate_agent_secret(x_agent_secret)

    await registry_store.deregister_module(org_id, slug.upper())

    from src.modules.module_checker import invalidate_cache
    invalidate_cache(org_id)

    return {"status": "unregistered", "slug": slug, "org_id": org_id}
