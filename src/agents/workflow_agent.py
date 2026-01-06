from typing import Any
import httpx
from .base import BaseAgent


class WorkflowAgent(BaseAgent):
    """
    Agent for workflow automation and management.

    Capabilities:
    - Define and manage workflows
    - Automate task transitions
    - Handle workflow triggers
    - Manage approvals within workflows
    - Track workflow status
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
        return "workflow_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a workflow automation expert.

Your role is to manage and optimize workflows:
1. Design efficient workflows
2. Automate task transitions
3. Handle workflow triggers
4. Manage approval flows
5. Track and report on workflow status"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_workflow",
                "description": "Get workflow definition.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "workflow_type": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "create_workflow",
                "description": "Create a new workflow.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "steps": {"type": "array", "items": {"type": "object"}},
                        "triggers": {"type": "array", "items": {"type": "object"}},
                    },
                    "required": ["name", "steps"],
                },
            },
            {
                "name": "trigger_workflow",
                "description": "Trigger a workflow instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "context": {"type": "object"},
                    },
                    "required": ["workflow_id"],
                },
            },
            {
                "name": "advance_workflow",
                "description": "Advance workflow to next step.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "action": {"type": "string"},
                        "data": {"type": "object"},
                    },
                    "required": ["instance_id", "action"],
                },
            },
            {
                "name": "get_workflow_status",
                "description": "Get workflow instance status.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "project_id": {"type": "string"},
                    },
                    "required": [],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "get_workflow":
                response = await self.http_client.get(f"/api/v1/workflows/{tool_input.get('workflow_id', '')}", params=tool_input)
                return response.json() if response.status_code == 200 else {"workflow": None}
            elif tool_name == "create_workflow":
                response = await self.http_client.post("/api/v1/workflows", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create"}
            elif tool_name == "trigger_workflow":
                response = await self.http_client.post(f"/api/v1/workflows/{tool_input['workflow_id']}/trigger", json=tool_input.get("context", {}))
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to trigger"}
            elif tool_name == "advance_workflow":
                response = await self.http_client.post(f"/api/v1/workflows/instances/{tool_input['instance_id']}/advance", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed to advance"}
            elif tool_name == "get_workflow_status":
                if tool_input.get("instance_id"):
                    response = await self.http_client.get(f"/api/v1/workflows/instances/{tool_input['instance_id']}")
                else:
                    response = await self.http_client.get("/api/v1/workflows/instances", params=tool_input)
                return response.json() if response.status_code == 200 else {"status": "unknown"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
