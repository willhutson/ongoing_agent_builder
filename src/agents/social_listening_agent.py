from typing import Any
import httpx
from .base import BaseAgent


class SocialListeningAgent(BaseAgent):
    """
    Agent for social media listening and monitoring.

    Capabilities:
    - Monitor brand mentions
    - Track sentiment
    - Identify trends
    - Monitor competitors
    - Alert on issues
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
        return "social_listening_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a social listening and monitoring expert.

Your role is to track and analyze social conversations:
1. Monitor brand and product mentions
2. Analyze sentiment trends
3. Identify emerging topics
4. Track competitor activity
5. Alert on potential issues"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "setup_monitoring",
                "description": "Set up social monitoring.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "array", "items": {"type": "string"}},
                        "platforms": {"type": "array", "items": {"type": "string"}},
                        "languages": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["keywords"],
                },
            },
            {
                "name": "get_mentions",
                "description": "Get brand mentions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "date_range": {"type": "object"},
                        "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral", "all"]},
                        "platform": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_sentiment",
                "description": "Analyze sentiment trends.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "date_range": {"type": "object"},
                        "granularity": {"type": "string", "enum": ["hourly", "daily", "weekly"]},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_trending_topics",
                "description": "Get trending topics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "industry": {"type": "string"},
                        "region": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "monitor_competitors",
                "description": "Monitor competitor activity.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "competitors": {"type": "array", "items": {"type": "string"}},
                        "date_range": {"type": "object"},
                    },
                    "required": ["competitors"],
                },
            },
            {
                "name": "create_alert",
                "description": "Create monitoring alert.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "conditions": {"type": "object"},
                        "notify": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["name", "conditions"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id
            if tool_name == "setup_monitoring":
                response = await self.http_client.post("/api/v1/social/monitoring", json={**tool_input, "client_id": client_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to setup"}
            elif tool_name == "get_mentions":
                response = await self.http_client.get("/api/v1/social/mentions", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"mentions": []}
            elif tool_name == "analyze_sentiment":
                response = await self.http_client.get("/api/v1/social/sentiment", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"sentiment": None}
            elif tool_name == "get_trending_topics":
                response = await self.http_client.get("/api/v1/social/trends", params=tool_input)
                return response.json() if response.status_code == 200 else {"trends": []}
            elif tool_name == "monitor_competitors":
                response = await self.http_client.get("/api/v1/social/competitors", params=tool_input)
                return response.json() if response.status_code == 200 else {"competitors": []}
            elif tool_name == "create_alert":
                response = await self.http_client.post("/api/v1/social/alerts", json={**tool_input, "client_id": client_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
