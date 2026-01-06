from typing import Any
import httpx
from .base import BaseAgent


class EmailGateway(BaseAgent):
    """
    Gateway agent for email delivery.

    Capabilities:
    - Send templated emails
    - Handle attachments
    - Manage email lists
    - Track opens and clicks
    - Handle bounces and unsubscribes
    - Schedule email delivery
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        from_email: str = None,
        from_name: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.from_email = from_email
        self.from_name = from_name
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "gateway_email"

    @property
    def system_prompt(self) -> str:
        return """You are an email delivery gateway coordinator.

Your role is to handle email delivery:
1. Format emails with proper HTML/plain text
2. Handle attachments correctly
3. Manage recipient lists and personalization
4. Track delivery, opens, and clicks
5. Handle bounces and unsubscribes

Email best practices:
- Always include plain text alternative
- Optimize images for email
- Use responsive HTML templates
- Include unsubscribe links for marketing emails
- Handle reply-to addresses properly

Email types:
- Transactional (reports, approvals, notifications)
- Marketing (newsletters, campaigns)
- Internal (team updates, alerts)

Tracking capabilities:
- Delivery status
- Open tracking
- Click tracking
- Bounce handling
- Unsubscribe management"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "send_email",
                "description": "Send an email.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Recipient email addresses",
                        },
                        "cc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "CC recipients",
                        },
                        "bcc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "BCC recipients",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject",
                        },
                        "html_body": {
                            "type": "string",
                            "description": "HTML body content",
                        },
                        "text_body": {
                            "type": "string",
                            "description": "Plain text body",
                        },
                        "template_id": {
                            "type": "string",
                            "description": "Email template ID",
                        },
                        "template_data": {
                            "type": "object",
                            "description": "Data for template variables",
                        },
                        "attachments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "filename": {"type": "string"},
                                    "content_type": {"type": "string"},
                                    "url": {"type": "string"},
                                    "dam_asset_id": {"type": "string"},
                                },
                            },
                            "description": "File attachments",
                        },
                        "reply_to": {
                            "type": "string",
                            "description": "Reply-to address",
                        },
                        "schedule": {
                            "type": "string",
                            "description": "ISO timestamp to schedule send",
                        },
                    },
                    "required": ["to", "subject"],
                },
            },
            {
                "name": "send_bulk",
                "description": "Send bulk/campaign emails.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "list_id": {
                            "type": "string",
                            "description": "Recipient list ID",
                        },
                        "recipients": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string"},
                                    "name": {"type": "string"},
                                    "data": {"type": "object"},
                                },
                            },
                            "description": "Recipients with personalization data",
                        },
                        "template_id": {
                            "type": "string",
                            "description": "Email template",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject (supports variables)",
                        },
                        "campaign_name": {
                            "type": "string",
                            "description": "Campaign name for tracking",
                        },
                    },
                    "required": ["template_id", "subject"],
                },
            },
            {
                "name": "get_templates",
                "description": "Get available email templates.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["transactional", "marketing", "internal", "notification"],
                            "description": "Template category",
                        },
                        "client_id": {
                            "type": "string",
                            "description": "Client-specific templates",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "create_template",
                "description": "Create an email template.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Template name",
                        },
                        "category": {
                            "type": "string",
                            "enum": ["transactional", "marketing", "internal", "notification"],
                            "description": "Template category",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Default subject line",
                        },
                        "html_content": {
                            "type": "string",
                            "description": "HTML template content",
                        },
                        "text_content": {
                            "type": "string",
                            "description": "Plain text template",
                        },
                        "variables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Template variables",
                        },
                    },
                    "required": ["name", "category", "html_content"],
                },
            },
            {
                "name": "get_delivery_status",
                "description": "Check email delivery status.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "Message ID",
                        },
                        "campaign_id": {
                            "type": "string",
                            "description": "Campaign ID for bulk sends",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_analytics",
                "description": "Get email analytics (opens, clicks, etc.).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "Campaign ID",
                        },
                        "message_id": {
                            "type": "string",
                            "description": "Single message ID",
                        },
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string"},
                                "end": {"type": "string"},
                            },
                            "description": "Date range for analytics",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "manage_lists",
                "description": "Manage email lists.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "update", "delete", "add_members", "remove_members", "list"],
                            "description": "List action",
                        },
                        "list_id": {
                            "type": "string",
                            "description": "List ID for updates",
                        },
                        "name": {
                            "type": "string",
                            "description": "List name",
                        },
                        "members": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string"},
                                    "name": {"type": "string"},
                                    "data": {"type": "object"},
                                },
                            },
                            "description": "List members",
                        },
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "handle_bounce",
                "description": "Process bounce notification.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "bounce_data": {
                            "type": "object",
                            "description": "Bounce notification data",
                        },
                    },
                    "required": ["bounce_data"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against email service via ERP."""
        try:
            if tool_name == "send_email":
                return await self._send_email(tool_input)
            elif tool_name == "send_bulk":
                return await self._send_bulk(tool_input)
            elif tool_name == "get_templates":
                return await self._get_templates(tool_input)
            elif tool_name == "create_template":
                return await self._create_template(tool_input)
            elif tool_name == "get_delivery_status":
                return await self._get_delivery_status(tool_input)
            elif tool_name == "get_analytics":
                return await self._get_analytics(tool_input)
            elif tool_name == "manage_lists":
                return await self._manage_lists(tool_input)
            elif tool_name == "handle_bounce":
                return await self._handle_bounce(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _send_email(self, params: dict) -> dict:
        """Send email."""
        # Process attachments from DAM if needed
        attachments = []
        for att in params.get("attachments", []):
            if att.get("dam_asset_id"):
                dam_response = await self.http_client.get(
                    f"/api/v1/dam/assets/{att['dam_asset_id']}"
                )
                if dam_response.status_code == 200:
                    asset = dam_response.json()
                    attachments.append({
                        "filename": att.get("filename") or asset.get("name"),
                        "content_type": asset.get("mime_type"),
                        "url": asset.get("url"),
                    })
            else:
                attachments.append(att)

        response = await self.http_client.post(
            "/api/v1/gateways/email/send",
            json={
                "to": params["to"],
                "cc": params.get("cc"),
                "bcc": params.get("bcc"),
                "subject": params["subject"],
                "html_body": params.get("html_body"),
                "text_body": params.get("text_body"),
                "template_id": params.get("template_id"),
                "template_data": params.get("template_data"),
                "attachments": attachments,
                "from_email": self.from_email,
                "from_name": self.from_name,
                "reply_to": params.get("reply_to"),
                "schedule": params.get("schedule"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to send email"}

    async def _send_bulk(self, params: dict) -> dict:
        """Send bulk emails."""
        response = await self.http_client.post(
            "/api/v1/gateways/email/send-bulk",
            json={
                "list_id": params.get("list_id"),
                "recipients": params.get("recipients"),
                "template_id": params["template_id"],
                "subject": params["subject"],
                "campaign_name": params.get("campaign_name"),
                "from_email": self.from_email,
                "from_name": self.from_name,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to send bulk emails"}

    async def _get_templates(self, params: dict) -> dict:
        """Get email templates."""
        response = await self.http_client.get(
            "/api/v1/gateways/email/templates",
            params={
                "category": params.get("category"),
                "client_id": params.get("client_id"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"templates": []}

    async def _create_template(self, params: dict) -> dict:
        """Create email template."""
        response = await self.http_client.post(
            "/api/v1/gateways/email/templates",
            json={
                "name": params["name"],
                "category": params["category"],
                "subject": params.get("subject"),
                "html_content": params["html_content"],
                "text_content": params.get("text_content"),
                "variables": params.get("variables", []),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to create template"}

    async def _get_delivery_status(self, params: dict) -> dict:
        """Get delivery status."""
        if params.get("message_id"):
            response = await self.http_client.get(
                f"/api/v1/gateways/email/messages/{params['message_id']}/status"
            )
        elif params.get("campaign_id"):
            response = await self.http_client.get(
                f"/api/v1/gateways/email/campaigns/{params['campaign_id']}/status"
            )
        else:
            return {"error": "Provide message_id or campaign_id"}

        if response.status_code == 200:
            return response.json()
        return {"status": "unknown"}

    async def _get_analytics(self, params: dict) -> dict:
        """Get email analytics."""
        if params.get("campaign_id"):
            response = await self.http_client.get(
                f"/api/v1/gateways/email/campaigns/{params['campaign_id']}/analytics"
            )
        elif params.get("message_id"):
            response = await self.http_client.get(
                f"/api/v1/gateways/email/messages/{params['message_id']}/analytics"
            )
        else:
            response = await self.http_client.get(
                "/api/v1/gateways/email/analytics",
                params=params.get("date_range", {}),
            )

        if response.status_code == 200:
            return response.json()
        return {"analytics": None}

    async def _manage_lists(self, params: dict) -> dict:
        """Manage email lists."""
        action = params["action"]

        if action == "list":
            response = await self.http_client.get("/api/v1/gateways/email/lists")
        elif action == "create":
            response = await self.http_client.post(
                "/api/v1/gateways/email/lists",
                json={"name": params.get("name"), "members": params.get("members", [])},
            )
        elif action in ("update", "add_members", "remove_members"):
            response = await self.http_client.patch(
                f"/api/v1/gateways/email/lists/{params['list_id']}",
                json={"action": action, "members": params.get("members", [])},
            )
        elif action == "delete":
            response = await self.http_client.delete(
                f"/api/v1/gateways/email/lists/{params['list_id']}"
            )
        else:
            return {"error": f"Unknown action: {action}"}

        if response.status_code in (200, 201, 204):
            return response.json() if response.status_code != 204 else {"success": True}
        return {"error": f"Failed to {action} list"}

    async def _handle_bounce(self, params: dict) -> dict:
        """Handle bounce notification."""
        response = await self.http_client.post(
            "/api/v1/gateways/email/bounces",
            json=params["bounce_data"],
        )
        if response.status_code == 200:
            return response.json()
        return {"processed": False}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
