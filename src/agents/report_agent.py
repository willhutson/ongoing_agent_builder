from typing import Any
import httpx
from .base import BaseAgent


class ReportAgent(BaseAgent):
    """
    Agent for generating and distributing reports.

    Capabilities:
    - Generate project status reports
    - Create campaign performance reports
    - Build client-facing summaries
    - Format reports for different channels
    - Schedule automated reporting
    - Distribute via gateways (WhatsApp, Email, Slack, SMS)
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        language: str = "en",
        client_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.language = language
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "report_agent"

    @property
    def system_prompt(self) -> str:
        base_prompt = """You are an expert report generator and communicator.

Your role is to create clear, actionable reports that:
1. Summarize complex data into digestible insights
2. Highlight key metrics and KPIs
3. Identify trends and anomalies
4. Provide actionable recommendations
5. Format appropriately for the delivery channel

Report types you generate:
- Project status updates (daily, weekly, monthly)
- Campaign performance reports
- Client deliverable summaries
- Resource utilization reports
- Budget/financial summaries
- Milestone completion reports
- Risk/issue reports

Format considerations by channel:
- WhatsApp: Concise, bullet points, key metrics only
- Email: Structured, detailed, with attachments
- Slack: Threaded updates, interactive elements
- SMS: Ultra-brief, critical info only

Always include:
- Report period/date
- Key highlights (3-5 bullets)
- Metrics with comparisons
- Next steps/actions required
- Link to detailed report (when applicable)"""

        if self.language != "en":
            base_prompt += f"\n\nPrimary language: {self.language}"
        if self.client_specific_id:
            base_prompt += f"\n\nApply client-specific reporting preferences for client: {self.client_specific_id}"

        return base_prompt

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_report",
                "description": "Generate a report from project/campaign data.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_type": {
                            "type": "string",
                            "enum": ["project_status", "campaign", "client_summary", "resource", "budget", "milestone", "risk"],
                            "description": "Type of report to generate",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project to report on",
                        },
                        "client_id": {
                            "type": "string",
                            "description": "Client to report on",
                        },
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string"},
                                "end": {"type": "string"},
                            },
                            "description": "Report period",
                        },
                        "compare_to": {
                            "type": "string",
                            "enum": ["previous_period", "last_year", "target"],
                            "description": "Comparison baseline",
                        },
                    },
                    "required": ["report_type"],
                },
            },
            {
                "name": "format_for_channel",
                "description": "Format a report for a specific delivery channel.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_id": {
                            "type": "string",
                            "description": "Report to format",
                        },
                        "report_content": {
                            "type": "object",
                            "description": "Report content if no ID",
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["whatsapp", "email", "slack", "sms"],
                            "description": "Target channel",
                        },
                        "include_charts": {
                            "type": "boolean",
                            "description": "Include visual charts",
                            "default": True,
                        },
                    },
                    "required": ["channel"],
                },
            },
            {
                "name": "send_report",
                "description": "Send report via specified channel gateway.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_id": {
                            "type": "string",
                            "description": "Report to send",
                        },
                        "formatted_content": {
                            "type": "object",
                            "description": "Pre-formatted content",
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["whatsapp", "email", "slack", "sms"],
                            "description": "Delivery channel",
                        },
                        "recipients": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Recipient identifiers",
                        },
                        "schedule": {
                            "type": "string",
                            "description": "ISO timestamp to schedule send",
                        },
                    },
                    "required": ["channel", "recipients"],
                },
            },
            {
                "name": "get_project_data",
                "description": "Fetch project data for reporting.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project ID",
                        },
                        "include": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Data to include: tasks, milestones, budget, resources, timeline",
                        },
                    },
                    "required": ["project_id"],
                },
            },
            {
                "name": "get_campaign_metrics",
                "description": "Fetch campaign performance metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "Campaign ID",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project to get campaigns from",
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to fetch: impressions, clicks, conversions, spend, roas",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "schedule_recurring",
                "description": "Set up recurring report delivery.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_config": {
                            "type": "object",
                            "description": "Report generation configuration",
                        },
                        "frequency": {
                            "type": "string",
                            "enum": ["daily", "weekly", "biweekly", "monthly"],
                            "description": "Report frequency",
                        },
                        "day_of_week": {
                            "type": "integer",
                            "description": "Day for weekly reports (0=Monday)",
                        },
                        "time": {
                            "type": "string",
                            "description": "Time to send (HH:MM)",
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["whatsapp", "email", "slack", "sms"],
                        },
                        "recipients": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["report_config", "frequency", "channel", "recipients"],
                },
            },
            {
                "name": "save_report",
                "description": "Save report to ERP.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_id": {
                            "type": "string",
                            "description": "Report ID if updating",
                        },
                        "title": {"type": "string"},
                        "content": {"type": "object"},
                        "report_type": {"type": "string"},
                        "project_id": {"type": "string"},
                        "client_id": {"type": "string"},
                    },
                    "required": ["title", "content", "report_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "generate_report":
                return await self._generate_report(tool_input)
            elif tool_name == "format_for_channel":
                return await self._format_for_channel(tool_input)
            elif tool_name == "send_report":
                return await self._send_report(tool_input)
            elif tool_name == "get_project_data":
                return await self._get_project_data(tool_input)
            elif tool_name == "get_campaign_metrics":
                return await self._get_campaign_metrics(tool_input)
            elif tool_name == "schedule_recurring":
                return await self._schedule_recurring(tool_input)
            elif tool_name == "save_report":
                return await self._save_report(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _generate_report(self, params: dict) -> dict:
        """Generate report from data."""
        project_data = None
        if params.get("project_id"):
            response = await self.http_client.get(
                f"/api/v1/projects/{params['project_id']}",
                params={"include": "tasks,milestones,budget,resources"},
            )
            if response.status_code == 200:
                project_data = response.json()

        client_data = None
        if params.get("client_id"):
            response = await self.http_client.get(
                f"/api/v1/clients/{params['client_id']}/summary"
            )
            if response.status_code == 200:
                client_data = response.json()

        return {
            "status": "ready_to_generate",
            "report_type": params["report_type"],
            "project_data": project_data,
            "client_data": client_data,
            "date_range": params.get("date_range"),
            "compare_to": params.get("compare_to"),
            "language": self.language,
            "instruction": f"Generate a {params['report_type']} report with insights and recommendations.",
        }

    async def _format_for_channel(self, params: dict) -> dict:
        """Format report for channel."""
        report = None
        if params.get("report_id"):
            response = await self.http_client.get(
                f"/api/v1/reporting/reports/{params['report_id']}"
            )
            if response.status_code == 200:
                report = response.json()
        else:
            report = params.get("report_content")

        return {
            "status": "ready_to_format",
            "report": report,
            "channel": params["channel"],
            "include_charts": params.get("include_charts", True),
            "instruction": f"Format report for {params['channel']} delivery with appropriate length and structure.",
        }

    async def _send_report(self, params: dict) -> dict:
        """Send report via gateway."""
        response = await self.http_client.post(
            f"/api/v1/gateways/{params['channel']}/send",
            json={
                "report_id": params.get("report_id"),
                "content": params.get("formatted_content"),
                "recipients": params["recipients"],
                "schedule": params.get("schedule"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": f"Failed to send via {params['channel']}"}

    async def _get_project_data(self, params: dict) -> dict:
        """Get project data."""
        include = ",".join(params.get("include", ["tasks", "milestones", "budget"]))
        response = await self.http_client.get(
            f"/api/v1/projects/{params['project_id']}",
            params={"include": include},
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Project not found"}

    async def _get_campaign_metrics(self, params: dict) -> dict:
        """Get campaign metrics."""
        if params.get("campaign_id"):
            response = await self.http_client.get(
                f"/api/v1/campaigns/{params['campaign_id']}/metrics"
            )
        elif params.get("project_id"):
            response = await self.http_client.get(
                f"/api/v1/projects/{params['project_id']}/campaigns/metrics"
            )
        else:
            return {"error": "Provide campaign_id or project_id"}

        if response.status_code == 200:
            return response.json()
        return {"metrics": None, "note": "No metrics found"}

    async def _schedule_recurring(self, params: dict) -> dict:
        """Schedule recurring report."""
        response = await self.http_client.post(
            "/api/v1/reporting/schedules",
            json={
                "report_config": params["report_config"],
                "frequency": params["frequency"],
                "day_of_week": params.get("day_of_week"),
                "time": params.get("time", "09:00"),
                "channel": params["channel"],
                "recipients": params["recipients"],
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to schedule recurring report"}

    async def _save_report(self, params: dict) -> dict:
        """Save report."""
        response = await self.http_client.post(
            "/api/v1/reporting/reports",
            json={
                "title": params["title"],
                "content": params["content"],
                "report_type": params["report_type"],
                "project_id": params.get("project_id"),
                "client_id": params.get("client_id") or self.client_specific_id,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to save report"}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
