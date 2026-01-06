from typing import Any
import httpx
from .base import BaseAgent


class OnboardingAgent(BaseAgent):
    """
    Agent for client onboarding.

    Capabilities:
    - Guide client onboarding process
    - Collect required information
    - Set up client accounts
    - Create initial brand profiles
    - Track onboarding progress
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
        return "onboarding_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a client onboarding specialist.

Your role is to ensure smooth client onboarding:
1. Guide through onboarding steps
2. Collect required information
3. Set up accounts and access
4. Create initial brand profiles
5. Track progress and follow up"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "start_onboarding",
                "description": "Start new client onboarding.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string"},
                        "contact_email": {"type": "string"},
                        "industry": {"type": "string"},
                    },
                    "required": ["client_name", "contact_email"],
                },
            },
            {
                "name": "get_onboarding_status",
                "description": "Get onboarding progress.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "onboarding_id": {"type": "string"},
                        "client_id": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "complete_step",
                "description": "Mark onboarding step complete.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "onboarding_id": {"type": "string"},
                        "step": {"type": "string"},
                        "data": {"type": "object"},
                    },
                    "required": ["onboarding_id", "step"],
                },
            },
            {
                "name": "create_client_account",
                "description": "Create client account in ERP.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "onboarding_id": {"type": "string"},
                        "client_data": {"type": "object"},
                    },
                    "required": ["onboarding_id", "client_data"],
                },
            },
            {
                "name": "setup_brand_profile",
                "description": "Set up initial brand profile.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "brand_data": {"type": "object"},
                    },
                    "required": ["client_id"],
                },
            },
            {
                "name": "send_onboarding_email",
                "description": "Send onboarding communication.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "onboarding_id": {"type": "string"},
                        "email_type": {"type": "string", "enum": ["welcome", "reminder", "completion", "questionnaire"]},
                    },
                    "required": ["onboarding_id", "email_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "start_onboarding":
                response = await self.http_client.post("/api/v1/onboarding", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to start"}
            elif tool_name == "get_onboarding_status":
                if tool_input.get("onboarding_id"):
                    response = await self.http_client.get(f"/api/v1/onboarding/{tool_input['onboarding_id']}")
                else:
                    response = await self.http_client.get("/api/v1/onboarding", params=tool_input)
                return response.json() if response.status_code == 200 else {"status": "not_found"}
            elif tool_name == "complete_step":
                response = await self.http_client.post(f"/api/v1/onboarding/{tool_input['onboarding_id']}/steps/{tool_input['step']}/complete", json=tool_input.get("data", {}))
                return response.json() if response.status_code == 200 else {"error": "Failed to complete step"}
            elif tool_name == "create_client_account":
                response = await self.http_client.post(f"/api/v1/onboarding/{tool_input['onboarding_id']}/create-account", json=tool_input["client_data"])
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create account"}
            elif tool_name == "setup_brand_profile":
                response = await self.http_client.post(f"/api/v1/clients/{tool_input['client_id']}/brand", json=tool_input.get("brand_data", {}))
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to setup brand"}
            elif tool_name == "send_onboarding_email":
                response = await self.http_client.post(f"/api/v1/onboarding/{tool_input['onboarding_id']}/emails/{tool_input['email_type']}")
                return response.json() if response.status_code == 200 else {"error": "Failed to send email"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
