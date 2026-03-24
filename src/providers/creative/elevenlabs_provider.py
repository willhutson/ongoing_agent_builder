"""
ElevenLabs Creative Provider — Voice synthesis (Flash, Multilingual v3).
Standard and premium tiers for voice generation.
"""

import httpx
import base64

from ..creative_registry import (
    CreativeProvider, AssetType, QualityTier,
    GenerationRequest, GenerationResult,
)


ELEVENLABS_MODELS = {
    QualityTier.STANDARD: ("eleven_flash_v2_5", 0.015),
    QualityTier.PREMIUM: ("eleven_multilingual_v2", 0.03),
}

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel


class ElevenLabsProvider(CreativeProvider):
    """ElevenLabs — Premium voice synthesis."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url="https://api.elevenlabs.io/v1",
            headers={"xi-api-key": api_key},
            timeout=60.0,
        )

    @property
    def provider_id(self) -> str:
        return "elevenlabs"

    def supports(self, asset_type: AssetType, quality_tier: QualityTier) -> bool:
        return asset_type == AssetType.VOICE and quality_tier in ELEVENLABS_MODELS

    def estimated_cost(self, request: GenerationRequest) -> float:
        if request.asset_type != AssetType.VOICE:
            return 0.0
        model_info = ELEVENLABS_MODELS.get(request.quality_tier)
        if model_info:
            _, cost_per_1k_chars = model_info
            char_count = len(request.prompt)
            return (char_count / 1000) * cost_per_1k_chars
        return 0.0

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if request.asset_type != AssetType.VOICE:
            raise ValueError("ElevenLabs only supports voice generation")

        model_info = ELEVENLABS_MODELS.get(request.quality_tier)
        if not model_info:
            raise ValueError(f"ElevenLabs does not support tier {request.quality_tier.value}")

        model_id, cost_per_1k = model_info
        voice_id = request.voice_id or DEFAULT_VOICE_ID

        payload = {
            "text": request.prompt,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }

        resp = await self.client.post(
            f"/text-to-speech/{voice_id}",
            json=payload,
            headers={"Accept": "audio/mpeg"},
        )
        resp.raise_for_status()

        audio_b64 = base64.b64encode(resp.content).decode()
        char_count = len(request.prompt)
        cost = (char_count / 1000) * cost_per_1k

        return GenerationResult(
            asset_url=f"data:audio/mpeg;base64,{audio_b64}",
            provider_id="elevenlabs",
            model_id=model_id,
            cost_usd=cost,
            metadata={
                "format": "mp3",
                "voice_id": voice_id,
                "characters": char_count,
            },
        )

    async def close(self) -> None:
        await self.client.aclose()
