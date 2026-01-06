from typing import Any
import httpx
from .base import BaseAgent


class CampaignAgent(BaseAgent):
    """
    Agent for campaign management.

    Capabilities:
    - Create and manage campaigns
    - Track campaign performance
    - Coordinate campaign assets
    - Manage campaign calendar
    - Handle multi-channel campaigns
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
        return "campaign_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a campaign management expert.

Your role is to orchestrate successful campaigns:
1. Plan and structure campaigns
2. Coordinate assets and deliverables
3. Manage campaign timelines
4. Track performance across channels
5. Optimize for results"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_campaign",
                "description": "Create a new campaign.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "client_id": {"type": "string"},
                        "objectives": {"type": "array", "items": {"type": "string"}},
                        "channels": {"type": "array", "items": {"type": "string"}},
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"},
                        "budget": {"type": "number"},
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "get_campaign",
                "description": "Get campaign details.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                    },
                    "required": ["campaign_id"],
                },
            },
            {
                "name": "update_campaign",
                "description": "Update campaign.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "updates": {"type": "object"},
                    },
                    "required": ["campaign_id", "updates"],
                },
            },
            {
                "name": "add_campaign_asset",
                "description": "Add asset to campaign.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "asset_id": {"type": "string"},
                        "channel": {"type": "string"},
                    },
                    "required": ["campaign_id", "asset_id"],
                },
            },
            {
                "name": "get_campaign_calendar",
                "description": "Get campaign calendar.",
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
                "name": "get_campaign_performance",
                "description": "Get campaign performance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "metrics": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["campaign_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "create_campaign":
                tool_input["client_id"] = tool_input.get("client_id") or self.client_specific_id
                response = await self.http_client.post("/api/v1/campaigns", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create"}
            elif tool_name == "get_campaign":
                response = await self.http_client.get(f"/api/v1/campaigns/{tool_input['campaign_id']}")
                return response.json() if response.status_code == 200 else {"error": "Campaign not found"}
            elif tool_name == "update_campaign":
                response = await self.http_client.patch(f"/api/v1/campaigns/{tool_input['campaign_id']}", json=tool_input["updates"])
                return response.json() if response.status_code == 200 else {"error": "Failed to update"}
            elif tool_name == "add_campaign_asset":
                response = await self.http_client.post(f"/api/v1/campaigns/{tool_input['campaign_id']}/assets", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to add asset"}
            elif tool_name == "get_campaign_calendar":
                response = await self.http_client.get("/api/v1/campaigns/calendar", params=tool_input)
                return response.json() if response.status_code == 200 else {"calendar": []}
            elif tool_name == "get_campaign_performance":
                response = await self.http_client.get(f"/api/v1/campaigns/{tool_input['campaign_id']}/performance")
                return response.json() if response.status_code == 200 else {"performance": None}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
