"""
Core Router — API endpoints for spokestack-core organizations.

Handles:
- Agent execution with tier-scoped tool injection
- Intent classification to route between TASKS/PROJECTS/BRIEFS/ORDERS
- Gated agent upgrade prompts
- Module agent registration (marketplace)
"""

import json
import logging
import os
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.agents.base import AgentContext
from src.services.openrouter import OpenRouterClient
from src.services.core_config_builder import (
    build_agent_config, get_available_agents, CORE_AGENT_TYPES,
    AGENT_MODEL_MAP, tier_has_access, AGENT_TIER_REQUIREMENTS,
)
from src.tools.core_tool_definitions import CORE_INTENT_PATTERNS
from src.tools.core_toolkit import CoreToolkit
from src.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/core", tags=["spokestack-core"])

# ══════════════════════════════════════════════════════════════
# Request / Response Models
# ══════════════════════════════════════════════════════════════


class CoreExecuteRequest(BaseModel):
    """Request to execute a core agent."""
    task: str
    agent_type: Optional[str] = None  # If omitted, intent classification is used
    org_id: str
    org_name: str = ""
    org_tier: str = "FREE"  # FREE, STARTER, PRO, BUSINESS
    user_id: str
    session_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    stream: bool = False


class CoreExecuteResponse(BaseModel):
    """Response from core agent execution."""
    execution_id: str
    status: str  # "completed", "streaming", "gated"
    output: Optional[str] = None
    agent_type: Optional[str] = None
    upgrade_message: Optional[str] = None
    token_usage: Optional[dict] = None


class ModuleAgentDefinition(BaseModel):
    """Serialized module agent definition from marketplace installer."""
    name: str
    slug: str
    system_prompt: str
    tools: list[dict]
    intent_patterns: list[str] = Field(default_factory=list)
    context_read_categories: list[str] = Field(default_factory=list)
    context_write_categories: list[str] = Field(default_factory=list)


class RegisterAgentRequest(BaseModel):
    """Request to register a marketplace module agent."""
    org_id: str
    agent: ModuleAgentDefinition


# In-memory registry for marketplace module agents (per-org)
# In production this would be backed by database
_module_agent_registry: dict[str, list[ModuleAgentDefinition]] = {}


# ══════════════════════════════════════════════════════════════
# Core Agent Registry
# ══════════════════════════════════════════════════════════════

CORE_AGENT_CLASSES = {
    "core_onboarding": "src.agents.core_onboarding_agent.CoreOnboardingAgent",
    "core_tasks":      "src.agents.core_tasks_agent.CoreTasksAgent",
    "core_projects":   "src.agents.core_projects_agent.CoreProjectsAgent",
    "core_briefs":     "src.agents.core_briefs_agent.CoreBriefsAgent",
    "core_orders":     "src.agents.core_orders_agent.CoreOrdersAgent",
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
# Intent Classification
# ══════════════════════════════════════════════════════════════


async def classify_intent(task: str, org_tier: str) -> str:
    """
    Classify user message intent to route to the appropriate core agent.
    Uses a lightweight keyword match first, falls back to LLM if ambiguous.
    """
    task_lower = task.lower()

    # Score each agent type by keyword matches
    scores: dict[str, int] = {}
    for agent_type, patterns in CORE_INTENT_PATTERNS.items():
        score = sum(1 for p in patterns if p in task_lower)
        if score > 0:
            scores[agent_type] = score

    if scores:
        # Pick the highest-scoring agent
        best = max(scores, key=scores.get)
        # Check if the user has access
        if tier_has_access(org_tier, AGENT_TIER_REQUIREMENTS.get(best, "FREE")):
            return best
        # If gated, still return it — the config builder will return upgrade message

    # If no keyword match, check for onboarding cues
    onboarding_cues = ["get started", "set up", "new here", "onboard", "first time", "hello", "hi"]
    if any(cue in task_lower for cue in onboarding_cues):
        return "core_onboarding"

    # Default to tasks (the universal catch-all)
    return "core_tasks"


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

    If agent_type is omitted, intent classification routes the request.
    If the requested agent is gated (tier too low), returns an upgrade prompt.

    ## Auth
    Requires X-Agent-Secret header matching AGENT_RUNTIME_SECRET env var.

    ## Streaming
    Set stream=true for SSE response (for real-time chat).
    """
    _validate_agent_secret(x_agent_secret)

    # Intent classification if agent_type not specified
    agent_type = request.agent_type
    if not agent_type:
        agent_type = await classify_intent(request.task, request.org_tier)

    # Build tier-scoped config
    # Get marketplace module tools for this org
    org_module_agents = _module_agent_registry.get(request.org_id, [])
    module_tools = []
    for ma in org_module_agents:
        module_tools.extend(ma.tools)

    config = await build_agent_config(
        org_id=request.org_id,
        org_name=request.org_name,
        org_tier=request.org_tier,
        agent_type=agent_type,
        user_id=request.user_id,
        module_tools=module_tools if module_tools else None,
    )

    execution_id = str(uuid.uuid4())

    # Check if agent is gated
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

    # Build context
    context = AgentContext(
        tenant_id=request.org_id,
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
    Register a marketplace module agent for an organization.

    Called by spokestack-core's marketplace installer when a module is installed.
    The agent definition is stored and made available to MC Router for that org.
    """
    _validate_agent_secret(x_agent_secret)

    org_id = request.org_id
    agent_def = request.agent

    # Initialize org's module agent list if needed
    if org_id not in _module_agent_registry:
        _module_agent_registry[org_id] = []

    # Check for duplicate slug
    existing_slugs = {a.slug for a in _module_agent_registry[org_id]}
    if agent_def.slug in existing_slugs:
        # Update existing
        _module_agent_registry[org_id] = [
            a for a in _module_agent_registry[org_id] if a.slug != agent_def.slug
        ]

    _module_agent_registry[org_id].append(agent_def)

    logger.info(f"Registered module agent '{agent_def.slug}' for org {org_id}")

    return {
        "status": "registered",
        "slug": agent_def.slug,
        "org_id": org_id,
        "total_module_agents": len(_module_agent_registry[org_id]),
    }


@router.delete("/agents/register/{slug}")
async def unregister_module_agent(
    slug: str,
    org_id: str,
    x_agent_secret: Optional[str] = Header(default=None, alias="X-Agent-Secret"),
):
    """Unregister a marketplace module agent."""
    _validate_agent_secret(x_agent_secret)

    if org_id in _module_agent_registry:
        _module_agent_registry[org_id] = [
            a for a in _module_agent_registry[org_id] if a.slug != slug
        ]

    return {"status": "unregistered", "slug": slug, "org_id": org_id}
