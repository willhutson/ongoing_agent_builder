"""
Operations Module Agents — Reports, QA, Legal, Approvals, Accessibility.

Compliance, quality, and admin workflows. Audit trail critical.
"""

from typing import Any
from shared.base_agent import BaseAgent
from shared.openrouter import OpenRouterClient
from shared.config import BaseModuleSettings, get_model_id


class ReportAgent(BaseAgent):
    """Report generation and analytics summaries."""

    @property
    def name(self) -> str:
        return "report"

    @property
    def system_prompt(self) -> str:
        return """You are a reporting specialist.

Generate clear, actionable reports:
- Performance dashboards and summaries
- Executive briefs and board reports
- Client-facing reports
- Data visualization recommendations
- Trend analysis and insights"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_report",
                "description": "Generate a report.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_type": {"type": "string", "enum": ["executive", "client", "performance", "financial", "custom"]},
                        "data_sources": {"type": "array", "items": {"type": "string"}},
                        "period": {"type": "string"},
                        "sections": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["report_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class OpsReportingAgent(BaseAgent):
    """Operational reporting and dashboard generation."""

    @property
    def name(self) -> str:
        return "ops_reporting"

    @property
    def system_prompt(self) -> str:
        return """You are an operational reporting specialist.

Track operational metrics:
- Team utilization and capacity
- Project status and health
- SLA compliance
- Resource burn rate
- Process efficiency metrics"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "ops_report",
                "description": "Generate operational report.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_type": {"type": "string", "enum": ["utilization", "project_health", "sla", "capacity"]},
                        "period": {"type": "string"},
                        "teams": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["report_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class QAAgent(BaseAgent):
    """Quality assurance and testing."""

    @property
    def name(self) -> str:
        return "qa"

    @property
    def system_prompt(self) -> str:
        return """You are a QA specialist.

Ensure quality across deliverables:
- Content review and proofreading
- Brand compliance checking
- Technical QA for digital assets
- Accessibility compliance (WCAG)
- Cross-browser/device testing guidance
- Checklist generation and tracking"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "review_content",
                "description": "Review content for quality.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "review_type": {"type": "string", "enum": ["copy", "brand", "technical", "accessibility", "full"]},
                        "brand_guidelines": {"type": "string"},
                    },
                    "required": ["content", "review_type"],
                },
            },
            {
                "name": "create_checklist",
                "description": "Create a QA checklist for a deliverable.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deliverable_type": {"type": "string"},
                        "channels": {"type": "array", "items": {"type": "string"}},
                        "standards": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["deliverable_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class LegalAgent(BaseAgent):
    """Contract analysis and legal compliance. Premium tier."""

    @property
    def name(self) -> str:
        return "legal"

    @property
    def system_prompt(self) -> str:
        return """You are a legal compliance specialist for marketing and advertising.

Review and advise on:
- Contract terms and red flags
- Advertising regulations and compliance
- IP and trademark considerations
- Privacy and data protection (GDPR, CCPA)
- Influencer disclosure requirements
- Music/image licensing

Always flag items needing actual legal counsel."""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "review_contract",
                "description": "Review a contract or legal document.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document": {"type": "string"},
                        "review_focus": {"type": "string", "enum": ["full", "risk", "compliance", "terms", "ip"]},
                        "jurisdiction": {"type": "string"},
                    },
                    "required": ["document"],
                },
            },
            {
                "name": "compliance_check",
                "description": "Check content for regulatory compliance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "content_type": {"type": "string", "enum": ["ad", "social", "email", "website", "influencer"]},
                        "industry": {"type": "string"},
                        "regions": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["content", "content_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class ApproveAgent(BaseAgent):
    """Approval routing and decision automation. Economy tier."""

    @property
    def name(self) -> str:
        return "approve"

    @property
    def system_prompt(self) -> str:
        return """You are an approval workflow coordinator.

Route and track approvals:
- Determine required approvers based on content type and value
- Track approval status and send reminders
- Escalate overdue approvals
- Log decisions and comments
- Manage revision cycles"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "route_approval",
                "description": "Route content for approval.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string"},
                        "content_id": {"type": "string"},
                        "approvers": {"type": "array", "items": {"type": "string"}},
                        "deadline": {"type": "string"},
                        "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"]},
                    },
                    "required": ["content_type", "content_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class AccessibilityAgent(BaseAgent):
    """WCAG compliance and accessibility auditing."""

    @property
    def name(self) -> str:
        return "accessibility"

    @property
    def system_prompt(self) -> str:
        return """You are an accessibility specialist (WCAG 2.1 AA/AAA).

Ensure digital content is accessible:
- Color contrast analysis
- Alt text and ARIA labels
- Keyboard navigation
- Screen reader compatibility
- Cognitive accessibility
- PDF and document accessibility"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "audit_accessibility",
                "description": "Audit content for accessibility.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "content_type": {"type": "string", "enum": ["html", "pdf", "email", "social", "video"]},
                        "standard": {"type": "string", "enum": ["WCAG_AA", "WCAG_AAA", "Section_508"]},
                    },
                    "required": ["content", "content_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class BriefUpdateAgent(BaseAgent):
    """Status updates and distribution. Economy tier."""

    @property
    def name(self) -> str:
        return "brief_update"

    @property
    def system_prompt(self) -> str:
        return """You are a status update coordinator.

Manage project status communications:
- Generate status summaries from project data
- Distribute updates to stakeholders
- Track acknowledgments
- Highlight blockers and risks"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_update",
                "description": "Generate a status update.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "update_type": {"type": "string", "enum": ["daily", "weekly", "milestone", "blocker"]},
                        "recipients": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["project_id", "update_type"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


def create_agents(llm: OpenRouterClient, settings: BaseModuleSettings) -> dict[str, BaseAgent]:
    standard = get_model_id(settings, "standard")
    premium = get_model_id(settings, "premium")
    economy = get_model_id(settings, "economy")
    return {
        "report": ReportAgent(llm, standard),
        "ops_reporting": OpsReportingAgent(llm, standard),
        "qa": QAAgent(llm, standard),
        "legal": LegalAgent(llm, premium),
        "approve": ApproveAgent(llm, economy),
        "accessibility": AccessibilityAgent(llm, standard),
        "brief_update": BriefUpdateAgent(llm, economy),
    }
