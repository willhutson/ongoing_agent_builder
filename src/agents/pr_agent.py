from typing import Any
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class PRAgent(BaseAgent):
    """
    Agent for public relations and media relations with coverage capture.

    Capabilities:
    - Create and distribute press releases (API)
    - Track media coverage (API)
    - Calculate AVR/ad value equivalent (API)
    - Capture press coverage screenshots (Browser)
    - Save articles as PDF (Browser)
    - Scrape Google News for mentions (Browser)
    - Scrape PR Newswire releases (Browser)
    - Scrape Business Wire releases (Browser)
    - Monitor industry publications (Browser)
    - Track competitor press coverage (Browser)
    """

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, client_id: str = None, instance_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.instance_id = instance_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        session_name = f"pr_{instance_id}" if instance_id else "pr"
        self.browser = AgentBrowserSkill(session_name=session_name)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "pr_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a PR and media relations expert. Manage press releases, media outreach, and coverage.

You have browser automation to:
- Capture press coverage and media mentions as proof
- Save articles as PDF for archives
- Scrape Google News for brand mentions
- Monitor PR Newswire and Business Wire for releases
- Track industry publications (TechCrunch, Forbes, etc.)
- Monitor competitor press coverage"""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "create_press_release", "description": "Create press release.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "embargo_date": {"type": "string"}}, "required": ["title", "content"]}},
            {"name": "get_media_list", "description": "Get media contacts list.", "input_schema": {"type": "object", "properties": {"beat": {"type": "string"}, "region": {"type": "string"}}, "required": []}},
            {"name": "distribute_release", "description": "Distribute press release.", "input_schema": {"type": "object", "properties": {"release_id": {"type": "string"}, "media_list_id": {"type": "string"}}, "required": ["release_id"]}},
            {"name": "track_coverage", "description": "Track media coverage.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "date_range": {"type": "object"}}, "required": []}},
            {"name": "calculate_avr", "description": "Calculate ad value equivalent.", "input_schema": {"type": "object", "properties": {"coverage_ids": {"type": "array", "items": {"type": "string"}}}, "required": ["coverage_ids"]}},
            {"name": "create_media_kit", "description": "Create media kit.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "include": {"type": "array", "items": {"type": "string"}}}, "required": []}},
            {"name": "capture_press_coverage", "description": "Screenshot press article.", "input_schema": {"type": "object", "properties": {"article_url": {"type": "string"}, "publication": {"type": "string"}}, "required": ["article_url"]}},
            {"name": "capture_media_mention", "description": "Screenshot media mention.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "mention_type": {"type": "string"}}, "required": ["url"]}},
            {"name": "save_article_pdf", "description": "Save article as PDF.", "input_schema": {"type": "object", "properties": {"article_url": {"type": "string"}, "article_name": {"type": "string"}}, "required": ["article_url", "article_name"]}},
            # Extended Browser Tools
            {"name": "scrape_google_news", "description": "Scrape Google News for brand/company mentions.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "time_range": {"type": "string", "enum": ["hour", "day", "week", "month"], "default": "week"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["query"]}},
            {"name": "scrape_pr_newswire", "description": "Scrape PR Newswire for press releases.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "industry": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["query"]}},
            {"name": "scrape_business_wire", "description": "Scrape Business Wire for press releases.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["query"]}},
            {"name": "scrape_techcrunch", "description": "Scrape TechCrunch for tech industry coverage.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["query"]}},
            {"name": "scrape_industry_publication", "description": "Scrape industry publication for coverage.", "input_schema": {"type": "object", "properties": {"publication": {"type": "string", "enum": ["techcrunch", "forbes", "bloomberg", "wsj", "reuters", "adweek", "adage"]}, "query": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["publication", "query"]}},
            {"name": "monitor_competitor_press", "description": "Monitor competitor press coverage.", "input_schema": {"type": "object", "properties": {"competitor_name": {"type": "string"}, "time_range": {"type": "string", "enum": ["day", "week", "month"], "default": "week"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["competitor_name"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id
            if tool_name == "create_press_release":
                response = await self.http_client.post("/api/v1/pr/releases", json={**tool_input, "client_id": client_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_media_list":
                response = await self.http_client.get("/api/v1/pr/media-lists", params=tool_input)
                return response.json() if response.status_code == 200 else {"contacts": []}
            elif tool_name == "distribute_release":
                response = await self.http_client.post(f"/api/v1/pr/releases/{tool_input['release_id']}/distribute", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            elif tool_name == "track_coverage":
                response = await self.http_client.get("/api/v1/pr/coverage", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"coverage": []}
            elif tool_name == "calculate_avr":
                response = await self.http_client.post("/api/v1/pr/coverage/avr", json=tool_input)
                return response.json() if response.status_code == 200 else {"avr": None}
            elif tool_name == "create_media_kit":
                return {"status": "ready_to_create", "instruction": "Create comprehensive media kit."}
            elif tool_name == "capture_press_coverage":
                return await self._capture_coverage(tool_input["article_url"], tool_input.get("publication", "article"))
            elif tool_name == "capture_media_mention":
                return await self._capture_mention(tool_input["url"], tool_input.get("mention_type", "mention"))
            elif tool_name == "save_article_pdf":
                return await self._save_pdf(tool_input["article_url"], tool_input["article_name"])
            # Extended Browser Tools
            elif tool_name == "scrape_google_news":
                return await self._scrape_google_news(tool_input["query"], tool_input.get("time_range", "week"), tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_pr_newswire":
                return await self._scrape_pr_newswire(tool_input["query"], tool_input.get("industry"), tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_business_wire":
                return await self._scrape_business_wire(tool_input["query"], tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_techcrunch":
                return await self._scrape_publication("techcrunch", tool_input["query"], tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_industry_publication":
                return await self._scrape_publication(tool_input["publication"], tool_input["query"], tool_input.get("capture_screenshot", True))
            elif tool_name == "monitor_competitor_press":
                return await self._monitor_competitor_press(tool_input["competitor_name"], tool_input.get("time_range", "week"), tool_input.get("capture_screenshot", True))
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_coverage(self, url: str, publication: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/pr_proofs", prefix=f"coverage_{publication}")
            return {"url": url, "publication": publication, "snapshot": snapshot.raw, "screenshot": screenshot_path, "timestamp": snapshot.timestamp.isoformat()}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_mention(self, url: str, mention_type: str) -> dict:
        try:
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/pr_proofs", prefix=f"mention_{mention_type}")
            return {"url": url, "mention_type": mention_type, "screenshot": screenshot_path, "success": True}
        except Exception as e:
            return {"error": str(e)}

    async def _save_pdf(self, url: str, name: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            pdf_path = f"/tmp/pr_proofs/{name}.pdf"
            await self.browser.pdf(pdf_path)
            return {"url": url, "pdf_path": pdf_path, "success": True}
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # Extended Browser Implementations
    # =========================================================================

    async def _scrape_google_news(self, query: str, time_range: str = "week", capture: bool = True) -> dict:
        """Scrape Google News for brand mentions."""
        time_map = {"hour": "qdr:h", "day": "qdr:d", "week": "qdr:w", "month": "qdr:m"}
        tbs = time_map.get(time_range, "qdr:w")
        url = f"https://www.google.com/search?q={query}&tbm=nws&tbs={tbs}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "time_range": time_range,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/pr_proofs", prefix=f"google_news_{query.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"Google News scrape failed: {str(e)}"}

    async def _scrape_pr_newswire(self, query: str, industry: str = None, capture: bool = True) -> dict:
        """Scrape PR Newswire for press releases."""
        url = f"https://www.prnewswire.com/search/news/?keyword={query}"
        if industry:
            url += f"&industrysearch={industry}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "industry": industry,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/pr_proofs", prefix=f"prnewswire_{query.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"PR Newswire scrape failed: {str(e)}"}

    async def _scrape_business_wire(self, query: str, capture: bool = True) -> dict:
        """Scrape Business Wire for press releases."""
        url = f"https://www.businesswire.com/portal/site/home/search/?searchTerm={query}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/pr_proofs", prefix=f"businesswire_{query.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"Business Wire scrape failed: {str(e)}"}

    async def _scrape_publication(self, publication: str, query: str, capture: bool = True) -> dict:
        """Scrape industry publication for coverage."""
        publication_urls = {
            "techcrunch": f"https://techcrunch.com/search/{query}",
            "forbes": f"https://www.forbes.com/search/?q={query}",
            "bloomberg": f"https://www.bloomberg.com/search?query={query}",
            "wsj": f"https://www.wsj.com/search?query={query}",
            "reuters": f"https://www.reuters.com/search/news?blob={query}",
            "adweek": f"https://www.adweek.com/?s={query}",
            "adage": f"https://adage.com/search?search_api_fulltext={query}",
        }

        url = publication_urls.get(publication)
        if not url:
            return {"error": f"Unknown publication: {publication}"}

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "publication": publication,
                "query": query,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/pr_proofs", prefix=f"{publication}_{query.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"{publication} scrape failed: {str(e)}"}

    async def _monitor_competitor_press(self, competitor: str, time_range: str = "week", capture: bool = True) -> dict:
        """Monitor competitor press coverage via Google News."""
        time_map = {"day": "qdr:d", "week": "qdr:w", "month": "qdr:m"}
        tbs = time_map.get(time_range, "qdr:w")
        url = f"https://www.google.com/search?q={competitor}&tbm=nws&tbs={tbs}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "competitor": competitor,
                "time_range": time_range,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/pr_proofs", prefix=f"competitor_{competitor.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"Competitor press monitoring failed: {str(e)}"}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
