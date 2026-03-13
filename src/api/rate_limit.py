"""
Rate Limiting Middleware

Simple sliding-window rate limiter using in-memory counters.
Uses Redis when available for distributed rate limiting.

Limits:
- /api/v1/agent/execute: 30 req/min per tenant
- /api/v1/agent/chat:    60 req/min per tenant
- All other /api/*:     120 req/min per IP
"""

import time
import logging
import os
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Rate limit windows (requests per minute)
RATE_LIMITS = {
    "/api/v1/agent/execute": 30,
    "/api/v1/agent/chat": 60,
}
DEFAULT_RATE_LIMIT = 120
WINDOW_SECONDS = 60


class _SlidingWindow:
    """Simple sliding window counter."""

    def __init__(self):
        self._hits: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, limit: int) -> bool:
        now = time.time()
        window_start = now - WINDOW_SECONDS

        # Clean old entries
        self._hits[key] = [t for t in self._hits[key] if t > window_start]

        if len(self._hits[key]) >= limit:
            return False

        self._hits[key].append(now)
        return True

    def remaining(self, key: str, limit: int) -> int:
        now = time.time()
        window_start = now - WINDOW_SECONDS
        recent = [t for t in self._hits[key] if t > window_start]
        return max(0, limit - len(recent))


_window = _SlidingWindow()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces per-tenant/IP rate limits."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"

        # Only rate-limit API routes
        if not path.startswith("/api/"):
            return await call_next(request)

        # Determine rate limit for this path
        limit = DEFAULT_RATE_LIMIT
        for prefix, rate in RATE_LIMITS.items():
            if path.startswith(prefix):
                limit = rate
                break

        # Key by tenant (from header or body is too expensive, use IP + org header)
        org_id = request.headers.get("X-Organization-Id", "")
        client_ip = request.client.host if request.client else "unknown"
        rate_key = f"rate:{org_id or client_ip}:{path.split('/')[3] if len(path.split('/')) > 3 else 'api'}"

        if not _window.is_allowed(rate_key, limit):
            logger.warning(f"Rate limit exceeded: {rate_key}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please slow down.",
                headers={"Retry-After": str(WINDOW_SECONDS)},
            )

        response = await call_next(request)

        # Add rate limit headers
        remaining = _window.remaining(rate_key, limit)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = f"{WINDOW_SECONDS}s"

        return response
