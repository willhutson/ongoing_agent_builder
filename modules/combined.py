"""
Combined Mode — All modules in one FastAPI process.

This is the simplest deployment: one service, one port, all 46 agents.
Perfect for Railway (single service), Replit, or any platform with one port.

Run: uvicorn combined:app --host 0.0.0.0 --port 8000
Or:  python combined.py

Split into separate services later when you need to scale individual modules.
"""

import sys
import os
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings

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
# Import all module agent factories
# =============================================================================

from foundation.agents import create_agents as create_foundation
from studio.agents import create_agents as create_studio
from brand.agents import create_agents as create_brand
from research.agents import create_agents as create_research
from strategy.agents import create_agents as create_strategy
from operations.agents import create_agents as create_operations
from client.agents import create_agents as create_client
from distribution.agents import create_agents as create_distribution

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
llm_client: OpenRouterClient | None = None


# =============================================================================
# Lifecycle
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global all_agents, agent_to_module, module_agent_counts, llm_client

    llm_client = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        app_name="SpokeStack",
    )

    for module_name, factory in MODULE_FACTORIES.items():
        agents = factory(llm_client, settings)
        for name, agent in agents.items():
            all_agents[name] = agent
            agent_to_module[name] = module_name
        module_agent_counts[module_name] = len(agents)
        logger.info(f"Loaded {module_name}: {list(agents.keys())}")

    logger.info(f"SpokeStack ready: {len(all_agents)} agents across {len(MODULE_FACTORIES)} modules")
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
    description="All 46 agents in one service. Powered by OpenRouter.",
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
    agents_by_module: dict[str, list[str]] = {}
    for name, module in agent_to_module.items():
        agents_by_module.setdefault(module, []).append(name)
    return {
        "total": len(all_agents),
        "by_module": agents_by_module,
    }


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


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    agents_by_module: dict[str, list[str]] = {}
    for name, module in agent_to_module.items():
        agents_by_module.setdefault(module, []).append(name)

    module_cards = ""
    colors = {
        "foundation": "#3b82f6", "studio": "#8b5cf6", "brand": "#ec4899",
        "research": "#06b6d4", "strategy": "#f59e0b", "operations": "#22c55e",
        "client": "#f97316", "distribution": "#6366f1",
    }
    for module_name, agents in sorted(agents_by_module.items()):
        color = colors.get(module_name, "#a3a3a3")
        agent_list = "".join(f"<li>{a}</li>" for a in sorted(agents))
        module_cards += f"""
        <div class="module-card" style="border-color:{color}40">
            <div class="module-header">
                <span class="dot" style="background:{color}"></span>
                <h3>{module_name.title()}</h3>
                <span class="count">{len(agents)}</span>
            </div>
            <ul>{agent_list}</ul>
        </div>"""

    return f"""<!DOCTYPE html>
<html><head>
<title>SpokeStack — Mission Control</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,system-ui,sans-serif;background:#09090b;color:#e4e4e7;padding:2rem}}
h1{{font-size:1.5rem;font-weight:600}}
.sub{{color:#71717a;margin-bottom:2rem;font-size:.9rem}}
.stats{{display:flex;gap:1rem;margin-bottom:2rem}}
.stat{{background:#18181b;border:1px solid #27272a;border-radius:8px;padding:1rem 1.5rem;min-width:120px}}
.stat b{{font-size:2rem;display:block;color:#22c55e}}
.stat span{{font-size:.75rem;color:#71717a}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1rem}}
.module-card{{background:#18181b;border:1px solid #27272a;border-left:3px solid;border-radius:8px;padding:1.25rem}}
.module-header{{display:flex;align-items:center;gap:.5rem;margin-bottom:.75rem}}
.module-header h3{{flex:1;font-size:.95rem}}
.dot{{width:8px;height:8px;border-radius:50%}}
.count{{font-size:.7rem;color:#71717a;background:#27272a;padding:2px 8px;border-radius:10px}}
ul{{list-style:none;font-size:.82rem;color:#a1a1aa}}
li{{padding:2px 0}}
li:before{{content:"→ ";color:#3f3f46}}
.try{{margin-top:2rem;background:#18181b;border:1px solid #27272a;border-radius:8px;padding:1.5rem}}
.try h3{{margin-bottom:.5rem;font-size:.95rem}}
code{{background:#27272a;padding:2px 6px;border-radius:4px;font-size:.8rem}}
pre{{background:#27272a;padding:1rem;border-radius:6px;margin-top:.75rem;overflow-x:auto;font-size:.8rem;color:#a1a1aa}}
</style></head>
<body>
<h1>SpokeStack Mission Control</h1>
<p class="sub">Modular Agent Platform — Combined Mode — {len(all_agents)} agents, {len(MODULE_FACTORIES)} modules</p>
<div class="stats">
<div class="stat"><b>{len(all_agents)}</b><span>Agents</span></div>
<div class="stat"><b>{len(MODULE_FACTORIES)}</b><span>Modules</span></div>
<div class="stat"><b>{'✓' if settings.openrouter_api_key else '✗'}</b><span>OpenRouter</span></div>
</div>
<div class="grid">{module_cards}</div>
<div class="try">
<h3>Try it</h3>
<p>POST to <code>/execute</code> with any agent:</p>
<pre>curl -X POST {'{'}url{'}'}/execute \\
  -H "Content-Type: application/json" \\
  -d '{{"agent_type":"brief","task":"Create a brief for a website redesign","tenant_id":"demo","user_id":"user1"}}'</pre>
</div>
</body></html>"""


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", os.environ.get("MODULE_PORT", 8000)))
    uvicorn.run(app, host="0.0.0.0", port=port)
