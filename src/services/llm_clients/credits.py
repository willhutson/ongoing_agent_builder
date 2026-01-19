"""
SpokeStack Credit System

Abstracts raw API costs into a credit-based billing model.
Supports different user tiers (agencies vs brands) and modules.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal
from enum import Enum
from datetime import datetime
from .billing import (
    CostBreakdown,
    CostCategory,
    calculate_video_cost,
    calculate_image_cost,
    calculate_voice_cost,
    calculate_vision_cost,
    calculate_research_cost,
    calculate_presentation_cost,
)


class UserTier(str, Enum):
    """User tier determines credit pricing and limits."""
    STARTER = "starter"      # Small brands, solo users
    BRAND = "brand"          # Mid-size brands, internal teams
    AGENCY = "agency"        # Agencies, multiple clients
    ENTERPRISE = "enterprise"  # Enterprise, unlimited


class Module(str, Enum):
    """SpokeStack modules that consume credits."""
    VIDEO = "video"
    STUDIO = "studio"        # Images, presentations
    VOICE = "voice"
    RESEARCH = "research"
    ANALYTICS = "analytics"
    DISTRIBUTION = "distribution"


# =============================================================================
# CREDIT CONVERSION RATES
# =============================================================================

# 1 credit = $0.01 base cost (we charge more, pocket the difference)
USD_TO_CREDITS_BASE = 100  # $1 = 100 credits

# Tier multipliers (how many credits $1 of API cost equals)
# Lower = better deal for customer (enterprise gets bulk discount)
TIER_CREDIT_MULTIPLIERS = {
    UserTier.STARTER: 1.0,      # 1 credit = $0.01 cost
    UserTier.BRAND: 0.9,        # 1 credit = $0.011 cost (10% discount)
    UserTier.AGENCY: 0.75,      # 1 credit = $0.0133 cost (25% discount)
    UserTier.ENTERPRISE: 0.6,   # 1 credit = $0.0167 cost (40% discount)
}

# What we charge per credit (our revenue)
CREDIT_PRICE_USD = {
    UserTier.STARTER: 0.03,     # $0.03 per credit (3x markup)
    UserTier.BRAND: 0.025,      # $0.025 per credit (2.5x markup)
    UserTier.AGENCY: 0.02,      # $0.02 per credit (2x markup on discounted)
    UserTier.ENTERPRISE: 0.015, # $0.015 per credit (custom)
}


# =============================================================================
# MONTHLY PLANS
# =============================================================================

@dataclass
class MonthlyPlan:
    """Monthly subscription plan."""
    name: str
    tier: UserTier
    base_price_usd: float
    included_credits: int
    max_users: int
    modules: list[Module]
    overage_rate: float  # Per credit over limit


PLANS = {
    "starter": MonthlyPlan(
        name="Starter",
        tier=UserTier.STARTER,
        base_price_usd=49,
        included_credits=2000,    # ~$20 of API costs
        max_users=3,
        modules=[Module.STUDIO, Module.VOICE],
        overage_rate=0.035,
    ),
    "brand": MonthlyPlan(
        name="Brand",
        tier=UserTier.BRAND,
        base_price_usd=199,
        included_credits=10000,   # ~$100 of API costs
        max_users=10,
        modules=[Module.VIDEO, Module.STUDIO, Module.VOICE, Module.RESEARCH],
        overage_rate=0.028,
    ),
    "agency": MonthlyPlan(
        name="Agency",
        tier=UserTier.AGENCY,
        base_price_usd=499,
        included_credits=35000,   # ~$350 of API costs
        max_users=50,
        modules=[Module.VIDEO, Module.STUDIO, Module.VOICE, Module.RESEARCH, Module.ANALYTICS],
        overage_rate=0.022,
    ),
    "enterprise": MonthlyPlan(
        name="Enterprise",
        tier=UserTier.ENTERPRISE,
        base_price_usd=1499,
        included_credits=150000,  # ~$1500 of API costs
        max_users=999,
        modules=list(Module),  # All modules
        overage_rate=0.018,
    ),
}


# =============================================================================
# CREDIT CALCULATION
# =============================================================================

@dataclass
class CreditUsage:
    """Credit usage for an operation."""
    operation: str
    category: CostCategory
    module: Module
    credits_used: int
    api_cost_usd: float
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "category": self.category.value,
            "module": self.module.value,
            "credits_used": self.credits_used,
            "api_cost_usd": round(self.api_cost_usd, 4),
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


def cost_to_credits(
    cost_usd: float,
    tier: UserTier = UserTier.BRAND,
) -> int:
    """
    Convert API cost to credits.

    Args:
        cost_usd: Raw API cost in USD
        tier: User tier (affects conversion rate)

    Returns:
        Number of credits
    """
    multiplier = TIER_CREDIT_MULTIPLIERS[tier]
    credits = cost_usd * USD_TO_CREDITS_BASE * multiplier
    return max(1, round(credits))  # Minimum 1 credit


def credits_to_revenue(
    credits: int,
    tier: UserTier = UserTier.BRAND,
) -> float:
    """
    Calculate our revenue from credits used.

    Args:
        credits: Number of credits
        tier: User tier

    Returns:
        Revenue in USD
    """
    rate = CREDIT_PRICE_USD[tier]
    return credits * rate


def get_margin(
    api_cost: float,
    credits_used: int,
    tier: UserTier,
) -> dict:
    """
    Calculate our margin on an operation.

    Returns:
        Dict with revenue, cost, margin details
    """
    revenue = credits_to_revenue(credits_used, tier)
    margin = revenue - api_cost
    margin_pct = (margin / revenue * 100) if revenue > 0 else 0

    return {
        "api_cost": round(api_cost, 4),
        "credits_used": credits_used,
        "revenue": round(revenue, 4),
        "margin_usd": round(margin, 4),
        "margin_percent": round(margin_pct, 1),
    }


# =============================================================================
# OPERATION CREDIT COSTS
# =============================================================================

def calculate_video_credits(
    provider: str,
    model: str,
    duration_seconds: int,
    tier: UserTier = UserTier.BRAND,
) -> CreditUsage:
    """Calculate credits for video generation."""
    cost = calculate_video_cost(provider, model, duration_seconds)
    credits = cost_to_credits(cost.total_cost_usd, tier)

    return CreditUsage(
        operation=f"video_{model}",
        category=CostCategory.VIDEO,
        module=Module.VIDEO,
        credits_used=credits,
        api_cost_usd=cost.total_cost_usd,
        details={
            "provider": provider,
            "model": model,
            "duration": duration_seconds,
            **cost.details,
        },
    )


def calculate_image_credits(
    provider: str,
    model: str,
    num_images: int = 1,
    size: str = "1024x1024",
    quality: str = "standard",
    tier: UserTier = UserTier.BRAND,
) -> CreditUsage:
    """Calculate credits for image generation."""
    cost = calculate_image_cost(provider, model, size, quality, num_images)
    credits = cost_to_credits(cost.total_cost_usd, tier)

    return CreditUsage(
        operation=f"image_{model}",
        category=CostCategory.IMAGE,
        module=Module.STUDIO,
        credits_used=credits,
        api_cost_usd=cost.total_cost_usd,
        details={
            "provider": provider,
            "model": model,
            "num_images": num_images,
            **cost.details,
        },
    )


def calculate_voice_credits(
    provider: str,
    operation: str,
    quantity: float,
    model: str = "default",
    tier: UserTier = UserTier.BRAND,
) -> CreditUsage:
    """Calculate credits for voice operations."""
    cost = calculate_voice_cost(provider, operation, quantity, model)
    credits = cost_to_credits(cost.total_cost_usd, tier)

    return CreditUsage(
        operation=f"voice_{operation}",
        category=cost.category,
        module=Module.VOICE,
        credits_used=credits,
        api_cost_usd=cost.total_cost_usd,
        details={
            "provider": provider,
            "operation": operation,
            "quantity": quantity,
            **cost.details,
        },
    )


def calculate_presentation_credits(
    provider: str,
    num_slides: int,
    include_images: bool = True,
    tier: UserTier = UserTier.BRAND,
) -> CreditUsage:
    """Calculate credits for presentation generation."""
    cost = calculate_presentation_cost(provider, num_slides, include_images=include_images)
    credits = cost_to_credits(cost.total_cost_usd, tier)

    return CreditUsage(
        operation=f"presentation_{provider}",
        category=CostCategory.PRESENTATION,
        module=Module.STUDIO,
        credits_used=credits,
        api_cost_usd=cost.total_cost_usd,
        details={
            "provider": provider,
            "num_slides": num_slides,
            **cost.details,
        },
    )


def calculate_research_credits(
    model: str,
    input_tokens: int,
    output_tokens: int,
    tier: UserTier = UserTier.BRAND,
) -> CreditUsage:
    """Calculate credits for research queries."""
    cost = calculate_research_cost(model, input_tokens, output_tokens)
    credits = cost_to_credits(cost.total_cost_usd, tier)

    return CreditUsage(
        operation="research",
        category=CostCategory.RESEARCH,
        module=Module.RESEARCH,
        credits_used=credits,
        api_cost_usd=cost.total_cost_usd,
        details={
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
    )


# =============================================================================
# QUICK REFERENCE
# =============================================================================

def get_credit_estimates() -> dict:
    """
    Get estimated credits for common operations.

    Useful for documentation and UI display.
    """
    return {
        "video": {
            "5s_wan_video": calculate_video_credits("higgsfield", "wan", 5).credits_used,
            "5s_veo3_video": calculate_video_credits("higgsfield", "veo3", 5).credits_used,
            "10s_kling_video": calculate_video_credits("higgsfield", "kling", 10).credits_used,
            "5s_runway_video": calculate_video_credits("runway", "gen3a_turbo", 5).credits_used,
        },
        "image": {
            "dalle3_standard": calculate_image_credits("openai", "dall-e-3", 1).credits_used,
            "dalle3_hd": calculate_image_credits("openai", "dall-e-3", 1, quality="hd").credits_used,
            "flux_pro": calculate_image_credits("replicate", "flux-1.1-pro", 1).credits_used,
            "flux_schnell": calculate_image_credits("replicate", "flux-schnell", 1).credits_used,
            "sdxl": calculate_image_credits("stability", "sdxl-1.0", 1).credits_used,
        },
        "voice": {
            "elevenlabs_1000_chars": calculate_voice_credits("elevenlabs", "tts", 1000).credits_used,
            "openai_tts_1000_chars": calculate_voice_credits("openai", "tts", 1000, "tts-1").credits_used,
            "whisper_1_minute": calculate_voice_credits("openai", "transcribe", 1).credits_used,
        },
        "presentation": {
            "presenton_10_slides": calculate_presentation_credits("presenton", 10).credits_used,
            "gamma_10_slides": calculate_presentation_credits("gamma", 10).credits_used,
        },
    }


def get_plan_comparison() -> list[dict]:
    """Get plan comparison table."""
    return [
        {
            "plan": plan.name,
            "price": f"${plan.base_price_usd}/mo",
            "credits": f"{plan.included_credits:,}",
            "users": plan.max_users,
            "modules": [m.value for m in plan.modules],
            "overage": f"${plan.overage_rate}/credit",
            "credit_value": f"${CREDIT_PRICE_USD[plan.tier]}",
        }
        for plan in PLANS.values()
    ]


def estimate_monthly_usage(
    videos_per_month: int = 0,
    images_per_month: int = 0,
    voice_chars_per_month: int = 0,
    presentations_per_month: int = 0,
    research_queries_per_month: int = 0,
    tier: UserTier = UserTier.BRAND,
) -> dict:
    """
    Estimate monthly credit usage.

    Args:
        videos_per_month: Number of 10s videos
        images_per_month: Number of images
        voice_chars_per_month: Characters of TTS
        presentations_per_month: Number of 10-slide decks
        research_queries_per_month: Number of research queries

    Returns:
        Usage estimate with recommended plan
    """
    total_credits = 0
    breakdown = {}

    if videos_per_month > 0:
        video_credits = calculate_video_credits("higgsfield", "veo3", 10).credits_used
        breakdown["video"] = video_credits * videos_per_month
        total_credits += breakdown["video"]

    if images_per_month > 0:
        image_credits = calculate_image_credits("openai", "dall-e-3", 1).credits_used
        breakdown["images"] = image_credits * images_per_month
        total_credits += breakdown["images"]

    if voice_chars_per_month > 0:
        voice_credits = calculate_voice_credits("elevenlabs", "tts", voice_chars_per_month).credits_used
        breakdown["voice"] = voice_credits
        total_credits += breakdown["voice"]

    if presentations_per_month > 0:
        pres_credits = calculate_presentation_credits("presenton", 10).credits_used
        breakdown["presentations"] = pres_credits * presentations_per_month
        total_credits += breakdown["presentations"]

    if research_queries_per_month > 0:
        research_credits = calculate_research_credits("sonar-pro", 500, 1000).credits_used
        breakdown["research"] = research_credits * research_queries_per_month
        total_credits += breakdown["research"]

    # Recommend plan
    recommended = "starter"
    for plan_name, plan in PLANS.items():
        if total_credits <= plan.included_credits:
            recommended = plan_name
            break
    else:
        recommended = "enterprise"

    return {
        "total_credits": total_credits,
        "breakdown": breakdown,
        "recommended_plan": recommended,
        "plan_credits": PLANS[recommended].included_credits,
        "overage_credits": max(0, total_credits - PLANS[recommended].included_credits),
    }
