from typing import Any
import httpx
from .base import BaseAgent


class CompetitorAgent(BaseAgent):
    """
    Agent for competitor analysis.

    Capabilities:
    - Track competitor activity
    - Analyze competitor strategies
    - Compare market positioning
    - Monitor competitive landscape
    - Generate competitive reports
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
        return "competitor_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a competitive intelligence expert.

Your role is to track and analyze competition:
1. Monitor competitor activities
2. Analyze competitive strategies
3. Compare market positioning
4. Identify competitive threats
5. Provide strategic recommendations"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "add_competitor",
                "description": "Add competitor to track.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "competitor_name": {"type": "string"},
                        "competitor_url": {"type": "string"},
                        "social_handles": {"type": "object"},
                    },
                    "required": ["competitor_name"],
                },
            },
            {
                "name": "get_competitor_activity",
                "description": "Get competitor activity.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "competitor_id": {"type": "string"},
                        "activity_types": {"type": "array", "items": {"type": "string"}},
                        "date_range": {"type": "object"},
                    },
                    "required": ["competitor_id"],
                },
            },
            {
                "name": "compare_positioning",
                "description": "Compare market positioning.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "competitors": {"type": "array", "items": {"type": "string"}},
                        "dimensions": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_strategy",
                "description": "Analyze competitor strategy.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "competitor_id": {"type": "string"},
                        "areas": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["competitor_id"],
                },
            },
            {
                "name": "get_market_share",
                "description": "Get market share comparison.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "market": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "generate_competitive_report",
                "description": "Generate competitive analysis report.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "competitors": {"type": "array", "items": {"type": "string"}},
                        "include": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id
            if tool_name == "add_competitor":
                response = await self.http_client.post("/api/v1/competitors", json={**tool_input, "client_id": client_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to add"}
            elif tool_name == "get_competitor_activity":
                response = await self.http_client.get(f"/api/v1/competitors/{tool_input['competitor_id']}/activity", params=tool_input)
                return response.json() if response.status_code == 200 else {"activity": []}
            elif tool_name == "compare_positioning":
                return {"status": "ready_to_compare", "instruction": "Compare market positioning across dimensions."}
            elif tool_name == "analyze_strategy":
                return {"status": "ready_to_analyze", "instruction": "Analyze competitor strategy and tactics."}
            elif tool_name == "get_market_share":
                response = await self.http_client.get("/api/v1/competitors/market-share", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"market_share": None}
            elif tool_name == "generate_competitive_report":
                return {"status": "ready_to_generate", "instruction": "Generate comprehensive competitive analysis report."}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
