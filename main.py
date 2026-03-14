from contextlib import asynccontextmanager
from pathlib import Path
import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import logging

from src.api.routes import router
from src.api.multi_tenant import router as multi_tenant_router
from src.api.erp_integration import router as erp_router
from src.api.chat_sessions import router as chat_sessions_router
from src.api.websocket import router as websocket_router
from src.api.auth import APIKeyAuthMiddleware
from src.api.rate_limit import RateLimitMiddleware
from src.config import get_settings
from src.db.session import init_db, close_db

# Dashboard path
DASHBOARD_PATH = Path(__file__).parent / "src" / "dashboard" / "index.html"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    logger.info("Starting SpokeStack Agent Service...")
    try:
        async with asyncio.timeout(10):
            await init_db()
        logger.info("Database initialized")
    except TimeoutError:
        logger.warning("Database init timed out after 10s — starting without DB")
    except Exception as e:
        logger.warning(f"Database init skipped (may not be configured): {e}")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_db()


app = FastAPI(
    title="SpokeStack Agent Service",
    description=(
        "Multi-tenant AI agent platform — Think → Act → Create\n\n"
        "Implements Agent Builder Integration Spec v2.0:\n"
        "- Agent State Machine Protocol\n"
        "- Agent Work Protocol (screen share paradigm)\n"
        "- Artifact creation and streaming\n"
        "- WebSocket real-time events\n"
        "- SpokeStack tool definitions\n"
        "- Vision/attachment support"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — locked to SpokeStack domains
_cors_origins = [
    "https://spokestack.app",
    "https://www.spokestack.app",
    "https://spokestack.com",
    "https://www.spokestack.com",
]
# Allow extra origins via env (comma-separated) for staging/dev
_extra_origins = os.environ.get("CORS_EXTRA_ORIGINS", "")
if _extra_origins:
    _cors_origins.extend([o.strip() for o in _extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key authentication (after CORS so preflight requests work)
app.add_middleware(APIKeyAuthMiddleware)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# Include API routes
app.include_router(router)                   # Original routes (backward compatible)
app.include_router(multi_tenant_router)      # Multi-tenant routes
app.include_router(erp_router)               # ERP integration routes (erp_staging_lmtd)
app.include_router(chat_sessions_router)     # Chat session management (spec Section 8)
app.include_router(websocket_router)         # WebSocket events (spec Section 7)


@app.get("/")
async def root():
    return {
        "service": "SpokeStack Agent Service",
        "version": "2.0.0",
        "spec_version": "Integration Spec v2.0",
        "paradigm": "Think → Act → Create",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "endpoints": {
            "agents": "/api/v1/agents",
            "instances": "/api/v1/instances",
            "execute": "/api/v1/agent/execute",
            "chats": "/api/v1/chats",
            "websocket": "/v1/ws",
            "models": "/api/v1/models/info",
            "health": "/api/v1/health",
        },
        "protocols": {
            "state_machine": "idle → thinking → working → complete/error",
            "work_events": ["work_start", "action", "entity_created", "work_complete", "work_error"],
            "artifact_events": ["artifact:create", "artifact:update", "artifact:complete"],
        },
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the agent dashboard UI."""
    if DASHBOARD_PATH.exists():
        return HTMLResponse(content=DASHBOARD_PATH.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


@app.get("/health")
async def health():
    """Health check endpoint for load balancers — verifies DB and Redis connectivity."""
    import asyncio

    checks = {}
    overall = "healthy"

    # Check database (with 3s timeout so health check responds quickly)
    try:
        from src.db.session import engine as db_engine
        from sqlalchemy import text
        async with asyncio.timeout(3):
            async with db_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception:
        checks["database"] = "unavailable"
        overall = "degraded"

    # Check Redis (with 3s timeout)
    try:
        redis_url = os.environ.get("REDIS_URL", "")
        if redis_url:
            import redis.asyncio as aioredis
            async with asyncio.timeout(3):
                r = aioredis.from_url(redis_url, decode_responses=True)
                await r.ping()
                await r.aclose()
            checks["redis"] = "connected"
        else:
            checks["redis"] = "not_configured"
    except Exception:
        checks["redis"] = "unavailable"
        overall = "degraded"

    # Check Anthropic key is set
    settings = get_settings()
    checks["anthropic"] = "configured" if settings.anthropic_api_key else "missing"
    if not settings.anthropic_api_key:
        overall = "unhealthy"

    return {
        "status": overall,
        "service": "spokestack-agent-service",
        "version": "2.0.0",
        "checks": checks,
    }


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True,
    )
