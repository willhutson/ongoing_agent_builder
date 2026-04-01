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
    "ANALYTICS": (
        "Analytics features aren't available yet. "
        "Add the Analytics module from the SpokeStack Marketplace "
        "to get performance dashboards, campaign tracking, and "
        "automated reporting for your team."
    ),
    "EMAIL_MARKETING": (
        "Email marketing features aren't set up yet. "
        "Install the Email Marketing module from the SpokeStack Marketplace "
        "to create campaigns, manage lists, and track engagement."
    ),
    "INVOICING": (
        "Invoicing features aren't available yet. "
        "Add the Invoicing module from the SpokeStack Marketplace "
        "to generate invoices, track payments, and manage your billing."
    ),
    "HR": (
        "HR features aren't available yet. "
        "Install the HR module from the SpokeStack Marketplace "
        "to manage team members, track time off, and handle onboarding."
    ),
}

# Tier-aware upgrade hints (appended when the module requires a higher tier)
_TIER_HINTS: dict[str, str] = {
    "STARTER": "This module is available on the Starter plan and above.",
    "PRO": "This module is available on the Pro plan and above.",
    "BUSINESS": "This module is available on the Business plan.",
}


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

    return message
