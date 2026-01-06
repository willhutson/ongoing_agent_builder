from typing import Any
import httpx
from .base import BaseAgent


class BudgetAgent(BaseAgent):
    """Agent for budget management."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "budget_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a budget management expert. Track, manage, and optimize budgets."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "create_budget", "description": "Create project/campaign budget.", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}, "total": {"type": "number"}, "categories": {"type": "array", "items": {"type": "object"}}}, "required": ["name", "total"]}},
            {"name": "get_budget", "description": "Get budget details.", "input_schema": {"type": "object", "properties": {"budget_id": {"type": "string"}, "project_id": {"type": "string"}}, "required": []}},
            {"name": "track_spend", "description": "Track budget spend.", "input_schema": {"type": "object", "properties": {"budget_id": {"type": "string"}, "amount": {"type": "number"}, "category": {"type": "string"}}, "required": ["budget_id", "amount"]}},
            {"name": "get_variance", "description": "Get budget variance.", "input_schema": {"type": "object", "properties": {"budget_id": {"type": "string"}}, "required": ["budget_id"]}},
            {"name": "reallocate_budget", "description": "Reallocate budget between categories.", "input_schema": {"type": "object", "properties": {"budget_id": {"type": "string"}, "reallocations": {"type": "array", "items": {"type": "object"}}}, "required": ["budget_id", "reallocations"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "create_budget":
                response = await self.http_client.post("/api/v1/finance/budgets", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_budget":
                bid = tool_input.get("budget_id") or tool_input.get("project_id")
                response = await self.http_client.get(f"/api/v1/finance/budgets/{bid}" if tool_input.get("budget_id") else "/api/v1/finance/budgets", params=tool_input)
                return response.json() if response.status_code == 200 else {"budget": None}
            elif tool_name == "track_spend":
                response = await self.http_client.post(f"/api/v1/finance/budgets/{tool_input['budget_id']}/spend", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            elif tool_name == "get_variance":
                response = await self.http_client.get(f"/api/v1/finance/budgets/{tool_input['budget_id']}/variance")
                return response.json() if response.status_code == 200 else {"variance": None}
            elif tool_name == "reallocate_budget":
                response = await self.http_client.post(f"/api/v1/finance/budgets/{tool_input['budget_id']}/reallocate", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
