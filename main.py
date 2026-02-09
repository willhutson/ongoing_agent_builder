from contextlib import asynccontextmanager
from pathlib import Path
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
        await init_db()
        logger.info("Database initialized")
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

# CORS for ERP instances
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure per-tenant in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "service": "spokestack-agent-service",
        "version": "2.0.0",
    }


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True,
    )
