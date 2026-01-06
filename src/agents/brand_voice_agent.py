from typing import Any
import httpx
from .base import BaseAgent


class BrandVoiceAgent(BaseAgent):
    """
    Agent for managing brand voice and tone.

    Capabilities:
    - Define and document brand voice
    - Analyze content for voice consistency
    - Generate voice guidelines
    - Adapt voice for different channels
    - Train on brand examples
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
        return "brand_voice_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a brand voice and tone expert.

Your role is to define, maintain, and enforce brand voice:
1. Document brand voice attributes
2. Create voice guidelines for different channels
3. Analyze content for voice consistency
4. Provide voice recommendations
5. Train teams on brand voice

Voice dimensions you work with:
- Personality traits (friendly, professional, bold, etc.)
- Tone variations (formal/casual, serious/playful)
- Language patterns (vocabulary, sentence structure)
- Channel adaptations (social vs corporate)
- Audience adaptations (B2B vs B2C)"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_voice_guidelines",
                "description": "Retrieve brand voice guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "channel": {"type": "string", "enum": ["social", "corporate", "advertising", "internal"]},
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_voice_consistency",
                "description": "Analyze content for voice consistency.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to analyze"},
                        "client_id": {"type": "string"},
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "generate_voice_guidelines",
                "description": "Generate voice guidelines from examples.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "examples": {"type": "array", "items": {"type": "string"}},
                        "brand_attributes": {"type": "array", "items": {"type": "string"}},
                        "target_audience": {"type": "string"},
                    },
                    "required": ["examples"],
                },
            },
            {
                "name": "adapt_voice",
                "description": "Adapt content to brand voice.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "target_channel": {"type": "string"},
                        "client_id": {"type": "string"},
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "save_guidelines",
                "description": "Save voice guidelines.",
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
            if tool_name == "get_voice_guidelines":
                response = await self.http_client.get(
                    "/api/v1/brand/voice",
                    params={"client_id": tool_input.get("client_id") or self.client_specific_id},
                )
                return response.json() if response.status_code == 200 else {"guidelines": None}
            elif tool_name == "analyze_voice_consistency":
                return {
                    "status": "ready_to_analyze",
                    "content": tool_input["content"],
                    "instruction": "Analyze content for brand voice consistency and provide score.",
                }
            elif tool_name == "generate_voice_guidelines":
                return {
                    "status": "ready_to_generate",
                    "examples": tool_input["examples"],
                    "instruction": "Generate comprehensive voice guidelines from examples.",
                }
            elif tool_name == "adapt_voice":
                return {
                    "status": "ready_to_adapt",
                    "content": tool_input["content"],
                    "instruction": "Adapt content to match brand voice guidelines.",
                }
            elif tool_name == "save_guidelines":
                response = await self.http_client.post(
                    "/api/v1/brand/voice",
                    json={"client_id": tool_input.get("client_id") or self.client_specific_id, **tool_input["guidelines"]},
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to save"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
