"""
Presenton Client

Open-source AI presentation generator.
Self-hosted alternative to Beautiful.ai and Gamma.

Repo: https://github.com/presenton/presenton
"""

from typing import Optional, Literal
from dataclasses import dataclass
from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


PresentonTheme = Literal["default", "modern", "minimal", "corporate", "creative"]
PresentonTone = Literal["casual", "professional", "educational", "formal"]
PresentonVerbosity = Literal["concise", "balanced", "detailed"]
ExportFormat = Literal["pptx", "pdf"]


@dataclass
class PresentationCost:
    """Cost breakdown for a presentation generation."""
    ai_model: str
    input_tokens: int
    output_tokens: int
    images_generated: int
    estimated_cost_usd: float

    def to_dict(self) -> dict:
        return {
            "ai_model": self.ai_model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "images_generated": self.images_generated,
            "estimated_cost_usd": self.estimated_cost_usd,
        }


# Cost per 1K tokens (approximate, as of 2025)
TOKEN_COSTS = {
    "gpt-4.1": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "claude-sonnet-4": {"input": 0.003, "output": 0.015},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
    "ollama": {"input": 0, "output": 0},  # Local, no API cost
}

# Cost per image
IMAGE_COSTS = {
    "dalle3": 0.04,  # Standard quality
    "dalle3_hd": 0.08,
    "gemini": 0.002,
    "pexels": 0,  # Free
    "pixabay": 0,  # Free
}


class PresentonClient(BaseExternalLLMClient):
    """
    Client for self-hosted Presenton presentation generator.

    Presenton uses your existing AI keys (OpenAI, Claude, Gemini)
    so costs are based on token usage, not per-presentation fees.
    """

    DEFAULT_BASE_URL = "http://localhost:8080/api/v1"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: Optional[str] = None,  # Optional auth for your deployment
        timeout: float = 120.0,
    ):
        # Presenton doesn't require an API key by default (self-hosted)
        super().__init__(api_key or "presenton", base_url, timeout)

    def _get_headers(self) -> dict:
        """Headers for Presenton API."""
        headers = {"Content-Type": "application/json"}
        if self.api_key and self.api_key != "presenton":
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def generate_presentation(
        self,
        prompt: str,
        num_slides: int = 10,
        language: str = "English",
        theme: PresentonTheme = "modern",
        tone: PresentonTone = "professional",
        verbosity: PresentonVerbosity = "balanced",
        include_images: bool = True,
        image_provider: str = "dalle3",
        export_format: ExportFormat = "pptx",
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate a presentation from a text prompt.

        Args:
            prompt: Description of the presentation topic
            num_slides: Number of slides to generate (5-30)
            language: Output language
            theme: Visual theme
            tone: Content tone
            verbosity: How detailed the content should be
            include_images: Whether to generate/include images
            image_provider: Image source (dalle3, gemini, pexels, pixabay)
            export_format: Output format (pptx, pdf)
            wait_for_completion: Whether to poll until complete

        Returns:
            GenerationResult with presentation URL and cost tracking
        """
        data = {
            "prompt": prompt,
            "num_slides": num_slides,
            "language": language,
            "theme": theme,
            "tone": tone,
            "verbosity": verbosity,
            "include_images": include_images,
            "image_provider": image_provider,
            "export_format": export_format,
        }

        try:
            result = await self._post("/ppt/presentation/generate", data)
            presentation_id = result.get("id") or result.get("presentation_id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=presentation_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(presentation_id, "/ppt/presentation")
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
        theme: PresentonTheme = "modern",
        tone: PresentonTone = "professional",
        include_images: bool = True,
        image_provider: str = "dalle3",
        export_format: ExportFormat = "pptx",
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate a presentation from a structured outline.

        Args:
            title: Presentation title
            outline: List of slide outlines with:
                - title: Slide title
                - points: Key points (list of strings)
                - image_prompt: Optional image description
            theme: Visual theme
            tone: Content tone
            include_images: Whether to generate images
            image_provider: Image source
            export_format: Output format
            wait_for_completion: Whether to poll

        Returns:
            GenerationResult with presentation URL and cost
        """
        data = {
            "title": title,
            "outline": outline,
            "theme": theme,
            "tone": tone,
            "include_images": include_images,
            "image_provider": image_provider,
            "export_format": export_format,
        }

        try:
            result = await self._post("/ppt/presentation/from-outline", data)
            presentation_id = result.get("id") or result.get("presentation_id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=presentation_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(presentation_id, "/ppt/presentation")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def generate_from_document(
        self,
        document_url: str,
        num_slides: int = 10,
        theme: PresentonTheme = "modern",
        summarize: bool = True,
        export_format: ExportFormat = "pptx",
        wait_for_completion: bool = True,
    ) -> GenerationResult:
        """
        Generate a presentation from an existing document.

        Args:
            document_url: URL to PDF, DOCX, or text file
            num_slides: Target number of slides
            theme: Visual theme
            summarize: Whether to summarize long documents
            export_format: Output format
            wait_for_completion: Whether to poll

        Returns:
            GenerationResult with presentation URL
        """
        data = {
            "document_url": document_url,
            "num_slides": num_slides,
            "theme": theme,
            "summarize": summarize,
            "export_format": export_format,
        }

        try:
            result = await self._post("/ppt/presentation/from-document", data)
            presentation_id = result.get("id") or result.get("presentation_id")

            if not wait_for_completion:
                return GenerationResult(
                    success=True,
                    task_id=presentation_id,
                    status=TaskStatus.PENDING,
                )

            return await self._poll_status(presentation_id, "/ppt/presentation")
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def get_presentation(self, presentation_id: str) -> GenerationResult:
        """Get presentation status and details."""
        try:
            result = await self._get(f"/ppt/presentation/{presentation_id}")
            return self._parse_presentation_response(result)
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def download_presentation(
        self,
        presentation_id: str,
        format: ExportFormat = "pptx",
    ) -> GenerationResult:
        """
        Get download URL for a completed presentation.

        Args:
            presentation_id: ID of the presentation
            format: Export format

        Returns:
            GenerationResult with download URL
        """
        try:
            result = await self._get(
                f"/ppt/presentation/{presentation_id}/download",
                params={"format": format},
            )

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_url=result.get("download_url") or result.get("url"),
                metadata={"format": format},
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def list_themes(self) -> GenerationResult:
        """List available presentation themes."""
        try:
            result = await self._get("/ppt/themes")
            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result.get("themes", []),
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    def calculate_cost(
        self,
        ai_model: str,
        input_tokens: int,
        output_tokens: int,
        images_generated: int = 0,
        image_provider: str = "dalle3",
    ) -> PresentationCost:
        """
        Calculate the estimated cost of a presentation generation.

        Use this for client billing.

        Args:
            ai_model: The AI model used (e.g., "gpt-4o", "claude-3-5-sonnet")
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            images_generated: Number of images generated
            image_provider: Image generation provider

        Returns:
            PresentationCost with breakdown
        """
        # Normalize model name
        model_key = ai_model.lower().replace("-", "_").replace(".", "")
        for key in TOKEN_COSTS:
            if key.replace("-", "").replace(".", "") in model_key or model_key in key.replace("-", "").replace(".", ""):
                model_key = key
                break
        else:
            model_key = "gpt-4o"  # Default fallback

        token_cost = TOKEN_COSTS.get(model_key, TOKEN_COSTS["gpt-4o"])
        image_cost = IMAGE_COSTS.get(image_provider, IMAGE_COSTS["dalle3"])

        text_cost = (
            (input_tokens / 1000) * token_cost["input"] +
            (output_tokens / 1000) * token_cost["output"]
        )
        total_image_cost = images_generated * image_cost
        total_cost = text_cost + total_image_cost

        return PresentationCost(
            ai_model=ai_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            images_generated=images_generated,
            estimated_cost_usd=round(total_cost, 4),
        )

    def estimate_presentation_cost(
        self,
        num_slides: int,
        include_images: bool = True,
        ai_model: str = "gpt-4o",
        image_provider: str = "dalle3",
    ) -> PresentationCost:
        """
        Estimate cost before generation.

        Rough estimates:
        - ~500 input tokens per slide (prompt + context)
        - ~300 output tokens per slide (content)
        - 1 image per slide if include_images=True

        Args:
            num_slides: Number of slides
            include_images: Whether images will be generated
            ai_model: AI model to use
            image_provider: Image provider

        Returns:
            Estimated PresentationCost
        """
        estimated_input = num_slides * 500
        estimated_output = num_slides * 300
        estimated_images = num_slides if include_images else 0

        return self.calculate_cost(
            ai_model=ai_model,
            input_tokens=estimated_input,
            output_tokens=estimated_output,
            images_generated=estimated_images,
            image_provider=image_provider,
        )

    def _parse_status(self, result: dict) -> TaskStatus:
        """Parse Presenton presentation status."""
        status = result.get("status", "").lower()
        if status in ("completed", "ready", "done"):
            return TaskStatus.COMPLETED
        elif status in ("failed", "error"):
            return TaskStatus.FAILED
        elif status in ("processing", "generating"):
            return TaskStatus.PROCESSING
        return TaskStatus.PENDING

    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse completed presentation with cost data."""
        # Extract usage data if available
        usage = result.get("usage", {})
        cost = None
        if usage:
            cost = self.calculate_cost(
                ai_model=usage.get("model", "gpt-4o"),
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                images_generated=usage.get("images_generated", 0),
                image_provider=usage.get("image_provider", "dalle3"),
            )

        return GenerationResult(
            success=True,
            task_id=result.get("id"),
            status=TaskStatus.COMPLETED,
            output_url=result.get("download_url") or result.get("url"),
            output_data={
                "slides": result.get("slides", []),
                "slide_count": result.get("slide_count") or result.get("num_slides"),
                "cost": cost.to_dict() if cost else None,
            },
            metadata={
                "title": result.get("title"),
                "theme": result.get("theme"),
                "format": result.get("format"),
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
        """Check if Presenton service is accessible."""
        try:
            await self._get("/ppt/themes")
            return True
        except Exception:
            return False
