"""
Brand Module Agents — Voice, Visual, Guidelines, Performance.

Brand identity system. Shared brand state across all work.
"""

from typing import Any
from shared.base_agent import BaseAgent
from shared.openrouter import OpenRouterClient
from shared.config import BaseModuleSettings, get_model_id


class BrandVoiceAgent(BaseAgent):
    """Brand voice, tone, and messaging personality."""

    @property
    def name(self) -> str:
        return "brand_voice"

    @property
    def system_prompt(self) -> str:
        return """You are a brand voice and tone specialist.

Define and maintain brand voice:
- Voice attributes (warm, authoritative, playful, etc.)
- Tone variations by context (social, formal, crisis)
- Vocabulary and language guidelines
- Do's and don'ts for brand communication
- Voice consistency scoring across content"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "define_voice",
                "description": "Define brand voice attributes and guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brand_name": {"type": "string"},
                        "industry": {"type": "string"},
                        "target_audience": {"type": "string"},
                        "personality_traits": {"type": "array", "items": {"type": "string"}},
                        "competitors": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["brand_name"],
                },
            },
            {
                "name": "score_voice_consistency",
                "description": "Score content against brand voice guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "voice_guidelines": {"type": "string"},
                    },
                    "required": ["content"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class BrandVisualAgent(BaseAgent):
    """Visual identity and design guidelines."""

    @property
    def name(self) -> str:
        return "brand_visual"

    @property
    def system_prompt(self) -> str:
        return """You are a visual identity specialist.

Define and enforce visual brand standards:
- Color palettes (primary, secondary, accent)
- Typography systems and hierarchy
- Logo usage rules and clear space
- Photography and illustration style
- Layout grids and spacing systems
- Icon and graphic element standards"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_visual_identity",
                "description": "Create visual identity guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brand_name": {"type": "string"},
                        "industry": {"type": "string"},
                        "mood": {"type": "array", "items": {"type": "string"}},
                        "existing_colors": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["brand_name"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class BrandGuidelinesAgent(BaseAgent):
    """Comprehensive brand standards documentation."""

    @property
    def name(self) -> str:
        return "brand_guidelines"

    @property
    def system_prompt(self) -> str:
        return """You are a brand standards documentation expert.

Create comprehensive brand guidelines covering:
- Mission, vision, and values
- Voice and tone (in coordination with BrandVoice)
- Visual identity (in coordination with BrandVisual)
- Application examples across touchpoints
- Do's and don'ts with visual examples
- Template specifications"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_guidelines",
                "description": "Generate brand guidelines document.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brand_name": {"type": "string"},
                        "sections": {"type": "array", "items": {"type": "string"}},
                        "format": {"type": "string", "enum": ["full", "quick_reference", "social_only"]},
                    },
                    "required": ["brand_name"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class BrandPerformanceAgent(BaseAgent):
    """Brand health metrics and KPI tracking."""

    @property
    def name(self) -> str:
        return "brand_performance"

    @property
    def system_prompt(self) -> str:
        return """You are a brand performance analyst.

Track and analyze brand health:
- Brand awareness and recognition metrics
- Sentiment analysis across channels
- Share of voice vs competitors
- Brand equity scoring
- Consistency audits across touchpoints
- Recommendation and loyalty metrics"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "analyze_brand_health",
                "description": "Analyze brand health metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brand_name": {"type": "string"},
                        "metrics": {"type": "array", "items": {"type": "string"}},
                        "period": {"type": "string", "enum": ["week", "month", "quarter", "year"]},
                        "competitors": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["brand_name"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


def create_agents(llm: OpenRouterClient, settings: BaseModuleSettings) -> dict[str, BaseAgent]:
    model = get_model_id(settings, "standard")
    return {
        "brand_voice": BrandVoiceAgent(llm, model),
        "brand_visual": BrandVisualAgent(llm, model),
        "brand_guidelines": BrandGuidelinesAgent(llm, model),
        "brand_performance": BrandPerformanceAgent(llm, model),
    }
