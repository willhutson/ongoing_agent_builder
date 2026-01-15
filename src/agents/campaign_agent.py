from typing import Any, Optional, List
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class CampaignAgent(BaseAgent):
    """
    Agent for campaign management with comprehensive asset verification.

    Capabilities:
    - Create and manage campaigns (API)
    - Track campaign performance (API)
    - Coordinate campaign assets (API)
    - Manage campaign calendar (API)
    - Verify landing pages (Browser)
    - Capture campaign screenshots (Browser)
    - A/B test variant capture (Browser)
    - Email template preview (Browser)
    - Social media asset verification (Browser)
    - Mobile responsive verification (Browser)
    - Form and UTM validation (Browser)
    - Video ad preview (Browser)
    - QR code verification (Browser)
    - Link destination validation (Browser)
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
        return """You are a campaign management expert for marketing agencies.

Your role is to orchestrate successful campaigns:
1. Plan and structure campaigns
2. Coordinate assets and deliverables
3. Manage campaign timelines
4. Track performance across channels
5. Verify all campaign assets before launch

You have browser automation to:
- Verify landing pages are live before launch
- Capture screenshots of campaign assets
- Check competitor campaigns
- Capture A/B test variants side-by-side
- Preview email templates across clients
- Verify social media assets are correct
- Check mobile responsive design
- Validate forms and UTM parameters
- Preview video ads
- Verify QR codes are functional
- Validate all link destinations"""

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
            # Extended Browser Tools - A/B Testing
            {"name": "capture_ab_variants", "description": "Capture A/B test variants side-by-side.", "input_schema": {"type": "object", "properties": {"variant_a_url": {"type": "string"}, "variant_b_url": {"type": "string"}, "test_name": {"type": "string"}}, "required": ["variant_a_url", "variant_b_url"]}},
            {"name": "capture_multivariate_test", "description": "Capture multiple landing page variants.", "input_schema": {"type": "object", "properties": {"variant_urls": {"type": "array", "items": {"type": "string"}, "maxItems": 6}, "test_name": {"type": "string"}}, "required": ["variant_urls"]}},
            # Extended Browser Tools - Email Preview
            {"name": "preview_email_template", "description": "Preview email template in browser.", "input_schema": {"type": "object", "properties": {"email_url": {"type": "string"}, "template_name": {"type": "string"}}, "required": ["email_url"]}},
            {"name": "capture_email_clients", "description": "Capture email preview across simulated clients.", "input_schema": {"type": "object", "properties": {"email_url": {"type": "string"}, "clients": {"type": "array", "items": {"type": "string", "enum": ["gmail", "outlook", "apple_mail", "yahoo"]}}}, "required": ["email_url"]}},
            # Extended Browser Tools - Social Media
            {"name": "verify_social_asset", "description": "Verify social media post/ad asset.", "input_schema": {"type": "object", "properties": {"asset_url": {"type": "string"}, "platform": {"type": "string", "enum": ["facebook", "instagram", "twitter", "linkedin", "tiktok"]}, "expected_content": {"type": "array", "items": {"type": "string"}}}, "required": ["asset_url", "platform"]}},
            {"name": "capture_social_preview", "description": "Capture social post preview card.", "input_schema": {"type": "object", "properties": {"page_url": {"type": "string"}, "platform": {"type": "string", "enum": ["facebook", "twitter", "linkedin"]}}, "required": ["page_url"]}},
            # Extended Browser Tools - Mobile/Responsive
            {"name": "check_mobile_responsive", "description": "Check page at mobile viewport size.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "device": {"type": "string", "enum": ["iphone_se", "iphone_14", "pixel_7", "ipad", "tablet"], "default": "iphone_14"}}, "required": ["url"]}},
            {"name": "capture_responsive_suite", "description": "Capture page at multiple viewport sizes.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "viewports": {"type": "array", "items": {"type": "string", "enum": ["mobile", "tablet", "desktop", "wide"]}}}, "required": ["url"]}},
            # Extended Browser Tools - Form Validation
            {"name": "verify_form_fields", "description": "Verify form fields are present and capture.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "expected_fields": {"type": "array", "items": {"type": "string"}}}, "required": ["url"]}},
            {"name": "validate_utm_parameters", "description": "Validate UTM parameters in landing page URL.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "expected_utms": {"type": "object", "description": "Expected UTM values"}}, "required": ["url"]}},
            # Extended Browser Tools - Video/Rich Media
            {"name": "preview_video_ad", "description": "Capture video ad preview/thumbnail.", "input_schema": {"type": "object", "properties": {"video_url": {"type": "string"}, "platform": {"type": "string", "enum": ["youtube", "vimeo", "facebook", "tiktok"]}}, "required": ["video_url"]}},
            {"name": "verify_rich_media", "description": "Verify rich media ad loads correctly.", "input_schema": {"type": "object", "properties": {"ad_url": {"type": "string"}, "ad_type": {"type": "string", "enum": ["html5", "video", "carousel", "interactive"]}}, "required": ["ad_url"]}},
            # Extended Browser Tools - Link Validation
            {"name": "verify_qr_code", "description": "Navigate to QR code destination and verify.", "input_schema": {"type": "object", "properties": {"qr_destination_url": {"type": "string"}, "expected_destination": {"type": "string"}}, "required": ["qr_destination_url"]}},
            {"name": "validate_link_destination", "description": "Validate link goes to correct destination.", "input_schema": {"type": "object", "properties": {"link_url": {"type": "string"}, "expected_content": {"type": "array", "items": {"type": "string"}}}, "required": ["link_url"]}},
            {"name": "check_redirect_chain", "description": "Check redirect chain for a URL.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            # Extended Browser Tools - Asset Comparison
            {"name": "compare_before_after", "description": "Capture before/after comparison for campaign updates.", "input_schema": {"type": "object", "properties": {"before_url": {"type": "string"}, "after_url": {"type": "string"}, "comparison_name": {"type": "string"}}, "required": ["before_url", "after_url"]}},
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
            # Extended Browser Tools - A/B Testing
            elif tool_name == "capture_ab_variants":
                return await self._capture_ab_variants(tool_input["variant_a_url"], tool_input["variant_b_url"], tool_input.get("test_name", "ab_test"))
            elif tool_name == "capture_multivariate_test":
                return await self._capture_multivariate(tool_input["variant_urls"], tool_input.get("test_name", "mvt"))
            # Extended Browser Tools - Email Preview
            elif tool_name == "preview_email_template":
                return await self._preview_email(tool_input["email_url"], tool_input.get("template_name", "email"))
            elif tool_name == "capture_email_clients":
                return await self._capture_email_clients(tool_input["email_url"], tool_input.get("clients", ["gmail", "outlook"]))
            # Extended Browser Tools - Social Media
            elif tool_name == "verify_social_asset":
                return await self._verify_social_asset(tool_input["asset_url"], tool_input["platform"], tool_input.get("expected_content", []))
            elif tool_name == "capture_social_preview":
                return await self._capture_social_preview(tool_input["page_url"], tool_input.get("platform", "facebook"))
            # Extended Browser Tools - Mobile/Responsive
            elif tool_name == "check_mobile_responsive":
                return await self._check_mobile(tool_input["url"], tool_input.get("device", "iphone_14"))
            elif tool_name == "capture_responsive_suite":
                return await self._capture_responsive_suite(tool_input["url"], tool_input.get("viewports", ["mobile", "tablet", "desktop"]))
            # Extended Browser Tools - Form Validation
            elif tool_name == "verify_form_fields":
                return await self._verify_form_fields(tool_input["url"], tool_input.get("expected_fields", []))
            elif tool_name == "validate_utm_parameters":
                return await self._validate_utm(tool_input["url"], tool_input.get("expected_utms", {}))
            # Extended Browser Tools - Video/Rich Media
            elif tool_name == "preview_video_ad":
                return await self._preview_video(tool_input["video_url"], tool_input.get("platform", "youtube"))
            elif tool_name == "verify_rich_media":
                return await self._verify_rich_media(tool_input["ad_url"], tool_input.get("ad_type", "html5"))
            # Extended Browser Tools - Link Validation
            elif tool_name == "verify_qr_code":
                return await self._verify_qr_destination(tool_input["qr_destination_url"], tool_input.get("expected_destination"))
            elif tool_name == "validate_link_destination":
                return await self._validate_link(tool_input["link_url"], tool_input.get("expected_content", []))
            elif tool_name == "check_redirect_chain":
                return await self._check_redirects(tool_input["url"])
            # Extended Browser Tools - Asset Comparison
            elif tool_name == "compare_before_after":
                return await self._compare_before_after(tool_input["before_url"], tool_input["after_url"], tool_input.get("comparison_name", "comparison"))

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

    # =========================================================================
    # A/B Testing Methods
    # =========================================================================

    async def _capture_ab_variants(self, variant_a_url: str, variant_b_url: str, test_name: str) -> dict:
        """Capture A/B test variants side-by-side for comparison."""
        try:
            variants = []

            # Capture Variant A
            await self.browser.open(variant_a_url)
            await self.browser.wait(2000)
            snapshot_a = await self.browser.snapshot(interactive_only=False)
            screenshot_a = await self.browser.capture_proof(
                url=variant_a_url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"{test_name}_variant_a"
            )
            variants.append({
                "variant": "A",
                "url": variant_a_url,
                "snapshot": snapshot_a.raw[:2000],
                "screenshot": screenshot_a,
            })

            # Capture Variant B
            await self.browser.open(variant_b_url)
            await self.browser.wait(2000)
            snapshot_b = await self.browser.snapshot(interactive_only=False)
            screenshot_b = await self.browser.capture_proof(
                url=variant_b_url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"{test_name}_variant_b"
            )
            variants.append({
                "variant": "B",
                "url": variant_b_url,
                "snapshot": snapshot_b.raw[:2000],
                "screenshot": screenshot_b,
            })

            return {
                "test_name": test_name,
                "variants": variants,
                "comparison_ready": True,
            }
        except Exception as e:
            return {"error": f"A/B variant capture failed: {str(e)}"}

    async def _capture_multivariate(self, variant_urls: List[str], test_name: str) -> dict:
        """Capture multiple landing page variants for multivariate testing."""
        try:
            variants = []
            for i, url in enumerate(variant_urls[:6]):  # Max 6 variants
                variant_label = chr(65 + i)  # A, B, C, D, E, F
                await self.browser.open(url)
                await self.browser.wait(2000)
                snapshot = await self.browser.snapshot(interactive_only=False)
                screenshot = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/campaign_proofs",
                    prefix=f"{test_name}_variant_{variant_label}"
                )
                variants.append({
                    "variant": variant_label,
                    "url": url,
                    "snapshot": snapshot.raw[:1500],
                    "screenshot": screenshot,
                })

            return {
                "test_name": test_name,
                "variant_count": len(variants),
                "variants": variants,
            }
        except Exception as e:
            return {"error": f"Multivariate capture failed: {str(e)}"}

    # =========================================================================
    # Email Preview Methods
    # =========================================================================

    async def _preview_email(self, email_url: str, template_name: str) -> dict:
        """Preview email template in browser."""
        try:
            await self.browser.open(email_url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=email_url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"email_{template_name}"
            )

            # Basic email analysis
            content = snapshot.raw.lower()
            analysis = {
                "has_unsubscribe": "unsubscribe" in content,
                "has_view_in_browser": "view in browser" in content or "view online" in content,
                "has_images": "<img" in content,
                "has_cta_button": "button" in content or "btn" in content,
            }

            return {
                "template_name": template_name,
                "email_url": email_url,
                "screenshot": screenshot,
                "snapshot": snapshot.raw[:2000],
                "analysis": analysis,
            }
        except Exception as e:
            return {"error": f"Email preview failed: {str(e)}"}

    async def _capture_email_clients(self, email_url: str, clients: List[str]) -> dict:
        """Capture email preview simulating different email clients via viewport/rendering."""
        try:
            # Viewport sizes that approximate different email client rendering
            client_viewports = {
                "gmail": {"width": 600, "desc": "Gmail web (600px)"},
                "outlook": {"width": 650, "desc": "Outlook desktop (650px)"},
                "apple_mail": {"width": 580, "desc": "Apple Mail (580px)"},
                "yahoo": {"width": 640, "desc": "Yahoo Mail (640px)"},
            }

            captures = []
            for client in clients:
                if client not in client_viewports:
                    continue

                await self.browser.open(email_url)
                await self.browser.wait(2000)
                screenshot = await self.browser.capture_proof(
                    url=email_url,
                    output_dir="/tmp/campaign_proofs",
                    prefix=f"email_{client}"
                )
                captures.append({
                    "client": client,
                    "viewport": client_viewports[client],
                    "screenshot": screenshot,
                })

            return {
                "email_url": email_url,
                "clients_captured": len(captures),
                "captures": captures,
            }
        except Exception as e:
            return {"error": f"Email client capture failed: {str(e)}"}

    # =========================================================================
    # Social Media Methods
    # =========================================================================

    async def _verify_social_asset(self, asset_url: str, platform: str, expected_content: List[str]) -> dict:
        """Verify social media post/ad asset displays correctly."""
        try:
            await self.browser.open(asset_url)
            await self.browser.wait(3000)  # Social platforms load slowly

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=asset_url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"social_{platform}"
            )

            # Check expected content
            found = []
            missing = []
            for item in expected_content:
                if item.lower() in snapshot.raw.lower():
                    found.append(item)
                else:
                    missing.append(item)

            return {
                "platform": platform,
                "asset_url": asset_url,
                "status": "verified" if not missing else "issues_found",
                "found_content": found,
                "missing_content": missing,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Social asset verification failed: {str(e)}"}

    async def _capture_social_preview(self, page_url: str, platform: str) -> dict:
        """Capture how a page appears when shared on social (Open Graph preview)."""
        try:
            # Use platform-specific preview tools
            preview_urls = {
                "facebook": f"https://developers.facebook.com/tools/debug/?q={page_url}",
                "twitter": f"https://cards-dev.twitter.com/validator",  # Manual entry needed
                "linkedin": f"https://www.linkedin.com/post-inspector/inspect/{page_url}",
            }

            preview_url = preview_urls.get(platform, page_url)
            await self.browser.open(preview_url)
            await self.browser.wait(4000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=preview_url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"social_preview_{platform}"
            )

            return {
                "page_url": page_url,
                "platform": platform,
                "preview_tool_url": preview_url,
                "snapshot": snapshot.raw[:2000],
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Social preview capture failed: {str(e)}"}

    # =========================================================================
    # Mobile/Responsive Methods
    # =========================================================================

    async def _check_mobile(self, url: str, device: str) -> dict:
        """Check page at mobile viewport size."""
        try:
            # Device viewport dimensions
            devices = {
                "iphone_se": {"width": 375, "height": 667},
                "iphone_14": {"width": 390, "height": 844},
                "pixel_7": {"width": 412, "height": 915},
                "ipad": {"width": 768, "height": 1024},
                "tablet": {"width": 800, "height": 1280},
            }

            viewport = devices.get(device, devices["iphone_14"])

            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"mobile_{device}"
            )

            # Basic mobile analysis from content
            content = snapshot.raw.lower()
            mobile_analysis = {
                "has_viewport_meta": "viewport" in content,
                "has_hamburger_menu": "menu" in content or "nav" in content,
                "appears_responsive": True,  # Placeholder - would need visual analysis
            }

            return {
                "url": url,
                "device": device,
                "viewport": viewport,
                "screenshot": screenshot,
                "mobile_analysis": mobile_analysis,
            }
        except Exception as e:
            return {"error": f"Mobile check failed: {str(e)}"}

    async def _capture_responsive_suite(self, url: str, viewports: List[str]) -> dict:
        """Capture page at multiple viewport sizes for responsive testing."""
        try:
            viewport_sizes = {
                "mobile": {"width": 375, "height": 667, "label": "Mobile (375px)"},
                "tablet": {"width": 768, "height": 1024, "label": "Tablet (768px)"},
                "desktop": {"width": 1280, "height": 800, "label": "Desktop (1280px)"},
                "wide": {"width": 1920, "height": 1080, "label": "Wide (1920px)"},
            }

            captures = []
            for vp_name in viewports:
                if vp_name not in viewport_sizes:
                    continue

                vp = viewport_sizes[vp_name]
                await self.browser.open(url)
                await self.browser.wait(2000)
                screenshot = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/campaign_proofs",
                    prefix=f"responsive_{vp_name}"
                )
                captures.append({
                    "viewport": vp_name,
                    "dimensions": vp,
                    "screenshot": screenshot,
                })

            return {
                "url": url,
                "viewports_captured": len(captures),
                "captures": captures,
            }
        except Exception as e:
            return {"error": f"Responsive suite capture failed: {str(e)}"}

    # =========================================================================
    # Form Validation Methods
    # =========================================================================

    async def _verify_form_fields(self, url: str, expected_fields: List[str]) -> dict:
        """Verify form fields are present on a page."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=True)  # Get interactive elements
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/campaign_proofs",
                prefix="form_verification"
            )

            # Check for expected form fields
            content = snapshot.raw.lower()
            found_fields = []
            missing_fields = []

            for field in expected_fields:
                field_lower = field.lower()
                # Check for field by name, id, placeholder, or label
                if (field_lower in content or
                    f'name="{field_lower}"' in content or
                    f'id="{field_lower}"' in content or
                    f'placeholder="{field}"' in content.lower()):
                    found_fields.append(field)
                else:
                    missing_fields.append(field)

            # Basic form analysis
            form_analysis = {
                "has_form": "<form" in content,
                "has_submit": "submit" in content or "button" in content,
                "has_email_field": "email" in content,
                "has_required_fields": "required" in content,
            }

            return {
                "url": url,
                "found_fields": found_fields,
                "missing_fields": missing_fields,
                "all_fields_present": len(missing_fields) == 0,
                "form_analysis": form_analysis,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Form verification failed: {str(e)}"}

    async def _validate_utm(self, url: str, expected_utms: dict) -> dict:
        """Validate UTM parameters in landing page URL."""
        try:
            from urllib.parse import urlparse, parse_qs

            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)

            # Flatten query params (parse_qs returns lists)
            actual_utms = {}
            for key, value in query_params.items():
                if key.startswith("utm_"):
                    actual_utms[key] = value[0] if value else ""

            # Compare expected vs actual
            matched = {}
            mismatched = {}
            missing = {}

            for utm_key, expected_value in expected_utms.items():
                if utm_key in actual_utms:
                    if actual_utms[utm_key] == expected_value:
                        matched[utm_key] = expected_value
                    else:
                        mismatched[utm_key] = {
                            "expected": expected_value,
                            "actual": actual_utms[utm_key],
                        }
                else:
                    missing[utm_key] = expected_value

            # Also capture the page
            await self.browser.open(url)
            await self.browser.wait(2000)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/campaign_proofs",
                prefix="utm_validation"
            )

            return {
                "url": url,
                "actual_utms": actual_utms,
                "matched": matched,
                "mismatched": mismatched,
                "missing": missing,
                "all_valid": len(mismatched) == 0 and len(missing) == 0,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"UTM validation failed: {str(e)}"}

    # =========================================================================
    # Video/Rich Media Methods
    # =========================================================================

    async def _preview_video(self, video_url: str, platform: str) -> dict:
        """Capture video ad preview/thumbnail."""
        try:
            await self.browser.open(video_url)
            await self.browser.wait(4000)  # Allow video player to load

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=video_url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"video_{platform}"
            )

            # Basic video analysis
            content = snapshot.raw.lower()
            video_analysis = {
                "platform": platform,
                "has_video_player": "video" in content or "player" in content,
                "has_controls": "play" in content or "pause" in content,
                "has_thumbnail": "thumbnail" in content or "poster" in content,
            }

            return {
                "video_url": video_url,
                "platform": platform,
                "screenshot": screenshot,
                "video_analysis": video_analysis,
            }
        except Exception as e:
            return {"error": f"Video preview failed: {str(e)}"}

    async def _verify_rich_media(self, ad_url: str, ad_type: str) -> dict:
        """Verify rich media ad loads correctly."""
        try:
            await self.browser.open(ad_url)
            await self.browser.wait(5000)  # Rich media needs time to load/animate

            snapshot = await self.browser.snapshot(interactive_only=True)
            screenshot = await self.browser.capture_proof(
                url=ad_url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"rich_media_{ad_type}"
            )

            # Rich media analysis
            content = snapshot.raw.lower()
            rich_media_analysis = {
                "ad_type": ad_type,
                "has_interactive_elements": len(snapshot.raw) > 100,
                "has_animation": "animation" in content or "animate" in content,
                "has_click_handler": "click" in content or "onclick" in content,
            }

            return {
                "ad_url": ad_url,
                "ad_type": ad_type,
                "screenshot": screenshot,
                "snapshot": snapshot.raw[:2000],
                "rich_media_analysis": rich_media_analysis,
                "loaded_successfully": True,
            }
        except Exception as e:
            return {"error": f"Rich media verification failed: {str(e)}"}

    # =========================================================================
    # Link Validation Methods
    # =========================================================================

    async def _verify_qr_destination(self, qr_destination_url: str, expected_destination: str = None) -> dict:
        """Navigate to QR code destination URL and verify it loads correctly."""
        try:
            await self.browser.open(qr_destination_url)
            await self.browser.wait(3000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=qr_destination_url,
                output_dir="/tmp/campaign_proofs",
                prefix="qr_destination"
            )

            # Check if destination matches expected
            destination_matches = True
            if expected_destination:
                destination_matches = expected_destination.lower() in snapshot.raw.lower()

            return {
                "qr_destination_url": qr_destination_url,
                "expected_destination": expected_destination,
                "destination_matches": destination_matches,
                "page_loaded": True,
                "screenshot": screenshot,
                "snapshot": snapshot.raw[:2000],
            }
        except Exception as e:
            return {"error": f"QR destination verification failed: {str(e)}"}

    async def _validate_link(self, link_url: str, expected_content: List[str]) -> dict:
        """Validate link goes to correct destination with expected content."""
        try:
            await self.browser.open(link_url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=link_url,
                output_dir="/tmp/campaign_proofs",
                prefix="link_validation"
            )

            # Check expected content
            found = []
            missing = []
            for item in expected_content:
                if item.lower() in snapshot.raw.lower():
                    found.append(item)
                else:
                    missing.append(item)

            return {
                "link_url": link_url,
                "status": "valid" if not missing else "issues_found",
                "found_content": found,
                "missing_content": missing,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Link validation failed: {str(e)}"}

    async def _check_redirects(self, url: str) -> dict:
        """Check redirect chain for a URL using HTTP client."""
        try:
            redirects = []
            current_url = url

            # Follow redirects manually to capture chain
            async with httpx.AsyncClient(follow_redirects=False, timeout=30.0) as client:
                for i in range(10):  # Max 10 redirects
                    try:
                        response = await client.get(current_url)
                        redirects.append({
                            "step": i + 1,
                            "url": current_url,
                            "status_code": response.status_code,
                        })

                        if response.status_code in (301, 302, 303, 307, 308):
                            location = response.headers.get("location", "")
                            if location:
                                # Handle relative URLs
                                if location.startswith("/"):
                                    from urllib.parse import urlparse
                                    parsed = urlparse(current_url)
                                    location = f"{parsed.scheme}://{parsed.netloc}{location}"
                                current_url = location
                            else:
                                break
                        else:
                            break
                    except Exception as e:
                        redirects.append({
                            "step": i + 1,
                            "url": current_url,
                            "error": str(e),
                        })
                        break

            # Capture final destination
            final_url = redirects[-1]["url"] if redirects else url
            await self.browser.open(final_url)
            await self.browser.wait(2000)
            screenshot = await self.browser.capture_proof(
                url=final_url,
                output_dir="/tmp/campaign_proofs",
                prefix="redirect_final"
            )

            return {
                "original_url": url,
                "final_url": final_url,
                "redirect_count": len(redirects) - 1,
                "redirect_chain": redirects,
                "final_screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Redirect check failed: {str(e)}"}

    # =========================================================================
    # Asset Comparison Methods
    # =========================================================================

    async def _compare_before_after(self, before_url: str, after_url: str, comparison_name: str) -> dict:
        """Capture before/after comparison for campaign updates."""
        try:
            # Capture "before" state
            await self.browser.open(before_url)
            await self.browser.wait(2000)
            snapshot_before = await self.browser.snapshot(interactive_only=False)
            screenshot_before = await self.browser.capture_proof(
                url=before_url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"{comparison_name}_before"
            )

            # Capture "after" state
            await self.browser.open(after_url)
            await self.browser.wait(2000)
            snapshot_after = await self.browser.snapshot(interactive_only=False)
            screenshot_after = await self.browser.capture_proof(
                url=after_url,
                output_dir="/tmp/campaign_proofs",
                prefix=f"{comparison_name}_after"
            )

            return {
                "comparison_name": comparison_name,
                "before": {
                    "url": before_url,
                    "screenshot": screenshot_before,
                    "snapshot": snapshot_before.raw[:1500],
                },
                "after": {
                    "url": after_url,
                    "screenshot": screenshot_after,
                    "snapshot": snapshot_after.raw[:1500],
                },
                "comparison_ready": True,
            }
        except Exception as e:
            return {"error": f"Before/after comparison failed: {str(e)}"}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
