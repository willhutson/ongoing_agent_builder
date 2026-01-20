"""
ERP Integration API - Endpoints for erp_staging_lmtd integration.

Implements the contract defined in JAN_2026_ERP_TO_AGENT_BUILDER_HANDOFF.md:
- POST /api/v1/agent/execute - Execute agents with ERP-resolved models
- GET /api/health - Provider status with latency
- Callback mechanism for result delivery
"""

from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, Request
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum
import uuid
import time
import asyncio
import httpx
import hmac
import hashlib
import logging

from ..config import get_settings
from ..services.model_registry import get_model_for_agent, get_agent_tier, AGENT_MODEL_RECOMMENDATIONS
from ..services.external_llm_registry import get_configured_providers, get_provider_status
from ..agents.base import AgentContext
from .routes import get_agent, AgentType, tasks

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
    """
    agent: str = Field(..., description="Agent type (one of 46 options)")
    task: str = Field(..., description="Task/prompt text")
    model: str = Field(..., description="Resolved model name from ERP (e.g., claude-sonnet-4-20250514)")
    tier: ERPTier = Field(..., description="Tier designation for billing/tracking")
    tenant_id: str = Field(..., description="Organization/tenant ID")
    user_id: str = Field(..., description="User initiating the request")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")
    context: Optional[dict] = Field(default_factory=dict, description="Additional context")
    callback_url: Optional[str] = Field(default=None, description="URL to POST results when complete")
    invocation_id: Optional[str] = Field(default=None, description="ERP invocation ID for callback")


class TokenUsage(BaseModel):
    """Token usage metrics."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class AgentExecuteResponse(BaseModel):
    """
    Response schema for POST /api/v1/agent/execute
    """
    execution_id: str
    status: str  # pending, running, completed, failed
    output: Optional[str] = None
    result: Optional[dict] = None
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
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

    # Performance Layer (standard)
    "brand_performance": ERPTier.STANDARD,
    "campaign_analytics": ERPTier.STANDARD,
    "competitor": ERPTier.STANDARD,

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
    ) -> bool:
        """Send execution result to ERP callback URL."""
        payload = {
            "invocation_id": invocation_id,
            "status": status,
            "output": output,
            "token_usage": {
                "input_tokens": token_usage.input_tokens,
                "output_tokens": token_usage.output_tokens,
                "total_tokens": token_usage.total_tokens,
            },
            "duration_ms": duration_ms,
            "error": error,
            "completed_at": datetime.utcnow().isoformat(),
        }

        import json
        payload_str = json.dumps(payload, sort_keys=True)
        signature = self._generate_signature(payload_str)

        try:
            response = await self.http_client.patch(
                callback_url,
                json=payload,
                headers={
                    "X-Signature": signature,
                    "Content-Type": "application/json",
                },
            )

            if response.status_code in (200, 201, 204):
                logger.info(f"Callback sent successfully to {callback_url}")
                return True
            else:
                logger.error(f"Callback failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Callback error: {str(e)}")
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
    tasks[execution_id]["status"] = "running"

    try:
        # Map string agent type to enum
        try:
            agent_type = AgentType(request.agent)
        except ValueError:
            raise ValueError(f"Unknown agent type: {request.agent}")

        # Create context
        context = AgentContext(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            task=request.task,
            metadata={
                "session_id": request.session_id,
                "erp_context": request.context,
                "invocation_id": request.invocation_id,
            },
        )

        # Get agent - note: we use the ERP-provided model directly
        # The model parameter from ERP is already resolved
        agent = get_agent(agent_type)

        # Override model if ERP provided a specific one
        if request.model:
            agent.model = request.model

        # Execute
        result = await agent.run(context)
        await agent.close()

        duration_ms = int((time.time() - start_time) * 1000)

        # Estimate token usage (simplified - real implementation would track actual usage)
        token_usage = TokenUsage(
            input_tokens=len(request.task.split()) * 2,  # Rough estimate
            output_tokens=len(result.output.split()) * 2 if result.output else 0,
        )
        token_usage.total_tokens = token_usage.input_tokens + token_usage.output_tokens

        # Update task storage
        tasks[execution_id]["status"] = "completed"
        tasks[execution_id]["result"] = {
            "success": result.success,
            "output": result.output,
            "artifacts": result.artifacts,
            "metadata": result.metadata,
        }
        tasks[execution_id]["token_usage"] = token_usage.model_dump()
        tasks[execution_id]["duration_ms"] = duration_ms

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
        tasks[execution_id]["status"] = "failed"
        tasks[execution_id]["error"] = str(e)
        tasks[execution_id]["duration_ms"] = duration_ms

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

@router.post("/agent/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    request: AgentExecuteRequest,
    background_tasks: BackgroundTasks,
    x_organization_id: Optional[str] = Header(default=None, alias="X-Organization-Id"),
    x_request_id: Optional[str] = Header(default=None, alias="X-Request-Id"),
):
    """
    Execute an agent task.

    This endpoint accepts requests from erp_staging_lmtd with pre-resolved models.
    The ERP handles tier-to-model mapping; Agent Builder uses the provided model directly.

    ## Request Headers
    - X-Organization-Id: Organization identifier (optional, can use tenant_id in body)
    - X-Request-Id: Request tracking ID (optional)

    ## Request Body
    - agent: One of 46 agent types
    - task: The prompt/task for the agent
    - model: Pre-resolved model name (e.g., claude-sonnet-4-20250514)
    - tier: ERP tier (economy/standard/premium) for billing
    - tenant_id: Organization ID
    - user_id: User ID
    - session_id: Optional session for conversation continuity
    - context: Additional context object
    - callback_url: URL to PATCH with results
    - invocation_id: ERP invocation ID for callbacks

    ## Response
    Returns execution_id immediately. Poll /agent/status/{execution_id} for results
    or provide callback_url for async notification.
    """
    # Validate agent type
    if request.agent not in AGENT_TIER_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agent type: {request.agent}. Available: {list(AGENT_TIER_MAP.keys())}"
        )

    # Use header org ID if provided, otherwise fall back to body
    org_id = x_organization_id or request.tenant_id

    # Generate execution ID
    execution_id = x_request_id or str(uuid.uuid4())
    session_id = request.session_id or str(uuid.uuid4())

    # Initialize task storage
    tasks[execution_id] = {
        "status": "pending",
        "result": None,
        "error": None,
        "token_usage": None,
        "duration_ms": None,
        "session_id": session_id,
    }

    # Queue background execution
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
        session_id=session_id,
    )


@router.get("/agent/status/{execution_id}", response_model=AgentExecuteResponse)
async def get_execution_status(execution_id: str):
    """
    Get status of an agent execution.

    Poll this endpoint to check execution progress and retrieve results.
    """
    if execution_id not in tasks:
        raise HTTPException(status_code=404, detail="Execution not found")

    task = tasks[execution_id]

    token_usage = TokenUsage()
    if task.get("token_usage"):
        token_usage = TokenUsage(**task["token_usage"])

    return AgentExecuteResponse(
        execution_id=execution_id,
        status=task["status"],
        output=task.get("result", {}).get("output") if task.get("result") else None,
        result=task.get("result"),
        token_usage=token_usage,
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

    # Check Anthropic (primary)
    anthropic_healthy = bool(settings.anthropic_api_key)
    providers.append(ProviderHealth(
        provider="anthropic",
        status="healthy" if anthropic_healthy else "unavailable",
        latency_ms=50 if anthropic_healthy else None,  # Placeholder
        last_checked=datetime.utcnow().isoformat(),
    ))

    if not anthropic_healthy:
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
