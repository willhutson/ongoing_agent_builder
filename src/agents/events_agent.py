from typing import Any
import httpx
from .base import BaseAgent


class EventsAgent(BaseAgent):
    """Agent for event planning and management."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, client_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "events_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an event planning expert. Plan, execute, and measure events."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "create_event", "description": "Create event.", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}, "type": {"type": "string"}, "date": {"type": "string"}, "venue": {"type": "string"}}, "required": ["name", "date"]}},
            {"name": "manage_rsvp", "description": "Manage RSVPs.", "input_schema": {"type": "object", "properties": {"event_id": {"type": "string"}, "action": {"type": "string"}}, "required": ["event_id", "action"]}},
            {"name": "create_run_of_show", "description": "Create run of show.", "input_schema": {"type": "object", "properties": {"event_id": {"type": "string"}, "items": {"type": "array", "items": {"type": "object"}}}, "required": ["event_id"]}},
            {"name": "manage_vendors", "description": "Manage event vendors.", "input_schema": {"type": "object", "properties": {"event_id": {"type": "string"}, "vendors": {"type": "array", "items": {"type": "object"}}}, "required": ["event_id"]}},
            {"name": "track_budget", "description": "Track event budget.", "input_schema": {"type": "object", "properties": {"event_id": {"type": "string"}}, "required": ["event_id"]}},
            {"name": "measure_success", "description": "Measure event success.", "input_schema": {"type": "object", "properties": {"event_id": {"type": "string"}, "metrics": {"type": "array", "items": {"type": "string"}}}, "required": ["event_id"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "create_event":
                response = await self.http_client.post("/api/v1/events", json={**tool_input, "client_id": self.client_specific_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "manage_rsvp":
                response = await self.http_client.get(f"/api/v1/events/{tool_input['event_id']}/rsvp") if tool_input["action"] == "list" else await self.http_client.post(f"/api/v1/events/{tool_input['event_id']}/rsvp", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "create_run_of_show":
                response = await self.http_client.post(f"/api/v1/events/{tool_input['event_id']}/run-of-show", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "manage_vendors":
                response = await self.http_client.post(f"/api/v1/events/{tool_input['event_id']}/vendors", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "track_budget":
                response = await self.http_client.get(f"/api/v1/events/{tool_input['event_id']}/budget")
                return response.json() if response.status_code == 200 else {"budget": None}
            elif tool_name == "measure_success":
                return {"status": "ready_to_measure", "instruction": "Measure event success against objectives."}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
