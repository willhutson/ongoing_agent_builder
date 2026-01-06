from typing import Any
import httpx
from .base import BaseAgent


class ResourceAgent(BaseAgent):
    """
    Agent for resource management and allocation.

    Capabilities:
    - Track resource availability
    - Allocate resources to projects
    - Forecast resource needs
    - Manage skills and capacity
    - Handle resource conflicts
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
        return "resource_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a resource management expert.

Your role is to optimize resource allocation:
1. Track availability and capacity
2. Match skills to project needs
3. Forecast resource requirements
4. Resolve allocation conflicts
5. Optimize utilization"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_availability",
                "description": "Get resource availability.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resource_ids": {"type": "array", "items": {"type": "string"}},
                        "date_range": {"type": "object"},
                        "skills": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [],
                },
            },
            {
                "name": "allocate_resource",
                "description": "Allocate resource to project.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resource_id": {"type": "string"},
                        "project_id": {"type": "string"},
                        "allocation_percent": {"type": "integer"},
                        "date_range": {"type": "object"},
                    },
                    "required": ["resource_id", "project_id"],
                },
            },
            {
                "name": "forecast_needs",
                "description": "Forecast resource needs.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "brief_id": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "find_resources",
                "description": "Find resources by skills.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "skills": {"type": "array", "items": {"type": "string"}},
                        "availability_required": {"type": "object"},
                    },
                    "required": ["skills"],
                },
            },
            {
                "name": "get_utilization",
                "description": "Get utilization report.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resource_ids": {"type": "array", "items": {"type": "string"}},
                        "date_range": {"type": "object"},
                    },
                    "required": [],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "get_availability":
                response = await self.http_client.get("/api/v1/resources/availability", params=tool_input)
                return response.json() if response.status_code == 200 else {"availability": []}
            elif tool_name == "allocate_resource":
                response = await self.http_client.post("/api/v1/resources/allocations", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to allocate"}
            elif tool_name == "forecast_needs":
                return {"status": "ready_to_forecast", "instruction": "Forecast resource needs based on project/brief requirements."}
            elif tool_name == "find_resources":
                response = await self.http_client.get("/api/v1/resources/search", params={"skills": ",".join(tool_input["skills"])})
                return response.json() if response.status_code == 200 else {"resources": []}
            elif tool_name == "get_utilization":
                response = await self.http_client.get("/api/v1/resources/utilization", params=tool_input)
                return response.json() if response.status_code == 200 else {"utilization": []}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
