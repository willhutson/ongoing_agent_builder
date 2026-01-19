"""
External LLM Billing & Cost Tracking

Comprehensive cost models for all external LLM providers.
Use this to calculate costs and set client pricing.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal
from enum import Enum
from datetime import datetime


class CostCategory(str, Enum):
    """Categories of billable operations."""
    VIDEO = "video"
    IMAGE = "image"
    VOICE = "voice"
    TRANSCRIPTION = "transcription"
    PRESENTATION = "presentation"
    RESEARCH = "research"
    VISION = "vision"


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for any operation."""
    provider: str
    operation: str
    category: CostCategory
    base_cost_usd: float
    quantity: float = 1.0
    unit: str = "item"
    total_cost_usd: float = 0.0
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.total_cost_usd == 0.0:
            self.total_cost_usd = self.base_cost_usd * self.quantity

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "operation": self.operation,
            "category": self.category.value,
            "base_cost_usd": self.base_cost_usd,
            "quantity": self.quantity,
            "unit": self.unit,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# VIDEO GENERATION COSTS
# =============================================================================

# Higgsfield - Multi-model video platform
HIGGSFIELD_COSTS = {
    # Per-second pricing (approximate)
    "sora2": {"per_second": 0.20, "min_duration": 5, "max_duration": 20},
    "veo3": {"per_second": 0.15, "min_duration": 5, "max_duration": 16},
    "veo3.1": {"per_second": 0.18, "min_duration": 5, "max_duration": 16},
    "kling": {"per_second": 0.08, "min_duration": 5, "max_duration": 10},
    "kling1.6": {"per_second": 0.10, "min_duration": 5, "max_duration": 10},
    "wan": {"per_second": 0.05, "min_duration": 5, "max_duration": 10},
    "wan2.1": {"per_second": 0.06, "min_duration": 5, "max_duration": 10},
    "minimax": {"per_second": 0.07, "min_duration": 5, "max_duration": 60},
    "luma": {"per_second": 0.10, "min_duration": 5, "max_duration": 10},
    "pika": {"per_second": 0.04, "min_duration": 3, "max_duration": 10},
    "hunyuan": {"per_second": 0.05, "min_duration": 5, "max_duration": 10},
    "seedance": {"per_second": 0.04, "min_duration": 5, "max_duration": 10},
}

# Runway Gen-3 Alpha
RUNWAY_COSTS = {
    "gen3a": {"per_second": 0.10, "min_duration": 5, "max_duration": 10},
    "gen3a_turbo": {"per_second": 0.05, "min_duration": 5, "max_duration": 10},
}


def calculate_video_cost(
    provider: str,
    model: str,
    duration_seconds: int,
    resolution: str = "1080p",
) -> CostBreakdown:
    """
    Calculate video generation cost.

    Args:
        provider: "higgsfield" or "runway"
        model: Model name (e.g., "veo3", "gen3a_turbo")
        duration_seconds: Video duration
        resolution: Video resolution (affects some models)

    Returns:
        CostBreakdown with pricing details
    """
    if provider == "higgsfield":
        costs = HIGGSFIELD_COSTS.get(model, HIGGSFIELD_COSTS["wan"])
    elif provider == "runway":
        costs = RUNWAY_COSTS.get(model, RUNWAY_COSTS["gen3a_turbo"])
    else:
        raise ValueError(f"Unknown video provider: {provider}")

    base_cost = costs["per_second"]
    total = base_cost * duration_seconds

    # Resolution multiplier (some providers charge more for 4K)
    if resolution == "4k" and provider == "higgsfield":
        total *= 1.5

    return CostBreakdown(
        provider=provider,
        operation=f"{model}_video",
        category=CostCategory.VIDEO,
        base_cost_usd=base_cost,
        quantity=duration_seconds,
        unit="seconds",
        total_cost_usd=total,
        details={
            "model": model,
            "duration": duration_seconds,
            "resolution": resolution,
            "per_second_rate": base_cost,
        },
    )


# =============================================================================
# IMAGE GENERATION COSTS
# =============================================================================

# OpenAI DALL-E 3
DALLE_COSTS = {
    "1024x1024": {"standard": 0.040, "hd": 0.080},
    "1792x1024": {"standard": 0.080, "hd": 0.120},
    "1024x1792": {"standard": 0.080, "hd": 0.120},
}

# Replicate Flux
FLUX_COSTS = {
    "flux-1.1-pro": 0.040,  # Per image
    "flux-schnell": 0.003,  # Per image (fast, lower quality)
    "flux-dev": 0.025,  # Per image
}

# Stability AI
STABILITY_COSTS = {
    "sd3-large": 0.065,  # Per image
    "sd3-large-turbo": 0.040,
    "sd3-medium": 0.035,
    "stable-image-ultra": 0.080,
    "sdxl-1.0": 0.020,
    "upscale": 0.025,  # Per upscale
}


def calculate_image_cost(
    provider: str,
    model: str,
    size: str = "1024x1024",
    quality: str = "standard",
    num_images: int = 1,
) -> CostBreakdown:
    """
    Calculate image generation cost.

    Args:
        provider: "openai", "replicate", or "stability"
        model: Model name
        size: Image dimensions
        quality: Quality level (standard/hd)
        num_images: Number of images

    Returns:
        CostBreakdown with pricing details
    """
    if provider == "openai":
        size_costs = DALLE_COSTS.get(size, DALLE_COSTS["1024x1024"])
        base_cost = size_costs.get(quality, size_costs["standard"])
    elif provider == "replicate":
        base_cost = FLUX_COSTS.get(model, FLUX_COSTS["flux-1.1-pro"])
    elif provider == "stability":
        base_cost = STABILITY_COSTS.get(model, STABILITY_COSTS["sd3-large"])
    else:
        raise ValueError(f"Unknown image provider: {provider}")

    total = base_cost * num_images

    return CostBreakdown(
        provider=provider,
        operation=f"{model}_image",
        category=CostCategory.IMAGE,
        base_cost_usd=base_cost,
        quantity=num_images,
        unit="images",
        total_cost_usd=total,
        details={
            "model": model,
            "size": size,
            "quality": quality,
            "num_images": num_images,
        },
    )


# =============================================================================
# VOICE/AUDIO COSTS
# =============================================================================

# ElevenLabs
ELEVENLABS_COSTS = {
    "tts": 0.00030,  # Per character (~$0.30 per 1000 chars)
    "voice_clone": 0.00030,  # Same as TTS once cloned
    "sound_effect": 0.10,  # Per generation
}

# OpenAI TTS
OPENAI_TTS_COSTS = {
    "tts-1": 0.015,  # Per 1000 characters
    "tts-1-hd": 0.030,  # Per 1000 characters
}

# OpenAI Whisper
WHISPER_COSTS = {
    "whisper-1": 0.006,  # Per minute of audio
}


def calculate_voice_cost(
    provider: str,
    operation: str,
    quantity: float,
    model: str = "default",
) -> CostBreakdown:
    """
    Calculate voice/audio cost.

    Args:
        provider: "elevenlabs" or "openai"
        operation: "tts", "voice_clone", "sound_effect", "transcribe"
        quantity: Characters (TTS) or minutes (transcription)
        model: Model name for OpenAI

    Returns:
        CostBreakdown with pricing details
    """
    if provider == "elevenlabs":
        if operation == "tts":
            base_cost = ELEVENLABS_COSTS["tts"]
            unit = "characters"
        elif operation == "sound_effect":
            base_cost = ELEVENLABS_COSTS["sound_effect"]
            unit = "generations"
        else:
            base_cost = ELEVENLABS_COSTS["tts"]
            unit = "characters"
    elif provider == "openai":
        if operation == "transcribe":
            base_cost = WHISPER_COSTS["whisper-1"]
            unit = "minutes"
        else:
            tts_model = model if model in OPENAI_TTS_COSTS else "tts-1"
            base_cost = OPENAI_TTS_COSTS[tts_model] / 1000  # Per character
            unit = "characters"
    else:
        raise ValueError(f"Unknown voice provider: {provider}")

    total = base_cost * quantity

    return CostBreakdown(
        provider=provider,
        operation=operation,
        category=CostCategory.VOICE if operation != "transcribe" else CostCategory.TRANSCRIPTION,
        base_cost_usd=base_cost,
        quantity=quantity,
        unit=unit,
        total_cost_usd=total,
        details={"model": model},
    )


# =============================================================================
# VISION/ANALYSIS COSTS
# =============================================================================

# OpenAI Vision (GPT-4V)
VISION_COSTS = {
    "gpt-4o": {
        "input_per_1k": 0.005,
        "output_per_1k": 0.015,
        "image_base": 0.00255,  # Base cost per image
        "image_per_tile": 0.00255,  # 512x512 tiles
    },
    "gpt-4-turbo": {
        "input_per_1k": 0.01,
        "output_per_1k": 0.03,
        "image_base": 0.00765,
        "image_per_tile": 0.00765,
    },
}


def calculate_vision_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    num_images: int = 1,
    image_detail: str = "auto",
) -> CostBreakdown:
    """
    Calculate vision/image analysis cost.

    Args:
        model: "gpt-4o" or "gpt-4-turbo"
        input_tokens: Text input tokens
        output_tokens: Text output tokens
        num_images: Number of images analyzed
        image_detail: "low", "high", or "auto"

    Returns:
        CostBreakdown with pricing details
    """
    costs = VISION_COSTS.get(model, VISION_COSTS["gpt-4o"])

    text_cost = (
        (input_tokens / 1000) * costs["input_per_1k"] +
        (output_tokens / 1000) * costs["output_per_1k"]
    )

    # Image cost depends on detail level
    if image_detail == "low":
        image_cost = costs["image_base"] * num_images
    else:
        # High detail: base + tiles (assume 4 tiles average)
        image_cost = (costs["image_base"] + costs["image_per_tile"] * 4) * num_images

    total = text_cost + image_cost

    return CostBreakdown(
        provider="openai",
        operation="vision_analysis",
        category=CostCategory.VISION,
        base_cost_usd=total / max(num_images, 1),
        quantity=num_images,
        unit="images",
        total_cost_usd=total,
        details={
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "text_cost": round(text_cost, 4),
            "image_cost": round(image_cost, 4),
        },
    )


# =============================================================================
# RESEARCH COSTS
# =============================================================================

# Perplexity
PERPLEXITY_COSTS = {
    "sonar-pro": {"input_per_1k": 0.003, "output_per_1k": 0.015},
    "sonar": {"input_per_1k": 0.001, "output_per_1k": 0.001},
    "sonar-reasoning": {"input_per_1k": 0.001, "output_per_1k": 0.005},
}


def calculate_research_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> CostBreakdown:
    """
    Calculate research/search cost.

    Args:
        model: Perplexity model name
        input_tokens: Input tokens
        output_tokens: Output tokens

    Returns:
        CostBreakdown with pricing details
    """
    costs = PERPLEXITY_COSTS.get(model, PERPLEXITY_COSTS["sonar"])

    total = (
        (input_tokens / 1000) * costs["input_per_1k"] +
        (output_tokens / 1000) * costs["output_per_1k"]
    )

    return CostBreakdown(
        provider="perplexity",
        operation="research",
        category=CostCategory.RESEARCH,
        base_cost_usd=total,
        quantity=1,
        unit="queries",
        total_cost_usd=total,
        details={
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
    )


# =============================================================================
# PRESENTATION COSTS (included from presenton.py)
# =============================================================================

PRESENTATION_COSTS = {
    "beautiful_ai": {"per_deck": 3.00, "per_slide": 0.30},
    "gamma": {"per_deck": 2.00, "per_slide": 0.20},
    "presenton": {"per_deck": 0.00, "uses_ai_tokens": True},  # Token-based
}


def calculate_presentation_cost(
    provider: str,
    num_slides: int,
    ai_model: str = "gpt-4o",
    include_images: bool = True,
    image_provider: str = "dalle3",
) -> CostBreakdown:
    """
    Calculate presentation generation cost.

    Args:
        provider: "beautiful_ai", "gamma", or "presenton"
        num_slides: Number of slides
        ai_model: AI model for Presenton
        include_images: Whether images are included
        image_provider: Image provider for Presenton

    Returns:
        CostBreakdown with pricing details
    """
    if provider == "presenton":
        # Token-based pricing (estimate)
        input_tokens = num_slides * 500
        output_tokens = num_slides * 300

        # Use gpt-4o costs as baseline
        text_cost = (input_tokens / 1000) * 0.005 + (output_tokens / 1000) * 0.015

        # Add image costs if included
        if include_images:
            image_cost_per = 0.04 if image_provider == "dalle3" else 0.01
            image_cost = num_slides * image_cost_per
        else:
            image_cost = 0

        total = text_cost + image_cost

        return CostBreakdown(
            provider="presenton",
            operation="presentation",
            category=CostCategory.PRESENTATION,
            base_cost_usd=total / num_slides,
            quantity=num_slides,
            unit="slides",
            total_cost_usd=total,
            details={
                "ai_model": ai_model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "text_cost": round(text_cost, 4),
                "image_cost": round(image_cost, 4),
                "include_images": include_images,
            },
        )
    else:
        costs = PRESENTATION_COSTS.get(provider, PRESENTATION_COSTS["gamma"])
        total = costs["per_deck"] + (costs["per_slide"] * num_slides)

        return CostBreakdown(
            provider=provider,
            operation="presentation",
            category=CostCategory.PRESENTATION,
            base_cost_usd=costs["per_slide"],
            quantity=num_slides,
            unit="slides",
            total_cost_usd=total,
            details={
                "base_fee": costs["per_deck"],
                "per_slide_fee": costs["per_slide"],
            },
        )


# =============================================================================
# CLIENT BILLING HELPERS
# =============================================================================

@dataclass
class ClientBillingRate:
    """Suggested client billing rate."""
    category: CostCategory
    our_cost: float
    suggested_price: float
    margin_percent: float
    margin_usd: float


def suggest_client_pricing(
    cost: CostBreakdown,
    margin_percent: float = 200,  # 200% = 3x our cost
    minimum_price: float = 1.00,
) -> ClientBillingRate:
    """
    Suggest client pricing based on our cost.

    Args:
        cost: Our cost breakdown
        margin_percent: Desired margin (100 = 2x, 200 = 3x)
        minimum_price: Minimum price to charge

    Returns:
        ClientBillingRate with suggested pricing
    """
    suggested = max(
        cost.total_cost_usd * (1 + margin_percent / 100),
        minimum_price
    )
    margin_usd = suggested - cost.total_cost_usd
    actual_margin = (margin_usd / suggested) * 100 if suggested > 0 else 0

    return ClientBillingRate(
        category=cost.category,
        our_cost=round(cost.total_cost_usd, 4),
        suggested_price=round(suggested, 2),
        margin_percent=round(actual_margin, 1),
        margin_usd=round(margin_usd, 2),
    )


# =============================================================================
# QUICK REFERENCE TABLES
# =============================================================================

def get_video_pricing_table() -> list[dict]:
    """Get video pricing reference table."""
    table = []
    for model, costs in HIGGSFIELD_COSTS.items():
        table.append({
            "provider": "higgsfield",
            "model": model,
            "per_second": costs["per_second"],
            "5s_video": costs["per_second"] * 5,
            "10s_video": costs["per_second"] * 10,
        })
    for model, costs in RUNWAY_COSTS.items():
        table.append({
            "provider": "runway",
            "model": model,
            "per_second": costs["per_second"],
            "5s_video": costs["per_second"] * 5,
            "10s_video": costs["per_second"] * 10,
        })
    return sorted(table, key=lambda x: x["5s_video"])


def get_image_pricing_table() -> list[dict]:
    """Get image pricing reference table."""
    return [
        {"provider": "openai", "model": "dall-e-3", "size": "1024x1024", "standard": 0.04, "hd": 0.08},
        {"provider": "openai", "model": "dall-e-3", "size": "1792x1024", "standard": 0.08, "hd": 0.12},
        {"provider": "replicate", "model": "flux-1.1-pro", "per_image": 0.04},
        {"provider": "replicate", "model": "flux-schnell", "per_image": 0.003},
        {"provider": "replicate", "model": "flux-dev", "per_image": 0.025},
        {"provider": "stability", "model": "sd3-large", "per_image": 0.065},
        {"provider": "stability", "model": "stable-image-ultra", "per_image": 0.08},
        {"provider": "stability", "model": "sdxl-1.0", "per_image": 0.02},
    ]


def get_voice_pricing_table() -> list[dict]:
    """Get voice/audio pricing reference table."""
    return [
        {"provider": "elevenlabs", "operation": "tts", "unit": "1000 chars", "cost": 0.30},
        {"provider": "elevenlabs", "operation": "sound_effect", "unit": "generation", "cost": 0.10},
        {"provider": "openai", "operation": "tts-1", "unit": "1000 chars", "cost": 0.015},
        {"provider": "openai", "operation": "tts-1-hd", "unit": "1000 chars", "cost": 0.030},
        {"provider": "openai", "operation": "whisper", "unit": "minute", "cost": 0.006},
    ]


def get_presentation_pricing_table() -> list[dict]:
    """Get presentation pricing reference table."""
    return [
        {"provider": "beautiful_ai", "base_fee": 3.00, "per_slide": 0.30, "10_slides": 6.00},
        {"provider": "gamma", "base_fee": 2.00, "per_slide": 0.20, "10_slides": 4.00},
        {"provider": "presenton", "base_fee": 0.00, "per_slide": "~$0.04", "10_slides": "~$0.40"},
    ]


def get_full_pricing_summary() -> dict:
    """Get complete pricing summary for all providers."""
    return {
        "video": get_video_pricing_table(),
        "image": get_image_pricing_table(),
        "voice": get_voice_pricing_table(),
        "presentation": get_presentation_pricing_table(),
        "research": [
            {"provider": "perplexity", "model": "sonar-pro", "per_query_estimate": "$0.02-0.10"},
            {"provider": "perplexity", "model": "sonar", "per_query_estimate": "$0.002-0.01"},
        ],
    }
