from typing import Any
import httpx
from .base import BaseAgent


class TrainingAgent(BaseAgent):
    """Agent for training and learning."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "training_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a training and learning expert. Create and manage training content."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "create_training", "description": "Create training module.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "object"}, "type": {"type": "string"}}, "required": ["title"]}},
            {"name": "assign_training", "description": "Assign training to users.", "input_schema": {"type": "object", "properties": {"training_id": {"type": "string"}, "user_ids": {"type": "array", "items": {"type": "string"}}}, "required": ["training_id", "user_ids"]}},
            {"name": "track_progress", "description": "Track training progress.", "input_schema": {"type": "object", "properties": {"user_id": {"type": "string"}, "training_id": {"type": "string"}}, "required": []}},
            {"name": "create_quiz", "description": "Create training quiz.", "input_schema": {"type": "object", "properties": {"training_id": {"type": "string"}, "questions": {"type": "array", "items": {"type": "object"}}}, "required": ["training_id", "questions"]}},
            {"name": "get_certifications", "description": "Get user certifications.", "input_schema": {"type": "object", "properties": {"user_id": {"type": "string"}}, "required": ["user_id"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "create_training":
                response = await self.http_client.post("/api/v1/training/modules", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "assign_training":
                response = await self.http_client.post(f"/api/v1/training/modules/{tool_input['training_id']}/assign", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            elif tool_name == "track_progress":
                response = await self.http_client.get("/api/v1/training/progress", params=tool_input)
                return response.json() if response.status_code == 200 else {"progress": None}
            elif tool_name == "create_quiz":
                response = await self.http_client.post(f"/api/v1/training/modules/{tool_input['training_id']}/quiz", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_certifications":
                response = await self.http_client.get(f"/api/v1/training/users/{tool_input['user_id']}/certifications")
                return response.json() if response.status_code == 200 else {"certifications": []}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
