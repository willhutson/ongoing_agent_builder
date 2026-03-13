"""
Module App Factory — creates a standalone FastAPI app for any module.

Each module calls create_module_app() with its agents and settings.
Gets you: /health, /agents, /execute, /stream — all wired up.
"""

import json
import logging
from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .config import BaseModuleSettings, get_model_id
from .openrouter import OpenRouterClient
from .base_agent import BaseAgent, AgentContext, AgentResult

logger = logging.getLogger(__name__)


class ExecuteRequest(BaseModel):
    agent_type: str
    task: str
    tenant_id: str = "default"
    user_id: str = "anonymous"
    stream: bool = False
    model_tier: str = "standard"  # premium, standard, economy
    metadata: dict = {}


def create_module_app(
    module_name: str,
    agents_factory: callable,  # (llm, settings) -> dict[str, BaseAgent]
    settings: BaseModuleSettings,
) -> FastAPI:
    """
    Create a standalone FastAPI app for a module.

    Args:
        module_name: e.g. "foundation", "studio"
        agents_factory: function that takes (OpenRouterClient, settings) and returns {name: agent}
        settings: module settings
    """
    agents: dict[str, BaseAgent] = {}
    llm_client: OpenRouterClient | None = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal agents, llm_client
        # Startup
        llm_client = OpenRouterClient(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            app_name=f"SpokeStack/{module_name}",
        )
        agents = agents_factory(llm_client, settings)
        logger.info(f"[{module_name}] Started with {len(agents)} agents: {list(agents.keys())}")
        yield
        # Shutdown
        for agent in agents.values():
            await agent.close()
        if llm_client:
            await llm_client.close()

    app = FastAPI(
        title=f"SpokeStack {module_name.title()} Module",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "module": module_name,
            "agents": list(agents.keys()),
            "agent_count": len(agents),
        }

    @app.get("/agents")
    async def list_agents():
        return {
            "module": module_name,
            "agents": [
                {"name": name, "type": type(agent).__name__}
                for name, agent in agents.items()
            ],
        }

    @app.post("/execute")
    async def execute(req: ExecuteRequest):
        agent = agents.get(req.agent_type)
        if not agent:
            raise HTTPException(404, f"Agent '{req.agent_type}' not found in {module_name} module. Available: {list(agents.keys())}")

        ctx = AgentContext(
            tenant_id=req.tenant_id,
            user_id=req.user_id,
            task=req.task,
            metadata=req.metadata,
        )

        if req.stream:
            return StreamingResponse(
                agent.stream(ctx),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )

        result = await agent.run(ctx)
        return {
            "success": result.success,
            "output": result.output,
            "agent": result.agent,
            "artifacts": result.artifacts,
            "metadata": result.metadata,
        }

    return app
