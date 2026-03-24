"""
Creative Provider Registry — Routes generation requests to the cheapest
available provider based on asset type and quality tier.

Follows the same adapter+fallback pattern as the ERP billing tiers.
The agent doesn't choose the provider — it calls generate() and the
registry picks the cheapest provider that matches the tier.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import logging
import time

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# Core Types
# ══════════════════════════════════════════════════════════════

class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    VOICE = "voice"
    MUSIC = "music"
    PRESENTATION = "presentation"
    VIDEO_COMPOSITION = "video_composition"


class QualityTier(str, Enum):
    DRAFT = "draft"
    STANDARD = "standard"
    PREMIUM = "premium"


@dataclass
class GenerationRequest:
    """Request to generate a creative asset."""
    prompt: str
    asset_type: AssetType
    quality_tier: QualityTier = QualityTier.STANDARD

    # Type-specific params
    duration_seconds: Optional[int] = None       # video, voice, music
    resolution: Optional[str] = None             # image, video (e.g. "1024x1024", "1080p")
    aspect_ratio: Optional[str] = None           # image, video (e.g. "16:9", "9:16")
    voice_id: Optional[str] = None               # voice
    reference_image_url: Optional[str] = None    # image (image-to-image), video (image-to-video)
    num_variants: int = 1                        # image (multiple outputs)
    style: Optional[str] = None                  # presentation style
    num_slides: Optional[int] = None             # presentation

    # Composition-specific (video_composition is handled by the agent, not a provider)
    scenes: Optional[list[dict]] = None


@dataclass
class GenerationResult:
    """Result from a creative generation."""
    asset_url: str
    provider_id: str
    model_id: str
    cost_usd: float = 0.0
    duration_ms: int = 0
    thumbnail_url: Optional[str] = None
    variants: list[str] = field(default_factory=list)  # additional URLs for multi-variant
    metadata: dict = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════
# Provider Interface
# ══════════════════════════════════════════════════════════════

class CreativeProvider(ABC):
    """Base class for creative asset providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier."""
        pass

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate a creative asset."""
        pass

    @abstractmethod
    def supports(self, asset_type: AssetType, quality_tier: QualityTier) -> bool:
        """Check if this provider supports the given asset type and tier."""
        pass

    @abstractmethod
    def estimated_cost(self, request: GenerationRequest) -> float:
        """Estimate cost in USD for a generation request."""
        pass


# ══════════════════════════════════════════════════════════════
# Registry
# ══════════════════════════════════════════════════════════════

# Default provider chains per (asset_type, quality_tier)
# Each chain is tried in order; first success wins.
DEFAULT_CHAINS: dict[tuple[AssetType, QualityTier], list[str]] = {
    # Image
    (AssetType.IMAGE, QualityTier.DRAFT): ["openai_creative", "fal"],
    (AssetType.IMAGE, QualityTier.STANDARD): ["fal", "openai_creative"],
    (AssetType.IMAGE, QualityTier.PREMIUM): ["openai_creative", "fal"],
    # Video
    (AssetType.VIDEO, QualityTier.DRAFT): ["fal"],
    (AssetType.VIDEO, QualityTier.STANDARD): ["fal"],
    (AssetType.VIDEO, QualityTier.PREMIUM): ["fal"],
    # Voice
    (AssetType.VOICE, QualityTier.DRAFT): ["openai_creative"],
    (AssetType.VOICE, QualityTier.STANDARD): ["elevenlabs"],
    (AssetType.VOICE, QualityTier.PREMIUM): ["elevenlabs"],
    # Presentation
    (AssetType.PRESENTATION, QualityTier.DRAFT): ["beautiful_ai"],
    (AssetType.PRESENTATION, QualityTier.STANDARD): ["beautiful_ai"],
    (AssetType.PRESENTATION, QualityTier.PREMIUM): ["beautiful_ai"],
}


class CreativeRegistry:
    """
    Routes generation requests to providers using fallback chains.

    The agent calls generate() — the registry picks the cheapest provider
    that matches the quality tier, falling back through the chain on failure.
    """

    def __init__(self):
        self._providers: dict[str, CreativeProvider] = {}
        self._chains: dict[tuple[AssetType, QualityTier], list[str]] = dict(DEFAULT_CHAINS)

    def register(self, provider: CreativeProvider) -> None:
        """Register a provider."""
        self._providers[provider.provider_id] = provider

    def set_chain(self, asset_type: AssetType, quality_tier: QualityTier,
                  provider_ids: list[str]) -> None:
        """Override the default chain for a specific (type, tier) combo."""
        self._chains[(asset_type, quality_tier)] = provider_ids

    def list_providers(self) -> list[str]:
        """List all registered provider IDs."""
        return list(self._providers.keys())

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Generate a creative asset using the provider chain.

        Tries each provider in the chain for the (asset_type, quality_tier) combo.
        Falls back on failure. Raises RuntimeError if all providers fail.
        """
        # Video compositions are handled by the agent (JSON spec), not a provider
        if request.asset_type == AssetType.VIDEO_COMPOSITION:
            return GenerationResult(
                asset_url="",
                provider_id="agent",
                model_id="remotion_spec",
                metadata={"scenes": request.scenes or [], "note": "Composition spec — render via ERP Remotion"},
            )

        chain_key = (request.asset_type, request.quality_tier)
        chain = self._chains.get(chain_key, [])

        if not chain:
            raise RuntimeError(
                f"No provider chain configured for {request.asset_type.value}/{request.quality_tier.value}"
            )

        errors = []
        for provider_id in chain:
            provider = self._providers.get(provider_id)
            if not provider:
                continue
            if not provider.supports(request.asset_type, request.quality_tier):
                continue
            try:
                start = time.monotonic()
                result = await provider.generate(request)
                result.duration_ms = int((time.monotonic() - start) * 1000)
                logger.info(
                    "Creative generation: %s/%s via %s in %dms ($%.4f)",
                    request.asset_type.value, request.quality_tier.value,
                    provider_id, result.duration_ms, result.cost_usd,
                )
                return result
            except Exception as e:
                logger.warning("Provider %s failed: %s", provider_id, e)
                errors.append(f"{provider_id}: {e}")

        raise RuntimeError(
            f"All providers failed for {request.asset_type.value}/{request.quality_tier.value}: "
            + "; ".join(errors)
        )
