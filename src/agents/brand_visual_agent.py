from typing import Any
import httpx
from .base import BaseAgent


class BrandVisualAgent(BaseAgent):
    """
    Agent for managing brand visual identity.

    Capabilities:
    - Manage visual assets and guidelines
    - Validate visual consistency
    - Generate visual recommendations
    - Manage color palettes and typography
    - Handle logo usage rules
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
        return "brand_visual_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a brand visual identity expert.

Your role is to manage and enforce visual brand standards:
1. Document visual guidelines (colors, typography, imagery)
2. Validate visual assets for brand compliance
3. Manage logo usage rules
4. Provide visual recommendations
5. Maintain visual asset library"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_visual_guidelines",
                "description": "Get brand visual guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "section": {"type": "string", "enum": ["colors", "typography", "logo", "imagery", "all"]},
                    },
                    "required": [],
                },
            },
            {
                "name": "validate_visual",
                "description": "Validate visual asset for brand compliance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string"},
                        "asset_url": {"type": "string"},
                        "check": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_color_palette",
                "description": "Get brand color palette.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "format": {"type": "string", "enum": ["hex", "rgb", "cmyk", "all"]},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_typography",
                "description": "Get brand typography specifications.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_logo_assets",
                "description": "Get logo assets and usage rules.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "variant": {"type": "string", "enum": ["primary", "secondary", "icon", "all"]},
                    },
                    "required": [],
                },
            },
            {
                "name": "save_visual_guidelines",
                "description": "Save visual guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "guidelines": {"type": "object"},
                    },
                    "required": ["guidelines"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id
            if tool_name == "get_visual_guidelines":
                response = await self.http_client.get(
                    "/api/v1/brand/visual",
                    params={"client_id": client_id, "section": tool_input.get("section", "all")},
                )
                return response.json() if response.status_code == 200 else {"guidelines": None}
            elif tool_name == "validate_visual":
                return {
                    "status": "ready_to_validate",
                    "asset_id": tool_input.get("asset_id"),
                    "instruction": "Validate visual asset against brand guidelines.",
                }
            elif tool_name == "get_color_palette":
                response = await self.http_client.get(f"/api/v1/brand/visual/colors", params={"client_id": client_id})
                return response.json() if response.status_code == 200 else {"colors": []}
            elif tool_name == "get_typography":
                response = await self.http_client.get(f"/api/v1/brand/visual/typography", params={"client_id": client_id})
                return response.json() if response.status_code == 200 else {"typography": None}
            elif tool_name == "get_logo_assets":
                response = await self.http_client.get(f"/api/v1/brand/visual/logos", params={"client_id": client_id})
                return response.json() if response.status_code == 200 else {"logos": []}
            elif tool_name == "save_visual_guidelines":
                response = await self.http_client.post("/api/v1/brand/visual", json={"client_id": client_id, **tool_input["guidelines"]})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to save"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
