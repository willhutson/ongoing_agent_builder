from typing import Any
import httpx
from .base import BaseAgent


class CommunityAgent(BaseAgent):
    """
    Agent for community management and the OCM unified inbox.

    Capabilities:
    - Manage social community interactions via unified inbox
    - AI-categorize incoming messages
    - Draft brand-voice responses
    - Send approved responses via platform APIs
    - Escalate sensitive issues to account managers
    - Track engagement metrics
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
        return """You are a community management expert powering the OCM unified inbox.

Your role is to build and nurture communities:
1. Monitor and triage the unified social inbox across platforms
2. AI-categorize messages (question, complaint, praise, spam)
3. Draft brand-voice responses that match the client's tone
4. Send approved responses via platform APIs
5. Escalate sensitive issues with context to account managers
6. Track engagement and response SLA metrics

When drafting responses:
- Always match the brand voice and tone guidelines
- Be empathetic for complaints, enthusiastic for praise
- Never make promises about refunds/changes without escalation
- Keep responses concise and platform-appropriate"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_inbox_summary",
                "description": "Get unread message counts, categories, and SLA status for a client's social inbox.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "platform": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "categorize_messages",
                "description": "AI-categorize a batch of inbox messages (question, complaint, praise, spam).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "messages": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "text": {"type": "string"},
                                },
                            },
                            "description": "Messages to categorize",
                        },
                    },
                    "required": ["messages"],
                },
            },
            {
                "name": "draft_response",
                "description": "Draft a brand-voice response to a social media comment or DM. Uses brand context from the client.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "message_text": {"type": "string"},
                        "category": {"type": "string"},
                        "client_id": {"type": "string"},
                        "tone": {
                            "type": "string",
                            "enum": ["helpful", "empathetic", "professional", "casual", "apologetic"],
                        },
                        "brand_guidelines": {
                            "type": "string",
                            "description": "Brand tone/voice notes",
                        },
                    },
                    "required": ["message_text", "client_id"],
                },
            },
            {
                "name": "send_response",
                "description": "Send an approved response via the platform API.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "response_text": {"type": "string"},
                        "platform": {"type": "string"},
                    },
                    "required": ["message_id", "response_text"],
                },
            },
            {
                "name": "escalate_message",
                "description": "Escalate a message to the account manager or create a brief for follow-up.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "reason": {"type": "string"},
                        "escalate_to": {
                            "type": "string",
                            "description": "User email or 'account_manager'",
                        },
                        "create_brief": {"type": "boolean", "default": False},
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

            if tool_name == "get_inbox_summary":
                params = {"client_id": client_id}
                if tool_input.get("platform"):
                    params["platform"] = tool_input["platform"]
                response = await self.http_client.get(
                    "/api/v1/social/inbox/summary", params=params,
                )
                return response.json() if response.status_code == 200 else {
                    "unread": 0, "categories": {}, "sla_status": "unknown",
                }

            elif tool_name == "categorize_messages":
                # LLM-based categorization — return structured prompt for the agent loop
                messages = tool_input["messages"]
                return {
                    "message_count": len(messages),
                    "messages": messages[:50],  # cap for token safety
                    "instruction": (
                        "Categorize each message as one of: question, complaint, praise, spam. "
                        "Return a JSON array of {id, category, confidence} objects."
                    ),
                }

            elif tool_name == "draft_response":
                # Fetch brand guidelines from ERP if not provided inline
                brand_guidelines = tool_input.get("brand_guidelines")
                if not brand_guidelines and client_id:
                    guidelines_resp = await self.http_client.get(
                        "/api/v1/content/brand-guidelines",
                        params={"client_id": client_id},
                    )
                    if guidelines_resp.status_code == 200:
                        brand_guidelines = guidelines_resp.json().get("tone", "")

                return {
                    "message_id": tool_input.get("message_id"),
                    "message_text": tool_input["message_text"],
                    "category": tool_input.get("category", "general"),
                    "tone": tool_input.get("tone", "professional"),
                    "brand_guidelines": brand_guidelines or "Professional, helpful tone",
                    "instruction": (
                        "Draft a brand-voice response to this message. "
                        "Match the requested tone and brand guidelines. "
                        "Keep it concise and platform-appropriate."
                    ),
                }

            elif tool_name == "send_response":
                response = await self.http_client.post(
                    f"/api/v1/social/messages/{tool_input['message_id']}/reply",
                    json={
                        "response_text": tool_input["response_text"],
                        "platform": tool_input.get("platform"),
                    },
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to send"}

            elif tool_name == "escalate_message":
                response = await self.http_client.post(
                    f"/api/v1/social/messages/{tool_input['message_id']}/escalate",
                    json={
                        "reason": tool_input["reason"],
                        "escalate_to": tool_input.get("escalate_to", "account_manager"),
                        "create_brief": tool_input.get("create_brief", False),
                    },
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to escalate"}

            elif tool_name == "get_engagement_metrics":
                response = await self.http_client.get(
                    "/api/v1/social/engagement",
                    params={**tool_input, "client_id": client_id},
                )
                return response.json() if response.status_code == 200 else {"metrics": None}

            elif tool_name == "tag_message":
                response = await self.http_client.post(
                    f"/api/v1/social/messages/{tool_input['message_id']}/tags",
                    json={"tags": tool_input["tags"]},
                )
                return response.json() if response.status_code == 200 else {"error": "Failed to tag"}

            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
