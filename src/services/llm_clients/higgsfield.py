"""
Higgsfield AI Client

Multi-model video generation platform supporting:
- Sora 2 (OpenAI)
- Veo 3.1 (Google)
- WAN (Alibaba)
- Kling (Kuaishou)
- Minimax
"""

from typing import Optional, Literal
from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


VideoModel = Literal["sora2", "veo3", "wan", "kling", "minimax"]


class HiggsfieldClient(BaseExternalLLMClient):
    """Client for Higgsfield AI video generation API."""

    DEFAULT_BASE_URL = "https://api.higgsfield.ai/v1"

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
    ):
        super().__init__(api_key, base_url, timeout)

    async def text_to_video(
        self,
        prompt: str,
        model: VideoModel = "veo3",
        duration: int = 5,
        aspect_ratio: str = "16:9",
        quality: str = "high",
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate video from text prompt.

        Args:
            prompt: Text description of the video
            model: Video model to use (sora2, veo3, wan, kling, minimax)
            duration: Video duration in seconds (5-60 depending on model)
            aspect_ratio: Aspect ratio (16:9, 9:16, 1:1)
            quality: Quality level (draft, standard, high)
            wait_for_completion: Whether to poll until complete

        Returns:
            GenerationResult with video URL
        """
        data = {
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "quality": quality,
        }

        result = await self._post("/generations/text-to-video", data)
        task_id = result.get("id") or result.get("task_id")

        if not wait_for_completion:
            return GenerationResult(
                success=True,
                task_id=task_id,
                status=TaskStatus.PENDING,
            )

        return await self._poll_status(task_id, "/generations")

    async def image_to_video(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        model: VideoModel = "kling",
        duration: int = 5,
        motion_strength: float = 0.7,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate video from an image.

        Args:
            image_url: URL of the source image
            prompt: Optional motion/action description
            model: Video model (kling and wan work best for img2vid)
            duration: Video duration in seconds
            motion_strength: How much motion (0.0-1.0)
            wait_for_completion: Whether to poll until complete

        Returns:
            GenerationResult with video URL
        """
        data = {
            "image_url": image_url,
            "model": model,
            "duration": duration,
            "motion_strength": motion_strength,
        }
        if prompt:
            data["prompt"] = prompt

        result = await self._post("/generations/image-to-video", data)
        task_id = result.get("id") or result.get("task_id")

        if not wait_for_completion:
            return GenerationResult(
                success=True,
                task_id=task_id,
                status=TaskStatus.PENDING,
            )

        return await self._poll_status(task_id, "/generations")

    async def product_to_video(
        self,
        product_image_url: str,
        style: str = "commercial",
        scene: Optional[str] = None,
        model: VideoModel = "veo3",
        duration: int = 10,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate product showcase video.

        Args:
            product_image_url: URL of product image
            style: Video style (commercial, lifestyle, minimal, dramatic)
            scene: Optional scene description
            model: Video model to use
            duration: Video duration
            wait_for_completion: Whether to poll until complete

        Returns:
            GenerationResult with video URL
        """
        data = {
            "product_image_url": product_image_url,
            "style": style,
            "model": model,
            "duration": duration,
        }
        if scene:
            data["scene"] = scene

        result = await self._post("/generations/product-to-video", data)
        task_id = result.get("id") or result.get("task_id")

        if not wait_for_completion:
            return GenerationResult(
                success=True,
                task_id=task_id,
                status=TaskStatus.PENDING,
            )

        return await self._poll_status(task_id, "/generations")

    async def get_generation_status(self, task_id: str) -> GenerationResult:
        """Get the status of a generation task."""
        result = await self._get(f"/generations/{task_id}")
        return self._parse_generation_response(result)

    async def list_models(self) -> dict:
        """List available video models and their capabilities."""
        return await self._get("/models")

    def _parse_status(self, result: dict) -> TaskStatus:
        """Parse task status from Higgsfield response."""
        status = result.get("status", "").lower()
        if status in ("completed", "succeeded", "done"):
            return TaskStatus.COMPLETED
        elif status in ("failed", "error"):
            return TaskStatus.FAILED
        elif status in ("processing", "running", "in_progress"):
            return TaskStatus.PROCESSING
        return TaskStatus.PENDING

    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse completed result from Higgsfield response."""
        return GenerationResult(
            success=True,
            task_id=result.get("id"),
            status=TaskStatus.COMPLETED,
            output_url=result.get("video_url") or result.get("output", {}).get("url"),
            metadata={
                "model": result.get("model"),
                "duration": result.get("duration"),
                "resolution": result.get("resolution"),
            },
        )

    def _parse_generation_response(self, result: dict) -> GenerationResult:
        """Parse any generation response."""
        status = self._parse_status(result)
        if status == TaskStatus.COMPLETED:
            return self._parse_completed_result(result)
        elif status == TaskStatus.FAILED:
            return GenerationResult(
                success=False,
                task_id=result.get("id"),
                status=TaskStatus.FAILED,
                error=result.get("error", "Generation failed"),
            )
        return GenerationResult(
            success=True,
            task_id=result.get("id"),
            status=status,
        )

    async def health_check(self) -> bool:
        """Check if Higgsfield API is accessible."""
        try:
            await self._get("/models")
            return True
        except Exception:
            return False
