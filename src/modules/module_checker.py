"""
Module Checker — Fast lookup for installed modules with TTL cache.

Called by CoreToolkit on every agent invocation. Uses a 60-second TTL cache
to avoid hitting the DB on every request.
"""

import asyncio
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Simple TTL cache: {org_id: (modules_list, expiry_timestamp)}
_cache: dict[str, tuple[list[str], float]] = {}
_CACHE_TTL_SECONDS = 60


async def get_installed_modules(org_id: str) -> list[str]:
    """
    Get the list of active module_type strings for an org.
    Uses a 60-second TTL cache to avoid DB queries on every request.

    Returns e.g. ["CRM", "SOCIAL_PUBLISHING", "ANALYTICS"]
    """
    now = time.monotonic()

    # Check cache
    cached = _cache.get(org_id)
    if cached is not None:
        modules, expiry = cached
        if now < expiry:
            return modules

    # Cache miss or expired — query the DB
    from src.modules.registry_store import get_org_modules

    try:
        registrations = await get_org_modules(org_id)
        modules = [r.module_type for r in registrations]
    except Exception as e:
        logger.error(f"Failed to fetch modules for org {org_id}: {e}")
        # On error, return cached data if available (stale is better than nothing)
        if cached is not None:
            return cached[0]
        return []

    # Update cache
    _cache[org_id] = (modules, now + _CACHE_TTL_SECONDS)
    return modules


def invalidate_cache(org_id: str) -> None:
    """Invalidate the cache for a specific org. Called after register/deregister."""
    _cache.pop(org_id, None)


def invalidate_all() -> None:
    """Clear all cached data."""
    _cache.clear()
