from typing import Any
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class ReportAgent(BaseAgent):
    """Agent for generating and distributing reports with dashboard capture."""

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
        prompt = """You are an expert report generator and communicator. Create clear, actionable reports.

You have browser automation to capture dashboard screenshots for visual reports."""
        if self.language != "en":
            prompt += f"\n\nPrimary language: {self.language}"
        return prompt

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "generate_report", "description": "Generate report.", "input_schema": {"type": "object", "properties": {"report_type": {"type": "string", "enum": ["project_status", "campaign", "client_summary", "resource", "budget", "milestone", "risk"]}, "project_id": {"type": "string"}, "client_id": {"type": "string"}, "date_range": {"type": "object"}, "compare_to": {"type": "string", "enum": ["previous_period", "last_year", "target"]}}, "required": ["report_type"]}},
            {"name": "format_for_channel", "description": "Format report for channel.", "input_schema": {"type": "object", "properties": {"report_id": {"type": "string"}, "report_content": {"type": "object"}, "channel": {"type": "string", "enum": ["whatsapp", "email", "slack", "sms"]}, "include_charts": {"type": "boolean", "default": True}}, "required": ["channel"]}},
            {"name": "send_report", "description": "Send report via gateway.", "input_schema": {"type": "object", "properties": {"report_id": {"type": "string"}, "formatted_content": {"type": "object"}, "channel": {"type": "string", "enum": ["whatsapp", "email", "slack", "sms"]}, "recipients": {"type": "array", "items": {"type": "string"}}, "schedule": {"type": "string"}}, "required": ["channel", "recipients"]}},
            {"name": "get_project_data", "description": "Fetch project data.", "input_schema": {"type": "object", "properties": {"project_id": {"type": "string"}, "include": {"type": "array", "items": {"type": "string"}}}, "required": ["project_id"]}},
            {"name": "get_campaign_metrics", "description": "Fetch campaign metrics.", "input_schema": {"type": "object", "properties": {"campaign_id": {"type": "string"}, "project_id": {"type": "string"}, "metrics": {"type": "array", "items": {"type": "string"}}}, "required": []}},
            {"name": "schedule_recurring", "description": "Schedule recurring report.", "input_schema": {"type": "object", "properties": {"report_config": {"type": "object"}, "frequency": {"type": "string", "enum": ["daily", "weekly", "biweekly", "monthly"]}, "day_of_week": {"type": "integer"}, "time": {"type": "string"}, "channel": {"type": "string", "enum": ["whatsapp", "email", "slack", "sms"]}, "recipients": {"type": "array", "items": {"type": "string"}}}, "required": ["report_config", "frequency", "channel", "recipients"]}},
            {"name": "save_report", "description": "Save report.", "input_schema": {"type": "object", "properties": {"report_id": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "object"}, "report_type": {"type": "string"}, "project_id": {"type": "string"}, "client_id": {"type": "string"}}, "required": ["title", "content", "report_type"]}},
            {"name": "capture_analytics_dashboard", "description": "Screenshot analytics dashboard.", "input_schema": {"type": "object", "properties": {"dashboard_url": {"type": "string"}, "report_name": {"type": "string"}}, "required": ["dashboard_url"]}},
            {"name": "capture_platform_stats", "description": "Screenshot platform stats page.", "input_schema": {"type": "object", "properties": {"platform_url": {"type": "string"}, "platform": {"type": "string"}}, "required": ["platform_url"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
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
            elif tool_name == "capture_analytics_dashboard":
                return await self._capture_dashboard(tool_input["dashboard_url"], tool_input.get("report_name", "analytics"))
            elif tool_name == "capture_platform_stats":
                return await self._capture_platform(tool_input["platform_url"], tool_input.get("platform", "platform"))
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_dashboard(self, url: str, name: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(5000)  # Let charts render
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"dashboard_{name}")
            return {"url": url, "screenshot": screenshot_path, "success": True}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_platform(self, url: str, platform: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(3000)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/report_proofs", prefix=f"stats_{platform}")
            return {"url": url, "platform": platform, "screenshot": screenshot_path, "success": True}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
