"""
OpenAI Creative Provider — Image (GPT Image 1 Mini / 1.5) and Voice (gpt-4o-mini-tts).
Uses the existing OPENAI_API_KEY from the environment.
"""

import httpx
import base64

from ..creative_registry import (
    CreativeProvider, AssetType, QualityTier,
    GenerationRequest, GenerationResult,
)


# Model mapping
OPENAI_MODELS = {
    (AssetType.IMAGE, QualityTier.DRAFT): ("gpt-image-1-mini", "low", 0.003),
    (AssetType.IMAGE, QualityTier.STANDARD): ("gpt-image-1-mini", "medium", 0.007),
    (AssetType.IMAGE, QualityTier.PREMIUM): ("gpt-image-1", "high", 0.04),
    (AssetType.VOICE, QualityTier.DRAFT): ("gpt-4o-mini-tts", None, 0.003),
    (AssetType.VOICE, QualityTier.STANDARD): ("gpt-4o-mini-tts", None, 0.003),
}


class OpenAICreativeProvider(CreativeProvider):
    """OpenAI — GPT Image generation + TTS voice."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=120.0,
        )

    @property
    def provider_id(self) -> str:
        return "openai_creative"

    def supports(self, asset_type: AssetType, quality_tier: QualityTier) -> bool:
        return (asset_type, quality_tier) in OPENAI_MODELS

    def estimated_cost(self, request: GenerationRequest) -> float:
        key = (request.asset_type, request.quality_tier)
        if key in OPENAI_MODELS:
            _, _, base_cost = OPENAI_MODELS[key]
            return base_cost * request.num_variants
        return 0.0

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if request.asset_type == AssetType.IMAGE:
            return await self._generate_image(request)
        elif request.asset_type == AssetType.VOICE:
            return await self._generate_voice(request)
        raise ValueError(f"OpenAI does not support {request.asset_type.value}")

    async def _generate_image(self, request: GenerationRequest) -> GenerationResult:
        key = (AssetType.IMAGE, request.quality_tier)
        model_id, quality, base_cost = OPENAI_MODELS[key]

        payload = {
            "model": model_id,
            "prompt": request.prompt,
            "n": request.num_variants,
            "size": request.resolution or "1024x1024",
        }
        if quality:
            payload["quality"] = quality

        resp = await self.client.post("/images/generations", json=payload)
        resp.raise_for_status()
        data = resp.json()

        images = data.get("data", [])
        asset_url = images[0].get("url", "") if images else ""
        variants = [img.get("url", "") for img in images[1:]]

        return GenerationResult(
            asset_url=asset_url,
            provider_id="openai_creative",
            model_id=model_id,
            cost_usd=base_cost * request.num_variants,
            variants=variants,
        )

    async def _generate_voice(self, request: GenerationRequest) -> GenerationResult:
        key = (AssetType.VOICE, request.quality_tier)
        model_id, _, base_cost = OPENAI_MODELS[key]

        payload = {
            "model": model_id,
            "input": request.prompt,
            "voice": request.voice_id or "alloy",
        }

        resp = await self.client.post("/audio/speech", json=payload)
        resp.raise_for_status()

        # OpenAI TTS returns raw audio bytes — encode as data URL for transport
        audio_b64 = base64.b64encode(resp.content).decode()
        audio_url = f"data:audio/mp3;base64,{audio_b64[:100]}..."  # Truncated for logging

        # In practice, the full base64 or a temp file URL would be returned
        return GenerationResult(
            asset_url=f"data:audio/mp3;base64,{audio_b64}",
            provider_id="openai_creative",
            model_id=model_id,
            cost_usd=base_cost,
            metadata={"format": "mp3", "voice": request.voice_id or "alloy"},
        )

    async def close(self) -> None:
        await self.client.aclose()
