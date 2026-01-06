from typing import Any
import httpx
from .base import BaseAgent


class BrandGuidelinesAgent(BaseAgent):
    """
    Agent for comprehensive brand guidelines management.

    Capabilities:
    - Create and maintain brand books
    - Generate guidelines documents
    - Manage brand assets
    - Ensure brand consistency
    - Train teams on brand standards
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
        return "brand_guidelines_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a brand guidelines expert.

Your role is to create and maintain comprehensive brand guidelines:
1. Compile brand books from voice + visual guidelines
2. Create channel-specific guidelines
3. Generate training materials
4. Audit brand consistency
5. Manage brand asset libraries"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_brand_book",
                "description": "Get complete brand book.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "sections": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [],
                },
            },
            {
                "name": "generate_brand_book",
                "description": "Generate brand book from components.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "include": {"type": "array", "items": {"type": "string"}},
                        "format": {"type": "string", "enum": ["pdf", "web", "presentation"]},
                    },
                    "required": [],
                },
            },
            {
                "name": "audit_brand_consistency",
                "description": "Audit assets for brand consistency.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "asset_ids": {"type": "array", "items": {"type": "string"}},
                        "project_id": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_channel_guidelines",
                "description": "Get channel-specific guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "channel": {"type": "string"},
                    },
                    "required": ["channel"],
                },
            },
            {
                "name": "save_brand_book",
                "description": "Save brand book.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "content": {"type": "object"},
                        "version": {"type": "string"},
                    },
                    "required": ["content"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id
            if tool_name == "get_brand_book":
                response = await self.http_client.get("/api/v1/brand/book", params={"client_id": client_id})
                return response.json() if response.status_code == 200 else {"brand_book": None}
            elif tool_name == "generate_brand_book":
                return {
                    "status": "ready_to_generate",
                    "client_id": client_id,
                    "format": tool_input.get("format", "pdf"),
                    "instruction": "Generate comprehensive brand book with all guidelines.",
                }
            elif tool_name == "audit_brand_consistency":
                return {
                    "status": "ready_to_audit",
                    "asset_ids": tool_input.get("asset_ids"),
                    "instruction": "Audit assets for brand consistency and provide report.",
                }
            elif tool_name == "get_channel_guidelines":
                response = await self.http_client.get(
                    f"/api/v1/brand/guidelines/channels/{tool_input['channel']}",
                    params={"client_id": client_id},
                )
                return response.json() if response.status_code == 200 else {"guidelines": None}
            elif tool_name == "save_brand_book":
                response = await self.http_client.post("/api/v1/brand/book", json={"client_id": client_id, **tool_input})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to save"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
