"""
ElevenLabs Client

Provides access to:
- Text-to-speech
- Voice cloning
- Voice design
- Sound effects
"""

from typing import Optional, Literal
import base64
from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


VoiceModel = Literal["eleven_multilingual_v2", "eleven_turbo_v2", "eleven_monolingual_v1"]


class ElevenLabsClient(BaseExternalLLMClient):
    """Client for ElevenLabs voice synthesis API."""

    DEFAULT_BASE_URL = "https://api.elevenlabs.io/v1"

    # Pre-made voice IDs
    PREMADE_VOICES = {
        "rachel": "21m00Tcm4TlvDq8ikWAM",
        "adam": "pNInz6obpgDQGcFmaJgB",
        "antoni": "ErXwobaYiN019PkySvjV",
        "arnold": "VR6AewLTigWG4xSOukaG",
        "bella": "EXAVITQu4vr4xnSDxMaL",
        "domi": "AZnzlk1XvdvUeBnXmlld",
        "elli": "MF3mGyEYCl7XYWbV9V6O",
        "josh": "TxGEqnHWrfWFTfGW9XjX",
        "sam": "yoZ06aMxZJJ28mfd3POQ",
    }

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
    ):
        super().__init__(api_key, base_url, timeout)

    def _get_headers(self) -> dict:
        """ElevenLabs uses xi-api-key header."""
        return {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    async def text_to_speech(
        self,
        text: str,
        voice_id: str = "rachel",
        model_id: VoiceModel = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
    ) -> GenerationResult:
        """
        Convert text to speech.

        Args:
            text: Text to synthesize
            voice_id: Voice ID or name from PREMADE_VOICES
            model_id: TTS model to use
            stability: Voice stability (0-1)
            similarity_boost: Voice similarity (0-1)
            style: Style exaggeration (0-1)
            use_speaker_boost: Enhance speaker clarity

        Returns:
            GenerationResult with audio data (base64 MP3)
        """
        # Resolve voice name to ID
        resolved_voice_id = self.PREMADE_VOICES.get(voice_id.lower(), voice_id)

        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost,
            },
        }

        try:
            response = await self.client.post(
                f"/text-to-speech/{resolved_voice_id}",
                json=data,
                headers={**self._get_headers(), "Accept": "audio/mpeg"},
            )
            response.raise_for_status()

            audio_base64 = base64.b64encode(response.content).decode()

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=audio_base64,
                metadata={
                    "format": "mp3",
                    "voice_id": resolved_voice_id,
                    "model_id": model_id,
                },
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def text_to_speech_stream(
        self,
        text: str,
        voice_id: str = "rachel",
        model_id: VoiceModel = "eleven_multilingual_v2",
    ) -> GenerationResult:
        """
        Stream text to speech for low-latency playback.

        Args:
            text: Text to synthesize
            voice_id: Voice ID or name
            model_id: TTS model

        Returns:
            GenerationResult with streaming URL
        """
        resolved_voice_id = self.PREMADE_VOICES.get(voice_id.lower(), voice_id)

        data = {
            "text": text,
            "model_id": model_id,
        }

        try:
            result = await self._post(
                f"/text-to-speech/{resolved_voice_id}/stream",
                data,
            )

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_url=result.get("audio_url"),
                metadata={"voice_id": resolved_voice_id},
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def list_voices(self) -> GenerationResult:
        """
        List all available voices.

        Returns:
            GenerationResult with voices list
        """
        try:
            result = await self._get("/voices")

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result.get("voices", []),
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def get_voice(self, voice_id: str) -> GenerationResult:
        """
        Get details about a specific voice.

        Args:
            voice_id: Voice ID

        Returns:
            GenerationResult with voice details
        """
        resolved_voice_id = self.PREMADE_VOICES.get(voice_id.lower(), voice_id)

        try:
            result = await self._get(f"/voices/{resolved_voice_id}")

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

    async def clone_voice(
        self,
        name: str,
        description: str,
        audio_files: list[str],  # Base64 encoded audio samples
        labels: Optional[dict] = None,
    ) -> GenerationResult:
        """
        Clone a voice from audio samples.

        Args:
            name: Name for the cloned voice
            description: Description of the voice
            audio_files: List of base64-encoded audio samples
            labels: Optional labels (e.g., {"accent": "american"})

        Returns:
            GenerationResult with new voice ID
        """
        data = {
            "name": name,
            "description": description,
            "files": audio_files,
        }
        if labels:
            data["labels"] = labels

        try:
            result = await self._post("/voices/add", data)

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=result.get("voice_id"),
                metadata={
                    "name": name,
                    "voice_id": result.get("voice_id"),
                },
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def generate_sound_effect(
        self,
        text: str,
        duration_seconds: Optional[float] = None,
        prompt_influence: float = 0.3,
    ) -> GenerationResult:
        """
        Generate a sound effect from text description.

        Args:
            text: Description of the sound effect
            duration_seconds: Target duration (optional)
            prompt_influence: How much the prompt influences (0-1)

        Returns:
            GenerationResult with audio data
        """
        data = {
            "text": text,
            "prompt_influence": prompt_influence,
        }
        if duration_seconds:
            data["duration_seconds"] = duration_seconds

        try:
            response = await self.client.post(
                "/sound-generation",
                json=data,
                headers={**self._get_headers(), "Accept": "audio/mpeg"},
            )
            response.raise_for_status()

            audio_base64 = base64.b64encode(response.content).decode()

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data=audio_base64,
                metadata={"format": "mp3"},
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def get_user_info(self) -> GenerationResult:
        """Get user subscription and usage info."""
        try:
            result = await self._get("/user")
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

    def _parse_status(self, result: dict) -> TaskStatus:
        """ElevenLabs API is synchronous."""
        return TaskStatus.COMPLETED

    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse ElevenLabs response."""
        return GenerationResult(
            success=True,
            status=TaskStatus.COMPLETED,
            output_data=result,
        )

    async def health_check(self) -> bool:
        """Check if ElevenLabs API is accessible."""
        try:
            await self._get("/user")
            return True
        except Exception:
            return False
