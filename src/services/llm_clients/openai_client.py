"""
OpenAI Client

Provides access to:
- DALL-E 3 (image generation)
- GPT-4V (vision/image analysis)
- Whisper (transcription)
- TTS (text-to-speech)
"""

from typing import Optional, Literal, BinaryIO
import base64
from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


ImageSize = Literal["1024x1024", "1792x1024", "1024x1792"]
ImageQuality = Literal["standard", "hd"]
ImageStyle = Literal["vivid", "natural"]
TTSVoice = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
TTSModel = Literal["tts-1", "tts-1-hd"]


class OpenAIClient(BaseExternalLLMClient):
    """Client for OpenAI APIs (DALL-E, Vision, Whisper, TTS)."""

    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
    ):
        super().__init__(api_key, base_url, timeout)

    # ==========================================
    # DALL-E 3 Image Generation
    # ==========================================

    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: ImageSize = "1024x1024",
        quality: ImageQuality = "standard",
        style: ImageStyle = "vivid",
        n: int = 1,
    ) -> GenerationResult:
        """
        Generate image using DALL-E 3.

        Args:
            prompt: Text description of the image
            model: Model to use (dall-e-3 or dall-e-2)
            size: Image dimensions
            quality: Quality level (standard or hd)
            style: Visual style (vivid or natural)
            n: Number of images (DALL-E 3 only supports 1)

        Returns:
            GenerationResult with image URL
        """
        data = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "style": style,
            "n": n,
            "response_format": "url",
        }

        try:
            result = await self._post("/images/generations", data)
            image_data = result.get("data", [{}])[0]

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_url=image_data.get("url"),
                metadata={
                    "revised_prompt": image_data.get("revised_prompt"),
                    "model": model,
                    "size": size,
                },
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def edit_image(
        self,
        image_url: str,
        mask_url: Optional[str],
        prompt: str,
        size: ImageSize = "1024x1024",
        n: int = 1,
    ) -> GenerationResult:
        """
        Edit an image using DALL-E 2 inpainting.

        Args:
            image_url: URL of the original image
            mask_url: URL of the mask (transparent areas will be replaced)
            prompt: Description of the desired edit
            size: Output size
            n: Number of variations

        Returns:
            GenerationResult with edited image URL
        """
        data = {
            "model": "dall-e-2",
            "image": image_url,
            "prompt": prompt,
            "size": size,
            "n": n,
        }
        if mask_url:
            data["mask"] = mask_url

        try:
            result = await self._post("/images/edits", data)
            image_data = result.get("data", [{}])[0]

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_url=image_data.get("url"),
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    # ==========================================
    # GPT-4 Vision (Image Analysis)
    # ==========================================

    async def analyze_image(
        self,
        image_url: str,
        prompt: str = "Describe this image in detail.",
        model: str = "gpt-4o",
        max_tokens: int = 1024,
    ) -> GenerationResult:
        """
        Analyze an image using GPT-4 Vision.

        Args:
            image_url: URL of the image to analyze
            prompt: Question or instruction about the image
            model: Vision model (gpt-4o or gpt-4-turbo)
            max_tokens: Maximum response length

        Returns:
            GenerationResult with analysis text
        """
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
        }

        try:
            result = await self._post("/chat/completions", data)
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=content,
                metadata={
                    "model": model,
                    "usage": result.get("usage"),
                },
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def compare_images(
        self,
        image_urls: list[str],
        prompt: str = "Compare these images and describe the differences.",
        model: str = "gpt-4o",
    ) -> GenerationResult:
        """
        Compare multiple images using GPT-4 Vision.

        Args:
            image_urls: List of image URLs to compare
            prompt: Comparison instruction
            model: Vision model

        Returns:
            GenerationResult with comparison analysis
        """
        content = [{"type": "text", "text": prompt}]
        for url in image_urls:
            content.append({"type": "image_url", "image_url": {"url": url}})

        data = {
            "model": model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": content}],
        }

        try:
            result = await self._post("/chat/completions", data)
            analysis = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=analysis,
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    # ==========================================
    # Whisper (Speech-to-Text)
    # ==========================================

    async def transcribe_audio(
        self,
        audio_url: str,
        language: Optional[str] = None,
        response_format: str = "json",
    ) -> GenerationResult:
        """
        Transcribe audio using Whisper.

        Args:
            audio_url: URL of the audio file
            language: ISO language code (optional, auto-detected)
            response_format: Output format (json, text, srt, vtt)

        Returns:
            GenerationResult with transcription
        """
        # Note: Whisper API requires file upload, not URL
        # This is a simplified version - in production, download and upload
        data = {
            "model": "whisper-1",
            "response_format": response_format,
        }
        if language:
            data["language"] = language

        try:
            # For URL-based audio, we'd need to download first
            # This is a placeholder for the actual implementation
            result = await self._post("/audio/transcriptions", {
                "model": "whisper-1",
                "file": audio_url,  # Would need to be actual file
            })

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result.get("text"),
                metadata={
                    "language": result.get("language"),
                    "duration": result.get("duration"),
                },
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def translate_audio(
        self,
        audio_url: str,
        response_format: str = "json",
    ) -> GenerationResult:
        """
        Translate audio to English using Whisper.

        Args:
            audio_url: URL of the audio file
            response_format: Output format

        Returns:
            GenerationResult with English translation
        """
        try:
            result = await self._post("/audio/translations", {
                "model": "whisper-1",
                "file": audio_url,
                "response_format": response_format,
            })

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result.get("text"),
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    # ==========================================
    # TTS (Text-to-Speech)
    # ==========================================

    async def text_to_speech(
        self,
        text: str,
        voice: TTSVoice = "alloy",
        model: TTSModel = "tts-1",
        speed: float = 1.0,
    ) -> GenerationResult:
        """
        Generate speech from text.

        Args:
            text: Text to convert to speech
            voice: Voice to use
            model: TTS model (tts-1 for speed, tts-1-hd for quality)
            speed: Speech speed (0.25 to 4.0)

        Returns:
            GenerationResult with audio data (base64)
        """
        data = {
            "model": model,
            "input": text,
            "voice": voice,
            "speed": speed,
            "response_format": "mp3",
        }

        try:
            response = await self.client.post("/audio/speech", json=data)
            response.raise_for_status()

            # Audio is returned as binary
            audio_base64 = base64.b64encode(response.content).decode()

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=audio_base64,
                metadata={
                    "format": "mp3",
                    "voice": voice,
                    "model": model,
                },
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    def _parse_status(self, result: dict) -> TaskStatus:
        """OpenAI APIs are synchronous, so always return COMPLETED."""
        return TaskStatus.COMPLETED

    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse OpenAI response."""
        return GenerationResult(
            success=True,
            status=TaskStatus.COMPLETED,
            output_data=result,
        )

    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            await self._get("/models")
            return True
        except Exception:
            return False
