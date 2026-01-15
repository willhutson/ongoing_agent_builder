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
    - Scrape LinkedIn company pages (Browser)
    - Scrape Glassdoor reviews (Browser)
    - Scrape Crunchbase funding data (Browser)
    - Scrape G2 software reviews (Browser)
    - Scrape Trustpilot reviews (Browser)
    - Scrape Google Trends data (Browser)
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
- LinkedIn company pages for employee counts, updates, job postings
- Glassdoor for employee reviews, ratings, salary data
- Crunchbase for funding rounds, investors, company info
- G2 for software reviews and comparisons
- Trustpilot for customer reviews and ratings
- Google Trends for search interest over time

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
            {
                "name": "scrape_linkedin_company",
                "description": "Scrape LinkedIn company page for employee count, recent posts, job openings.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "company_slug": {"type": "string", "description": "LinkedIn company slug (e.g., 'microsoft' from linkedin.com/company/microsoft)"},
                        "include_jobs": {"type": "boolean", "default": True, "description": "Also scrape jobs page"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["company_slug"],
                },
            },
            {
                "name": "scrape_glassdoor",
                "description": "Scrape Glassdoor for company reviews, ratings, and salary data.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "company_name": {"type": "string", "description": "Company name to search"},
                        "include_reviews": {"type": "boolean", "default": True},
                        "include_salaries": {"type": "boolean", "default": False},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["company_name"],
                },
            },
            {
                "name": "scrape_crunchbase",
                "description": "Scrape Crunchbase for funding rounds, investors, and company data.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "company_slug": {"type": "string", "description": "Crunchbase company slug"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["company_slug"],
                },
            },
            {
                "name": "scrape_g2_reviews",
                "description": "Scrape G2 for software product reviews and comparisons.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "product_slug": {"type": "string", "description": "G2 product slug (e.g., 'slack' from g2.com/products/slack)"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["product_slug"],
                },
            },
            {
                "name": "scrape_trustpilot",
                "description": "Scrape Trustpilot for customer reviews and ratings.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Company domain (e.g., 'amazon.com')"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["domain"],
                },
            },
            {
                "name": "scrape_google_trends",
                "description": "Scrape Google Trends for search interest comparison.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "array", "items": {"type": "string"}, "description": "Keywords to compare (max 5)"},
                        "timeframe": {"type": "string", "enum": ["past_hour", "past_day", "past_week", "past_month", "past_year", "past_5_years"], "default": "past_year"},
                        "geo": {"type": "string", "default": "US", "description": "Country code"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["keywords"],
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

            elif tool_name == "scrape_linkedin_company":
                return await self._scrape_linkedin_company(
                    company_slug=tool_input["company_slug"],
                    include_jobs=tool_input.get("include_jobs", True),
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_glassdoor":
                return await self._scrape_glassdoor(
                    company_name=tool_input["company_name"],
                    include_reviews=tool_input.get("include_reviews", True),
                    include_salaries=tool_input.get("include_salaries", False),
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_crunchbase":
                return await self._scrape_crunchbase(
                    company_slug=tool_input["company_slug"],
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_g2_reviews":
                return await self._scrape_g2(
                    product_slug=tool_input["product_slug"],
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_trustpilot":
                return await self._scrape_trustpilot(
                    domain=tool_input["domain"],
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_google_trends":
                return await self._scrape_google_trends(
                    keywords=tool_input["keywords"],
                    timeframe=tool_input.get("timeframe", "past_year"),
                    geo=tool_input.get("geo", "US"),
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

    async def _scrape_linkedin_company(
        self,
        company_slug: str,
        include_jobs: bool = True,
        capture: bool = True
    ) -> dict:
        """Scrape LinkedIn company page for employee count, posts, job openings."""
        base_url = f"https://www.linkedin.com/company/{company_slug}"
        results = {"company_slug": company_slug, "pages": {}}

        try:
            # Main company page
            await self.browser.open(base_url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            results["pages"]["about"] = {
                "url": base_url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }
            if capture:
                results["pages"]["about"]["screenshot"] = await self.browser.capture_proof(
                    url=base_url,
                    output_dir="/tmp/competitor_proofs",
                    prefix=f"linkedin_{company_slug}_about"
                )

            # Jobs page if requested
            if include_jobs:
                jobs_url = f"{base_url}/jobs"
                await self.browser.open(jobs_url)
                await self.browser.wait(2000)
                jobs_snapshot = await self.browser.snapshot(interactive_only=False)
                results["pages"]["jobs"] = {
                    "url": jobs_url,
                    "snapshot": jobs_snapshot.raw,
                    "timestamp": jobs_snapshot.timestamp.isoformat(),
                }
                if capture:
                    results["pages"]["jobs"]["screenshot"] = await self.browser.capture_proof(
                        url=jobs_url,
                        output_dir="/tmp/competitor_proofs",
                        prefix=f"linkedin_{company_slug}_jobs"
                    )

            return results

        except Exception as e:
            return {"error": f"LinkedIn scrape failed: {str(e)}"}

    async def _scrape_glassdoor(
        self,
        company_name: str,
        include_reviews: bool = True,
        include_salaries: bool = False,
        capture: bool = True
    ) -> dict:
        """Scrape Glassdoor for company reviews and ratings."""
        search_url = f"https://www.glassdoor.com/Search/results.htm?keyword={company_name.replace(' ', '%20')}"

        try:
            await self.browser.open(search_url)
            await self.browser.wait(3000)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "company_name": company_name,
                "search_url": search_url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=search_url,
                    output_dir="/tmp/competitor_proofs",
                    prefix=f"glassdoor_{company_name.replace(' ', '_')}"
                )

            return result

        except Exception as e:
            return {"error": f"Glassdoor scrape failed: {str(e)}"}

    async def _scrape_crunchbase(self, company_slug: str, capture: bool = True) -> dict:
        """Scrape Crunchbase for funding and company data."""
        url = f"https://www.crunchbase.com/organization/{company_slug}"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "company_slug": company_slug,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/competitor_proofs",
                    prefix=f"crunchbase_{company_slug}"
                )

            return result

        except Exception as e:
            return {"error": f"Crunchbase scrape failed: {str(e)}"}

    async def _scrape_g2(self, product_slug: str, capture: bool = True) -> dict:
        """Scrape G2 for software reviews."""
        url = f"https://www.g2.com/products/{product_slug}/reviews"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "product_slug": product_slug,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/competitor_proofs",
                    prefix=f"g2_{product_slug}"
                )

            return result

        except Exception as e:
            return {"error": f"G2 scrape failed: {str(e)}"}

    async def _scrape_trustpilot(self, domain: str, capture: bool = True) -> dict:
        """Scrape Trustpilot for customer reviews."""
        url = f"https://www.trustpilot.com/review/{domain}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "domain": domain,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/competitor_proofs",
                    prefix=f"trustpilot_{domain.replace('.', '_')}"
                )

            return result

        except Exception as e:
            return {"error": f"Trustpilot scrape failed: {str(e)}"}

    async def _scrape_google_trends(
        self,
        keywords: list,
        timeframe: str = "past_year",
        geo: str = "US",
        capture: bool = True
    ) -> dict:
        """Scrape Google Trends for search interest comparison."""
        # Map timeframe to Google Trends format
        timeframe_map = {
            "past_hour": "now%201-H",
            "past_day": "now%201-d",
            "past_week": "now%207-d",
            "past_month": "today%201-m",
            "past_year": "today%2012-m",
            "past_5_years": "today%205-y",
        }
        tf = timeframe_map.get(timeframe, "today%2012-m")

        # Build URL with keywords (max 5)
        kw_param = ",".join(keywords[:5])
        url = f"https://trends.google.com/trends/explore?date={tf}&geo={geo}&q={kw_param}"

        try:
            await self.browser.open(url)
            await self.browser.wait(4000)  # Charts need time to render

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "keywords": keywords[:5],
                "timeframe": timeframe,
                "geo": geo,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/competitor_proofs",
                    prefix=f"trends_{'_'.join(keywords[:3])}"
                )

            return result

        except Exception as e:
            return {"error": f"Google Trends scrape failed: {str(e)}"}

    async def close(self):
        """Cleanup resources."""
        await self.http_client.aclose()
        await self.browser.close()
