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
    - Scrape Google Ads Preview Tool (Browser)
    - Capture SERP ad positions (Browser)
    - Scrape Facebook Ad Library (Browser)
    - Check display ad placements (Browser)
    - Monitor competitor ad spend (Browser)
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

You have browser automation to:
- Verify ads are live on platforms
- Capture dashboard screenshots for reporting
- Check tracking pixel installation
- Preview Google Ads in different locations
- Capture SERP ad positions for proof
- Monitor competitor ads in Facebook Ad Library
- Check display ad placements on GDN
- Verify programmatic ad delivery"""

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
            # Extended Browser Tools
            {"name": "preview_google_ad", "description": "Preview Google ad using Google Ads Preview Tool.", "input_schema": {"type": "object", "properties": {"keyword": {"type": "string"}, "location": {"type": "string", "default": "United States"}, "device": {"type": "string", "enum": ["desktop", "mobile", "tablet"], "default": "desktop"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["keyword"]}},
            {"name": "capture_serp_ads", "description": "Capture SERP ads for specific keywords as proof.", "input_schema": {"type": "object", "properties": {"keyword": {"type": "string"}, "search_engine": {"type": "string", "enum": ["google", "bing"], "default": "google"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["keyword"]}},
            {"name": "scrape_fb_ad_library", "description": "Scrape Facebook Ad Library for competitor ads.", "input_schema": {"type": "object", "properties": {"advertiser_name": {"type": "string"}, "country": {"type": "string", "default": "US"}, "ad_type": {"type": "string", "enum": ["all", "political", "housing", "employment"], "default": "all"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["advertiser_name"]}},
            {"name": "check_display_placement", "description": "Check if display ad appears on specific publisher site.", "input_schema": {"type": "object", "properties": {"publisher_url": {"type": "string"}, "ad_identifier": {"type": "string", "description": "Ad text or image to look for"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["publisher_url"]}},
            {"name": "scrape_spyfu", "description": "Scrape SpyFu for competitor PPC data.", "input_schema": {"type": "object", "properties": {"domain": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["domain"]}},
            {"name": "scrape_semrush_ads", "description": "Scrape SEMrush advertising research data.", "input_schema": {"type": "object", "properties": {"domain": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["domain"]}},
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
            # Extended Browser Tools
            elif tool_name == "preview_google_ad":
                return await self._preview_google_ad(tool_input["keyword"], tool_input.get("location", "United States"), tool_input.get("device", "desktop"), tool_input.get("capture_screenshot", True))
            elif tool_name == "capture_serp_ads":
                return await self._capture_serp_ads(tool_input["keyword"], tool_input.get("search_engine", "google"), tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_fb_ad_library":
                return await self._scrape_fb_ad_library(tool_input["advertiser_name"], tool_input.get("country", "US"), tool_input.get("ad_type", "all"), tool_input.get("capture_screenshot", True))
            elif tool_name == "check_display_placement":
                return await self._check_display_placement(tool_input["publisher_url"], tool_input.get("ad_identifier"), tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_spyfu":
                return await self._scrape_spyfu(tool_input["domain"], tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_semrush_ads":
                return await self._scrape_semrush(tool_input["domain"], tool_input.get("capture_screenshot", True))
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

    # =========================================================================
    # Extended Browser Implementations
    # =========================================================================

    async def _preview_google_ad(self, keyword: str, location: str = "United States", device: str = "desktop", capture: bool = True) -> dict:
        """Preview Google ad using Google Ads Preview and Diagnosis tool."""
        # Google Ads Preview Tool URL (requires being logged in, but we can still try)
        url = f"https://www.google.com/search?q={keyword}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "keyword": keyword,
                "location": location,
                "device": device,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/media_proofs", prefix=f"ad_preview_{keyword.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"Google Ad preview failed: {str(e)}"}

    async def _capture_serp_ads(self, keyword: str, engine: str = "google", capture: bool = True) -> dict:
        """Capture SERP ads for specific keywords."""
        if engine == "google":
            url = f"https://www.google.com/search?q={keyword}"
        else:
            url = f"https://www.bing.com/search?q={keyword}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "keyword": keyword,
                "search_engine": engine,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/media_proofs", prefix=f"serp_{engine}_{keyword.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"SERP ads capture failed: {str(e)}"}

    async def _scrape_fb_ad_library(self, advertiser: str, country: str = "US", ad_type: str = "all", capture: bool = True) -> dict:
        """Scrape Facebook Ad Library for competitor ads."""
        url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type={ad_type}&country={country}&q={advertiser}&media_type=all"

        try:
            await self.browser.open(url)
            await self.browser.wait(3500)  # Ad library loads slowly
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "advertiser": advertiser,
                "country": country,
                "ad_type": ad_type,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/media_proofs", prefix=f"fb_ads_{advertiser.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"Facebook Ad Library scrape failed: {str(e)}"}

    async def _check_display_placement(self, url: str, ad_identifier: str = None, capture: bool = True) -> dict:
        """Check if display ad appears on publisher site."""
        try:
            await self.browser.open(url)
            await self.browser.wait(3000)  # Let ads load
            snapshot = await self.browser.snapshot(interactive_only=False)

            # Check if ad identifier is present
            ad_found = ad_identifier.lower() in snapshot.raw.lower() if ad_identifier else None

            result = {
                "publisher_url": url,
                "ad_identifier": ad_identifier,
                "ad_found": ad_found,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/media_proofs", prefix="display_check"
                )

            return result
        except Exception as e:
            return {"error": f"Display placement check failed: {str(e)}"}

    async def _scrape_spyfu(self, domain: str, capture: bool = True) -> dict:
        """Scrape SpyFu for competitor PPC data."""
        url = f"https://www.spyfu.com/overview/domain?query={domain}"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "domain": domain,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/media_proofs", prefix=f"spyfu_{domain.replace('.', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"SpyFu scrape failed: {str(e)}"}

    async def _scrape_semrush(self, domain: str, capture: bool = True) -> dict:
        """Scrape SEMrush for advertising research data."""
        url = f"https://www.semrush.com/analytics/overview/?q={domain}&searchType=domain"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "domain": domain,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/media_proofs", prefix=f"semrush_{domain.replace('.', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"SEMrush scrape failed: {str(e)}"}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
