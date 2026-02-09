"""
SpokeStack Projects Tools (Integration Spec Section 11.4)

Tools for creating and managing projects and milestones in SpokeStack.
"""

from typing import Optional
from uuid import uuid4
import logging

from ..agents.base import AgentContext
from ..protocols.work import AgentWorkModule
from .spokestack_base import SpokeStackToolBase

logger = logging.getLogger(__name__)


class ProjectTools(SpokeStackToolBase):
    """Tools for the Projects module in SpokeStack."""

    MODULE = AgentWorkModule.PROJECTS

    @staticmethod
    def tool_definitions() -> list[dict]:
        """Return Claude tool definitions for project operations."""
        return [
            {
                "name": "create_project",
                "description": "Create a new project in SpokeStack.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name"},
                        "client_id": {"type": "string", "description": "Client ID"},
                        "budget": {"type": "number", "description": "Project budget"},
                        "start_date": {"type": "string", "description": "Start date (ISO)"},
                        "end_date": {"type": "string", "description": "End date (ISO)"},
                        "description": {"type": "string", "description": "Project description"},
                    },
                    "required": ["name", "client_id"],
                },
            },
            {
                "name": "add_project_milestone",
                "description": "Add a milestone to an existing project.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "name": {"type": "string", "description": "Milestone name"},
                        "due_date": {"type": "string", "description": "Due date (ISO)"},
                        "description": {"type": "string", "description": "Milestone description"},
                    },
                    "required": ["project_id", "name", "due_date"],
                },
            },
        ]

    async def create_project(self, name: str, client_id: str,
                              budget: float = None, start_date: str = None,
                              end_date: str = None, description: str = None,
                              context: AgentContext = None) -> dict:
        """Create a project in SpokeStack with work events."""
        route = "/projects/new"

        await context.emit_sse({
            "type": "work_start",
            "module": self.MODULE.value,
            "route": route,
            "pendingFields": ["name", "client", "budget", "start_date", "end_date", "description"],
        })

        fields = [
            ("name", name), ("client", client_id), ("budget", budget),
            ("start_date", start_date), ("end_date", end_date), ("description", description),
        ]
        await self.fill_fields(context, fields, self.MODULE, route)

        try:
            org_id = context.organization_id or context.tenant_id
            project_data = {"name": name, "clientId": client_id, "budget": budget,
                           "startDate": start_date, "endDate": end_date, "description": description}
            project_data = {k: v for k, v in project_data.items() if v is not None}

            response = await self.client.post("/api/v1/projects", json=project_data, organization_id=org_id)
            project_id = response.get("id", str(uuid4()))

            await self.emit_submit(context, self.MODULE, route)
            await context.emit_sse({
                "type": "entity_created",
                "entity": {"id": project_id, "type": "project", "title": name,
                          "module": self.MODULE.value, "url": f"/projects/{project_id}"},
            })
            await context.emit_sse({
                "type": "work_complete",
                "state": {"isWorking": False, "createdEntities": [
                    {"id": project_id, "type": "project", "title": name,
                     "module": self.MODULE.value, "url": f"/projects/{project_id}"}
                ]},
            })
            return {"success": True, "project_id": project_id, "url": f"/projects/{project_id}"}

        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            await context.emit_sse({"type": "work_error", "error": str(e)})
            return {"success": False, "error": str(e)}

    async def add_milestone(self, project_id: str, name: str, due_date: str,
                             description: str = None, context: AgentContext = None) -> dict:
        """Add a milestone to a project."""
        try:
            org_id = context.organization_id or context.tenant_id
            milestone_data = {"name": name, "dueDate": due_date, "description": description}
            milestone_data = {k: v for k, v in milestone_data.items() if v is not None}

            response = await self.client.post(
                f"/api/v1/projects/{project_id}/milestones", json=milestone_data, organization_id=org_id)
            milestone_id = response.get("id", str(uuid4()))

            await context.emit_sse({
                "type": "entity_created",
                "entity": {"id": milestone_id, "type": "milestone", "title": name,
                          "module": self.MODULE.value, "url": f"/projects/{project_id}/milestones/{milestone_id}"},
            })
            return {"success": True, "milestone_id": milestone_id}

        except Exception as e:
            logger.error(f"Failed to add milestone: {e}")
            return {"success": False, "error": str(e)}
