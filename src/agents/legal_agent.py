from typing import Any
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class LegalAgent(BaseAgent):
    """Agent for legal compliance and review with policy capture."""

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
        return """You are a legal compliance expert. Review content and contracts for compliance.

You have browser automation to capture T&C pages, privacy policies, and ad platform policies for audit trails."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "review_content", "description": "Review content for compliance.", "input_schema": {"type": "object", "properties": {"content": {"type": "string"}, "content_type": {"type": "string"}, "regions": {"type": "array", "items": {"type": "string"}}}, "required": ["content"]}},
            {"name": "review_contract", "description": "Review contract terms.", "input_schema": {"type": "object", "properties": {"contract_id": {"type": "string"}, "focus_areas": {"type": "array", "items": {"type": "string"}}}, "required": ["contract_id"]}},
            {"name": "check_ip_rights", "description": "Check IP/usage rights.", "input_schema": {"type": "object", "properties": {"asset_id": {"type": "string"}, "usage_type": {"type": "string"}}, "required": ["asset_id"]}},
            {"name": "get_compliance_requirements", "description": "Get compliance requirements.", "input_schema": {"type": "object", "properties": {"region": {"type": "string"}, "industry": {"type": "string"}}, "required": []}},
            {"name": "flag_compliance_issue", "description": "Flag compliance issue.", "input_schema": {"type": "object", "properties": {"item_id": {"type": "string"}, "issue": {"type": "object"}}, "required": ["item_id", "issue"]}},
            {"name": "capture_platform_policy", "description": "Capture ad platform policy page.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["meta", "google", "tiktok", "linkedin"]}, "policy_type": {"type": "string", "enum": ["ads", "community", "terms", "privacy"]}}, "required": ["platform"]}},
            {"name": "capture_website_terms", "description": "Capture website T&C or privacy page.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "page_type": {"type": "string", "enum": ["terms", "privacy", "cookies"]}}, "required": ["url"]}},
            {"name": "save_compliance_pdf", "description": "Save policy page as PDF.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "document_name": {"type": "string"}}, "required": ["url", "document_name"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
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
            elif tool_name == "capture_platform_policy":
                return await self._capture_platform_policy(tool_input["platform"], tool_input.get("policy_type", "ads"))
            elif tool_name == "capture_website_terms":
                return await self._capture_website_terms(tool_input["url"], tool_input.get("page_type", "terms"))
            elif tool_name == "save_compliance_pdf":
                return await self._save_pdf(tool_input["url"], tool_input["document_name"])
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_platform_policy(self, platform: str, policy_type: str) -> dict:
        policy_urls = {
            "meta": {"ads": "https://www.facebook.com/policies/ads/", "terms": "https://www.facebook.com/terms.php", "privacy": "https://www.facebook.com/privacy/policy/"},
            "google": {"ads": "https://support.google.com/adspolicy/answer/6008942", "terms": "https://policies.google.com/terms", "privacy": "https://policies.google.com/privacy"},
            "tiktok": {"ads": "https://ads.tiktok.com/help/article/tiktok-advertising-policies", "terms": "https://www.tiktok.com/legal/terms-of-service", "privacy": "https://www.tiktok.com/legal/privacy-policy"},
            "linkedin": {"ads": "https://www.linkedin.com/legal/ads-policy", "terms": "https://www.linkedin.com/legal/user-agreement", "privacy": "https://www.linkedin.com/legal/privacy-policy"},
        }
        url = policy_urls.get(platform, {}).get(policy_type)
        if not url:
            return {"error": f"Unknown platform/policy: {platform}/{policy_type}"}
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/legal_proofs", prefix=f"{platform}_{policy_type}")
            return {"platform": platform, "policy_type": policy_type, "url": url, "screenshot": screenshot_path}
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

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
