from typing import Any
import httpx
from .base import BaseAgent


class WhatsAppGateway(BaseAgent):
    """
    Gateway agent for WhatsApp message delivery.

    Capabilities:
    - Send templated messages
    - Handle rich media (images, documents, videos)
    - Manage message queues
    - Track delivery status
    - Handle responses/callbacks
    - Manage contacts/groups
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        whatsapp_business_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.whatsapp_business_id = whatsapp_business_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "gateway_whatsapp"

    @property
    def system_prompt(self) -> str:
        return """You are a WhatsApp Business API gateway coordinator.

Your role is to handle WhatsApp message delivery:
1. Format messages for WhatsApp constraints
2. Use appropriate templates for business messages
3. Handle media attachments properly
4. Track delivery and read receipts
5. Manage response handling

WhatsApp constraints:
- Template messages required for initiating business conversations
- 24-hour session window for free-form messages
- Media size limits (images: 5MB, video: 16MB, documents: 100MB)
- Character limits vary by message type
- Interactive messages (buttons, lists) where appropriate

Message types:
- Text messages (with formatting)
- Template messages (pre-approved)
- Media messages (image, video, document, audio)
- Interactive messages (buttons, lists)
- Location messages
- Contact messages"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "send_message",
                "description": "Send a WhatsApp message.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Phone number with country code",
                        },
                        "message_type": {
                            "type": "string",
                            "enum": ["text", "template", "image", "video", "document", "audio", "interactive", "location"],
                            "description": "Type of message",
                        },
                        "content": {
                            "type": "object",
                            "description": "Message content (varies by type)",
                        },
                        "template_name": {
                            "type": "string",
                            "description": "Template name for template messages",
                        },
                        "template_params": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Template parameter values",
                        },
                    },
                    "required": ["recipient", "message_type"],
                },
            },
            {
                "name": "send_bulk",
                "description": "Send messages to multiple recipients.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recipients": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of phone numbers",
                        },
                        "template_name": {
                            "type": "string",
                            "description": "Template to use",
                        },
                        "personalization": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "recipient": {"type": "string"},
                                    "params": {"type": "array", "items": {"type": "string"}},
                                },
                            },
                            "description": "Per-recipient personalization",
                        },
                    },
                    "required": ["recipients", "template_name"],
                },
            },
            {
                "name": "upload_media",
                "description": "Upload media for WhatsApp messages.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "media_url": {
                            "type": "string",
                            "description": "URL of media to upload",
                        },
                        "dam_asset_id": {
                            "type": "string",
                            "description": "DAM asset ID to upload",
                        },
                        "media_type": {
                            "type": "string",
                            "enum": ["image", "video", "document", "audio"],
                            "description": "Type of media",
                        },
                    },
                    "required": ["media_type"],
                },
            },
            {
                "name": "get_templates",
                "description": "Get available message templates.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["marketing", "utility", "authentication"],
                            "description": "Template category",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["approved", "pending", "rejected"],
                            "description": "Template status",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "create_template",
                "description": "Create a new message template (requires approval).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Template name",
                        },
                        "category": {
                            "type": "string",
                            "enum": ["marketing", "utility", "authentication"],
                            "description": "Template category",
                        },
                        "language": {
                            "type": "string",
                            "description": "Template language code",
                        },
                        "components": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Template components (header, body, footer, buttons)",
                        },
                    },
                    "required": ["name", "category", "language", "components"],
                },
            },
            {
                "name": "get_delivery_status",
                "description": "Check message delivery status.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "Message ID to check",
                        },
                        "batch_id": {
                            "type": "string",
                            "description": "Batch ID for bulk sends",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "handle_webhook",
                "description": "Process incoming webhook (message/status update).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "webhook_data": {
                            "type": "object",
                            "description": "Webhook payload",
                        },
                    },
                    "required": ["webhook_data"],
                },
            },
            {
                "name": "manage_contacts",
                "description": "Manage WhatsApp contacts/groups.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["add", "remove", "list", "sync"],
                            "description": "Contact action",
                        },
                        "contacts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "phone": {"type": "string"},
                                    "name": {"type": "string"},
                                    "tags": {"type": "array", "items": {"type": "string"}},
                                },
                            },
                            "description": "Contact details",
                        },
                    },
                    "required": ["action"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against WhatsApp API via ERP."""
        try:
            if tool_name == "send_message":
                return await self._send_message(tool_input)
            elif tool_name == "send_bulk":
                return await self._send_bulk(tool_input)
            elif tool_name == "upload_media":
                return await self._upload_media(tool_input)
            elif tool_name == "get_templates":
                return await self._get_templates(tool_input)
            elif tool_name == "create_template":
                return await self._create_template(tool_input)
            elif tool_name == "get_delivery_status":
                return await self._get_delivery_status(tool_input)
            elif tool_name == "handle_webhook":
                return await self._handle_webhook(tool_input)
            elif tool_name == "manage_contacts":
                return await self._manage_contacts(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _send_message(self, params: dict) -> dict:
        """Send WhatsApp message."""
        response = await self.http_client.post(
            "/api/v1/gateways/whatsapp/send",
            json={
                "recipient": params["recipient"],
                "message_type": params["message_type"],
                "content": params.get("content"),
                "template_name": params.get("template_name"),
                "template_params": params.get("template_params"),
                "business_id": self.whatsapp_business_id,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to send message", "status": response.status_code}

    async def _send_bulk(self, params: dict) -> dict:
        """Send bulk messages."""
        response = await self.http_client.post(
            "/api/v1/gateways/whatsapp/send-bulk",
            json={
                "recipients": params["recipients"],
                "template_name": params["template_name"],
                "personalization": params.get("personalization", []),
                "business_id": self.whatsapp_business_id,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to send bulk messages"}

    async def _upload_media(self, params: dict) -> dict:
        """Upload media for WhatsApp."""
        if params.get("dam_asset_id"):
            # Get from DAM first
            dam_response = await self.http_client.get(
                f"/api/v1/dam/assets/{params['dam_asset_id']}"
            )
            if dam_response.status_code == 200:
                params["media_url"] = dam_response.json().get("url")

        response = await self.http_client.post(
            "/api/v1/gateways/whatsapp/media",
            json={
                "media_url": params.get("media_url"),
                "media_type": params["media_type"],
                "business_id": self.whatsapp_business_id,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to upload media"}

    async def _get_templates(self, params: dict) -> dict:
        """Get message templates."""
        response = await self.http_client.get(
            "/api/v1/gateways/whatsapp/templates",
            params={
                "category": params.get("category"),
                "status": params.get("status", "approved"),
                "business_id": self.whatsapp_business_id,
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"templates": [], "note": "No templates found"}

    async def _create_template(self, params: dict) -> dict:
        """Create message template."""
        response = await self.http_client.post(
            "/api/v1/gateways/whatsapp/templates",
            json={
                "name": params["name"],
                "category": params["category"],
                "language": params["language"],
                "components": params["components"],
                "business_id": self.whatsapp_business_id,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to create template"}

    async def _get_delivery_status(self, params: dict) -> dict:
        """Get delivery status."""
        if params.get("message_id"):
            response = await self.http_client.get(
                f"/api/v1/gateways/whatsapp/messages/{params['message_id']}/status"
            )
        elif params.get("batch_id"):
            response = await self.http_client.get(
                f"/api/v1/gateways/whatsapp/batches/{params['batch_id']}/status"
            )
        else:
            return {"error": "Provide message_id or batch_id"}

        if response.status_code == 200:
            return response.json()
        return {"status": "unknown"}

    async def _handle_webhook(self, params: dict) -> dict:
        """Handle incoming webhook."""
        webhook_data = params["webhook_data"]

        response = await self.http_client.post(
            "/api/v1/gateways/whatsapp/webhook/process",
            json=webhook_data,
        )
        if response.status_code == 200:
            return response.json()
        return {"processed": False, "data": webhook_data}

    async def _manage_contacts(self, params: dict) -> dict:
        """Manage contacts."""
        action = params["action"]

        if action == "list":
            response = await self.http_client.get(
                "/api/v1/gateways/whatsapp/contacts",
                params={"business_id": self.whatsapp_business_id},
            )
        elif action == "sync":
            response = await self.http_client.post(
                "/api/v1/gateways/whatsapp/contacts/sync",
                json={"business_id": self.whatsapp_business_id},
            )
        else:
            response = await self.http_client.post(
                f"/api/v1/gateways/whatsapp/contacts/{action}",
                json={
                    "contacts": params.get("contacts", []),
                    "business_id": self.whatsapp_business_id,
                },
            )

        if response.status_code in (200, 201):
            return response.json()
        return {"error": f"Failed to {action} contacts"}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
