from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import anthropic
import uuid
import asyncio

from ..config import get_settings
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


def get_agent(agent_type: AgentType, language: str = "en", client_id: str = None, vertical: str = None, region: str = None):
    """Factory to create agent instances."""
    settings = get_settings()
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    base_kwargs = {
        "client": client,
        "model": settings.claude_model,
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

    agent_kwargs = {
        "language": request.language,
        "client_id": request.client_id,
        "vertical": request.vertical,
        "region": request.region,
    }

    if request.stream:
        # Return streaming response
        async def generate():
            agent = get_agent(request.agent_type, **agent_kwargs)
            try:
                async for chunk in agent.stream(context):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            finally:
                await agent.close()

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
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
    """List available agent types and their capabilities."""
    return {
        "agents": [
            # Foundation
            {"type": "rfp", "name": "RFP Agent", "layer": "foundation", "description": "Analyze RFPs, extract requirements, draft proposals", "status": "available"},
            {"type": "brief", "name": "Brief Agent", "layer": "foundation", "description": "AI-assisted brief intake and requirement extraction", "status": "available"},
            {"type": "content", "name": "Content Agent", "layer": "foundation", "description": "Generate documents, proposals, reports", "status": "available"},
            {"type": "commercial", "name": "Commercial Agent", "layer": "foundation", "description": "Pricing intelligence and commercial proposals", "status": "available"},
            # Studio
            {"type": "presentation", "name": "Presentation Agent", "layer": "studio", "description": "Generate presentations and pitch decks", "status": "available"},
            {"type": "copy", "name": "Copy Agent", "layer": "studio", "description": "Generate copy (EN/AR/multi-lang)", "status": "available"},
            {"type": "image", "name": "Image Agent", "layer": "studio", "description": "Generate and manage images", "status": "available"},
            # Video
            {"type": "video_script", "name": "Video Script Agent", "layer": "video", "description": "Generate video scripts", "status": "available"},
            {"type": "video_storyboard", "name": "Video Storyboard Agent", "layer": "video", "description": "Generate storyboards", "status": "available"},
            {"type": "video_production", "name": "Video Production Agent", "layer": "video", "description": "Manage video production", "status": "available"},
            # Distribution
            {"type": "report", "name": "Report Agent", "layer": "distribution", "description": "Generate and distribute reports", "status": "available"},
            {"type": "approve", "name": "Approve Agent", "layer": "distribution", "description": "Manage approvals and feedback", "status": "available"},
            {"type": "brief_update", "name": "Brief Update Agent", "layer": "distribution", "description": "Handle brief updates and changes", "status": "available"},
            # Gateways
            {"type": "gateway_whatsapp", "name": "WhatsApp Gateway", "layer": "gateway", "description": "WhatsApp message delivery", "status": "available"},
            {"type": "gateway_email", "name": "Email Gateway", "layer": "gateway", "description": "Email delivery", "status": "available"},
            {"type": "gateway_slack", "name": "Slack Gateway", "layer": "gateway", "description": "Slack integration", "status": "available"},
            {"type": "gateway_sms", "name": "SMS Gateway", "layer": "gateway", "description": "SMS delivery", "status": "available"},
            # Brand
            {"type": "brand_voice", "name": "Brand Voice Agent", "layer": "brand", "description": "Manage brand voice and tone", "status": "available"},
            {"type": "brand_visual", "name": "Brand Visual Agent", "layer": "brand", "description": "Manage visual identity", "status": "available"},
            {"type": "brand_guidelines", "name": "Brand Guidelines Agent", "layer": "brand", "description": "Manage brand guidelines", "status": "available"},
            # Operations
            {"type": "resource", "name": "Resource Agent", "layer": "operations", "description": "Resource management", "status": "available"},
            {"type": "workflow", "name": "Workflow Agent", "layer": "operations", "description": "Workflow automation", "status": "available"},
            {"type": "ops_reporting", "name": "Ops Reporting Agent", "layer": "operations", "description": "Operations reporting", "status": "available"},
            # Client
            {"type": "crm", "name": "CRM Agent", "layer": "client", "description": "Client relationship management", "status": "available"},
            {"type": "scope", "name": "Scope Agent", "layer": "client", "description": "Scope management", "status": "available"},
            {"type": "onboarding", "name": "Onboarding Agent", "layer": "client", "description": "Client onboarding", "status": "available"},
            {"type": "instance_onboarding", "name": "Instance Onboarding Agent", "layer": "client", "description": "New ERP instance setup with infrastructure, platform credentials, and sample data", "status": "available"},
            {"type": "instance_analytics", "name": "Instance Analytics Agent", "layer": "client", "description": "Platform-level analytics, health scoring, benchmarking, forecasting", "status": "available"},
            {"type": "instance_success", "name": "Instance Success Agent", "layer": "client", "description": "Customer success management, churn prevention, expansion, QBR prep", "status": "available"},
            # Media
            {"type": "media_buying", "name": "Media Buying Agent", "layer": "media", "description": "Media buying and planning", "status": "available"},
            {"type": "campaign", "name": "Campaign Agent", "layer": "media", "description": "Campaign management", "status": "available"},
            # Social
            {"type": "social_listening", "name": "Social Listening Agent", "layer": "social", "description": "Social media monitoring", "status": "available"},
            {"type": "community", "name": "Community Agent", "layer": "social", "description": "Community management", "status": "available"},
            {"type": "social_analytics", "name": "Social Analytics Agent", "layer": "social", "description": "Social media analytics", "status": "available"},
            # Performance
            {"type": "brand_performance", "name": "Brand Performance Agent", "layer": "performance", "description": "Brand performance tracking", "status": "available"},
            {"type": "campaign_analytics", "name": "Campaign Analytics Agent", "layer": "performance", "description": "Campaign analytics", "status": "available"},
            {"type": "competitor", "name": "Competitor Agent", "layer": "performance", "description": "Competitor analysis", "status": "available"},
            # Finance
            {"type": "invoice", "name": "Invoice Agent", "layer": "finance", "description": "Invoice management", "status": "available"},
            {"type": "forecast", "name": "Forecast Agent", "layer": "finance", "description": "Financial forecasting", "status": "available"},
            {"type": "budget", "name": "Budget Agent", "layer": "finance", "description": "Budget management", "status": "available"},
            # Quality
            {"type": "qa", "name": "QA Agent", "layer": "quality", "description": "Quality assurance", "status": "available"},
            {"type": "legal", "name": "Legal Agent", "layer": "quality", "description": "Legal compliance", "status": "available"},
            # Knowledge
            {"type": "knowledge", "name": "Knowledge Agent", "layer": "knowledge", "description": "Knowledge management", "status": "available"},
            {"type": "training", "name": "Training Agent", "layer": "knowledge", "description": "Training and learning", "status": "available"},
            # Specialized
            {"type": "influencer", "name": "Influencer Agent", "layer": "specialized", "description": "Influencer marketing (vertical/region specializable)", "status": "available"},
            {"type": "pr", "name": "PR Agent", "layer": "specialized", "description": "Public relations", "status": "available"},
            {"type": "events", "name": "Events Agent", "layer": "specialized", "description": "Event planning", "status": "available"},
            {"type": "localization", "name": "Localization Agent", "layer": "specialized", "description": "Multi-market localization", "status": "available"},
            {"type": "accessibility", "name": "Accessibility Agent", "layer": "specialized", "description": "WCAG compliance", "status": "available"},
        ],
        "total_agents": 46,
        "layers": ["foundation", "studio", "video", "distribution", "gateway", "brand", "operations", "client", "media", "social", "performance", "finance", "quality", "knowledge", "specialized"],
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




@router.get("/health")
async def health_check():
    """Service health check."""
    return {"status": "healthy", "service": "ongoing-agent-builder", "agents_available": 46}
