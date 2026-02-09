"""
SpokeStack Tool Base

Base class for all SpokeStack tools. Handles:
- API calls to SpokeStack ERP
- SSE work event emission
- Error handling with spec-compliant error codes
"""

from typing import Optional, Any
from datetime import datetime, timezone
from uuid import uuid4
import asyncio
import httpx
import logging

from ..agents.base import AgentContext
from ..protocols.work import AgentWorkModule, AgentActionType

logger = logging.getLogger(__name__)


class SpokeStackClient:
    """HTTP client for SpokeStack ERP API calls."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    async def get(self, path: str, params: dict = None,
                  organization_id: str = None) -> dict:
        """GET request to SpokeStack API."""
        headers = {}
        if organization_id:
            headers["X-Organization-Id"] = organization_id
        response = await self._client.get(path, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def post(self, path: str, json: dict = None,
                   organization_id: str = None) -> dict:
        """POST request to SpokeStack API."""
        headers = {}
        if organization_id:
            headers["X-Organization-Id"] = organization_id
        response = await self._client.post(path, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    async def patch(self, path: str, json: dict = None,
                    organization_id: str = None) -> dict:
        """PATCH request to SpokeStack API."""
        headers = {}
        if organization_id:
            headers["X-Organization-Id"] = organization_id
        response = await self._client.patch(path, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self._client.aclose()


class SpokeStackToolBase:
    """
    Base class for SpokeStack tools.

    Provides helpers for:
    - Emitting work events during tool execution
    - Making API calls to SpokeStack
    - Filling form fields with visual progress
    """

    def __init__(self, spokestack_client: SpokeStackClient):
        self.client = spokestack_client

    async def fill_fields(self, context: AgentContext, fields: list[tuple[str, Any]],
                          module: AgentWorkModule, route: str) -> None:
        """
        Fill multiple form fields, emitting SSE events for each.
        Follows the spec Section 11.5 pattern with visual delay.

        Args:
            context: Agent context with SSE callback
            fields: List of (field_name, value) tuples
            module: SpokeStack module being operated
            route: Current route in SpokeStack
        """
        for field_name, value in fields:
            if value is not None and value != "":
                await context.emit_sse({
                    "type": "action",
                    "action": {
                        "id": f"act_{uuid4().hex[:8]}",
                        "type": AgentActionType.FILL_FIELD.value,
                        "field": field_name,
                        "fieldLabel": field_name.replace("_", " ").title(),
                        "displayValue": str(value)[:50],
                        "status": "filled",
                        "module": module.value,
                        "route": route,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                })
                await asyncio.sleep(0.1)  # Small delay for visual effect

    async def emit_navigate(self, context: AgentContext, module: AgentWorkModule,
                            route: str) -> None:
        """Emit a navigation action event."""
        await context.emit_sse({
            "type": "action",
            "action": {
                "id": f"act_{uuid4().hex[:8]}",
                "type": AgentActionType.NAVIGATE.value,
                "module": module.value,
                "route": route,
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        })

    async def emit_submit(self, context: AgentContext, module: AgentWorkModule,
                          route: str, success: bool = True,
                          message: str = None) -> None:
        """Emit a form submission action event."""
        await context.emit_sse({
            "type": "action",
            "action": {
                "id": f"act_{uuid4().hex[:8]}",
                "type": AgentActionType.SUBMIT.value,
                "module": module.value,
                "route": route,
                "status": "success" if success else "error",
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        })
