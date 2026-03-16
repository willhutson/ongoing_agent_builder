"""
Module Registry — Maps ERP subdomain modules to available agents.

Implements the subdomain architecture from SUBDOMAIN_MODULES.md:
Each module subdomain (e.g., studio.spokestack.app) has a default agent
and a set of available agents that Mission Control can route to.

This is the Layer 1 (Agent Runtime) side of the module-agent binding.
The ERP sends module context via X-Module-Subdomain header or context.moduleSubdomain.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModuleConfig:
    """Configuration for a single ERP module subdomain."""
    subdomain: str
    display_name: str
    default_agent: str
    available_agents: list[str] = field(default_factory=list)
    description: str = ""


# Module-to-agent mapping from SUBDOMAIN_MODULES.md
MODULE_REGISTRY: dict[str, ModuleConfig] = {
    "studio": ModuleConfig(
        subdomain="studio",
        display_name="SpokeStudio",
        default_agent="content",
        available_agents=[
            "content", "copy", "image", "presentation",
            "video_script", "video_storyboard", "video_production",
            "brand_voice", "brand_visual", "brand_guidelines",
            "accessibility",
        ],
        description="Creative production suite",
    ),
    "crm": ModuleConfig(
        subdomain="crm",
        display_name="CRM",
        default_agent="crm",
        available_agents=[
            "crm", "scope", "onboarding",
            "instance_success", "community",
        ],
        description="Client relationship management",
    ),
    "briefs": ModuleConfig(
        subdomain="briefs",
        display_name="Briefs",
        default_agent="brief",
        available_agents=[
            "brief", "brief_update", "rfp", "scope",
            "content", "qa",
        ],
        description="Brief creation and management",
    ),
    "projects": ModuleConfig(
        subdomain="projects",
        display_name="Projects",
        default_agent="workflow",
        available_agents=[
            "workflow", "resource", "scope",
            "ops_reporting", "qa",
        ],
        description="Project management and workflows",
    ),
    "analytics": ModuleConfig(
        subdomain="analytics",
        display_name="Analytics",
        default_agent="campaign_analytics",
        available_agents=[
            "campaign_analytics", "brand_performance",
            "social_analytics", "competitor",
            "instance_analytics", "ops_reporting",
        ],
        description="Analytics and reporting",
    ),
    "lms": ModuleConfig(
        subdomain="lms",
        display_name="Learning",
        default_agent="training",
        available_agents=[
            "training", "knowledge", "content",
        ],
        description="Learning management system",
    ),
    "publisher": ModuleConfig(
        subdomain="publisher",
        display_name="Publisher",
        default_agent="campaign",
        available_agents=[
            "campaign", "copy", "social_listening",
            "community", "social_analytics",
            "gateway_whatsapp", "gateway_email",
            "gateway_slack", "gateway_sms",
        ],
        description="Content publishing and distribution",
    ),
    "time": ModuleConfig(
        subdomain="time",
        display_name="Time Tracking",
        default_agent="resource",
        available_agents=[
            "resource", "ops_reporting", "workflow",
        ],
        description="Time tracking and utilization",
    ),
    "finance": ModuleConfig(
        subdomain="finance",
        display_name="Finance",
        default_agent="invoice",
        available_agents=[
            "invoice", "forecast", "budget",
            "commercial", "ops_reporting",
        ],
        description="Financial management",
    ),
    "resources": ModuleConfig(
        subdomain="resources",
        display_name="Resources",
        default_agent="resource",
        available_agents=[
            "resource", "workflow", "ops_reporting",
        ],
        description="Resource allocation and management",
    ),
    "surveys": ModuleConfig(
        subdomain="surveys",
        display_name="Surveys",
        default_agent="community",
        available_agents=[
            "community", "social_analytics", "content",
        ],
        description="Surveys and feedback collection",
    ),
    "marketing": ModuleConfig(
        subdomain="marketing",
        display_name="Marketing",
        default_agent="campaign",
        available_agents=[
            "campaign", "media_buying", "influencer",
            "social_listening", "social_analytics",
            "brand_performance", "campaign_analytics",
            "competitor", "pr", "events", "localization",
        ],
        description="Marketing campaigns and media",
    ),
    # Full platform (app.spokestack.app) — all agents available
    "app": ModuleConfig(
        subdomain="app",
        display_name="SpokeStack Platform",
        default_agent="content",
        available_agents=list({
            "rfp", "brief", "content", "commercial",
            "presentation", "copy", "image",
            "video_script", "video_storyboard", "video_production",
            "report", "approve", "brief_update",
            "gateway_whatsapp", "gateway_email", "gateway_slack", "gateway_sms",
            "brand_voice", "brand_visual", "brand_guidelines",
            "resource", "workflow", "ops_reporting",
            "crm", "scope", "onboarding",
            "instance_onboarding", "instance_analytics", "instance_success",
            "media_buying", "campaign",
            "social_listening", "community", "social_analytics",
            "brand_performance", "campaign_analytics", "competitor",
            "invoice", "forecast", "budget",
            "qa", "legal",
            "knowledge", "training",
            "influencer", "pr", "events", "localization", "accessibility",
        }),
        description="Full SpokeStack platform — all agents",
    ),
}


def get_module_config(subdomain: str) -> Optional[ModuleConfig]:
    """Get module config for a subdomain. Returns None if unknown."""
    return MODULE_REGISTRY.get(subdomain)


def get_default_agent(subdomain: str) -> Optional[str]:
    """Get the default agent for a subdomain."""
    config = MODULE_REGISTRY.get(subdomain)
    return config.default_agent if config else None


def get_available_agents(subdomain: str) -> list[str]:
    """Get available agents for a subdomain. Falls back to all agents for unknown subdomains."""
    config = MODULE_REGISTRY.get(subdomain)
    if config:
        return config.available_agents
    # Unknown subdomain — fall back to app (all agents)
    return MODULE_REGISTRY["app"].available_agents


def is_agent_allowed_for_module(agent_type: str, subdomain: str) -> bool:
    """Check if an agent is allowed for a given module subdomain."""
    available = get_available_agents(subdomain)
    return agent_type in available


def resolve_agent_for_module(
    requested_agent: Optional[str],
    subdomain: Optional[str],
) -> str:
    """
    Resolve which agent to use given a request and module context.

    - If requested_agent is set and allowed for the module, use it.
    - If requested_agent is set but not allowed, raise ValueError.
    - If no requested_agent, use the module's default agent.
    - If no module context, require requested_agent.
    """
    if not subdomain or subdomain not in MODULE_REGISTRY:
        # No module context — must have explicit agent
        if not requested_agent:
            raise ValueError("agent_type is required when no module context is provided")
        return requested_agent

    if not requested_agent:
        return get_default_agent(subdomain)

    if not is_agent_allowed_for_module(requested_agent, subdomain):
        config = MODULE_REGISTRY[subdomain]
        raise ValueError(
            f"Agent '{requested_agent}' is not available in the '{subdomain}' module. "
            f"Available agents: {config.available_agents}"
        )

    return requested_agent
