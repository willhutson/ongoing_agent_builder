"""
External LLM Registry

Maps agents to their external LLM integrations that offset Claude's blindspots.
Each agent can use Claude for reasoning + external LLMs for specialized tasks.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from ..config import get_settings


class ExternalLLMProvider(str, Enum):
    """External LLM providers for specialized capabilities."""
    # Video Generation
    HIGGSFIELD = "higgsfield"  # Multi-model: Sora 2, Veo 3.1, WAN, Kling, Minimax

    # Image Generation
    OPENAI_DALLE = "openai_dalle"  # DALL-E 3
    REPLICATE_FLUX = "replicate_flux"  # Flux models
    STABILITY = "stability"  # Stable Diffusion, SDXL

    # Voice/Audio
    ELEVENLABS = "elevenlabs"  # Voice synthesis
    OPENAI_WHISPER = "openai_whisper"  # Transcription
    OPENAI_TTS = "openai_tts"  # Text-to-speech

    # Vision/Analysis
    OPENAI_VISION = "openai_vision"  # GPT-4V for image analysis

    # Presentations
    BEAUTIFUL_AI = "beautiful_ai"  # Presentation generation
    GAMMA = "gamma"  # Presentation/doc generation

    # Research
    PERPLEXITY = "perplexity"  # Search-augmented research

    # Video Editing
    RUNWAY = "runway"  # Video editing, Gen-2


@dataclass
class ExternalLLMConfig:
    """Configuration for an external LLM provider."""
    provider: ExternalLLMProvider
    name: str
    description: str
    capabilities: list[str]
    api_key_setting: str  # Name of the setting in config
    base_url: Optional[str] = None
    models: Optional[list[str]] = None


# External LLM provider configurations
EXTERNAL_LLM_CONFIGS: dict[ExternalLLMProvider, ExternalLLMConfig] = {
    ExternalLLMProvider.HIGGSFIELD: ExternalLLMConfig(
        provider=ExternalLLMProvider.HIGGSFIELD,
        name="Higgsfield AI",
        description="Multi-model video generation platform",
        capabilities=["text-to-video", "image-to-video", "product-to-video", "sketch-to-video"],
        api_key_setting="higgsfield_api_key",
        base_url="https://api.higgsfield.ai/v1",
        models=["sora2", "veo3", "wan", "kling", "minimax"],
    ),
    ExternalLLMProvider.OPENAI_DALLE: ExternalLLMConfig(
        provider=ExternalLLMProvider.OPENAI_DALLE,
        name="DALL-E 3",
        description="OpenAI image generation",
        capabilities=["text-to-image", "image-editing"],
        api_key_setting="openai_api_key",
        models=["dall-e-3", "dall-e-2"],
    ),
    ExternalLLMProvider.REPLICATE_FLUX: ExternalLLMConfig(
        provider=ExternalLLMProvider.REPLICATE_FLUX,
        name="Flux (Replicate)",
        description="High-quality image generation via Replicate",
        capabilities=["text-to-image", "image-to-image", "inpainting"],
        api_key_setting="replicate_api_key",
        models=["flux-1.1-pro", "flux-schnell", "flux-dev"],
    ),
    ExternalLLMProvider.STABILITY: ExternalLLMConfig(
        provider=ExternalLLMProvider.STABILITY,
        name="Stability AI",
        description="Stable Diffusion models",
        capabilities=["text-to-image", "upscaling", "inpainting", "outpainting"],
        api_key_setting="stability_api_key",
        models=["sd3-large", "sdxl-1.0", "stable-image-ultra"],
    ),
    ExternalLLMProvider.ELEVENLABS: ExternalLLMConfig(
        provider=ExternalLLMProvider.ELEVENLABS,
        name="ElevenLabs",
        description="AI voice synthesis and cloning",
        capabilities=["text-to-speech", "voice-cloning", "voice-design"],
        api_key_setting="elevenlabs_api_key",
        models=["eleven_multilingual_v2", "eleven_turbo_v2"],
    ),
    ExternalLLMProvider.OPENAI_WHISPER: ExternalLLMConfig(
        provider=ExternalLLMProvider.OPENAI_WHISPER,
        name="Whisper",
        description="OpenAI speech-to-text",
        capabilities=["transcription", "translation"],
        api_key_setting="openai_api_key",
        models=["whisper-1"],
    ),
    ExternalLLMProvider.OPENAI_TTS: ExternalLLMConfig(
        provider=ExternalLLMProvider.OPENAI_TTS,
        name="OpenAI TTS",
        description="OpenAI text-to-speech",
        capabilities=["text-to-speech"],
        api_key_setting="openai_api_key",
        models=["tts-1", "tts-1-hd"],
    ),
    ExternalLLMProvider.OPENAI_VISION: ExternalLLMConfig(
        provider=ExternalLLMProvider.OPENAI_VISION,
        name="GPT-4 Vision",
        description="OpenAI image analysis",
        capabilities=["image-analysis", "ocr", "visual-qa"],
        api_key_setting="openai_api_key",
        models=["gpt-4o", "gpt-4-turbo"],
    ),
    ExternalLLMProvider.BEAUTIFUL_AI: ExternalLLMConfig(
        provider=ExternalLLMProvider.BEAUTIFUL_AI,
        name="Beautiful.ai",
        description="AI presentation generation",
        capabilities=["presentation-generation", "slide-design"],
        api_key_setting="beautiful_ai_api_key",
    ),
    ExternalLLMProvider.GAMMA: ExternalLLMConfig(
        provider=ExternalLLMProvider.GAMMA,
        name="Gamma",
        description="AI presentation and document generation",
        capabilities=["presentation-generation", "document-generation"],
        api_key_setting="gamma_api_key",
    ),
    ExternalLLMProvider.PERPLEXITY: ExternalLLMConfig(
        provider=ExternalLLMProvider.PERPLEXITY,
        name="Perplexity",
        description="Search-augmented AI research",
        capabilities=["web-search", "research", "fact-checking"],
        api_key_setting="perplexity_api_key",
        models=["sonar-pro", "sonar"],
    ),
    ExternalLLMProvider.RUNWAY: ExternalLLMConfig(
        provider=ExternalLLMProvider.RUNWAY,
        name="Runway",
        description="AI video editing and generation",
        capabilities=["video-editing", "video-generation", "motion-brush"],
        api_key_setting="runway_api_key",
        models=["gen-3-alpha"],
    ),
}


# Agent to External LLM mapping
# Maps each agent to the external LLMs it can use
AGENT_EXTERNAL_LLMS: dict[str, list[ExternalLLMProvider]] = {
    # Video agents - Higgsfield
    "video_production_agent": [ExternalLLMProvider.HIGGSFIELD, ExternalLLMProvider.RUNWAY],
    "video_storyboard_agent": [ExternalLLMProvider.HIGGSFIELD],
    "video_script_agent": [ExternalLLMProvider.ELEVENLABS],  # For voice preview

    # Image agents - Multiple image providers
    "image_agent": [
        ExternalLLMProvider.OPENAI_DALLE,
        ExternalLLMProvider.REPLICATE_FLUX,
        ExternalLLMProvider.STABILITY,
    ],
    "brand_visual_agent": [
        ExternalLLMProvider.OPENAI_DALLE,
        ExternalLLMProvider.REPLICATE_FLUX,
        ExternalLLMProvider.STABILITY,
    ],

    # Campaign/Marketing - Video ads + images
    "campaign_agent": [
        ExternalLLMProvider.HIGGSFIELD,
        ExternalLLMProvider.OPENAI_DALLE,
    ],
    "media_buying_agent": [ExternalLLMProvider.OPENAI_DALLE],

    # Presentation agents
    "presentation_agent": [
        ExternalLLMProvider.BEAUTIFUL_AI,
        ExternalLLMProvider.GAMMA,
        ExternalLLMProvider.OPENAI_DALLE,
    ],

    # Voice/Audio agents
    "copy_agent": [ExternalLLMProvider.ELEVENLABS, ExternalLLMProvider.OPENAI_TTS],
    "brand_voice_agent": [ExternalLLMProvider.ELEVENLABS],
    "localization_agent": [ExternalLLMProvider.ELEVENLABS, ExternalLLMProvider.OPENAI_WHISPER],
    "accessibility_agent": [ExternalLLMProvider.ELEVENLABS, ExternalLLMProvider.OPENAI_WHISPER],

    # Research/Analysis agents
    "competitor_agent": [ExternalLLMProvider.PERPLEXITY, ExternalLLMProvider.OPENAI_VISION],
    "social_listening_agent": [ExternalLLMProvider.PERPLEXITY],
    "rfp_agent": [ExternalLLMProvider.PERPLEXITY],

    # QA agents - Vision for visual QA
    "qa_agent": [ExternalLLMProvider.OPENAI_VISION],

    # Social agents - Images
    "community_agent": [ExternalLLMProvider.OPENAI_DALLE],
    "social_analytics_agent": [ExternalLLMProvider.OPENAI_VISION],
    "influencer_agent": [ExternalLLMProvider.OPENAI_VISION, ExternalLLMProvider.PERPLEXITY],

    # Content agents
    "content_agent": [ExternalLLMProvider.OPENAI_DALLE, ExternalLLMProvider.PERPLEXITY],

    # Report agents
    "report_agent": [ExternalLLMProvider.GAMMA],
    "ops_reporting_agent": [ExternalLLMProvider.GAMMA],

    # Events
    "events_agent": [ExternalLLMProvider.OPENAI_DALLE, ExternalLLMProvider.BEAUTIFUL_AI],

    # PR
    "pr_agent": [ExternalLLMProvider.PERPLEXITY],
}


def get_external_llms_for_agent(agent_name: str) -> list[ExternalLLMConfig]:
    """Get the external LLM configurations for a specific agent."""
    if not agent_name.endswith("_agent"):
        agent_name = f"{agent_name}_agent"

    providers = AGENT_EXTERNAL_LLMS.get(agent_name, [])
    return [EXTERNAL_LLM_CONFIGS[p] for p in providers]


def get_configured_providers() -> dict[ExternalLLMProvider, bool]:
    """Check which external LLM providers have API keys configured."""
    settings = get_settings()
    result = {}

    for provider, config in EXTERNAL_LLM_CONFIGS.items():
        api_key = getattr(settings, config.api_key_setting, None)
        result[provider] = bool(api_key)

    return result


def get_provider_status() -> list[dict]:
    """Get status of all external LLM providers for dashboard display."""
    configured = get_configured_providers()
    result = []

    for provider, config in EXTERNAL_LLM_CONFIGS.items():
        result.append({
            "id": provider.value,
            "name": config.name,
            "description": config.description,
            "capabilities": config.capabilities,
            "models": config.models or [],
            "configured": configured[provider],
            "api_key_setting": config.api_key_setting,
        })

    return result


def get_agent_llm_summary() -> dict[str, dict]:
    """Get a summary of LLM usage for each agent."""
    configured = get_configured_providers()
    result = {}

    for agent_name, providers in AGENT_EXTERNAL_LLMS.items():
        external_llms = []
        for provider in providers:
            config = EXTERNAL_LLM_CONFIGS[provider]
            external_llms.append({
                "provider": provider.value,
                "name": config.name,
                "configured": configured[provider],
            })

        result[agent_name] = {
            "external_llms": external_llms,
            "has_external": len(providers) > 0,
            "all_configured": all(configured[p] for p in providers) if providers else True,
        }

    return result


def list_unconfigured_for_agent(agent_name: str) -> list[dict]:
    """List external LLMs that an agent needs but aren't configured."""
    if not agent_name.endswith("_agent"):
        agent_name = f"{agent_name}_agent"

    configured = get_configured_providers()
    providers = AGENT_EXTERNAL_LLMS.get(agent_name, [])

    unconfigured = []
    for provider in providers:
        if not configured[provider]:
            config = EXTERNAL_LLM_CONFIGS[provider]
            unconfigured.append({
                "provider": provider.value,
                "name": config.name,
                "api_key_setting": config.api_key_setting,
                "description": config.description,
            })

    return unconfigured
