"""
Agent Model Registry - Maps agents to recommended model tiers.

5-Tier System:
- OPUS/PREMIUM:     Complex reasoning, multi-step analysis, strategic decisions
- SONNET/STANDARD:  Balanced - most agents, good reasoning with reasonable cost/speed
- HAIKU/ECONOMY:    Fast, simple operations, high-volume tasks, gateways
- CREATIVE:         Visual design, copywriting, deck building, brand voice (Kimi K2.5)
- VISION:           Image generation, visual understanding (GPT-5 Image Mini)

The CREATIVE and VISION tiers route to best-in-class non-Anthropic models via
OpenRouter, giving agents specialized capabilities that Claude doesn't offer
(visual design sense, native image generation).

The registry supports:
1. Per-agent model recommendations
2. Runtime model tier override (force all to use same tier)
3. Per-instance model customization
4. External tier mapping for ERP UI compatibility
5. Per-tier model override via env vars (MODEL_TIER_CREATIVE, etc.)
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
    CREATIVE = "creative"  # Maps to CREATIVE (non-Anthropic)
    VISION = "vision"      # Maps to VISION (non-Anthropic)


# Bidirectional tier mappings
INTERNAL_TO_EXTERNAL: dict[ClaudeModelTier, ExternalModelTier] = {
    ClaudeModelTier.OPUS: ExternalModelTier.PREMIUM,
    ClaudeModelTier.SONNET: ExternalModelTier.STANDARD,
    ClaudeModelTier.HAIKU: ExternalModelTier.ECONOMY,
    ClaudeModelTier.CREATIVE: ExternalModelTier.CREATIVE,
    ClaudeModelTier.VISION: ExternalModelTier.VISION,
}

EXTERNAL_TO_INTERNAL: dict[ExternalModelTier, ClaudeModelTier] = {
    ExternalModelTier.PREMIUM: ClaudeModelTier.OPUS,
    ExternalModelTier.STANDARD: ClaudeModelTier.SONNET,
    ExternalModelTier.ECONOMY: ClaudeModelTier.HAIKU,
    ExternalModelTier.CREATIVE: ClaudeModelTier.CREATIVE,
    ExternalModelTier.VISION: ClaudeModelTier.VISION,
}


# Agent to recommended model tier mapping
AGENT_MODEL_RECOMMENDATIONS: dict[str, ClaudeModelTier] = {
    # =========================================================================
    # OPUS/PREMIUM TIER - Complex reasoning, analysis, strategic decisions
    # Per handoff: Finance (forecast, budget), Quality (legal), Knowledge
    # =========================================================================
    "legal_agent": ClaudeModelTier.OPUS,          # Contract analysis, risk assessment (premium)
    "forecast_agent": ClaudeModelTier.OPUS,       # Revenue forecasting, scenario modeling (premium)
    "budget_agent": ClaudeModelTier.OPUS,         # Budget management - accuracy critical (premium)
    "knowledge_agent": ClaudeModelTier.OPUS,      # Knowledge base - deep reasoning (premium)

    # =========================================================================
    # CREATIVE TIER - Visual design, copywriting, brand voice
    # Uses Kimi K2.5 (moonshotai/kimi-k2.5) — best visual coding + design sense
    # =========================================================================
    "presentation_agent": ClaudeModelTier.CREATIVE,     # Deck generation — HTML/CSS visual output
    "copy_agent": ClaudeModelTier.CREATIVE,             # Copywriting — tone, brand voice
    "brand_voice_agent": ClaudeModelTier.CREATIVE,      # Voice/tone definition
    "brand_visual_agent": ClaudeModelTier.CREATIVE,     # Visual identity guidelines
    "brand_guidelines_agent": ClaudeModelTier.CREATIVE, # Brand standards documentation
    "video_script_agent": ClaudeModelTier.CREATIVE,     # Script writing — narrative craft
    "video_storyboard_agent": ClaudeModelTier.CREATIVE, # Storyboard generation — visual layout

    # =========================================================================
    # VISION TIER - Image generation, visual understanding
    # Uses GPT-5 Image Mini (openai/gpt-5-image-mini)
    # =========================================================================
    "image_agent": ClaudeModelTier.VISION,        # Image prompt crafting + generation

    # =========================================================================
    # SONNET/STANDARD TIER - Balanced reasoning (default for most agents)
    # =========================================================================
    # Foundation Layer
    "rfp_agent": ClaudeModelTier.SONNET,          # RFP analysis
    "brief_agent": ClaudeModelTier.SONNET,        # Brief creation
    "content_agent": ClaudeModelTier.SONNET,      # Content generation
    "commercial_agent": ClaudeModelTier.SONNET,   # Commercial analysis

    # Video Layer (production guidance stays standard — not creative writing)
    "video_production_agent": ClaudeModelTier.SONNET,  # Production guidance

    # Operations Layer
    "resource_agent": ClaudeModelTier.SONNET,    # Resource allocation
    "workflow_agent": ClaudeModelTier.SONNET,    # Workflow management
    "ops_reporting_agent": ClaudeModelTier.SONNET,  # Ops reporting

    # Client Layer
    "crm_agent": ClaudeModelTier.SONNET,              # CRM
    "scope_agent": ClaudeModelTier.SONNET,            # Scope management
    "onboarding_agent": ClaudeModelTier.SONNET,       # Client onboarding
    "instance_onboarding_agent": ClaudeModelTier.SONNET,  # SuperAdmin wizard
    "instance_analytics_agent": ClaudeModelTier.SONNET,   # Platform analytics
    "instance_success_agent": ClaudeModelTier.SONNET,     # Customer success

    # Media Layer
    "media_buying_agent": ClaudeModelTier.SONNET,  # Media planning
    "campaign_agent": ClaudeModelTier.SONNET,      # Campaign management

    # Social Layer
    "social_listening_agent": ClaudeModelTier.SONNET,  # Listening
    "community_agent": ClaudeModelTier.SONNET,         # Community management
    "social_analytics_agent": ClaudeModelTier.SONNET,  # Social metrics

    # Performance Layer
    "brand_performance_agent": ClaudeModelTier.SONNET,    # Brand metrics
    "campaign_analytics_agent": ClaudeModelTier.SONNET,   # Campaign analytics
    "competitor_agent": ClaudeModelTier.SONNET,           # Competitor analysis

    # Finance Layer (invoice is standard, forecast/budget are premium above)
    "invoice_agent": ClaudeModelTier.SONNET,  # Invoice processing

    # Quality Layer (legal is premium above)
    "qa_agent": ClaudeModelTier.SONNET,  # QA

    # Knowledge Layer (knowledge is premium above)
    "training_agent": ClaudeModelTier.SONNET,  # Training content

    # Specialized Layer
    "influencer_agent": ClaudeModelTier.SONNET,   # Influencer marketing
    "pr_agent": ClaudeModelTier.SONNET,           # PR
    "events_agent": ClaudeModelTier.SONNET,       # Events
    "localization_agent": ClaudeModelTier.SONNET, # Localization
    "accessibility_agent": ClaudeModelTier.SONNET,# Accessibility

    # =========================================================================
    # HAIKU/ECONOMY TIER - Fast, simple operations, high-volume
    # Per handoff: Gateway agents, approval routing, brief updates
    # =========================================================================
    # Distribution Layer
    "report_agent": ClaudeModelTier.SONNET,       # Report generation (standard)
    "approve_agent": ClaudeModelTier.HAIKU,       # Approval routing (economy)
    "brief_update_agent": ClaudeModelTier.HAIKU,  # Update distribution (economy)

    # Gateway Layer - high volume, simple message routing (all economy)
    "gateway_whatsapp": ClaudeModelTier.HAIKU,
    "gateway_email": ClaudeModelTier.HAIKU,
    "gateway_slack": ClaudeModelTier.HAIKU,
    "gateway_sms": ClaudeModelTier.HAIKU,

    # =========================================================================
    # META AGENTS - Helper agents that assist with other agents
    # =========================================================================
    "prompt_helper_agent": ClaudeModelTier.SONNET,  # Helps users craft better prompts
}


def _resolve_model_for_tier(tier: ClaudeModelTier) -> str:
    """
    Resolve the actual model ID for a tier, respecting env var overrides.

    Checks MODEL_TIER_<NAME> env vars first (e.g., MODEL_TIER_CREATIVE),
    then falls back to CLAUDE_MODELS defaults.
    """
    settings = get_settings()

    # Check for per-tier env var override
    tier_override_attr = f"model_tier_{tier.value}"
    override = getattr(settings, tier_override_attr, None)
    if override:
        return override

    return CLAUDE_MODELS[tier]


def get_model_for_agent(
    agent_name: str,
    instance_override: Optional[ClaudeModelTier] = None,
) -> str:
    """
    Get the model ID for a specific agent.

    Priority:
    1. Global force_model_tier from settings (if set)
    2. Instance-level override (if provided)
    3. Agent's recommended tier from registry
    4. Default to SONNET if agent not in registry

    Returns:
        Model ID string (e.g., "claude-sonnet-4-20250514" or "moonshotai/kimi-k2.5")
    """
    settings = get_settings()

    # Check for global override
    if settings.force_model_tier:
        try:
            forced_tier = ClaudeModelTier(settings.force_model_tier)
            return _resolve_model_for_tier(forced_tier)
        except ValueError:
            pass  # Invalid tier, continue with normal resolution

    # Check for instance override
    if instance_override:
        return _resolve_model_for_tier(instance_override)

    # Get agent's recommended tier
    tier = AGENT_MODEL_RECOMMENDATIONS.get(agent_name, ClaudeModelTier.SONNET)
    return _resolve_model_for_tier(tier)


# Runtime tier overrides (persisted in memory, set via API)
_agent_tier_overrides: dict[str, ClaudeModelTier] = {}


def get_agent_tier(agent_name: str) -> ClaudeModelTier:
    """Get the recommended tier for an agent (respects runtime overrides)."""
    if agent_name in _agent_tier_overrides:
        return _agent_tier_overrides[agent_name]
    return AGENT_MODEL_RECOMMENDATIONS.get(agent_name, ClaudeModelTier.SONNET)


def set_agent_tier(agent_name: str, tier: ClaudeModelTier) -> None:
    """Override the tier for a specific agent at runtime."""
    _agent_tier_overrides[agent_name] = tier


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
                "model_id": _resolve_model_for_tier(tier),
                "default_model_id": CLAUDE_MODELS[tier],
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
        ClaudeModelTier.CREATIVE: "Visual design, copywriting, deck building, brand voice",
        ClaudeModelTier.VISION: "Image generation, visual understanding",
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
    """Get the model ID for an external tier."""
    internal_tier = EXTERNAL_TO_INTERNAL[external_tier]
    return _resolve_model_for_tier(internal_tier)


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
                "model_id": _resolve_model_for_tier(internal_tier),
                "default_model_id": CLAUDE_MODELS[internal_tier],
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
        ExternalModelTier.CREATIVE: "Visual design, copywriting, and brand-focused generation",
        ExternalModelTier.VISION: "Image generation and visual understanding",
    }
    return descriptions.get(tier, "")


def _get_cost_indicator(tier: ExternalModelTier) -> dict:
    """Get cost indicator for UI display (ModelSelector component compatibility)."""
    indicators = {
        ExternalModelTier.PREMIUM: {"level": 3, "label": "$$$", "relative": "highest"},
        ExternalModelTier.STANDARD: {"level": 2, "label": "$$", "relative": "moderate"},
        ExternalModelTier.ECONOMY: {"level": 1, "label": "$", "relative": "lowest"},
        ExternalModelTier.CREATIVE: {"level": 2, "label": "$$", "relative": "moderate"},
        ExternalModelTier.VISION: {"level": 2, "label": "$$", "relative": "moderate"},
    }
    return indicators.get(tier, indicators[ExternalModelTier.STANDARD])
