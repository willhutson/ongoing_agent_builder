from typing import Any
import httpx
from .base import BaseAgent


class CommunityAgent(BaseAgent):
    """
    Agent for community management.

    Capabilities:
    - Manage social community interactions
    - Handle customer inquiries
    - Generate response suggestions
    - Track engagement
    - Escalate issues
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
        return "community_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a community management expert.

Your role is to build and nurture communities:
1. Respond to community interactions
2. Handle customer inquiries
3. Generate appropriate responses
4. Track engagement metrics
5. Escalate sensitive issues"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_inbox",
                "description": "Get social inbox messages.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "platform": {"type": "string"},
                        "status": {"type": "string", "enum": ["unread", "pending", "resolved", "all"]},
                    },
                    "required": [],
                },
            },
            {
                "name": "generate_response",
                "description": "Generate response suggestion.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "message_content": {"type": "string"},
                        "tone": {"type": "string"},
                    },
                    "required": ["message_content"],
                },
            },
            {
                "name": "send_response",
                "description": "Send response to message.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "response": {"type": "string"},
                        "platform": {"type": "string"},
                    },
                    "required": ["message_id", "response"],
                },
            },
            {
                "name": "escalate_issue",
                "description": "Escalate issue to team.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "reason": {"type": "string"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    },
                    "required": ["message_id", "reason"],
                },
            },
            {
                "name": "get_engagement_metrics",
                "description": "Get community engagement metrics.",
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
                "name": "tag_message",
                "description": "Tag/categorize message.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["message_id", "tags"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id
            if tool_name == "get_inbox":
                response = await self.http_client.get("/api/v1/social/inbox", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"messages": []}
            elif tool_name == "generate_response":
                return {
                    "status": "ready_to_generate",
                    "message": tool_input["message_content"],
                    "instruction": "Generate appropriate response matching brand voice.",
                }
            elif tool_name == "send_response":
                response = await self.http_client.post(f"/api/v1/social/messages/{tool_input['message_id']}/reply", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to send"}
            elif tool_name == "escalate_issue":
                response = await self.http_client.post(f"/api/v1/social/messages/{tool_input['message_id']}/escalate", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed to escalate"}
            elif tool_name == "get_engagement_metrics":
                response = await self.http_client.get("/api/v1/social/engagement", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"metrics": None}
            elif tool_name == "tag_message":
                response = await self.http_client.post(f"/api/v1/social/messages/{tool_input['message_id']}/tags", json={"tags": tool_input["tags"]})
                return response.json() if response.status_code == 200 else {"error": "Failed to tag"}
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
