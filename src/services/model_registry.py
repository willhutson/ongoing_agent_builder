"""
Agent Model Registry - Maps agents to recommended Claude model tiers.

This registry defines which Claude model tier each agent should use based on
the complexity of reasoning required:

Internal Tiers (Technical):
- OPUS: Complex reasoning, multi-step analysis, strategic decisions
- SONNET: Balanced - most agents, good reasoning with reasonable cost/speed
- HAIKU: Fast, simple operations, high-volume tasks, gateways

External Tiers (User-Facing, aligned with erp_staging_lmtd):
- Premium → OPUS
- Standard → SONNET
- Economy → HAIKU

The registry supports:
1. Per-agent model recommendations
2. Runtime model tier override (force all to use same tier)
3. Per-instance model customization
4. External tier mapping for UI compatibility
"""

from typing import Optional
from enum import Enum
from src.config import ClaudeModelTier, CLAUDE_MODELS, get_settings


# =============================================================================
# External Tier Naming (aligned with erp_staging_lmtd)
# =============================================================================

class ExternalModelTier(str, Enum):
    """User-facing tier names for UI compatibility."""
    PREMIUM = "premium"    # Maps to OPUS
    STANDARD = "standard"  # Maps to SONNET
    ECONOMY = "economy"    # Maps to HAIKU


# Bidirectional tier mappings
INTERNAL_TO_EXTERNAL: dict[ClaudeModelTier, ExternalModelTier] = {
    ClaudeModelTier.OPUS: ExternalModelTier.PREMIUM,
    ClaudeModelTier.SONNET: ExternalModelTier.STANDARD,
    ClaudeModelTier.HAIKU: ExternalModelTier.ECONOMY,
}

EXTERNAL_TO_INTERNAL: dict[ExternalModelTier, ClaudeModelTier] = {
    ExternalModelTier.PREMIUM: ClaudeModelTier.OPUS,
    ExternalModelTier.STANDARD: ClaudeModelTier.SONNET,
    ExternalModelTier.ECONOMY: ClaudeModelTier.HAIKU,
}


# Agent to recommended model tier mapping
AGENT_MODEL_RECOMMENDATIONS: dict[str, ClaudeModelTier] = {
    # =========================================================================
    # OPUS TIER - Complex reasoning, analysis, strategic decisions
    # =========================================================================
    "rfp_agent": ClaudeModelTier.OPUS,           # RFP analysis, proposal strategy
    "commercial_agent": ClaudeModelTier.OPUS,    # Pricing intelligence, win/loss analysis
    "legal_agent": ClaudeModelTier.OPUS,         # Contract analysis, risk assessment
    "forecast_agent": ClaudeModelTier.OPUS,      # Revenue forecasting, scenario modeling
    "competitor_agent": ClaudeModelTier.OPUS,    # Competitive analysis, market intelligence
    "instance_analytics_agent": ClaudeModelTier.OPUS,  # Platform analytics, anomaly detection
    "instance_success_agent": ClaudeModelTier.OPUS,    # Churn prediction, expansion analysis

    # =========================================================================
    # SONNET TIER - Balanced reasoning (default for most agents)
    # =========================================================================
    "brief_agent": ClaudeModelTier.SONNET,
    "content_agent": ClaudeModelTier.SONNET,
    "brand_voice_agent": ClaudeModelTier.SONNET,
    "brand_visual_agent": ClaudeModelTier.SONNET,
    "brand_guidelines_agent": ClaudeModelTier.SONNET,
    "presentation_agent": ClaudeModelTier.SONNET,
    "copy_agent": ClaudeModelTier.SONNET,
    "image_agent": ClaudeModelTier.SONNET,
    "video_script_agent": ClaudeModelTier.SONNET,
    "video_storyboard_agent": ClaudeModelTier.SONNET,
    "video_production_agent": ClaudeModelTier.SONNET,
    "campaign_agent": ClaudeModelTier.SONNET,
    "media_buying_agent": ClaudeModelTier.SONNET,
    "resource_agent": ClaudeModelTier.SONNET,
    "workflow_agent": ClaudeModelTier.SONNET,
    "crm_agent": ClaudeModelTier.SONNET,
    "scope_agent": ClaudeModelTier.SONNET,
    "onboarding_agent": ClaudeModelTier.SONNET,
    "instance_onboarding_agent": ClaudeModelTier.SONNET,
    "social_listening_agent": ClaudeModelTier.SONNET,
    "community_agent": ClaudeModelTier.SONNET,
    "social_analytics_agent": ClaudeModelTier.SONNET,
    "brand_performance_agent": ClaudeModelTier.SONNET,
    "campaign_analytics_agent": ClaudeModelTier.SONNET,
    "invoice_agent": ClaudeModelTier.SONNET,
    "budget_agent": ClaudeModelTier.SONNET,
    "qa_agent": ClaudeModelTier.SONNET,
    "knowledge_agent": ClaudeModelTier.SONNET,
    "training_agent": ClaudeModelTier.SONNET,
    "influencer_agent": ClaudeModelTier.SONNET,
    "pr_agent": ClaudeModelTier.SONNET,
    "events_agent": ClaudeModelTier.SONNET,
    "localization_agent": ClaudeModelTier.SONNET,
    "accessibility_agent": ClaudeModelTier.SONNET,

    # =========================================================================
    # HAIKU TIER - Fast, simple operations, high-volume
    # =========================================================================
    "report_agent": ClaudeModelTier.HAIKU,       # Report distribution, simple routing
    "approve_agent": ClaudeModelTier.HAIKU,      # Approval routing, status tracking
    "brief_update_agent": ClaudeModelTier.HAIKU, # Update distribution
    "ops_reporting_agent": ClaudeModelTier.HAIKU,# KPI aggregation, simple alerts

    # Gateway agents - high volume, simple message routing
    "gateway_whatsapp": ClaudeModelTier.HAIKU,
    "gateway_email": ClaudeModelTier.HAIKU,
    "gateway_slack": ClaudeModelTier.HAIKU,
    "gateway_sms": ClaudeModelTier.HAIKU,

    # =========================================================================
    # META AGENTS - Helper agents that assist with other agents
    # =========================================================================
    "prompt_helper_agent": ClaudeModelTier.SONNET,  # Helps users craft better prompts
}


def get_model_for_agent(
    agent_name: str,
    instance_override: Optional[ClaudeModelTier] = None,
) -> str:
    """
    Get the Claude model ID for a specific agent.

    Priority:
    1. Global force_model_tier from settings (if set)
    2. Instance-level override (if provided)
    3. Agent's recommended tier from registry
    4. Default to SONNET if agent not in registry

    Args:
        agent_name: The agent's name (e.g., "rfp_agent")
        instance_override: Optional tier override for this instance

    Returns:
        Claude model ID string (e.g., "claude-sonnet-4-20250514")
    """
    settings = get_settings()

    # Check for global override
    if settings.force_model_tier:
        try:
            forced_tier = ClaudeModelTier(settings.force_model_tier)
            return CLAUDE_MODELS[forced_tier]
        except ValueError:
            pass  # Invalid tier, continue with normal resolution

    # Check for instance override
    if instance_override:
        return CLAUDE_MODELS[instance_override]

    # Get agent's recommended tier
    tier = AGENT_MODEL_RECOMMENDATIONS.get(agent_name, ClaudeModelTier.SONNET)
    return CLAUDE_MODELS[tier]


def get_agent_tier(agent_name: str) -> ClaudeModelTier:
    """Get the recommended tier for an agent."""
    return AGENT_MODEL_RECOMMENDATIONS.get(agent_name, ClaudeModelTier.SONNET)


def list_agents_by_tier() -> dict[ClaudeModelTier, list[str]]:
    """List all agents grouped by their recommended tier."""
    result = {tier: [] for tier in ClaudeModelTier}
    for agent, tier in AGENT_MODEL_RECOMMENDATIONS.items():
        result[tier].append(agent)
    return result


def get_model_info() -> dict:
    """Get information about all model tiers and their agents."""
    agents_by_tier = list_agents_by_tier()
    return {
        "tiers": {
            tier.value: {
                "model_id": CLAUDE_MODELS[tier],
                "description": _get_tier_description(tier),
                "agent_count": len(agents_by_tier[tier]),
                "agents": agents_by_tier[tier],
            }
            for tier in ClaudeModelTier
        },
        "total_agents": len(AGENT_MODEL_RECOMMENDATIONS),
    }


def _get_tier_description(tier: ClaudeModelTier) -> str:
    """Get human-readable description for a tier."""
    descriptions = {
        ClaudeModelTier.OPUS: "Complex reasoning, analysis, strategic decisions",
        ClaudeModelTier.SONNET: "Balanced - good reasoning with reasonable cost/speed",
        ClaudeModelTier.HAIKU: "Fast, simple operations, high-volume tasks",
    }
    return descriptions.get(tier, "")


# =============================================================================
# External Tier API (for erp_staging_lmtd compatibility)
# =============================================================================

def get_external_tier(agent_name: str) -> ExternalModelTier:
    """Get the external (user-facing) tier for an agent."""
    internal_tier = get_agent_tier(agent_name)
    return INTERNAL_TO_EXTERNAL[internal_tier]


def get_model_for_external_tier(external_tier: ExternalModelTier) -> str:
    """Get the Claude model ID for an external tier."""
    internal_tier = EXTERNAL_TO_INTERNAL[external_tier]
    return CLAUDE_MODELS[internal_tier]


def convert_external_to_internal(external_tier: ExternalModelTier) -> ClaudeModelTier:
    """Convert external tier to internal tier."""
    return EXTERNAL_TO_INTERNAL[external_tier]


def convert_internal_to_external(internal_tier: ClaudeModelTier) -> ExternalModelTier:
    """Convert internal tier to external tier name."""
    return INTERNAL_TO_EXTERNAL[internal_tier]


def get_external_model_info() -> dict:
    """Get model info using external tier naming (for UI/API compatibility)."""
    agents_by_tier = list_agents_by_tier()

    return {
        "tiers": {
            external_tier.value: {
                "internal_tier": internal_tier.value,
                "model_id": CLAUDE_MODELS[internal_tier],
                "description": _get_external_tier_description(external_tier),
                "agent_count": len(agents_by_tier[internal_tier]),
                "agents": agents_by_tier[internal_tier],
                "cost_indicator": _get_cost_indicator(external_tier),
            }
            for external_tier, internal_tier in EXTERNAL_TO_INTERNAL.items()
        },
        "total_agents": len(AGENT_MODEL_RECOMMENDATIONS),
    }


def _get_external_tier_description(tier: ExternalModelTier) -> str:
    """Get user-facing description for external tiers."""
    descriptions = {
        ExternalModelTier.PREMIUM: "Highest capability for complex analysis and strategic decisions",
        ExternalModelTier.STANDARD: "Balanced capability and cost - recommended for most tasks",
        ExternalModelTier.ECONOMY: "Fast and cost-effective for simple, high-volume tasks",
    }
    return descriptions.get(tier, "")


def _get_cost_indicator(tier: ExternalModelTier) -> dict:
    """Get cost indicator for UI display (ModelSelector component compatibility)."""
    indicators = {
        ExternalModelTier.PREMIUM: {"level": 3, "label": "$$$", "relative": "highest"},
        ExternalModelTier.STANDARD: {"level": 2, "label": "$$", "relative": "moderate"},
        ExternalModelTier.ECONOMY: {"level": 1, "label": "$", "relative": "lowest"},
    }
    return indicators.get(tier, indicators[ExternalModelTier.STANDARD])
