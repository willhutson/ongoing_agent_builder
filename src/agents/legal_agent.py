from typing import Any
import httpx
from .base import BaseAgent


class LegalAgent(BaseAgent):
    """Agent for legal compliance and review."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "legal_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a legal compliance expert. Review content and contracts for compliance."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "review_content", "description": "Review content for legal compliance.", "input_schema": {"type": "object", "properties": {"content": {"type": "string"}, "content_type": {"type": "string"}, "regions": {"type": "array", "items": {"type": "string"}}}, "required": ["content"]}},
            {"name": "review_contract", "description": "Review contract terms.", "input_schema": {"type": "object", "properties": {"contract_id": {"type": "string"}, "focus_areas": {"type": "array", "items": {"type": "string"}}}, "required": ["contract_id"]}},
            {"name": "check_ip_rights", "description": "Check IP/usage rights.", "input_schema": {"type": "object", "properties": {"asset_id": {"type": "string"}, "usage_type": {"type": "string"}}, "required": ["asset_id"]}},
            {"name": "get_compliance_requirements", "description": "Get compliance requirements.", "input_schema": {"type": "object", "properties": {"region": {"type": "string"}, "industry": {"type": "string"}}, "required": []}},
            {"name": "flag_compliance_issue", "description": "Flag compliance issue.", "input_schema": {"type": "object", "properties": {"item_id": {"type": "string"}, "issue": {"type": "object"}}, "required": ["item_id", "issue"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "review_content":
                return {"status": "ready_to_review", "instruction": "Review content for legal compliance issues."}
            elif tool_name == "review_contract":
                response = await self.http_client.get(f"/api/v1/legal/contracts/{tool_input['contract_id']}")
                contract = response.json() if response.status_code == 200 else None
                return {"status": "ready_to_review", "contract": contract, "instruction": "Review contract terms."}
            elif tool_name == "check_ip_rights":
                response = await self.http_client.get(f"/api/v1/legal/ip-rights/{tool_input['asset_id']}")
                return response.json() if response.status_code == 200 else {"rights": None}
            elif tool_name == "get_compliance_requirements":
                response = await self.http_client.get("/api/v1/legal/compliance", params=tool_input)
                return response.json() if response.status_code == 200 else {"requirements": []}
            elif tool_name == "flag_compliance_issue":
                response = await self.http_client.post("/api/v1/legal/issues", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
