from typing import Any
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class ReportAgent(BaseAgent):
    """
    Agent for generating, capturing, and distributing reports with comprehensive analytics integration.

    Capabilities:
    - Generate and format reports (API)
    - Send reports via multiple channels (API)
    - Schedule recurring reports (API)
    - Capture generic analytics dashboards (Browser)
    - Capture Google Analytics 4 dashboards (Browser)
    - Capture Google Ads performance reports (Browser)
    - Capture Facebook Ads Manager dashboards (Browser)
    - Capture LinkedIn Campaign Manager reports (Browser)
    - Capture Google Search Console data (Browser)
    - Capture Tableau dashboards (Browser)
    - Capture PowerBI reports (Browser)
    - Capture Salesforce dashboards (Browser)
    - Capture HubSpot analytics (Browser)
    - Capture Looker Studio reports (Browser)
    - Capture social media platform analytics (Browser)
    - Generate PDF reports from dashboards (Browser)
    - Capture multi-dashboard comparisons (Browser)
    """

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, language: str = "en", client_id: str = None, instance_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.language = language
        self.client_specific_id = client_id
        self.instance_id = instance_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        session_name = f"report_{instance_id}" if instance_id else "report"
        self.browser = AgentBrowserSkill(session_name=session_name)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "report_agent"

    @property
    def system_prompt(self) -> str:
        prompt = """You are an expert report generator and data visualization specialist for marketing agencies.

Your role is to create comprehensive reports:
1. Capture analytics dashboards as visual proof
2. Generate formatted reports for clients
3. Distribute reports via multiple channels
4. Schedule automated recurring reports
5. Compare performance across platforms

You have browser automation to:
- Capture Google Analytics 4 dashboards
- Capture Google Ads and Facebook Ads Manager
- Capture LinkedIn Campaign Manager reports
- Capture Search Console performance data
- Capture Tableau, PowerBI, and Looker dashboards
- Capture Salesforce and HubSpot reports
- Capture social media platform analytics
- Generate PDF reports from any dashboard
- Capture multi-platform comparison views"""
        if self.language != "en":
            prompt += f"\n\nPrimary language: {self.language}"
        return prompt

    def _define_tools(self) -> list[dict]:
        return [
            # API Tools
            {"name": "generate_report", "description": "Generate report.", "input_schema": {"type": "object", "properties": {"report_type": {"type": "string", "enum": ["project_status", "campaign", "client_summary", "resource", "budget", "milestone", "risk"]}, "project_id": {"type": "string"}, "client_id": {"type": "string"}, "date_range": {"type": "object"}, "compare_to": {"type": "string", "enum": ["previous_period", "last_year", "target"]}}, "required": ["report_type"]}},
            {"name": "format_for_channel", "description": "Format report for channel.", "input_schema": {"type": "object", "properties": {"report_id": {"type": "string"}, "report_content": {"type": "object"}, "channel": {"type": "string", "enum": ["whatsapp", "email", "slack", "sms"]}, "include_charts": {"type": "boolean", "default": True}}, "required": ["channel"]}},
            {"name": "send_report", "description": "Send report via gateway.", "input_schema": {"type": "object", "properties": {"report_id": {"type": "string"}, "formatted_content": {"type": "object"}, "channel": {"type": "string", "enum": ["whatsapp", "email", "slack", "sms"]}, "recipients": {"type": "array", "items": {"type": "string"}}, "schedule": {"type": "string"}}, "required": ["channel", "recipients"]}},
            {"name": "get_project_data", "description": "Fetch project data.", "input_schema": {"type": "object", "properties": {"project_id": {"type": "string"}, "include": {"type": "array", "items": {"type": "string"}}}, "required": ["project_id"]}},
            {"name": "get_campaign_metrics", "description": "Fetch campaign metrics.", "input_schema": {"type": "object", "properties": {"campaign_id": {"type": "string"}, "project_id": {"type": "string"}, "metrics": {"type": "array", "items": {"type": "string"}}}, "required": []}},
            {"name": "schedule_recurring", "description": "Schedule recurring report.", "input_schema": {"type": "object", "properties": {"report_config": {"type": "object"}, "frequency": {"type": "string", "enum": ["daily", "weekly", "biweekly", "monthly"]}, "day_of_week": {"type": "integer"}, "time": {"type": "string"}, "channel": {"type": "string", "enum": ["whatsapp", "email", "slack", "sms"]}, "recipients": {"type": "array", "items": {"type": "string"}}}, "required": ["report_config", "frequency", "channel", "recipients"]}},
            {"name": "save_report", "description": "Save report.", "input_schema": {"type": "object", "properties": {"report_id": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "object"}, "report_type": {"type": "string"}, "project_id": {"type": "string"}, "client_id": {"type": "string"}}, "required": ["title", "content", "report_type"]}},
            # Core Browser Tools
            {"name": "capture_analytics_dashboard", "description": "Screenshot analytics dashboard.", "input_schema": {"type": "object", "properties": {"dashboard_url": {"type": "string"}, "report_name": {"type": "string"}}, "required": ["dashboard_url"]}},
            {"name": "capture_platform_stats", "description": "Screenshot platform stats page.", "input_schema": {"type": "object", "properties": {"platform_url": {"type": "string"}, "platform": {"type": "string"}}, "required": ["platform_url"]}},
            # Extended Browser Tools - Google Analytics
            {"name": "capture_ga4_dashboard", "description": "Capture Google Analytics 4 dashboard.", "input_schema": {"type": "object", "properties": {"property_id": {"type": "string"}, "report_type": {"type": "string", "enum": ["overview", "realtime", "acquisition", "engagement", "monetization", "retention", "demographics"], "default": "overview"}, "date_range": {"type": "string", "enum": ["today", "yesterday", "7days", "28days", "90days", "custom"], "default": "28days"}}, "required": ["property_id"]}},
            {"name": "capture_ga4_custom_report", "description": "Capture custom GA4 exploration report.", "input_schema": {"type": "object", "properties": {"report_url": {"type": "string"}, "report_name": {"type": "string"}}, "required": ["report_url"]}},
            # Extended Browser Tools - Google Ads
            {"name": "capture_google_ads_dashboard", "description": "Capture Google Ads dashboard.", "input_schema": {"type": "object", "properties": {"account_id": {"type": "string"}, "view": {"type": "string", "enum": ["overview", "campaigns", "ad_groups", "ads", "keywords", "audiences"], "default": "overview"}, "date_range": {"type": "string", "enum": ["today", "yesterday", "7days", "30days", "this_month", "last_month"], "default": "30days"}}, "required": ["account_id"]}},
            {"name": "capture_google_ads_campaign", "description": "Capture specific Google Ads campaign performance.", "input_schema": {"type": "object", "properties": {"campaign_url": {"type": "string"}, "campaign_name": {"type": "string"}}, "required": ["campaign_url"]}},
            # Extended Browser Tools - Facebook Ads
            {"name": "capture_facebook_ads_manager", "description": "Capture Facebook Ads Manager dashboard.", "input_schema": {"type": "object", "properties": {"account_id": {"type": "string"}, "view": {"type": "string", "enum": ["campaigns", "ad_sets", "ads", "account_overview"], "default": "campaigns"}, "date_range": {"type": "string", "enum": ["today", "yesterday", "last_7_days", "last_14_days", "last_30_days", "this_month"], "default": "last_30_days"}}, "required": ["account_id"]}},
            {"name": "capture_meta_business_suite", "description": "Capture Meta Business Suite insights.", "input_schema": {"type": "object", "properties": {"page_id": {"type": "string"}, "section": {"type": "string", "enum": ["overview", "content", "audience", "ads"], "default": "overview"}}, "required": ["page_id"]}},
            # Extended Browser Tools - LinkedIn
            {"name": "capture_linkedin_campaign_manager", "description": "Capture LinkedIn Campaign Manager dashboard.", "input_schema": {"type": "object", "properties": {"account_id": {"type": "string"}, "view": {"type": "string", "enum": ["campaigns", "demographics", "website_demographics", "account_assets"], "default": "campaigns"}}, "required": ["account_id"]}},
            {"name": "capture_linkedin_analytics", "description": "Capture LinkedIn Page analytics.", "input_schema": {"type": "object", "properties": {"page_url": {"type": "string"}, "section": {"type": "string", "enum": ["visitors", "followers", "content", "leads"], "default": "visitors"}}, "required": ["page_url"]}},
            # Extended Browser Tools - Google Search Console
            {"name": "capture_search_console", "description": "Capture Google Search Console performance.", "input_schema": {"type": "object", "properties": {"property_url": {"type": "string"}, "report_type": {"type": "string", "enum": ["performance", "coverage", "experience", "enhancements"], "default": "performance"}, "date_range": {"type": "string", "enum": ["7days", "28days", "3months", "6months", "16months"], "default": "28days"}}, "required": ["property_url"]}},
            # Extended Browser Tools - BI Platforms
            {"name": "capture_tableau_dashboard", "description": "Capture Tableau dashboard.", "input_schema": {"type": "object", "properties": {"dashboard_url": {"type": "string"}, "dashboard_name": {"type": "string"}, "wait_for_load": {"type": "integer", "default": 8000}}, "required": ["dashboard_url"]}},
            {"name": "capture_powerbi_report", "description": "Capture PowerBI report.", "input_schema": {"type": "object", "properties": {"report_url": {"type": "string"}, "report_name": {"type": "string"}, "wait_for_load": {"type": "integer", "default": 8000}}, "required": ["report_url"]}},
            {"name": "capture_looker_dashboard", "description": "Capture Looker Studio (Data Studio) dashboard.", "input_schema": {"type": "object", "properties": {"dashboard_url": {"type": "string"}, "dashboard_name": {"type": "string"}}, "required": ["dashboard_url"]}},
            # Extended Browser Tools - CRM Platforms
            {"name": "capture_salesforce_dashboard", "description": "Capture Salesforce dashboard.", "input_schema": {"type": "object", "properties": {"dashboard_url": {"type": "string"}, "dashboard_name": {"type": "string"}}, "required": ["dashboard_url"]}},
            {"name": "capture_hubspot_analytics", "description": "Capture HubSpot analytics dashboard.", "input_schema": {"type": "object", "properties": {"portal_id": {"type": "string"}, "report_type": {"type": "string", "enum": ["marketing", "sales", "service", "website", "custom"], "default": "marketing"}}, "required": ["portal_id"]}},
            # Extended Browser Tools - Social Media Analytics
            {"name": "capture_instagram_insights", "description": "Capture Instagram Insights (via Meta Business Suite).", "input_schema": {"type": "object", "properties": {"account_url": {"type": "string"}, "section": {"type": "string", "enum": ["overview", "accounts_reached", "content_interactions", "followers"], "default": "overview"}}, "required": ["account_url"]}},
            {"name": "capture_tiktok_analytics", "description": "Capture TikTok Analytics dashboard.", "input_schema": {"type": "object", "properties": {"account_url": {"type": "string"}, "section": {"type": "string", "enum": ["overview", "content", "followers", "live"], "default": "overview"}}, "required": ["account_url"]}},
            {"name": "capture_twitter_analytics", "description": "Capture Twitter/X Analytics dashboard.", "input_schema": {"type": "object", "properties": {"account_url": {"type": "string"}, "section": {"type": "string", "enum": ["home", "tweets", "audiences", "events"], "default": "home"}}, "required": ["account_url"]}},
            {"name": "capture_youtube_studio", "description": "Capture YouTube Studio analytics.", "input_schema": {"type": "object", "properties": {"channel_url": {"type": "string"}, "section": {"type": "string", "enum": ["overview", "content", "analytics", "audience", "revenue"], "default": "analytics"}}, "required": ["channel_url"]}},
            # Extended Browser Tools - Report Generation
            {"name": "generate_dashboard_pdf", "description": "Generate PDF from dashboard URL.", "input_schema": {"type": "object", "properties": {"dashboard_url": {"type": "string"}, "pdf_name": {"type": "string"}, "wait_for_load": {"type": "integer", "default": 5000}}, "required": ["dashboard_url", "pdf_name"]}},
            {"name": "capture_multi_dashboard", "description": "Capture multiple dashboards for comparison report.", "input_schema": {"type": "object", "properties": {"dashboard_urls": {"type": "array", "items": {"type": "string"}, "maxItems": 6}, "report_name": {"type": "string"}}, "required": ["dashboard_urls", "report_name"]}},
            {"name": "capture_with_date_selector", "description": "Capture dashboard after setting custom date range.", "input_schema": {"type": "object", "properties": {"dashboard_url": {"type": "string"}, "start_date": {"type": "string"}, "end_date": {"type": "string"}, "report_name": {"type": "string"}}, "required": ["dashboard_url", "report_name"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            # API Tools
            if tool_name == "generate_report":
                return {"status": "ready_to_generate", "report_type": tool_input["report_type"], "language": self.language}
            elif tool_name == "format_for_channel":
                return {"status": "ready_to_format", "channel": tool_input["channel"]}
            elif tool_name == "send_report":
                response = await self.http_client.post(f"/api/v1/gateways/{tool_input['channel']}/send", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_project_data":
                response = await self.http_client.get(f"/api/v1/projects/{tool_input['project_id']}", params={"include": ",".join(tool_input.get("include", []))})
                return response.json() if response.status_code == 200 else {"error": "Not found"}
            elif tool_name == "get_campaign_metrics":
                if tool_input.get("campaign_id"):
                    response = await self.http_client.get(f"/api/v1/campaigns/{tool_input['campaign_id']}/metrics")
                else:
                    response = await self.http_client.get(f"/api/v1/projects/{tool_input.get('project_id')}/campaigns/metrics")
                return response.json() if response.status_code == 200 else {"metrics": None}
            elif tool_name == "schedule_recurring":
                response = await self.http_client.post("/api/v1/reporting/schedules", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "save_report":
                response = await self.http_client.post("/api/v1/reporting/reports", json={**tool_input, "client_id": tool_input.get("client_id") or self.client_specific_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            # Core Browser Tools
            elif tool_name == "capture_analytics_dashboard":
                return await self._capture_dashboard(tool_input["dashboard_url"], tool_input.get("report_name", "analytics"))
            elif tool_name == "capture_platform_stats":
                return await self._capture_platform(tool_input["platform_url"], tool_input.get("platform", "platform"))
            # Extended Browser Tools - Google Analytics
            elif tool_name == "capture_ga4_dashboard":
                return await self._capture_ga4(tool_input["property_id"], tool_input.get("report_type", "overview"), tool_input.get("date_range", "28days"))
            elif tool_name == "capture_ga4_custom_report":
                return await self._capture_ga4_custom(tool_input["report_url"], tool_input.get("report_name", "custom_report"))
            # Extended Browser Tools - Google Ads
            elif tool_name == "capture_google_ads_dashboard":
                return await self._capture_google_ads(tool_input["account_id"], tool_input.get("view", "overview"), tool_input.get("date_range", "30days"))
            elif tool_name == "capture_google_ads_campaign":
                return await self._capture_google_ads_campaign(tool_input["campaign_url"], tool_input.get("campaign_name", "campaign"))
            # Extended Browser Tools - Facebook Ads
            elif tool_name == "capture_facebook_ads_manager":
                return await self._capture_facebook_ads(tool_input["account_id"], tool_input.get("view", "campaigns"), tool_input.get("date_range", "last_30_days"))
            elif tool_name == "capture_meta_business_suite":
                return await self._capture_meta_suite(tool_input["page_id"], tool_input.get("section", "overview"))
            # Extended Browser Tools - LinkedIn
            elif tool_name == "capture_linkedin_campaign_manager":
                return await self._capture_linkedin_campaigns(tool_input["account_id"], tool_input.get("view", "campaigns"))
            elif tool_name == "capture_linkedin_analytics":
                return await self._capture_linkedin_analytics(tool_input["page_url"], tool_input.get("section", "visitors"))
            # Extended Browser Tools - Google Search Console
            elif tool_name == "capture_search_console":
                return await self._capture_search_console(tool_input["property_url"], tool_input.get("report_type", "performance"), tool_input.get("date_range", "28days"))
            # Extended Browser Tools - BI Platforms
            elif tool_name == "capture_tableau_dashboard":
                return await self._capture_tableau(tool_input["dashboard_url"], tool_input.get("dashboard_name", "tableau"), tool_input.get("wait_for_load", 8000))
            elif tool_name == "capture_powerbi_report":
                return await self._capture_powerbi(tool_input["report_url"], tool_input.get("report_name", "powerbi"), tool_input.get("wait_for_load", 8000))
            elif tool_name == "capture_looker_dashboard":
                return await self._capture_looker(tool_input["dashboard_url"], tool_input.get("dashboard_name", "looker"))
            # Extended Browser Tools - CRM Platforms
            elif tool_name == "capture_salesforce_dashboard":
                return await self._capture_salesforce(tool_input["dashboard_url"], tool_input.get("dashboard_name", "salesforce"))
            elif tool_name == "capture_hubspot_analytics":
                return await self._capture_hubspot(tool_input["portal_id"], tool_input.get("report_type", "marketing"))
            # Extended Browser Tools - Social Media Analytics
            elif tool_name == "capture_instagram_insights":
                return await self._capture_instagram(tool_input["account_url"], tool_input.get("section", "overview"))
            elif tool_name == "capture_tiktok_analytics":
                return await self._capture_tiktok(tool_input["account_url"], tool_input.get("section", "overview"))
            elif tool_name == "capture_twitter_analytics":
                return await self._capture_twitter(tool_input["account_url"], tool_input.get("section", "home"))
            elif tool_name == "capture_youtube_studio":
                return await self._capture_youtube(tool_input["channel_url"], tool_input.get("section", "analytics"))
            # Extended Browser Tools - Report Generation
            elif tool_name == "generate_dashboard_pdf":
                return await self._generate_pdf(tool_input["dashboard_url"], tool_input["pdf_name"], tool_input.get("wait_for_load", 5000))
            elif tool_name == "capture_multi_dashboard":
                return await self._capture_multi(tool_input["dashboard_urls"], tool_input["report_name"])
            elif tool_name == "capture_with_date_selector":
                return await self._capture_with_dates(tool_input["dashboard_url"], tool_input.get("start_date"), tool_input.get("end_date"), tool_input["report_name"])
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_dashboard(self, url: str, name: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(5000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"dashboard_{name}")
            return {"url": url, "screenshot": screenshot_path, "snapshot": snapshot.raw, "timestamp": snapshot.timestamp.isoformat()}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_platform(self, url: str, platform: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"stats_{platform}")
            return {"url": url, "platform": platform, "screenshot": screenshot_path, "snapshot": snapshot.raw, "timestamp": snapshot.timestamp.isoformat()}
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # Extended Browser Implementations - Google Analytics
    # =========================================================================

    async def _capture_ga4(self, property_id: str, report_type: str = "overview", date_range: str = "28days") -> dict:
        """Capture Google Analytics 4 dashboard."""
        report_paths = {
            "overview": "reports/dashboard",
            "realtime": "reports/realtime/overview",
            "acquisition": "reports/acquisition-traffic-acquisition-overview",
            "engagement": "reports/engagement-overview",
            "monetization": "reports/monetization-overview",
            "retention": "reports/retention-overview",
            "demographics": "reports/user-attributes-overview",
        }
        path = report_paths.get(report_type, "reports/dashboard")
        url = f"https://analytics.google.com/analytics/web/#/p{property_id}/{path}"

        try:
            await self.browser.open(url)
            await self.browser.wait(6000)  # GA4 loads slowly
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"ga4_{report_type}")

            return {
                "property_id": property_id,
                "report_type": report_type,
                "date_range": date_range,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"GA4 capture failed: {str(e)}"}

    async def _capture_ga4_custom(self, report_url: str, report_name: str = "custom") -> dict:
        """Capture custom GA4 exploration report."""
        try:
            await self.browser.open(report_url)
            await self.browser.wait(7000)  # Explorations load slowly
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=report_url, output_dir="/tmp/report_proofs", prefix=f"ga4_custom_{report_name}")

            return {
                "report_name": report_name,
                "url": report_url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"GA4 custom report capture failed: {str(e)}"}

    # =========================================================================
    # Extended Browser Implementations - Google Ads
    # =========================================================================

    async def _capture_google_ads(self, account_id: str, view: str = "overview", date_range: str = "30days") -> dict:
        """Capture Google Ads dashboard."""
        view_paths = {
            "overview": "overview",
            "campaigns": "campaigns",
            "ad_groups": "adgroups",
            "ads": "ads",
            "keywords": "keywords",
            "audiences": "audiences",
        }
        path = view_paths.get(view, "overview")
        url = f"https://ads.google.com/aw/{path}?ocid={account_id}"

        try:
            await self.browser.open(url)
            await self.browser.wait(5000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"google_ads_{view}")

            return {
                "account_id": account_id,
                "view": view,
                "date_range": date_range,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Google Ads capture failed: {str(e)}"}

    async def _capture_google_ads_campaign(self, campaign_url: str, campaign_name: str = "campaign") -> dict:
        """Capture specific Google Ads campaign."""
        try:
            await self.browser.open(campaign_url)
            await self.browser.wait(5000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=campaign_url, output_dir="/tmp/report_proofs", prefix=f"google_ads_campaign_{campaign_name}")

            return {
                "campaign_name": campaign_name,
                "url": campaign_url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Google Ads campaign capture failed: {str(e)}"}

    # =========================================================================
    # Extended Browser Implementations - Facebook Ads
    # =========================================================================

    async def _capture_facebook_ads(self, account_id: str, view: str = "campaigns", date_range: str = "last_30_days") -> dict:
        """Capture Facebook Ads Manager dashboard."""
        url = f"https://www.facebook.com/adsmanager/manage/{view}?act={account_id}"

        try:
            await self.browser.open(url)
            await self.browser.wait(5000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"fb_ads_{view}")

            return {
                "account_id": account_id,
                "view": view,
                "date_range": date_range,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Facebook Ads capture failed: {str(e)}"}

    async def _capture_meta_suite(self, page_id: str, section: str = "overview") -> dict:
        """Capture Meta Business Suite insights."""
        section_paths = {
            "overview": "insights/overview",
            "content": "insights/content",
            "audience": "insights/audience",
            "ads": "ads",
        }
        path = section_paths.get(section, "insights/overview")
        url = f"https://business.facebook.com/{path}?asset_id={page_id}"

        try:
            await self.browser.open(url)
            await self.browser.wait(5000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"meta_suite_{section}")

            return {
                "page_id": page_id,
                "section": section,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Meta Business Suite capture failed: {str(e)}"}

    # =========================================================================
    # Extended Browser Implementations - LinkedIn
    # =========================================================================

    async def _capture_linkedin_campaigns(self, account_id: str, view: str = "campaigns") -> dict:
        """Capture LinkedIn Campaign Manager dashboard."""
        url = f"https://www.linkedin.com/campaignmanager/accounts/{account_id}/{view}"

        try:
            await self.browser.open(url)
            await self.browser.wait(5000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"linkedin_cm_{view}")

            return {
                "account_id": account_id,
                "view": view,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"LinkedIn Campaign Manager capture failed: {str(e)}"}

    async def _capture_linkedin_analytics(self, page_url: str, section: str = "visitors") -> dict:
        """Capture LinkedIn Page analytics."""
        # Construct analytics URL from page URL
        if "/company/" in page_url:
            analytics_url = f"{page_url}/admin/analytics/{section}/"
        else:
            analytics_url = page_url

        try:
            await self.browser.open(analytics_url)
            await self.browser.wait(4000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=analytics_url, output_dir="/tmp/report_proofs", prefix=f"linkedin_analytics_{section}")

            return {
                "page_url": page_url,
                "section": section,
                "url": analytics_url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"LinkedIn analytics capture failed: {str(e)}"}

    # =========================================================================
    # Extended Browser Implementations - Google Search Console
    # =========================================================================

    async def _capture_search_console(self, property_url: str, report_type: str = "performance", date_range: str = "28days") -> dict:
        """Capture Google Search Console performance."""
        from urllib.parse import quote
        encoded_property = quote(property_url, safe='')

        report_paths = {
            "performance": "performance/search-analytics",
            "coverage": "index-coverage",
            "experience": "page-experience",
            "enhancements": "enhancements",
        }
        path = report_paths.get(report_type, "performance/search-analytics")
        url = f"https://search.google.com/search-console/{path}?resource_id={encoded_property}"

        try:
            await self.browser.open(url)
            await self.browser.wait(5000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"gsc_{report_type}")

            return {
                "property_url": property_url,
                "report_type": report_type,
                "date_range": date_range,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Search Console capture failed: {str(e)}"}

    # =========================================================================
    # Extended Browser Implementations - BI Platforms
    # =========================================================================

    async def _capture_tableau(self, dashboard_url: str, name: str = "tableau", wait_time: int = 8000) -> dict:
        """Capture Tableau dashboard."""
        try:
            await self.browser.open(dashboard_url)
            await self.browser.wait(wait_time)  # Tableau needs extra time
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=dashboard_url, output_dir="/tmp/report_proofs", prefix=f"tableau_{name}")

            return {
                "dashboard_name": name,
                "url": dashboard_url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Tableau capture failed: {str(e)}"}

    async def _capture_powerbi(self, report_url: str, name: str = "powerbi", wait_time: int = 8000) -> dict:
        """Capture PowerBI report."""
        try:
            await self.browser.open(report_url)
            await self.browser.wait(wait_time)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=report_url, output_dir="/tmp/report_proofs", prefix=f"powerbi_{name}")

            return {
                "report_name": name,
                "url": report_url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"PowerBI capture failed: {str(e)}"}

    async def _capture_looker(self, dashboard_url: str, name: str = "looker") -> dict:
        """Capture Looker Studio dashboard."""
        try:
            await self.browser.open(dashboard_url)
            await self.browser.wait(6000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=dashboard_url, output_dir="/tmp/report_proofs", prefix=f"looker_{name}")

            return {
                "dashboard_name": name,
                "url": dashboard_url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Looker capture failed: {str(e)}"}

    # =========================================================================
    # Extended Browser Implementations - CRM Platforms
    # =========================================================================

    async def _capture_salesforce(self, dashboard_url: str, name: str = "salesforce") -> dict:
        """Capture Salesforce dashboard."""
        try:
            await self.browser.open(dashboard_url)
            await self.browser.wait(6000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=dashboard_url, output_dir="/tmp/report_proofs", prefix=f"salesforce_{name}")

            return {
                "dashboard_name": name,
                "url": dashboard_url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Salesforce capture failed: {str(e)}"}

    async def _capture_hubspot(self, portal_id: str, report_type: str = "marketing") -> dict:
        """Capture HubSpot analytics dashboard."""
        report_paths = {
            "marketing": "reports-dashboard/marketing",
            "sales": "reports-dashboard/sales",
            "service": "reports-dashboard/service",
            "website": "reports-dashboard/website",
            "custom": "reports-dashboard/custom",
        }
        path = report_paths.get(report_type, "reports-dashboard/marketing")
        url = f"https://app.hubspot.com/{path}/{portal_id}"

        try:
            await self.browser.open(url)
            await self.browser.wait(5000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"hubspot_{report_type}")

            return {
                "portal_id": portal_id,
                "report_type": report_type,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"HubSpot capture failed: {str(e)}"}

    # =========================================================================
    # Extended Browser Implementations - Social Media Analytics
    # =========================================================================

    async def _capture_instagram(self, account_url: str, section: str = "overview") -> dict:
        """Capture Instagram Insights via Meta Business Suite."""
        try:
            await self.browser.open(account_url)
            await self.browser.wait(4000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=account_url, output_dir="/tmp/report_proofs", prefix=f"instagram_{section}")

            return {
                "account_url": account_url,
                "section": section,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Instagram insights capture failed: {str(e)}"}

    async def _capture_tiktok(self, account_url: str, section: str = "overview") -> dict:
        """Capture TikTok Analytics dashboard."""
        try:
            await self.browser.open(account_url)
            await self.browser.wait(4000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=account_url, output_dir="/tmp/report_proofs", prefix=f"tiktok_{section}")

            return {
                "account_url": account_url,
                "section": section,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"TikTok analytics capture failed: {str(e)}"}

    async def _capture_twitter(self, account_url: str, section: str = "home") -> dict:
        """Capture Twitter/X Analytics dashboard."""
        try:
            await self.browser.open(account_url)
            await self.browser.wait(4000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=account_url, output_dir="/tmp/report_proofs", prefix=f"twitter_{section}")

            return {
                "account_url": account_url,
                "section": section,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Twitter analytics capture failed: {str(e)}"}

    async def _capture_youtube(self, channel_url: str, section: str = "analytics") -> dict:
        """Capture YouTube Studio analytics."""
        try:
            await self.browser.open(channel_url)
            await self.browser.wait(5000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=channel_url, output_dir="/tmp/report_proofs", prefix=f"youtube_{section}")

            return {
                "channel_url": channel_url,
                "section": section,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"YouTube Studio capture failed: {str(e)}"}

    # =========================================================================
    # Extended Browser Implementations - Report Generation
    # =========================================================================

    async def _generate_pdf(self, dashboard_url: str, pdf_name: str, wait_time: int = 5000) -> dict:
        """Generate PDF from dashboard URL."""
        try:
            await self.browser.open(dashboard_url)
            await self.browser.wait(wait_time)

            pdf_path = f"/tmp/report_proofs/{pdf_name}.pdf"
            await self.browser.pdf(pdf_path)

            screenshot = await self.browser.capture_proof(url=dashboard_url, output_dir="/tmp/report_proofs", prefix=f"pdf_preview_{pdf_name}")

            return {
                "pdf_name": pdf_name,
                "url": dashboard_url,
                "pdf_path": pdf_path,
                "preview_screenshot": screenshot,
                "success": True,
            }
        except Exception as e:
            return {"error": f"PDF generation failed: {str(e)}"}

    async def _capture_multi(self, dashboard_urls: list, report_name: str) -> dict:
        """Capture multiple dashboards for comparison."""
        results = {"report_name": report_name, "dashboards": [], "timestamp": None}

        for i, url in enumerate(dashboard_urls[:6]):  # Max 6
            try:
                await self.browser.open(url)
                await self.browser.wait(5000)
                snapshot = await self.browser.snapshot(interactive_only=False)
                screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"multi_{report_name}_{i}")

                results["dashboards"].append({
                    "index": i,
                    "url": url,
                    "screenshot": screenshot,
                    "snapshot": snapshot.raw[:500],  # Truncate for summary
                })
                results["timestamp"] = snapshot.timestamp.isoformat()
            except Exception as e:
                results["dashboards"].append({"index": i, "url": url, "error": str(e)})

        return results

    async def _capture_with_dates(self, dashboard_url: str, start_date: str, end_date: str, report_name: str) -> dict:
        """Capture dashboard (date selection requires manual interaction in most platforms)."""
        try:
            await self.browser.open(dashboard_url)
            await self.browser.wait(5000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=dashboard_url, output_dir="/tmp/report_proofs", prefix=f"dated_{report_name}")

            return {
                "report_name": report_name,
                "url": dashboard_url,
                "requested_start_date": start_date,
                "requested_end_date": end_date,
                "note": "Date range selection requires platform authentication. Screenshot captured with current view.",
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Date-specific capture failed: {str(e)}"}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
