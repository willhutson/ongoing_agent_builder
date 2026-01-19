"""
External LLM Client Factory

Provides a unified way to get configured LLM clients for agents.
"""

from typing import Optional
from functools import lru_cache

from ...config import get_settings
from ..external_llm_registry import ExternalLLMProvider, AGENT_EXTERNAL_LLMS

from .higgsfield import HiggsfieldClient
from .openai_client import OpenAIClient
from .replicate import ReplicateClient
from .stability import StabilityClient
from .elevenlabs import ElevenLabsClient
from .runway import RunwayClient
from .beautiful_ai import BeautifulAIClient
from .gamma import GammaClient
from .perplexity import PerplexityClient
from .base import BaseExternalLLMClient


class ExternalLLMFactory:
    """
    Factory for creating external LLM clients.

    Usage:
        factory = ExternalLLMFactory()

        # Get a specific client
        higgsfield = factory.get_higgsfield()

        # Get all clients for an agent
        clients = factory.get_clients_for_agent("video_production_agent")

        # Check if a provider is configured
        if factory.is_configured(ExternalLLMProvider.HIGGSFIELD):
            ...
    """

    def __init__(self):
        self._settings = get_settings()
        self._clients: dict[ExternalLLMProvider, BaseExternalLLMClient] = {}

    def is_configured(self, provider: ExternalLLMProvider) -> bool:
        """Check if a provider has its API key configured."""
        key_map = {
            ExternalLLMProvider.HIGGSFIELD: self._settings.higgsfield_api_key,
            ExternalLLMProvider.OPENAI_DALLE: self._settings.openai_api_key,
            ExternalLLMProvider.OPENAI_VISION: self._settings.openai_api_key,
            ExternalLLMProvider.OPENAI_WHISPER: self._settings.openai_api_key,
            ExternalLLMProvider.OPENAI_TTS: self._settings.openai_api_key,
            ExternalLLMProvider.REPLICATE_FLUX: self._settings.replicate_api_key,
            ExternalLLMProvider.STABILITY: self._settings.stability_api_key,
            ExternalLLMProvider.ELEVENLABS: self._settings.elevenlabs_api_key,
            ExternalLLMProvider.RUNWAY: self._settings.runway_api_key,
            ExternalLLMProvider.BEAUTIFUL_AI: self._settings.beautiful_ai_api_key,
            ExternalLLMProvider.GAMMA: self._settings.gamma_api_key,
            ExternalLLMProvider.PERPLEXITY: self._settings.perplexity_api_key,
        }
        return bool(key_map.get(provider))

    def get_higgsfield(self) -> Optional[HiggsfieldClient]:
        """Get Higgsfield client for video generation."""
        if not self._settings.higgsfield_api_key:
            return None

        if ExternalLLMProvider.HIGGSFIELD not in self._clients:
            self._clients[ExternalLLMProvider.HIGGSFIELD] = HiggsfieldClient(
                api_key=self._settings.higgsfield_api_key,
                base_url=self._settings.higgsfield_base_url,
            )
        return self._clients[ExternalLLMProvider.HIGGSFIELD]

    def get_openai(self) -> Optional[OpenAIClient]:
        """Get OpenAI client for DALL-E, Vision, Whisper, TTS."""
        if not self._settings.openai_api_key:
            return None

        if ExternalLLMProvider.OPENAI_DALLE not in self._clients:
            self._clients[ExternalLLMProvider.OPENAI_DALLE] = OpenAIClient(
                api_key=self._settings.openai_api_key,
            )
        return self._clients[ExternalLLMProvider.OPENAI_DALLE]

    def get_replicate(self) -> Optional[ReplicateClient]:
        """Get Replicate client for Flux image generation."""
        if not self._settings.replicate_api_key:
            return None

        if ExternalLLMProvider.REPLICATE_FLUX not in self._clients:
            self._clients[ExternalLLMProvider.REPLICATE_FLUX] = ReplicateClient(
                api_key=self._settings.replicate_api_key,
            )
        return self._clients[ExternalLLMProvider.REPLICATE_FLUX]

    def get_stability(self) -> Optional[StabilityClient]:
        """Get Stability AI client for Stable Diffusion."""
        if not self._settings.stability_api_key:
            return None

        if ExternalLLMProvider.STABILITY not in self._clients:
            self._clients[ExternalLLMProvider.STABILITY] = StabilityClient(
                api_key=self._settings.stability_api_key,
            )
        return self._clients[ExternalLLMProvider.STABILITY]

    def get_elevenlabs(self) -> Optional[ElevenLabsClient]:
        """Get ElevenLabs client for voice synthesis."""
        if not self._settings.elevenlabs_api_key:
            return None

        if ExternalLLMProvider.ELEVENLABS not in self._clients:
            self._clients[ExternalLLMProvider.ELEVENLABS] = ElevenLabsClient(
                api_key=self._settings.elevenlabs_api_key,
            )
        return self._clients[ExternalLLMProvider.ELEVENLABS]

    def get_runway(self) -> Optional[RunwayClient]:
        """Get Runway client for video generation/editing."""
        if not self._settings.runway_api_key:
            return None

        if ExternalLLMProvider.RUNWAY not in self._clients:
            self._clients[ExternalLLMProvider.RUNWAY] = RunwayClient(
                api_key=self._settings.runway_api_key,
            )
        return self._clients[ExternalLLMProvider.RUNWAY]

    def get_beautiful_ai(self) -> Optional[BeautifulAIClient]:
        """Get Beautiful.ai client for presentations."""
        if not self._settings.beautiful_ai_api_key:
            return None

        if ExternalLLMProvider.BEAUTIFUL_AI not in self._clients:
            self._clients[ExternalLLMProvider.BEAUTIFUL_AI] = BeautifulAIClient(
                api_key=self._settings.beautiful_ai_api_key,
            )
        return self._clients[ExternalLLMProvider.BEAUTIFUL_AI]

    def get_gamma(self) -> Optional[GammaClient]:
        """Get Gamma client for presentations/documents."""
        if not self._settings.gamma_api_key:
            return None

        if ExternalLLMProvider.GAMMA not in self._clients:
            self._clients[ExternalLLMProvider.GAMMA] = GammaClient(
                api_key=self._settings.gamma_api_key,
            )
        return self._clients[ExternalLLMProvider.GAMMA]

    def get_perplexity(self) -> Optional[PerplexityClient]:
        """Get Perplexity client for research."""
        if not self._settings.perplexity_api_key:
            return None

        if ExternalLLMProvider.PERPLEXITY not in self._clients:
            self._clients[ExternalLLMProvider.PERPLEXITY] = PerplexityClient(
                api_key=self._settings.perplexity_api_key,
            )
        return self._clients[ExternalLLMProvider.PERPLEXITY]

    def get_client(self, provider: ExternalLLMProvider) -> Optional[BaseExternalLLMClient]:
        """Get a client by provider enum."""
        provider_map = {
            ExternalLLMProvider.HIGGSFIELD: self.get_higgsfield,
            ExternalLLMProvider.OPENAI_DALLE: self.get_openai,
            ExternalLLMProvider.OPENAI_VISION: self.get_openai,
            ExternalLLMProvider.OPENAI_WHISPER: self.get_openai,
            ExternalLLMProvider.OPENAI_TTS: self.get_openai,
            ExternalLLMProvider.REPLICATE_FLUX: self.get_replicate,
            ExternalLLMProvider.STABILITY: self.get_stability,
            ExternalLLMProvider.ELEVENLABS: self.get_elevenlabs,
            ExternalLLMProvider.RUNWAY: self.get_runway,
            ExternalLLMProvider.BEAUTIFUL_AI: self.get_beautiful_ai,
            ExternalLLMProvider.GAMMA: self.get_gamma,
            ExternalLLMProvider.PERPLEXITY: self.get_perplexity,
        }
        getter = provider_map.get(provider)
        return getter() if getter else None

    def get_clients_for_agent(self, agent_name: str) -> dict[ExternalLLMProvider, BaseExternalLLMClient]:
        """
        Get all configured external LLM clients for a specific agent.

        Args:
            agent_name: Name of the agent (e.g., "video_production_agent")

        Returns:
            Dict mapping provider to client (only configured providers)
        """
        if not agent_name.endswith("_agent"):
            agent_name = f"{agent_name}_agent"

        providers = AGENT_EXTERNAL_LLMS.get(agent_name, [])
        clients = {}

        for provider in providers:
            client = self.get_client(provider)
            if client:
                clients[provider] = client

        return clients

    def get_missing_for_agent(self, agent_name: str) -> list[ExternalLLMProvider]:
        """
        Get list of providers that an agent needs but aren't configured.

        Args:
            agent_name: Name of the agent

        Returns:
            List of unconfigured providers
        """
        if not agent_name.endswith("_agent"):
            agent_name = f"{agent_name}_agent"

        providers = AGENT_EXTERNAL_LLMS.get(agent_name, [])
        return [p for p in providers if not self.is_configured(p)]

    async def close_all(self):
        """Close all client connections."""
        for client in self._clients.values():
            await client.close()
        self._clients.clear()

    async def health_check_all(self) -> dict[ExternalLLMProvider, bool]:
        """Check health of all configured providers."""
        results = {}
        for provider in ExternalLLMProvider:
            if self.is_configured(provider):
                client = self.get_client(provider)
                if client:
                    results[provider] = await client.health_check()
        return results


# Singleton factory instance
_factory: Optional[ExternalLLMFactory] = None


def get_llm_factory() -> ExternalLLMFactory:
    """Get or create the singleton factory instance."""
    global _factory
    if _factory is None:
        _factory = ExternalLLMFactory()
    return _factory


# Convenience functions for common operations
def get_video_clients() -> dict[str, BaseExternalLLMClient]:
    """Get all configured video generation clients."""
    factory = get_llm_factory()
    clients = {}
    if factory.is_configured(ExternalLLMProvider.HIGGSFIELD):
        clients["higgsfield"] = factory.get_higgsfield()
    if factory.is_configured(ExternalLLMProvider.RUNWAY):
        clients["runway"] = factory.get_runway()
    return clients


def get_image_clients() -> dict[str, BaseExternalLLMClient]:
    """Get all configured image generation clients."""
    factory = get_llm_factory()
    clients = {}
    if factory.is_configured(ExternalLLMProvider.OPENAI_DALLE):
        clients["dalle"] = factory.get_openai()
    if factory.is_configured(ExternalLLMProvider.REPLICATE_FLUX):
        clients["flux"] = factory.get_replicate()
    if factory.is_configured(ExternalLLMProvider.STABILITY):
        clients["stability"] = factory.get_stability()
    return clients


def get_voice_clients() -> dict[str, BaseExternalLLMClient]:
    """Get all configured voice/audio clients."""
    factory = get_llm_factory()
    clients = {}
    if factory.is_configured(ExternalLLMProvider.ELEVENLABS):
        clients["elevenlabs"] = factory.get_elevenlabs()
    if factory.is_configured(ExternalLLMProvider.OPENAI_TTS):
        clients["openai_tts"] = factory.get_openai()
    if factory.is_configured(ExternalLLMProvider.OPENAI_WHISPER):
        clients["whisper"] = factory.get_openai()
    return clients


def get_presentation_clients() -> dict[str, BaseExternalLLMClient]:
    """Get all configured presentation clients."""
    factory = get_llm_factory()
    clients = {}
    if factory.is_configured(ExternalLLMProvider.BEAUTIFUL_AI):
        clients["beautiful_ai"] = factory.get_beautiful_ai()
    if factory.is_configured(ExternalLLMProvider.GAMMA):
        clients["gamma"] = factory.get_gamma()
    return clients


def get_research_clients() -> dict[str, BaseExternalLLMClient]:
    """Get all configured research clients."""
    factory = get_llm_factory()
    clients = {}
    if factory.is_configured(ExternalLLMProvider.PERPLEXITY):
        clients["perplexity"] = factory.get_perplexity()
    return clients
