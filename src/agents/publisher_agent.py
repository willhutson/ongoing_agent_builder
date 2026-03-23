from typing import Any
import httpx
from .base import BaseAgent


class PublisherAgent(BaseAgent):
    """
    Agent for social media publishing orchestration.

    Capabilities:
    - Create and manage post drafts with platform-optimized content
    - Schedule posts for publishing across platforms
    - View and manage publishing calendars
    - AI-powered optimal posting time suggestions
    - Adapt content for multiple platforms
    - Track post performance analytics
    - Plan multi-post content series
    - Generate platform-specific captions with hashtags
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
        return "publisher_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a social media publishing specialist.

You help teams plan, schedule, and optimize their social media content across platforms.
You understand platform-specific best practices — Instagram carousels vs TikTok videos
vs X threads. You always consider the brand voice and audience when crafting content.

Your capabilities:
1. Create post drafts with platform-optimized content
2. Schedule posts at optimal times for maximum engagement
3. Manage publishing calendars across clients and platforms
4. Adapt a single piece of content for multiple platforms
5. Analyze post performance to inform future strategy
6. Plan multi-post content series (e.g., 5-day campaign rollouts)
7. Generate captions with strategic hashtag selection

Platform guidelines you follow:
- Instagram: Visual-first, 2200 char caption limit, 30 hashtag max, carousel for engagement
- TikTok: Trend-aware, short captions, trending sounds, hooks in first 3 seconds
- X/Twitter: 280 chars, thread strategy for long-form, timely engagement
- LinkedIn: Professional tone, 3000 char limit, thought leadership positioning
- Facebook: Community-focused, link posts for traffic, longer form acceptable"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_post_draft",
                "description": "Create a draft social media post with platform-optimized content. Emits a SOCIAL_POST artifact.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Post content/copy"},
                        "platforms": {"type": "array", "items": {"type": "string"}},
                        "client_id": {"type": "string"},
                        "content_type": {
                            "type": "string",
                            "enum": ["image", "video", "carousel", "text", "reel", "story"],
                        },
                        "media_urls": {"type": "array", "items": {"type": "string"}},
                        "hashtags": {"type": "array", "items": {"type": "string"}},
                        "campaign_id": {"type": "string"},
                    },
                    "required": ["content", "platforms", "client_id"],
                },
            },
            {
                "name": "schedule_post",
                "description": "Schedule a draft post for publishing at a specific time.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "post_id": {"type": "string", "description": "ID of the draft post"},
                        "scheduled_for": {"type": "string", "description": "ISO datetime for publishing"},
                        "platforms": {"type": "array", "items": {"type": "string"}},
                        "client_id": {"type": "string"},
                    },
                    "required": ["post_id", "scheduled_for", "client_id"],
                },
            },
            {
                "name": "get_publishing_calendar",
                "description": "View the publishing calendar for a client. Shows scheduled, published, and draft posts.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string"},
                                "end": {"type": "string"},
                            },
                        },
                        "platform": {"type": "string"},
                        "status": {"type": "string", "enum": ["draft", "scheduled", "published", "all"]},
                    },
                    "required": ["client_id"],
                },
            },
            {
                "name": "suggest_posting_times",
                "description": "AI-powered optimal posting time suggestions based on audience analytics and past performance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "platform": {"type": "string"},
                        "content_type": {
                            "type": "string",
                            "enum": ["image", "video", "carousel", "text", "reel", "story"],
                        },
                        "target_day": {"type": "string", "description": "Day of week or specific date"},
                        "count": {"type": "integer", "description": "Number of suggestions", "default": 3},
                    },
                    "required": ["client_id", "platform"],
                },
            },
            {
                "name": "adapt_for_platforms",
                "description": "Adapt a single piece of content for multiple platforms, respecting character limits, hashtag strategies, and format differences.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "original_content": {"type": "string"},
                        "source_platform": {"type": "string"},
                        "target_platforms": {"type": "array", "items": {"type": "string"}},
                        "brand_guidelines": {"type": "string"},
                        "client_id": {"type": "string"},
                    },
                    "required": ["original_content", "target_platforms"],
                },
            },
            {
                "name": "get_post_performance",
                "description": "Get analytics and performance metrics for published posts.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "post_id": {"type": "string", "description": "Specific post ID, or omit for recent posts"},
                        "period": {"type": "string", "enum": ["day", "week", "month"]},
                        "platform": {"type": "string"},
                        "sort_by": {"type": "string", "enum": ["engagement", "impressions", "clicks", "date"]},
                    },
                    "required": ["client_id"],
                },
            },
            {
                "name": "create_content_series",
                "description": "Plan a multi-post content series (e.g., a 5-day campaign rollout, weekly tips series).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "series_name": {"type": "string"},
                        "theme": {"type": "string", "description": "Overall theme/topic for the series"},
                        "post_count": {"type": "integer", "description": "Number of posts in the series"},
                        "platforms": {"type": "array", "items": {"type": "string"}},
                        "cadence": {
                            "type": "string",
                            "enum": ["daily", "every_other_day", "weekly", "biweekly"],
                        },
                        "start_date": {"type": "string", "description": "ISO date for first post"},
                        "campaign_id": {"type": "string"},
                    },
                    "required": ["client_id", "series_name", "theme", "post_count", "platforms"],
                },
            },
            {
                "name": "generate_captions",
                "description": "Generate platform-specific captions with strategic hashtags.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "What the post is about"},
                        "platforms": {"type": "array", "items": {"type": "string"}},
                        "client_id": {"type": "string"},
                        "tone": {
                            "type": "string",
                            "enum": ["professional", "casual", "playful", "inspirational", "educational"],
                        },
                        "include_hashtags": {"type": "boolean", "default": True},
                        "include_cta": {"type": "boolean", "default": True},
                        "max_hashtags": {"type": "integer", "default": 10},
                    },
                    "required": ["topic", "platforms", "client_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id

            if tool_name == "create_post_draft":
                response = await self.http_client.post(
                    "/api/v1/publishing/posts/draft",
                    json={
                        "content": tool_input["content"],
                        "platforms": tool_input["platforms"],
                        "client_id": client_id,
                        "content_type": tool_input.get("content_type", "text"),
                        "media_urls": tool_input.get("media_urls", []),
                        "hashtags": tool_input.get("hashtags", []),
                        "campaign_id": tool_input.get("campaign_id"),
                    },
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create draft"}

            elif tool_name == "schedule_post":
                response = await self.http_client.post(
                    f"/api/v1/publishing/posts/{tool_input['post_id']}/schedule",
                    json={
                        "scheduled_for": tool_input["scheduled_for"],
                        "platforms": tool_input.get("platforms", []),
                        "client_id": client_id,
                    },
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to schedule post"}

            elif tool_name == "get_publishing_calendar":
                params = {"client_id": client_id, "status": tool_input.get("status", "all")}
                if tool_input.get("platform"):
                    params["platform"] = tool_input["platform"]
                date_range = tool_input.get("date_range", {})
                if date_range.get("start"):
                    params["start"] = date_range["start"]
                if date_range.get("end"):
                    params["end"] = date_range["end"]
                response = await self.http_client.get(
                    "/api/v1/publishing/calendar", params=params,
                )
                return response.json() if response.status_code == 200 else {"posts": [], "total": 0}

            elif tool_name == "suggest_posting_times":
                response = await self.http_client.get(
                    "/api/v1/publishing/optimal-times",
                    params={
                        "client_id": client_id,
                        "platform": tool_input["platform"],
                        "content_type": tool_input.get("content_type"),
                        "target_day": tool_input.get("target_day"),
                        "count": tool_input.get("count", 3),
                    },
                )
                return response.json() if response.status_code == 200 else {"suggestions": [], "note": "No data available"}

            elif tool_name == "adapt_for_platforms":
                # LLM-based adaptation — return structured prompt for agent loop
                return {
                    "original_content": tool_input["original_content"],
                    "source_platform": tool_input.get("source_platform", "generic"),
                    "target_platforms": tool_input["target_platforms"],
                    "brand_guidelines": tool_input.get("brand_guidelines", ""),
                    "instruction": (
                        "Adapt the original content for each target platform. "
                        "Consider: character limits (X: 280, LinkedIn: 3000, Instagram: 2200), "
                        "hashtag best practices, format differences, and audience tone. "
                        "Return a dict of platform -> {content, hashtags, notes}."
                    ),
                }

            elif tool_name == "get_post_performance":
                params = {"client_id": client_id}
                if tool_input.get("post_id"):
                    params["post_id"] = tool_input["post_id"]
                if tool_input.get("period"):
                    params["period"] = tool_input["period"]
                if tool_input.get("platform"):
                    params["platform"] = tool_input["platform"]
                if tool_input.get("sort_by"):
                    params["sort_by"] = tool_input["sort_by"]
                response = await self.http_client.get(
                    "/api/v1/publishing/posts/performance", params=params,
                )
                return response.json() if response.status_code == 200 else {"posts": [], "summary": {}}

            elif tool_name == "create_content_series":
                response = await self.http_client.post(
                    "/api/v1/publishing/series",
                    json={
                        "client_id": client_id,
                        "series_name": tool_input["series_name"],
                        "theme": tool_input["theme"],
                        "post_count": tool_input["post_count"],
                        "platforms": tool_input["platforms"],
                        "cadence": tool_input.get("cadence", "daily"),
                        "start_date": tool_input.get("start_date"),
                        "campaign_id": tool_input.get("campaign_id"),
                    },
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create series"}

            elif tool_name == "generate_captions":
                # LLM-based caption generation — return structured prompt
                return {
                    "topic": tool_input["topic"],
                    "platforms": tool_input["platforms"],
                    "tone": tool_input.get("tone", "professional"),
                    "include_hashtags": tool_input.get("include_hashtags", True),
                    "include_cta": tool_input.get("include_cta", True),
                    "max_hashtags": tool_input.get("max_hashtags", 10),
                    "instruction": (
                        "Generate platform-specific captions for the given topic. "
                        "For each platform, provide: caption text, hashtags (if requested), "
                        "and a call-to-action (if requested). Match the requested tone. "
                        "Respect platform character limits and hashtag best practices."
                    ),
                }

            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        """Cleanup resources."""
        await self.http_client.aclose()
