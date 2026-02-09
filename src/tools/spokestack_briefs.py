"""
SpokeStack Briefs Tools (Integration Spec Section 11.4)

Tools for creating and managing briefs in SpokeStack.
Emits Agent Work Protocol SSE events for the Mission Control UI.
"""

from typing import Optional
from uuid import uuid4
from pydantic import BaseModel
import logging

from ..agents.base import AgentContext
from ..protocols.work import AgentWorkModule
from .spokestack_base import SpokeStackToolBase

logger = logging.getLogger(__name__)


class CreateBriefParams(BaseModel):
    """Parameters for creating a brief."""
    title: str
    type: str  # VIDEO_SHOOT, VIDEO_EDIT, DESIGN, COPYWRITING, etc.
    client_id: str
    assignee_id: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[str] = None  # ISO date
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, URGENT


class CreateBriefResult(BaseModel):
    """Result from creating a brief."""
    success: bool
    brief_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None


class BriefTools(SpokeStackToolBase):
    """Tools for the Briefs module in SpokeStack."""

    MODULE = AgentWorkModule.BRIEFS

    @staticmethod
    def tool_definitions() -> list[dict]:
        """Return Claude tool definitions for brief operations."""
        return [
            {
                "name": "create_brief",
                "description": "Create a new brief in SpokeStack. Emits work events showing form filling in the Agent Work pane.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Brief title"},
                        "type": {
                            "type": "string",
                            "enum": ["VIDEO_SHOOT", "VIDEO_EDIT", "DESIGN", "COPYWRITING",
                                     "SOCIAL_MEDIA", "CAMPAIGN", "EVENT", "PR", "OTHER"],
                            "description": "Brief type",
                        },
                        "client_id": {"type": "string", "description": "Client ID"},
                        "assignee_id": {"type": "string", "description": "Team member to assign to"},
                        "description": {"type": "string", "description": "Brief description"},
                        "deadline": {"type": "string", "description": "Deadline (ISO date)"},
                        "priority": {
                            "type": "string",
                            "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"],
                            "default": "MEDIUM",
                        },
                    },
                    "required": ["title", "type", "client_id"],
                },
            },
            {
                "name": "get_briefs",
                "description": "Get list of briefs, optionally filtered by client or status.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Filter by client ID"},
                        "status": {
                            "type": "string",
                            "enum": ["draft", "active", "completed", "cancelled"],
                            "description": "Filter by status",
                        },
                        "limit": {"type": "integer", "default": 20},
                    },
                },
            },
        ]

    async def create_brief(self, params: CreateBriefParams,
                           context: AgentContext) -> CreateBriefResult:
        """
        Create a brief in SpokeStack, emitting work events for the Agent Work pane.
        Follows the spec Section 11.5 implementation pattern.
        """
        route = "/briefs/new"
        pending_fields = ["title", "type", "client", "description", "deadline", "assignee"]

        # 1. Emit work_start
        await context.emit_sse({
            "type": "work_start",
            "module": self.MODULE.value,
            "route": route,
            "pendingFields": pending_fields,
        })

        # 2. Fill form fields with visual progress
        fields_to_fill = [
            ("title", params.title),
            ("type", params.type),
            ("client", params.client_id),
            ("description", params.description or ""),
            ("deadline", params.deadline or ""),
            ("priority", params.priority),
        ]
        if params.assignee_id:
            fields_to_fill.append(("assignee", params.assignee_id))

        await self.fill_fields(context, fields_to_fill, self.MODULE, route)

        # 3. Call SpokeStack API
        try:
            org_id = context.organization_id or context.tenant_id
            brief_data = {
                "title": params.title,
                "type": params.type,
                "clientId": params.client_id,
                "description": params.description,
                "deadline": params.deadline,
                "assigneeId": params.assignee_id,
                "priority": params.priority,
            }
            brief_data = {k: v for k, v in brief_data.items() if v is not None}

            response = await self.client.post(
                "/api/v1/briefs",
                json=brief_data,
                organization_id=org_id,
            )

            brief_id = response.get("id", str(uuid4()))
            brief_title = response.get("title", params.title)

            # 4. Emit submit
            await self.emit_submit(context, self.MODULE, route)

            # 5. Emit entity_created
            await context.emit_sse({
                "type": "entity_created",
                "entity": {
                    "id": brief_id,
                    "type": "brief",
                    "title": brief_title,
                    "module": self.MODULE.value,
                    "url": f"/briefs/{brief_id}",
                },
            })

            # 6. Emit work_complete
            await context.emit_sse({
                "type": "work_complete",
                "state": {
                    "isWorking": False,
                    "createdEntities": [{
                        "id": brief_id,
                        "type": "brief",
                        "title": brief_title,
                        "module": self.MODULE.value,
                        "url": f"/briefs/{brief_id}",
                    }],
                },
            })

            return CreateBriefResult(success=True, brief_id=brief_id, url=f"/briefs/{brief_id}")

        except Exception as e:
            logger.error(f"Failed to create brief: {e}")
            await context.emit_sse({"type": "work_error", "error": f"Failed to create brief: {str(e)}"})
            return CreateBriefResult(success=False, error=str(e))

    async def get_briefs(self, client_id: str = None, status: str = None,
                         limit: int = 20, context: AgentContext = None) -> dict:
        """Get briefs from SpokeStack."""
        try:
            org_id = context.organization_id or context.tenant_id if context else None
            params = {}
            if client_id:
                params["clientId"] = client_id
            if status:
                params["status"] = status
            params["limit"] = limit

            return await self.client.get("/api/v1/briefs", params=params, organization_id=org_id)
        except Exception as e:
            logger.error(f"Failed to get briefs: {e}")
            return {"briefs": [], "error": str(e)}
