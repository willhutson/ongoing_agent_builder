"""
Agent UI Component Definitions

Defines contextual agent UI components that can be rendered in the ERP.
These are Python dataclasses that serialize to JSON for frontend consumption.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ActionPriority(Enum):
    """Priority level for suggested actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ModuleType(Enum):
    """ERP module types for contextual suggestions."""
    PROJECTS = "projects"
    CAMPAIGNS = "campaigns"
    CLIENTS = "clients"
    DELIVERABLES = "deliverables"
    REPORTS = "reports"
    COMPLIANCE = "compliance"
    CONTENT_STUDIO = "content_studio"
    SALES_PIPELINE = "sales_pipeline"
    RESOURCE_PLANNING = "resource_planning"


@dataclass
class AgentCapabilityCard:
    """
    A card displaying an agent's capability.
    Used in agent discovery panels and module sidebars.
    """
    agent_id: str
    agent_name: str
    tool_name: str
    tool_description: str
    category: str
    icon: str
    color: str
    estimated_duration: str
    requires_browser: bool = False
    example_prompt: str = ""

    def to_dict(self) -> dict:
        return {
            "agentId": self.agent_id,
            "agentName": self.agent_name,
            "toolName": self.tool_name,
            "toolDescription": self.tool_description,
            "category": self.category,
            "icon": self.icon,
            "color": self.color,
            "estimatedDuration": self.estimated_duration,
            "requiresBrowser": self.requires_browser,
            "examplePrompt": self.example_prompt,
        }


@dataclass
class AgentContextualSuggestion:
    """
    A contextual suggestion for using an agent based on current context.
    Displayed proactively in relevant ERP modules.
    """
    id: str
    agent_id: str
    agent_name: str
    tool_name: str
    suggestion_text: str
    why_suggested: str
    priority: ActionPriority
    module_context: ModuleType

    # Pre-filled parameters based on context
    prefilled_params: dict = field(default_factory=dict)

    # Visual elements
    icon: str = "sparkles"
    color: str = "blue"

    # Tracking
    dismissable: bool = True
    show_learn_more: bool = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agentId": self.agent_id,
            "agentName": self.agent_name,
            "toolName": self.tool_name,
            "suggestionText": self.suggestion_text,
            "whySuggested": self.why_suggested,
            "priority": self.priority.value,
            "moduleContext": self.module_context.value,
            "prefilledParams": self.prefilled_params,
            "icon": self.icon,
            "color": self.color,
            "dismissable": self.dismissable,
            "showLearnMore": self.show_learn_more,
        }


@dataclass
class AgentQuickAction:
    """
    A quick action button for common agent operations.
    Displayed in module toolbars and context menus.
    """
    id: str
    label: str
    agent_id: str
    tool_name: str
    icon: str
    shortcut: Optional[str] = None  # Keyboard shortcut
    tooltip: str = ""
    requires_selection: bool = False  # Needs selected item(s)

    # Context requirements
    available_in_modules: list[ModuleType] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "agentId": self.agent_id,
            "toolName": self.tool_name,
            "icon": self.icon,
            "shortcut": self.shortcut,
            "tooltip": self.tooltip,
            "requiresSelection": self.requires_selection,
            "availableInModules": [m.value for m in self.available_in_modules],
        }


@dataclass
class WorkflowProgressCard:
    """
    Card displaying progress of a running workflow.
    Used in workflow management panels and notifications.
    """
    execution_id: str
    workflow_name: str
    status: str
    progress_percentage: float
    current_step: str
    current_agent: str
    steps_completed: int
    steps_total: int
    started_at: str
    estimated_completion: Optional[str] = None

    # For paused workflows
    awaiting_review: bool = False
    review_step_name: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "executionId": self.execution_id,
            "workflowName": self.workflow_name,
            "status": self.status,
            "progressPercentage": self.progress_percentage,
            "currentStep": self.current_step,
            "currentAgent": self.current_agent,
            "stepsCompleted": self.steps_completed,
            "stepsTotal": self.steps_total,
            "startedAt": self.started_at,
            "estimatedCompletion": self.estimated_completion,
            "awaitingReview": self.awaiting_review,
            "reviewStepName": self.review_step_name,
        }


# =============================================================================
# Module-Context Agent Mapping
# =============================================================================

# Maps ERP modules to relevant agents and their tools
MODULE_AGENT_MAPPING = {
    ModuleType.PROJECTS: [
        {"agent_id": "qa_agent", "tools": ["verify_landing_page", "run_performance_audit", "capture_device_suite"]},
        {"agent_id": "campaign_agent", "tools": ["verify_landing_page", "check_redirect_chain"]},
    ],
    ModuleType.CAMPAIGNS: [
        {"agent_id": "campaign_agent", "tools": ["verify_landing_page", "capture_ab_variants", "validate_utm_parameters", "check_redirect_chain"]},
        {"agent_id": "qa_agent", "tools": ["run_performance_audit", "check_broken_links", "verify_meta_tags"]},
        {"agent_id": "legal_agent", "tools": ["verify_gdpr_compliance", "check_ad_disclosure"]},
    ],
    ModuleType.CLIENTS: [
        {"agent_id": "competitor_agent", "tools": ["analyze_competitor", "capture_competitor_ads"]},
        {"agent_id": "report_agent", "tools": ["capture_ga4_dashboard", "generate_dashboard_pdf"]},
    ],
    ModuleType.DELIVERABLES: [
        {"agent_id": "qa_agent", "tools": ["verify_landing_page", "run_accessibility_audit", "capture_device_suite"]},
        {"agent_id": "campaign_agent", "tools": ["preview_email", "capture_email_clients", "verify_social_asset"]},
    ],
    ModuleType.REPORTS: [
        {"agent_id": "report_agent", "tools": ["capture_ga4_dashboard", "capture_facebook_ads_manager", "generate_dashboard_pdf", "capture_multi_dashboard"]},
    ],
    ModuleType.COMPLIANCE: [
        {"agent_id": "legal_agent", "tools": ["verify_gdpr_compliance", "analyze_cookie_banner", "check_ad_disclosure", "detect_policy_changes"]},
        {"agent_id": "qa_agent", "tools": ["run_accessibility_audit", "check_link_attributes"]},
    ],
    ModuleType.CONTENT_STUDIO: [
        {"agent_id": "qa_agent", "tools": ["verify_meta_tags", "check_structured_data", "verify_alt_text"]},
        {"agent_id": "campaign_agent", "tools": ["preview_email", "verify_social_asset", "capture_social_preview"]},
    ],
    ModuleType.SALES_PIPELINE: [
        {"agent_id": "competitor_agent", "tools": ["analyze_competitor", "capture_competitor_ads"]},
    ],
    ModuleType.RESOURCE_PLANNING: [
        # Typically no direct agent integrations here
    ],
}

# Quick actions available per module
MODULE_QUICK_ACTIONS = {
    ModuleType.PROJECTS: [
        AgentQuickAction(
            id="qa_verify_page",
            label="Verify Page",
            agent_id="qa_agent",
            tool_name="verify_landing_page",
            icon="check-circle",
            shortcut="Ctrl+Shift+V",
            tooltip="Verify the project's landing page is live and correct",
            available_in_modules=[ModuleType.PROJECTS],
        ),
        AgentQuickAction(
            id="qa_perf_audit",
            label="Performance Audit",
            agent_id="qa_agent",
            tool_name="run_performance_audit",
            icon="gauge",
            tooltip="Run a performance audit on the page",
            available_in_modules=[ModuleType.PROJECTS],
        ),
    ],
    ModuleType.CAMPAIGNS: [
        AgentQuickAction(
            id="campaign_verify",
            label="Verify Campaign",
            agent_id="campaign_agent",
            tool_name="verify_landing_page",
            icon="check",
            shortcut="Ctrl+Shift+C",
            tooltip="Verify campaign landing page",
            available_in_modules=[ModuleType.CAMPAIGNS],
        ),
        AgentQuickAction(
            id="campaign_ab_capture",
            label="Capture A/B Test",
            agent_id="campaign_agent",
            tool_name="capture_ab_variants",
            icon="split",
            tooltip="Capture A/B test variants",
            available_in_modules=[ModuleType.CAMPAIGNS],
        ),
        AgentQuickAction(
            id="campaign_utm_check",
            label="Check UTMs",
            agent_id="campaign_agent",
            tool_name="validate_utm_parameters",
            icon="tag",
            tooltip="Validate UTM parameters",
            available_in_modules=[ModuleType.CAMPAIGNS],
        ),
    ],
    ModuleType.CLIENTS: [
        AgentQuickAction(
            id="competitor_analyze",
            label="Analyze Competitor",
            agent_id="competitor_agent",
            tool_name="analyze_competitor",
            icon="search",
            tooltip="Run competitor analysis",
            available_in_modules=[ModuleType.CLIENTS],
        ),
    ],
    ModuleType.COMPLIANCE: [
        AgentQuickAction(
            id="legal_gdpr",
            label="GDPR Check",
            agent_id="legal_agent",
            tool_name="verify_gdpr_compliance",
            icon="shield-check",
            tooltip="Verify GDPR compliance",
            available_in_modules=[ModuleType.COMPLIANCE],
        ),
        AgentQuickAction(
            id="legal_cookies",
            label="Cookie Analysis",
            agent_id="legal_agent",
            tool_name="analyze_cookie_banner",
            icon="cookie",
            tooltip="Analyze cookie consent",
            available_in_modules=[ModuleType.COMPLIANCE],
        ),
    ],
}


def get_contextual_agents_for_module(module: ModuleType) -> list[dict]:
    """
    Get agents and tools relevant for a specific ERP module.

    Returns a list of agent configurations with their relevant tools.
    """
    return MODULE_AGENT_MAPPING.get(module, [])


def get_quick_actions_for_context(
    module: ModuleType,
    has_selection: bool = False,
) -> list[AgentQuickAction]:
    """
    Get quick actions available for the current context.

    Args:
        module: The current ERP module
        has_selection: Whether items are selected in the view

    Returns:
        List of available quick actions
    """
    actions = MODULE_QUICK_ACTIONS.get(module, [])

    # Filter based on selection requirement
    if not has_selection:
        actions = [a for a in actions if not a.requires_selection]

    return actions


def generate_contextual_suggestion(
    module: ModuleType,
    context_data: dict,
) -> Optional[AgentContextualSuggestion]:
    """
    Generate a contextual suggestion based on current module and data.

    Args:
        module: The current ERP module
        context_data: Data from the current context (e.g., project, campaign)

    Returns:
        A contextual suggestion or None
    """
    # Example: Suggest verification for campaigns about to launch
    if module == ModuleType.CAMPAIGNS:
        if context_data.get("status") == "ready_to_launch":
            landing_url = context_data.get("landing_page_url", "")
            return AgentContextualSuggestion(
                id=f"suggest_verify_{context_data.get('id', 'unknown')}",
                agent_id="campaign_agent",
                agent_name="Campaign Agent",
                tool_name="verify_landing_page",
                suggestion_text="Verify landing page before launch",
                why_suggested="This campaign is ready to launch. Run a quick verification to ensure the landing page is live and correct.",
                priority=ActionPriority.HIGH,
                module_context=module,
                prefilled_params={"url": landing_url},
                icon="rocket",
                color="green",
            )

    # Example: Suggest competitor analysis for new clients
    if module == ModuleType.CLIENTS:
        if context_data.get("is_new") or context_data.get("days_since_onboard", 100) < 30:
            competitor_url = context_data.get("primary_competitor_url", "")
            if competitor_url:
                return AgentContextualSuggestion(
                    id=f"suggest_competitor_{context_data.get('id', 'unknown')}",
                    agent_id="competitor_agent",
                    agent_name="Competitor Agent",
                    tool_name="analyze_competitor",
                    suggestion_text="Analyze primary competitor",
                    why_suggested="Run a competitive analysis to establish baseline intelligence for this new client.",
                    priority=ActionPriority.MEDIUM,
                    module_context=module,
                    prefilled_params={"url": competitor_url},
                    icon="search",
                    color="orange",
                )

    # Example: Suggest accessibility audit for deliverables
    if module == ModuleType.DELIVERABLES:
        if context_data.get("type") == "landing_page" and not context_data.get("accessibility_checked"):
            url = context_data.get("url", "")
            return AgentContextualSuggestion(
                id=f"suggest_a11y_{context_data.get('id', 'unknown')}",
                agent_id="qa_agent",
                agent_name="QA Agent",
                tool_name="run_accessibility_audit",
                suggestion_text="Check accessibility compliance",
                why_suggested="This landing page hasn't been checked for accessibility. Ensure WCAG compliance before delivery.",
                priority=ActionPriority.MEDIUM,
                module_context=module,
                prefilled_params={"url": url, "wcag_level": "AA"},
                icon="universal-access",
                color="purple",
            )

    return None


# =============================================================================
# API Response Helpers
# =============================================================================

def get_agent_panel_data(module: ModuleType) -> dict:
    """
    Get complete data for rendering an agent panel in a module.

    Returns data structure suitable for React component consumption.
    """
    from ..orchestration.registry import get_registry

    registry = get_registry()
    agent_configs = get_contextual_agents_for_module(module)
    quick_actions = get_quick_actions_for_context(module)

    capability_cards = []
    for config in agent_configs:
        agent_info = registry.get_agent(config["agent_id"])
        if agent_info:
            for tool_name in config["tools"]:
                cap = agent_info.get_capability(tool_name)
                if cap:
                    card = AgentCapabilityCard(
                        agent_id=agent_info.agent_id,
                        agent_name=agent_info.name,
                        tool_name=cap.tool_name,
                        tool_description=cap.description,
                        category=cap.category.value,
                        icon=agent_info.icon,
                        color=agent_info.color,
                        estimated_duration=f"{cap.avg_duration_seconds}s",
                        requires_browser=cap.requires_browser,
                        example_prompt=cap.example_prompts[0] if cap.example_prompts else "",
                    )
                    capability_cards.append(card.to_dict())

    return {
        "module": module.value,
        "capabilities": capability_cards,
        "quickActions": [a.to_dict() for a in quick_actions],
    }
