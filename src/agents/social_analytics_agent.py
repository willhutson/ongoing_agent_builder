from typing import Any
import httpx
from .base import BaseAgent


class SocialAnalyticsAgent(BaseAgent):
    """
    Agent for social media analytics.

    Capabilities:
    - Track social performance metrics
    - Analyze audience demographics
    - Compare platform performance
    - Generate social reports
    - Benchmark against competitors
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
        return "social_analytics_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a social media analytics expert.

Your role is to analyze social performance:
1. Track key social metrics
2. Analyze audience insights
3. Compare platform performance
4. Identify content winners
5. Provide strategic recommendations"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_metrics",
                "description": "Get social media metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "platforms": {"type": "array", "items": {"type": "string"}},
                        "metrics": {"type": "array", "items": {"type": "string"}},
                        "date_range": {"type": "object"},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_audience_insights",
                "description": "Get audience demographics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "platform": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_top_content",
                "description": "Get top performing content.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "platform": {"type": "string"},
                        "metric": {"type": "string", "enum": ["engagement", "reach", "shares", "clicks"]},
                        "limit": {"type": "integer"},
                    },
                    "required": [],
                },
            },
            {
                "name": "compare_platforms",
                "description": "Compare performance across platforms.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "date_range": {"type": "object"},
                    },
                    "required": [],
                },
            },
            {
                "name": "generate_social_report",
                "description": "Generate social analytics report.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "date_range": {"type": "object"},
                        "include": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [],
                },
            },
            {
                "name": "benchmark_competitors",
                "description": "Benchmark against competitors.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "competitors": {"type": "array", "items": {"type": "string"}},
                        "metrics": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["competitors"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id
            if tool_name == "get_metrics":
                response = await self.http_client.get("/api/v1/social/analytics/metrics", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"metrics": {}}
            elif tool_name == "get_audience_insights":
                response = await self.http_client.get("/api/v1/social/analytics/audience", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"audience": None}
            elif tool_name == "get_top_content":
                response = await self.http_client.get("/api/v1/social/analytics/top-content", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"content": []}
            elif tool_name == "compare_platforms":
                response = await self.http_client.get("/api/v1/social/analytics/compare", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"comparison": None}
            elif tool_name == "generate_social_report":
                return {"status": "ready_to_generate", "instruction": "Generate comprehensive social analytics report."}
            elif tool_name == "benchmark_competitors":
                response = await self.http_client.get("/api/v1/social/analytics/benchmark", params=tool_input)
                return response.json() if response.status_code == 200 else {"benchmark": None}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
