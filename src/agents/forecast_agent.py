from typing import Any
import httpx
from .base import BaseAgent


class ForecastAgent(BaseAgent):
    """Agent for financial forecasting."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "forecast_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a financial forecasting expert. Create revenue and resource forecasts."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "generate_forecast", "description": "Generate financial forecast.", "input_schema": {"type": "object", "properties": {"forecast_type": {"type": "string", "enum": ["revenue", "expense", "resource"]}, "period": {"type": "string"}}, "required": ["forecast_type"]}},
            {"name": "get_pipeline", "description": "Get revenue pipeline.", "input_schema": {"type": "object", "properties": {"date_range": {"type": "object"}}, "required": []}},
            {"name": "analyze_trends", "description": "Analyze financial trends.", "input_schema": {"type": "object", "properties": {"metric": {"type": "string"}, "date_range": {"type": "object"}}, "required": ["metric"]}},
            {"name": "scenario_analysis", "description": "Run scenario analysis.", "input_schema": {"type": "object", "properties": {"scenarios": {"type": "array", "items": {"type": "object"}}}, "required": ["scenarios"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "generate_forecast":
                return {"status": "ready_to_forecast", "instruction": "Generate financial forecast with assumptions."}
            elif tool_name == "get_pipeline":
                response = await self.http_client.get("/api/v1/finance/pipeline", params=tool_input)
                return response.json() if response.status_code == 200 else {"pipeline": []}
            elif tool_name == "analyze_trends":
                response = await self.http_client.get("/api/v1/finance/trends", params=tool_input)
                return response.json() if response.status_code == 200 else {"trends": None}
            elif tool_name == "scenario_analysis":
                return {"status": "ready_to_analyze", "instruction": "Run scenario analysis with provided parameters."}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
