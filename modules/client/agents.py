"""
Client Module Agents — CRM, Scope, Invoice, Onboarding, Training, Community, Events.

Client-facing operations. CRM integration.
"""

from typing import Any
from shared.base_agent import BaseAgent
from shared.openrouter import OpenRouterClient
from shared.config import BaseModuleSettings, get_model_id


class CRMAgent(BaseAgent):
    """Customer relationship management."""

    @property
    def name(self) -> str:
        return "crm"

    @property
    def system_prompt(self) -> str:
        return """You are a CRM specialist.

Manage client relationships:
- Contact and account management
- Interaction logging and history
- Pipeline and opportunity tracking
- Client health scoring
- Relationship insights and recommendations"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "manage_client",
                "description": "Client CRM operations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["lookup", "update", "log_interaction", "health_score", "pipeline"]},
                        "client_name": {"type": "string"},
                        "data": {"type": "object"},
                    },
                    "required": ["action", "client_name"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class ScopeAgent(BaseAgent):
    """Project scope definition and management."""

    @property
    def name(self) -> str:
        return "scope"

    @property
    def system_prompt(self) -> str:
        return """You are a scope management specialist.

Define and manage project scope:
- Scope document creation
- Deliverable breakdown and estimation
- Change request evaluation
- Scope creep detection
- SOW generation"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "define_scope",
                "description": "Define project scope.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string"},
                        "objectives": {"type": "array", "items": {"type": "string"}},
                        "deliverables": {"type": "array", "items": {"type": "string"}},
                        "constraints": {"type": "object"},
                        "exclusions": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["project_name", "objectives"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class InvoiceAgent(BaseAgent):
    """Invoice processing and payment tracking."""

    @property
    def name(self) -> str:
        return "invoice"

    @property
    def system_prompt(self) -> str:
        return """You are an invoicing specialist.

Manage billing:
- Invoice generation from project milestones
- Payment tracking and reminders
- Expense categorization
- Revenue recognition guidance
- Aging report generation"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "manage_invoice",
                "description": "Invoice operations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["create", "track", "remind", "report"]},
                        "client_name": {"type": "string"},
                        "amount": {"type": "number"},
                        "items": {"type": "array", "items": {"type": "object"}},
                    },
                    "required": ["action"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class OnboardingAgent(BaseAgent):
    """Client onboarding workflows."""

    @property
    def name(self) -> str:
        return "onboarding"

    @property
    def system_prompt(self) -> str:
        return """You are a client onboarding specialist.

Guide new client setup:
- Welcome package generation
- Brand asset collection checklists
- Access and permission setup
- Kickoff meeting agendas
- Onboarding timeline and milestones"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_onboarding",
                "description": "Create client onboarding plan.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string"},
                        "service_type": {"type": "string"},
                        "team_size": {"type": "integer"},
                        "start_date": {"type": "string"},
                    },
                    "required": ["client_name"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class TrainingAgent(BaseAgent):
    """Training content creation and knowledge transfer."""

    @property
    def name(self) -> str:
        return "training"

    @property
    def system_prompt(self) -> str:
        return """You are a training and knowledge transfer specialist.

Create training materials:
- How-to guides and documentation
- Video training scripts
- Quiz and assessment creation
- Knowledge base articles
- Onboarding curricula"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_training",
                "description": "Create training material.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "format": {"type": "string", "enum": ["guide", "video_script", "quiz", "kb_article", "curriculum"]},
                        "audience": {"type": "string"},
                        "difficulty": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
                    },
                    "required": ["topic", "format"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class CommunityAgent(BaseAgent):
    """Community management and engagement."""

    @property
    def name(self) -> str:
        return "community"

    @property
    def system_prompt(self) -> str:
        return """You are a community management specialist.

Build and manage communities:
- Community strategy and guidelines
- Engagement content and prompts
- Moderation guidance
- Member segmentation
- Community health metrics"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "manage_community",
                "description": "Community management operations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["strategy", "content", "moderate", "analyze"]},
                        "platform": {"type": "string"},
                        "context": {"type": "string"},
                    },
                    "required": ["action"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class EventsAgent(BaseAgent):
    """Event planning and coordination."""

    @property
    def name(self) -> str:
        return "events"

    @property
    def system_prompt(self) -> str:
        return """You are an event planning specialist.

Plan and coordinate events:
- Event concept and theme development
- Timeline and logistics planning
- Vendor coordination checklists
- Budget tracking
- Post-event analysis"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "plan_event",
                "description": "Plan an event.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string", "enum": ["conference", "webinar", "launch", "networking", "workshop"]},
                        "attendees": {"type": "integer"},
                        "budget": {"type": "number"},
                        "date": {"type": "string"},
                        "virtual": {"type": "boolean"},
                    },
                    "required": ["event_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


def create_agents(llm: OpenRouterClient, settings: BaseModuleSettings) -> dict[str, BaseAgent]:
    model = get_model_id(settings, "standard")
    return {
        "crm": CRMAgent(llm, model),
        "scope": ScopeAgent(llm, model),
        "invoice": InvoiceAgent(llm, model),
        "onboarding": OnboardingAgent(llm, model),
        "training": TrainingAgent(llm, model),
        "community": CommunityAgent(llm, model),
        "events": EventsAgent(llm, model),
    }
