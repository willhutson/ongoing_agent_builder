"""
Strategy Module Agents — Campaign, MediaBuying, Forecast, Budget, Resource, Workflow.

Planning and resource allocation. Cross-module context needed.
"""

from typing import Any
from shared.base_agent import BaseAgent
from shared.openrouter import OpenRouterClient
from shared.config import BaseModuleSettings, get_model_id


class CampaignAgent(BaseAgent):
    """Campaign orchestration and execution planning."""

    @property
    def name(self) -> str:
        return "campaign"

    @property
    def system_prompt(self) -> str:
        return """You are a campaign strategist and orchestrator.

Plan and manage campaigns end-to-end:
- Campaign strategy and objectives
- Channel mix and tactics
- Timeline and milestone planning
- Budget allocation across channels
- Creative brief generation
- Performance targets and KPIs"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "plan_campaign",
                "description": "Create a campaign plan.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "objective": {"type": "string"},
                        "budget": {"type": "number"},
                        "duration_weeks": {"type": "integer"},
                        "channels": {"type": "array", "items": {"type": "string"}},
                        "target_audience": {"type": "string"},
                        "kpis": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["objective"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class MediaBuyingAgent(BaseAgent):
    """Media planning and buying guidance."""

    @property
    def name(self) -> str:
        return "media_buying"

    @property
    def system_prompt(self) -> str:
        return """You are a media planning and buying specialist.

Optimize media spend:
- Channel selection and media mix
- Audience targeting strategies
- Budget allocation and pacing
- Rate negotiation guidance
- Performance optimization
- Programmatic buying strategy"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_media_plan",
                "description": "Create a media buying plan.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "budget": {"type": "number"},
                        "objective": {"type": "string", "enum": ["awareness", "consideration", "conversion", "retention"]},
                        "target_audience": {"type": "string"},
                        "channels": {"type": "array", "items": {"type": "string"}},
                        "duration_weeks": {"type": "integer"},
                    },
                    "required": ["budget", "objective"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class ForecastAgent(BaseAgent):
    """Revenue forecasting and scenario modeling. Premium tier."""

    @property
    def name(self) -> str:
        return "forecast"

    @property
    def system_prompt(self) -> str:
        return """You are a financial forecasting specialist.

Build revenue forecasts and scenarios:
- Pipeline analysis and conversion modeling
- Revenue projection with confidence intervals
- Scenario planning (optimistic, realistic, pessimistic)
- Seasonal adjustment and trend analysis
- Risk identification and mitigation"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_forecast",
                "description": "Create a revenue forecast.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "period": {"type": "string", "enum": ["month", "quarter", "year"]},
                        "historical_data": {"type": "string", "description": "Historical revenue data or context"},
                        "pipeline": {"type": "string", "description": "Current pipeline status"},
                        "scenarios": {"type": "array", "items": {"type": "string"}, "default": ["optimistic", "realistic", "pessimistic"]},
                    },
                    "required": ["period"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class BudgetAgent(BaseAgent):
    """Budget management and financial planning. Premium tier."""

    @property
    def name(self) -> str:
        return "budget"

    @property
    def system_prompt(self) -> str:
        return """You are a budget management specialist.

Manage budgets with precision:
- Budget creation and allocation
- Spend tracking and variance analysis
- Reallocation recommendations
- Cost optimization opportunities
- Financial reporting and summaries"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_budget",
                "description": "Create or analyze a budget.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "total_budget": {"type": "number"},
                        "categories": {"type": "array", "items": {"type": "string"}},
                        "period": {"type": "string"},
                        "constraints": {"type": "object"},
                    },
                    "required": ["total_budget"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class ResourceAgent(BaseAgent):
    """Resource allocation and team planning."""

    @property
    def name(self) -> str:
        return "resource"

    @property
    def system_prompt(self) -> str:
        return """You are a resource planning specialist.

Optimize resource allocation:
- Team capacity planning
- Skill-based assignment
- Workload balancing
- Utilization tracking
- Hiring/outsourcing recommendations"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "plan_resources",
                "description": "Plan resource allocation for a project.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project": {"type": "string"},
                        "required_skills": {"type": "array", "items": {"type": "string"}},
                        "duration_weeks": {"type": "integer"},
                        "budget_hours": {"type": "number"},
                    },
                    "required": ["project"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class WorkflowAgent(BaseAgent):
    """Workflow design and process optimization."""

    @property
    def name(self) -> str:
        return "workflow"

    @property
    def system_prompt(self) -> str:
        return """You are a workflow and process optimization specialist.

Design efficient workflows:
- Process mapping and documentation
- Automation opportunity identification
- Approval chain design
- SLA definition and tracking
- Bottleneck analysis and resolution"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "design_workflow",
                "description": "Design a workflow process.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "process_name": {"type": "string"},
                        "steps": {"type": "array", "items": {"type": "string"}},
                        "approvers": {"type": "array", "items": {"type": "string"}},
                        "sla_hours": {"type": "number"},
                    },
                    "required": ["process_name"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


def create_agents(llm: OpenRouterClient, settings: BaseModuleSettings) -> dict[str, BaseAgent]:
    standard = get_model_id(settings, "standard")
    premium = get_model_id(settings, "premium")
    return {
        "campaign": CampaignAgent(llm, standard),
        "media_buying": MediaBuyingAgent(llm, standard),
        "forecast": ForecastAgent(llm, premium),
        "budget": BudgetAgent(llm, premium),
        "resource": ResourceAgent(llm, standard),
        "workflow": WorkflowAgent(llm, standard),
    }
