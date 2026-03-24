"""
fal.ai Creative Provider — Single API key covers Wan, Seedance, Kling,
Pika, Flux, Seedream. Primary aggregator for video and image generation.
"""

import httpx
from typing import Optional

from ..creative_registry import (
    CreativeProvider, AssetType, QualityTier,
    GenerationRequest, GenerationResult,
)


# Model mapping per (asset_type, quality_tier)
FAL_MODELS = {
    # Image
    (AssetType.IMAGE, QualityTier.DRAFT): ("fal-ai/flux/schnell", 0.003),
    (AssetType.IMAGE, QualityTier.STANDARD): ("fal-ai/seedream-4.5", 0.02),
    (AssetType.IMAGE, QualityTier.PREMIUM): ("fal-ai/flux-pro/v1.1", 0.05),
    # Video
    (AssetType.VIDEO, QualityTier.DRAFT): ("fal-ai/wan/v2.5/1080p", 0.30),
    (AssetType.VIDEO, QualityTier.STANDARD): ("fal-ai/kling-video/v2.5/turbo/text-to-video", 0.50),
    (AssetType.VIDEO, QualityTier.PREMIUM): ("fal-ai/kling-video/v2.5/pro/text-to-video", 1.00),
}


class FalProvider(CreativeProvider):
    """fal.ai aggregator — video (Wan, Kling, Seedance) + image (Flux, Seedream)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url="https://queue.fal.run",
            headers={"Authorization": f"Key {api_key}"},
            timeout=120.0,
        )

    @property
    def provider_id(self) -> str:
        return "fal"

    def supports(self, asset_type: AssetType, quality_tier: QualityTier) -> bool:
        return (asset_type, quality_tier) in FAL_MODELS

    def estimated_cost(self, request: GenerationRequest) -> float:
        key = (request.asset_type, request.quality_tier)
        if key in FAL_MODELS:
            _, base_cost = FAL_MODELS[key]
            return base_cost * request.num_variants
        return 0.0

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        key = (request.asset_type, request.quality_tier)
        if key not in FAL_MODELS:
            raise ValueError(f"fal.ai does not support {request.asset_type.value}/{request.quality_tier.value}")

        model_id, base_cost = FAL_MODELS[key]

        # Build request payload
        payload: dict = {"prompt": request.prompt}

        if request.asset_type == AssetType.IMAGE:
            if request.resolution:
                # Parse "1024x1024" into width/height
                parts = request.resolution.split("x")
                if len(parts) == 2:
                    payload["image_size"] = {"width": int(parts[0]), "height": int(parts[1])}
            if request.aspect_ratio:
                payload["aspect_ratio"] = request.aspect_ratio
            if request.num_variants > 1:
                payload["num_images"] = request.num_variants
            if request.reference_image_url:
                payload["image_url"] = request.reference_image_url

        elif request.asset_type == AssetType.VIDEO:
            if request.duration_seconds:
                payload["duration"] = str(request.duration_seconds)
            if request.aspect_ratio:
                payload["aspect_ratio"] = request.aspect_ratio
            if request.reference_image_url:
                payload["image_url"] = request.reference_image_url

        # Submit to fal queue
        submit_resp = await self.client.post(f"/{model_id}", json=payload)
        submit_resp.raise_for_status()
        submit_data = submit_resp.json()

        request_id = submit_data.get("request_id", "")

        # Poll for result
        result_url = f"https://queue.fal.run/{model_id}/requests/{request_id}/status"
        result_data = await self._poll_result(model_id, request_id)

        # Extract URLs from result
        asset_url = ""
        variants = []

        if request.asset_type == AssetType.IMAGE:
            images = result_data.get("images", [])
            if images:
                asset_url = images[0].get("url", "")
                variants = [img.get("url", "") for img in images[1:]]
        elif request.asset_type == AssetType.VIDEO:
            video = result_data.get("video", {})
            asset_url = video.get("url", "") if isinstance(video, dict) else str(video)

        return GenerationResult(
            asset_url=asset_url,
            provider_id="fal",
            model_id=model_id,
            cost_usd=base_cost * max(request.num_variants, 1),
            variants=variants,
            metadata={"request_id": request_id},
        )

    async def _poll_result(self, model_id: str, request_id: str,
                           max_wait: int = 300) -> dict:
        """Poll fal queue until result is ready."""
        import asyncio

        status_url = f"https://queue.fal.run/{model_id}/requests/{request_id}/status"
        result_url = f"https://queue.fal.run/{model_id}/requests/{request_id}"

        elapsed = 0
        interval = 2
        while elapsed < max_wait:
            status_resp = await self.client.get(status_url)
            status_data = status_resp.json()
            status = status_data.get("status", "")

            if status == "COMPLETED":
                result_resp = await self.client.get(result_url)
                result_resp.raise_for_status()
                return result_resp.json()
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"fal.ai generation failed: {status_data}")

            await asyncio.sleep(interval)
            elapsed += interval
            interval = min(interval * 1.5, 10)

        raise TimeoutError(f"fal.ai generation timed out after {max_wait}s")

    async def close(self) -> None:
        await self.client.aclose()
