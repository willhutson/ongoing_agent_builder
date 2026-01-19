"""
xAI (Grok) Client

Supports:
- Grok-3, Grok-2 for chat/reasoning
- Aurora for image generation
- Real-time X/Twitter data access

API Docs: https://docs.x.ai/
"""

import asyncio
from dataclasses import dataclass
from typing import Optional, Literal
from .base import BaseExternalLLMClient


@dataclass
class GrokResponse:
    """Response from Grok chat."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    finish_reason: str


@dataclass
class AuroraImage:
    """Generated image from Aurora."""
    url: str
    revised_prompt: Optional[str] = None


class XAIClient(BaseExternalLLMClient):
    """
    xAI API client for Grok models and Aurora image generation.

    Models:
        Chat:
        - grok-3: Latest, most capable
        - grok-3-fast: Faster, slightly less capable
        - grok-2: Previous generation
        - grok-2-mini: Smaller, faster

        Image:
        - aurora: High-quality image generation

    Usage:
        client = XAIClient(api_key="xai-...")

        # Chat
        response = await client.chat("Explain quantum computing")

        # Image generation
        images = await client.generate_image("A sunset over mountains")
    """

    BASE_URL = "https://api.x.ai/v1"

    # Model pricing (per 1M tokens)
    PRICING = {
        "grok-3": {"input": 3.00, "output": 15.00},
        "grok-3-fast": {"input": 1.00, "output": 5.00},
        "grok-2": {"input": 2.00, "output": 10.00},
        "grok-2-mini": {"input": 0.50, "output": 2.50},
        "aurora": {"per_image": 0.04},  # Estimated
    }

    CHAT_MODELS = ["grok-3", "grok-3-fast", "grok-2", "grok-2-mini"]
    IMAGE_MODELS = ["aurora"]

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_chat_model: str = "grok-2",
        timeout: int = 120,
    ):
        super().__init__(api_key=api_key, api_key_env="XAI_API_KEY", timeout=timeout)
        self.default_chat_model = default_chat_model

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # =========================================================================
    # CHAT / REASONING
    # =========================================================================

    async def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> GrokResponse:
        """
        Chat with Grok.

        Args:
            prompt: User message
            model: Model to use (default: grok-2)
            system_prompt: Optional system message
            temperature: Creativity (0-2)
            max_tokens: Max response length
            stream: Whether to stream response

        Returns:
            GrokResponse with content and usage stats
        """
        model = model or self.default_chat_model

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        response = await self._post(
            f"{self.BASE_URL}/chat/completions",
            json=payload,
        )

        choice = response["choices"][0]
        usage = response.get("usage", {})

        return GrokResponse(
            content=choice["message"]["content"],
            model=response["model"],
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
        )

    async def chat_with_context(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> GrokResponse:
        """
        Multi-turn chat with message history.

        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Model to use
            temperature: Creativity
            max_tokens: Max response length

        Returns:
            GrokResponse
        """
        model = model or self.default_chat_model

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = await self._post(
            f"{self.BASE_URL}/chat/completions",
            json=payload,
        )

        choice = response["choices"][0]
        usage = response.get("usage", {})

        return GrokResponse(
            content=choice["message"]["content"],
            model=response["model"],
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
        )

    # =========================================================================
    # IMAGE GENERATION (AURORA)
    # =========================================================================

    async def generate_image(
        self,
        prompt: str,
        model: str = "aurora",
        n: int = 1,
        size: Literal["1024x1024", "1536x1024", "1024x1536"] = "1024x1024",
        response_format: Literal["url", "b64_json"] = "url",
    ) -> list[AuroraImage]:
        """
        Generate images with Aurora.

        Args:
            prompt: Image description
            model: Image model (aurora)
            n: Number of images (1-4)
            size: Image dimensions
            response_format: Return URL or base64

        Returns:
            List of AuroraImage objects
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "n": min(n, 4),
            "size": size,
            "response_format": response_format,
        }

        response = await self._post(
            f"{self.BASE_URL}/images/generations",
            json=payload,
        )

        images = []
        for item in response.get("data", []):
            images.append(AuroraImage(
                url=item.get("url") or item.get("b64_json"),
                revised_prompt=item.get("revised_prompt"),
            ))

        return images

    async def generate_image_variations(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        n: int = 1,
        size: Literal["1024x1024", "1536x1024", "1024x1536"] = "1024x1024",
    ) -> list[AuroraImage]:
        """
        Generate variations of an existing image.

        Args:
            image_url: URL of source image
            prompt: Optional guidance for variations
            n: Number of variations
            size: Output dimensions

        Returns:
            List of AuroraImage variations
        """
        payload = {
            "model": "aurora",
            "image": image_url,
            "n": min(n, 4),
            "size": size,
        }
        if prompt:
            payload["prompt"] = prompt

        response = await self._post(
            f"{self.BASE_URL}/images/variations",
            json=payload,
        )

        images = []
        for item in response.get("data", []):
            images.append(AuroraImage(
                url=item.get("url"),
                revised_prompt=item.get("revised_prompt"),
            ))

        return images

    # =========================================================================
    # LIVE SEARCH (X/Twitter Integration)
    # =========================================================================

    async def search_realtime(
        self,
        query: str,
        model: str = "grok-2",
        max_results: int = 10,
    ) -> GrokResponse:
        """
        Search with real-time X/Twitter data.

        Grok has native access to live X data, making it useful
        for current events, trending topics, and social sentiment.

        Args:
            query: Search query
            model: Model to use
            max_results: Max search results to consider

        Returns:
            GrokResponse with synthesized answer
        """
        # Grok's real-time search is implicit - just ask about current events
        system_prompt = (
            "You have access to real-time information from X (Twitter). "
            "Provide current, accurate information based on recent posts and trends. "
            "Cite sources when relevant."
        )

        return await self.chat(
            prompt=query,
            model=model,
            system_prompt=system_prompt,
        )

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
        pricing = self.PRICING.get(model, self.PRICING["grok-2"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def calculate_image_cost(
        self,
        model: str = "aurora",
        num_images: int = 1,
    ) -> float:
        """Calculate cost for image generation."""
        pricing = self.PRICING.get(model, self.PRICING["aurora"])
        return pricing.get("per_image", 0.04) * num_images

    # =========================================================================
    # UTILITY
    # =========================================================================

    async def list_models(self) -> list[dict]:
        """List available models."""
        response = await self._get(f"{self.BASE_URL}/models")
        return response.get("data", [])

    def get_available_models(self) -> dict:
        """Get locally known models and their capabilities."""
        return {
            "chat": {
                "grok-3": {
                    "description": "Most capable, best reasoning",
                    "context": 131072,
                    "pricing": self.PRICING["grok-3"],
                },
                "grok-3-fast": {
                    "description": "Fast responses, good quality",
                    "context": 131072,
                    "pricing": self.PRICING["grok-3-fast"],
                },
                "grok-2": {
                    "description": "Balanced performance",
                    "context": 131072,
                    "pricing": self.PRICING["grok-2"],
                },
                "grok-2-mini": {
                    "description": "Fast and economical",
                    "context": 131072,
                    "pricing": self.PRICING["grok-2-mini"],
                },
            },
            "image": {
                "aurora": {
                    "description": "High-quality image generation",
                    "sizes": ["1024x1024", "1536x1024", "1024x1536"],
                    "strengths": ["photorealism", "text-in-image", "prompt adherence"],
                    "pricing": self.PRICING["aurora"],
                },
            },
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def grok_chat(
    prompt: str,
    model: str = "grok-2",
    api_key: Optional[str] = None,
) -> str:
    """Quick Grok chat."""
    client = XAIClient(api_key=api_key)
    response = await client.chat(prompt, model=model)
    return response.content


async def grok_image(
    prompt: str,
    n: int = 1,
    size: str = "1024x1024",
    api_key: Optional[str] = None,
) -> list[str]:
    """Quick Aurora image generation."""
    client = XAIClient(api_key=api_key)
    images = await client.generate_image(prompt, n=n, size=size)
    return [img.url for img in images]


async def grok_realtime(
    query: str,
    api_key: Optional[str] = None,
) -> str:
    """Quick real-time search via Grok."""
    client = XAIClient(api_key=api_key)
    response = await client.search_realtime(query)
    return response.content
