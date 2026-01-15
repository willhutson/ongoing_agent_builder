from typing import Any
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class InfluencerAgent(BaseAgent):
    """
    Agent for influencer marketing. Specializable by vertical/region.

    Capabilities:
    - Discover and analyze influencers (API)
    - Create and manage campaigns (API)
    - Track performance and ROI (API)
    - Scrape influencer profiles (Browser)
    - Capture post engagement proof (Browser)
    - Verify follower counts (Browser)
    - Scrape SocialBlade analytics (Browser)
    - Scrape HypeAuditor public data (Browser)
    - Check influencer authenticity (Browser)
    - Monitor influencer content (Browser)
    """

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, vertical: str = None, region: str = None, client_id: str = None, instance_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.vertical = vertical
        self.region = region
        self.client_specific_id = client_id
        self.instance_id = instance_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        session_name = f"influencer_{instance_id}" if instance_id else "influencer"
        self.browser = AgentBrowserSkill(session_name=session_name)
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
        prompt = """You are an influencer marketing expert. Discover, manage, and measure influencer campaigns.

You have browser automation to:
- Scrape influencer profiles from Instagram, TikTok, YouTube, Twitter
- Capture post engagement as proof for clients
- Verify follower counts directly from platforms
- Check SocialBlade for growth trends and analytics
- Review HypeAuditor for audience quality metrics
- Detect fake followers and engagement
- Monitor influencer content for brand safety"""
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
            {"name": "scrape_influencer_profile", "description": "Scrape influencer social profile via browser.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["instagram", "tiktok", "youtube", "twitter"]}, "profile_url": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["platform", "profile_url"]}},
            {"name": "capture_post_engagement", "description": "Screenshot post as engagement proof.", "input_schema": {"type": "object", "properties": {"post_url": {"type": "string"}, "campaign_id": {"type": "string"}}, "required": ["post_url"]}},
            {"name": "verify_follower_count", "description": "Verify follower count via browser.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["instagram", "tiktok", "youtube", "twitter"]}, "profile_url": {"type": "string"}}, "required": ["platform", "profile_url"]}},
            # Extended Browser Tools
            {"name": "scrape_socialblade", "description": "Scrape SocialBlade for influencer growth trends and analytics.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["instagram", "tiktok", "youtube", "twitter"]}, "username": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["platform", "username"]}},
            {"name": "scrape_hypeauditor", "description": "Scrape HypeAuditor for audience quality metrics.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["instagram", "tiktok", "youtube"]}, "username": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["platform", "username"]}},
            {"name": "check_fake_followers", "description": "Check for fake followers using FakeCheck.co or similar.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["instagram", "twitter"]}, "username": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["platform", "username"]}},
            {"name": "scrape_influencer_feed", "description": "Scrape recent posts from influencer feed for brand safety check.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["instagram", "tiktok", "youtube", "twitter"]}, "profile_url": {"type": "string"}, "scroll_count": {"type": "integer", "default": 3}}, "required": ["platform", "profile_url"]}},
            {"name": "capture_story_highlight", "description": "Capture influencer story highlights as proof.", "input_schema": {"type": "object", "properties": {"highlight_url": {"type": "string"}, "influencer_name": {"type": "string"}}, "required": ["highlight_url"]}},
            {"name": "scrape_modash", "description": "Scrape Modash for influencer discovery data.", "input_schema": {"type": "object", "properties": {"search_query": {"type": "string"}, "platform": {"type": "string", "enum": ["instagram", "tiktok", "youtube"]}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["search_query"]}},
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
            elif tool_name == "scrape_influencer_profile":
                return await self._scrape_profile(tool_input["platform"], tool_input["profile_url"], tool_input.get("capture_screenshot", True))
            elif tool_name == "capture_post_engagement":
                return await self._capture_post(tool_input["post_url"], tool_input.get("campaign_id"))
            elif tool_name == "verify_follower_count":
                return await self._verify_followers(tool_input["platform"], tool_input["profile_url"])
            # Extended Browser Tools
            elif tool_name == "scrape_socialblade":
                return await self._scrape_socialblade(tool_input["platform"], tool_input["username"], tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_hypeauditor":
                return await self._scrape_hypeauditor(tool_input["platform"], tool_input["username"], tool_input.get("capture_screenshot", True))
            elif tool_name == "check_fake_followers":
                return await self._check_fake_followers(tool_input["platform"], tool_input["username"], tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_influencer_feed":
                return await self._scrape_feed(tool_input["platform"], tool_input["profile_url"], tool_input.get("scroll_count", 3))
            elif tool_name == "capture_story_highlight":
                return await self._capture_highlight(tool_input["highlight_url"], tool_input.get("influencer_name", "influencer"))
            elif tool_name == "scrape_modash":
                return await self._scrape_modash(tool_input["search_query"], tool_input.get("platform"), tool_input.get("capture_screenshot", True))
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _scrape_profile(self, platform: str, url: str, capture: bool = True) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            result = {"platform": platform, "profile_url": url, "snapshot": snapshot.raw, "timestamp": snapshot.timestamp.isoformat()}
            if capture:
                result["screenshot"] = await self.browser.capture_proof(url=url, output_dir="/tmp/influencer_proofs", prefix=f"profile_{platform}")
            return result
        except Exception as e:
            return {"error": str(e)}

    async def _capture_post(self, url: str, campaign_id: str = None) -> dict:
        try:
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/influencer_proofs", prefix=f"post_{campaign_id}" if campaign_id else "post")
            return {"post_url": url, "screenshot": screenshot_path, "success": True}
        except Exception as e:
            return {"error": str(e)}

    async def _verify_followers(self, platform: str, url: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/influencer_proofs", prefix=f"followers_{platform}")
            return {"platform": platform, "snapshot": snapshot.raw, "screenshot": screenshot_path, "timestamp": snapshot.timestamp.isoformat()}
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # Extended Browser Implementations
    # =========================================================================

    async def _scrape_socialblade(self, platform: str, username: str, capture: bool = True) -> dict:
        """Scrape SocialBlade for growth trends and analytics."""
        platform_map = {"instagram": "instagram", "youtube": "youtube", "twitter": "twitter", "tiktok": "tiktok"}
        sb_platform = platform_map.get(platform, platform)
        url = f"https://socialblade.com/{sb_platform}/user/{username}"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "platform": platform,
                "username": username,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/influencer_proofs", prefix=f"socialblade_{platform}_{username}"
                )

            return result
        except Exception as e:
            return {"error": f"SocialBlade scrape failed: {str(e)}"}

    async def _scrape_hypeauditor(self, platform: str, username: str, capture: bool = True) -> dict:
        """Scrape HypeAuditor for audience quality metrics."""
        platform_map = {"instagram": "instagram", "youtube": "youtube", "tiktok": "tiktok"}
        ha_platform = platform_map.get(platform, "instagram")
        url = f"https://hypeauditor.com/{ha_platform}/{username}/"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "platform": platform,
                "username": username,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/influencer_proofs", prefix=f"hypeauditor_{platform}_{username}"
                )

            return result
        except Exception as e:
            return {"error": f"HypeAuditor scrape failed: {str(e)}"}

    async def _check_fake_followers(self, platform: str, username: str, capture: bool = True) -> dict:
        """Check for fake followers using FakeCheck."""
        # Use different fake check tools based on platform
        if platform == "instagram":
            url = f"https://www.modash.io/fake-follower-check?handle={username}"
        else:
            url = f"https://sparktoro.com/tools/fake-followers-audit?username={username}"

        try:
            await self.browser.open(url)
            await self.browser.wait(4000)  # These tools take time to analyze
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "platform": platform,
                "username": username,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/influencer_proofs", prefix=f"fake_check_{platform}_{username}"
                )

            return result
        except Exception as e:
            return {"error": f"Fake follower check failed: {str(e)}"}

    async def _scrape_feed(self, platform: str, url: str, scroll_count: int = 3) -> dict:
        """Scrape influencer feed for brand safety check."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            # Scroll to load more content
            for _ in range(scroll_count):
                await self.browser.scroll(direction="down", pixels=800)
                await self.browser.wait(1500)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(
                url=url, output_dir="/tmp/influencer_proofs", prefix=f"feed_{platform}"
            )

            return {
                "platform": platform,
                "profile_url": url,
                "scroll_count": scroll_count,
                "snapshot": snapshot.raw,
                "screenshot": screenshot_path,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Feed scrape failed: {str(e)}"}

    async def _capture_highlight(self, url: str, name: str) -> dict:
        """Capture story highlight."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            screenshot_path = await self.browser.capture_proof(
                url=url, output_dir="/tmp/influencer_proofs", prefix=f"highlight_{name}"
            )
            return {"url": url, "influencer": name, "screenshot": screenshot_path, "success": True}
        except Exception as e:
            return {"error": f"Highlight capture failed: {str(e)}"}

    async def _scrape_modash(self, query: str, platform: str = None, capture: bool = True) -> dict:
        """Scrape Modash for influencer discovery."""
        url = f"https://www.modash.io/search?query={query}"
        if platform:
            url += f"&platform={platform}"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "platform": platform,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/influencer_proofs", prefix=f"modash_{query.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"Modash scrape failed: {str(e)}"}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
