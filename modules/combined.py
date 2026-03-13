"""
Combined Mode — All modules + wizard in one FastAPI process.

One service, one port, 47 agents (46 module agents + wizard concierge).
The / endpoint serves the 3-pane Mission Control UI with chat.

Run: uvicorn combined:app --host 0.0.0.0 --port 8000
Or:  python combined.py
"""

import sys
import os
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

from shared.config import BaseModuleSettings, get_model_id
from shared.openrouter import OpenRouterClient
from shared.base_agent import BaseAgent, AgentContext

logger = logging.getLogger(__name__)


# =============================================================================
# Config
# =============================================================================

class CombinedSettings(BaseModuleSettings):
    module_name: str = "spokestack"
    module_port: int = 8000

    class Config:
        env_file = ".env"


settings = CombinedSettings()


# =============================================================================
# Import all module agent factories + wizard
# =============================================================================

from foundation.agents import create_agents as create_foundation
from studio.agents import create_agents as create_studio
from brand.agents import create_agents as create_brand
from research.agents import create_agents as create_research
from strategy.agents import create_agents as create_strategy
from operations.agents import create_agents as create_operations
from client.agents import create_agents as create_client
from distribution.agents import create_agents as create_distribution
from wizard.agent import create_wizard

MODULE_FACTORIES = {
    "foundation": create_foundation,
    "studio": create_studio,
    "brand": create_brand,
    "research": create_research,
    "strategy": create_strategy,
    "operations": create_operations,
    "client": create_client,
    "distribution": create_distribution,
}


# =============================================================================
# State
# =============================================================================

all_agents: dict[str, BaseAgent] = {}
agent_to_module: dict[str, str] = {}
module_agent_counts: dict[str, int] = {}
platform_state: dict = {}  # Shared state for wizard
llm_client: OpenRouterClient | None = None


# =============================================================================
# Lifecycle
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global all_agents, agent_to_module, module_agent_counts, platform_state, llm_client

    llm_client = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        app_name="SpokeStack",
    )

    # Load all module agents
    agents_by_module: dict[str, list[str]] = {}
    for module_name, factory in MODULE_FACTORIES.items():
        agents = factory(llm_client, settings)
        for name, agent in agents.items():
            all_agents[name] = agent
            agent_to_module[name] = module_name
        module_agent_counts[module_name] = len(agents)
        agents_by_module[module_name] = list(agents.keys())
        logger.info(f"Loaded {module_name}: {list(agents.keys())}")

    # Build platform state for wizard
    platform_state.update({
        "total_agents": len(all_agents),
        "total_modules": len(MODULE_FACTORIES),
        "openrouter_configured": bool(settings.openrouter_api_key),
        "modules": {
            name: {"agents": count, "status": "loaded"}
            for name, count in module_agent_counts.items()
        },
        "agents_by_module": agents_by_module,
        "integrations": {},
        "mcp_servers": {},
        "documents": [],
        "onboarding": {},
    })

    # Create wizard agent with platform state access
    wizard = create_wizard(llm_client, settings, platform_state)
    all_agents["wizard"] = wizard
    agent_to_module["wizard"] = "wizard"

    logger.info(f"SpokeStack ready: {len(all_agents)} agents ({len(MODULE_FACTORIES)} modules + wizard)")
    yield

    for agent in all_agents.values():
        await agent.close()
    if llm_client:
        await llm_client.close()


# =============================================================================
# App
# =============================================================================

app = FastAPI(
    title="SpokeStack Agent Platform",
    description="47 agents in one service. Wizard concierge + 8 modules. Powered by OpenRouter.",
    version="2.0.0",
    lifespan=lifespan,
)


class ExecuteRequest(BaseModel):
    agent_type: str
    task: str
    tenant_id: str = "default"
    user_id: str = "anonymous"
    stream: bool = False
    model_tier: str = "standard"
    metadata: dict = {}


@app.get("/health")
async def health():
    has_key = bool(settings.openrouter_api_key)
    return {
        "status": "healthy" if has_key else "no_api_key",
        "service": "spokestack-combined",
        "agents": len(all_agents),
        "modules": len(MODULE_FACTORIES),
        "openrouter_configured": has_key,
    }


@app.get("/agents")
async def list_agents():
    by_module: dict[str, list[str]] = {}
    for name, module in agent_to_module.items():
        by_module.setdefault(module, []).append(name)
    return {"total": len(all_agents), "by_module": by_module}


@app.get("/modules")
async def list_modules():
    return {
        "modules": {
            name: {"agents": count, "status": "loaded"}
            for name, count in module_agent_counts.items()
        },
        "total": len(MODULE_FACTORIES),
    }


@app.post("/execute")
async def execute(req: ExecuteRequest):
    agent = all_agents.get(req.agent_type)
    if not agent:
        raise HTTPException(
            404,
            f"Agent '{req.agent_type}' not found. Available: {sorted(all_agents.keys())}",
        )

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
        "module": agent_to_module.get(req.agent_type, "unknown"),
        "artifacts": result.artifacts,
        "metadata": result.metadata,
    }


@app.get("/state")
async def get_state():
    """Current platform state — used by the wizard and status panel."""
    return platform_state


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """3-pane Mission Control UI with wizard chat."""
    from wizard.ui import render_dashboard
    return render_dashboard(platform_state)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", os.environ.get("MODULE_PORT", 8000)))
    uvicorn.run(app, host="0.0.0.0", port=port)
