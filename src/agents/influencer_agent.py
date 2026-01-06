from typing import Any
import httpx
from .base import BaseAgent


class InfluencerAgent(BaseAgent):
    """Agent for influencer marketing. Specializable by vertical/region."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, vertical: str = None, region: str = None, client_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.vertical = vertical
        self.region = region
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        parts = ["influencer_agent"]
        if self.vertical:
            parts.append(self.vertical)
        if self.region:
            parts.append(self.region)
        return "_".join(parts)

    @property
    def system_prompt(self) -> str:
        prompt = """You are an influencer marketing expert. Discover, manage, and measure influencer campaigns."""
        if self.vertical:
            prompt += f"\n\nSpecialized in {self.vertical} vertical."
        if self.region:
            prompt += f"\n\nFocused on {self.region} region."
        return prompt

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "discover_influencers", "description": "Discover influencers.", "input_schema": {"type": "object", "properties": {"criteria": {"type": "object"}, "vertical": {"type": "string"}, "region": {"type": "string"}}, "required": []}},
            {"name": "analyze_influencer", "description": "Analyze influencer profile.", "input_schema": {"type": "object", "properties": {"influencer_id": {"type": "string"}, "social_handle": {"type": "string"}}, "required": []}},
            {"name": "create_campaign", "description": "Create influencer campaign.", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}, "influencers": {"type": "array", "items": {"type": "string"}}, "deliverables": {"type": "array", "items": {"type": "object"}}}, "required": ["name"]}},
            {"name": "manage_contract", "description": "Manage influencer contract.", "input_schema": {"type": "object", "properties": {"influencer_id": {"type": "string"}, "terms": {"type": "object"}}, "required": ["influencer_id"]}},
            {"name": "track_performance", "description": "Track campaign performance.", "input_schema": {"type": "object", "properties": {"campaign_id": {"type": "string"}}, "required": ["campaign_id"]}},
            {"name": "calculate_roi", "description": "Calculate influencer ROI.", "input_schema": {"type": "object", "properties": {"campaign_id": {"type": "string"}}, "required": ["campaign_id"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            tool_input["vertical"] = tool_input.get("vertical") or self.vertical
            tool_input["region"] = tool_input.get("region") or self.region
            if tool_name == "discover_influencers":
                response = await self.http_client.get("/api/v1/influencers/discover", params=tool_input)
                return response.json() if response.status_code == 200 else {"influencers": []}
            elif tool_name == "analyze_influencer":
                response = await self.http_client.get(f"/api/v1/influencers/{tool_input.get('influencer_id', 'search')}/analyze", params=tool_input)
                return response.json() if response.status_code == 200 else {"analysis": None}
            elif tool_name == "create_campaign":
                response = await self.http_client.post("/api/v1/influencers/campaigns", json={**tool_input, "client_id": self.client_specific_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "manage_contract":
                response = await self.http_client.post(f"/api/v1/influencers/{tool_input['influencer_id']}/contracts", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "track_performance":
                response = await self.http_client.get(f"/api/v1/influencers/campaigns/{tool_input['campaign_id']}/performance")
                return response.json() if response.status_code == 200 else {"performance": None}
            elif tool_name == "calculate_roi":
                response = await self.http_client.get(f"/api/v1/influencers/campaigns/{tool_input['campaign_id']}/roi")
                return response.json() if response.status_code == 200 else {"roi": None}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
