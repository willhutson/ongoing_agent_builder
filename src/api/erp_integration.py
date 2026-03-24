"""
ERP Integration API - Endpoints for erp_staging_lmtd integration.

Implements the contract defined in JAN_2026_ERP_TO_AGENT_BUILDER_HANDOFF.md:
- POST /api/v1/agent/execute - Execute agents with ERP-resolved models
- POST /api/v1/agent/stream - SSE streaming for Mission Control embedded chat
- GET /api/health - Provider status with latency
- GET /api/v1/modules - Module registry for subdomain architecture
- Callback mechanism for result delivery

Subdomain architecture: Each module subdomain (e.g., studio.spokestack.app)
routes to module-scoped agents via X-Module-Subdomain header or context.moduleSubdomain.
"""

from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum
import uuid
import time
import asyncio
import json
import httpx
import hmac
import hashlib
import logging

from ..config import get_settings
from ..services.model_registry import get_model_for_agent, get_agent_tier, AGENT_MODEL_RECOMMENDATIONS
from ..services.external_llm_registry import get_configured_providers, get_provider_status
from ..services.module_registry import (
    MODULE_REGISTRY, get_module_config, get_available_agents,
    resolve_agent_for_module, is_agent_allowed_for_module,
)
from ..services.task_store import save_task, get_task, update_task
from ..agents.base import AgentContext
from .routes import get_agent, AgentType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["erp-integration"])


# =============================================================================
# REQUEST/RESPONSE SCHEMAS (per handoff spec)
# =============================================================================

class ERPTier(str, Enum):
    """ERP pricing tiers mapped to Claude models."""
    ECONOMY = "economy"    # Claude 3.5 Haiku
    STANDARD = "standard"  # Claude Sonnet 4
    PREMIUM = "premium"    # Claude Opus 4


class AgentExecuteRequest(BaseModel):
    """
    Request schema for POST /api/v1/agent/execute

    Note: ERP resolves tiers to models. Agent Builder uses the model sent directly.
    Field names match the ERP contract in JAN_2026_ERP_TO_AGENT_BUILDER_HANDOFF.md.

    Module context: The ERP middleware sets x-module-subdomain header when requests
    come from a module subdomain (e.g., studio.spokestack.app). This scopes agent
    selection to module-appropriate agents. Can also be passed in context.moduleSubdomain.
    """
    agent_type: Optional[str] = Field(default=None, description="Agent type — optional if module context provides a default")
    task: str = Field(..., description="Task/prompt text")
    llm_model: str = Field(..., alias="model", description="Resolved model name from ERP (e.g., claude-sonnet-4-20250514)")
    tier: ERPTier = Field(..., description="Tier designation for billing/tracking")
    tenant_id: str = Field(..., description="Organization/tenant ID")
    user_id: str = Field(..., description="User initiating the request")
    user_role: Optional[str] = Field(default=None, description="User permission level (e.g., ADMIN, MEMBER)")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")
    context: Optional[dict] = Field(default_factory=dict, description="Additional context (moduleSubdomain, clientId, projectId)")
    metadata: Optional[dict] = Field(default_factory=dict, description="Optional additional metadata")
    callback_url: Optional[str] = Field(default=None, description="URL to PATCH results when complete")
    invocation_id: Optional[str] = Field(default=None, description="ERP invocation ID for callback")
    stream: bool = Field(default=False, description="If true, return SSE stream instead of background task")

    model_config = {"populate_by_name": True}


class TokenUsage(BaseModel):
    """Token usage metrics."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class AgentExecuteResponse(BaseModel):
    """
    Response schema for POST /api/v1/agent/execute
    Matches ERP handoff spec fields: output, structured_output, session_id, is_complete, usage.
    """
    execution_id: str
    status: str  # pending, running, completed, failed
    output: Optional[str] = None
    message: Optional[str] = None  # Alternative to output
    structured_output: Optional[dict] = None  # Structured data from agent
    result: Optional[dict] = None
    is_complete: bool = False  # Whether task is complete
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    usage: Optional[dict] = None  # ERP-format usage: {input_tokens, output_tokens}
    session_id: Optional[str] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None


class ProviderHealth(BaseModel):
    """Health status for a single provider."""
    provider: str
    status: str  # healthy, degraded, unavailable
    latency_ms: Optional[int] = None
    last_checked: str


class HealthResponse(BaseModel):
    """
    Response schema for GET /api/health
    """
    status: str  # healthy, degraded, unhealthy
    service: str
    version: str
    timestamp: str
    agents_available: int
    providers: list[ProviderHealth]


# =============================================================================
# MODEL TIER MAPPING
# =============================================================================

# ERP tier to Claude model mapping (for reference - ERP pre-resolves)
TIER_TO_MODEL = {
    ERPTier.ECONOMY: "claude-3-5-haiku-20241022",
    ERPTier.STANDARD: "claude-sonnet-4-20250514",
    ERPTier.PREMIUM: "claude-opus-4-20250514",
}

# Agent to tier mapping (46 agents)
AGENT_TIER_MAP = {
    # Foundation Layer (standard)
    "rfp": ERPTier.STANDARD,
    "brief": ERPTier.STANDARD,
    "content": ERPTier.STANDARD,
    "commercial": ERPTier.STANDARD,

    # Studio Layer (standard)
    "presentation": ERPTier.STANDARD,
    "copy": ERPTier.STANDARD,
    "image": ERPTier.STANDARD,

    # Video Layer (standard)
    "video_script": ERPTier.STANDARD,
    "video_storyboard": ERPTier.STANDARD,
    "video_production": ERPTier.STANDARD,
    "video_editor": ERPTier.STANDARD,

    # Distribution Layer (economy - simple routing)
    "report": ERPTier.STANDARD,
    "approve": ERPTier.ECONOMY,
    "brief_update": ERPTier.ECONOMY,

    # Gateway Layer (economy - message routing)
    "gateway_whatsapp": ERPTier.ECONOMY,
    "gateway_email": ERPTier.ECONOMY,
    "gateway_slack": ERPTier.ECONOMY,
    "gateway_sms": ERPTier.ECONOMY,

    # Brand Layer (standard)
    "brand_voice": ERPTier.STANDARD,
    "brand_visual": ERPTier.STANDARD,
    "brand_guidelines": ERPTier.STANDARD,

    # Operations Layer (standard)
    "resource": ERPTier.STANDARD,
    "workflow": ERPTier.STANDARD,
    "ops_reporting": ERPTier.STANDARD,

    # Client Layer (standard/premium)
    "crm": ERPTier.STANDARD,
    "scope": ERPTier.STANDARD,
    "onboarding": ERPTier.STANDARD,
    "instance_onboarding": ERPTier.STANDARD,  # SuperAdmin wizard
    "instance_analytics": ERPTier.STANDARD,
    "instance_success": ERPTier.STANDARD,

    # Media Layer (standard)
    "media_buying": ERPTier.STANDARD,
    "campaign": ERPTier.STANDARD,

    # Social Layer (standard)
    "social_listening": ERPTier.STANDARD,
    "community": ERPTier.STANDARD,
    "social_analytics": ERPTier.STANDARD,
    "publisher": ERPTier.STANDARD,

    # Performance Layer (standard)
    "brand_performance": ERPTier.STANDARD,
    "campaign_analytics": ERPTier.STANDARD,
    "competitor": ERPTier.STANDARD,
    "observer": ERPTier.STANDARD,

    # Finance Layer (premium - accuracy critical)
    "invoice": ERPTier.STANDARD,
    "forecast": ERPTier.PREMIUM,
    "budget": ERPTier.PREMIUM,

    # Quality Layer (premium - high stakes)
    "qa": ERPTier.STANDARD,
    "legal": ERPTier.PREMIUM,

    # Knowledge Layer (premium - deep reasoning)
    "knowledge": ERPTier.PREMIUM,
    "training": ERPTier.STANDARD,

    # Specialized Layer (varies)
    "influencer": ERPTier.STANDARD,
    "pr": ERPTier.STANDARD,
    "events": ERPTier.STANDARD,
    "localization": ERPTier.STANDARD,
    "accessibility": ERPTier.STANDARD,
}


def get_recommended_tier(agent_type: str) -> ERPTier:
    """Get recommended ERP tier for an agent."""
    return AGENT_TIER_MAP.get(agent_type, ERPTier.STANDARD)


# =============================================================================
# CALLBACK SERVICE
# =============================================================================

class ERPCallbackService:
    """Service to send results back to ERP via callback."""

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or get_settings().erp_callback_secret
        self.http_client = httpx.AsyncClient(timeout=30.0)

    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for callback."""
        if not self.secret_key:
            return ""
        return hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    async def send_callback(
        self,
        callback_url: str,
        invocation_id: str,
        status: str,
        output: Optional[str],
        token_usage: TokenUsage,
        duration_ms: int,
        error: Optional[str] = None,
        max_retries: int = 3,
    ) -> bool:
        """Send execution result to ERP callback URL with exponential backoff retry."""
        payload = {
            "status": "COMPLETED" if status == "completed" else "FAILED",
            "output": {"text": output} if output else None,
            "inputTokens": token_usage.input_tokens,
            "outputTokens": token_usage.output_tokens,
            "totalTokens": token_usage.total_tokens,
            "durationMs": duration_ms,
            "error": error,
        }

        import json
        payload_str = json.dumps(payload, sort_keys=True)
        signature = self._generate_signature(payload_str)

        headers = {
            "X-Webhook-Signature": f"v1={signature}",
            "Content-Type": "application/json",
        }

        for attempt in range(max_retries + 1):
            try:
                response = await self.http_client.patch(
                    callback_url,
                    json=payload,
                    headers=headers,
                )

                if response.status_code in (200, 201, 204):
                    logger.info(f"Callback sent successfully to {callback_url}")
                    return True

                # Don't retry client errors (4xx)
                if 400 <= response.status_code < 500:
                    logger.error(f"Callback rejected (4xx): {response.status_code} - {response.text}")
                    return False

                logger.warning(f"Callback attempt {attempt + 1}/{max_retries + 1} failed: {response.status_code}")

            except Exception as e:
                logger.warning(f"Callback attempt {attempt + 1}/{max_retries + 1} error: {e}")

            # Exponential backoff: 2s, 4s, 8s
            if attempt < max_retries:
                backoff = 2 ** (attempt + 1)
                logger.info(f"Retrying callback in {backoff}s...")
                await asyncio.sleep(backoff)

        logger.error(f"Callback to {callback_url} failed after {max_retries + 1} attempts")
        return False

    async def close(self):
        await self.http_client.aclose()


# Singleton callback service
_callback_service: Optional[ERPCallbackService] = None

def get_callback_service() -> ERPCallbackService:
    global _callback_service
    if _callback_service is None:
        _callback_service = ERPCallbackService()
    return _callback_service


class UsageReportService:
    """Reports token usage to the ERP billing endpoint."""

    def __init__(self, service_key: str = None, base_url: str = None):
        settings = get_settings()
        self.service_key = service_key or settings.erp_service_key
        self.base_url = base_url or settings.erp_api_base_url
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def report_usage(
        self,
        organization_id: str,
        token_input: int,
        token_output: int,
        model: str,
        agent_type: str,
        module: Optional[str] = None,
        max_retries: int = 3,
    ) -> bool:
        """Report usage to ERP billing. Fire-and-forget with retry."""
        payload = {
            "organizationId": organization_id,
            "tokenInput": token_input,
            "tokenOutput": token_output,
            "model": model,
            "agentType": agent_type,
            "module": module,
        }

        headers = {
            "X-Service-Key": self.service_key,
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/api/v1/billing/usage/report"

        for attempt in range(max_retries + 1):
            try:
                response = await self.http_client.post(
                    url, json=payload, headers=headers,
                )
                if response.status_code in (200, 201, 204):
                    logger.info(f"Billing reported: {agent_type} ({token_input}+{token_output} tokens)")
                    return True
                if 400 <= response.status_code < 500:
                    logger.error(f"Billing rejected: {response.status_code}")
                    return False
            except Exception as e:
                logger.warning(f"Billing attempt {attempt + 1} error: {e}")

            if attempt < max_retries:
                await asyncio.sleep(2 ** (attempt + 1))

        logger.error(f"Billing report failed after {max_retries + 1} attempts")
        return False

    async def close(self):
        await self.http_client.aclose()


# Singleton usage report service
_usage_service: Optional[UsageReportService] = None

def get_usage_service() -> UsageReportService:
    global _usage_service
    if _usage_service is None:
        _usage_service = UsageReportService()
    return _usage_service


# =============================================================================
# AGENT EXECUTION
# =============================================================================

async def execute_agent_with_callback(
    execution_id: str,
    request: AgentExecuteRequest,
    callback_service: ERPCallbackService,
):
    """Background task to execute agent and send callback."""
    start_time = time.time()
    await update_task(execution_id, {"status": "running"})

    try:
        # Map string agent type to enum
        try:
            agent_type = AgentType(request.agent_type)
        except ValueError:
            raise ValueError(f"Unknown agent type: {request.agent_type}")

        # Resolve module context
        erp_context = request.context or {}
        module_subdomain = erp_context.get("moduleSubdomain")

        # Create context with module awareness
        module_config = get_module_config(module_subdomain) if module_subdomain else None
        context = AgentContext(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            task=request.task,
            module_subdomain=module_subdomain,
            module_display_name=module_config.display_name if module_config else None,
            metadata={
                "session_id": request.session_id,
                "erp_context": erp_context,
                "erp_metadata": request.metadata,
                "invocation_id": request.invocation_id,
                "user_role": request.user_role,
                "module_subdomain": module_subdomain,
            },
        )

        # Get agent - note: we use the ERP-provided model directly
        # The model parameter from ERP is already resolved
        agent = get_agent(agent_type)

        # Override model if ERP provided a specific one
        if request.llm_model:
            agent.model = request.llm_model

        # Execute
        result = await agent.run(context)
        await agent.close()

        duration_ms = int((time.time() - start_time) * 1000)

        # Extract real token usage from the agent's API response metadata
        result_meta = result.metadata or {}
        input_tokens = result_meta.get("input_tokens", 0)
        output_tokens = result_meta.get("output_tokens", 0)
        token_usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )

        # Update task storage (Redis-backed)
        await update_task(execution_id, {
            "status": "completed",
            "result": {
                "success": result.success,
                "output": result.output,
                "artifacts": result.artifacts,
                "metadata": result.metadata,
            },
            "token_usage": token_usage.model_dump(),
            "duration_ms": duration_ms,
        })

        # Send callback if URL provided
        if request.callback_url and request.invocation_id:
            await callback_service.send_callback(
                callback_url=request.callback_url,
                invocation_id=request.invocation_id,
                status="completed",
                output=result.output,
                token_usage=token_usage,
                duration_ms=duration_ms,
            )

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        await update_task(execution_id, {
            "status": "failed",
            "error": str(e),
            "duration_ms": duration_ms,
        })

        # Send error callback
        if request.callback_url and request.invocation_id:
            await callback_service.send_callback(
                callback_url=request.callback_url,
                invocation_id=request.invocation_id,
                status="failed",
                output=None,
                token_usage=TokenUsage(),
                duration_ms=duration_ms,
                error=str(e),
            )


# =============================================================================
# API ENDPOINTS
# =============================================================================

def _resolve_module_subdomain(
    request: AgentExecuteRequest,
    header_subdomain: Optional[str],
) -> Optional[str]:
    """Extract module subdomain from header or request context."""
    if header_subdomain:
        return header_subdomain
    ctx = request.context or {}
    return ctx.get("moduleSubdomain")


@router.post("/agent/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    request: AgentExecuteRequest,
    background_tasks: BackgroundTasks,
    x_organization_id: Optional[str] = Header(default=None, alias="X-Organization-Id"),
    x_request_id: Optional[str] = Header(default=None, alias="X-Request-Id"),
    x_module_subdomain: Optional[str] = Header(default=None, alias="X-Module-Subdomain"),
):
    """
    Execute an agent task (module-aware).

    This endpoint accepts requests from erp_staging_lmtd with pre-resolved models.
    The ERP handles tier-to-model mapping; Agent Builder uses the provided model directly.

    ## Module Routing
    When called from a module subdomain (e.g., studio.spokestack.app), the ERP
    middleware sets X-Module-Subdomain header. This scopes agent selection:
    - If agent_type is omitted, the module's default agent is used.
    - If agent_type is provided, it must be in the module's allowed list.
    - If no module context, agent_type is required.

    ## Streaming (Mission Control)
    Set `stream: true` to get an SSE response for the embedded Mission Control chat.
    The stream emits state:update, message:stream, work events, and artifact events.

    ## Request Headers
    - X-API-Key: Required
    - X-Organization-Id: Optional (can use tenant_id in body)
    - X-Module-Subdomain: Optional (e.g., "studio", "crm", "briefs")
    - X-Request-Id: Optional tracking ID

    ## Response
    - stream=false: Returns execution_id. Poll /agent/status/{execution_id} for results.
    - stream=true: Returns SSE event stream (text/event-stream).
    """
    # Resolve module subdomain from header or context
    module_subdomain = _resolve_module_subdomain(request, x_module_subdomain)

    # Resolve agent type using module context
    try:
        resolved_agent = resolve_agent_for_module(request.agent_type, module_subdomain)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Validate resolved agent type exists
    if resolved_agent not in AGENT_TIER_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agent type: {resolved_agent}. Available: {list(AGENT_TIER_MAP.keys())}"
        )

    # Use header org ID if provided, otherwise fall back to body
    org_id = x_organization_id or request.tenant_id

    # Generate execution ID
    execution_id = x_request_id or str(uuid.uuid4())
    session_id = request.session_id or str(uuid.uuid4())

    # Build module-aware context
    module_config = get_module_config(module_subdomain) if module_subdomain else None

    # Handle SSE streaming for Mission Control embedded chat
    if request.stream:
        context = AgentContext(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            task=request.task,
            organization_id=org_id,
            session_id=session_id,
            module_subdomain=module_subdomain,
            module_display_name=module_config.display_name if module_config else None,
            metadata={
                "session_id": session_id,
                "erp_context": request.context or {},
                "erp_metadata": request.metadata or {},
                "invocation_id": request.invocation_id,
                "user_role": request.user_role,
                "module_subdomain": module_subdomain,
            },
        )

        async def generate_sse():
            try:
                agent_type_enum = AgentType(resolved_agent)
            except ValueError:
                yield f"data: {json.dumps({'type': 'error', 'error': f'Unknown agent: {resolved_agent}'})}\n\n"
                return

            agent = get_agent(agent_type_enum)
            if request.llm_model:
                agent.model = request.llm_model

            try:
                async for chunk in agent.stream(context):
                    yield chunk
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            finally:
                await agent.close()

        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Chat-Id": session_id,
                "X-Agent-Type": resolved_agent,
                "X-Module-Subdomain": module_subdomain or "",
            },
        )

    # Non-streaming: queue background task
    # Patch the resolved agent type back onto the request for the background task
    request.agent_type = resolved_agent

    await save_task(execution_id, {
        "status": "pending",
        "result": None,
        "error": None,
        "token_usage": None,
        "duration_ms": None,
        "session_id": session_id,
        "module_subdomain": module_subdomain,
        "agent_type": resolved_agent,
    })

    callback_service = get_callback_service()
    background_tasks.add_task(
        execute_agent_with_callback,
        execution_id,
        request,
        callback_service,
    )

    return AgentExecuteResponse(
        execution_id=execution_id,
        status="pending",
        is_complete=False,
        session_id=session_id,
        message=f"Agent '{resolved_agent}' queued"
            + (f" (module: {module_subdomain})" if module_subdomain else ""),
    )


@router.get("/agent/status/{execution_id}", response_model=AgentExecuteResponse)
async def get_execution_status(execution_id: str):
    """
    Get status of an agent execution.

    Poll this endpoint to check execution progress and retrieve results.
    """
    task = await get_task(execution_id)
    if not task:
        raise HTTPException(status_code=404, detail="Execution not found")

    token_usage = TokenUsage()
    if task.get("token_usage"):
        token_usage = TokenUsage(**task["token_usage"])

    result_data = task.get("result") or {}
    is_done = task["status"] in ("completed", "failed")

    return AgentExecuteResponse(
        execution_id=execution_id,
        status=task["status"],
        output=result_data.get("output") if result_data else None,
        structured_output=result_data.get("artifacts") if result_data else None,
        result=result_data or None,
        is_complete=is_done,
        token_usage=token_usage,
        usage={"input_tokens": token_usage.input_tokens, "output_tokens": token_usage.output_tokens} if is_done else None,
        session_id=task.get("session_id"),
        duration_ms=task.get("duration_ms"),
        error=task.get("error"),
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for provider status.

    Returns system status with provider availability and latency measurements
    for Anthropic and OpenAI integrations.
    """
    settings = get_settings()
    providers_status = get_provider_status()
    configured = get_configured_providers()

    # Build provider health list
    providers = []
    overall_status = "healthy"

    # Check OpenRouter (primary LLM gateway)
    openrouter_healthy = bool(settings.openrouter_api_key)
    providers.append(ProviderHealth(
        provider="openrouter",
        status="healthy" if openrouter_healthy else "unavailable",
        latency_ms=50 if openrouter_healthy else None,  # Placeholder
        last_checked=datetime.utcnow().isoformat(),
    ))

    if not openrouter_healthy:
        overall_status = "unhealthy"

    # Check external providers
    for provider_info in providers_status:
        is_configured = provider_info.get("configured", False)
        status = "healthy" if is_configured else "unavailable"

        providers.append(ProviderHealth(
            provider=provider_info["provider"],
            status=status,
            latency_ms=100 if is_configured else None,  # Placeholder
            last_checked=datetime.utcnow().isoformat(),
        ))

        # Don't degrade overall status for optional external providers

    # Count configured vs total
    configured_count = sum(1 for v in configured.values() if v)
    if configured_count < len(configured) // 2:
        if overall_status == "healthy":
            overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        service="ongoing-agent-builder",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        agents_available=len(AGENT_TIER_MAP),
        providers=providers,
    )


@router.get("/agents/registry")
async def get_agent_registry():
    """
    Get complete agent registry with tier annotations.

    Returns all 46 agents organized by layer with their recommended tiers.
    """
    registry = {
        "total_agents": len(AGENT_TIER_MAP),
        "layers": {},
        "agents": [],
    }

    # Organize by layer
    layer_mapping = {
        "foundation": ["rfp", "brief", "content", "commercial"],
        "studio": ["presentation", "copy", "image"],
        "video": ["video_script", "video_storyboard", "video_production"],
        "distribution": ["report", "approve", "brief_update"],
        "gateway": ["gateway_whatsapp", "gateway_email", "gateway_slack", "gateway_sms"],
        "brand": ["brand_voice", "brand_visual", "brand_guidelines"],
        "operations": ["resource", "workflow", "ops_reporting"],
        "client": ["crm", "scope", "onboarding", "instance_onboarding", "instance_analytics", "instance_success"],
        "media": ["media_buying", "campaign"],
        "social": ["social_listening", "community", "social_analytics"],
        "performance": ["brand_performance", "campaign_analytics", "competitor"],
        "finance": ["invoice", "forecast", "budget"],
        "quality": ["qa", "legal"],
        "knowledge": ["knowledge", "training"],
        "specialized": ["influencer", "pr", "events", "localization", "accessibility"],
    }

    for layer, agents in layer_mapping.items():
        registry["layers"][layer] = {
            "agents": [],
            "count": len(agents),
        }

        for agent_type in agents:
            tier = AGENT_TIER_MAP.get(agent_type, ERPTier.STANDARD)
            agent_info = {
                "type": agent_type,
                "tier": tier.value,
                "layer": layer,
                "model": TIER_TO_MODEL.get(tier),
            }
            registry["layers"][layer]["agents"].append(agent_info)
            registry["agents"].append(agent_info)

    return registry


@router.get("/agents/{agent_type}")
async def get_agent_details(agent_type: str):
    """
    Get details for a specific agent.

    Includes tier, recommended inputs, and capabilities.
    """
    if agent_type not in AGENT_TIER_MAP:
        raise HTTPException(
            status_code=404,
            detail=f"Agent not found: {agent_type}"
        )

    tier = AGENT_TIER_MAP[agent_type]

    # Agent-specific details
    agent_details = {
        "type": agent_type,
        "tier": tier.value,
        "model": TIER_TO_MODEL.get(tier),
        "description": _get_agent_description(agent_type),
        "recommended_inputs": _get_recommended_inputs(agent_type),
        "example_task": _get_example_task(agent_type),
    }

    return agent_details


def _get_agent_description(agent_type: str) -> str:
    """Get description for an agent."""
    descriptions = {
        "rfp": "Analyze RFPs, extract requirements, draft proposals",
        "brief": "AI-assisted brief intake and requirement extraction",
        "content": "Generate documents, proposals, reports",
        "commercial": "Pricing intelligence and commercial proposals",
        "presentation": "Generate presentations and pitch decks",
        "copy": "Generate copy (EN/AR/multi-lang)",
        "image": "Generate and manage images",
        "video_script": "Generate video scripts",
        "video_storyboard": "Generate storyboards",
        "video_production": "Manage video production guidance",
        "report": "Generate and distribute reports",
        "approve": "Manage approvals and feedback routing",
        "brief_update": "Handle brief updates and changes",
        "gateway_whatsapp": "WhatsApp message delivery",
        "gateway_email": "Email delivery",
        "gateway_slack": "Slack integration",
        "gateway_sms": "SMS delivery",
        "brand_voice": "Manage brand voice and tone",
        "brand_visual": "Manage visual identity",
        "brand_guidelines": "Manage brand guidelines",
        "resource": "Resource allocation and management",
        "workflow": "Workflow automation",
        "ops_reporting": "Operations reporting",
        "crm": "Client relationship management",
        "scope": "Scope management",
        "onboarding": "Client onboarding",
        "instance_onboarding": "SuperAdmin wizard for new ERP instances",
        "instance_analytics": "Platform-level analytics and health scoring",
        "instance_success": "Customer success management",
        "media_buying": "Media buying and planning",
        "campaign": "Campaign management",
        "social_listening": "Social media monitoring",
        "community": "Community management",
        "social_analytics": "Social media analytics",
        "brand_performance": "Brand performance tracking",
        "campaign_analytics": "Campaign analytics",
        "competitor": "Competitor analysis",
        "invoice": "Invoice processing",
        "forecast": "Financial forecasting",
        "budget": "Budget management",
        "qa": "Quality assurance",
        "legal": "Legal review and compliance",
        "knowledge": "Knowledge base management",
        "training": "Training content generation",
        "influencer": "Influencer marketing",
        "pr": "Public relations",
        "events": "Event planning",
        "localization": "Multi-market localization",
        "accessibility": "WCAG compliance",
    }
    return descriptions.get(agent_type, "Agent for specialized tasks")


def _get_recommended_inputs(agent_type: str) -> dict:
    """Get recommended inputs for an agent."""
    inputs = {
        "instance_onboarding": {
            "wizard_step": "Current wizard step (e.g., 'business_assessment', 'module_selection')",
            "tenant_info": {
                "name": "Organization name",
                "industry": "Industry vertical",
                "team_size": "Team size category",
            },
            "responses": "User responses to previous questions",
        },
        "rfp": {
            "rfp_document": "RFP document text or URL",
            "company_capabilities": "Optional company capabilities for matching",
        },
        "brief": {
            "client_request": "Client's initial request or requirements",
            "project_type": "Type of project (campaign, retainer, etc.)",
        },
    }
    return inputs.get(agent_type, {"task": "Description of the task to perform"})


def _get_example_task(agent_type: str) -> str:
    """Get example task for an agent."""
    examples = {
        "instance_onboarding": "We are a mid-sized creative agency with 25 employees, focusing on digital campaigns and social media management for B2B tech companies in the GCC region.",
        "rfp": "Analyze this RFP for a digital transformation project and extract key requirements, timeline, and budget parameters.",
        "brief": "Create a campaign brief for a new product launch targeting millennials in the UAE market.",
        "presentation": "Create a pitch deck for our agency capabilities focusing on our video production services.",
        "copy": "Write social media copy for a luxury watch brand launching a new collection.",
    }
    return examples.get(agent_type, f"Execute {agent_type} task")


# =============================================================================
# MODULE REGISTRY ENDPOINTS (Subdomain Architecture)
# =============================================================================

@router.get("/modules")
async def list_modules():
    """
    List all ERP module subdomains and their agent assignments.

    Used by the ERP to discover which agents are available per module,
    and by Mission Control to populate the agent selector dropdown.
    """
    modules = []
    for subdomain, config in MODULE_REGISTRY.items():
        modules.append({
            "subdomain": config.subdomain,
            "display_name": config.display_name,
            "description": config.description,
            "default_agent": config.default_agent,
            "available_agents": config.available_agents,
            "agent_count": len(config.available_agents),
            "url": f"https://{config.subdomain}.spokestack.app",
        })

    return {
        "modules": modules,
        "total_modules": len(modules),
    }


@router.get("/modules/{subdomain}")
async def get_module_details(subdomain: str):
    """
    Get agent configuration for a specific module subdomain.

    Returns the default agent, available agents with their tiers,
    and the module description.
    """
    config = get_module_config(subdomain)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown module subdomain: {subdomain}. Available: {list(MODULE_REGISTRY.keys())}"
        )

    agents_with_tiers = []
    for agent_type in config.available_agents:
        tier = AGENT_TIER_MAP.get(agent_type, ERPTier.STANDARD)
        agents_with_tiers.append({
            "type": agent_type,
            "tier": tier.value,
            "model": TIER_TO_MODEL.get(tier),
            "is_default": agent_type == config.default_agent,
            "description": _get_agent_description(agent_type),
        })

    return {
        "subdomain": config.subdomain,
        "display_name": config.display_name,
        "description": config.description,
        "default_agent": config.default_agent,
        "agents": agents_with_tiers,
        "url": f"https://{config.subdomain}.spokestack.app",
    }


@router.get("/modules/{subdomain}/agents")
async def get_module_agents(subdomain: str):
    """
    Get just the agent list for a module — lightweight endpoint for Mission Control
    agent selector dropdown.
    """
    agents = get_available_agents(subdomain)
    config = get_module_config(subdomain)
    default = config.default_agent if config else agents[0] if agents else None

    return {
        "subdomain": subdomain,
        "default_agent": default,
        "agents": agents,
    }


# =============================================================================
# PLATFORM SKILLS ENDPOINTS (Layer 2)
# =============================================================================

@router.get("/skills")
async def list_skills():
    """
    List all Platform Skills (Layer 2).

    Platform skills are universal capabilities available to all agents:
    - brief_quality_scorer: Score briefs for completeness
    - smart_assigner: Recommend optimal team assignments
    - scope_creep_detector: Detect scope deviations
    - timeline_estimator: Estimate project timelines

    These encode 15+ years of agency expertise as reusable agent tools.
    """
    from ..skills.platform_skills import list_platform_skills, get_platform_skill_tools

    skills = list_platform_skills()
    return {
        "skills": skills,
        "total": len(skills),
        "layer": "Layer 2 — Platform Skills",
        "phase": "Phase 2",
    }


@router.get("/skills/{skill_name}")
async def get_skill_detail(skill_name: str):
    """
    Get details for a specific platform skill, including its tool definition.
    """
    from ..skills.platform_skills import get_platform_skill

    skill = get_platform_skill(skill_name)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Unknown skill: {skill_name}")

    return {
        "name": skill.name,
        "display_name": skill.display_name,
        "category": skill.category.value,
        "description": skill.description,
        "tool_definition": skill.tool_definition,
    }


# =============================================================================
# INSTANCE SKILLS (Layer 3) — Per-org custom skills (Phase 2+)
# =============================================================================

@router.get("/orgs/{organization_id}/skills")
async def list_org_skills(organization_id: str):
    """
    List custom skills for an organization (Layer 3).

    Phase 2+ feature: Organizations can define custom skills that encode
    org-specific processes and expertise.
    """
    from ..skills.instance_skills import get_instance_skills

    skills = await get_instance_skills(organization_id)
    return {
        "organization_id": organization_id,
        "skills": [
            {
                "id": s.id,
                "name": s.name,
                "display_name": s.display_name,
                "description": s.description,
                "status": s.status.value,
                "allowed_agents": s.allowed_agents,
                "version": s.version,
            }
            for s in skills
        ],
        "total": len(skills),
        "layer": "Layer 3 — Instance Skills",
    }


@router.post("/orgs/{organization_id}/skills")
async def create_org_skill(organization_id: str, body: dict):
    """
    Create a custom skill for an organization (Layer 3).

    Required fields: name, display_name, description, system_prompt, tool_definition
    Optional: allowed_agents (list of agent types that can use this skill)
    """
    from ..skills.instance_skills import InstanceSkill, InstanceSkillStatus, save_instance_skill

    required = ["name", "display_name", "description", "system_prompt", "tool_definition"]
    missing = [f for f in required if f not in body]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {missing}")

    skill = InstanceSkill(
        id=str(uuid.uuid4()),
        organization_id=organization_id,
        name=body["name"],
        display_name=body["display_name"],
        description=body["description"],
        system_prompt=body["system_prompt"],
        tool_definition=body["tool_definition"],
        allowed_agents=body.get("allowed_agents", []),
        created_by=body.get("created_by"),
        status=InstanceSkillStatus.DRAFT,
    )

    saved = await save_instance_skill(skill)
    return {"id": saved.id, "status": saved.status.value, "message": "Skill created (draft)"}


# =============================================================================
# INSTANCE KNOWLEDGE (Layer 4) — Per-org context documents (Phase 2+)
# =============================================================================

@router.get("/orgs/{organization_id}/knowledge")
async def list_org_knowledge(
    organization_id: str,
    category: Optional[str] = None,
    agent_type: Optional[str] = None,
    module: Optional[str] = None,
):
    """
    List knowledge documents for an organization (Layer 4).

    Phase 2+ feature: Organizations upload brand guides, process docs,
    client preferences, etc. These are injected into agent context at runtime.
    """
    from ..knowledge.instance_knowledge import (
        get_knowledge_documents, KnowledgeCategory,
    )

    cat = None
    if category:
        try:
            cat = KnowledgeCategory(category)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category: {category}. Valid: {[c.value for c in KnowledgeCategory]}"
            )

    docs = await get_knowledge_documents(
        organization_id=organization_id,
        category=cat,
        agent_type=agent_type,
        module_subdomain=module,
    )

    return {
        "organization_id": organization_id,
        "documents": [
            {
                "id": d.id,
                "title": d.title,
                "category": d.category.value,
                "tags": d.tags,
                "version": d.version,
                "created_at": d.created_at,
            }
            for d in docs
        ],
        "total": len(docs),
        "layer": "Layer 4 — Instance Knowledge",
    }


@router.post("/orgs/{organization_id}/knowledge")
async def create_org_knowledge(organization_id: str, body: dict):
    """
    Upload a knowledge document for an organization (Layer 4).

    Required fields: title, content, category
    Optional: tags, allowed_agents, allowed_modules, created_by
    """
    from ..knowledge.instance_knowledge import (
        KnowledgeDocument, KnowledgeCategory, save_knowledge_document,
    )

    required = ["title", "content", "category"]
    missing = [f for f in required if f not in body]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {missing}")

    try:
        cat = KnowledgeCategory(body["category"])
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {body['category']}. Valid: {[c.value for c in KnowledgeCategory]}"
        )

    doc = KnowledgeDocument(
        id=str(uuid.uuid4()),
        organization_id=organization_id,
        title=body["title"],
        content=body["content"],
        category=cat,
        tags=body.get("tags", []),
        allowed_agents=body.get("allowed_agents", []),
        allowed_modules=body.get("allowed_modules", []),
        created_by=body.get("created_by"),
    )

    saved = await save_knowledge_document(doc)
    return {"id": saved.id, "title": saved.title, "message": "Knowledge document saved"}
