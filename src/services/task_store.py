"""
Redis-backed task and session storage.

Replaces in-memory dicts with Redis for persistence across restarts
and support for horizontal scaling.

Falls back to in-memory storage if Redis is unavailable.
"""

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_redis_client = None
_fallback_store: dict[str, dict] = {}
_use_redis = False

TASK_TTL = 86400  # 24 hours
SESSION_TTL = 3600  # 1 hour


async def _get_redis():
    """Lazy-init Redis connection."""
    global _redis_client, _use_redis
    if _redis_client is not None:
        return _redis_client

    redis_url = os.environ.get("REDIS_URL", "")
    if not redis_url:
        logger.info("REDIS_URL not set, using in-memory fallback")
        _use_redis = False
        return None

    try:
        import redis.asyncio as aioredis
        _redis_client = aioredis.from_url(redis_url, decode_responses=True)
        await _redis_client.ping()
        _use_redis = True
        logger.info("Connected to Redis for task/session storage")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis unavailable ({e}), using in-memory fallback")
        _use_redis = False
        _redis_client = None
        return None


# ── Generic key-value operations ─────────────────────────────────

async def store_set(key: str, value: dict, ttl: int = TASK_TTL) -> None:
    """Store a dict under the given key."""
    r = await _get_redis()
    if r:
        await r.setex(key, ttl, json.dumps(value))
    else:
        _fallback_store[key] = value


async def store_get(key: str) -> Optional[dict]:
    """Retrieve a dict by key."""
    r = await _get_redis()
    if r:
        raw = await r.get(key)
        return json.loads(raw) if raw else None
    return _fallback_store.get(key)


async def store_delete(key: str) -> None:
    """Delete a key."""
    r = await _get_redis()
    if r:
        await r.delete(key)
    else:
        _fallback_store.pop(key, None)


async def store_exists(key: str) -> bool:
    """Check if a key exists."""
    r = await _get_redis()
    if r:
        return bool(await r.exists(key))
    return key in _fallback_store


# ── Task-specific helpers ────────────────────────────────────────

def _task_key(task_id: str) -> str:
    return f"task:{task_id}"


async def save_task(task_id: str, data: dict) -> None:
    await store_set(_task_key(task_id), data, ttl=TASK_TTL)


async def get_task(task_id: str) -> Optional[dict]:
    return await store_get(_task_key(task_id))


async def delete_task(task_id: str) -> None:
    await store_delete(_task_key(task_id))


async def task_exists(task_id: str) -> bool:
    return await store_exists(_task_key(task_id))


async def update_task(task_id: str, updates: dict) -> None:
    """Merge updates into an existing task."""
    task = await get_task(task_id)
    if task:
        task.update(updates)
        await save_task(task_id, task)


# ── Chat session helpers ─────────────────────────────────────────

def _session_key(session_id: str) -> str:
    return f"session:{session_id}"


async def save_session(session_id: str, data: dict) -> None:
    await store_set(_session_key(session_id), data, ttl=SESSION_TTL)


async def get_session(session_id: str) -> Optional[dict]:
    return await store_get(_session_key(session_id))


async def delete_session(session_id: str) -> None:
    await store_delete(_session_key(session_id))


async def session_exists(session_id: str) -> bool:
    return await store_exists(_session_key(session_id))


async def update_session(session_id: str, updates: dict) -> None:
    """Merge updates into an existing session."""
    session = await get_session(session_id)
    if session:
        session.update(updates)
        await save_session(session_id, session)
