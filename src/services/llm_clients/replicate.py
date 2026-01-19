"""
Replicate Client

Provides access to:
- Flux (image generation)
- SDXL
- Other hosted models
"""

from typing import Optional, Literal
from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


FluxModel = Literal["flux-1.1-pro", "flux-schnell", "flux-dev"]


class ReplicateClient(BaseExternalLLMClient):
    """Client for Replicate API (Flux, SDXL, etc.)."""

    DEFAULT_BASE_URL = "https://api.replicate.com/v1"

    # Model version IDs for common models
    FLUX_VERSIONS = {
        "flux-1.1-pro": "black-forest-labs/flux-1.1-pro",
        "flux-schnell": "black-forest-labs/flux-schnell",
        "flux-dev": "black-forest-labs/flux-dev",
    }

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
    ):
        super().__init__(api_key, base_url, timeout)

    def _get_headers(self) -> dict:
        """Replicate uses Token auth."""
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_image_flux(
        self,
        prompt: str,
        model: FluxModel = "flux-1.1-pro",
        width: int = 1024,
        height: int = 1024,
        num_outputs: int = 1,
        guidance_scale: float = 3.5,
        num_inference_steps: int = 28,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate image using Flux models.

        Args:
            prompt: Text description
            model: Flux model variant
            width: Output width (must be multiple of 8)
            height: Output height (must be multiple of 8)
            num_outputs: Number of images
            guidance_scale: CFG scale (higher = more prompt adherence)
            num_inference_steps: Denoising steps
            wait_for_completion: Whether to poll until complete

        Returns:
            GenerationResult with image URL(s)
        """
        model_id = self.FLUX_VERSIONS.get(model, model)

        data = {
            "input": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_outputs": num_outputs,
                "guidance_scale": guidance_scale,
                "num_inference_steps": num_inference_steps,
            }
        }

        try:
            result = await self._post(f"/models/{model_id}/predictions", data)
            prediction_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=prediction_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(prediction_id, "/predictions")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def image_to_image(
        self,
        image_url: str,
        prompt: str,
        model: FluxModel = "flux-dev",
        strength: float = 0.75,
        guidance_scale: float = 7.5,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Transform an image using Flux.

        Args:
            image_url: Source image URL
            prompt: Transformation description
            model: Flux model
            strength: How much to transform (0-1)
            guidance_scale: CFG scale
            wait_for_completion: Whether to poll

        Returns:
            GenerationResult with transformed image URL
        """
        model_id = self.FLUX_VERSIONS.get(model, model)

        data = {
            "input": {
                "image": image_url,
                "prompt": prompt,
                "strength": strength,
                "guidance_scale": guidance_scale,
            }
        }

        try:
            result = await self._post(f"/models/{model_id}/predictions", data)
            prediction_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=prediction_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(prediction_id, "/predictions")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def inpaint(
        self,
        image_url: str,
        mask_url: str,
        prompt: str,
        model: FluxModel = "flux-dev",
        guidance_scale: float = 7.5,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Inpaint an image region using Flux.

        Args:
            image_url: Source image URL
            mask_url: Mask URL (white = inpaint area)
            prompt: What to generate in masked area
            model: Flux model
            guidance_scale: CFG scale
            wait_for_completion: Whether to poll

        Returns:
            GenerationResult with inpainted image URL
        """
        model_id = self.FLUX_VERSIONS.get(model, model)

        data = {
            "input": {
                "image": image_url,
                "mask": mask_url,
                "prompt": prompt,
                "guidance_scale": guidance_scale,
            }
        }

        try:
            result = await self._post(f"/models/{model_id}/predictions", data)
            prediction_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=prediction_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(prediction_id, "/predictions")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def get_prediction(self, prediction_id: str) -> GenerationResult:
        """Get the status of a prediction."""
        result = await self._get(f"/predictions/{prediction_id}")
        return self._parse_prediction_response(result)

    async def cancel_prediction(self, prediction_id: str) -> bool:
        """Cancel a running prediction."""
        try:
            await self._post(f"/predictions/{prediction_id}/cancel", {})
            return True
        except Exception:
            return False

    def _parse_status(self, result: dict) -> TaskStatus:
        """Parse Replicate prediction status."""
        status = result.get("status", "").lower()
        if status == "succeeded":
            return TaskStatus.COMPLETED
        elif status in ("failed", "canceled"):
            return TaskStatus.FAILED
        elif status == "processing":
            return TaskStatus.PROCESSING
        return TaskStatus.PENDING

    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse completed Replicate prediction."""
        output = result.get("output")
        # Replicate returns list of URLs for images
        if isinstance(output, list):
            output_url = output[0] if output else None
            output_data = output if len(output) > 1 else None
        else:
            output_url = output
            output_data = None

        return GenerationResult(
            success=True,
            task_id=result.get("id"),
            status=TaskStatus.COMPLETED,
            output_url=output_url,
            output_data=output_data,
            metadata={
                "model": result.get("model"),
                "version": result.get("version"),
                "metrics": result.get("metrics"),
            },
        )

    def _parse_prediction_response(self, result: dict) -> GenerationResult:
        """Parse any prediction response."""
        status = self._parse_status(result)
        if status == TaskStatus.COMPLETED:
            return self._parse_completed_result(result)
        elif status == TaskStatus.FAILED:
            return GenerationResult(
                success=False,
                task_id=result.get("id"),
                status=TaskStatus.FAILED,
                error=result.get("error", "Prediction failed"),
            )
        return GenerationResult(
            success=True,
            task_id=result.get("id"),
            status=status,
        )

    async def health_check(self) -> bool:
        """Check if Replicate API is accessible."""
        try:
            await self._get("/models")
            return True
        except Exception:
            return False
