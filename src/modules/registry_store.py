"""
Persistent Module Registry Store — SQLAlchemy model + CRUD helpers.

Replaces the in-memory dict from Phase 1. Uses the same SQLAlchemy engine
as multi_tenant.py (via src.db.session). Table: module_registrations.

Agent-builder's module_registrations table is a denormalized cache —
the source of truth is OrgModule in spokestack-core's Supabase/Prisma DB.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, JSON, UniqueConstraint, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Base
from src.db.session import get_session_factory

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# SQLAlchemy Model
# ══════════════════════════════════════════════════════════════

class ModuleRegistration(Base):
    """
    Tracks which marketplace modules are installed for each org.
    Denormalized cache of spokestack-core's OrgModule table.
    """
    __tablename__ = "module_registrations"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    org_id = Column(String, nullable=False, index=True)
    module_type = Column(String, nullable=False)           # matches ModuleType enum string (e.g., "CRM")
    agent_definition = Column(JSON, nullable=True)         # full agent def from manifest (optional)
    installed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    active = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("org_id", "module_type", name="uq_org_module"),
    )


# ══════════════════════════════════════════════════════════════
# CRUD Helpers
# ══════════════════════════════════════════════════════════════

async def register_module(
    org_id: str,
    module_type: str,
    agent_definition: Optional[dict] = None,
) -> ModuleRegistration:
    """
    Register a module for an org. Idempotent:
    - If already active: return existing record
    - If inactive (previously uninstalled): reactivate it
    - If new: create the record
    """
    factory = get_session_factory()
    async with factory() as session:
        # Check for existing registration
        stmt = select(ModuleRegistration).where(
            ModuleRegistration.org_id == org_id,
            ModuleRegistration.module_type == module_type,
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            if not existing.active:
                # Reactivate
                existing.active = True
                existing.updated_at = datetime.now(timezone.utc)
                if agent_definition is not None:
                    existing.agent_definition = agent_definition
                logger.info(f"Reactivated module {module_type} for org {org_id}")
            elif agent_definition is not None and existing.agent_definition != agent_definition:
                # Update agent definition if changed
                existing.agent_definition = agent_definition
                existing.updated_at = datetime.now(timezone.utc)
                logger.info(f"Updated agent definition for {module_type} on org {org_id}")
            else:
                logger.info(f"Module {module_type} already active for org {org_id}")
            await session.commit()
            return existing

        # Create new registration
        registration = ModuleRegistration(
            org_id=org_id,
            module_type=module_type,
            agent_definition=agent_definition,
            active=True,
        )
        session.add(registration)
        await session.commit()
        await session.refresh(registration)
        logger.info(f"Registered module {module_type} for org {org_id}")
        return registration


async def deregister_module(org_id: str, module_type: str) -> bool:
    """
    Soft-delete a module registration. Sets active=False, does NOT delete the row.
    Returns True if a record was deactivated, False if not found.
    """
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(ModuleRegistration).where(
            ModuleRegistration.org_id == org_id,
            ModuleRegistration.module_type == module_type,
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing and existing.active:
            existing.active = False
            existing.updated_at = datetime.now(timezone.utc)
            await session.commit()
            logger.info(f"Deregistered module {module_type} for org {org_id}")
            return True

        return False


async def get_org_modules(org_id: str) -> list[ModuleRegistration]:
    """Get all active module registrations for an org."""
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(ModuleRegistration).where(
            ModuleRegistration.org_id == org_id,
            ModuleRegistration.active == True,
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def is_module_active(org_id: str, module_type: str) -> bool:
    """Check if a specific module is active for an org."""
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(ModuleRegistration.active).where(
            ModuleRegistration.org_id == org_id,
            ModuleRegistration.module_type == module_type,
            ModuleRegistration.active == True,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None
