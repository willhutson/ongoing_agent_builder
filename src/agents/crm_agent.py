from typing import Any
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class CRMAgent(BaseAgent):
    """
    Agent for CRM and client relationship management with browser enrichment.

    Capabilities:
    - Manage client records and interactions (API)
    - Track client health and opportunities (API)
    - Enrich contacts from LinkedIn (Browser)
    - Scrape company websites (Browser)
    - Scrape Apollo.io for contact data (Browser)
    - Scrape ZoomInfo snippets (Browser)
    - Scrape Clearbit for company info (Browser)
    - Monitor company news and updates (Browser)
    - Capture client social presence (Browser)
    """

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, instance_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.instance_id = instance_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        session_name = f"crm_{instance_id}" if instance_id else "crm"
        self.browser = AgentBrowserSkill(session_name=session_name)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "crm_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a CRM and client relationship expert.

Your role is to optimize client relationships:
1. Maintain accurate client records
2. Track all client interactions
3. Analyze client health and satisfaction
4. Identify growth opportunities
5. Manage client communications

You have browser automation to:
- Enrich contacts from LinkedIn profiles
- Scrape company websites for info
- Search Apollo.io for contact data
- Search ZoomInfo for company info
- Look up Clearbit company data
- Monitor company social presence
- Capture company news and updates"""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "get_client", "description": "Get client information.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "include": {"type": "array", "items": {"type": "string"}}}, "required": ["client_id"]}},
            {"name": "update_client", "description": "Update client record.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "updates": {"type": "object"}}, "required": ["client_id", "updates"]}},
            {"name": "log_interaction", "description": "Log client interaction.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "type": {"type": "string", "enum": ["call", "email", "meeting", "note"]}, "summary": {"type": "string"}, "participants": {"type": "array", "items": {"type": "string"}}}, "required": ["client_id", "type", "summary"]}},
            {"name": "get_client_health", "description": "Get client health score.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}}, "required": ["client_id"]}},
            {"name": "get_opportunities", "description": "Get client opportunities.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "status": {"type": "string", "enum": ["open", "won", "lost", "all"]}}, "required": []}},
            {"name": "create_opportunity", "description": "Create new opportunity.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "name": {"type": "string"}, "value": {"type": "number"}, "probability": {"type": "number"}}, "required": ["client_id", "name"]}},
            {"name": "enrich_contact_linkedin", "description": "Enrich contact from LinkedIn.", "input_schema": {"type": "object", "properties": {"linkedin_url": {"type": "string"}, "contact_id": {"type": "string"}}, "required": ["linkedin_url"]}},
            {"name": "scrape_company_website", "description": "Scrape company website.", "input_schema": {"type": "object", "properties": {"company_url": {"type": "string"}, "pages": {"type": "array", "items": {"type": "string"}}}, "required": ["company_url"]}},
            {"name": "capture_company_news", "description": "Capture company news page.", "input_schema": {"type": "object", "properties": {"company_url": {"type": "string"}, "news_page": {"type": "string", "default": "/news"}}, "required": ["company_url"]}},
            # Extended Browser Tools
            {"name": "scrape_apollo", "description": "Search Apollo.io for contact/company data.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "search_type": {"type": "string", "enum": ["people", "companies"], "default": "people"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["query"]}},
            {"name": "scrape_zoominfo", "description": "Search ZoomInfo for company data.", "input_schema": {"type": "object", "properties": {"company_name": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["company_name"]}},
            {"name": "scrape_clearbit", "description": "Look up company on Clearbit.", "input_schema": {"type": "object", "properties": {"domain": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["domain"]}},
            {"name": "scrape_linkedin_company", "description": "Scrape LinkedIn company page.", "input_schema": {"type": "object", "properties": {"company_slug": {"type": "string"}, "include_employees": {"type": "boolean", "default": False}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["company_slug"]}},
            {"name": "capture_company_social", "description": "Capture company social media presence.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["twitter", "facebook", "instagram", "linkedin"]}, "handle": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["platform", "handle"]}},
            {"name": "scrape_hunter", "description": "Search Hunter.io for company emails.", "input_schema": {"type": "object", "properties": {"domain": {"type": "string"}, "capture_screenshot": {"type": "boolean", "default": True}}, "required": ["domain"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "get_client":
                response = await self.http_client.get(f"/api/v1/crm/clients/{tool_input['client_id']}", params={"include": ",".join(tool_input.get("include", []))})
                return response.json() if response.status_code == 200 else {"error": "Not found"}
            elif tool_name == "update_client":
                response = await self.http_client.patch(f"/api/v1/crm/clients/{tool_input['client_id']}", json=tool_input["updates"])
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            elif tool_name == "log_interaction":
                response = await self.http_client.post(f"/api/v1/crm/clients/{tool_input['client_id']}/interactions", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_client_health":
                response = await self.http_client.get(f"/api/v1/crm/clients/{tool_input['client_id']}/health")
                return response.json() if response.status_code == 200 else {"health": None}
            elif tool_name == "get_opportunities":
                response = await self.http_client.get("/api/v1/crm/opportunities", params={k: v for k, v in tool_input.items() if v})
                return response.json() if response.status_code == 200 else {"opportunities": []}
            elif tool_name == "create_opportunity":
                response = await self.http_client.post("/api/v1/crm/opportunities", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "enrich_contact_linkedin":
                return await self._enrich_linkedin(tool_input["linkedin_url"], tool_input.get("contact_id"))
            elif tool_name == "scrape_company_website":
                return await self._scrape_company(tool_input["company_url"], tool_input.get("pages", ["about"]))
            elif tool_name == "capture_company_news":
                return await self._capture_news(tool_input["company_url"], tool_input.get("news_page", "/news"))
            # Extended Browser Tools
            elif tool_name == "scrape_apollo":
                return await self._scrape_apollo(tool_input["query"], tool_input.get("search_type", "people"), tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_zoominfo":
                return await self._scrape_zoominfo(tool_input["company_name"], tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_clearbit":
                return await self._scrape_clearbit(tool_input["domain"], tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_linkedin_company":
                return await self._scrape_linkedin_company(tool_input["company_slug"], tool_input.get("include_employees", False), tool_input.get("capture_screenshot", True))
            elif tool_name == "capture_company_social":
                return await self._capture_social(tool_input["platform"], tool_input["handle"], tool_input.get("capture_screenshot", True))
            elif tool_name == "scrape_hunter":
                return await self._scrape_hunter(tool_input["domain"], tool_input.get("capture_screenshot", True))
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _enrich_linkedin(self, url: str, contact_id: str = None) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/crm_proofs", prefix="linkedin")
            return {"linkedin_url": url, "contact_id": contact_id, "snapshot": snapshot.raw, "screenshot": screenshot_path, "timestamp": snapshot.timestamp.isoformat()}
        except Exception as e:
            return {"error": str(e)}

    async def _scrape_company(self, url: str, pages: list) -> dict:
        results = []
        for page in pages:
            try:
                page_url = f"{url.rstrip('/')}/{page.lstrip('/')}"
                await self.browser.open(page_url)
                await self.browser.wait(1500)
                snapshot = await self.browser.snapshot(interactive_only=False)
                results.append({"page": page, "url": page_url, "snapshot": snapshot.raw})
            except Exception as e:
                results.append({"page": page, "error": str(e)})
        return {"company_url": url, "pages_scraped": results}

    async def _capture_news(self, url: str, news_page: str) -> dict:
        try:
            news_url = f"{url.rstrip('/')}{news_page}"
            await self.browser.open(news_url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(url=news_url, output_dir="/tmp/crm_proofs", prefix="company_news")
            return {"news_url": news_url, "snapshot": snapshot.raw, "screenshot": screenshot_path, "timestamp": snapshot.timestamp.isoformat()}
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # Extended Browser Implementations
    # =========================================================================

    async def _scrape_apollo(self, query: str, search_type: str = "people", capture: bool = True) -> dict:
        """Search Apollo.io for contact/company data."""
        url = f"https://www.apollo.io/search?q={query}&type={search_type}"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "search_type": search_type,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/crm_proofs", prefix=f"apollo_{query.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"Apollo scrape failed: {str(e)}"}

    async def _scrape_zoominfo(self, company_name: str, capture: bool = True) -> dict:
        """Search ZoomInfo for company data."""
        url = f"https://www.zoominfo.com/c/{company_name.lower().replace(' ', '-')}"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "company_name": company_name,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/crm_proofs", prefix=f"zoominfo_{company_name.replace(' ', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"ZoomInfo scrape failed: {str(e)}"}

    async def _scrape_clearbit(self, domain: str, capture: bool = True) -> dict:
        """Look up company on Clearbit."""
        url = f"https://clearbit.com/company/{domain}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "domain": domain,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/crm_proofs", prefix=f"clearbit_{domain.replace('.', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"Clearbit scrape failed: {str(e)}"}

    async def _scrape_linkedin_company(self, company_slug: str, include_employees: bool = False, capture: bool = True) -> dict:
        """Scrape LinkedIn company page."""
        url = f"https://www.linkedin.com/company/{company_slug}"
        results = {"company_slug": company_slug, "pages": {}}

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            results["pages"]["about"] = {
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }
            if capture:
                results["pages"]["about"]["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/crm_proofs", prefix=f"linkedin_{company_slug}"
                )

            if include_employees:
                emp_url = f"{url}/people"
                await self.browser.open(emp_url)
                await self.browser.wait(2000)
                emp_snapshot = await self.browser.snapshot(interactive_only=False)
                results["pages"]["employees"] = {
                    "url": emp_url,
                    "snapshot": emp_snapshot.raw,
                    "timestamp": emp_snapshot.timestamp.isoformat(),
                }

            return results
        except Exception as e:
            return {"error": f"LinkedIn company scrape failed: {str(e)}"}

    async def _capture_social(self, platform: str, handle: str, capture: bool = True) -> dict:
        """Capture company social media presence."""
        platform_urls = {
            "twitter": f"https://twitter.com/{handle}",
            "facebook": f"https://www.facebook.com/{handle}",
            "instagram": f"https://www.instagram.com/{handle}",
            "linkedin": f"https://www.linkedin.com/company/{handle}",
        }

        url = platform_urls.get(platform)
        if not url:
            return {"error": f"Unknown platform: {platform}"}

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "platform": platform,
                "handle": handle,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url, output_dir="/tmp/crm_proofs", prefix=f"social_{platform}_{handle}"
                )

            return result
        except Exception as e:
            return {"error": f"Social capture failed: {str(e)}"}

    async def _scrape_hunter(self, domain: str, capture: bool = True) -> dict:
        """Search Hunter.io for company emails."""
        url = f"https://hunter.io/search/{domain}"

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
                    url=url, output_dir="/tmp/crm_proofs", prefix=f"hunter_{domain.replace('.', '_')}"
                )

            return result
        except Exception as e:
            return {"error": f"Hunter.io scrape failed: {str(e)}"}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
