from typing import Any
import httpx
from .base import BaseAgent


class KnowledgeAgent(BaseAgent):
    """Agent for knowledge management."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "knowledge_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a knowledge management expert. Organize and retrieve organizational knowledge."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "search_knowledge", "description": "Search knowledge base.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "categories": {"type": "array", "items": {"type": "string"}}}, "required": ["query"]}},
            {"name": "add_article", "description": "Add knowledge article.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "category": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}}, "required": ["title", "content"]}},
            {"name": "get_best_practices", "description": "Get best practices.", "input_schema": {"type": "object", "properties": {"topic": {"type": "string"}, "industry": {"type": "string"}}, "required": ["topic"]}},
            {"name": "get_templates", "description": "Get templates.", "input_schema": {"type": "object", "properties": {"template_type": {"type": "string"}}, "required": ["template_type"]}},
            {"name": "suggest_resources", "description": "Suggest relevant resources.", "input_schema": {"type": "object", "properties": {"context": {"type": "string"}}, "required": ["context"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "search_knowledge":
                response = await self.http_client.get("/api/v1/knowledge/search", params=tool_input)
                return response.json() if response.status_code == 200 else {"results": []}
            elif tool_name == "add_article":
                response = await self.http_client.post("/api/v1/knowledge/articles", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_best_practices":
                response = await self.http_client.get("/api/v1/knowledge/best-practices", params=tool_input)
                return response.json() if response.status_code == 200 else {"practices": []}
            elif tool_name == "get_templates":
                response = await self.http_client.get("/api/v1/knowledge/templates", params=tool_input)
                return response.json() if response.status_code == 200 else {"templates": []}
            elif tool_name == "suggest_resources":
                return {"status": "ready_to_suggest", "instruction": "Suggest relevant resources based on context."}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
