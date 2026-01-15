from typing import Any, Optional, List
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class CampaignAgent(BaseAgent):
    """
    Agent for campaign management.

    Capabilities:
    - Create and manage campaigns (API)
    - Track campaign performance (API)
    - Coordinate campaign assets (API)
    - Manage campaign calendar (API)
    - Verify landing pages (Browser)
    - Capture campaign screenshots (Browser)
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        client_id: str = None,
        instance_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.instance_id = instance_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        session_name = f"campaign_{instance_id}" if instance_id else "campaign"
        self.browser = AgentBrowserSkill(session_name=session_name)
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
5. Optimize for results

You have browser automation to:
- Verify landing pages are live before launch
- Capture screenshots of campaign assets
- Check competitor campaigns"""

    def _define_tools(self) -> list[dict]:
        return [
            # API-Based Tools
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
            # Browser-Based Tools
            {
                "name": "verify_landing_page",
                "description": "Verify campaign landing page is live.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "campaign_id": {"type": "string"},
                        "expected_content": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "capture_campaign_creative",
                "description": "Capture screenshot of campaign creative/landing page.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "campaign_id": {"type": "string"},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "check_competitor_campaign",
                "description": "Check competitor campaign landing page.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "competitor_url": {"type": "string"},
                        "campaign_id": {"type": "string", "description": "Our campaign to compare against"},
                    },
                    "required": ["competitor_url"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            # API-Based Tools
            if tool_name == "create_campaign":
                tool_input["client_id"] = tool_input.get("client_id") or self.client_specific_id
                response = await self.http_client.post("/api/v1/campaigns", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create"}
            elif tool_name == "get_campaign":
                response = await self.http_client.get(f"/api/v1/campaigns/{tool_input['campaign_id']}")
                return response.json() if response.status_code == 200 else {"error": "Campaign not found"}
            elif tool_name == "update_campaign":
                response = await self.http_client.patch(
                    f"/api/v1/campaigns/{tool_input['campaign_id']}",
                    json=tool_input["updates"]
                )
                return response.json() if response.status_code == 200 else {"error": "Failed to update"}
            elif tool_name == "add_campaign_asset":
                response = await self.http_client.post(
                    f"/api/v1/campaigns/{tool_input['campaign_id']}/assets",
                    json=tool_input
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to add asset"}
            elif tool_name == "get_campaign_calendar":
                response = await self.http_client.get("/api/v1/campaigns/calendar", params=tool_input)
                return response.json() if response.status_code == 200 else {"calendar": []}
            elif tool_name == "get_campaign_performance":
                response = await self.http_client.get(f"/api/v1/campaigns/{tool_input['campaign_id']}/performance")
                return response.json() if response.status_code == 200 else {"performance": None}

            # Browser-Based Tools
            elif tool_name == "verify_landing_page":
                return await self._verify_landing(
                    url=tool_input["url"],
                    campaign_id=tool_input.get("campaign_id"),
                    expected=tool_input.get("expected_content", []),
                )
            elif tool_name == "capture_campaign_creative":
                return await self._capture_creative(
                    url=tool_input["url"],
                    campaign_id=tool_input.get("campaign_id"),
                )
            elif tool_name == "check_competitor_campaign":
                return await self._check_competitor(
                    url=tool_input["competitor_url"],
                    campaign_id=tool_input.get("campaign_id"),
                )

            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _verify_landing(self, url: str, campaign_id: str = None, expected: List[str] = None) -> dict:
        """Verify landing page is live."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)

            found = []
            missing = []
            if expected:
                for item in expected:
                    if item.lower() in snapshot.raw.lower():
                        found.append(item)
                    else:
                        missing.append(item)

            screenshot_path = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"landing_{campaign_id}" if campaign_id else "landing"
            )

            return {
                "url": url,
                "campaign_id": campaign_id,
                "status": "live" if not missing else "issues_found",
                "found_content": found,
                "missing_content": missing,
                "screenshot": screenshot_path,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"url": url, "status": "error", "error": str(e)}

    async def _capture_creative(self, url: str, campaign_id: str = None) -> dict:
        """Capture campaign creative screenshot."""
        try:
            screenshot_path = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"creative_{campaign_id}" if campaign_id else "creative"
            )
            return {
                "url": url,
                "campaign_id": campaign_id,
                "screenshot": screenshot_path,
                "success": True,
            }
        except Exception as e:
            return {"error": f"Creative capture failed: {str(e)}"}

    async def _check_competitor(self, url: str, campaign_id: str = None) -> dict:
        """Check competitor campaign page."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/campaign_proofs",
                prefix="competitor"
            )

            return {
                "competitor_url": url,
                "our_campaign_id": campaign_id,
                "snapshot": snapshot.raw,
                "screenshot": screenshot_path,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Competitor check failed: {str(e)}"}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
