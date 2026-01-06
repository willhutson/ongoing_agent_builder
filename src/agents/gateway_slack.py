from typing import Any
import httpx
from .base import BaseAgent


class SlackGateway(BaseAgent):
    """
    Gateway agent for Slack message delivery.

    Capabilities:
    - Send messages to channels and DMs
    - Handle rich formatting (blocks, attachments)
    - Manage interactive components
    - Handle slash commands
    - Track message delivery
    - Manage channel/user interactions
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        slack_workspace_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.slack_workspace_id = slack_workspace_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "gateway_slack"

    @property
    def system_prompt(self) -> str:
        return """You are a Slack integration gateway coordinator.

Your role is to handle Slack message delivery and interactions:
1. Send messages with rich formatting
2. Use Block Kit for complex layouts
3. Handle interactive components (buttons, menus)
4. Manage threads and replies
5. Process incoming events and commands

Slack formatting:
- Use Block Kit for structured messages
- mrkdwn for text formatting
- Attachments for legacy formatting
- Interactive components for user actions

Message types:
- Channel messages
- Direct messages
- Threaded replies
- Scheduled messages
- Ephemeral messages (visible only to one user)

Interactive components:
- Buttons
- Select menus
- Date pickers
- Overflow menus
- Modal dialogs"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "send_message",
                "description": "Send a Slack message.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Channel ID or name",
                        },
                        "user": {
                            "type": "string",
                            "description": "User ID for DM",
                        },
                        "text": {
                            "type": "string",
                            "description": "Message text (fallback for blocks)",
                        },
                        "blocks": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Block Kit blocks",
                        },
                        "attachments": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Legacy attachments",
                        },
                        "thread_ts": {
                            "type": "string",
                            "description": "Thread timestamp for replies",
                        },
                        "reply_broadcast": {
                            "type": "boolean",
                            "description": "Also send reply to channel",
                            "default": False,
                        },
                        "ephemeral_user": {
                            "type": "string",
                            "description": "User ID for ephemeral message",
                        },
                        "schedule": {
                            "type": "string",
                            "description": "Unix timestamp to schedule message",
                        },
                    },
                    "required": ["text"],
                },
            },
            {
                "name": "update_message",
                "description": "Update an existing message.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Channel containing the message",
                        },
                        "ts": {
                            "type": "string",
                            "description": "Message timestamp",
                        },
                        "text": {
                            "type": "string",
                            "description": "New text",
                        },
                        "blocks": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "New blocks",
                        },
                    },
                    "required": ["channel", "ts"],
                },
            },
            {
                "name": "send_file",
                "description": "Upload and share a file.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "channels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Channels to share to",
                        },
                        "file_url": {
                            "type": "string",
                            "description": "URL of file to upload",
                        },
                        "dam_asset_id": {
                            "type": "string",
                            "description": "DAM asset to share",
                        },
                        "filename": {
                            "type": "string",
                            "description": "Filename",
                        },
                        "title": {
                            "type": "string",
                            "description": "File title",
                        },
                        "initial_comment": {
                            "type": "string",
                            "description": "Comment with the file",
                        },
                        "thread_ts": {
                            "type": "string",
                            "description": "Thread to share in",
                        },
                    },
                    "required": ["channels"],
                },
            },
            {
                "name": "open_modal",
                "description": "Open a modal dialog.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "trigger_id": {
                            "type": "string",
                            "description": "Trigger ID from interaction",
                        },
                        "view": {
                            "type": "object",
                            "description": "Modal view definition",
                        },
                    },
                    "required": ["trigger_id", "view"],
                },
            },
            {
                "name": "handle_interaction",
                "description": "Process an interactive component callback.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "payload": {
                            "type": "object",
                            "description": "Interaction payload",
                        },
                    },
                    "required": ["payload"],
                },
            },
            {
                "name": "handle_slash_command",
                "description": "Process a slash command.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Slash command name",
                        },
                        "text": {
                            "type": "string",
                            "description": "Command text/arguments",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User who invoked",
                        },
                        "channel_id": {
                            "type": "string",
                            "description": "Channel context",
                        },
                        "trigger_id": {
                            "type": "string",
                            "description": "Trigger for modals",
                        },
                    },
                    "required": ["command", "user_id"],
                },
            },
            {
                "name": "get_channels",
                "description": "List available channels.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Channel types: public_channel, private_channel, im, mpim",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_users",
                "description": "List workspace users.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "add_reaction",
                "description": "Add emoji reaction to a message.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Channel ID",
                        },
                        "timestamp": {
                            "type": "string",
                            "description": "Message timestamp",
                        },
                        "emoji": {
                            "type": "string",
                            "description": "Emoji name (without colons)",
                        },
                    },
                    "required": ["channel", "timestamp", "emoji"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against Slack via ERP."""
        try:
            if tool_name == "send_message":
                return await self._send_message(tool_input)
            elif tool_name == "update_message":
                return await self._update_message(tool_input)
            elif tool_name == "send_file":
                return await self._send_file(tool_input)
            elif tool_name == "open_modal":
                return await self._open_modal(tool_input)
            elif tool_name == "handle_interaction":
                return await self._handle_interaction(tool_input)
            elif tool_name == "handle_slash_command":
                return await self._handle_slash_command(tool_input)
            elif tool_name == "get_channels":
                return await self._get_channels(tool_input)
            elif tool_name == "get_users":
                return await self._get_users(tool_input)
            elif tool_name == "add_reaction":
                return await self._add_reaction(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _send_message(self, params: dict) -> dict:
        """Send Slack message."""
        response = await self.http_client.post(
            "/api/v1/gateways/slack/send",
            json={
                "channel": params.get("channel"),
                "user": params.get("user"),
                "text": params["text"],
                "blocks": params.get("blocks"),
                "attachments": params.get("attachments"),
                "thread_ts": params.get("thread_ts"),
                "reply_broadcast": params.get("reply_broadcast", False),
                "ephemeral_user": params.get("ephemeral_user"),
                "schedule": params.get("schedule"),
                "workspace_id": self.slack_workspace_id,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to send message"}

    async def _update_message(self, params: dict) -> dict:
        """Update message."""
        response = await self.http_client.post(
            "/api/v1/gateways/slack/update",
            json={
                "channel": params["channel"],
                "ts": params["ts"],
                "text": params.get("text"),
                "blocks": params.get("blocks"),
                "workspace_id": self.slack_workspace_id,
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to update message"}

    async def _send_file(self, params: dict) -> dict:
        """Upload and share file."""
        file_url = params.get("file_url")

        if params.get("dam_asset_id"):
            dam_response = await self.http_client.get(
                f"/api/v1/dam/assets/{params['dam_asset_id']}"
            )
            if dam_response.status_code == 200:
                asset = dam_response.json()
                file_url = asset.get("url")
                if not params.get("filename"):
                    params["filename"] = asset.get("name")

        response = await self.http_client.post(
            "/api/v1/gateways/slack/files",
            json={
                "channels": params["channels"],
                "file_url": file_url,
                "filename": params.get("filename"),
                "title": params.get("title"),
                "initial_comment": params.get("initial_comment"),
                "thread_ts": params.get("thread_ts"),
                "workspace_id": self.slack_workspace_id,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to share file"}

    async def _open_modal(self, params: dict) -> dict:
        """Open modal dialog."""
        response = await self.http_client.post(
            "/api/v1/gateways/slack/modals",
            json={
                "trigger_id": params["trigger_id"],
                "view": params["view"],
                "workspace_id": self.slack_workspace_id,
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to open modal"}

    async def _handle_interaction(self, params: dict) -> dict:
        """Handle interaction callback."""
        response = await self.http_client.post(
            "/api/v1/gateways/slack/interactions",
            json={
                "payload": params["payload"],
                "workspace_id": self.slack_workspace_id,
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"processed": False, "payload": params["payload"]}

    async def _handle_slash_command(self, params: dict) -> dict:
        """Handle slash command."""
        response = await self.http_client.post(
            "/api/v1/gateways/slack/commands",
            json={
                "command": params["command"],
                "text": params.get("text"),
                "user_id": params["user_id"],
                "channel_id": params.get("channel_id"),
                "trigger_id": params.get("trigger_id"),
                "workspace_id": self.slack_workspace_id,
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to process command"}

    async def _get_channels(self, params: dict) -> dict:
        """Get channels."""
        response = await self.http_client.get(
            "/api/v1/gateways/slack/channels",
            params={
                "types": ",".join(params.get("types", ["public_channel"])),
                "limit": params.get("limit", 100),
                "workspace_id": self.slack_workspace_id,
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"channels": []}

    async def _get_users(self, params: dict) -> dict:
        """Get users."""
        response = await self.http_client.get(
            "/api/v1/gateways/slack/users",
            params={
                "limit": params.get("limit", 100),
                "workspace_id": self.slack_workspace_id,
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"users": []}

    async def _add_reaction(self, params: dict) -> dict:
        """Add reaction."""
        response = await self.http_client.post(
            "/api/v1/gateways/slack/reactions",
            json={
                "channel": params["channel"],
                "timestamp": params["timestamp"],
                "emoji": params["emoji"],
                "workspace_id": self.slack_workspace_id,
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to add reaction"}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
