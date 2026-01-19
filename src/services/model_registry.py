"""
Agent Model Registry - Maps agents to recommended Claude model tiers.

This registry defines which Claude model tier each agent should use based on
the complexity of reasoning required:

- OPUS: Complex reasoning, multi-step analysis, strategic decisions
- SONNET: Balanced - most agents, good reasoning with reasonable cost/speed
- HAIKU: Fast, simple operations, high-volume tasks, gateways

The registry supports:
1. Per-agent model recommendations
2. Runtime model tier override (force all to use same tier)
3. Per-instance model customization
"""

from typing import Optional
from src.config import ClaudeModelTier, CLAUDE_MODELS, get_settings


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
