"""
SpokeStack Credit System

Configurable credit-based billing loaded from pricing_config.json.
All pricing can be adjusted without code changes.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
from functools import lru_cache


# =============================================================================
# CONFIG LOADING
# =============================================================================

CONFIG_PATH = Path(__file__).parent / "pricing_config.json"


@lru_cache(maxsize=1)
def load_pricing_config() -> dict:
    """Load pricing config from JSON file."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return get_default_config()


def reload_pricing_config() -> dict:
    """Force reload of pricing config (clears cache)."""
    load_pricing_config.cache_clear()
    return load_pricing_config()


def get_default_config() -> dict:
    """Fallback defaults if config file missing."""
    return {
        "credit_conversion": {"usd_to_credits_base": 100},
        "tiers": {
            "starter": {"credit_multiplier": 1.0, "credit_price_usd": 0.03},
            "brand": {"credit_multiplier": 0.9, "credit_price_usd": 0.025},
            "agency": {"credit_multiplier": 0.75, "credit_price_usd": 0.02},
            "enterprise": {"credit_multiplier": 0.6, "credit_price_usd": 0.015},
        },
        "plans": {},
        "provider_costs": {},
    }


def get_config() -> dict:
    """Get current pricing config."""
    return load_pricing_config()


def get_tier_config(tier: str) -> dict:
    """Get config for a specific tier."""
    config = get_config()
    return config.get("tiers", {}).get(tier, config["tiers"]["brand"])


def get_plan_config(plan: str) -> dict:
    """Get config for a specific plan."""
    config = get_config()
    return config.get("plans", {}).get(plan, {})


def get_provider_costs(category: str, provider: str) -> dict:
    """Get costs for a specific provider."""
    config = get_config()
    return config.get("provider_costs", {}).get(category, {}).get(provider, {})


def get_model_cost(category: str, provider: str, model: str) -> dict:
    """Get cost for a specific model."""
    provider_costs = get_provider_costs(category, provider)
    return provider_costs.get(model, {})


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CreditUsage:
    """Credit usage for an operation."""
    operation: str
    category: str
    module: str
    credits_used: int
    api_cost_usd: float
    tier: str = "brand"
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "category": self.category,
            "module": self.module,
            "credits_used": self.credits_used,
            "api_cost_usd": round(self.api_cost_usd, 4),
            "tier": self.tier,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class PlanInfo:
    """Plan information from config."""
    name: str
    tier: str
    base_price_usd: float
    included_credits: int
    max_users: int
    modules: list[str]
    overage_rate: float

    @classmethod
    def from_config(cls, plan_key: str) -> "PlanInfo":
        config = get_plan_config(plan_key)
        return cls(
            name=config.get("name", plan_key),
            tier=config.get("tier", "brand"),
            base_price_usd=config.get("base_price_usd", 0),
            included_credits=config.get("included_credits", 0),
            max_users=config.get("max_users", 1),
            modules=config.get("modules", []),
            overage_rate=config.get("overage_rate", 0.03),
        )


# =============================================================================
# CREDIT CONVERSION
# =============================================================================

def cost_to_credits(cost_usd: float, tier: str = "brand") -> int:
    """
    Convert API cost to credits.

    Args:
        cost_usd: Raw API cost in USD
        tier: User tier (affects conversion rate)

    Returns:
        Number of credits
    """
    config = get_config()
    base_rate = config["credit_conversion"]["usd_to_credits_base"]
    tier_config = get_tier_config(tier)
    multiplier = tier_config.get("credit_multiplier", 1.0)

    credits = cost_usd * base_rate * multiplier
    return max(1, round(credits))  # Minimum 1 credit


def credits_to_revenue(credits: int, tier: str = "brand") -> float:
    """
    Calculate our revenue from credits used.

    Args:
        credits: Number of credits
        tier: User tier

    Returns:
        Revenue in USD
    """
    tier_config = get_tier_config(tier)
    rate = tier_config.get("credit_price_usd", 0.025)
    return credits * rate


def get_margin(api_cost: float, credits_used: int, tier: str) -> dict:
    """Calculate our margin on an operation."""
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
# COST CALCULATIONS
# =============================================================================

def calculate_video_cost(
    provider: str,
    model: str,
    duration_seconds: int,
) -> float:
    """Calculate video generation cost in USD."""
    model_cost = get_model_cost("video", provider, model)
    per_second = model_cost.get("per_second", 0.05)
    return per_second * duration_seconds


def calculate_image_cost(
    provider: str,
    model: str,
    num_images: int = 1,
    size: str = "1024x1024",
    quality: str = "standard",
) -> float:
    """Calculate image generation cost in USD."""
    model_cost = get_model_cost("image", provider, model)

    if "per_image" in model_cost:
        return model_cost["per_image"] * num_images
    elif size in model_cost:
        return model_cost[size].get(quality, model_cost[size].get("standard", 0.04)) * num_images

    return 0.04 * num_images  # Default


def calculate_voice_cost(
    provider: str,
    operation: str,
    quantity: float,
    model: str = "default",
) -> float:
    """Calculate voice/audio cost in USD."""
    provider_costs = get_provider_costs("voice", provider)

    if operation == "tts":
        if provider == "elevenlabs":
            per_char = provider_costs.get("tts", {}).get("per_character", 0.0003)
            return per_char * quantity
        else:
            model_key = model if model in provider_costs else "tts-1"
            per_1k = provider_costs.get(model_key, {}).get("per_1k_chars", 0.015)
            return (quantity / 1000) * per_1k

    elif operation == "transcribe":
        per_minute = provider_costs.get("whisper-1", {}).get("per_minute", 0.006)
        return per_minute * quantity

    elif operation == "sound_effect":
        per_gen = provider_costs.get("sound_effect", {}).get("per_generation", 0.10)
        return per_gen * quantity

    return 0.01 * quantity  # Default


def calculate_presentation_cost(
    provider: str,
    num_slides: int,
    include_images: bool = True,
    ai_model: str = "gpt-4o",
    image_provider: str = "dalle3",
) -> float:
    """Calculate presentation generation cost in USD."""
    provider_costs = get_provider_costs("presentation", provider)

    if provider == "presenton":
        # Token-based pricing
        config = get_config()
        tokens_per_slide = provider_costs.get("tokens_per_slide", {"input": 500, "output": 300})
        ai_costs = config.get("provider_costs", {}).get("ai_tokens", {}).get(ai_model, {})

        input_tokens = num_slides * tokens_per_slide["input"]
        output_tokens = num_slides * tokens_per_slide["output"]

        text_cost = (
            (input_tokens / 1000) * ai_costs.get("input_per_1k", 0.005) +
            (output_tokens / 1000) * ai_costs.get("output_per_1k", 0.015)
        )

        if include_images:
            img_costs = config.get("provider_costs", {}).get("image_generation", {})
            image_cost = num_slides * img_costs.get(image_provider, {}).get("per_image", 0.04)
        else:
            image_cost = 0

        return text_cost + image_cost

    else:
        # Per-presentation pricing
        base = provider_costs.get("per_deck", 2.0)
        per_slide = provider_costs.get("per_slide", 0.20)
        return base + (per_slide * num_slides)


def calculate_research_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Calculate research/search cost in USD."""
    model_cost = get_model_cost("research", "perplexity", model)
    return (
        (input_tokens / 1000) * model_cost.get("input_per_1k", 0.001) +
        (output_tokens / 1000) * model_cost.get("output_per_1k", 0.001)
    )


# =============================================================================
# CREDIT CALCULATIONS
# =============================================================================

def calculate_video_credits(
    provider: str,
    model: str,
    duration_seconds: int,
    tier: str = "brand",
) -> CreditUsage:
    """Calculate credits for video generation."""
    cost = calculate_video_cost(provider, model, duration_seconds)
    credits = cost_to_credits(cost, tier)

    return CreditUsage(
        operation=f"video_{model}",
        category="video",
        module="video",
        credits_used=credits,
        api_cost_usd=cost,
        tier=tier,
        details={
            "provider": provider,
            "model": model,
            "duration": duration_seconds,
        },
    )


def calculate_image_credits(
    provider: str,
    model: str,
    num_images: int = 1,
    size: str = "1024x1024",
    quality: str = "standard",
    tier: str = "brand",
) -> CreditUsage:
    """Calculate credits for image generation."""
    cost = calculate_image_cost(provider, model, num_images, size, quality)
    credits = cost_to_credits(cost, tier)

    return CreditUsage(
        operation=f"image_{model}",
        category="image",
        module="studio",
        credits_used=credits,
        api_cost_usd=cost,
        tier=tier,
        details={
            "provider": provider,
            "model": model,
            "num_images": num_images,
            "size": size,
            "quality": quality,
        },
    )


def calculate_voice_credits(
    provider: str,
    operation: str,
    quantity: float,
    model: str = "default",
    tier: str = "brand",
) -> CreditUsage:
    """Calculate credits for voice operations."""
    cost = calculate_voice_cost(provider, operation, quantity, model)
    credits = cost_to_credits(cost, tier)

    return CreditUsage(
        operation=f"voice_{operation}",
        category="voice",
        module="voice",
        credits_used=credits,
        api_cost_usd=cost,
        tier=tier,
        details={
            "provider": provider,
            "operation": operation,
            "quantity": quantity,
        },
    )


def calculate_presentation_credits(
    provider: str,
    num_slides: int,
    include_images: bool = True,
    tier: str = "brand",
) -> CreditUsage:
    """Calculate credits for presentation generation."""
    cost = calculate_presentation_cost(provider, num_slides, include_images)
    credits = cost_to_credits(cost, tier)

    return CreditUsage(
        operation=f"presentation_{provider}",
        category="presentation",
        module="studio",
        credits_used=credits,
        api_cost_usd=cost,
        tier=tier,
        details={
            "provider": provider,
            "num_slides": num_slides,
            "include_images": include_images,
        },
    )


def calculate_research_credits(
    model: str,
    input_tokens: int,
    output_tokens: int,
    tier: str = "brand",
) -> CreditUsage:
    """Calculate credits for research queries."""
    cost = calculate_research_cost(model, input_tokens, output_tokens)
    credits = cost_to_credits(cost, tier)

    return CreditUsage(
        operation="research",
        category="research",
        module="research",
        credits_used=credits,
        api_cost_usd=cost,
        tier=tier,
        details={
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
    )


# =============================================================================
# REFERENCE FUNCTIONS
# =============================================================================

def get_all_plans() -> list[dict]:
    """Get all available plans from config."""
    config = get_config()
    plans = []
    for plan_key, plan_data in config.get("plans", {}).items():
        tier = plan_data.get("tier", "brand")
        tier_config = get_tier_config(tier)
        plans.append({
            "key": plan_key,
            "name": plan_data.get("name", plan_key),
            "price": f"${plan_data.get('base_price_usd', 0)}/mo",
            "credits": plan_data.get("included_credits", 0),
            "users": plan_data.get("max_users", 1),
            "modules": plan_data.get("modules", []),
            "overage": f"${plan_data.get('overage_rate', 0.03)}/credit",
            "credit_value": f"${tier_config.get('credit_price_usd', 0.025)}/credit",
        })
    return plans


def get_all_tiers() -> list[dict]:
    """Get all available tiers from config."""
    config = get_config()
    tiers = []
    for tier_key, tier_data in config.get("tiers", {}).items():
        tiers.append({
            "key": tier_key,
            "name": tier_data.get("name", tier_key),
            "credit_multiplier": tier_data.get("credit_multiplier", 1.0),
            "credit_price": tier_data.get("credit_price_usd", 0.025),
            "description": tier_data.get("description", ""),
        })
    return tiers


def get_credit_estimates(tier: str = "brand") -> dict:
    """Get estimated credits for common operations."""
    return {
        "video": {
            "5s_wan_video": calculate_video_credits("higgsfield", "wan", 5, tier).credits_used,
            "5s_veo3_video": calculate_video_credits("higgsfield", "veo3", 5, tier).credits_used,
            "10s_kling_video": calculate_video_credits("higgsfield", "kling", 10, tier).credits_used,
            "5s_runway_video": calculate_video_credits("runway", "gen3a_turbo", 5, tier).credits_used,
        },
        "image": {
            "dalle3_standard": calculate_image_credits("openai", "dall-e-3", 1, tier=tier).credits_used,
            "flux_pro": calculate_image_credits("replicate", "flux-1.1-pro", 1, tier=tier).credits_used,
            "flux_schnell": calculate_image_credits("replicate", "flux-schnell", 1, tier=tier).credits_used,
        },
        "voice": {
            "elevenlabs_1000_chars": calculate_voice_credits("elevenlabs", "tts", 1000, tier=tier).credits_used,
            "whisper_1_minute": calculate_voice_credits("openai", "transcribe", 1, tier=tier).credits_used,
        },
        "presentation": {
            "presenton_10_slides": calculate_presentation_credits("presenton", 10, tier=tier).credits_used,
            "gamma_10_slides": calculate_presentation_credits("gamma", 10, tier=tier).credits_used,
        },
    }


def estimate_monthly_usage(
    videos_per_month: int = 0,
    images_per_month: int = 0,
    voice_chars_per_month: int = 0,
    presentations_per_month: int = 0,
    research_queries_per_month: int = 0,
    tier: str = "brand",
) -> dict:
    """Estimate monthly credit usage and recommend a plan."""
    total_credits = 0
    breakdown = {}

    if videos_per_month > 0:
        credits = calculate_video_credits("higgsfield", "veo3", 10, tier).credits_used
        breakdown["video"] = credits * videos_per_month
        total_credits += breakdown["video"]

    if images_per_month > 0:
        credits = calculate_image_credits("openai", "dall-e-3", 1, tier=tier).credits_used
        breakdown["images"] = credits * images_per_month
        total_credits += breakdown["images"]

    if voice_chars_per_month > 0:
        credits = calculate_voice_credits("elevenlabs", "tts", voice_chars_per_month, tier=tier).credits_used
        breakdown["voice"] = credits
        total_credits += breakdown["voice"]

    if presentations_per_month > 0:
        credits = calculate_presentation_credits("presenton", 10, tier=tier).credits_used
        breakdown["presentations"] = credits * presentations_per_month
        total_credits += breakdown["presentations"]

    if research_queries_per_month > 0:
        credits = calculate_research_credits("sonar-pro", 500, 1000, tier).credits_used
        breakdown["research"] = credits * research_queries_per_month
        total_credits += breakdown["research"]

    # Recommend plan
    config = get_config()
    recommended = "starter"
    for plan_key, plan_data in config.get("plans", {}).items():
        if total_credits <= plan_data.get("included_credits", 0):
            recommended = plan_key
            break
    else:
        recommended = "enterprise"

    plan_credits = config.get("plans", {}).get(recommended, {}).get("included_credits", 0)

    return {
        "total_credits": total_credits,
        "breakdown": breakdown,
        "recommended_plan": recommended,
        "plan_credits": plan_credits,
        "overage_credits": max(0, total_credits - plan_credits),
    }


def update_pricing(updates: dict) -> dict:
    """
    Update pricing config programmatically.

    Args:
        updates: Dict with pricing updates (merged with existing config)

    Returns:
        Updated config

    Example:
        update_pricing({
            "tiers": {
                "brand": {"credit_price_usd": 0.028}
            }
        })
    """
    config = get_config()

    def deep_merge(base: dict, updates: dict) -> dict:
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    merged = deep_merge(config.copy(), updates)

    # Save to file
    with open(CONFIG_PATH, "w") as f:
        json.dump(merged, f, indent=2)

    # Clear cache to reload
    reload_pricing_config()

    return merged
