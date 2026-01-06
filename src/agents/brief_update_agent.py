from typing import Any
import httpx
from .base import BaseAgent


class BriefUpdateAgent(BaseAgent):
    """
    Agent for managing brief updates and change communications.

    Capabilities:
    - Track brief changes and revisions
    - Generate change summaries
    - Notify stakeholders of updates
    - Compare brief versions
    - Assess impact of changes
    - Maintain change history
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        language: str = "en",
        client_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.language = language
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "brief_update_agent"

    @property
    def system_prompt(self) -> str:
        base_prompt = """You are an expert at managing brief updates and change communications.

Your role is to ensure smooth handling of brief changes:
1. Detect and categorize changes between versions
2. Assess impact on timeline, budget, and scope
3. Generate clear change summaries
4. Notify relevant stakeholders
5. Maintain audit trail of changes

Types of changes you track:
- Scope changes (additions, removals, modifications)
- Timeline changes (deadline shifts, milestone updates)
- Budget changes (increases, decreases, reallocation)
- Deliverable changes (new outputs, modified specs)
- Stakeholder changes (new contacts, role changes)
- Technical changes (platform, format, specs)

Impact assessment includes:
- Resource implications
- Timeline impact
- Budget implications
- Risk factors
- Dependencies affected

Communication approach:
- Clear before/after comparison
- Impact highlighted prominently
- Action required stated clearly
- Version tracking visible"""

        if self.language != "en":
            base_prompt += f"\n\nPrimary language: {self.language}"
        if self.client_specific_id:
            base_prompt += f"\n\nApply client-specific change management process for client: {self.client_specific_id}"

        return base_prompt

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "detect_changes",
                "description": "Compare brief versions and detect changes.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief to analyze",
                        },
                        "version_from": {
                            "type": "integer",
                            "description": "Starting version number",
                        },
                        "version_to": {
                            "type": "integer",
                            "description": "Ending version number (latest if omitted)",
                        },
                    },
                    "required": ["brief_id"],
                },
            },
            {
                "name": "assess_impact",
                "description": "Assess impact of brief changes.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief ID",
                        },
                        "changes": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Changes to assess (or fetch from brief)",
                        },
                        "assess": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to assess: timeline, budget, resources, risk, scope",
                        },
                    },
                    "required": ["brief_id"],
                },
            },
            {
                "name": "generate_change_summary",
                "description": "Generate a human-readable change summary.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief ID",
                        },
                        "changes": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Changes to summarize",
                        },
                        "impact": {
                            "type": "object",
                            "description": "Impact assessment",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["detailed", "executive", "technical"],
                            "description": "Summary format",
                        },
                    },
                    "required": ["brief_id"],
                },
            },
            {
                "name": "notify_stakeholders",
                "description": "Send update notifications to stakeholders.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief ID",
                        },
                        "update_summary": {
                            "type": "object",
                            "description": "Change summary to send",
                        },
                        "stakeholders": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Who to notify (auto-detect if empty)",
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["whatsapp", "email", "slack", "sms", "all"],
                            "description": "Notification channel",
                        },
                        "require_acknowledgment": {
                            "type": "boolean",
                            "description": "Require stakeholders to acknowledge",
                            "default": False,
                        },
                    },
                    "required": ["brief_id"],
                },
            },
            {
                "name": "get_brief_history",
                "description": "Get version history for a brief.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief ID",
                        },
                        "include_changes": {
                            "type": "boolean",
                            "description": "Include change details",
                            "default": True,
                        },
                    },
                    "required": ["brief_id"],
                },
            },
            {
                "name": "get_brief_version",
                "description": "Get a specific version of a brief.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief ID",
                        },
                        "version": {
                            "type": "integer",
                            "description": "Version number (latest if omitted)",
                        },
                    },
                    "required": ["brief_id"],
                },
            },
            {
                "name": "create_change_request",
                "description": "Create a formal change request.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief ID",
                        },
                        "requested_changes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "field": {"type": "string"},
                                    "current_value": {"type": "string"},
                                    "proposed_value": {"type": "string"},
                                    "reason": {"type": "string"},
                                },
                            },
                            "description": "Requested changes",
                        },
                        "requester_id": {
                            "type": "string",
                            "description": "Who is requesting",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Change priority",
                        },
                    },
                    "required": ["brief_id", "requested_changes", "requester_id"],
                },
            },
            {
                "name": "apply_changes",
                "description": "Apply approved changes to brief.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief ID",
                        },
                        "change_request_id": {
                            "type": "string",
                            "description": "Approved change request ID",
                        },
                        "changes": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Changes to apply (if no change request)",
                        },
                        "create_version": {
                            "type": "boolean",
                            "description": "Create new version",
                            "default": True,
                        },
                    },
                    "required": ["brief_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "detect_changes":
                return await self._detect_changes(tool_input)
            elif tool_name == "assess_impact":
                return await self._assess_impact(tool_input)
            elif tool_name == "generate_change_summary":
                return await self._generate_change_summary(tool_input)
            elif tool_name == "notify_stakeholders":
                return await self._notify_stakeholders(tool_input)
            elif tool_name == "get_brief_history":
                return await self._get_brief_history(tool_input)
            elif tool_name == "get_brief_version":
                return await self._get_brief_version(tool_input)
            elif tool_name == "create_change_request":
                return await self._create_change_request(tool_input)
            elif tool_name == "apply_changes":
                return await self._apply_changes(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _detect_changes(self, params: dict) -> dict:
        """Detect changes between brief versions."""
        brief_id = params["brief_id"]
        version_from = params.get("version_from", 1)
        version_to = params.get("version_to")

        # Get versions
        from_response = await self.http_client.get(
            f"/api/v1/briefs/{brief_id}/versions/{version_from}"
        )
        from_version = from_response.json() if from_response.status_code == 200 else None

        if version_to:
            to_response = await self.http_client.get(
                f"/api/v1/briefs/{brief_id}/versions/{version_to}"
            )
        else:
            to_response = await self.http_client.get(f"/api/v1/briefs/{brief_id}")
        to_version = to_response.json() if to_response.status_code == 200 else None

        return {
            "status": "ready_to_compare",
            "version_from": from_version,
            "version_to": to_version,
            "instruction": "Compare the two versions and identify all changes categorized by type.",
        }

    async def _assess_impact(self, params: dict) -> dict:
        """Assess impact of changes."""
        brief_id = params["brief_id"]

        # Get current brief and project data
        brief_response = await self.http_client.get(f"/api/v1/briefs/{brief_id}")
        brief = brief_response.json() if brief_response.status_code == 200 else None

        project_id = brief.get("project_id") if brief else None
        project = None
        if project_id:
            project_response = await self.http_client.get(
                f"/api/v1/projects/{project_id}",
                params={"include": "resources,budget,timeline"},
            )
            project = project_response.json() if project_response.status_code == 200 else None

        return {
            "status": "ready_to_assess",
            "brief": brief,
            "project": project,
            "changes": params.get("changes"),
            "assess": params.get("assess", ["timeline", "budget", "resources", "scope"]),
            "instruction": "Assess the impact of changes on timeline, budget, resources, and scope.",
        }

    async def _generate_change_summary(self, params: dict) -> dict:
        """Generate change summary."""
        return {
            "status": "ready_to_generate",
            "brief_id": params["brief_id"],
            "changes": params.get("changes"),
            "impact": params.get("impact"),
            "format": params.get("format", "detailed"),
            "language": self.language,
            "instruction": "Generate a clear change summary with before/after comparison and impact.",
        }

    async def _notify_stakeholders(self, params: dict) -> dict:
        """Notify stakeholders of changes."""
        brief_id = params["brief_id"]

        # Get stakeholders if not provided
        stakeholders = params.get("stakeholders")
        if not stakeholders:
            response = await self.http_client.get(
                f"/api/v1/briefs/{brief_id}/stakeholders"
            )
            if response.status_code == 200:
                stakeholders = [s["id"] for s in response.json().get("stakeholders", [])]

        # Send notification
        response = await self.http_client.post(
            f"/api/v1/briefs/{brief_id}/notifications",
            json={
                "type": "update",
                "summary": params.get("update_summary"),
                "stakeholders": stakeholders,
                "channel": params.get("channel", "email"),
                "require_acknowledgment": params.get("require_acknowledgment", False),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to send notifications"}

    async def _get_brief_history(self, params: dict) -> dict:
        """Get brief version history."""
        response = await self.http_client.get(
            f"/api/v1/briefs/{params['brief_id']}/history",
            params={"include_changes": params.get("include_changes", True)},
        )
        if response.status_code == 200:
            return response.json()
        return {"history": [], "note": "No history found"}

    async def _get_brief_version(self, params: dict) -> dict:
        """Get specific brief version."""
        brief_id = params["brief_id"]
        version = params.get("version")

        if version:
            response = await self.http_client.get(
                f"/api/v1/briefs/{brief_id}/versions/{version}"
            )
        else:
            response = await self.http_client.get(f"/api/v1/briefs/{brief_id}")

        if response.status_code == 200:
            return response.json()
        return {"error": "Brief version not found"}

    async def _create_change_request(self, params: dict) -> dict:
        """Create change request."""
        response = await self.http_client.post(
            f"/api/v1/briefs/{params['brief_id']}/change-requests",
            json={
                "requested_changes": params["requested_changes"],
                "requester_id": params["requester_id"],
                "priority": params.get("priority", "medium"),
                "client_id": self.client_specific_id,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to create change request"}

    async def _apply_changes(self, params: dict) -> dict:
        """Apply changes to brief."""
        brief_id = params["brief_id"]

        if params.get("change_request_id"):
            response = await self.http_client.post(
                f"/api/v1/briefs/{brief_id}/change-requests/{params['change_request_id']}/apply",
                json={"create_version": params.get("create_version", True)},
            )
        else:
            response = await self.http_client.patch(
                f"/api/v1/briefs/{brief_id}",
                json={
                    "changes": params.get("changes", []),
                    "create_version": params.get("create_version", True),
                },
            )

        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to apply changes"}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
