"""
Multi-Tenant API Routes for SpokeStack Platform

Provides endpoints for:
- Instance management
- Client management
- Agent configuration per instance
- Custom skills (Layer 3)
- Version control
- Tuning (all three tiers)
- Feedback loop
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db.session import get_db
from ..db.models import (
    Instance,
    Client,
    InstanceAgentConfig,
    InstanceSkill,
    AgentVersion,
    InstanceVersionConfig,
    InstanceTuningConfig,
    ClientTuningConfig,
    AgentOutputFeedback,
    FeedbackType,
    UpdatePolicy,
)
from ..services import AgentFactory, SkillExecutor, PromptAssembler, FeedbackAnalyzer
from ..agents.base import AgentContext


router = APIRouter(prefix="/api/v1", tags=["multi-tenant"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class InstanceCreate(BaseModel):
    name: str
    slug: str
    organization_name: Optional[str] = None
    contact_email: Optional[str] = None
    tier: str = "standard"


class InstanceResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    organization_name: Optional[str]
    contact_email: Optional[str]
    tier: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    name: str
    slug: str
    industry: Optional[str] = None
    vertical: Optional[str] = None
    region: Optional[str] = None


class ClientResponse(BaseModel):
    id: UUID
    instance_id: UUID
    name: str
    slug: str
    industry: Optional[str]
    vertical: Optional[str]
    region: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AgentConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    prompt_extension: Optional[str] = None
    default_vertical: Optional[str] = None
    default_region: Optional[str] = None
    default_language: Optional[str] = None
    disabled_tools: Optional[list[str]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class SkillCreate(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: str
    input_schema: dict
    execution_type: str = "webhook"
    webhook_url: Optional[str] = None
    webhook_method: str = "POST"
    webhook_headers: dict = {}
    webhook_auth: dict = {}
    agent_types: list[str] = []
    timeout_seconds: int = 30
    retry_count: int = 0


class SkillResponse(BaseModel):
    id: UUID
    instance_id: UUID
    name: str
    display_name: Optional[str]
    description: str
    execution_type: str
    agent_types: list[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InstanceTuningUpdate(BaseModel):
    agency_brand_voice: Optional[str] = None
    vertical_knowledge: Optional[str] = None
    regional_context: Optional[str] = None
    behavior_params: Optional[dict] = None
    content_policies: Optional[dict] = None
    custom_instructions: Optional[str] = None


class ClientTuningUpdate(BaseModel):
    brand_voice: Optional[str] = None
    tone_keywords: Optional[list[str]] = None
    content_rules: Optional[dict] = None
    writing_style: Optional[dict] = None
    active_preset: Optional[str] = None
    custom_presets: Optional[dict] = None


class FeedbackCreate(BaseModel):
    agent_type: str
    task_id: Optional[str] = None
    original_output: str
    feedback_type: str  # "approved", "rejected", "corrected"
    corrected_output: Optional[str] = None
    correction_reason: Optional[str] = None
    feedback_by: Optional[str] = None


class ExecuteAgentRequest(BaseModel):
    agent_type: str
    task: str
    user_id: str
    client_id: Optional[UUID] = None
    language: Optional[str] = None
    vertical: Optional[str] = None
    region: Optional[str] = None
    metadata: dict = {}
    stream: bool = False


# =============================================================================
# INSTANCE ENDPOINTS
# =============================================================================

@router.post("/instances", response_model=InstanceResponse)
async def create_instance(
    data: InstanceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new SpokeStack instance (tenant)."""
    # Check slug uniqueness
    existing = await db.execute(
        select(Instance).where(Instance.slug == data.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Slug already exists")

    instance = Instance(**data.model_dump())
    db.add(instance)
    await db.commit()
    await db.refresh(instance)
    return instance


@router.get("/instances", response_model=list[InstanceResponse])
async def list_instances(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all instances."""
    query = select(Instance)
    if active_only:
        query = query.where(Instance.is_active == True)
    result = await db.execute(query.order_by(Instance.name))
    return result.scalars().all()


@router.get("/instances/{instance_id}", response_model=InstanceResponse)
async def get_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get instance details."""
    result = await db.execute(
        select(Instance).where(Instance.id == instance_id)
    )
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance


# =============================================================================
# CLIENT ENDPOINTS
# =============================================================================

@router.post("/instances/{instance_id}/clients", response_model=ClientResponse)
async def create_client(
    instance_id: UUID,
    data: ClientCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new client within an instance."""
    # Verify instance exists
    result = await db.execute(
        select(Instance).where(Instance.id == instance_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Instance not found")

    client = Client(instance_id=instance_id, **data.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/instances/{instance_id}/clients", response_model=list[ClientResponse])
async def list_clients(
    instance_id: UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List clients for an instance."""
    query = select(Client).where(Client.instance_id == instance_id)
    if active_only:
        query = query.where(Client.is_active == True)
    result = await db.execute(query.order_by(Client.name))
    return result.scalars().all()


# =============================================================================
# AGENT CONFIGURATION ENDPOINTS
# =============================================================================

@router.get("/instances/{instance_id}/agents")
async def list_instance_agents(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List agent configurations for an instance."""
    result = await db.execute(
        select(InstanceAgentConfig)
        .where(InstanceAgentConfig.instance_id == instance_id)
    )
    configs = result.scalars().all()

    # Get all agent types from factory
    all_agents = AgentFactory.list_agent_types()

    # Build response with configured + unconfigured agents
    agent_list = []
    configured = {c.agent_type: c for c in configs}

    for agent_type in all_agents:
        if agent_type in configured:
            config = configured[agent_type]
            agent_list.append({
                "agent_type": agent_type,
                "configured": True,
                "enabled": config.enabled,
                "default_language": config.default_language,
                "default_vertical": config.default_vertical,
                "has_prompt_extension": bool(config.prompt_extension),
            })
        else:
            agent_list.append({
                "agent_type": agent_type,
                "configured": False,
                "enabled": True,  # Default enabled
            })

    return {"instance_id": str(instance_id), "agents": agent_list}


@router.put("/instances/{instance_id}/agents/{agent_type}")
async def update_agent_config(
    instance_id: UUID,
    agent_type: str,
    data: AgentConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update agent configuration for an instance."""
    # Get or create config
    result = await db.execute(
        select(InstanceAgentConfig)
        .where(
            InstanceAgentConfig.instance_id == instance_id,
            InstanceAgentConfig.agent_type == agent_type,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        config = InstanceAgentConfig(
            instance_id=instance_id,
            agent_type=agent_type,
        )
        db.add(config)

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    await db.commit()
    return {"status": "updated", "agent_type": agent_type}


# =============================================================================
# SKILL ENDPOINTS (Layer 3)
# =============================================================================

@router.post("/instances/{instance_id}/skills", response_model=SkillResponse)
async def create_skill(
    instance_id: UUID,
    data: SkillCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a custom skill for an instance."""
    skill = InstanceSkill(instance_id=instance_id, **data.model_dump())
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.get("/instances/{instance_id}/skills", response_model=list[SkillResponse])
async def list_skills(
    instance_id: UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List custom skills for an instance."""
    query = select(InstanceSkill).where(InstanceSkill.instance_id == instance_id)
    if active_only:
        query = query.where(InstanceSkill.is_active == True)
    result = await db.execute(query.order_by(InstanceSkill.name))
    return result.scalars().all()


@router.delete("/instances/{instance_id}/skills/{skill_id}")
async def delete_skill(
    instance_id: UUID,
    skill_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete (deactivate) a skill."""
    result = await db.execute(
        select(InstanceSkill)
        .where(
            InstanceSkill.id == skill_id,
            InstanceSkill.instance_id == instance_id,
        )
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill.is_active = False
    await db.commit()
    return {"status": "deleted"}


# =============================================================================
# TUNING ENDPOINTS
# =============================================================================

@router.get("/instances/{instance_id}/tuning")
async def get_instance_tuning(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get instance-level tuning configuration."""
    result = await db.execute(
        select(InstanceTuningConfig)
        .where(InstanceTuningConfig.instance_id == instance_id)
    )
    tuning = result.scalar_one_or_none()

    if not tuning:
        return {"instance_id": str(instance_id), "configured": False}

    return {
        "instance_id": str(instance_id),
        "configured": True,
        "agency_brand_voice": tuning.agency_brand_voice,
        "vertical_knowledge": tuning.vertical_knowledge,
        "regional_context": tuning.regional_context,
        "behavior_params": tuning.behavior_params,
        "content_policies": tuning.content_policies,
        "custom_instructions": tuning.custom_instructions,
    }


@router.put("/instances/{instance_id}/tuning")
async def update_instance_tuning(
    instance_id: UUID,
    data: InstanceTuningUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update instance-level tuning configuration."""
    result = await db.execute(
        select(InstanceTuningConfig)
        .where(InstanceTuningConfig.instance_id == instance_id)
    )
    tuning = result.scalar_one_or_none()

    if not tuning:
        tuning = InstanceTuningConfig(instance_id=instance_id)
        db.add(tuning)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tuning, field, value)

    await db.commit()
    return {"status": "updated"}


@router.get("/clients/{client_id}/tuning")
async def get_client_tuning(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get client-level tuning configuration."""
    result = await db.execute(
        select(ClientTuningConfig)
        .where(ClientTuningConfig.client_id == client_id)
    )
    tuning = result.scalar_one_or_none()

    if not tuning:
        return {"client_id": str(client_id), "configured": False}

    return {
        "client_id": str(client_id),
        "configured": True,
        "brand_voice": tuning.brand_voice,
        "tone_keywords": tuning.tone_keywords,
        "content_rules": tuning.content_rules,
        "writing_style": tuning.writing_style,
        "learned_preferences": tuning.learned_preferences,
        "active_preset": tuning.active_preset,
        "custom_presets": tuning.custom_presets,
    }


@router.put("/clients/{client_id}/tuning")
async def update_client_tuning(
    client_id: UUID,
    data: ClientTuningUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update client-level tuning configuration."""
    result = await db.execute(
        select(ClientTuningConfig)
        .where(ClientTuningConfig.client_id == client_id)
    )
    tuning = result.scalar_one_or_none()

    if not tuning:
        tuning = ClientTuningConfig(client_id=client_id)
        db.add(tuning)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tuning, field, value)

    await db.commit()
    return {"status": "updated"}


# =============================================================================
# FEEDBACK ENDPOINTS
# =============================================================================

@router.post("/instances/{instance_id}/feedback")
async def submit_feedback(
    instance_id: UUID,
    data: FeedbackCreate,
    client_id: Optional[UUID] = None,
    auto_analyze: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback on agent output."""
    feedback = AgentOutputFeedback(
        instance_id=instance_id,
        client_id=client_id,
        agent_type=data.agent_type,
        task_id=data.task_id,
        original_output=data.original_output,
        feedback_type=FeedbackType(data.feedback_type),
        corrected_output=data.corrected_output,
        correction_reason=data.correction_reason,
        feedback_by=data.feedback_by,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    result = {"feedback_id": str(feedback.id), "status": "submitted"}

    # Auto-analyze if requested
    if auto_analyze:
        analyzer = FeedbackAnalyzer(db)
        analysis = await analyzer.analyze_feedback(feedback.id, auto_apply=True)
        result["analysis"] = analysis

    return result


@router.post("/instances/{instance_id}/feedback/analyze")
async def analyze_feedback_batch(
    instance_id: UUID,
    client_id: Optional[UUID] = None,
    auto_apply: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Analyze unprocessed feedback for an instance."""
    analyzer = FeedbackAnalyzer(db)
    results = await analyzer.analyze_batch(
        instance_id=instance_id,
        client_id=client_id,
        auto_apply=auto_apply,
    )
    return results


# =============================================================================
# AGENT EXECUTION (Multi-Tenant)
# =============================================================================

# In-memory task storage (replace with Redis in production)
tasks: dict[str, dict] = {}


@router.post("/instances/{instance_id}/execute")
async def execute_agent(
    instance_id: UUID,
    request: ExecuteAgentRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Execute an agent with full multi-tenant context.

    Uses AgentFactory to assemble agent with:
    - Instance configuration
    - Custom skills
    - Three-tier tuning
    """
    import uuid as uuid_module

    task_id = str(uuid_module.uuid4())

    # Create agent context
    context = AgentContext(
        tenant_id=str(instance_id),
        user_id=request.user_id,
        task=request.task,
        metadata=request.metadata,
    )

    if request.stream:
        # Streaming response
        async def generate():
            factory = AgentFactory(db)
            agent = await factory.create_agent(
                agent_type=request.agent_type,
                instance_id=instance_id,
                client_id=request.client_id,
                language=request.language,
                vertical=request.vertical,
                region=request.region,
            )
            try:
                async for chunk in agent.stream(context):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            finally:
                await agent.close()

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
        )

    # Non-streaming: queue background task
    tasks[task_id] = {"status": "pending", "result": None, "error": None}

    async def run_agent():
        tasks[task_id]["status"] = "running"
        try:
            factory = AgentFactory(db)
            agent = await factory.create_agent(
                agent_type=request.agent_type,
                instance_id=instance_id,
                client_id=request.client_id,
                language=request.language,
                vertical=request.vertical,
                region=request.region,
            )
            result = await agent.run(context)
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["result"] = {
                "success": result.success,
                "output": result.output,
                "artifacts": result.artifacts,
            }
            await agent.close()
        except Exception as e:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = str(e)

    background_tasks.add_task(run_agent)

    return {
        "task_id": task_id,
        "status": "pending",
        "message": f"Task queued. Poll /api/v1/tasks/{task_id} for results.",
    }


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of an agent execution task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "result": task.get("result"),
        "error": task.get("error"),
    }
