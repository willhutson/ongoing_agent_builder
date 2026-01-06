from typing import Any
import httpx
from .base import BaseAgent


class CampaignAnalyticsAgent(BaseAgent):
    """
    Agent for campaign analytics.

    Capabilities:
    - Track campaign KPIs
    - Analyze performance by channel
    - Calculate ROI/ROAS
    - Identify optimization opportunities
    - Generate campaign reports
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
        return "campaign_analytics_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a campaign analytics expert.

Your role is to measure and optimize campaigns:
1. Track campaign KPIs
2. Analyze performance by channel
3. Calculate ROI and ROAS
4. Identify optimization opportunities
5. Provide data-driven recommendations"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_campaign_kpis",
                "description": "Get campaign KPIs.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "kpis": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["campaign_id"],
                },
            },
            {
                "name": "analyze_by_channel",
                "description": "Analyze performance by channel.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "date_range": {"type": "object"},
                    },
                    "required": ["campaign_id"],
                },
            },
            {
                "name": "calculate_roi",
                "description": "Calculate ROI/ROAS.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "attribution_model": {"type": "string"},
                    },
                    "required": ["campaign_id"],
                },
            },
            {
                "name": "get_funnel_metrics",
                "description": "Get conversion funnel metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "funnel_stages": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["campaign_id"],
                },
            },
            {
                "name": "identify_optimizations",
                "description": "Identify optimization opportunities.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                    },
                    "required": ["campaign_id"],
                },
            },
            {
                "name": "generate_campaign_report",
                "description": "Generate campaign analytics report.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "include": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["campaign_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "get_campaign_kpis":
                response = await self.http_client.get(f"/api/v1/analytics/campaigns/{tool_input['campaign_id']}/kpis")
                return response.json() if response.status_code == 200 else {"kpis": {}}
            elif tool_name == "analyze_by_channel":
                response = await self.http_client.get(f"/api/v1/analytics/campaigns/{tool_input['campaign_id']}/channels")
                return response.json() if response.status_code == 200 else {"channels": []}
            elif tool_name == "calculate_roi":
                response = await self.http_client.get(f"/api/v1/analytics/campaigns/{tool_input['campaign_id']}/roi")
                return response.json() if response.status_code == 200 else {"roi": None}
            elif tool_name == "get_funnel_metrics":
                response = await self.http_client.get(f"/api/v1/analytics/campaigns/{tool_input['campaign_id']}/funnel")
                return response.json() if response.status_code == 200 else {"funnel": None}
            elif tool_name == "identify_optimizations":
                return {"status": "ready_to_analyze", "instruction": "Identify campaign optimization opportunities based on data."}
            elif tool_name == "generate_campaign_report":
                return {"status": "ready_to_generate", "instruction": "Generate comprehensive campaign analytics report."}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
