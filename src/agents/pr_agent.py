from typing import Any
import httpx
from .base import BaseAgent


class PRAgent(BaseAgent):
    """Agent for public relations and media relations."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, client_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "pr_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a PR and media relations expert. Manage press releases, media outreach, and coverage."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "create_press_release", "description": "Create press release.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "embargo_date": {"type": "string"}}, "required": ["title", "content"]}},
            {"name": "get_media_list", "description": "Get media contacts list.", "input_schema": {"type": "object", "properties": {"beat": {"type": "string"}, "region": {"type": "string"}}, "required": []}},
            {"name": "distribute_release", "description": "Distribute press release.", "input_schema": {"type": "object", "properties": {"release_id": {"type": "string"}, "media_list_id": {"type": "string"}}, "required": ["release_id"]}},
            {"name": "track_coverage", "description": "Track media coverage.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "date_range": {"type": "object"}}, "required": []}},
            {"name": "calculate_avr", "description": "Calculate advertising value equivalent.", "input_schema": {"type": "object", "properties": {"coverage_ids": {"type": "array", "items": {"type": "string"}}}, "required": ["coverage_ids"]}},
            {"name": "create_media_kit", "description": "Create media kit.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "include": {"type": "array", "items": {"type": "string"}}}, "required": []}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id
            if tool_name == "create_press_release":
                response = await self.http_client.post("/api/v1/pr/releases", json={**tool_input, "client_id": client_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_media_list":
                response = await self.http_client.get("/api/v1/pr/media-lists", params=tool_input)
                return response.json() if response.status_code == 200 else {"contacts": []}
            elif tool_name == "distribute_release":
                response = await self.http_client.post(f"/api/v1/pr/releases/{tool_input['release_id']}/distribute", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            elif tool_name == "track_coverage":
                response = await self.http_client.get("/api/v1/pr/coverage", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"coverage": []}
            elif tool_name == "calculate_avr":
                response = await self.http_client.post("/api/v1/pr/coverage/avr", json=tool_input)
                return response.json() if response.status_code == 200 else {"avr": None}
            elif tool_name == "create_media_kit":
                return {"status": "ready_to_create", "instruction": "Create comprehensive media kit."}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
