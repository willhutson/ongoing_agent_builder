"""
Observer Agent — Obsei-inspired Source → Analyze → Route pipeline.

Collects unstructured data from external platforms (Twitter, Reddit, App Store,
Google Reviews, news), runs LLM-based sentiment/classification analysis via
OpenRouter, and routes structured insights to other research agents.

This agent is the shared data ingestion backbone for:
- social_listening (brand mentions + sentiment)
- social_analytics (engagement metrics)
- competitor (digital presence audits)
- brand_performance (brand health across channels)
"""

from typing import Any
from shared.base_agent import BaseAgent
from shared.openrouter import OpenRouterClient

from .source_config import SourceConfig
from .source_adapters import (
    MentionBatch,
    collect_twitter,
    collect_reddit,
    collect_app_store,
    collect_google_reviews,
    collect_news,
    collect_website,
)


class ObserverAgent(BaseAgent):
    """
    Source → Analyze → Route agent.

    Collects normalized data from external platforms, analyzes it with
    Claude via OpenRouter, and routes structured insights to consumer agents.
    """

    @property
    def name(self) -> str:
        return "observer"

    @property
    def system_prompt(self) -> str:
        return """You are a data collection and analysis specialist.

You operate a Source → Analyze → Route pipeline:
1. COLLECT: Gather mentions, reviews, and content from external platforms
2. ANALYZE: Run sentiment analysis, topic classification, and trend detection
3. ROUTE: Structure insights for downstream agents (social_listening, brand_performance, competitor, social_analytics)

When analyzing collected data:
- Classify sentiment as positive, negative, neutral, or mixed
- Identify key themes and recurring topics
- Flag potential crises (high-volume negative sentiment spikes)
- Score overall brand health on a 0-100 scale
- Compare against competitors when data is available

Always indicate whether data is from live APIs or mock sources."""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "collect_mentions",
                "description": "Collect brand/keyword mentions from one or more platforms. Returns normalized mention objects.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brand": {"type": "string", "description": "Brand or keyword to search for"},
                        "sources": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["twitter", "reddit", "news", "google_reviews"]},
                            "description": "Platforms to collect from",
                        },
                        "period": {"type": "string", "enum": ["day", "week", "month", "quarter"], "default": "week"},
                        "keywords": {
                            "type": "array", "items": {"type": "string"},
                            "description": "Additional keywords to filter by",
                        },
                    },
                    "required": ["brand", "sources"],
                },
            },
            {
                "name": "analyze_sentiment",
                "description": "Run sentiment and topic analysis on a batch of collected texts. Uses Claude for analysis.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "texts": {
                            "type": "array", "items": {"type": "string"},
                            "description": "Texts to analyze",
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["sentiment", "classification", "topics"],
                            "default": "sentiment",
                        },
                        "brand": {"type": "string", "description": "Brand context for analysis"},
                    },
                    "required": ["texts"],
                },
            },
            {
                "name": "collect_reviews",
                "description": "Collect app or product reviews from app stores.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "app_id": {"type": "string", "description": "App ID or name"},
                        "platform": {"type": "string", "enum": ["ios", "android", "google_maps"]},
                        "period": {"type": "string", "enum": ["day", "week", "month", "quarter"], "default": "week"},
                    },
                    "required": ["app_id", "platform"],
                },
            },
            {
                "name": "collect_competitor_content",
                "description": "Collect competitor digital presence data from websites, social, news, and reviews.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "competitor_name": {"type": "string"},
                        "sources": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["website", "social", "news", "reviews"]},
                            "description": "Data sources to check",
                        },
                        "website_url": {"type": "string", "description": "Competitor website URL (for website source)"},
                    },
                    "required": ["competitor_name"],
                },
            },
            {
                "name": "route_insights",
                "description": "Structure and route analyzed data for a target agent.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target_agent": {
                            "type": "string",
                            "enum": ["social_listening", "social_analytics", "competitor", "brand_performance"],
                        },
                        "insights": {"type": "object", "description": "The analyzed data to route"},
                        "summary": {"type": "string", "description": "Brief summary of what was found"},
                    },
                    "required": ["target_agent", "insights"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "collect_mentions":
            return await self._collect_mentions(tool_input)
        elif tool_name == "analyze_sentiment":
            return await self._analyze_sentiment(tool_input)
        elif tool_name == "collect_reviews":
            return await self._collect_reviews(tool_input)
        elif tool_name == "collect_competitor_content":
            return await self._collect_competitor_content(tool_input)
        elif tool_name == "route_insights":
            return await self._route_insights(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    # ── Tool implementations ─────────────────────────────────────────────

    async def _collect_mentions(self, tool_input: dict) -> dict:
        """Collect from multiple sources, merge into unified batch."""
        brand = tool_input["brand"]
        sources = tool_input.get("sources", ["twitter"])
        period = tool_input.get("period", "week")

        all_mentions = []
        source_results = []

        for source in sources:
            batch = await self._collect_from_source(source, brand, period)
            all_mentions.extend(batch.mentions)
            source_results.append({
                "source": source,
                "count": len(batch.mentions),
                "mock": batch.mock,
            })

        return {
            "brand": brand,
            "total_mentions": len(all_mentions),
            "mentions": [m.to_dict() for m in all_mentions],
            "sources": source_results,
            "period": period,
        }

    async def _collect_from_source(
        self, source: str, brand: str, period: str
    ) -> MentionBatch:
        """Dispatch to the appropriate source adapter."""
        if source == "twitter":
            return await collect_twitter(brand, period)
        elif source == "reddit":
            return await collect_reddit(brand, period=period)
        elif source == "news":
            return await collect_news(brand, period)
        elif source == "google_reviews":
            return await collect_google_reviews(brand, period)
        # Fallback — empty batch
        return MentionBatch(
            mentions=[], source=source, query=brand,
            collected_at="", mock=True,
        )

    async def _analyze_sentiment(self, tool_input: dict) -> dict:
        """
        Analyze sentiment on collected texts.

        This is where we diverge from Obsei: instead of HuggingFace models,
        we use Claude via OpenRouter for higher-quality analysis.
        The LLM call happens naturally in the agent loop — the tool returns
        the texts in a structured format for the LLM to analyze in its response.
        """
        texts = tool_input.get("texts", [])
        analysis_type = tool_input.get("analysis_type", "sentiment")
        brand = tool_input.get("brand", "")

        return {
            "analysis_type": analysis_type,
            "brand": brand,
            "text_count": len(texts),
            "texts": texts[:20],  # cap to avoid token overflow
            "instruction": (
                f"Analyze the following {len(texts)} texts for {analysis_type}. "
                f"{'For brand: ' + brand + '. ' if brand else ''}"
                "Return a structured summary with per-text scores and overall trends."
            ),
        }

    async def _collect_reviews(self, tool_input: dict) -> dict:
        """Collect app/product reviews."""
        app_id = tool_input["app_id"]
        platform = tool_input.get("platform", "ios")
        period = tool_input.get("period", "week")

        if platform == "google_maps":
            batch = await collect_google_reviews(app_id, period)
        else:
            batch = await collect_app_store(app_id, platform, period)

        return batch.to_dict()

    async def _collect_competitor_content(self, tool_input: dict) -> dict:
        """Collect competitor data from multiple source types."""
        competitor = tool_input["competitor_name"]
        sources = tool_input.get("sources", ["news", "social"])
        website_url = tool_input.get("website_url")

        results = {}

        for source in sources:
            if source == "website" and website_url:
                batch = await collect_website(website_url)
                results["website"] = batch.to_dict()
            elif source == "social":
                twitter_batch = await collect_twitter(competitor)
                reddit_batch = await collect_reddit(competitor)
                results["social"] = {
                    "twitter": twitter_batch.to_dict(),
                    "reddit": reddit_batch.to_dict(),
                }
            elif source == "news":
                batch = await collect_news(competitor)
                results["news"] = batch.to_dict()
            elif source == "reviews":
                batch = await collect_google_reviews(competitor)
                results["reviews"] = batch.to_dict()

        return {
            "competitor": competitor,
            "sources_collected": list(results.keys()),
            "data": results,
        }

    async def _route_insights(self, tool_input: dict) -> dict:
        """
        Route analyzed data to a target agent.

        In the current architecture, this structures the data for handoff.
        Future: direct inter-agent delegation via Mission Control.
        """
        target = tool_input["target_agent"]
        insights = tool_input.get("insights", {})
        summary = tool_input.get("summary", "")

        return {
            "status": "routed",
            "target_agent": target,
            "payload_keys": list(insights.keys()),
            "summary": summary,
            "insights": insights,
        }
