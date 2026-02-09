"""
SpokeStack Clients Tools (Integration Spec Section 11.4)

Tools for querying client data and context from SpokeStack.
"""

import logging

from ..agents.base import AgentContext
from ..protocols.work import AgentWorkModule
from .spokestack_base import SpokeStackToolBase

logger = logging.getLogger(__name__)


class ClientTools(SpokeStackToolBase):
    """Tools for the Clients module in SpokeStack."""

    MODULE = AgentWorkModule.CLIENTS

    @staticmethod
    def tool_definitions() -> list[dict]:
        """Return Claude tool definitions for client operations."""
        return [
            {
                "name": "get_clients",
                "description": "Get list of clients for the organization.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "active_only": {"type": "boolean", "default": True, "description": "Only active clients"},
                    },
                },
            },
            {
                "name": "get_client_context",
                "description": "Get full context for a client including brand guide, recent work, and team members.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client ID"},
                    },
                    "required": ["client_id"],
                },
            },
        ]

    async def get_clients(self, active_only: bool = True, context: AgentContext = None) -> dict:
        """Get clients from SpokeStack."""
        try:
            org_id = context.organization_id or context.tenant_id if context else None
            params = {"activeOnly": "true"} if active_only else {}
            return await self.client.get("/api/v1/clients", params=params, organization_id=org_id)
        except Exception as e:
            logger.error(f"Failed to get clients: {e}")
            return {"clients": [], "error": str(e)}

    async def get_client_context(self, client_id: str, context: AgentContext = None) -> dict:
        """Get full context for a client."""
        try:
            org_id = context.organization_id or context.tenant_id if context else None
            return await self.client.get(f"/api/v1/clients/{client_id}/context", organization_id=org_id)
        except Exception as e:
            logger.error(f"Failed to get client context: {e}")
            return {"client": None, "brand_guide": None, "recent_briefs": [],
                    "recent_calendar_entries": [], "team_members": [], "error": str(e)}
