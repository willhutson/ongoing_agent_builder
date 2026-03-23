"""
Research Module Agents — Competitor, SocialListening, RFP, CampaignAnalytics, SocialAnalytics, Commercial.

Data ingestion and analysis. External API heavy.
"""

from typing import Any
from shared.base_agent import BaseAgent
from shared.openrouter import OpenRouterClient
from shared.config import BaseModuleSettings, get_model_id

from .observer_agent import ObserverAgent


class CompetitorAgent(BaseAgent):
    """Competitive landscape analysis."""

    @property
    def name(self) -> str:
        return "competitor"

    @property
    def system_prompt(self) -> str:
        return """You are a competitive intelligence analyst.

Analyze competitive landscapes:
- Competitor identification and profiling
- Positioning and messaging analysis
- Product/service comparisons
- Pricing strategy analysis
- Digital presence and content audit
- SWOT analysis and strategic gaps"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "analyze_competitor",
                "description": "Analyze a specific competitor.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "competitor_name": {"type": "string"},
                        "analysis_type": {"type": "string", "enum": ["full", "positioning", "digital", "pricing", "content"]},
                        "industry": {"type": "string"},
                    },
                    "required": ["competitor_name"],
                },
            },
            {
                "name": "competitive_landscape",
                "description": "Map the full competitive landscape.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "industry": {"type": "string"},
                        "our_brand": {"type": "string"},
                        "competitors": {"type": "array", "items": {"type": "string"}},
                        "dimensions": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["industry"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class SocialListeningAgent(BaseAgent):
    """Social media monitoring and sentiment analysis."""

    @property
    def name(self) -> str:
        return "social_listening"

    @property
    def system_prompt(self) -> str:
        return """You are a social media intelligence specialist.

Monitor and analyze social conversations:
- Brand mention tracking and sentiment
- Trend identification and emerging topics
- Influencer and community mapping
- Crisis detection and alerting
- Audience insight extraction"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "analyze_mentions",
                "description": "Analyze brand mentions and sentiment.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brand": {"type": "string"},
                        "platforms": {"type": "array", "items": {"type": "string"}},
                        "period": {"type": "string", "enum": ["day", "week", "month"]},
                        "sentiment_filter": {"type": "string", "enum": ["all", "positive", "negative", "neutral"]},
                    },
                    "required": ["brand"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class RFPAgent(BaseAgent):
    """RFP analysis and proposal evaluation."""

    @property
    def name(self) -> str:
        return "rfp"

    @property
    def system_prompt(self) -> str:
        return """You are an RFP analysis specialist.

Analyze and respond to RFPs:
- Extract requirements and evaluation criteria
- Identify compliance gaps
- Score fit and feasibility
- Draft response sections
- Competitive positioning for the proposal"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "analyze_rfp",
                "description": "Analyze an RFP document.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rfp_text": {"type": "string"},
                        "our_capabilities": {"type": "array", "items": {"type": "string"}},
                        "analysis_depth": {"type": "string", "enum": ["quick", "detailed", "full"]},
                    },
                    "required": ["rfp_text"],
                },
            },
            {
                "name": "draft_response",
                "description": "Draft an RFP response section.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "section": {"type": "string"},
                        "requirements": {"type": "array", "items": {"type": "string"}},
                        "our_approach": {"type": "string"},
                    },
                    "required": ["section", "requirements"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class CampaignAnalyticsAgent(BaseAgent):
    """Campaign performance measurement and attribution."""

    @property
    def name(self) -> str:
        return "campaign_analytics"

    @property
    def system_prompt(self) -> str:
        return """You are a campaign performance analyst.

Measure and optimize campaigns:
- KPI tracking and reporting
- Attribution modeling
- A/B test analysis
- Budget efficiency and ROAS
- Audience performance segmentation
- Recommendations for optimization"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "analyze_campaign",
                "description": "Analyze campaign performance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "metrics": {"type": "array", "items": {"type": "string"}},
                        "period": {"type": "string"},
                        "compare_to": {"type": "string", "description": "Benchmark or previous period"},
                    },
                    "required": ["campaign_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class SocialAnalyticsAgent(BaseAgent):
    """Social media analytics and engagement metrics."""

    @property
    def name(self) -> str:
        return "social_analytics"

    @property
    def system_prompt(self) -> str:
        return """You are a social media analytics expert.

Analyze social performance:
- Engagement rates and trends
- Content performance by type/format
- Audience growth and demographics
- Best posting times and frequency
- Platform-specific insights"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "analyze_social",
                "description": "Analyze social media performance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "platforms": {"type": "array", "items": {"type": "string"}},
                        "period": {"type": "string", "enum": ["week", "month", "quarter"]},
                        "metrics": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["platforms"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class CommercialAgent(BaseAgent):
    """Commercial strategy and pricing analysis."""

    @property
    def name(self) -> str:
        return "commercial"

    @property
    def system_prompt(self) -> str:
        return """You are a commercial strategy analyst.

Analyze commercial opportunities:
- Pricing strategy and competitive positioning
- Market sizing and opportunity assessment
- Revenue modeling and forecasting
- Go-to-market strategy
- Partnership and channel analysis"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "analyze_commercial",
                "description": "Commercial analysis and strategy.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "analysis_type": {"type": "string", "enum": ["pricing", "market_size", "revenue_model", "gtm", "partnership"]},
                        "data": {"type": "object"},
                    },
                    "required": ["topic", "analysis_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


def create_agents(llm: OpenRouterClient, settings: BaseModuleSettings) -> dict[str, BaseAgent]:
    model = get_model_id(settings, "standard")
    return {
        "competitor": CompetitorAgent(llm, model),
        "social_listening": SocialListeningAgent(llm, model),
        "rfp": RFPAgent(llm, model),
        "campaign_analytics": CampaignAnalyticsAgent(llm, model),
        "social_analytics": SocialAnalyticsAgent(llm, model),
        "commercial": CommercialAgent(llm, model),
        "observer": ObserverAgent(llm, model),
    }
