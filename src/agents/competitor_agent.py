from typing import Any, Optional
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class CompetitorAgent(BaseAgent):
    """
    Agent for competitor analysis.

    Capabilities:
    - Track competitor activity (API)
    - Analyze competitor strategies (API)
    - Compare market positioning (API)
    - Scrape Meta Ad Library (Browser)
    - Scrape SimilarWeb traffic data (Browser)
    - Capture competitor website screenshots (Browser)
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
        # Browser for competitive intelligence scraping
        session_name = f"competitor_{instance_id}" if instance_id else "competitor"
        self.browser = AgentBrowserSkill(session_name=session_name)
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
5. Provide strategic recommendations

You have browser automation to scrape competitive intelligence sources:
- Meta Ad Library for competitor ads
- SimilarWeb for traffic estimates
- Competitor websites for content analysis

Always capture screenshots as proof for client reports."""

    def _define_tools(self) -> list[dict]:
        return [
            # ===== API-Based Tools =====
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
                "description": "Get competitor activity from database.",
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
            # ===== Browser-Based Tools =====
            {
                "name": "scrape_meta_ad_library",
                "description": "Scrape Meta Ad Library for competitor's active Facebook/Instagram ads.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "competitor_name": {"type": "string", "description": "Company name to search"},
                        "country": {"type": "string", "default": "US"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["competitor_name"],
                },
            },
            {
                "name": "scrape_similarweb",
                "description": "Scrape SimilarWeb for competitor traffic estimates.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Competitor domain (e.g., competitor.com)"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["domain"],
                },
            },
            {
                "name": "scrape_competitor_website",
                "description": "Visit competitor website and capture content/screenshot.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Competitor website URL"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["url"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id

            # ===== API-Based Tools =====
            if tool_name == "add_competitor":
                response = await self.http_client.post(
                    "/api/v1/competitors",
                    json={**tool_input, "client_id": client_id}
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to add"}

            elif tool_name == "get_competitor_activity":
                response = await self.http_client.get(
                    f"/api/v1/competitors/{tool_input['competitor_id']}/activity",
                    params=tool_input
                )
                return response.json() if response.status_code == 200 else {"activity": []}

            elif tool_name == "compare_positioning":
                return {"status": "ready", "instruction": "Compare market positioning across dimensions."}

            elif tool_name == "get_market_share":
                response = await self.http_client.get(
                    "/api/v1/competitors/market-share",
                    params={**tool_input, "client_id": client_id}
                )
                return response.json() if response.status_code == 200 else {"market_share": None}

            elif tool_name == "generate_competitive_report":
                return {"status": "ready", "instruction": "Generate comprehensive competitive analysis."}

            # ===== Browser-Based Tools =====
            elif tool_name == "scrape_meta_ad_library":
                return await self._scrape_ad_library(
                    competitor=tool_input["competitor_name"],
                    country=tool_input.get("country", "US"),
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_similarweb":
                return await self._scrape_similarweb(
                    domain=tool_input["domain"],
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_competitor_website":
                return await self._scrape_website(
                    url=tool_input["url"],
                    capture=tool_input.get("capture_screenshot", True),
                )

            return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # Browser-Based Implementations
    # =========================================================================

    async def _scrape_ad_library(
        self,
        competitor: str,
        country: str = "US",
        capture: bool = True
    ) -> dict:
        """Scrape Meta Ad Library for competitor ads."""
        url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&q={competitor}&media_type=all"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)  # Let ads load

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "competitor": competitor,
                "country": country,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                screenshot_path = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/competitor_proofs",
                    prefix=f"ad_library_{competitor.replace(' ', '_')}"
                )
                result["screenshot"] = screenshot_path

            return result

        except Exception as e:
            return {"error": f"Ad Library scrape failed: {str(e)}"}

    async def _scrape_similarweb(self, domain: str, capture: bool = True) -> dict:
        """Scrape SimilarWeb for traffic data."""
        url = f"https://www.similarweb.com/website/{domain}/"

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
                screenshot_path = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/competitor_proofs",
                    prefix=f"similarweb_{domain.replace('.', '_')}"
                )
                result["screenshot"] = screenshot_path

            return result

        except Exception as e:
            return {"error": f"SimilarWeb scrape failed: {str(e)}"}

    async def _scrape_website(self, url: str, capture: bool = True) -> dict:
        """Scrape competitor website."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                screenshot_path = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/competitor_proofs",
                    prefix="competitor_site"
                )
                result["screenshot"] = screenshot_path

            return result

        except Exception as e:
            return {"error": f"Website scrape failed: {str(e)}"}

    async def close(self):
        """Cleanup resources."""
        await self.http_client.aclose()
        await self.browser.close()
