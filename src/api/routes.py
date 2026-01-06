from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import anthropic
import uuid
import asyncio

from ..config import get_settings
from ..agents import RFPAgent
from ..agents.base import AgentContext, AgentResult


router = APIRouter(prefix="/api/v1", tags=["agents"])

# In-memory task storage (replace with Redis/DB in production)
tasks: dict[str, dict] = {}


class AgentType(str, Enum):
    RFP = "rfp"
    BRIEF = "brief"
    CONTENT = "content"
    RESOURCE = "resource"


class ExecuteRequest(BaseModel):
    """Request to execute an agent task."""
    agent_type: AgentType
    task: str = Field(..., description="The task for the agent to perform")
    tenant_id: str = Field(..., description="Tenant/organization ID")
    user_id: str = Field(..., description="User initiating the request")
    metadata: dict = Field(default_factory=dict, description="Additional context")
    stream: bool = Field(default=False, description="Stream responses")


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


def get_agent(agent_type: AgentType):
    """Factory to create agent instances."""
    settings = get_settings()
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    if agent_type == AgentType.RFP:
        return RFPAgent(
            client=client,
            model=settings.claude_model,
            erp_base_url=settings.erp_api_base_url,
            erp_api_key=settings.erp_api_key,
        )
    # TODO: Add other agent types
    else:
        raise ValueError(f"Agent type {agent_type} not implemented")


async def run_agent_task(task_id: str, agent_type: AgentType, context: AgentContext):
    """Background task to run agent."""
    tasks[task_id]["status"] = "running"

    try:
        agent = get_agent(agent_type)
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

    if request.stream:
        # Return streaming response
        async def generate():
            agent = get_agent(request.agent_type)
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
    background_tasks.add_task(run_agent_task, task_id, request.agent_type, context)

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
            {
                "type": "rfp",
                "name": "RFP Agent",
                "description": "Analyze RFPs, extract requirements, draft proposals",
                "status": "available",
            },
            {
                "type": "brief",
                "name": "Brief Agent",
                "description": "AI-assisted brief intake and requirement extraction",
                "status": "coming_soon",
            },
            {
                "type": "content",
                "name": "Content Agent",
                "description": "Generate documents, proposals, reports",
                "status": "coming_soon",
            },
            {
                "type": "resource",
                "name": "Resource Agent",
                "description": "Smart resource allocation and workload balancing",
                "status": "coming_soon",
            },
        ]
    }


@router.get("/health")
async def health_check():
    """Service health check."""
    return {"status": "healthy", "service": "ongoing-agent-builder"}
