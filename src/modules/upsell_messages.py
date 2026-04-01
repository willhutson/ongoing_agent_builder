"""
Upsell Messages — Contextual, helpful messages when a user requests
a capability from a module they don't have installed.

Tone: helpful and product-aware, not generic. Under 100 words.
"""


# Module-specific upsell messages
_UPSELL_TEMPLATES: dict[str, str] = {
    "CRM": (
        "It looks like you're trying to access CRM features. "
        "CRM isn't installed on your workspace yet — head to the "
        "SpokeStack Marketplace to add it in seconds. "
        "You'll get contact management, deal tracking, and client history "
        "right inside your workspace."
    ),
    "SOCIAL_PUBLISHING": (
        "Social publishing features aren't set up yet. "
        "Install the Social Publishing module from the SpokeStack Marketplace "
        "to schedule posts, manage content calendars, and track engagement "
        "across all your platforms."
    ),
    "CONTENT_STUDIO": (
        "Content studio features aren't available yet. "
        "Add the Content Studio module from the SpokeStack Marketplace "
        "to create, collaborate on, and manage content assets "
        "across your team."
    ),
    "ANALYTICS": (
        "Analytics features aren't available yet. "
        "Add the Analytics module from the SpokeStack Marketplace "
        "to get performance dashboards, campaign tracking, and "
        "automated reporting for your team."
    ),
    "SURVEYS": (
        "Survey features aren't set up yet. "
        "Install the Surveys module from the SpokeStack Marketplace "
        "to create surveys, collect responses, and analyze feedback."
    ),
    "LISTENING": (
        "Social listening features aren't available yet. "
        "Add the Listening module from the SpokeStack Marketplace "
        "to monitor brand mentions, track sentiment, and stay ahead of trends."
    ),
    "MEDIA_BUYING": (
        "Media buying features aren't set up yet. "
        "Install the Media Buying module from the SpokeStack Marketplace "
        "to plan, purchase, and optimize ad placements across channels."
    ),
    "LMS": (
        "Learning management features aren't available yet. "
        "Add the LMS module from the SpokeStack Marketplace "
        "to create courses, track progress, and manage team training."
    ),
    "NPS": (
        "NPS features aren't set up yet. "
        "Install the NPS module from the SpokeStack Marketplace "
        "to measure customer loyalty, track scores, and act on feedback."
    ),
    "TIME_LEAVE": (
        "Time and leave features aren't available yet. "
        "Add the Time & Leave module from the SpokeStack Marketplace "
        "to track attendance, manage leave requests, and view team schedules."
    ),
    "BOARDS": (
        "Board features aren't set up yet. "
        "Install the Boards module from the SpokeStack Marketplace "
        "to organize work visually with kanban boards and custom workflows."
    ),
    "FINANCE": (
        "Finance features aren't available yet. "
        "Add the Finance module from the SpokeStack Marketplace "
        "to manage budgets, track expenses, and generate financial reports."
    ),
    "WORKFLOWS": (
        "Workflow automation features aren't set up yet. "
        "Install the Workflows module from the SpokeStack Marketplace "
        "to automate repetitive processes and connect actions across modules."
    ),
    # Enterprise modules
    "SPOKECHAT": (
        "Internal chat features aren't available yet. "
        "Add SpokeChat from the Enterprise plan to enable team channels, "
        "direct messaging, and threaded conversations within your workspace."
    ),
    "DELEGATION": (
        "Delegation features aren't set up yet. "
        "Add the Delegation module from the Enterprise plan to manage "
        "out-of-office handoffs, proxy approvals, and authority assignment."
    ),
    "ACCESS_CONTROL": (
        "Access control features aren't available yet. "
        "Add Access Control from the Enterprise plan to manage role-based "
        "permissions, access policies, and data visibility rules."
    ),
    "API_MANAGEMENT": (
        "API management features aren't set up yet. "
        "Add API Management from the Enterprise plan to create API keys, "
        "manage webhooks, and control external API access."
    ),
    "BUILDER": (
        "Builder features aren't available yet. "
        "Add the Builder module from the Enterprise plan to create custom "
        "templates, configure builder permissions, and extend your workspace."
    ),
}

# Tier-aware upgrade hints (appended when the module requires a higher tier)
_TIER_HINTS: dict[str, str] = {
    "STARTER": "This module is available on the Starter plan and above.",
    "PRO": "This module is available on the Pro plan and above.",
    "BUSINESS": "This module is available on the Business plan.",
    "ENTERPRISE": "This module is available on the Enterprise plan.",
}

# Module → minimum tier required
_MODULE_TIER_REQUIREMENTS: dict[str, str] = {
    "CRM": "PRO",
    "SOCIAL_PUBLISHING": "PRO",
    "ANALYTICS": "PRO",
    "CONTENT_STUDIO": "PRO",
    "SURVEYS": "STARTER",
    "LISTENING": "PRO",
    "MEDIA_BUYING": "BUSINESS",
    "LMS": "BUSINESS",
    "NPS": "STARTER",
    "TIME_LEAVE": "STARTER",
    "BOARDS": "STARTER",
    "FINANCE": "BUSINESS",
    "WORKFLOWS": "PRO",
    # Enterprise modules
    "SPOKECHAT": "ENTERPRISE",
    "DELEGATION": "ENTERPRISE",
    "ACCESS_CONTROL": "ENTERPRISE",
    "API_MANAGEMENT": "ENTERPRISE",
    "BUILDER": "ENTERPRISE",
}

_TIER_LEVELS = {"FREE": 0, "STARTER": 1, "PRO": 2, "BUSINESS": 3, "ENTERPRISE": 4}


def get_upsell_message(module_type: str, org_tier: str = "FREE") -> str:
    """
    Get a contextual upsell message for a module that isn't installed.

    Args:
        module_type: The ModuleType string (e.g., "CRM")
        org_tier: The org's current billing tier

    Returns:
        A helpful, under-100-word message
    """
    # Get module-specific message or generate a generic one
    message = _UPSELL_TEMPLATES.get(
        module_type,
        f"The {module_type.replace('_', ' ').title()} module isn't installed on your workspace yet. "
        f"Head to the SpokeStack Marketplace to add it."
    )

    # Append tier hint if org is below the required tier
    required_tier = _MODULE_TIER_REQUIREMENTS.get(module_type)
    if required_tier:
        org_level = _TIER_LEVELS.get(org_tier, 0)
        req_level = _TIER_LEVELS.get(required_tier, 0)
        if org_level < req_level:
            hint = _TIER_HINTS.get(required_tier, "")
            if hint:
                message = f"{message} {hint}"

    return message
