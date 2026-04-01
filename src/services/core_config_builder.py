"""
Tier-Scoped Config Builder for spokestack-core agents.

buildAgentConfig(org, agentType) assembles the complete agent configuration:
  - Loads agent definition
  - Assembles tools based on BillingTier (FREE/STARTER/PRO/BUSINESS)
  - Adds marketplace module tools (from OrgModule records)
  - Adds context graph tools (always available)
  - Builds system prompt with org-specific context
  - Selects LLM model per agent type
"""

import logging
from typing import Any, Optional

from src.tools.core_tool_definitions import (
    CONTEXT_TOOLS, TASKS_TOOLS, PROJECTS_TOOLS, BRIEFS_TOOLS, ORDERS_TOOLS,
    TIER_TOOL_MAP, AGENT_CORE_TOOL_MAP, CORE_TOOL_NAMES,
)
from src.tools.spokestack_onboarding_modules import ONBOARDING_MODULE_TOOLS

logger = logging.getLogger(__name__)


# Agent type → LLM model mapping
# Onboarding/Briefs need stronger reasoning → Claude Sonnet
# Tasks/Projects/Orders are more CRUD-like → DeepSeek (cheaper)
AGENT_MODEL_MAP: dict[str, str] = {
    "core_onboarding": "claude-sonnet-4-20250514",
    "core_tasks":      "deepseek/deepseek-chat",
    "core_projects":   "deepseek/deepseek-chat",
    "core_briefs":     "claude-sonnet-4-20250514",
    "core_orders":     "deepseek/deepseek-chat",
}

# Agent type → required billing tier
AGENT_TIER_REQUIREMENTS: dict[str, str] = {
    "core_onboarding": "FREE",       # Always available
    "core_tasks":      "FREE",       # Always available
    "core_projects":   "STARTER",    # STARTER+
    "core_briefs":     "PRO",        # PRO+
    "core_orders":     "BUSINESS",   # BUSINESS only
}

# Tier hierarchy for comparisons
TIER_LEVELS: dict[str, int] = {
    "FREE": 0,
    "STARTER": 1,
    "PRO": 2,
    "BUSINESS": 3,
}

# Core agent types (for registry/routing)
CORE_AGENT_TYPES = list(AGENT_TIER_REQUIREMENTS.keys())


def tier_has_access(org_tier: str, required_tier: str) -> bool:
    """Check if an org's billing tier grants access to a required tier."""
    return TIER_LEVELS.get(org_tier, 0) >= TIER_LEVELS.get(required_tier, 0)


def get_gated_agents(org_tier: str) -> list[str]:
    """Get agent types that are gated (above the org's current tier)."""
    return [
        agent_type
        for agent_type, required in AGENT_TIER_REQUIREMENTS.items()
        if not tier_has_access(org_tier, required)
    ]


def get_available_agents(org_tier: str) -> list[str]:
    """Get agent types available at the org's billing tier."""
    return [
        agent_type
        for agent_type, required in AGENT_TIER_REQUIREMENTS.items()
        if tier_has_access(org_tier, required)
    ]


def build_tools_for_tier(org_tier: str, agent_type: str) -> list[dict]:
    """
    Assemble the tool list for an agent based on the org's billing tier.

    Returns the intersection of:
      - Tools available at the org's tier
      - Tools the specific agent type uses
    """
    # Get all tool groups available at this tier
    tier_groups = TIER_TOOL_MAP.get(org_tier, TIER_TOOL_MAP["FREE"])

    # Flatten into a single list
    all_tier_tools = []
    for group in tier_groups:
        all_tier_tools.extend(group)

    # Get the tool names this agent type is allowed to use
    agent_tool_names = AGENT_CORE_TOOL_MAP.get(agent_type)
    if agent_tool_names is None:
        # Unknown agent type — give context tools only
        return list(CONTEXT_TOOLS)

    # Filter: only include tools that are both in the tier AND in the agent's set
    filtered = [
        tool for tool in all_tier_tools
        if tool["function"]["name"] in agent_tool_names
    ]

    # Onboarding agent gets module recommendation tools
    if agent_type == "core_onboarding":
        filtered.extend(ONBOARDING_MODULE_TOOLS)

    return filtered


def build_system_prompt_context(
    org_name: str,
    org_tier: str,
    team_members: list[dict] = None,
    installed_modules: list[str] = None,
    gated_agents: list[str] = None,
) -> str:
    """
    Build org-specific context to append to the agent's system prompt.
    """
    lines = [
        f"\n## Organization Context",
        f"- Organization: {org_name}",
        f"- Tier: {org_tier}",
    ]

    if team_members:
        member_lines = [f"  - {m.get('name', 'Unknown')} ({m.get('role', 'member')})" for m in team_members[:20]]
        lines.append(f"- Team members:\n" + "\n".join(member_lines))

    if installed_modules:
        lines.append(f"- Installed modules: {', '.join(installed_modules)}")

    if gated_agents:
        agent_labels = {
            "core_projects": "Projects (STARTER tier)",
            "core_briefs": "Briefs (PRO tier)",
            "core_orders": "Orders (BUSINESS tier)",
        }
        gated_labels = [agent_labels.get(a, a) for a in gated_agents]
        lines.append(
            f"- Upgrade-available agents: {', '.join(gated_labels)}\n"
            f"  (Don't push upgrades. Only mention if the user's request naturally relates to one of these.)"
        )

    return "\n".join(lines)


async def build_agent_config(
    org_id: str,
    org_name: str,
    org_tier: str,
    agent_type: str,
    user_id: str = "system",
    team_members: list[dict] = None,
    installed_modules: list[str] = None,
    module_tools: list[dict] = None,
) -> dict:
    """
    Build the complete agent configuration for a spokestack-core request.

    Returns:
        {
            "agent_type": str,
            "model": str,
            "tools": list[dict],
            "system_prompt_context": str,
            "core_toolkit_config": {"org_id": str, "user_id": str},
            "available": bool,
            "upgrade_message": str | None,
        }
    """
    # Check tier access
    required_tier = AGENT_TIER_REQUIREMENTS.get(agent_type, "FREE")
    if not tier_has_access(org_tier, required_tier):
        tier_names = {"STARTER": "Starter", "PRO": "Pro", "BUSINESS": "Business"}
        return {
            "agent_type": agent_type,
            "model": None,
            "tools": [],
            "system_prompt_context": "",
            "core_toolkit_config": None,
            "available": False,
            "upgrade_message": (
                f"The {agent_type.replace('core_', '').title()} agent requires the "
                f"{tier_names.get(required_tier, required_tier)} plan. "
                f"Upgrade to unlock this capability."
            ),
        }

    # Assemble tools
    tools = build_tools_for_tier(org_tier, agent_type)

    # Add marketplace module tools if any
    if module_tools:
        tools.extend(module_tools)

    # Select model
    model = AGENT_MODEL_MAP.get(agent_type, "deepseek/deepseek-chat")

    # Build prompt context
    gated = get_gated_agents(org_tier)
    prompt_context = build_system_prompt_context(
        org_name=org_name,
        org_tier=org_tier,
        team_members=team_members,
        installed_modules=installed_modules,
        gated_agents=gated if gated else None,
    )

    return {
        "agent_type": agent_type,
        "model": model,
        "tools": tools,
        "system_prompt_context": prompt_context,
        "core_toolkit_config": {"org_id": org_id, "user_id": user_id},
        "available": True,
        "upgrade_message": None,
    }
