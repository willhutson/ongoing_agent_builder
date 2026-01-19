"""
External LLM API Clients

Provides unified interfaces to external LLM providers for capabilities
that offset Claude's blindspots (video, image, voice, etc.)
"""

from .base import BaseExternalLLMClient, GenerationResult, TaskStatus
from .higgsfield import HiggsfieldClient
from .openai_client import OpenAIClient
from .replicate import ReplicateClient
from .stability import StabilityClient
from .elevenlabs import ElevenLabsClient
from .runway import RunwayClient
from .beautiful_ai import BeautifulAIClient
from .gamma import GammaClient
from .perplexity import PerplexityClient
from .presenton import PresentonClient
from .factory import (
    ExternalLLMFactory,
    get_llm_factory,
    get_video_clients,
    get_image_clients,
    get_voice_clients,
    get_presentation_clients,
    get_research_clients,
)

__all__ = [
    # Base
    "BaseExternalLLMClient",
    "GenerationResult",
    "TaskStatus",
    # Clients
    "HiggsfieldClient",
    "OpenAIClient",
    "ReplicateClient",
    "StabilityClient",
    "ElevenLabsClient",
    "RunwayClient",
    "BeautifulAIClient",
    "GammaClient",
    "PerplexityClient",
    "PresentonClient",
    # Factory
    "ExternalLLMFactory",
    "get_llm_factory",
    "get_video_clients",
    "get_image_clients",
    "get_voice_clients",
    "get_presentation_clients",
    "get_research_clients",
]
