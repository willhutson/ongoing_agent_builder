from typing import Any
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class LegalAgent(BaseAgent):
    """
    Agent for legal compliance, regulatory monitoring, and policy verification.

    Capabilities:
    - Review content and contracts for compliance (API)
    - Check IP/usage rights (API)
    - Flag compliance issues (API)
    - Capture platform ad policies (Browser)
    - Capture website T&C and privacy policies (Browser)
    - Save compliance documents as PDF (Browser)
    - Detect T&C and privacy policy changes (Browser)
    - Verify GDPR/CCPA compliance indicators (Browser)
    - Analyze cookie consent banners (Browser)
    - Check FTC ad disclosure compliance (Browser)
    - Verify influencer disclosure requirements (Browser)
    - Monitor regulatory filings (Browser)
    - Check accessibility compliance (Browser)
    - Compare competitor terms (Browser)
    - Verify data processing agreements (Browser)
    """

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, instance_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.instance_id = instance_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        session_name = f"legal_{instance_id}" if instance_id else "legal"
        self.browser = AgentBrowserSkill(session_name=session_name)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "legal_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a legal compliance expert for marketing and advertising agencies.

Your role is to ensure regulatory compliance:
1. Review content for legal issues
2. Monitor platform policy changes
3. Verify GDPR/CCPA compliance
4. Check FTC disclosure requirements
5. Capture audit trail documentation

You have browser automation to:
- Capture T&C and privacy policy pages
- Detect policy changes over time
- Verify GDPR cookie consent compliance
- Check FTC ad disclosure requirements
- Verify influencer #ad disclosure
- Monitor SEC/FTC regulatory filings
- Check website accessibility compliance
- Compare competitor legal terms
- Capture data processing agreements"""

    def _define_tools(self) -> list[dict]:
        return [
            # API Tools
            {"name": "review_content", "description": "Review content for compliance.", "input_schema": {"type": "object", "properties": {"content": {"type": "string"}, "content_type": {"type": "string"}, "regions": {"type": "array", "items": {"type": "string"}}}, "required": ["content"]}},
            {"name": "review_contract", "description": "Review contract terms.", "input_schema": {"type": "object", "properties": {"contract_id": {"type": "string"}, "focus_areas": {"type": "array", "items": {"type": "string"}}}, "required": ["contract_id"]}},
            {"name": "check_ip_rights", "description": "Check IP/usage rights.", "input_schema": {"type": "object", "properties": {"asset_id": {"type": "string"}, "usage_type": {"type": "string"}}, "required": ["asset_id"]}},
            {"name": "get_compliance_requirements", "description": "Get compliance requirements.", "input_schema": {"type": "object", "properties": {"region": {"type": "string"}, "industry": {"type": "string"}}, "required": []}},
            {"name": "flag_compliance_issue", "description": "Flag compliance issue.", "input_schema": {"type": "object", "properties": {"item_id": {"type": "string"}, "issue": {"type": "object"}}, "required": ["item_id", "issue"]}},
            # Core Browser Tools
            {"name": "capture_platform_policy", "description": "Capture ad platform policy page.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["meta", "google", "tiktok", "linkedin", "twitter", "snapchat", "pinterest"]}, "policy_type": {"type": "string", "enum": ["ads", "community", "terms", "privacy", "data"]}}, "required": ["platform"]}},
            {"name": "capture_website_terms", "description": "Capture website T&C or privacy page.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "page_type": {"type": "string", "enum": ["terms", "privacy", "cookies", "acceptable_use", "dmca"]}}, "required": ["url"]}},
            {"name": "save_compliance_pdf", "description": "Save policy page as PDF.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "document_name": {"type": "string"}}, "required": ["url", "document_name"]}},
            # Extended Browser Tools - Policy Change Detection
            {"name": "detect_policy_changes", "description": "Capture current policy and compare with previous version for changes.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "policy_name": {"type": "string"}, "previous_snapshot": {"type": "string", "description": "Previous policy text to compare against"}}, "required": ["url", "policy_name"]}},
            {"name": "monitor_terms_update", "description": "Check if website terms page has been recently updated.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "look_for_date": {"type": "boolean", "default": True}}, "required": ["url"]}},
            {"name": "capture_wayback_policy", "description": "Capture historical version of policy from Wayback Machine.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "date": {"type": "string", "description": "Date in YYYYMMDD format"}}, "required": ["url"]}},
            # GDPR/Privacy Compliance
            {"name": "verify_gdpr_compliance", "description": "Check website for GDPR compliance indicators.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "check_items": {"type": "array", "items": {"type": "string", "enum": ["cookie_banner", "privacy_link", "consent_management", "data_request", "opt_out"]}}}, "required": ["url"]}},
            {"name": "analyze_cookie_banner", "description": "Analyze cookie consent banner for compliance.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "region": {"type": "string", "enum": ["eu", "california", "brazil", "uk"], "default": "eu"}}, "required": ["url"]}},
            {"name": "check_ccpa_compliance", "description": "Check for CCPA 'Do Not Sell' link and privacy notice.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            {"name": "verify_consent_mechanism", "description": "Verify consent management platform implementation.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "cmp_provider": {"type": "string", "enum": ["onetrust", "cookiebot", "trustarc", "quantcast", "didomi", "other"]}}, "required": ["url"]}},
            # FTC/Advertising Compliance
            {"name": "check_ad_disclosure", "description": "Check ad/sponsored content for FTC disclosure compliance.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "content_type": {"type": "string", "enum": ["blog_post", "social_post", "video", "landing_page", "email"]}}, "required": ["url"]}},
            {"name": "verify_influencer_disclosure", "description": "Check influencer post for proper #ad disclosure.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "platform": {"type": "string", "enum": ["instagram", "tiktok", "youtube", "twitter", "facebook"]}}, "required": ["url", "platform"]}},
            {"name": "check_testimonial_disclosure", "description": "Verify testimonials have proper disclosure.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            {"name": "verify_sweepstakes_rules", "description": "Check sweepstakes/contest for required legal disclosures.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "promotion_type": {"type": "string", "enum": ["sweepstakes", "contest", "giveaway"]}}, "required": ["url"]}},
            # Regulatory Filings
            {"name": "search_sec_filings", "description": "Search SEC EDGAR for company filings.", "input_schema": {"type": "object", "properties": {"company_name": {"type": "string"}, "filing_type": {"type": "string", "enum": ["10-K", "10-Q", "8-K", "S-1", "all"], "default": "all"}}, "required": ["company_name"]}},
            {"name": "search_ftc_actions", "description": "Search FTC for enforcement actions.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "case_type": {"type": "string", "enum": ["advertising", "privacy", "competition", "all"], "default": "all"}}, "required": ["query"]}},
            {"name": "check_trademark_status", "description": "Check USPTO trademark status.", "input_schema": {"type": "object", "properties": {"trademark": {"type": "string"}, "search_type": {"type": "string", "enum": ["wordmark", "design", "all"], "default": "wordmark"}}, "required": ["trademark"]}},
            # Accessibility Compliance
            {"name": "check_accessibility", "description": "Check website for basic accessibility compliance indicators.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "standard": {"type": "string", "enum": ["wcag_aa", "wcag_aaa", "section_508"], "default": "wcag_aa"}}, "required": ["url"]}},
            {"name": "capture_accessibility_statement", "description": "Capture website accessibility statement page.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            # Competitor/Comparison Tools
            {"name": "compare_competitor_terms", "description": "Capture competitor terms for comparison analysis.", "input_schema": {"type": "object", "properties": {"urls": {"type": "array", "items": {"type": "string"}, "maxItems": 5}, "focus_sections": {"type": "array", "items": {"type": "string"}}}, "required": ["urls"]}},
            {"name": "capture_dpa_agreement", "description": "Capture Data Processing Agreement page.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "vendor_name": {"type": "string"}}, "required": ["url"]}},
            # Content Licensing
            {"name": "verify_stock_license", "description": "Verify stock image/video licensing page.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["shutterstock", "getty", "adobe_stock", "istock", "unsplash"]}, "asset_id": {"type": "string"}}, "required": ["platform"]}},
            {"name": "capture_music_license", "description": "Capture music licensing terms.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["epidemic_sound", "artlist", "musicbed", "soundstripe"]}, "license_type": {"type": "string", "enum": ["personal", "commercial", "broadcast"]}}, "required": ["platform"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            # API Tools
            if tool_name == "review_content":
                return {"status": "ready_to_review", "instruction": "Review content for legal compliance issues."}
            elif tool_name == "review_contract":
                response = await self.http_client.get(f"/api/v1/legal/contracts/{tool_input['contract_id']}")
                contract = response.json() if response.status_code == 200 else None
                return {"status": "ready_to_review", "contract": contract}
            elif tool_name == "check_ip_rights":
                response = await self.http_client.get(f"/api/v1/legal/ip-rights/{tool_input['asset_id']}")
                return response.json() if response.status_code == 200 else {"rights": None}
            elif tool_name == "get_compliance_requirements":
                response = await self.http_client.get("/api/v1/legal/compliance", params=tool_input)
                return response.json() if response.status_code == 200 else {"requirements": []}
            elif tool_name == "flag_compliance_issue":
                response = await self.http_client.post("/api/v1/legal/issues", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            # Core Browser Tools
            elif tool_name == "capture_platform_policy":
                return await self._capture_platform_policy(tool_input["platform"], tool_input.get("policy_type", "ads"))
            elif tool_name == "capture_website_terms":
                return await self._capture_website_terms(tool_input["url"], tool_input.get("page_type", "terms"))
            elif tool_name == "save_compliance_pdf":
                return await self._save_pdf(tool_input["url"], tool_input["document_name"])
            # Extended Browser Tools - Policy Change Detection
            elif tool_name == "detect_policy_changes":
                return await self._detect_policy_changes(tool_input["url"], tool_input["policy_name"], tool_input.get("previous_snapshot"))
            elif tool_name == "monitor_terms_update":
                return await self._monitor_terms_update(tool_input["url"], tool_input.get("look_for_date", True))
            elif tool_name == "capture_wayback_policy":
                return await self._capture_wayback_policy(tool_input["url"], tool_input.get("date"))
            # GDPR/Privacy Compliance
            elif tool_name == "verify_gdpr_compliance":
                return await self._verify_gdpr_compliance(tool_input["url"], tool_input.get("check_items", ["cookie_banner", "privacy_link"]))
            elif tool_name == "analyze_cookie_banner":
                return await self._analyze_cookie_banner(tool_input["url"], tool_input.get("region", "eu"))
            elif tool_name == "check_ccpa_compliance":
                return await self._check_ccpa_compliance(tool_input["url"])
            elif tool_name == "verify_consent_mechanism":
                return await self._verify_consent_mechanism(tool_input["url"], tool_input.get("cmp_provider"))
            # FTC/Advertising Compliance
            elif tool_name == "check_ad_disclosure":
                return await self._check_ad_disclosure(tool_input["url"], tool_input.get("content_type", "landing_page"))
            elif tool_name == "verify_influencer_disclosure":
                return await self._verify_influencer_disclosure(tool_input["url"], tool_input["platform"])
            elif tool_name == "check_testimonial_disclosure":
                return await self._check_testimonial_disclosure(tool_input["url"])
            elif tool_name == "verify_sweepstakes_rules":
                return await self._verify_sweepstakes_rules(tool_input["url"], tool_input.get("promotion_type", "sweepstakes"))
            # Regulatory Filings
            elif tool_name == "search_sec_filings":
                return await self._search_sec_filings(tool_input["company_name"], tool_input.get("filing_type", "all"))
            elif tool_name == "search_ftc_actions":
                return await self._search_ftc_actions(tool_input["query"], tool_input.get("case_type", "all"))
            elif tool_name == "check_trademark_status":
                return await self._check_trademark_status(tool_input["trademark"], tool_input.get("search_type", "wordmark"))
            # Accessibility Compliance
            elif tool_name == "check_accessibility":
                return await self._check_accessibility(tool_input["url"], tool_input.get("standard", "wcag_aa"))
            elif tool_name == "capture_accessibility_statement":
                return await self._capture_accessibility_statement(tool_input["url"])
            # Competitor/Comparison Tools
            elif tool_name == "compare_competitor_terms":
                return await self._compare_competitor_terms(tool_input["urls"], tool_input.get("focus_sections", []))
            elif tool_name == "capture_dpa_agreement":
                return await self._capture_dpa_agreement(tool_input["url"], tool_input.get("vendor_name", "vendor"))
            # Content Licensing
            elif tool_name == "verify_stock_license":
                return await self._verify_stock_license(tool_input["platform"], tool_input.get("asset_id"))
            elif tool_name == "capture_music_license":
                return await self._capture_music_license(tool_input["platform"], tool_input.get("license_type", "commercial"))
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_platform_policy(self, platform: str, policy_type: str) -> dict:
        policy_urls = {
            "meta": {"ads": "https://www.facebook.com/policies/ads/", "terms": "https://www.facebook.com/terms.php", "privacy": "https://www.facebook.com/privacy/policy/", "data": "https://www.facebook.com/privacy/policy/"},
            "google": {"ads": "https://support.google.com/adspolicy/answer/6008942", "terms": "https://policies.google.com/terms", "privacy": "https://policies.google.com/privacy", "data": "https://policies.google.com/privacy"},
            "tiktok": {"ads": "https://ads.tiktok.com/help/article/tiktok-advertising-policies", "terms": "https://www.tiktok.com/legal/terms-of-service", "privacy": "https://www.tiktok.com/legal/privacy-policy", "data": "https://www.tiktok.com/legal/privacy-policy"},
            "linkedin": {"ads": "https://www.linkedin.com/legal/ads-policy", "terms": "https://www.linkedin.com/legal/user-agreement", "privacy": "https://www.linkedin.com/legal/privacy-policy", "data": "https://www.linkedin.com/legal/privacy-policy"},
            "twitter": {"ads": "https://business.twitter.com/en/help/ads-policies.html", "terms": "https://twitter.com/en/tos", "privacy": "https://twitter.com/en/privacy", "data": "https://twitter.com/en/privacy"},
            "snapchat": {"ads": "https://snap.com/en-US/ad-policies", "terms": "https://snap.com/en-US/terms", "privacy": "https://snap.com/en-US/privacy/privacy-policy", "data": "https://snap.com/en-US/privacy/privacy-policy"},
            "pinterest": {"ads": "https://policy.pinterest.com/en/advertising-guidelines", "terms": "https://policy.pinterest.com/en/terms-of-service", "privacy": "https://policy.pinterest.com/en/privacy-policy", "data": "https://policy.pinterest.com/en/privacy-policy"},
        }
        url = policy_urls.get(platform, {}).get(policy_type)
        if not url:
            return {"error": f"Unknown platform/policy: {platform}/{policy_type}"}
        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"{platform}_{policy_type}")
            return {"platform": platform, "policy_type": policy_type, "url": url, "snapshot": snapshot.raw, "screenshot": screenshot_path, "timestamp": snapshot.timestamp.isoformat()}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_website_terms(self, url: str, page_type: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"website_{page_type}")
            return {"url": url, "page_type": page_type, "snapshot": snapshot.raw, "screenshot": screenshot_path, "timestamp": snapshot.timestamp.isoformat()}
        except Exception as e:
            return {"error": str(e)}

    async def _save_pdf(self, url: str, name: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            pdf_path = f"/tmp/legal_proofs/{name}.pdf"
            await self.browser.pdf(pdf_path)
            return {"url": url, "pdf_path": pdf_path, "success": True}
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # Extended Browser Implementations - Policy Change Detection
    # =========================================================================

    async def _detect_policy_changes(self, url: str, policy_name: str, previous_snapshot: str = None) -> dict:
        """Capture current policy and identify changes from previous version."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"policy_change_{policy_name}")

            result = {
                "policy_name": policy_name,
                "url": url,
                "current_snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if previous_snapshot:
                # Simple change detection
                result["has_changes"] = snapshot.raw.strip() != previous_snapshot.strip()
                result["previous_length"] = len(previous_snapshot)
                result["current_length"] = len(snapshot.raw)

            return result
        except Exception as e:
            return {"error": f"Policy change detection failed: {str(e)}"}

    async def _monitor_terms_update(self, url: str, look_for_date: bool = True) -> dict:
        """Check if terms page shows recent update date."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix="terms_update")

            result = {
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if look_for_date:
                # Look for common date patterns in the page
                import re
                date_patterns = [
                    r"last updated[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
                    r"effective[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
                    r"revised[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
                    r"(\d{1,2}/\d{1,2}/\d{4})",
                    r"(\d{4}-\d{2}-\d{2})",
                ]
                for pattern in date_patterns:
                    match = re.search(pattern, snapshot.raw, re.IGNORECASE)
                    if match:
                        result["detected_date"] = match.group(1)
                        break

            return result
        except Exception as e:
            return {"error": f"Terms monitoring failed: {str(e)}"}

    async def _capture_wayback_policy(self, url: str, date: str = None) -> dict:
        """Capture historical policy from Wayback Machine."""
        if date:
            wayback_url = f"https://web.archive.org/web/{date}/{url}"
        else:
            wayback_url = f"https://web.archive.org/web/*/{url}"

        try:
            await self.browser.open(wayback_url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=wayback_url, output_dir="/tmp/legal_proofs", prefix=f"wayback_{date or 'latest'}")

            return {
                "original_url": url,
                "wayback_url": wayback_url,
                "date": date,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Wayback capture failed: {str(e)}"}

    # =========================================================================
    # GDPR/Privacy Compliance
    # =========================================================================

    async def _verify_gdpr_compliance(self, url: str, check_items: list) -> dict:
        """Check website for GDPR compliance indicators."""
        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix="gdpr_check")

            content_lower = snapshot.raw.lower()
            findings = {}

            if "cookie_banner" in check_items:
                cookie_indicators = ["cookie", "cookies", "consent", "accept all", "reject all", "manage preferences"]
                findings["cookie_banner"] = any(ind in content_lower for ind in cookie_indicators)

            if "privacy_link" in check_items:
                privacy_indicators = ["privacy policy", "privacy notice", "data protection"]
                findings["privacy_link"] = any(ind in content_lower for ind in privacy_indicators)

            if "consent_management" in check_items:
                cmp_indicators = ["onetrust", "cookiebot", "trustarc", "quantcast", "didomi", "consent manager"]
                findings["consent_management"] = any(ind in content_lower for ind in cmp_indicators)

            if "data_request" in check_items:
                request_indicators = ["data request", "access your data", "download your data", "gdpr request"]
                findings["data_request"] = any(ind in content_lower for ind in request_indicators)

            if "opt_out" in check_items:
                optout_indicators = ["opt out", "opt-out", "unsubscribe", "do not sell"]
                findings["opt_out"] = any(ind in content_lower for ind in optout_indicators)

            return {
                "url": url,
                "findings": findings,
                "compliance_score": sum(findings.values()) / len(findings) if findings else 0,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"GDPR verification failed: {str(e)}"}

    async def _analyze_cookie_banner(self, url: str, region: str = "eu") -> dict:
        """Analyze cookie consent banner for compliance."""
        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"cookie_banner_{region}")

            content_lower = snapshot.raw.lower()

            analysis = {
                "has_banner": "cookie" in content_lower or "consent" in content_lower,
                "has_accept": "accept" in content_lower,
                "has_reject": "reject" in content_lower or "decline" in content_lower,
                "has_settings": "settings" in content_lower or "preferences" in content_lower or "manage" in content_lower,
                "has_necessary_only": "necessary" in content_lower or "essential" in content_lower,
            }

            # Region-specific requirements
            if region == "eu":
                analysis["eu_compliant"] = analysis["has_reject"] and analysis["has_settings"]
            elif region == "california":
                analysis["ccpa_compliant"] = "do not sell" in content_lower

            return {
                "url": url,
                "region": region,
                "analysis": analysis,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Cookie banner analysis failed: {str(e)}"}

    async def _check_ccpa_compliance(self, url: str) -> dict:
        """Check for CCPA compliance indicators."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix="ccpa_check")

            content_lower = snapshot.raw.lower()

            findings = {
                "do_not_sell_link": "do not sell" in content_lower or "do-not-sell" in content_lower,
                "privacy_notice": "privacy" in content_lower,
                "california_rights": "california" in content_lower and "rights" in content_lower,
                "opt_out_mechanism": "opt out" in content_lower or "opt-out" in content_lower,
                "contact_info": "contact" in content_lower,
            }

            return {
                "url": url,
                "findings": findings,
                "ccpa_compliant": findings["do_not_sell_link"] and findings["privacy_notice"],
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"CCPA check failed: {str(e)}"}

    async def _verify_consent_mechanism(self, url: str, cmp_provider: str = None) -> dict:
        """Verify consent management platform implementation."""
        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix="cmp_verify")

            content_lower = snapshot.raw.lower()

            cmp_signatures = {
                "onetrust": ["onetrust", "optanon"],
                "cookiebot": ["cookiebot", "cybot"],
                "trustarc": ["trustarc", "truste"],
                "quantcast": ["quantcast", "__cmp"],
                "didomi": ["didomi"],
            }

            detected_cmps = []
            for cmp, signatures in cmp_signatures.items():
                if any(sig in content_lower for sig in signatures):
                    detected_cmps.append(cmp)

            result = {
                "url": url,
                "detected_cmps": detected_cmps,
                "has_cmp": len(detected_cmps) > 0,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if cmp_provider:
                result["expected_cmp_found"] = cmp_provider.lower() in detected_cmps

            return result
        except Exception as e:
            return {"error": f"CMP verification failed: {str(e)}"}

    # =========================================================================
    # FTC/Advertising Compliance
    # =========================================================================

    async def _check_ad_disclosure(self, url: str, content_type: str = "landing_page") -> dict:
        """Check ad/sponsored content for FTC disclosure compliance."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"ad_disclosure_{content_type}")

            content_lower = snapshot.raw.lower()

            disclosure_indicators = {
                "ad": ["#ad", "advertisement", "sponsored", "paid partnership"],
                "affiliate": ["affiliate", "commission", "affiliate link"],
                "partnership": ["partnership", "partner", "collaboration"],
                "material_connection": ["material connection", "compensation", "free product"],
            }

            findings = {}
            for category, indicators in disclosure_indicators.items():
                findings[category] = any(ind in content_lower for ind in indicators)

            return {
                "url": url,
                "content_type": content_type,
                "disclosure_found": any(findings.values()),
                "findings": findings,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Ad disclosure check failed: {str(e)}"}

    async def _verify_influencer_disclosure(self, url: str, platform: str) -> dict:
        """Check influencer post for proper #ad disclosure."""
        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"influencer_{platform}")

            content_lower = snapshot.raw.lower()

            ftc_compliant_disclosures = ["#ad", "#sponsored", "#paidpartnership", "paid partnership", "advertisement"]
            non_compliant_disclosures = ["#sp", "#spon", "#partner", "#collab"]

            findings = {
                "compliant_disclosure": any(d in content_lower for d in ftc_compliant_disclosures),
                "non_compliant_disclosure": any(d in content_lower for d in non_compliant_disclosures),
                "no_disclosure": not any(d in content_lower for d in ftc_compliant_disclosures + non_compliant_disclosures),
            }

            return {
                "url": url,
                "platform": platform,
                "ftc_compliant": findings["compliant_disclosure"],
                "findings": findings,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Influencer disclosure check failed: {str(e)}"}

    async def _check_testimonial_disclosure(self, url: str) -> dict:
        """Verify testimonials have proper disclosure."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix="testimonial")

            content_lower = snapshot.raw.lower()

            findings = {
                "has_testimonials": "testimonial" in content_lower or "review" in content_lower or "customer says" in content_lower,
                "has_disclosure": "results may vary" in content_lower or "individual results" in content_lower or "typical results" in content_lower,
                "has_verification": "verified" in content_lower or "authentic" in content_lower,
            }

            return {
                "url": url,
                "findings": findings,
                "compliant": findings["has_disclosure"] if findings["has_testimonials"] else True,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Testimonial check failed: {str(e)}"}

    async def _verify_sweepstakes_rules(self, url: str, promotion_type: str = "sweepstakes") -> dict:
        """Check sweepstakes/contest for required legal disclosures."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"{promotion_type}_rules")

            content_lower = snapshot.raw.lower()

            required_elements = {
                "no_purchase": "no purchase necessary" in content_lower,
                "void_where": "void where prohibited" in content_lower,
                "eligibility": "eligibility" in content_lower or "must be" in content_lower,
                "odds": "odds" in content_lower,
                "sponsor": "sponsor" in content_lower,
                "prize_description": "prize" in content_lower,
                "entry_period": "entry" in content_lower and ("period" in content_lower or "deadline" in content_lower or "ends" in content_lower),
                "official_rules": "official rules" in content_lower,
            }

            return {
                "url": url,
                "promotion_type": promotion_type,
                "required_elements": required_elements,
                "compliant": sum(required_elements.values()) >= 5,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Sweepstakes verification failed: {str(e)}"}

    # =========================================================================
    # Regulatory Filings
    # =========================================================================

    async def _search_sec_filings(self, company_name: str, filing_type: str = "all") -> dict:
        """Search SEC EDGAR for company filings."""
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={company_name}&type={filing_type if filing_type != 'all' else ''}&dateb=&owner=include&count=40"

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"sec_{company_name.replace(' ', '_')}")

            return {
                "company_name": company_name,
                "filing_type": filing_type,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"SEC search failed: {str(e)}"}

    async def _search_ftc_actions(self, query: str, case_type: str = "all") -> dict:
        """Search FTC for enforcement actions."""
        url = f"https://www.ftc.gov/legal-library/browse/cases-proceedings?search_api_fulltext={query}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"ftc_{query.replace(' ', '_')}")

            return {
                "query": query,
                "case_type": case_type,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"FTC search failed: {str(e)}"}

    async def _check_trademark_status(self, trademark: str, search_type: str = "wordmark") -> dict:
        """Check USPTO trademark status."""
        url = f"https://tmsearch.uspto.gov/bin/showfield?f=toc&state=4810:xphp0x.1.1&p_search=searchss&p_L=50&BackReference=&p_plural=yes&p_s_PARA1=&p_taession=3&p_s_PARA2={trademark}"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"trademark_{trademark.replace(' ', '_')}")

            return {
                "trademark": trademark,
                "search_type": search_type,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Trademark search failed: {str(e)}"}

    # =========================================================================
    # Accessibility Compliance
    # =========================================================================

    async def _check_accessibility(self, url: str, standard: str = "wcag_aa") -> dict:
        """Check website for basic accessibility compliance indicators."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"accessibility_{standard}")

            content_lower = snapshot.raw.lower()

            # Basic accessibility indicators (limited without full DOM analysis)
            indicators = {
                "has_alt_text": "alt=" in content_lower,
                "has_skip_link": "skip to" in content_lower or "skip navigation" in content_lower,
                "has_aria": "aria-" in content_lower,
                "has_lang": "lang=" in content_lower,
                "has_heading_structure": "<h1" in content_lower and "<h2" in content_lower,
                "accessibility_statement": "accessibility" in content_lower,
            }

            return {
                "url": url,
                "standard": standard,
                "indicators": indicators,
                "basic_compliance_score": sum(indicators.values()) / len(indicators),
                "screenshot": screenshot,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Accessibility check failed: {str(e)}"}

    async def _capture_accessibility_statement(self, url: str) -> dict:
        """Capture website accessibility statement page."""
        # Try common accessibility page URLs
        accessibility_paths = ["/accessibility", "/accessibility-statement", "/ada", "/accessibility-policy"]

        from urllib.parse import urlparse
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        for path in accessibility_paths:
            try:
                test_url = base_url + path
                await self.browser.open(test_url)
                await self.browser.wait(2000)
                snapshot = await self.browser.snapshot(interactive_only=False)

                if "accessibility" in snapshot.raw.lower() and len(snapshot.raw) > 500:
                    screenshot = await self.browser.capture_proof(url=test_url, output_dir="/tmp/legal_proofs", prefix="accessibility_statement")
                    pdf_path = f"/tmp/legal_proofs/accessibility_statement.pdf"
                    await self.browser.pdf(pdf_path)

                    return {
                        "url": test_url,
                        "found": True,
                        "snapshot": snapshot.raw,
                        "screenshot": screenshot,
                        "pdf_path": pdf_path,
                        "timestamp": snapshot.timestamp.isoformat(),
                    }
            except:
                continue

        return {"url": url, "found": False, "error": "No accessibility statement page found"}

    # =========================================================================
    # Competitor/Comparison Tools
    # =========================================================================

    async def _compare_competitor_terms(self, urls: list, focus_sections: list = None) -> dict:
        """Capture competitor terms for comparison analysis."""
        results = {"comparisons": [], "timestamp": None}

        for url in urls[:5]:  # Limit to 5
            try:
                await self.browser.open(url)
                await self.browser.wait(2500)
                snapshot = await self.browser.snapshot(interactive_only=False)
                screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"compare_{len(results['comparisons'])}")

                results["comparisons"].append({
                    "url": url,
                    "snapshot": snapshot.raw,
                    "screenshot": screenshot,
                    "word_count": len(snapshot.raw.split()),
                })
                results["timestamp"] = snapshot.timestamp.isoformat()
            except Exception as e:
                results["comparisons"].append({"url": url, "error": str(e)})

        return results

    async def _capture_dpa_agreement(self, url: str, vendor_name: str = "vendor") -> dict:
        """Capture Data Processing Agreement page."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"dpa_{vendor_name}")
            pdf_path = f"/tmp/legal_proofs/dpa_{vendor_name}.pdf"
            await self.browser.pdf(pdf_path)

            return {
                "vendor_name": vendor_name,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "pdf_path": pdf_path,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"DPA capture failed: {str(e)}"}

    # =========================================================================
    # Content Licensing
    # =========================================================================

    async def _verify_stock_license(self, platform: str, asset_id: str = None) -> dict:
        """Verify stock image/video licensing page."""
        license_urls = {
            "shutterstock": "https://www.shutterstock.com/license",
            "getty": "https://www.gettyimages.com/eula",
            "adobe_stock": "https://stock.adobe.com/license-terms",
            "istock": "https://www.istockphoto.com/legal/license-agreement",
            "unsplash": "https://unsplash.com/license",
        }

        url = license_urls.get(platform)
        if not url:
            return {"error": f"Unknown platform: {platform}"}

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"stock_license_{platform}")
            pdf_path = f"/tmp/legal_proofs/stock_license_{platform}.pdf"
            await self.browser.pdf(pdf_path)

            return {
                "platform": platform,
                "asset_id": asset_id,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "pdf_path": pdf_path,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Stock license verification failed: {str(e)}"}

    async def _capture_music_license(self, platform: str, license_type: str = "commercial") -> dict:
        """Capture music licensing terms."""
        license_urls = {
            "epidemic_sound": "https://www.epidemicsound.com/music-licensing/",
            "artlist": "https://artlist.io/license-agreement",
            "musicbed": "https://www.musicbed.com/license-types",
            "soundstripe": "https://www.soundstripe.com/license",
        }

        url = license_urls.get(platform)
        if not url:
            return {"error": f"Unknown platform: {platform}"}

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"music_license_{platform}")
            pdf_path = f"/tmp/legal_proofs/music_license_{platform}.pdf"
            await self.browser.pdf(pdf_path)

            return {
                "platform": platform,
                "license_type": license_type,
                "url": url,
                "snapshot": snapshot.raw,
                "screenshot": screenshot,
                "pdf_path": pdf_path,
                "timestamp": snapshot.timestamp.isoformat(),
            }
        except Exception as e:
            return {"error": f"Music license capture failed: {str(e)}"}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
