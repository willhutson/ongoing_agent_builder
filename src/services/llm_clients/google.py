"""
Google AI Client

Supports:
- Gemini 2.0 Flash, 1.5 Pro, 1.5 Flash (chat/multimodal)
- Imagen 3 (image generation)
- Google Cloud TTS (text-to-speech)

API Docs: https://ai.google.dev/
"""

import asyncio
import base64
from dataclasses import dataclass
from typing import Optional, Literal, Union
from .base import BaseExternalLLMClient


@dataclass
class GeminiResponse:
    """Response from Gemini chat."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    finish_reason: str


@dataclass
class ImagenImage:
    """Generated image from Imagen."""
    base64_data: str
    mime_type: str = "image/png"

    @property
    def data_url(self) -> str:
        return f"data:{self.mime_type};base64,{self.base64_data}"


@dataclass
class GoogleTTSAudio:
    """Generated audio from Google TTS."""
    audio_content: bytes
    mime_type: str = "audio/mp3"


class GoogleClient(BaseExternalLLMClient):
    """
    Google AI client for Gemini, Imagen, and TTS.

    Models:
        Chat (Gemini):
        - gemini-2.0-flash-exp: Fastest, cheapest, great for routing
        - gemini-1.5-pro: Best quality, longer context
        - gemini-1.5-flash: Balanced speed/quality

        Image (Imagen):
        - imagen-3.0-generate-001: Latest image generation

        Voice (TTS):
        - Multiple voices and languages via Google Cloud TTS

    Usage:
        client = GoogleClient(api_key="...")

        # Chat (super cheap for routing/classification)
        response = await client.chat("Classify this intent: ...")

        # Image generation
        images = await client.generate_image("A mountain landscape")

        # Text-to-speech
        audio = await client.text_to_speech("Hello world")
    """

    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    TTS_BASE_URL = "https://texttospeech.googleapis.com/v1"

    # Pricing per 1M tokens (input/output)
    PRICING = {
        # Gemini models - VERY cheap
        "gemini-2.0-flash-exp": {"input": 0.10, "output": 0.40},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-1.5-flash-8b": {"input": 0.0375, "output": 0.15},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        # Imagen
        "imagen-3.0-generate-001": {"per_image": 0.02},
        # TTS (per 1M characters)
        "tts-standard": {"per_1m_chars": 4.00},
        "tts-wavenet": {"per_1m_chars": 16.00},
        "tts-neural2": {"per_1m_chars": 16.00},
    }

    CHAT_MODELS = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_chat_model: str = "gemini-2.0-flash-exp",
        timeout: int = 120,
    ):
        super().__init__(api_key=api_key, api_key_env="GOOGLE_API_KEY", timeout=timeout)
        self.default_chat_model = default_chat_model

    def _get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
        }

    # =========================================================================
    # GEMINI CHAT
    # =========================================================================

    async def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        images: Optional[list[str]] = None,
    ) -> GeminiResponse:
        """
        Chat with Gemini.

        Args:
            prompt: User message
            model: Model to use (default: gemini-2.0-flash-exp)
            system_prompt: Optional system instruction
            temperature: Creativity (0-2)
            max_tokens: Max response length
            images: Optional list of image URLs or base64 for vision

        Returns:
            GeminiResponse with content and usage stats
        """
        model = model or self.default_chat_model

        # Build content parts
        parts = []
        if images:
            for img in images:
                if img.startswith("data:"):
                    # Base64 data URL
                    mime_type, b64_data = img.split(";base64,")
                    mime_type = mime_type.replace("data:", "")
                    parts.append({
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": b64_data,
                        }
                    })
                else:
                    # URL - fetch and convert
                    parts.append({
                        "file_data": {
                            "file_uri": img,
                        }
                    })

        parts.append({"text": prompt})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        url = f"{self.GEMINI_BASE_URL}/models/{model}:generateContent?key={self.api_key}"

        response = await self._post(url, json=payload)

        # Parse response
        candidate = response.get("candidates", [{}])[0]
        content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
        usage = response.get("usageMetadata", {})

        return GeminiResponse(
            content=content,
            model=model,
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            finish_reason=candidate.get("finishReason", "STOP"),
        )

    async def chat_with_context(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> GeminiResponse:
        """
        Multi-turn chat with message history.

        Args:
            messages: List of {"role": "user/model", "content": "..."}
            model: Model to use
            system_prompt: Optional system instruction
            temperature: Creativity
            max_tokens: Max response length

        Returns:
            GeminiResponse
        """
        model = model or self.default_chat_model

        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}],
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        url = f"{self.GEMINI_BASE_URL}/models/{model}:generateContent?key={self.api_key}"

        response = await self._post(url, json=payload)

        candidate = response.get("candidates", [{}])[0]
        content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
        usage = response.get("usageMetadata", {})

        return GeminiResponse(
            content=content,
            model=model,
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            finish_reason=candidate.get("finishReason", "STOP"),
        )

    # =========================================================================
    # IMAGEN (Image Generation)
    # =========================================================================

    async def generate_image(
        self,
        prompt: str,
        model: str = "imagen-3.0-generate-001",
        n: int = 1,
        aspect_ratio: Literal["1:1", "3:4", "4:3", "9:16", "16:9"] = "1:1",
        negative_prompt: Optional[str] = None,
        safety_filter_level: Literal["block_none", "block_few", "block_some", "block_most"] = "block_some",
    ) -> list[ImagenImage]:
        """
        Generate images with Imagen 3.

        Args:
            prompt: Image description
            model: Imagen model version
            n: Number of images (1-4)
            aspect_ratio: Output aspect ratio
            negative_prompt: What to avoid in the image
            safety_filter_level: Content filtering level

        Returns:
            List of ImagenImage objects with base64 data
        """
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": min(n, 4),
                "aspectRatio": aspect_ratio,
                "safetyFilterLevel": safety_filter_level,
            },
        }

        if negative_prompt:
            payload["parameters"]["negativePrompt"] = negative_prompt

        url = f"{self.GEMINI_BASE_URL}/models/{model}:predict?key={self.api_key}"

        response = await self._post(url, json=payload)

        images = []
        for prediction in response.get("predictions", []):
            if "bytesBase64Encoded" in prediction:
                images.append(ImagenImage(
                    base64_data=prediction["bytesBase64Encoded"],
                    mime_type=prediction.get("mimeType", "image/png"),
                ))

        return images

    # =========================================================================
    # GOOGLE CLOUD TTS
    # =========================================================================

    async def text_to_speech(
        self,
        text: str,
        voice: str = "en-US-Neural2-J",
        language_code: str = "en-US",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        audio_encoding: Literal["MP3", "LINEAR16", "OGG_OPUS"] = "MP3",
    ) -> GoogleTTSAudio:
        """
        Convert text to speech with Google Cloud TTS.

        Args:
            text: Text to synthesize
            voice: Voice name (e.g., en-US-Neural2-J)
            language_code: Language code
            speaking_rate: Speed (0.25 to 4.0)
            pitch: Pitch adjustment (-20 to 20 semitones)
            audio_encoding: Output format

        Returns:
            GoogleTTSAudio with audio bytes

        Voice types:
            - Standard: Basic quality (~$4/1M chars)
            - WaveNet: High quality (~$16/1M chars)
            - Neural2: Best quality (~$16/1M chars)
        """
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": language_code,
                "name": voice,
            },
            "audioConfig": {
                "audioEncoding": audio_encoding,
                "speakingRate": speaking_rate,
                "pitch": pitch,
            },
        }

        url = f"{self.TTS_BASE_URL}/text:synthesize?key={self.api_key}"

        response = await self._post(url, json=payload)

        audio_content = base64.b64decode(response.get("audioContent", ""))

        mime_map = {
            "MP3": "audio/mp3",
            "LINEAR16": "audio/wav",
            "OGG_OPUS": "audio/ogg",
        }

        return GoogleTTSAudio(
            audio_content=audio_content,
            mime_type=mime_map.get(audio_encoding, "audio/mp3"),
        )

    async def list_voices(
        self,
        language_code: Optional[str] = None,
    ) -> list[dict]:
        """List available TTS voices."""
        url = f"{self.TTS_BASE_URL}/voices?key={self.api_key}"
        if language_code:
            url += f"&languageCode={language_code}"

        response = await self._get(url)
        return response.get("voices", [])

    # =========================================================================
    # COST CALCULATION
    # =========================================================================

    def calculate_chat_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate cost for a chat completion."""
        pricing = self.PRICING.get(model, self.PRICING["gemini-2.0-flash-exp"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def calculate_image_cost(
        self,
        model: str = "imagen-3.0-generate-001",
        num_images: int = 1,
    ) -> float:
        """Calculate cost for image generation."""
        pricing = self.PRICING.get(model, self.PRICING["imagen-3.0-generate-001"])
        return pricing.get("per_image", 0.02) * num_images

    def calculate_tts_cost(
        self,
        text: str,
        voice_type: Literal["standard", "wavenet", "neural2"] = "neural2",
    ) -> float:
        """Calculate cost for TTS."""
        char_count = len(text)
        pricing = self.PRICING.get(f"tts-{voice_type}", self.PRICING["tts-neural2"])
        return (char_count / 1_000_000) * pricing["per_1m_chars"]

    # =========================================================================
    # UTILITY
    # =========================================================================

    def get_available_models(self) -> dict:
        """Get locally known models and their capabilities."""
        return {
            "chat": {
                "gemini-2.0-flash-exp": {
                    "description": "Fastest, cheapest - ideal for routing",
                    "context": 1_000_000,
                    "pricing": self.PRICING["gemini-2.0-flash-exp"],
                    "multimodal": True,
                },
                "gemini-1.5-flash": {
                    "description": "Fast with good quality",
                    "context": 1_000_000,
                    "pricing": self.PRICING["gemini-1.5-flash"],
                    "multimodal": True,
                },
                "gemini-1.5-flash-8b": {
                    "description": "Smallest, fastest, cheapest",
                    "context": 1_000_000,
                    "pricing": self.PRICING["gemini-1.5-flash-8b"],
                    "multimodal": True,
                },
                "gemini-1.5-pro": {
                    "description": "Best quality, complex reasoning",
                    "context": 2_000_000,
                    "pricing": self.PRICING["gemini-1.5-pro"],
                    "multimodal": True,
                },
            },
            "image": {
                "imagen-3.0-generate-001": {
                    "description": "High-quality image generation",
                    "aspect_ratios": ["1:1", "3:4", "4:3", "9:16", "16:9"],
                    "pricing": self.PRICING["imagen-3.0-generate-001"],
                },
            },
            "tts": {
                "standard": {
                    "description": "Basic quality voices",
                    "pricing": self.PRICING["tts-standard"],
                },
                "wavenet": {
                    "description": "High quality WaveNet voices",
                    "pricing": self.PRICING["tts-wavenet"],
                },
                "neural2": {
                    "description": "Best quality Neural2 voices",
                    "pricing": self.PRICING["tts-neural2"],
                },
            },
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def gemini_chat(
    prompt: str,
    model: str = "gemini-2.0-flash-exp",
    api_key: Optional[str] = None,
) -> str:
    """Quick Gemini chat - super cheap for routing/classification."""
    client = GoogleClient(api_key=api_key)
    response = await client.chat(prompt, model=model)
    return response.content


async def gemini_classify(
    text: str,
    categories: list[str],
    api_key: Optional[str] = None,
) -> str:
    """
    Quick classification using Gemini Flash.

    Extremely cost-effective for intent detection, routing, etc.
    """
    client = GoogleClient(api_key=api_key)
    prompt = f"""Classify the following text into exactly one of these categories: {', '.join(categories)}

Text: {text}

Respond with only the category name, nothing else."""

    response = await client.chat(prompt, model="gemini-2.0-flash-exp", temperature=0)
    return response.content.strip()


async def imagen_generate(
    prompt: str,
    n: int = 1,
    aspect_ratio: str = "1:1",
    api_key: Optional[str] = None,
) -> list[str]:
    """Quick Imagen image generation. Returns base64 data URLs."""
    client = GoogleClient(api_key=api_key)
    images = await client.generate_image(prompt, n=n, aspect_ratio=aspect_ratio)
    return [img.data_url for img in images]


async def google_tts(
    text: str,
    voice: str = "en-US-Neural2-J",
    api_key: Optional[str] = None,
) -> bytes:
    """Quick Google TTS. Returns audio bytes."""
    client = GoogleClient(api_key=api_key)
    audio = await client.text_to_speech(text, voice=voice)
    return audio.audio_content
