"""
Mission Control — The orchestrator.

Routes requests to the right module, discovers available agents across all modules,
provides the unified API and dashboard. This is the only service users talk to directly.

Architecture:
  User → Mission Control → Module (foundation, studio, brand, etc.)
  User ← Mission Control ← Module

Each module registers at startup or is configured via MODULE_URLS env var.
"""

import sys
import os
import json
import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(__name__)


# =============================================================================
# Config
# =============================================================================

class MissionControlSettings(BaseSettings):
    module_port: int = 8000
    log_level: str = "INFO"

    # Module URLs — comma-separated or JSON
    # Default: all modules on their standard ports (docker-compose networking)
    foundation_url: str = "http://foundation:8001"
    studio_url: str = "http://studio:8002"
    brand_url: str = "http://brand:8003"
    research_url: str = "http://research:8004"
    strategy_url: str = "http://strategy:8005"
    operations_url: str = "http://operations:8006"
    client_url: str = "http://client:8007"
    distribution_url: str = "http://distribution:8008"

    class Config:
        env_file = ".env"


settings = MissionControlSettings()

# Module registry: module_name → URL
MODULES = {
    "foundation": settings.foundation_url,
    "studio": settings.studio_url,
    "brand": settings.brand_url,
    "research": settings.research_url,
    "strategy": settings.strategy_url,
    "operations": settings.operations_url,
    "client": settings.client_url,
    "distribution": settings.distribution_url,
}

# Agent → module mapping (built at startup from module discovery)
AGENT_REGISTRY: dict[str, str] = {}  # agent_name → module_name
MODULE_HEALTH: dict[str, dict] = {}  # module_name → health response


# =============================================================================
# Lifecycle
# =============================================================================

async def discover_modules(http: httpx.AsyncClient):
    """Discover all agents from all modules."""
    AGENT_REGISTRY.clear()
    MODULE_HEALTH.clear()

    for module_name, url in MODULES.items():
        try:
            # Health check
            health_resp = await http.get(f"{url}/health", timeout=5.0)
            if health_resp.status_code == 200:
                health = health_resp.json()
                MODULE_HEALTH[module_name] = {"status": "healthy", "url": url, **health}

                # Register agents
                for agent_name in health.get("agents", []):
                    AGENT_REGISTRY[agent_name] = module_name
                    logger.info(f"  Registered agent '{agent_name}' → {module_name}")
            else:
                MODULE_HEALTH[module_name] = {"status": "unhealthy", "url": url, "code": health_resp.status_code}
                logger.warning(f"  Module {module_name} returned {health_resp.status_code}")
        except Exception as e:
            MODULE_HEALTH[module_name] = {"status": "unreachable", "url": url, "error": str(e)}
            logger.warning(f"  Module {module_name} unreachable: {e}")

    logger.info(f"Discovery complete: {len(AGENT_REGISTRY)} agents across {sum(1 for m in MODULE_HEALTH.values() if m['status'] == 'healthy')} modules")


http_client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(timeout=120.0)
    await discover_modules(http_client)
    yield
    await http_client.aclose()


# =============================================================================
# App
# =============================================================================

app = FastAPI(
    title="SpokeStack Mission Control",
    description="Orchestrator for the modular agent platform. Routes to specialized modules.",
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


# =============================================================================
# Routes
# =============================================================================

@app.get("/health")
async def health():
    healthy = sum(1 for m in MODULE_HEALTH.values() if m.get("status") == "healthy")
    return {
        "status": "healthy" if healthy > 0 else "degraded",
        "service": "mission-control",
        "modules_healthy": healthy,
        "modules_total": len(MODULES),
        "agents_registered": len(AGENT_REGISTRY),
    }


@app.get("/modules")
async def list_modules():
    """List all modules and their status."""
    return {
        "modules": MODULE_HEALTH,
        "total": len(MODULES),
        "healthy": sum(1 for m in MODULE_HEALTH.values() if m.get("status") == "healthy"),
    }


@app.get("/agents")
async def list_agents():
    """List all registered agents across all modules."""
    agents_by_module: dict[str, list[str]] = {}
    for agent, module in AGENT_REGISTRY.items():
        agents_by_module.setdefault(module, []).append(agent)

    return {
        "total_agents": len(AGENT_REGISTRY),
        "agents_by_module": agents_by_module,
        "agent_registry": AGENT_REGISTRY,
    }


@app.post("/execute")
async def execute(req: ExecuteRequest):
    """Execute an agent — routes to the correct module."""
    module_name = AGENT_REGISTRY.get(req.agent_type)
    if not module_name:
        raise HTTPException(
            404,
            f"Agent '{req.agent_type}' not found. Available agents: {sorted(AGENT_REGISTRY.keys())}",
        )

    module_url = MODULES[module_name]

    if req.stream:
        # Proxy the SSE stream
        async def stream_proxy():
            async with http_client.stream(
                "POST",
                f"{module_url}/execute",
                json=req.model_dump(),
                timeout=120.0,
            ) as response:
                async for line in response.aiter_lines():
                    yield line + "\n"

        return StreamingResponse(
            stream_proxy(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # Non-streaming: proxy the request
    response = await http_client.post(
        f"{module_url}/execute",
        json=req.model_dump(),
        timeout=120.0,
    )

    if response.status_code != 200:
        raise HTTPException(response.status_code, response.text)

    return response.json()


@app.post("/rediscover")
async def rediscover():
    """Re-discover all modules and agents."""
    await discover_modules(http_client)
    return {
        "status": "discovery_complete",
        "agents": len(AGENT_REGISTRY),
        "modules_healthy": sum(1 for m in MODULE_HEALTH.values() if m.get("status") == "healthy"),
    }


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Mission Control dashboard."""
    agents_by_module = {}
    for agent, module in AGENT_REGISTRY.items():
        agents_by_module.setdefault(module, []).append(agent)

    module_cards = ""
    for module_name, health in MODULE_HEALTH.items():
        status = health.get("status", "unknown")
        color = "#22c55e" if status == "healthy" else "#ef4444" if status == "unreachable" else "#eab308"
        agents = agents_by_module.get(module_name, [])
        agent_list = "".join(f"<li>{a}</li>" for a in sorted(agents))
        module_cards += f"""
        <div class="module-card">
            <div class="module-header">
                <span class="status-dot" style="background:{color}"></span>
                <h3>{module_name.title()}</h3>
                <span class="agent-count">{len(agents)} agents</span>
            </div>
            <ul class="agent-list">{agent_list}</ul>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>SpokeStack Mission Control</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family: -apple-system, system-ui, sans-serif; background:#0a0a0a; color:#e5e5e5; padding:2rem; }}
        h1 {{ font-size:1.5rem; margin-bottom:0.5rem; }}
        .subtitle {{ color:#a3a3a3; margin-bottom:2rem; }}
        .stats {{ display:flex; gap:1rem; margin-bottom:2rem; }}
        .stat {{ background:#171717; border:1px solid #262626; border-radius:8px; padding:1rem 1.5rem; }}
        .stat-value {{ font-size:2rem; font-weight:700; color:#22c55e; }}
        .stat-label {{ font-size:0.8rem; color:#a3a3a3; }}
        .modules {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:1rem; }}
        .module-card {{ background:#171717; border:1px solid #262626; border-radius:8px; padding:1.25rem; }}
        .module-header {{ display:flex; align-items:center; gap:0.5rem; margin-bottom:0.75rem; }}
        .module-header h3 {{ flex:1; font-size:1rem; }}
        .status-dot {{ width:8px; height:8px; border-radius:50%; }}
        .agent-count {{ font-size:0.75rem; color:#a3a3a3; background:#262626; padding:2px 8px; border-radius:10px; }}
        .agent-list {{ list-style:none; font-size:0.85rem; color:#a3a3a3; }}
        .agent-list li {{ padding:2px 0; }}
        .agent-list li:before {{ content:"→ "; color:#525252; }}
    </style>
</head>
<body>
    <h1>SpokeStack Mission Control</h1>
    <p class="subtitle">Modular Agent Platform — Orchestrator</p>
    <div class="stats">
        <div class="stat">
            <div class="stat-value">{len(AGENT_REGISTRY)}</div>
            <div class="stat-label">Total Agents</div>
        </div>
        <div class="stat">
            <div class="stat-value">{sum(1 for m in MODULE_HEALTH.values() if m.get('status')=='healthy')}/{len(MODULES)}</div>
            <div class="stat-label">Modules Online</div>
        </div>
    </div>
    <div class="modules">{module_cards}</div>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.module_port)
