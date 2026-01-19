"""
Runway Client

Provides access to:
- Gen-3 Alpha (video generation)
- Video editing
- Motion Brush
"""

from typing import Optional, Literal
from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


RunwayModel = Literal["gen3a_turbo", "gen3a"]


class RunwayClient(BaseExternalLLMClient):
    """Client for Runway API (Gen-3 Alpha video generation)."""

    DEFAULT_BASE_URL = "https://api.runwayml.com/v1"

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 180.0,  # Video generation takes time
    ):
        super().__init__(api_key, base_url, timeout)

    def _get_headers(self) -> dict:
        """Runway uses X-Runway-Key header."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Runway-Version": "2024-11-06",
            "Content-Type": "application/json",
        }

    async def text_to_video(
        self,
        prompt: str,
        model: RunwayModel = "gen3a_turbo",
        duration: int = 5,
        ratio: str = "16:9",
        seed: Optional[int] = None,
        watermark: bool = False,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate video from text prompt using Gen-3 Alpha.

        Args:
            prompt: Text description of the video
            model: gen3a_turbo (faster) or gen3a (higher quality)
            duration: Video duration (5 or 10 seconds)
            ratio: Aspect ratio (16:9, 9:16)
            seed: Random seed for reproducibility
            watermark: Include Runway watermark
            wait_for_completion: Whether to poll until complete

        Returns:
            GenerationResult with video URL
        """
        data = {
            "promptText": prompt,
            "model": model,
            "duration": duration,
            "ratio": ratio,
            "watermark": watermark,
        }
        if seed is not None:
            data["seed"] = seed

        try:
            result = await self._post("/image_to_video", data)
            task_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=task_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(task_id, "/tasks")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def image_to_video(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        model: RunwayModel = "gen3a_turbo",
        duration: int = 5,
        seed: Optional[int] = None,
        watermark: bool = False,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate video from an image using Gen-3 Alpha.

        Args:
            image_url: URL of the source image
            prompt: Optional motion/action guidance
            model: gen3a_turbo (faster) or gen3a (higher quality)
            duration: Video duration (5 or 10 seconds)
            seed: Random seed
            watermark: Include Runway watermark
            wait_for_completion: Whether to poll until complete

        Returns:
            GenerationResult with video URL
        """
        data = {
            "promptImage": image_url,
            "model": model,
            "duration": duration,
            "watermark": watermark,
        }
        if prompt:
            data["promptText"] = prompt
        if seed is not None:
            data["seed"] = seed

        try:
            result = await self._post("/image_to_video", data)
            task_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=task_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(task_id, "/tasks")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def first_last_frame(
        self,
        first_image_url: str,
        last_image_url: str,
        prompt: Optional[str] = None,
        model: RunwayModel = "gen3a_turbo",
        duration: int = 5,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate video interpolating between two images.

        Args:
            first_image_url: URL of the starting frame
            last_image_url: URL of the ending frame
            prompt: Optional motion guidance
            model: gen3a model to use
            duration: Video duration
            wait_for_completion: Whether to poll

        Returns:
            GenerationResult with video URL
        """
        data = {
            "promptImage": first_image_url,
            "lastFrame": last_image_url,
            "model": model,
            "duration": duration,
        }
        if prompt:
            data["promptText"] = prompt

        try:
            result = await self._post("/image_to_video", data)
            task_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=task_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(task_id, "/tasks")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def get_task(self, task_id: str) -> GenerationResult:
        """Get the status of a video generation task."""
        try:
            result = await self._get(f"/tasks/{task_id}")
            return self._parse_task_response(result)
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        try:
            await self._post(f"/tasks/{task_id}/cancel", {})
            return True
        except Exception:
            return False

    def _parse_status(self, result: dict) -> TaskStatus:
        """Parse Runway task status."""
        status = result.get("status", "").upper()
        if status == "SUCCEEDED":
            return TaskStatus.COMPLETED
        elif status in ("FAILED", "CANCELLED"):
            return TaskStatus.FAILED
        elif status in ("RUNNING", "PENDING"):
            return TaskStatus.PROCESSING
        return TaskStatus.PENDING

    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse completed Runway task."""
        output = result.get("output", [])
        video_url = output[0] if output else None

        return GenerationResult(
            success=True,
            task_id=result.get("id"),
            status=TaskStatus.COMPLETED,
            output_url=video_url,
            metadata={
                "model": result.get("model"),
                "duration": result.get("duration"),
                "created_at": result.get("createdAt"),
            },
        )

    def _parse_task_response(self, result: dict) -> GenerationResult:
        """Parse any task response."""
        status = self._parse_status(result)
        if status == TaskStatus.COMPLETED:
            return self._parse_completed_result(result)
        elif status == TaskStatus.FAILED:
            return GenerationResult(
                success=False,
                task_id=result.get("id"),
                status=TaskStatus.FAILED,
                error=result.get("failure", "Task failed"),
            )
        return GenerationResult(
            success=True,
            task_id=result.get("id"),
            status=status,
            metadata={"progress": result.get("progress")},
        )

    async def health_check(self) -> bool:
        """Check if Runway API is accessible."""
        try:
            # Runway doesn't have a dedicated health endpoint
            # We'll try to access the tasks endpoint
            await self._get("/tasks", params={"limit": 1})
            return True
        except Exception:
            return False
