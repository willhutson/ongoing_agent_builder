from typing import Any
import httpx
from .base import BaseAgent


class MediaBuyingAgent(BaseAgent):
    """
    Agent for media buying and planning.

    Capabilities:
    - Create media plans
    - Manage ad placements
    - Optimize media spend
    - Track media performance
    - Negotiate rates
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
        return "media_buying_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a media buying and planning expert.

Your role is to optimize media investments:
1. Create strategic media plans
2. Select optimal channels and placements
3. Manage budgets and bidding
4. Optimize for performance
5. Track and report on results"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_media_plan",
                "description": "Create a media plan.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "budget": {"type": "number"},
                        "objectives": {"type": "array", "items": {"type": "string"}},
                        "target_audience": {"type": "object"},
                        "channels": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["budget", "objectives"],
                },
            },
            {
                "name": "get_channel_rates",
                "description": "Get advertising rates by channel.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "channels": {"type": "array", "items": {"type": "string"}},
                        "region": {"type": "string"},
                    },
                    "required": ["channels"],
                },
            },
            {
                "name": "allocate_budget",
                "description": "Allocate budget across channels.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "media_plan_id": {"type": "string"},
                        "allocation": {"type": "object"},
                    },
                    "required": ["media_plan_id", "allocation"],
                },
            },
            {
                "name": "create_placement",
                "description": "Create ad placement.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "media_plan_id": {"type": "string"},
                        "channel": {"type": "string"},
                        "placement_details": {"type": "object"},
                    },
                    "required": ["media_plan_id", "channel"],
                },
            },
            {
                "name": "get_media_performance",
                "description": "Get media performance metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "media_plan_id": {"type": "string"},
                        "campaign_id": {"type": "string"},
                        "date_range": {"type": "object"},
                    },
                    "required": [],
                },
            },
            {
                "name": "optimize_spend",
                "description": "Optimize media spend allocation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "media_plan_id": {"type": "string"},
                        "optimize_for": {"type": "string", "enum": ["reach", "conversions", "engagement", "cpm"]},
                    },
                    "required": ["media_plan_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "create_media_plan":
                response = await self.http_client.post("/api/v1/media/plans", json={**tool_input, "client_id": self.client_specific_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create"}
            elif tool_name == "get_channel_rates":
                response = await self.http_client.get("/api/v1/media/rates", params=tool_input)
                return response.json() if response.status_code == 200 else {"rates": []}
            elif tool_name == "allocate_budget":
                response = await self.http_client.post(f"/api/v1/media/plans/{tool_input['media_plan_id']}/allocate", json=tool_input["allocation"])
                return response.json() if response.status_code == 200 else {"error": "Failed to allocate"}
            elif tool_name == "create_placement":
                response = await self.http_client.post(f"/api/v1/media/plans/{tool_input['media_plan_id']}/placements", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create"}
            elif tool_name == "get_media_performance":
                response = await self.http_client.get("/api/v1/media/performance", params=tool_input)
                return response.json() if response.status_code == 200 else {"performance": None}
            elif tool_name == "optimize_spend":
                return {"status": "ready_to_optimize", "instruction": "Analyze performance and recommend optimal budget allocation."}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
