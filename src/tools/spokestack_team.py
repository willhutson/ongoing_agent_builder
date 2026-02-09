"""
SpokeStack Team Tools (Integration Spec Section 11.4)

Tools for querying team members and assigning work in SpokeStack.
"""

from datetime import datetime, timezone
from uuid import uuid4
import logging

from ..agents.base import AgentContext
from ..protocols.work import AgentWorkModule, AgentActionType
from .spokestack_base import SpokeStackToolBase

logger = logging.getLogger(__name__)


class TeamTools(SpokeStackToolBase):
    """Tools for the Team module in SpokeStack."""

    MODULE = AgentWorkModule.TEAM

    @staticmethod
    def tool_definitions() -> list[dict]:
        """Return Claude tool definitions for team operations."""
        return [
            {
                "name": "get_team_members",
                "description": "Get team members, optionally filtered by department or skill.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "department": {"type": "string", "description": "Filter by department"},
                        "skill": {"type": "string", "description": "Filter by skill"},
                        "available_only": {"type": "boolean", "default": False},
                    },
                },
            },
            {
                "name": "assign_to_user",
                "description": "Assign an entity (brief, project, task) to a team member.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "entity_type": {"type": "string", "enum": ["brief", "project", "task"]},
                        "entity_id": {"type": "string", "description": "Entity ID"},
                        "user_id": {"type": "string", "description": "Team member user ID"},
                        "message": {"type": "string", "description": "Optional assignment message"},
                    },
                    "required": ["entity_type", "entity_id", "user_id"],
                },
            },
        ]

    async def get_team_members(self, department: str = None, skill: str = None,
                                available_only: bool = False, context: AgentContext = None) -> dict:
        """Get team members from SpokeStack."""
        try:
            org_id = context.organization_id or context.tenant_id if context else None
            params = {}
            if department:
                params["department"] = department
            if skill:
                params["skill"] = skill
            if available_only:
                params["availableOnly"] = "true"
            return await self.client.get("/api/v1/team", params=params, organization_id=org_id)
        except Exception as e:
            logger.error(f"Failed to get team members: {e}")
            return {"team": [], "error": str(e)}

    async def assign_to_user(self, entity_type: str, entity_id: str,
                              user_id: str, message: str = None,
                              context: AgentContext = None) -> dict:
        """Assign an entity to a team member with work event."""
        try:
            org_id = context.organization_id or context.tenant_id if context else None
            response = await self.client.post(
                f"/api/v1/{entity_type}s/{entity_id}/assign",
                json={"userId": user_id, "message": message},
                organization_id=org_id,
            )
            user_name = response.get("userName", user_id)

            await context.emit_sse({
                "type": "action",
                "action": {
                    "id": f"act_{uuid4().hex[:8]}",
                    "type": AgentActionType.ASSIGN.value,
                    "displayValue": f"Assigned to {user_name}",
                    "status": "success",
                    "module": self.MODULE.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            })
            return {"success": True, "assigned_to": user_name}

        except Exception as e:
            logger.error(f"Failed to assign: {e}")
            return {"success": False, "error": str(e)}
