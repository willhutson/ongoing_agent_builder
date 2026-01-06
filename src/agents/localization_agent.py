from typing import Any
import httpx
from .base import BaseAgent


class LocalizationAgent(BaseAgent):
    """Agent for localization and multi-market adaptation."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, target_markets: list = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.target_markets = target_markets or []
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "localization_agent"

    @property
    def system_prompt(self) -> str:
        prompt = """You are a localization expert. Adapt content for different markets and cultures."""
        if self.target_markets:
            prompt += f"\n\nTarget markets: {', '.join(self.target_markets)}"
        return prompt

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "translate_content", "description": "Translate content.", "input_schema": {"type": "object", "properties": {"content": {"type": "string"}, "source_lang": {"type": "string"}, "target_lang": {"type": "string"}, "adapt_cultural": {"type": "boolean"}}, "required": ["content", "target_lang"]}},
            {"name": "adapt_for_market", "description": "Adapt content for market.", "input_schema": {"type": "object", "properties": {"content_id": {"type": "string"}, "target_market": {"type": "string"}, "adaptations": {"type": "array", "items": {"type": "string"}}}, "required": ["content_id", "target_market"]}},
            {"name": "get_market_requirements", "description": "Get market requirements.", "input_schema": {"type": "object", "properties": {"market": {"type": "string"}, "content_type": {"type": "string"}}, "required": ["market"]}},
            {"name": "validate_localization", "description": "Validate localized content.", "input_schema": {"type": "object", "properties": {"content_id": {"type": "string"}, "market": {"type": "string"}}, "required": ["content_id", "market"]}},
            {"name": "manage_translation_memory", "description": "Manage translation memory.", "input_schema": {"type": "object", "properties": {"action": {"type": "string", "enum": ["add", "search", "export"]}}, "required": ["action"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "translate_content":
                return {"status": "ready_to_translate", "content": tool_input["content"], "target_lang": tool_input["target_lang"], "instruction": "Translate with cultural adaptation."}
            elif tool_name == "adapt_for_market":
                return {"status": "ready_to_adapt", "instruction": "Adapt content for target market requirements."}
            elif tool_name == "get_market_requirements":
                response = await self.http_client.get(f"/api/v1/localization/markets/{tool_input['market']}/requirements")
                return response.json() if response.status_code == 200 else {"requirements": []}
            elif tool_name == "validate_localization":
                return {"status": "ready_to_validate", "instruction": "Validate localized content against market standards."}
            elif tool_name == "manage_translation_memory":
                response = await self.http_client.get("/api/v1/localization/translation-memory", params=tool_input)
                return response.json() if response.status_code == 200 else {"memory": None}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
