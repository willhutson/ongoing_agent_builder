from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from src.api.routes import router
from src.api.multi_tenant import router as multi_tenant_router
from src.config import get_settings
from src.db.session import init_db, close_db

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
    description="Multi-tenant AI agent platform - Think → Act → Create",
    version="1.0.0",
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
app.include_router(router)  # Original routes (backward compatible)
app.include_router(multi_tenant_router)  # Multi-tenant routes


@app.get("/")
async def root():
    return {
        "service": "SpokeStack Agent Service",
        "version": "1.0.0",
        "paradigm": "Think → Act → Create",
        "docs": "/docs",
        "endpoints": {
            "agents": "/api/v1/agents",
            "instances": "/api/v1/instances",
            "execute": "/api/v1/instances/{instance_id}/execute",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "service": "spokestack-agent-service",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True,
    )
