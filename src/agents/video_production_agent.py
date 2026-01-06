from typing import Any
import httpx
from .base import BaseAgent


class VideoProductionAgent(BaseAgent):
    """
    Agent for managing video production workflow.

    Capabilities:
    - Create production schedules
    - Manage shot tracking
    - Coordinate with resources
    - Track production status
    - Handle post-production handoff
    - Manage deliverables
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        client_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "video_production_agent"

    @property
    def system_prompt(self) -> str:
        base_prompt = """You are an expert video production coordinator and manager.

Your role is to orchestrate the entire video production process:
1. Create and optimize production schedules
2. Track shot completion and progress
3. Coordinate crew and equipment resources
4. Manage production documentation
5. Facilitate post-production handoff

Production phases you manage:
- Pre-production (planning, scheduling, resource allocation)
- Production (shoot day coordination, shot tracking)
- Post-production (edit handoff, review cycles, delivery)

Documents you create/manage:
- Call sheets
- Production schedules
- Shot lists (from storyboard)
- Equipment lists
- Talent/crew lists
- Location permits
- Release forms
- Delivery specs

Production metrics you track:
- Shot completion rate
- Schedule adherence
- Budget utilization
- Resource allocation
- Deliverable status"""

        if self.client_specific_id:
            base_prompt += f"\n\nApply client-specific production requirements for client: {self.client_specific_id}"

        return base_prompt

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_production_schedule",
                "description": "Create a production schedule from storyboard and resources.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "storyboard_id": {
                            "type": "string",
                            "description": "Storyboard to schedule",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project for the production",
                        },
                        "shoot_dates": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Available shoot dates",
                        },
                        "locations": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Location details",
                        },
                        "optimize_for": {
                            "type": "string",
                            "enum": ["time", "cost", "location", "talent"],
                            "description": "Optimization priority",
                        },
                    },
                    "required": ["storyboard_id", "shoot_dates"],
                },
            },
            {
                "name": "generate_call_sheet",
                "description": "Generate a call sheet for a shoot day.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {
                            "type": "string",
                            "description": "Production schedule ID",
                        },
                        "shoot_date": {
                            "type": "string",
                            "description": "Date for call sheet",
                        },
                        "include": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to include: crew, talent, equipment, locations, schedule",
                        },
                    },
                    "required": ["schedule_id", "shoot_date"],
                },
            },
            {
                "name": "track_shot",
                "description": "Update shot status during production.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "shot_id": {
                            "type": "string",
                            "description": "Shot to update",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "setup", "filming", "completed", "needs_reshoot"],
                            "description": "Shot status",
                        },
                        "takes": {
                            "type": "integer",
                            "description": "Number of takes",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Production notes",
                        },
                        "selected_take": {
                            "type": "integer",
                            "description": "Selected take number",
                        },
                    },
                    "required": ["shot_id", "status"],
                },
            },
            {
                "name": "get_resources",
                "description": "Get available resources for production.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "enum": ["crew", "equipment", "talent", "location", "all"],
                            "description": "Type of resource",
                        },
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string"},
                                "end": {"type": "string"},
                            },
                            "description": "Date range to check availability",
                        },
                        "skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Required skills for crew",
                        },
                    },
                    "required": ["resource_type"],
                },
            },
            {
                "name": "allocate_resources",
                "description": "Allocate resources to production.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {
                            "type": "string",
                            "description": "Production schedule",
                        },
                        "allocations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "resource_id": {"type": "string"},
                                    "resource_type": {"type": "string"},
                                    "dates": {"type": "array", "items": {"type": "string"}},
                                    "role": {"type": "string"},
                                },
                            },
                            "description": "Resource allocations",
                        },
                    },
                    "required": ["schedule_id", "allocations"],
                },
            },
            {
                "name": "get_production_status",
                "description": "Get overall production status and metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {
                            "type": "string",
                            "description": "Production schedule ID",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "create_post_handoff",
                "description": "Create post-production handoff package.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {
                            "type": "string",
                            "description": "Production schedule ID",
                        },
                        "include": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to include: footage, audio, script, storyboard, selects, notes",
                        },
                        "edit_specs": {
                            "type": "object",
                            "description": "Edit specifications (format, duration, deliverables)",
                        },
                    },
                    "required": ["schedule_id"],
                },
            },
            {
                "name": "manage_deliverables",
                "description": "Track and manage video deliverables.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project ID",
                        },
                        "action": {
                            "type": "string",
                            "enum": ["list", "add", "update", "complete"],
                            "description": "Action to perform",
                        },
                        "deliverable": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "format": {"type": "string"},
                                "specs": {"type": "object"},
                                "status": {"type": "string"},
                                "due_date": {"type": "string"},
                            },
                            "description": "Deliverable details",
                        },
                    },
                    "required": ["project_id", "action"],
                },
            },
            {
                "name": "get_storyboard",
                "description": "Retrieve storyboard for production planning.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "storyboard_id": {
                            "type": "string",
                            "description": "Storyboard ID",
                        },
                    },
                    "required": ["storyboard_id"],
                },
            },
            {
                "name": "save_schedule",
                "description": "Save production schedule.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {
                            "type": "string",
                            "description": "Schedule ID if updating",
                        },
                        "title": {"type": "string"},
                        "storyboard_id": {"type": "string"},
                        "project_id": {"type": "string"},
                        "client_id": {"type": "string"},
                        "shoot_days": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Shoot day details",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["draft", "confirmed", "in_production", "wrapped", "post"],
                            "default": "draft",
                        },
                    },
                    "required": ["title", "shoot_days"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "create_production_schedule":
                return await self._create_production_schedule(tool_input)
            elif tool_name == "generate_call_sheet":
                return await self._generate_call_sheet(tool_input)
            elif tool_name == "track_shot":
                return await self._track_shot(tool_input)
            elif tool_name == "get_resources":
                return await self._get_resources(tool_input)
            elif tool_name == "allocate_resources":
                return await self._allocate_resources(tool_input)
            elif tool_name == "get_production_status":
                return await self._get_production_status(tool_input)
            elif tool_name == "create_post_handoff":
                return await self._create_post_handoff(tool_input)
            elif tool_name == "manage_deliverables":
                return await self._manage_deliverables(tool_input)
            elif tool_name == "get_storyboard":
                return await self._get_storyboard(tool_input)
            elif tool_name == "save_schedule":
                return await self._save_schedule(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _create_production_schedule(self, params: dict) -> dict:
        """Create production schedule."""
        response = await self.http_client.get(
            f"/api/v1/studio/storyboards/{params['storyboard_id']}"
        )
        storyboard = response.json() if response.status_code == 200 else None

        return {
            "status": "ready_to_create",
            "storyboard": storyboard,
            "shoot_dates": params["shoot_dates"],
            "locations": params.get("locations", []),
            "optimize_for": params.get("optimize_for", "time"),
            "instruction": "Create an optimized production schedule grouping shots efficiently.",
        }

    async def _generate_call_sheet(self, params: dict) -> dict:
        """Generate call sheet."""
        response = await self.http_client.get(
            f"/api/v1/studio/production/schedules/{params['schedule_id']}"
        )
        schedule = response.json() if response.status_code == 200 else None

        return {
            "status": "ready_to_generate",
            "schedule": schedule,
            "shoot_date": params["shoot_date"],
            "include": params.get("include", ["crew", "talent", "equipment", "schedule"]),
            "instruction": "Generate a complete call sheet with all production details.",
        }

    async def _track_shot(self, params: dict) -> dict:
        """Update shot status."""
        response = await self.http_client.patch(
            f"/api/v1/studio/production/shots/{params['shot_id']}",
            json={
                "status": params["status"],
                "takes": params.get("takes"),
                "notes": params.get("notes"),
                "selected_take": params.get("selected_take"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to update shot", "shot_id": params["shot_id"]}

    async def _get_resources(self, params: dict) -> dict:
        """Get available resources."""
        response = await self.http_client.get(
            "/api/v1/resources",
            params={
                "type": params["resource_type"],
                "start_date": params.get("date_range", {}).get("start"),
                "end_date": params.get("date_range", {}).get("end"),
                "skills": ",".join(params.get("skills", [])),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"resources": [], "note": "No resources found"}

    async def _allocate_resources(self, params: dict) -> dict:
        """Allocate resources to production."""
        response = await self.http_client.post(
            f"/api/v1/studio/production/schedules/{params['schedule_id']}/allocations",
            json={"allocations": params["allocations"]},
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to allocate resources"}

    async def _get_production_status(self, params: dict) -> dict:
        """Get production status."""
        schedule_id = params.get("schedule_id")
        project_id = params.get("project_id")

        if schedule_id:
            response = await self.http_client.get(
                f"/api/v1/studio/production/schedules/{schedule_id}/status"
            )
        elif project_id:
            response = await self.http_client.get(
                f"/api/v1/projects/{project_id}/production/status"
            )
        else:
            return {"error": "Provide schedule_id or project_id"}

        if response.status_code == 200:
            return response.json()
        return {"status": "unknown", "note": "Could not fetch status"}

    async def _create_post_handoff(self, params: dict) -> dict:
        """Create post-production handoff."""
        response = await self.http_client.get(
            f"/api/v1/studio/production/schedules/{params['schedule_id']}"
        )
        schedule = response.json() if response.status_code == 200 else None

        return {
            "status": "ready_to_create",
            "schedule": schedule,
            "include": params.get("include", ["footage", "audio", "script", "selects"]),
            "edit_specs": params.get("edit_specs", {}),
            "instruction": "Create a complete post-production handoff package.",
        }

    async def _manage_deliverables(self, params: dict) -> dict:
        """Manage deliverables."""
        action = params["action"]
        project_id = params["project_id"]

        if action == "list":
            response = await self.http_client.get(
                f"/api/v1/projects/{project_id}/deliverables"
            )
        elif action == "add":
            response = await self.http_client.post(
                f"/api/v1/projects/{project_id}/deliverables",
                json=params.get("deliverable", {}),
            )
        elif action == "update":
            deliverable = params.get("deliverable", {})
            response = await self.http_client.patch(
                f"/api/v1/projects/{project_id}/deliverables/{deliverable.get('id')}",
                json=deliverable,
            )
        elif action == "complete":
            deliverable = params.get("deliverable", {})
            response = await self.http_client.patch(
                f"/api/v1/projects/{project_id}/deliverables/{deliverable.get('id')}",
                json={"status": "completed"},
            )
        else:
            return {"error": f"Unknown action: {action}"}

        if response.status_code in (200, 201):
            return response.json()
        return {"error": f"Failed to {action} deliverable"}

    async def _get_storyboard(self, params: dict) -> dict:
        """Get storyboard."""
        response = await self.http_client.get(
            f"/api/v1/studio/storyboards/{params['storyboard_id']}"
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Storyboard not found"}

    async def _save_schedule(self, params: dict) -> dict:
        """Save production schedule."""
        response = await self.http_client.post(
            "/api/v1/studio/production/schedules",
            json={
                "title": params["title"],
                "storyboard_id": params.get("storyboard_id"),
                "project_id": params.get("project_id"),
                "client_id": params.get("client_id") or self.client_specific_id,
                "shoot_days": params["shoot_days"],
                "status": params.get("status", "draft"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to save schedule"}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
