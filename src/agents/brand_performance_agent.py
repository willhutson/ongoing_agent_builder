from typing import Any
import httpx
from .base import BaseAgent


class BrandPerformanceAgent(BaseAgent):
    """
    Agent for brand performance tracking.

    Capabilities:
    - Track brand health metrics
    - Measure brand awareness
    - Analyze brand perception
    - Monitor brand equity
    - Generate brand reports
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        client_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "brand_performance_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a brand performance expert.

Your role is to measure and optimize brand health:
1. Track brand health metrics
2. Measure awareness and recall
3. Analyze perception and sentiment
4. Monitor brand equity over time
5. Provide strategic insights"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_brand_health",
                "description": "Get brand health score.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "date_range": {"type": "object"},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_awareness_metrics",
                "description": "Get brand awareness metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "metrics": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_perception",
                "description": "Analyze brand perception.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "sources": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [],
                },
            },
            {
                "name": "track_brand_equity",
                "description": "Track brand equity over time.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "date_range": {"type": "object"},
                        "compare_to": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "generate_brand_report",
                "description": "Generate brand performance report.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "date_range": {"type": "object"},
                        "include": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id
            if tool_name == "get_brand_health":
                response = await self.http_client.get("/api/v1/performance/brand/health", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"health": None}
            elif tool_name == "get_awareness_metrics":
                response = await self.http_client.get("/api/v1/performance/brand/awareness", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"awareness": None}
            elif tool_name == "analyze_perception":
                return {"status": "ready_to_analyze", "instruction": "Analyze brand perception from multiple sources."}
            elif tool_name == "track_brand_equity":
                response = await self.http_client.get("/api/v1/performance/brand/equity", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"equity": None}
            elif tool_name == "generate_brand_report":
                return {"status": "ready_to_generate", "instruction": "Generate comprehensive brand performance report."}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
