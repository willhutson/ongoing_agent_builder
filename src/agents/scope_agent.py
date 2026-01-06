from typing import Any
import httpx
from .base import BaseAgent


class ScopeAgent(BaseAgent):
    """
    Agent for scope management and change control.

    Capabilities:
    - Define project scope
    - Track scope changes
    - Assess change impact
    - Manage scope requests
    - Prevent scope creep
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "scope_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a scope management expert.

Your role is to manage and protect project scope:
1. Define clear scope boundaries
2. Track and document scope changes
3. Assess impact of change requests
4. Manage approval workflow for changes
5. Prevent scope creep"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_scope",
                "description": "Get project scope definition.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                    },
                    "required": ["project_id"],
                },
            },
            {
                "name": "create_change_request",
                "description": "Create scope change request.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "description": {"type": "string"},
                        "justification": {"type": "string"},
                        "requested_by": {"type": "string"},
                    },
                    "required": ["project_id", "description"],
                },
            },
            {
                "name": "assess_change_impact",
                "description": "Assess impact of scope change.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "change_request_id": {"type": "string"},
                        "assess": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["change_request_id"],
                },
            },
            {
                "name": "approve_change",
                "description": "Approve or reject scope change.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "change_request_id": {"type": "string"},
                        "decision": {"type": "string", "enum": ["approved", "rejected"]},
                        "comments": {"type": "string"},
                    },
                    "required": ["change_request_id", "decision"],
                },
            },
            {
                "name": "get_change_history",
                "description": "Get scope change history.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                    },
                    "required": ["project_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "get_scope":
                response = await self.http_client.get(f"/api/v1/projects/{tool_input['project_id']}/scope")
                return response.json() if response.status_code == 200 else {"scope": None}
            elif tool_name == "create_change_request":
                response = await self.http_client.post(f"/api/v1/projects/{tool_input['project_id']}/scope-changes", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create"}
            elif tool_name == "assess_change_impact":
                return {
                    "status": "ready_to_assess",
                    "change_request_id": tool_input["change_request_id"],
                    "instruction": "Assess scope change impact on timeline, budget, and resources.",
                }
            elif tool_name == "approve_change":
                response = await self.http_client.post(f"/api/v1/scope-changes/{tool_input['change_request_id']}/decision", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed to process"}
            elif tool_name == "get_change_history":
                response = await self.http_client.get(f"/api/v1/projects/{tool_input['project_id']}/scope-changes")
                return response.json() if response.status_code == 200 else {"history": []}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
