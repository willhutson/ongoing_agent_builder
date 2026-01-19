"""
Beautiful.ai Client

Provides access to:
- AI presentation generation
- Slide design
- Template management
"""

from typing import Optional, Literal
from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


PresentationTheme = Literal["modern", "classic", "minimal", "bold", "corporate", "creative"]


class BeautifulAIClient(BaseExternalLLMClient):
    """Client for Beautiful.ai presentation generation API."""

    DEFAULT_BASE_URL = "https://api.beautiful.ai/v1"

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
    ):
        super().__init__(api_key, base_url, timeout)

    async def create_presentation(
        self,
        title: str,
        outline: list[dict],
        theme: PresentationTheme = "modern",
        brand_colors: Optional[list[str]] = None,
        logo_url: Optional[str] = None,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Create a new presentation from outline.

        Args:
            title: Presentation title
            outline: List of slide outlines, each with:
                - title: Slide title
                - content: Main content/points
                - type: Slide type (title, content, chart, image, etc.)
            theme: Visual theme
            brand_colors: Custom brand colors (hex)
            logo_url: URL to company logo
            wait_for_completion: Whether to poll until complete

        Returns:
            GenerationResult with presentation URL
        """
        data = {
            "title": title,
            "slides": outline,
            "theme": theme,
        }
        if brand_colors:
            data["brand_colors"] = brand_colors
        if logo_url:
            data["logo_url"] = logo_url

        try:
            result = await self._post("/presentations", data)
            presentation_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=presentation_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(presentation_id, "/presentations")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def generate_from_brief(
        self,
        brief: str,
        num_slides: int = 10,
        theme: PresentationTheme = "modern",
        audience: Optional[str] = None,
        tone: Optional[str] = None,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate a full presentation from a text brief.

        Args:
            brief: Text description of the presentation
            num_slides: Target number of slides
            theme: Visual theme
            audience: Target audience description
            tone: Desired tone (professional, casual, inspiring, etc.)
            wait_for_completion: Whether to poll

        Returns:
            GenerationResult with presentation URL
        """
        data = {
            "brief": brief,
            "num_slides": num_slides,
            "theme": theme,
        }
        if audience:
            data["audience"] = audience
        if tone:
            data["tone"] = tone

        try:
            result = await self._post("/presentations/generate", data)
            presentation_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=presentation_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(presentation_id, "/presentations")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def add_slide(
        self,
        presentation_id: str,
        slide_type: str,
        title: str,
        content: Optional[str] = None,
        position: Optional[int] = None,
    ) -> GenerationResult:
        """
        Add a slide to an existing presentation.

        Args:
            presentation_id: ID of the presentation
            slide_type: Type of slide (title, content, chart, quote, etc.)
            title: Slide title
            content: Slide content
            position: Position to insert (None = end)

        Returns:
            GenerationResult with slide details
        """
        data = {
            "type": slide_type,
            "title": title,
        }
        if content:
            data["content"] = content
        if position is not None:
            data["position"] = position

        try:
            result = await self._post(f"/presentations/{presentation_id}/slides", data)

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result,
                metadata={"slide_id": result.get("id")},
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def get_presentation(self, presentation_id: str) -> GenerationResult:
        """Get presentation details and status."""
        try:
            result = await self._get(f"/presentations/{presentation_id}")
            return self._parse_presentation_response(result)
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def export_presentation(
        self,
        presentation_id: str,
        format: str = "pdf",
    ) -> GenerationResult:
        """
        Export presentation to PDF or PPTX.

        Args:
            presentation_id: ID of the presentation
            format: Export format (pdf, pptx)

        Returns:
            GenerationResult with download URL
        """
        try:
            result = await self._post(
                f"/presentations/{presentation_id}/export",
                {"format": format},
            )

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_url=result.get("download_url"),
                metadata={"format": format},
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def list_templates(self) -> GenerationResult:
        """List available presentation templates."""
        try:
            result = await self._get("/templates")
            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result.get("templates", []),
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    def _parse_status(self, result: dict) -> TaskStatus:
        """Parse Beautiful.ai presentation status."""
        status = result.get("status", "").lower()
        if status in ("completed", "ready"):
            return TaskStatus.COMPLETED
        elif status in ("failed", "error"):
            return TaskStatus.FAILED
        elif status in ("processing", "generating"):
            return TaskStatus.PROCESSING
        return TaskStatus.PENDING

    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse completed presentation."""
        return GenerationResult(
            success=True,
            task_id=result.get("id"),
            status=TaskStatus.COMPLETED,
            output_url=result.get("url") or result.get("share_url"),
            output_data={
                "slides": result.get("slides", []),
                "slide_count": result.get("slide_count"),
            },
            metadata={
                "title": result.get("title"),
                "theme": result.get("theme"),
                "created_at": result.get("created_at"),
            },
        )

    def _parse_presentation_response(self, result: dict) -> GenerationResult:
        """Parse any presentation response."""
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
        """Check if Beautiful.ai API is accessible."""
        try:
            await self._get("/templates")
            return True
        except Exception:
            return False
