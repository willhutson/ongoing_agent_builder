from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import anthropic
import uuid
import asyncio

from ..config import get_settings, ClaudeModelTier, CLAUDE_MODELS
from ..services.model_registry import (
    get_model_for_agent,
    get_agent_tier,
    get_model_info,
    list_agents_by_tier,
    AGENT_MODEL_RECOMMENDATIONS,
)
from ..services.external_llm_registry import (
    get_external_llms_for_agent,
    get_configured_providers,
    get_provider_status,
    get_agent_llm_summary,
    list_unconfigured_for_agent,
    AGENT_EXTERNAL_LLMS,
)
from ..services.prompt_assistant import (
    PromptAssistant,
    PromptType,
    get_prompt_templates,
    get_prompt_assistant,
)
from ..agents import (
    # Foundation
    RFPAgent, BriefAgent, ContentAgent, CommercialAgent,
    # Studio
    PresentationAgent, CopyAgent, ImageAgent,
    # Video
    VideoScriptAgent, VideoStoryboardAgent, VideoProductionAgent,
    # Distribution
    ReportAgent, ApproveAgent, BriefUpdateAgent,
    # Gateways
    WhatsAppGateway, EmailGateway, SlackGateway, SMSGateway,
    # Brand
    BrandVoiceAgent, BrandVisualAgent, BrandGuidelinesAgent,
    # Operations
    ResourceAgent, WorkflowAgent, OpsReportingAgent,
    # Client
    CRMAgent, ScopeAgent, OnboardingAgent, InstanceOnboardingAgent, InstanceAnalyticsAgent, InstanceSuccessAgent,
    # Media
    MediaBuyingAgent, CampaignAgent,
    # Social
    SocialListeningAgent, CommunityAgent, SocialAnalyticsAgent,
    # Performance
    BrandPerformanceAgent, CampaignAnalyticsAgent, CompetitorAgent,
    # Finance
    InvoiceAgent, ForecastAgent, BudgetAgent,
    # Quality
    QAAgent, LegalAgent,
    # Knowledge
    KnowledgeAgent, TrainingAgent,
    # Specialized
    InfluencerAgent, PRAgent, EventsAgent, LocalizationAgent, AccessibilityAgent,
)
from ..agents.base import AgentContext, AgentResult


router = APIRouter(prefix="/api/v1", tags=["agents"])

# In-memory task storage (replace with Redis/DB in production)
tasks: dict[str, dict] = {}


class AgentType(str, Enum):
    # Foundation
    RFP = "rfp"
    BRIEF = "brief"
    CONTENT = "content"
    COMMERCIAL = "commercial"
    # Studio
    PRESENTATION = "presentation"
    COPY = "copy"
    IMAGE = "image"
    # Video
    VIDEO_SCRIPT = "video_script"
    VIDEO_STORYBOARD = "video_storyboard"
    VIDEO_PRODUCTION = "video_production"
    # Distribution
    REPORT = "report"
    APPROVE = "approve"
    BRIEF_UPDATE = "brief_update"
    # Gateways
    GATEWAY_WHATSAPP = "gateway_whatsapp"
    GATEWAY_EMAIL = "gateway_email"
    GATEWAY_SLACK = "gateway_slack"
    GATEWAY_SMS = "gateway_sms"
    # Brand
    BRAND_VOICE = "brand_voice"
    BRAND_VISUAL = "brand_visual"
    BRAND_GUIDELINES = "brand_guidelines"
    # Operations
    RESOURCE = "resource"
    WORKFLOW = "workflow"
    OPS_REPORTING = "ops_reporting"
    # Client
    CRM = "crm"
    SCOPE = "scope"
    ONBOARDING = "onboarding"
    INSTANCE_ONBOARDING = "instance_onboarding"
    INSTANCE_ANALYTICS = "instance_analytics"
    INSTANCE_SUCCESS = "instance_success"
    # Media
    MEDIA_BUYING = "media_buying"
    CAMPAIGN = "campaign"
    # Social
    SOCIAL_LISTENING = "social_listening"
    COMMUNITY = "community"
    SOCIAL_ANALYTICS = "social_analytics"
    # Performance
    BRAND_PERFORMANCE = "brand_performance"
    CAMPAIGN_ANALYTICS = "campaign_analytics"
    COMPETITOR = "competitor"
    # Finance
    INVOICE = "invoice"
    FORECAST = "forecast"
    BUDGET = "budget"
    # Quality
    QA = "qa"
    LEGAL = "legal"
    # Knowledge
    KNOWLEDGE = "knowledge"
    TRAINING = "training"
    # Specialized
    INFLUENCER = "influencer"
    PR = "pr"
    EVENTS = "events"
    LOCALIZATION = "localization"
    ACCESSIBILITY = "accessibility"


class ExecuteRequest(BaseModel):
    """Request to execute an agent task."""
    agent_type: AgentType
    task: str = Field(..., description="The task for the agent to perform")
    tenant_id: str = Field(..., description="Tenant/organization ID")
    user_id: str = Field(..., description="User initiating the request")
    metadata: dict = Field(default_factory=dict, description="Additional context")
    stream: bool = Field(default=False, description="Stream responses")
    # Optional specialization params
    language: str = Field(default="en", description="Language for language-aware agents")
    client_id: Optional[str] = Field(default=None, description="Client ID for client-specific agents")
    vertical: Optional[str] = Field(default=None, description="Vertical specialization")
    region: Optional[str] = Field(default=None, description="Region specialization")
    # Model tier override (optional - uses agent's recommended tier if not set)
    model_tier: Optional[str] = Field(default=None, description="Override model tier: 'opus', 'sonnet', or 'haiku'")


class ExecuteResponse(BaseModel):
    """Response from agent execution."""
    task_id: str
    status: str
    result: Optional[AgentResult] = None
    message: str = ""


class TaskStatus(BaseModel):
    """Status of a running task."""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None


def get_agent(agent_type: AgentType, language: str = "en", client_id: str = None, vertical: str = None, region: str = None, model_override: ClaudeModelTier = None):
    """Factory to create agent instances with per-agent model selection."""
    settings = get_settings()
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    # Get the appropriate model for this specific agent
    agent_name = f"{agent_type.value}_agent"
    model = get_model_for_agent(agent_name, instance_override=model_override)

    base_kwargs = {
        "client": client,
        "model": model,
        "erp_base_url": settings.erp_api_base_url,
        "erp_api_key": settings.erp_api_key,
    }

    # Agent mapping with specialization support
    agent_map = {
        # Foundation
        AgentType.RFP: (RFPAgent, {}),
        AgentType.BRIEF: (BriefAgent, {}),
        AgentType.CONTENT: (ContentAgent, {}),
        AgentType.COMMERCIAL: (CommercialAgent, {}),
        # Studio
        AgentType.PRESENTATION: (PresentationAgent, {"language": language, "client_id": client_id}),
        AgentType.COPY: (CopyAgent, {"language": language, "client_id": client_id}),
        AgentType.IMAGE: (ImageAgent, {"client_id": client_id}),
        # Video
        AgentType.VIDEO_SCRIPT: (VideoScriptAgent, {"language": language, "client_id": client_id}),
        AgentType.VIDEO_STORYBOARD: (VideoStoryboardAgent, {"client_id": client_id}),
        AgentType.VIDEO_PRODUCTION: (VideoProductionAgent, {"client_id": client_id}),
        # Distribution
        AgentType.REPORT: (ReportAgent, {"language": language, "client_id": client_id}),
        AgentType.APPROVE: (ApproveAgent, {"language": language, "client_id": client_id}),
        AgentType.BRIEF_UPDATE: (BriefUpdateAgent, {"language": language, "client_id": client_id}),
        # Gateways
        AgentType.GATEWAY_WHATSAPP: (WhatsAppGateway, {}),
        AgentType.GATEWAY_EMAIL: (EmailGateway, {}),
        AgentType.GATEWAY_SLACK: (SlackGateway, {}),
        AgentType.GATEWAY_SMS: (SMSGateway, {}),
        # Brand
        AgentType.BRAND_VOICE: (BrandVoiceAgent, {"client_id": client_id}),
        AgentType.BRAND_VISUAL: (BrandVisualAgent, {"client_id": client_id}),
        AgentType.BRAND_GUIDELINES: (BrandGuidelinesAgent, {"client_id": client_id}),
        # Operations
        AgentType.RESOURCE: (ResourceAgent, {}),
        AgentType.WORKFLOW: (WorkflowAgent, {}),
        AgentType.OPS_REPORTING: (OpsReportingAgent, {}),
        # Client
        AgentType.CRM: (CRMAgent, {}),
        AgentType.SCOPE: (ScopeAgent, {}),
        AgentType.ONBOARDING: (OnboardingAgent, {}),
        AgentType.INSTANCE_ONBOARDING: (InstanceOnboardingAgent, {}),
        AgentType.INSTANCE_ANALYTICS: (InstanceAnalyticsAgent, {}),
        AgentType.INSTANCE_SUCCESS: (InstanceSuccessAgent, {}),
        # Media
        AgentType.MEDIA_BUYING: (MediaBuyingAgent, {"client_id": client_id}),
        AgentType.CAMPAIGN: (CampaignAgent, {"client_id": client_id}),
        # Social
        AgentType.SOCIAL_LISTENING: (SocialListeningAgent, {"client_id": client_id}),
        AgentType.COMMUNITY: (CommunityAgent, {"client_id": client_id}),
        AgentType.SOCIAL_ANALYTICS: (SocialAnalyticsAgent, {"client_id": client_id}),
        # Performance
        AgentType.BRAND_PERFORMANCE: (BrandPerformanceAgent, {"client_id": client_id}),
        AgentType.CAMPAIGN_ANALYTICS: (CampaignAnalyticsAgent, {"client_id": client_id}),
        AgentType.COMPETITOR: (CompetitorAgent, {"client_id": client_id}),
        # Finance
        AgentType.INVOICE: (InvoiceAgent, {"client_id": client_id}),
        AgentType.FORECAST: (ForecastAgent, {}),
        AgentType.BUDGET: (BudgetAgent, {}),
        # Quality
        AgentType.QA: (QAAgent, {}),
        AgentType.LEGAL: (LegalAgent, {}),
        # Knowledge
        AgentType.KNOWLEDGE: (KnowledgeAgent, {}),
        AgentType.TRAINING: (TrainingAgent, {}),
        # Specialized
        AgentType.INFLUENCER: (InfluencerAgent, {"vertical": vertical, "region": region, "client_id": client_id}),
        AgentType.PR: (PRAgent, {"client_id": client_id}),
        AgentType.EVENTS: (EventsAgent, {"client_id": client_id}),
        AgentType.LOCALIZATION: (LocalizationAgent, {}),
        AgentType.ACCESSIBILITY: (AccessibilityAgent, {}),
    }

    if agent_type not in agent_map:
        raise ValueError(f"Agent type {agent_type} not implemented")

    agent_class, extra_kwargs = agent_map[agent_type]
    # Filter out None values from extra_kwargs
    extra_kwargs = {k: v for k, v in extra_kwargs.items() if v is not None}
    return agent_class(**base_kwargs, **extra_kwargs)


async def run_agent_task(task_id: str, agent_type: AgentType, context: AgentContext, **kwargs):
    """Background task to run agent."""
    tasks[task_id]["status"] = "running"

    try:
        agent = get_agent(agent_type, **kwargs)
        result = await agent.run(context)
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = {
            "success": result.success,
            "output": result.output,
            "artifacts": result.artifacts,
            "metadata": result.metadata,
        }
        await agent.close()
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)


@router.post("/agent/execute", response_model=ExecuteResponse)
async def execute_agent(request: ExecuteRequest, background_tasks: BackgroundTasks):
    """
    Execute an agent task.

    For non-streaming requests, returns a task_id to poll for results.
    For streaming requests, returns an SSE stream.
    """
    task_id = str(uuid.uuid4())

    context = AgentContext(
        tenant_id=request.tenant_id,
        user_id=request.user_id,
        task=request.task,
        metadata=request.metadata,
    )

    # Parse model tier override if provided
    model_override = None
    if request.model_tier:
        try:
            model_override = ClaudeModelTier(request.model_tier)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid model tier: {request.model_tier}. Use 'opus', 'sonnet', or 'haiku'.")

    agent_kwargs = {
        "language": request.language,
        "client_id": request.client_id,
        "vertical": request.vertical,
        "region": request.region,
        "model_override": model_override,
    }

    if request.stream:
        # Return streaming response with structured SSE events
        # (Integration Spec Section 7 & 11.3)
        async def generate():
            agent = get_agent(request.agent_type, **agent_kwargs)
            try:
                async for chunk in agent.stream(context):
                    # Chunks are already formatted as SSE events from BaseAgent.stream()
                    yield chunk
                yield "data: [DONE]\n\n"
            finally:
                await agent.close()

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Chat-Id": context.chat_id,
            },
        )

    # Non-streaming: queue background task
    tasks[task_id] = {"status": "pending", "result": None, "error": None}
    background_tasks.add_task(run_agent_task, task_id, request.agent_type, context, **agent_kwargs)

    return ExecuteResponse(
        task_id=task_id,
        status="pending",
        message=f"Task queued. Poll /api/v1/agent/status/{task_id} for results.",
    )


@router.get("/agent/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get status of a running or completed task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        result=task.get("result"),
        error=task.get("error"),
    )


@router.delete("/agent/task/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a pending or running task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    # TODO: Implement actual cancellation
    tasks[task_id]["status"] = "cancelled"
    return {"message": "Task cancellation requested", "task_id": task_id}


@router.get("/agents")
async def list_agents():
    """List available agent types and their capabilities, including model tier and external LLMs."""
    def get_tier(agent_type: str) -> str:
        """Get model tier for agent type."""
        agent_name = f"{agent_type}_agent"
        return get_agent_tier(agent_name).value

    def get_external(agent_type: str) -> list[str]:
        """Get external LLM providers for agent type."""
        agent_name = f"{agent_type}_agent"
        providers = AGENT_EXTERNAL_LLMS.get(agent_name, [])
        return [p.value for p in providers]

    return {
        "agents": [
            # Foundation
            {"type": "rfp", "name": "RFP Agent", "layer": "foundation", "description": "Analyze RFPs, extract requirements, draft proposals", "status": "available", "model_tier": get_tier("rfp"), "external_llms": get_external("rfp")},
            {"type": "brief", "name": "Brief Agent", "layer": "foundation", "description": "AI-assisted brief intake and requirement extraction", "status": "available", "model_tier": get_tier("brief"), "external_llms": get_external("brief")},
            {"type": "content", "name": "Content Agent", "layer": "foundation", "description": "Generate documents, proposals, reports", "status": "available", "model_tier": get_tier("content"), "external_llms": get_external("content")},
            {"type": "commercial", "name": "Commercial Agent", "layer": "foundation", "description": "Pricing intelligence and commercial proposals", "status": "available", "model_tier": get_tier("commercial"), "external_llms": get_external("commercial")},
            # Studio
            {"type": "presentation", "name": "Presentation Agent", "layer": "studio", "description": "Generate presentations and pitch decks", "status": "available", "model_tier": get_tier("presentation"), "external_llms": get_external("presentation")},
            {"type": "copy", "name": "Copy Agent", "layer": "studio", "description": "Generate copy (EN/AR/multi-lang)", "status": "available", "model_tier": get_tier("copy"), "external_llms": get_external("copy")},
            {"type": "image", "name": "Image Agent", "layer": "studio", "description": "Generate and manage images", "status": "available", "model_tier": get_tier("image"), "external_llms": get_external("image")},
            # Video
            {"type": "video_script", "name": "Video Script Agent", "layer": "video", "description": "Generate video scripts", "status": "available", "model_tier": get_tier("video_script"), "external_llms": get_external("video_script")},
            {"type": "video_storyboard", "name": "Video Storyboard Agent", "layer": "video", "description": "Generate storyboards", "status": "available", "model_tier": get_tier("video_storyboard"), "external_llms": get_external("video_storyboard")},
            {"type": "video_production", "name": "Video Production Agent", "layer": "video", "description": "Manage video production", "status": "available", "model_tier": get_tier("video_production"), "external_llms": get_external("video_production")},
            # Distribution
            {"type": "report", "name": "Report Agent", "layer": "distribution", "description": "Generate and distribute reports", "status": "available", "model_tier": get_tier("report"), "external_llms": get_external("report")},
            {"type": "approve", "name": "Approve Agent", "layer": "distribution", "description": "Manage approvals and feedback", "status": "available", "model_tier": get_tier("approve"), "external_llms": get_external("approve")},
            {"type": "brief_update", "name": "Brief Update Agent", "layer": "distribution", "description": "Handle brief updates and changes", "status": "available", "model_tier": get_tier("brief_update"), "external_llms": get_external("brief_update")},
            # Gateways
            {"type": "gateway_whatsapp", "name": "WhatsApp Gateway", "layer": "gateway", "description": "WhatsApp message delivery", "status": "available", "model_tier": get_tier("gateway_whatsapp"), "external_llms": get_external("gateway_whatsapp")},
            {"type": "gateway_email", "name": "Email Gateway", "layer": "gateway", "description": "Email delivery", "status": "available", "model_tier": get_tier("gateway_email"), "external_llms": get_external("gateway_email")},
            {"type": "gateway_slack", "name": "Slack Gateway", "layer": "gateway", "description": "Slack integration", "status": "available", "model_tier": get_tier("gateway_slack"), "external_llms": get_external("gateway_slack")},
            {"type": "gateway_sms", "name": "SMS Gateway", "layer": "gateway", "description": "SMS delivery", "status": "available", "model_tier": get_tier("gateway_sms"), "external_llms": get_external("gateway_sms")},
            # Brand
            {"type": "brand_voice", "name": "Brand Voice Agent", "layer": "brand", "description": "Manage brand voice and tone", "status": "available", "model_tier": get_tier("brand_voice"), "external_llms": get_external("brand_voice")},
            {"type": "brand_visual", "name": "Brand Visual Agent", "layer": "brand", "description": "Manage visual identity", "status": "available", "model_tier": get_tier("brand_visual"), "external_llms": get_external("brand_visual")},
            {"type": "brand_guidelines", "name": "Brand Guidelines Agent", "layer": "brand", "description": "Manage brand guidelines", "status": "available", "model_tier": get_tier("brand_guidelines"), "external_llms": get_external("brand_guidelines")},
            # Operations
            {"type": "resource", "name": "Resource Agent", "layer": "operations", "description": "Resource management", "status": "available", "model_tier": get_tier("resource"), "external_llms": get_external("resource")},
            {"type": "workflow", "name": "Workflow Agent", "layer": "operations", "description": "Workflow automation", "status": "available", "model_tier": get_tier("workflow"), "external_llms": get_external("workflow")},
            {"type": "ops_reporting", "name": "Ops Reporting Agent", "layer": "operations", "description": "Operations reporting", "status": "available", "model_tier": get_tier("ops_reporting"), "external_llms": get_external("ops_reporting")},
            # Client
            {"type": "crm", "name": "CRM Agent", "layer": "client", "description": "Client relationship management", "status": "available", "model_tier": get_tier("crm"), "external_llms": get_external("crm")},
            {"type": "scope", "name": "Scope Agent", "layer": "client", "description": "Scope management", "status": "available", "model_tier": get_tier("scope"), "external_llms": get_external("scope")},
            {"type": "onboarding", "name": "Onboarding Agent", "layer": "client", "description": "Client onboarding", "status": "available", "model_tier": get_tier("onboarding"), "external_llms": get_external("onboarding")},
            {"type": "instance_onboarding", "name": "Instance Onboarding Agent", "layer": "client", "description": "New ERP instance setup with infrastructure, platform credentials, and sample data", "status": "available", "model_tier": get_tier("instance_onboarding"), "external_llms": get_external("instance_onboarding")},
            {"type": "instance_analytics", "name": "Instance Analytics Agent", "layer": "client", "description": "Platform-level analytics, health scoring, benchmarking, forecasting", "status": "available", "model_tier": get_tier("instance_analytics"), "external_llms": get_external("instance_analytics")},
            {"type": "instance_success", "name": "Instance Success Agent", "layer": "client", "description": "Customer success management, churn prevention, expansion, QBR prep", "status": "available", "model_tier": get_tier("instance_success"), "external_llms": get_external("instance_success")},
            # Media
            {"type": "media_buying", "name": "Media Buying Agent", "layer": "media", "description": "Media buying and planning", "status": "available", "model_tier": get_tier("media_buying"), "external_llms": get_external("media_buying")},
            {"type": "campaign", "name": "Campaign Agent", "layer": "media", "description": "Campaign management", "status": "available", "model_tier": get_tier("campaign"), "external_llms": get_external("campaign")},
            # Social
            {"type": "social_listening", "name": "Social Listening Agent", "layer": "social", "description": "Social media monitoring", "status": "available", "model_tier": get_tier("social_listening"), "external_llms": get_external("social_listening")},
            {"type": "community", "name": "Community Agent", "layer": "social", "description": "Community management", "status": "available", "model_tier": get_tier("community"), "external_llms": get_external("community")},
            {"type": "social_analytics", "name": "Social Analytics Agent", "layer": "social", "description": "Social media analytics", "status": "available", "model_tier": get_tier("social_analytics"), "external_llms": get_external("social_analytics")},
            # Performance
            {"type": "brand_performance", "name": "Brand Performance Agent", "layer": "performance", "description": "Brand performance tracking", "status": "available", "model_tier": get_tier("brand_performance"), "external_llms": get_external("brand_performance")},
            {"type": "campaign_analytics", "name": "Campaign Analytics Agent", "layer": "performance", "description": "Campaign analytics", "status": "available", "model_tier": get_tier("campaign_analytics"), "external_llms": get_external("campaign_analytics")},
            {"type": "competitor", "name": "Competitor Agent", "layer": "performance", "description": "Competitor analysis", "status": "available", "model_tier": get_tier("competitor"), "external_llms": get_external("competitor")},
            # Finance
            {"type": "invoice", "name": "Invoice Agent", "layer": "finance", "description": "Invoice management", "status": "available", "model_tier": get_tier("invoice"), "external_llms": get_external("invoice")},
            {"type": "forecast", "name": "Forecast Agent", "layer": "finance", "description": "Financial forecasting", "status": "available", "model_tier": get_tier("forecast"), "external_llms": get_external("forecast")},
            {"type": "budget", "name": "Budget Agent", "layer": "finance", "description": "Budget management", "status": "available", "model_tier": get_tier("budget"), "external_llms": get_external("budget")},
            # Quality
            {"type": "qa", "name": "QA Agent", "layer": "quality", "description": "Quality assurance", "status": "available", "model_tier": get_tier("qa"), "external_llms": get_external("qa")},
            {"type": "legal", "name": "Legal Agent", "layer": "quality", "description": "Legal compliance", "status": "available", "model_tier": get_tier("legal"), "external_llms": get_external("legal")},
            # Knowledge
            {"type": "knowledge", "name": "Knowledge Agent", "layer": "knowledge", "description": "Knowledge management", "status": "available", "model_tier": get_tier("knowledge"), "external_llms": get_external("knowledge")},
            {"type": "training", "name": "Training Agent", "layer": "knowledge", "description": "Training and learning", "status": "available", "model_tier": get_tier("training"), "external_llms": get_external("training")},
            # Specialized
            {"type": "influencer", "name": "Influencer Agent", "layer": "specialized", "description": "Influencer marketing (vertical/region specializable)", "status": "available", "model_tier": get_tier("influencer"), "external_llms": get_external("influencer")},
            {"type": "pr", "name": "PR Agent", "layer": "specialized", "description": "Public relations", "status": "available", "model_tier": get_tier("pr"), "external_llms": get_external("pr")},
            {"type": "events", "name": "Events Agent", "layer": "specialized", "description": "Event planning", "status": "available", "model_tier": get_tier("events"), "external_llms": get_external("events")},
            {"type": "localization", "name": "Localization Agent", "layer": "specialized", "description": "Multi-market localization", "status": "available", "model_tier": get_tier("localization"), "external_llms": get_external("localization")},
            {"type": "accessibility", "name": "Accessibility Agent", "layer": "specialized", "description": "WCAG compliance", "status": "available", "model_tier": get_tier("accessibility"), "external_llms": get_external("accessibility")},
        ],
        "total_agents": 46,
        "layers": ["foundation", "studio", "video", "distribution", "gateway", "brand", "operations", "client", "media", "social", "performance", "finance", "quality", "knowledge", "specialized"],
        "model_tiers": {
            tier.value: CLAUDE_MODELS[tier] for tier in ClaudeModelTier
        },
    }
# ============================================
# Chat Session Support
# ============================================

# In-memory chat sessions (replace with Redis in production)
chat_sessions: dict[str, dict] = {}


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request to send a chat message."""
    session_id: Optional[str] = None  # None to create new session
    message: str
    agent_type: AgentType = AgentType.INSTANCE_ONBOARDING
    tenant_id: str
    user_id: str
    metadata: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Response from chat."""
    session_id: str
    message: str
    preview_updates: Optional[dict] = None
    is_complete: bool = False


@router.post("/agent/chat")
async def chat_with_agent(request: ChatRequest):
    """Chat with an agent, maintaining conversation history."""
    if request.session_id and request.session_id in chat_sessions:
        session = chat_sessions[request.session_id]
    else:
        session_id = str(uuid.uuid4())
        session = {
            "id": session_id,
            "agent_type": request.agent_type,
            "tenant_id": request.tenant_id,
            "user_id": request.user_id,
            "messages": [],
            "state": {},
            "metadata": request.metadata,
        }
        chat_sessions[session_id] = session

    session["messages"].append({"role": "user", "content": request.message})

    context = AgentContext(
        tenant_id=session["tenant_id"],
        user_id=session["user_id"],
        task=f"Continue this onboarding conversation. History: {session['messages']}. Respond to: {request.message}",
        metadata={"session_id": session["id"]},
    )

    try:
        agent = get_agent(session["agent_type"])
        result = await agent.run(context)
        await agent.close()

        response_text = result.output
        session["messages"].append({"role": "assistant", "content": response_text})

        return ChatResponse(
            session_id=session["id"],
            message=response_text,
            preview_updates=None,
            is_complete=False,
        )
    except Exception as e:
        return ChatResponse(
            session_id=session["id"],
            message=f"I encountered an error: {str(e)}. Let's try again.",
            preview_updates=None,
            is_complete=False,
        )


@router.get("/agent/chat/{session_id}")
async def get_chat_session(session_id: str):
    """Get chat session state and history."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = chat_sessions[session_id]
    return {"session_id": session_id, "messages": session["messages"], "state": session["state"]}


@router.delete("/agent/chat/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session."""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return {"message": "Session deleted", "session_id": session_id}




# ============================================
# Model Management Endpoints
# ============================================

class ModelTierRequest(BaseModel):
    """Request to set global model tier."""
    tier: str = Field(..., description="Model tier: 'opus', 'sonnet', or 'haiku'")


class AgentModelOverrideRequest(BaseModel):
    """Request to override model for a specific agent."""
    agent_name: str = Field(..., description="Agent name (e.g., 'rfp_agent')")
    tier: str = Field(..., description="Model tier: 'opus', 'sonnet', or 'haiku'")


@router.get("/models/info")
async def get_models_info():
    """
    Get information about all model tiers and agent assignments.

    Returns model tiers, their descriptions, and which agents use each tier.
    """
    info = get_model_info()
    settings = get_settings()

    return {
        **info,
        "current_settings": {
            "force_model_tier": settings.force_model_tier,
            "default_model": settings.claude_model,
        }
    }


@router.get("/models/agents")
async def get_agents_by_model():
    """
    List all agents grouped by their recommended model tier.
    """
    agents_by_tier = list_agents_by_tier()
    return {
        tier.value: {
            "model_id": CLAUDE_MODELS[tier],
            "agents": agents,
            "count": len(agents),
        }
        for tier, agents in agents_by_tier.items()
    }


@router.get("/models/agent/{agent_name}")
async def get_agent_model(agent_name: str):
    """
    Get the model tier and ID for a specific agent.
    """
    # Normalize agent name
    if not agent_name.endswith("_agent"):
        agent_name = f"{agent_name}_agent"

    tier = get_agent_tier(agent_name)
    model_id = get_model_for_agent(agent_name)

    return {
        "agent_name": agent_name,
        "recommended_tier": tier.value,
        "model_id": model_id,
        "in_registry": agent_name in AGENT_MODEL_RECOMMENDATIONS,
    }


# ============================================
# External LLM Management Endpoints
# ============================================

@router.get("/external-llms/providers")
async def list_external_providers():
    """
    List all external LLM providers and their configuration status.
    Shows which providers have API keys configured.
    """
    return {
        "providers": get_provider_status(),
        "configured_count": sum(1 for v in get_configured_providers().values() if v),
        "total_count": len(get_configured_providers()),
    }


@router.get("/external-llms/agents")
async def get_agents_external_llms():
    """
    Get external LLM requirements for all agents.
    Shows which agents use which external LLMs.
    """
    return get_agent_llm_summary()


@router.get("/external-llms/agent/{agent_name}")
async def get_agent_external_llms(agent_name: str):
    """
    Get external LLM configuration for a specific agent.
    """
    if not agent_name.endswith("_agent"):
        agent_name = f"{agent_name}_agent"

    external_llms = get_external_llms_for_agent(agent_name)
    unconfigured = list_unconfigured_for_agent(agent_name)

    return {
        "agent_name": agent_name,
        "external_llms": [
            {
                "provider": llm.provider.value,
                "name": llm.name,
                "description": llm.description,
                "capabilities": llm.capabilities,
                "models": llm.models or [],
            }
            for llm in external_llms
        ],
        "unconfigured": unconfigured,
        "all_configured": len(unconfigured) == 0,
    }


@router.get("/external-llms/unconfigured")
async def list_unconfigured_providers():
    """
    List all external LLM providers that need API keys configured.
    Useful for onboarding checklist.
    """
    configured = get_configured_providers()
    providers = get_provider_status()

    unconfigured = [p for p in providers if not p["configured"]]

    return {
        "unconfigured": unconfigured,
        "count": len(unconfigured),
        "onboarding_guide": {
            "higgsfield_api_key": "Get from https://higgsfield.ai/dashboard",
            "openai_api_key": "Get from https://platform.openai.com/api-keys",
            "replicate_api_key": "Get from https://replicate.com/account/api-tokens",
            "stability_api_key": "Get from https://platform.stability.ai/account/keys",
            "elevenlabs_api_key": "Get from https://elevenlabs.io/app/settings/api-keys",
            "runway_api_key": "Get from https://app.runwayml.com/settings/api-keys",
            "beautiful_ai_api_key": "Get from Beautiful.ai settings",
            "gamma_api_key": "Get from Gamma.app settings",
            "perplexity_api_key": "Get from https://perplexity.ai/settings/api",
        },
    }


# ============================================
# Prompt Assistant Endpoints
# ============================================

class PromptAssistantRequest(BaseModel):
    """Request to enhance a prompt."""
    prompt_type: str = Field(..., description="Type: 'video', 'image', 'presentation', 'voice', 'storyboard'")
    user_input: str = Field(..., description="User's rough idea/prompt")
    context: Optional[str] = Field(default=None, description="Additional context (e.g., campaign info)")
    brand_guidelines: Optional[str] = Field(default=None, description="Brand guidelines to follow")


class PromptSuggestionsRequest(BaseModel):
    """Request for multiple prompt variations."""
    prompt_type: str = Field(..., description="Type: 'video', 'image', 'presentation', 'voice', 'storyboard'")
    user_input: str = Field(..., description="User's rough idea/prompt")
    num_variations: int = Field(default=3, ge=1, le=5, description="Number of variations (1-5)")


@router.get("/prompt-assistant/templates")
async def get_templates():
    """
    Get all available prompt templates with examples.
    Useful for showing users what types of prompts they can enhance.
    """
    return {
        "templates": get_prompt_templates(),
        "model_used": "claude-sonnet-4-20250514",
        "description": "Use Claude Sonnet to craft better prompts for visual and video generation tools",
    }


@router.post("/prompt-assistant/enhance")
async def enhance_prompt(request: PromptAssistantRequest):
    """
    Enhance a user's rough prompt into an optimized generation prompt.

    Uses Claude Sonnet (cost-effective) to transform vague ideas into
    detailed, effective prompts for DALL-E, Flux, Higgsfield, etc.
    """
    try:
        prompt_type = PromptType(request.prompt_type)
    except ValueError:
        valid_types = [t.value for t in PromptType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prompt_type: {request.prompt_type}. Valid types: {valid_types}"
        )

    try:
        assistant = get_prompt_assistant()
        result = await assistant.enhance_prompt(
            prompt_type=prompt_type,
            user_input=request.user_input,
            context=request.context,
            brand_guidelines=request.brand_guidelines,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enhance prompt: {str(e)}")


@router.post("/prompt-assistant/suggestions")
async def get_prompt_suggestions(request: PromptSuggestionsRequest):
    """
    Generate multiple prompt variations for the user to choose from.

    Useful when users want to explore different creative directions.
    """
    try:
        prompt_type = PromptType(request.prompt_type)
    except ValueError:
        valid_types = [t.value for t in PromptType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prompt_type: {request.prompt_type}. Valid types: {valid_types}"
        )

    try:
        assistant = get_prompt_assistant()
        result = await assistant.get_suggestions(
            prompt_type=prompt_type,
            user_input=request.user_input,
            num_variations=request.num_variations,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")


@router.get("/health")
async def health_check():
    """Service health check."""
    configured = get_configured_providers()
    configured_count = sum(1 for v in configured.values() if v)

    return {
        "status": "healthy",
        "service": "ongoing-agent-builder",
        "agents_available": 46,
        "external_llms_configured": configured_count,
        "external_llms_total": len(configured),
    }
