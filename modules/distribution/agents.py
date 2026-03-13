"""
Distribution Module Agents — Gateways (WhatsApp, Email, Slack, SMS), PR, Influencer, Localization.

Outbound communication. High volume, async.
"""

from typing import Any
from shared.base_agent import BaseAgent
from shared.openrouter import OpenRouterClient
from shared.config import BaseModuleSettings, get_model_id


class WhatsAppGateway(BaseAgent):
    """WhatsApp message routing and delivery."""

    @property
    def name(self) -> str:
        return "gateway_whatsapp"

    @property
    def system_prompt(self) -> str:
        return """You are a WhatsApp Business API coordinator.

Handle WhatsApp messaging:
- Format messages for WhatsApp constraints
- Use templates for business conversations
- Handle media attachments (5MB images, 16MB video)
- Track delivery and read receipts
- Interactive messages (buttons, lists) where appropriate"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "send_message",
                "description": "Send a WhatsApp message.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "Phone number with country code"},
                        "message_type": {"type": "string", "enum": ["text", "template", "image", "video", "document", "interactive"]},
                        "content": {"type": "object"},
                        "template_name": {"type": "string"},
                    },
                    "required": ["recipient", "message_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "queued", "spec": tool_input}


class EmailGateway(BaseAgent):
    """Email message routing and delivery."""

    @property
    def name(self) -> str:
        return "gateway_email"

    @property
    def system_prompt(self) -> str:
        return """You are an email delivery specialist.

Manage email communications:
- Format HTML and plain text emails
- Template management
- Personalization and merge fields
- Deliverability optimization
- Tracking (opens, clicks)"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "send_email",
                "description": "Send an email.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "array", "items": {"type": "string"}},
                        "subject": {"type": "string"},
                        "body_html": {"type": "string"},
                        "body_text": {"type": "string"},
                        "template_id": {"type": "string"},
                        "merge_data": {"type": "object"},
                    },
                    "required": ["to", "subject"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "queued", "spec": tool_input}


class SlackGateway(BaseAgent):
    """Slack message routing."""

    @property
    def name(self) -> str:
        return "gateway_slack"

    @property
    def system_prompt(self) -> str:
        return """You are a Slack integration specialist.

Manage Slack communications:
- Channel and DM messaging
- Rich message formatting (blocks, attachments)
- Thread management
- Notification routing
- Slash command responses"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "send_slack",
                "description": "Send a Slack message.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string"},
                        "message": {"type": "string"},
                        "blocks": {"type": "array", "items": {"type": "object"}},
                        "thread_ts": {"type": "string"},
                    },
                    "required": ["channel", "message"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "queued", "spec": tool_input}


class SMSGateway(BaseAgent):
    """SMS message routing."""

    @property
    def name(self) -> str:
        return "gateway_sms"

    @property
    def system_prompt(self) -> str:
        return """You are an SMS delivery specialist.

Manage SMS communications:
- Message formatting within 160 char limit
- MMS for media
- Delivery tracking
- Opt-in/opt-out compliance
- Rate limiting and throttling"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "send_sms",
                "description": "Send an SMS.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string"},
                        "message": {"type": "string"},
                        "media_url": {"type": "string"},
                    },
                    "required": ["recipient", "message"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "queued", "spec": tool_input}


class PRAgent(BaseAgent):
    """Public relations and media relations."""

    @property
    def name(self) -> str:
        return "pr"

    @property
    def system_prompt(self) -> str:
        return """You are a public relations specialist.

Manage PR activities:
- Press release writing
- Media list curation
- Pitch development
- Crisis communication
- Media monitoring and coverage tracking"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_pr_content",
                "description": "Create PR content.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string", "enum": ["press_release", "pitch", "statement", "q_and_a", "talking_points"]},
                        "topic": {"type": "string"},
                        "key_messages": {"type": "array", "items": {"type": "string"}},
                        "tone": {"type": "string", "enum": ["formal", "conversational", "crisis", "celebratory"]},
                    },
                    "required": ["content_type", "topic"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class InfluencerAgent(BaseAgent):
    """Influencer partnership and outreach."""

    @property
    def name(self) -> str:
        return "influencer"

    @property
    def system_prompt(self) -> str:
        return """You are an influencer marketing specialist.

Manage influencer programs:
- Influencer discovery and vetting
- Outreach message crafting
- Campaign brief creation for influencers
- Performance tracking and ROI
- Contract and compliance guidance"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "manage_influencer",
                "description": "Influencer operations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["discover", "outreach", "brief", "track", "report"]},
                        "criteria": {"type": "object"},
                        "campaign": {"type": "string"},
                    },
                    "required": ["action"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class LocalizationAgent(BaseAgent):
    """Translation and cultural adaptation."""

    @property
    def name(self) -> str:
        return "localization"

    @property
    def system_prompt(self) -> str:
        return """You are a localization specialist.

Adapt content for global markets:
- Translation with cultural context
- Tone and idiom adaptation
- Regional compliance considerations
- Multi-language content management
- Cultural sensitivity review"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "localize_content",
                "description": "Localize content for a market.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "source_language": {"type": "string", "default": "en"},
                        "target_language": {"type": "string"},
                        "target_market": {"type": "string"},
                        "content_type": {"type": "string"},
                    },
                    "required": ["content", "target_language"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


def create_agents(llm: OpenRouterClient, settings: BaseModuleSettings) -> dict[str, BaseAgent]:
    standard = get_model_id(settings, "standard")
    economy = get_model_id(settings, "economy")
    return {
        "gateway_whatsapp": WhatsAppGateway(llm, economy),
        "gateway_email": EmailGateway(llm, economy),
        "gateway_slack": SlackGateway(llm, economy),
        "gateway_sms": SMSGateway(llm, economy),
        "pr": PRAgent(llm, standard),
        "influencer": InfluencerAgent(llm, standard),
        "localization": LocalizationAgent(llm, standard),
    }
