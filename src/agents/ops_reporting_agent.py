from typing import Any
import httpx
from .base import BaseAgent


class OpsReportingAgent(BaseAgent):
    """
    Agent for operations reporting and analytics.

    Capabilities:
    - Generate operational reports
    - Track KPIs and metrics
    - Create dashboards
    - Analyze trends
    - Alert on anomalies
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "ops_reporting_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an operations reporting expert.

Your role is to provide operational insights:
1. Generate performance reports
2. Track operational KPIs
3. Identify trends and anomalies
4. Create executive dashboards
5. Provide actionable recommendations"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_ops_report",
                "description": "Generate operations report.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_type": {"type": "string", "enum": ["utilization", "delivery", "quality", "financial", "comprehensive"]},
                        "date_range": {"type": "object"},
                        "filters": {"type": "object"},
                    },
                    "required": ["report_type"],
                },
            },
            {
                "name": "get_kpis",
                "description": "Get operational KPIs.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "kpi_names": {"type": "array", "items": {"type": "string"}},
                        "date_range": {"type": "object"},
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_trends",
                "description": "Analyze operational trends.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "metric": {"type": "string"},
                        "date_range": {"type": "object"},
                        "granularity": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                    },
                    "required": ["metric"],
                },
            },
            {
                "name": "get_alerts",
                "description": "Get operational alerts.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                        "acknowledged": {"type": "boolean"},
                    },
                    "required": [],
                },
            },
            {
                "name": "create_dashboard",
                "description": "Create dashboard configuration.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "widgets": {"type": "array", "items": {"type": "object"}},
                    },
                    "required": ["name", "widgets"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "generate_ops_report":
                response = await self.http_client.get("/api/v1/reporting/operations", params=tool_input)
                if response.status_code == 200:
                    return response.json()
                return {"status": "ready_to_generate", "instruction": "Generate operations report with insights."}
            elif tool_name == "get_kpis":
                response = await self.http_client.get("/api/v1/reporting/kpis", params=tool_input)
                return response.json() if response.status_code == 200 else {"kpis": []}
            elif tool_name == "analyze_trends":
                response = await self.http_client.get("/api/v1/reporting/trends", params=tool_input)
                return response.json() if response.status_code == 200 else {"trends": []}
            elif tool_name == "get_alerts":
                response = await self.http_client.get("/api/v1/reporting/alerts", params=tool_input)
                return response.json() if response.status_code == 200 else {"alerts": []}
            elif tool_name == "create_dashboard":
                response = await self.http_client.post("/api/v1/reporting/dashboards", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
