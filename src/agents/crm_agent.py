from typing import Any
import httpx
from .base import BaseAgent


class CRMAgent(BaseAgent):
    """
    Agent for CRM and client relationship management.

    Capabilities:
    - Manage client records
    - Track client interactions
    - Analyze client health
    - Handle client communications
    - Manage opportunities
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
        return "crm_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a CRM and client relationship expert.

Your role is to optimize client relationships:
1. Maintain accurate client records
2. Track all client interactions
3. Analyze client health and satisfaction
4. Identify growth opportunities
5. Manage client communications"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_client",
                "description": "Get client information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "include": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["client_id"],
                },
            },
            {
                "name": "update_client",
                "description": "Update client record.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "updates": {"type": "object"},
                    },
                    "required": ["client_id", "updates"],
                },
            },
            {
                "name": "log_interaction",
                "description": "Log client interaction.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "type": {"type": "string", "enum": ["call", "email", "meeting", "note"]},
                        "summary": {"type": "string"},
                        "participants": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["client_id", "type", "summary"],
                },
            },
            {
                "name": "get_client_health",
                "description": "Get client health score and analysis.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                    },
                    "required": ["client_id"],
                },
            },
            {
                "name": "get_opportunities",
                "description": "Get client opportunities.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["open", "won", "lost", "all"]},
                    },
                    "required": [],
                },
            },
            {
                "name": "create_opportunity",
                "description": "Create new opportunity.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "name": {"type": "string"},
                        "value": {"type": "number"},
                        "probability": {"type": "number"},
                    },
                    "required": ["client_id", "name"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "get_client":
                response = await self.http_client.get(f"/api/v1/crm/clients/{tool_input['client_id']}", params={"include": ",".join(tool_input.get("include", []))})
                return response.json() if response.status_code == 200 else {"error": "Client not found"}
            elif tool_name == "update_client":
                response = await self.http_client.patch(f"/api/v1/crm/clients/{tool_input['client_id']}", json=tool_input["updates"])
                return response.json() if response.status_code == 200 else {"error": "Failed to update"}
            elif tool_name == "log_interaction":
                response = await self.http_client.post(f"/api/v1/crm/clients/{tool_input['client_id']}/interactions", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to log"}
            elif tool_name == "get_client_health":
                response = await self.http_client.get(f"/api/v1/crm/clients/{tool_input['client_id']}/health")
                return response.json() if response.status_code == 200 else {"health": None}
            elif tool_name == "get_opportunities":
                params = {k: v for k, v in tool_input.items() if v}
                response = await self.http_client.get("/api/v1/crm/opportunities", params=params)
                return response.json() if response.status_code == 200 else {"opportunities": []}
            elif tool_name == "create_opportunity":
                response = await self.http_client.post("/api/v1/crm/opportunities", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
