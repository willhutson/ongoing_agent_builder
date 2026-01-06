from typing import Any
import httpx
from .base import BaseAgent


class SMSGateway(BaseAgent):
    """
    Gateway agent for SMS message delivery.

    Capabilities:
    - Send SMS messages
    - Handle MMS with media
    - Manage delivery status
    - Handle two-way messaging
    - Support for multiple providers
    - Handle opt-outs
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        from_number: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.from_number = from_number
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "gateway_sms"

    @property
    def system_prompt(self) -> str:
        return """You are an SMS/MMS gateway coordinator.

Your role is to handle SMS message delivery:
1. Send concise, effective SMS messages
2. Handle media for MMS
3. Track delivery status
4. Manage opt-outs and compliance
5. Handle incoming messages

SMS constraints:
- Standard SMS: 160 characters (GSM-7) or 70 characters (Unicode)
- Concatenated SMS: Multiple segments for longer messages
- MMS: Up to 1600 characters + media
- Carrier-specific limitations

Best practices:
- Keep messages concise
- Include clear call-to-action
- Respect opt-out requests
- Include sender identification
- Time-zone aware delivery

Compliance:
- Honor STOP/unsubscribe requests
- Include opt-out instructions for marketing
- Respect quiet hours
- Maintain consent records"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "send_sms",
                "description": "Send an SMS message.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Recipient phone number with country code",
                        },
                        "message": {
                            "type": "string",
                            "description": "Message text",
                        },
                        "media_urls": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Media URLs for MMS",
                        },
                        "dam_asset_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "DAM assets for MMS",
                        },
                        "schedule": {
                            "type": "string",
                            "description": "ISO timestamp to schedule",
                        },
                    },
                    "required": ["to", "message"],
                },
            },
            {
                "name": "send_bulk",
                "description": "Send SMS to multiple recipients.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recipients": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "phone": {"type": "string"},
                                    "name": {"type": "string"},
                                    "data": {"type": "object"},
                                },
                            },
                            "description": "Recipients with personalization",
                        },
                        "message_template": {
                            "type": "string",
                            "description": "Message with {{variables}}",
                        },
                        "campaign_name": {
                            "type": "string",
                            "description": "Campaign name for tracking",
                        },
                    },
                    "required": ["recipients", "message_template"],
                },
            },
            {
                "name": "get_delivery_status",
                "description": "Check SMS delivery status.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "Message ID",
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
                "name": "handle_incoming",
                "description": "Process incoming SMS.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "from_number": {
                            "type": "string",
                            "description": "Sender phone number",
                        },
                        "to_number": {
                            "type": "string",
                            "description": "Receiving number",
                        },
                        "message": {
                            "type": "string",
                            "description": "Message text",
                        },
                        "media_urls": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Incoming media URLs",
                        },
                    },
                    "required": ["from_number", "message"],
                },
            },
            {
                "name": "manage_optouts",
                "description": "Manage SMS opt-outs.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["check", "add", "remove", "list"],
                            "description": "Opt-out action",
                        },
                        "phone_number": {
                            "type": "string",
                            "description": "Phone number to check/modify",
                        },
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "get_analytics",
                "description": "Get SMS analytics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "Campaign ID",
                        },
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string"},
                                "end": {"type": "string"},
                            },
                            "description": "Date range",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "validate_number",
                "description": "Validate a phone number.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "Number to validate",
                        },
                    },
                    "required": ["phone_number"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against SMS service via ERP."""
        try:
            if tool_name == "send_sms":
                return await self._send_sms(tool_input)
            elif tool_name == "send_bulk":
                return await self._send_bulk(tool_input)
            elif tool_name == "get_delivery_status":
                return await self._get_delivery_status(tool_input)
            elif tool_name == "handle_incoming":
                return await self._handle_incoming(tool_input)
            elif tool_name == "manage_optouts":
                return await self._manage_optouts(tool_input)
            elif tool_name == "get_analytics":
                return await self._get_analytics(tool_input)
            elif tool_name == "validate_number":
                return await self._validate_number(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _send_sms(self, params: dict) -> dict:
        """Send SMS."""
        # Get media from DAM if needed
        media_urls = list(params.get("media_urls", []))
        for asset_id in params.get("dam_asset_ids", []):
            dam_response = await self.http_client.get(
                f"/api/v1/dam/assets/{asset_id}"
            )
            if dam_response.status_code == 200:
                media_urls.append(dam_response.json().get("url"))

        response = await self.http_client.post(
            "/api/v1/gateways/sms/send",
            json={
                "to": params["to"],
                "message": params["message"],
                "media_urls": media_urls if media_urls else None,
                "from_number": self.from_number,
                "schedule": params.get("schedule"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to send SMS"}

    async def _send_bulk(self, params: dict) -> dict:
        """Send bulk SMS."""
        response = await self.http_client.post(
            "/api/v1/gateways/sms/send-bulk",
            json={
                "recipients": params["recipients"],
                "message_template": params["message_template"],
                "campaign_name": params.get("campaign_name"),
                "from_number": self.from_number,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to send bulk SMS"}

    async def _get_delivery_status(self, params: dict) -> dict:
        """Get delivery status."""
        if params.get("message_id"):
            response = await self.http_client.get(
                f"/api/v1/gateways/sms/messages/{params['message_id']}/status"
            )
        elif params.get("batch_id"):
            response = await self.http_client.get(
                f"/api/v1/gateways/sms/batches/{params['batch_id']}/status"
            )
        else:
            return {"error": "Provide message_id or batch_id"}

        if response.status_code == 200:
            return response.json()
        return {"status": "unknown"}

    async def _handle_incoming(self, params: dict) -> dict:
        """Handle incoming SMS."""
        # Check for opt-out keywords
        message = params["message"].strip().upper()
        opt_out_keywords = ["STOP", "UNSUBSCRIBE", "CANCEL", "END", "QUIT"]

        if message in opt_out_keywords:
            await self._manage_optouts({
                "action": "add",
                "phone_number": params["from_number"],
            })
            return {
                "type": "opt_out",
                "from": params["from_number"],
                "handled": True,
            }

        # Process as regular incoming message
        response = await self.http_client.post(
            "/api/v1/gateways/sms/incoming",
            json={
                "from_number": params["from_number"],
                "to_number": params.get("to_number") or self.from_number,
                "message": params["message"],
                "media_urls": params.get("media_urls"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"processed": False, "message": params["message"]}

    async def _manage_optouts(self, params: dict) -> dict:
        """Manage opt-outs."""
        action = params["action"]

        if action == "list":
            response = await self.http_client.get("/api/v1/gateways/sms/optouts")
        elif action == "check":
            response = await self.http_client.get(
                f"/api/v1/gateways/sms/optouts/{params['phone_number']}"
            )
        elif action == "add":
            response = await self.http_client.post(
                "/api/v1/gateways/sms/optouts",
                json={"phone_number": params["phone_number"]},
            )
        elif action == "remove":
            response = await self.http_client.delete(
                f"/api/v1/gateways/sms/optouts/{params['phone_number']}"
            )
        else:
            return {"error": f"Unknown action: {action}"}

        if response.status_code in (200, 201, 204):
            return response.json() if response.status_code != 204 else {"success": True}
        return {"error": f"Failed to {action}"}

    async def _get_analytics(self, params: dict) -> dict:
        """Get SMS analytics."""
        if params.get("campaign_id"):
            response = await self.http_client.get(
                f"/api/v1/gateways/sms/campaigns/{params['campaign_id']}/analytics"
            )
        else:
            response = await self.http_client.get(
                "/api/v1/gateways/sms/analytics",
                params=params.get("date_range", {}),
            )

        if response.status_code == 200:
            return response.json()
        return {"analytics": None}

    async def _validate_number(self, params: dict) -> dict:
        """Validate phone number."""
        response = await self.http_client.post(
            "/api/v1/gateways/sms/validate",
            json={"phone_number": params["phone_number"]},
        )
        if response.status_code == 200:
            return response.json()
        return {"valid": False, "phone_number": params["phone_number"]}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
