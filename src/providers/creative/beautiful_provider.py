"""
Beautiful.ai Creative Provider — Prompt-to-deck presentation generation.
Falls back to structured JSON for ERP's internal renderer if API fails.
"""

import httpx
from typing import Optional

from ..creative_registry import (
    CreativeProvider, AssetType, QualityTier,
    GenerationRequest, GenerationResult,
)


class BeautifulAIProvider(CreativeProvider):
    """Beautiful.ai — AI-powered presentation generation."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url="https://api.beautiful.ai/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=120.0,
        )

    @property
    def provider_id(self) -> str:
        return "beautiful_ai"

    def supports(self, asset_type: AssetType, quality_tier: QualityTier) -> bool:
        return asset_type == AssetType.PRESENTATION

    def estimated_cost(self, request: GenerationRequest) -> float:
        if request.asset_type != AssetType.PRESENTATION:
            return 0.0
        slides = request.num_slides or 10
        return 0.10 * slides  # ~$0.10 per slide

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if request.asset_type != AssetType.PRESENTATION:
            raise ValueError("Beautiful.ai only supports presentations")

        payload = {
            "prompt": request.prompt,
            "num_slides": request.num_slides or 10,
        }
        if request.style:
            payload["style"] = request.style

        try:
            resp = await self.client.post("/presentations/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()

            return GenerationResult(
                asset_url=data.get("editor_url", data.get("url", "")),
                provider_id="beautiful_ai",
                model_id="beautiful_ai_v1",
                cost_usd=self.estimated_cost(request),
                metadata={
                    "presentation_id": data.get("id", ""),
                    "slides": data.get("num_slides", request.num_slides or 10),
                },
            )
        except Exception:
            # Fallback: return structured JSON for ERP's internal renderer
            return GenerationResult(
                asset_url="",
                provider_id="beautiful_ai",
                model_id="fallback_json",
                cost_usd=0.0,
                metadata={
                    "fallback": True,
                    "prompt": request.prompt,
                    "num_slides": request.num_slides or 10,
                    "style": request.style or "corporate",
                    "note": "Beautiful.ai unavailable — use ERP internal renderer with this spec",
                },
            )

    async def close(self) -> None:
        await self.client.aclose()
