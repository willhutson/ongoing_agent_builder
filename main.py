from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.api.routes import router
from src.config import get_settings

app = FastAPI(
    title="Ongoing Agent Builder",
    description="API agent service for TeamLMTD ERP - Think → Act → Create",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
app.include_router(router)


@app.get("/")
async def root():
    return {
        "service": "Ongoing Agent Builder",
        "version": "0.1.0",
        "paradigm": "Think → Act → Create",
        "docs": "/docs",
    }


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True,
    )
