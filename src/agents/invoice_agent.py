from typing import Any
import httpx
from .base import BaseAgent


class InvoiceAgent(BaseAgent):
    """Agent for invoice generation and management."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, client_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "invoice_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an invoicing expert. Generate, track, and manage invoices."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "generate_invoice", "description": "Generate invoice from project/retainer.", "input_schema": {"type": "object", "properties": {"project_id": {"type": "string"}, "line_items": {"type": "array", "items": {"type": "object"}}}, "required": []}},
            {"name": "get_invoice", "description": "Get invoice details.", "input_schema": {"type": "object", "properties": {"invoice_id": {"type": "string"}}, "required": ["invoice_id"]}},
            {"name": "send_invoice", "description": "Send invoice to client.", "input_schema": {"type": "object", "properties": {"invoice_id": {"type": "string"}, "channel": {"type": "string"}}, "required": ["invoice_id"]}},
            {"name": "track_payment", "description": "Track invoice payment.", "input_schema": {"type": "object", "properties": {"invoice_id": {"type": "string"}, "status": {"type": "string"}}, "required": ["invoice_id"]}},
            {"name": "get_outstanding", "description": "Get outstanding invoices.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}}, "required": []}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "generate_invoice":
                response = await self.http_client.post("/api/v1/finance/invoices", json={**tool_input, "client_id": self.client_specific_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_invoice":
                response = await self.http_client.get(f"/api/v1/finance/invoices/{tool_input['invoice_id']}")
                return response.json() if response.status_code == 200 else {"error": "Not found"}
            elif tool_name == "send_invoice":
                response = await self.http_client.post(f"/api/v1/finance/invoices/{tool_input['invoice_id']}/send", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            elif tool_name == "track_payment":
                response = await self.http_client.patch(f"/api/v1/finance/invoices/{tool_input['invoice_id']}/payment", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            elif tool_name == "get_outstanding":
                response = await self.http_client.get("/api/v1/finance/invoices/outstanding", params={"client_id": tool_input.get("client_id") or self.client_specific_id})
                return response.json() if response.status_code == 200 else {"invoices": []}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
