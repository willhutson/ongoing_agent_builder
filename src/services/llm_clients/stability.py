"""
Stability AI Client

Provides access to:
- Stable Diffusion 3
- SDXL
- Image upscaling
- Inpainting/Outpainting
"""

from typing import Optional, Literal
import base64
from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


StabilityModel = Literal["sd3-large", "sd3-large-turbo", "sd3-medium", "sdxl-1.0", "stable-image-ultra"]
OutputFormat = Literal["png", "jpeg", "webp"]


class StabilityClient(BaseExternalLLMClient):
    """Client for Stability AI API."""

    DEFAULT_BASE_URL = "https://api.stability.ai/v2beta"

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
    ):
        super().__init__(api_key, base_url, timeout)

    def _get_headers(self) -> dict:
        """Stability uses Bearer auth with Accept header."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    async def generate_image(
        self,
        prompt: str,
        model: StabilityModel = "sd3-large",
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "1:1",
        seed: Optional[int] = None,
        output_format: OutputFormat = "png",
    ) -> GenerationResult:
        """
        Generate image using Stable Diffusion 3 or SDXL.

        Args:
            prompt: Text description
            model: Model to use
            negative_prompt: What to avoid
            aspect_ratio: Output ratio (1:1, 16:9, 21:9, 2:3, 3:2, 4:5, 5:4, 9:16, 9:21)
            seed: Random seed for reproducibility
            output_format: Output image format

        Returns:
            GenerationResult with image data
        """
        data = {
            "prompt": prompt,
            "model": model,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format,
        }
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = seed

        try:
            response = await self.client.post(
                "/stable-image/generate/sd3",
                data=data,
                headers={**self._get_headers(), "Accept": "image/*"},
            )
            response.raise_for_status()

            # Response is raw image bytes
            image_base64 = base64.b64encode(response.content).decode()

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=image_base64,
                metadata={
                    "model": model,
                    "format": output_format,
                    "seed": seed,
                },
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def generate_ultra(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "1:1",
        seed: Optional[int] = None,
        output_format: OutputFormat = "png",
    ) -> GenerationResult:
        """
        Generate high-quality image using Stable Image Ultra.

        Args:
            prompt: Text description
            negative_prompt: What to avoid
            aspect_ratio: Output ratio
            seed: Random seed
            output_format: Output format

        Returns:
            GenerationResult with image data
        """
        data = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format,
        }
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = seed

        try:
            response = await self.client.post(
                "/stable-image/generate/ultra",
                data=data,
                headers={**self._get_headers(), "Accept": "image/*"},
            )
            response.raise_for_status()

            image_base64 = base64.b64encode(response.content).decode()

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=image_base64,
                metadata={
                    "model": "stable-image-ultra",
                    "format": output_format,
                },
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def upscale_image(
        self,
        image_base64: str,
        prompt: Optional[str] = None,
        output_format: OutputFormat = "png",
    ) -> GenerationResult:
        """
        Upscale an image using Stability's upscaler.

        Args:
            image_base64: Base64-encoded source image
            prompt: Optional guidance prompt
            output_format: Output format

        Returns:
            GenerationResult with upscaled image
        """
        data = {
            "image": image_base64,
            "output_format": output_format,
        }
        if prompt:
            data["prompt"] = prompt

        try:
            response = await self.client.post(
                "/stable-image/upscale/conservative",
                data=data,
                headers={**self._get_headers(), "Accept": "image/*"},
            )
            response.raise_for_status()

            upscaled_base64 = base64.b64encode(response.content).decode()

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=upscaled_base64,
                metadata={"format": output_format},
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def inpaint(
        self,
        image_base64: str,
        mask_base64: str,
        prompt: str,
        negative_prompt: Optional[str] = None,
        output_format: OutputFormat = "png",
    ) -> GenerationResult:
        """
        Inpaint a region of an image.

        Args:
            image_base64: Base64-encoded source image
            mask_base64: Base64-encoded mask (white = inpaint area)
            prompt: What to generate
            negative_prompt: What to avoid
            output_format: Output format

        Returns:
            GenerationResult with inpainted image
        """
        data = {
            "image": image_base64,
            "mask": mask_base64,
            "prompt": prompt,
            "output_format": output_format,
        }
        if negative_prompt:
            data["negative_prompt"] = negative_prompt

        try:
            response = await self.client.post(
                "/stable-image/edit/inpaint",
                data=data,
                headers={**self._get_headers(), "Accept": "image/*"},
            )
            response.raise_for_status()

            result_base64 = base64.b64encode(response.content).decode()

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result_base64,
                metadata={"format": output_format},
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def outpaint(
        self,
        image_base64: str,
        prompt: str,
        left: int = 0,
        right: int = 0,
        up: int = 0,
        down: int = 0,
        output_format: OutputFormat = "png",
    ) -> GenerationResult:
        """
        Expand an image beyond its borders.

        Args:
            image_base64: Base64-encoded source image
            prompt: Description of what to generate
            left/right/up/down: Pixels to expand in each direction
            output_format: Output format

        Returns:
            GenerationResult with expanded image
        """
        data = {
            "image": image_base64,
            "prompt": prompt,
            "left": left,
            "right": right,
            "up": up,
            "down": down,
            "output_format": output_format,
        }

        try:
            response = await self.client.post(
                "/stable-image/edit/outpaint",
                data=data,
                headers={**self._get_headers(), "Accept": "image/*"},
            )
            response.raise_for_status()

            result_base64 = base64.b64encode(response.content).decode()

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result_base64,
                metadata={"format": output_format},
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    def _parse_status(self, result: dict) -> TaskStatus:
        """Stability API is synchronous."""
        return TaskStatus.COMPLETED

    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse Stability response."""
        return GenerationResult(
            success=True,
            status=TaskStatus.COMPLETED,
            output_data=result,
        )

    async def health_check(self) -> bool:
        """Check if Stability API is accessible."""
        try:
            response = await self.client.get("/user/account")
            return response.status_code == 200
        except Exception:
            return False
