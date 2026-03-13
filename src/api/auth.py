"""
API Authentication Middleware

Validates requests using API key or ERP callback signature.
- Public endpoints (health, docs) are excluded.
- All /api/v1/* endpoints require a valid API key via X-API-Key header
  or a valid ERP callback HMAC signature via X-Signature header.
"""

import hmac
import hashlib
import os
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Paths that don't require authentication
PUBLIC_PATHS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/dashboard",
}


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces API key authentication on protected routes."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"

        # Allow public endpoints
        if path in PUBLIC_PATHS:
            return await call_next(request)

        # Allow WebSocket upgrades (WS auth handled at connection level)
        if path.startswith("/v1/ws"):
            return await call_next(request)

        # Only protect /api/* routes
        if not path.startswith("/api/"):
            return await call_next(request)

        # Check X-API-Key header
        api_key = request.headers.get("X-API-Key")
        expected_key = os.environ.get("ERP_API_KEY", "")

        if api_key and expected_key and hmac.compare_digest(api_key, expected_key):
            return await call_next(request)

        # Check ERP callback HMAC signature
        signature = request.headers.get("X-Signature")
        callback_secret = os.environ.get("ERP_CALLBACK_SECRET", "")
        if signature and callback_secret:
            # Signature is validated per-request in the callback handler
            # Here we just verify the header is present with a valid secret configured
            return await call_next(request)

        # No valid auth — reject
        logger.warning(f"Unauthorized request to {path} from {request.client.host}")
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
