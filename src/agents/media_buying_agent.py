from typing import Any
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class MediaBuyingAgent(BaseAgent):
    """
    Agent for media buying and planning.

    Capabilities:
    - Create media plans (API)
    - Manage ad placements (API)
    - Optimize media spend (API)
    - Verify ads are live (Browser)
    - Screenshot campaign dashboards (Browser)
    - Check tracking pixel installation (Browser)
    """

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, client_id: str = None, instance_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.instance_id = instance_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        session_name = f"media_buying_{instance_id}" if instance_id else "media_buying"
        self.browser = AgentBrowserSkill(session_name=session_name)
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
5. Track and report on results

You have browser automation to verify ads are live, capture dashboard screenshots, and check pixel installations."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "create_media_plan", "description": "Create a media plan.", "input_schema": {"type": "object", "properties": {"campaign_id": {"type": "string"}, "budget": {"type": "number"}, "objectives": {"type": "array", "items": {"type": "string"}}, "target_audience": {"type": "object"}, "channels": {"type": "array", "items": {"type": "string"}}}, "required": ["budget", "objectives"]}},
            {"name": "get_channel_rates", "description": "Get advertising rates by channel.", "input_schema": {"type": "object", "properties": {"channels": {"type": "array", "items": {"type": "string"}}, "region": {"type": "string"}}, "required": ["channels"]}},
            {"name": "allocate_budget", "description": "Allocate budget across channels.", "input_schema": {"type": "object", "properties": {"media_plan_id": {"type": "string"}, "allocation": {"type": "object"}}, "required": ["media_plan_id", "allocation"]}},
            {"name": "create_placement", "description": "Create ad placement.", "input_schema": {"type": "object", "properties": {"media_plan_id": {"type": "string"}, "channel": {"type": "string"}, "placement_details": {"type": "object"}}, "required": ["media_plan_id", "channel"]}},
            {"name": "get_media_performance", "description": "Get media performance metrics.", "input_schema": {"type": "object", "properties": {"media_plan_id": {"type": "string"}, "campaign_id": {"type": "string"}, "date_range": {"type": "object"}}, "required": []}},
            {"name": "optimize_spend", "description": "Optimize media spend allocation.", "input_schema": {"type": "object", "properties": {"media_plan_id": {"type": "string"}, "optimize_for": {"type": "string", "enum": ["reach", "conversions", "engagement", "cpm"]}}, "required": ["media_plan_id"]}},
            {"name": "verify_ad_live", "description": "Verify ad is live via browser.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["google_ads", "meta_ads", "tiktok_ads", "linkedin_ads"]}, "dashboard_url": {"type": "string"}, "expected_status": {"type": "string", "default": "Active"}}, "required": ["platform", "dashboard_url"]}},
            {"name": "capture_campaign_dashboard", "description": "Screenshot campaign dashboard.", "input_schema": {"type": "object", "properties": {"dashboard_url": {"type": "string"}, "campaign_id": {"type": "string"}}, "required": ["dashboard_url"]}},
            {"name": "check_pixel_installation", "description": "Check tracking pixel on site.", "input_schema": {"type": "object", "properties": {"site_url": {"type": "string"}, "pixel_type": {"type": "string", "enum": ["meta", "google", "tiktok", "linkedin"]}}, "required": ["site_url", "pixel_type"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "create_media_plan":
                response = await self.http_client.post("/api/v1/media/plans", json={**tool_input, "client_id": self.client_specific_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_channel_rates":
                response = await self.http_client.get("/api/v1/media/rates", params=tool_input)
                return response.json() if response.status_code == 200 else {"rates": []}
            elif tool_name == "allocate_budget":
                response = await self.http_client.post(f"/api/v1/media/plans/{tool_input['media_plan_id']}/allocate", json=tool_input["allocation"])
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            elif tool_name == "create_placement":
                response = await self.http_client.post(f"/api/v1/media/plans/{tool_input['media_plan_id']}/placements", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_media_performance":
                response = await self.http_client.get("/api/v1/media/performance", params=tool_input)
                return response.json() if response.status_code == 200 else {"performance": None}
            elif tool_name == "optimize_spend":
                return {"status": "ready_to_optimize", "instruction": "Analyze performance and recommend optimal budget allocation."}
            elif tool_name == "verify_ad_live":
                return await self._verify_ad_live(tool_input["platform"], tool_input["dashboard_url"], tool_input.get("expected_status", "Active"))
            elif tool_name == "capture_campaign_dashboard":
                return await self._capture_dashboard(tool_input["dashboard_url"], tool_input.get("campaign_id"))
            elif tool_name == "check_pixel_installation":
                return await self._check_pixel(tool_input["site_url"], tool_input["pixel_type"])
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _verify_ad_live(self, platform: str, url: str, expected: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/media_proofs", prefix=f"ad_verify_{platform}")
            return {"platform": platform, "verified": expected.lower() in snapshot.raw.lower(), "screenshot": screenshot_path, "timestamp": snapshot.timestamp.isoformat()}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_dashboard(self, url: str, campaign_id: str = None) -> dict:
        try:
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/media_proofs", prefix=f"dashboard_{campaign_id}" if campaign_id else "dashboard")
            return {"url": url, "screenshot": screenshot_path, "success": True}
        except Exception as e:
            return {"error": str(e)}

    async def _check_pixel(self, url: str, pixel_type: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            patterns = {"meta": ["fbevents.js", "fbq("], "google": ["gtag", "googletagmanager"], "tiktok": ["analytics.tiktok.com"], "linkedin": ["snap.licdn.com"]}
            found = any(p.lower() in snapshot.raw.lower() for p in patterns.get(pixel_type, []))
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/media_proofs", prefix=f"pixel_{pixel_type}")
            return {"url": url, "pixel_type": pixel_type, "pixel_found": found, "screenshot": screenshot_path}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
