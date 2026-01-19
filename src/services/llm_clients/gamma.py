"""
Gamma Client

Provides access to:
- AI presentation generation
- Document generation
- Website/page generation
"""

from typing import Optional, Literal
from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


GammaOutputType = Literal["presentation", "document", "webpage"]
GammaStyle = Literal["professional", "creative", "minimal", "bold", "elegant"]


class GammaClient(BaseExternalLLMClient):
    """Client for Gamma.app presentation and document generation API."""

    DEFAULT_BASE_URL = "https://api.gamma.app/v1"

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
    ):
        super().__init__(api_key, base_url, timeout)

    async def generate(
        self,
        prompt: str,
        output_type: GammaOutputType = "presentation",
        style: GammaStyle = "professional",
        num_cards: int = 10,
        include_images: bool = True,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate content from a prompt.

        Args:
            prompt: Description of what to generate
            output_type: Type of output (presentation, document, webpage)
            style: Visual style
            num_cards: Target number of cards/slides
            include_images: Whether to include AI-generated images
            wait_for_completion: Whether to poll until complete

        Returns:
            GenerationResult with content URL
        """
        data = {
            "prompt": prompt,
            "output_type": output_type,
            "style": style,
            "num_cards": num_cards,
            "include_images": include_images,
        }

        try:
            result = await self._post("/generate", data)
            generation_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=generation_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(generation_id, "/generations")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def generate_from_outline(
        self,
        title: str,
        outline: list[dict],
        output_type: GammaOutputType = "presentation",
        style: GammaStyle = "professional",
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate content from a structured outline.

        Args:
            title: Content title
            outline: List of sections, each with:
                - heading: Section heading
                - points: Key points to cover
                - image_prompt: Optional image description
            output_type: Type of output
            style: Visual style
            wait_for_completion: Whether to poll

        Returns:
            GenerationResult with content URL
        """
        data = {
            "title": title,
            "outline": outline,
            "output_type": output_type,
            "style": style,
        }

        try:
            result = await self._post("/generate/outline", data)
            generation_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=generation_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(generation_id, "/generations")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def generate_from_document(
        self,
        document_url: str,
        output_type: GammaOutputType = "presentation",
        style: GammaStyle = "professional",
        summarize: bool = True,
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate content from an existing document (PDF, DOCX, etc.).

        Args:
            document_url: URL to the source document
            output_type: Type of output to generate
            style: Visual style
            summarize: Whether to summarize long documents
            wait_for_completion: Whether to poll

        Returns:
            GenerationResult with content URL
        """
        data = {
            "document_url": document_url,
            "output_type": output_type,
            "style": style,
            "summarize": summarize,
        }

        try:
            result = await self._post("/generate/document", data)
            generation_id = result.get("id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=generation_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(generation_id, "/generations")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def edit_card(
        self,
        generation_id: str,
        card_index: int,
        instruction: str,
    ) -> GenerationResult:
        """
        Edit a specific card in a generation.

        Args:
            generation_id: ID of the generation
            card_index: Index of the card to edit
            instruction: Edit instruction

        Returns:
            GenerationResult with updated card
        """
        data = {
            "card_index": card_index,
            "instruction": instruction,
        }

        try:
            result = await self._post(f"/generations/{generation_id}/edit", data)

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result,
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def get_generation(self, generation_id: str) -> GenerationResult:
        """Get generation details and status."""
        try:
            result = await self._get(f"/generations/{generation_id}")
            return self._parse_generation_response(result)
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def export(
        self,
        generation_id: str,
        format: str = "pdf",
    ) -> GenerationResult:
        """
        Export generation to PDF or PPTX.

        Args:
            generation_id: ID of the generation
            format: Export format (pdf, pptx)

        Returns:
            GenerationResult with download URL
        """
        try:
            result = await self._post(
                f"/generations/{generation_id}/export",
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

    async def list_generations(self, limit: int = 20) -> GenerationResult:
        """List recent generations."""
        try:
            result = await self._get("/generations", params={"limit": limit})
            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result.get("generations", []),
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    def _parse_status(self, result: dict) -> TaskStatus:
        """Parse Gamma generation status."""
        status = result.get("status", "").lower()
        if status in ("completed", "ready", "done"):
            return TaskStatus.COMPLETED
        elif status in ("failed", "error"):
            return TaskStatus.FAILED
        elif status in ("processing", "generating"):
            return TaskStatus.PROCESSING
        return TaskStatus.PENDING

    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse completed generation."""
        return GenerationResult(
            success=True,
            task_id=result.get("id"),
            status=TaskStatus.COMPLETED,
            output_url=result.get("url") or result.get("share_url"),
            output_data={
                "cards": result.get("cards", []),
                "card_count": result.get("card_count"),
            },
            metadata={
                "title": result.get("title"),
                "output_type": result.get("output_type"),
                "style": result.get("style"),
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
        """Check if Gamma API is accessible."""
        try:
            await self._get("/generations", params={"limit": 1})
            return True
        except Exception:
            return False
