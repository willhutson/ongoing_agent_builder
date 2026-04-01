"""
Module Router — FastAPI endpoints for /api/v1/core/modules/*.

Called by spokestack-core when modules are installed/uninstalled.
Manages the persistent module_registrations table.
"""

import logging
import os
from datetime import timezone
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from src.modules import registry_store
from src.modules.module_checker import invalidate_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/core/modules", tags=["spokestack-core-modules"])


# ══════════════════════════════════════════════════════════════
# Request / Response Models
# ══════════════════════════════════════════════════════════════

class ModuleRegisterRequest(BaseModel):
    """Request from spokestack-core when a module is installed."""
    org_id: str
    module_type: str                             # ModuleType enum value, e.g. "CRM"
    agent_definition: Optional[dict] = None      # Optional — from module manifest


class ModuleRegisterResponse(BaseModel):
    success: bool
    org_id: str
    module_type: str
    registered_at: str


class ModuleListResponse(BaseModel):
    org_id: str
    modules: list[dict]


class ModuleDeregisterResponse(BaseModel):
    success: bool
    org_id: str
    module_type: str


# ══════════════════════════════════════════════════════════════
# Auth Helper
# ══════════════════════════════════════════════════════════════

def _validate_agent_secret(x_agent_secret: Optional[str]):
    """Validate the X-Agent-Secret header from spokestack-core."""
    expected = os.environ.get("AGENT_RUNTIME_SECRET", "")
    if not expected:
        logger.warning("AGENT_RUNTIME_SECRET not configured — module endpoints unprotected")
        return
    if not x_agent_secret or x_agent_secret != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Agent-Secret")


# ══════════════════════════════════════════════════════════════
# Endpoints
# ══════════════════════════════════════════════════════════════

@router.post("/register", response_model=ModuleRegisterResponse)
async def register_module(
    request: ModuleRegisterRequest,
    x_agent_secret: Optional[str] = Header(default=None, alias="X-Agent-Secret"),
):
    """
    Register a module for an org. Called by spokestack-core on module install.

    Idempotent:
    - Already active → return success with existing record
    - Previously uninstalled (inactive) → reactivate
    - New → create registration
    """
    _validate_agent_secret(x_agent_secret)

    if not request.org_id or not request.module_type:
        raise HTTPException(status_code=400, detail="org_id and module_type are required")

    registration = await registry_store.register_module(
        org_id=request.org_id,
        module_type=request.module_type,
        agent_definition=request.agent_definition,
    )

    # Invalidate the TTL cache for this org so next request sees the change
    invalidate_cache(request.org_id)

    return ModuleRegisterResponse(
        success=True,
        org_id=registration.org_id,
        module_type=registration.module_type,
        registered_at=registration.installed_at.isoformat() if registration.installed_at else "",
    )


@router.delete("/{org_id}/{module_type}/deregister", response_model=ModuleDeregisterResponse)
async def deregister_module(
    org_id: str,
    module_type: str,
    x_agent_secret: Optional[str] = Header(default=None, alias="X-Agent-Secret"),
):
    """
    Deregister a module for an org. Called by spokestack-core on uninstall.
    Sets active=False. Does NOT delete the row.
    """
    _validate_agent_secret(x_agent_secret)

    await registry_store.deregister_module(org_id, module_type)

    # Invalidate cache
    invalidate_cache(org_id)

    return ModuleDeregisterResponse(
        success=True,
        org_id=org_id,
        module_type=module_type,
    )


@router.get("/{org_id}", response_model=ModuleListResponse)
async def list_org_modules(
    org_id: str,
    x_agent_secret: Optional[str] = Header(default=None, alias="X-Agent-Secret"),
):
    """
    List all active module registrations for an org.
    Useful for debugging and for spokestack-core to sync state.
    """
    _validate_agent_secret(x_agent_secret)

    modules = await registry_store.get_org_modules(org_id)

    return ModuleListResponse(
        org_id=org_id,
        modules=[
            {
                "module_type": m.module_type,
                "installed_at": m.installed_at.isoformat() if m.installed_at else None,
                "active": m.active,
            }
            for m in modules
        ],
    )
