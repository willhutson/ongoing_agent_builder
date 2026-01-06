from typing import Any
import httpx
from .base import BaseAgent


class QAAgent(BaseAgent):
    """Agent for quality assurance."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "qa_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a quality assurance expert. Review and ensure quality of deliverables."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "create_qa_checklist", "description": "Create QA checklist.", "input_schema": {"type": "object", "properties": {"deliverable_type": {"type": "string"}, "items": {"type": "array", "items": {"type": "object"}}}, "required": ["deliverable_type"]}},
            {"name": "run_qa_review", "description": "Run QA review on deliverable.", "input_schema": {"type": "object", "properties": {"deliverable_id": {"type": "string"}, "checklist_id": {"type": "string"}}, "required": ["deliverable_id"]}},
            {"name": "log_issue", "description": "Log QA issue.", "input_schema": {"type": "object", "properties": {"deliverable_id": {"type": "string"}, "issue": {"type": "object"}}, "required": ["deliverable_id", "issue"]}},
            {"name": "get_qa_status", "description": "Get QA status.", "input_schema": {"type": "object", "properties": {"project_id": {"type": "string"}}, "required": ["project_id"]}},
            {"name": "approve_qa", "description": "Approve QA review.", "input_schema": {"type": "object", "properties": {"review_id": {"type": "string"}, "notes": {"type": "string"}}, "required": ["review_id"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "create_qa_checklist":
                response = await self.http_client.post("/api/v1/qa/checklists", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "run_qa_review":
                return {"status": "ready_to_review", "instruction": "Review deliverable against quality checklist."}
            elif tool_name == "log_issue":
                response = await self.http_client.post(f"/api/v1/qa/deliverables/{tool_input['deliverable_id']}/issues", json=tool_input["issue"])
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_qa_status":
                response = await self.http_client.get(f"/api/v1/qa/projects/{tool_input['project_id']}/status")
                return response.json() if response.status_code == 200 else {"status": None}
            elif tool_name == "approve_qa":
                response = await self.http_client.post(f"/api/v1/qa/reviews/{tool_input['review_id']}/approve", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
