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
    RUNWAY = "runway"  # Video editing, Gen-3

    # Image Generation
    OPENAI_DALLE = "openai_dalle"  # DALL-E 3
    REPLICATE_FLUX = "replicate_flux"  # Flux models
    STABILITY = "stability"  # Stable Diffusion, SDXL
    XAI_AURORA = "xai_aurora"  # Grok Aurora images
    GOOGLE_IMAGEN = "google_imagen"  # Imagen 3

    # Voice/Audio
    ELEVENLABS = "elevenlabs"  # Voice synthesis (premium)
    OPENAI_WHISPER = "openai_whisper"  # Transcription
    OPENAI_TTS = "openai_tts"  # Text-to-speech
    GOOGLE_TTS = "google_tts"  # Budget TTS (75x cheaper than ElevenLabs)

    # Vision/Analysis
    OPENAI_VISION = "openai_vision"  # GPT-4V for image analysis
    GOOGLE_GEMINI_VISION = "google_gemini_vision"  # Gemini 1.5 Pro (2M context, 4x cheaper)

    # Chat/Reasoning (for routing/classification)
    GOOGLE_GEMINI = "google_gemini"  # Gemini Flash (50x cheaper than GPT-4o)
    XAI_GROK = "xai_grok"  # Grok with real-time X/Twitter data

    # Presentations
    BEAUTIFUL_AI = "beautiful_ai"  # Premium presentation generation
    GAMMA = "gamma"  # Client-facing presentations
    PRESENTON = "presenton"  # Self-hosted (90%+ margin for internal reports)

    # Research
    PERPLEXITY = "perplexity"  # Search-augmented research

    # Code/Reports/Math (Zhipu GLM)
    ZHIPU_GLM = "zhipu_glm"  # GLM-4.7: 200K context, 128K output, strong math/code


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
    ExternalLLMProvider.XAI_AURORA: ExternalLLMConfig(
        provider=ExternalLLMProvider.XAI_AURORA,
        name="Aurora (xAI)",
        description="Grok image generation - strong at text-in-image",
        capabilities=["text-to-image", "photorealism"],
        api_key_setting="xai_api_key",
        models=["aurora"],
    ),
    ExternalLLMProvider.XAI_GROK: ExternalLLMConfig(
        provider=ExternalLLMProvider.XAI_GROK,
        name="Grok (xAI)",
        description="Real-time X/Twitter data access for social intelligence",
        capabilities=["real-time-social", "trending-topics", "sentiment-analysis"],
        api_key_setting="xai_api_key",
        models=["grok-2", "grok-3"],
    ),
    ExternalLLMProvider.GOOGLE_IMAGEN: ExternalLLMConfig(
        provider=ExternalLLMProvider.GOOGLE_IMAGEN,
        name="Imagen 3 (Google)",
        description="High-quality image generation at 50% DALL-E cost",
        capabilities=["text-to-image"],
        api_key_setting="google_api_key",
        models=["imagen-3.0-generate-001"],
    ),
    ExternalLLMProvider.GOOGLE_TTS: ExternalLLMConfig(
        provider=ExternalLLMProvider.GOOGLE_TTS,
        name="Google Cloud TTS",
        description="Budget TTS - 75x cheaper than ElevenLabs",
        capabilities=["text-to-speech"],
        api_key_setting="google_api_key",
        models=["tts-standard", "tts-wavenet", "tts-neural2"],
    ),
    ExternalLLMProvider.GOOGLE_GEMINI: ExternalLLMConfig(
        provider=ExternalLLMProvider.GOOGLE_GEMINI,
        name="Gemini Flash (Google)",
        description="Ultra-cheap routing/classification - 50x cheaper than GPT-4o",
        capabilities=["classification", "routing", "intent-detection"],
        api_key_setting="google_api_key",
        models=["gemini-2.0-flash-exp", "gemini-1.5-flash-8b"],
    ),
    ExternalLLMProvider.GOOGLE_GEMINI_VISION: ExternalLLMConfig(
        provider=ExternalLLMProvider.GOOGLE_GEMINI_VISION,
        name="Gemini Vision (Google)",
        description="Dashboard/screenshot analysis with 2M context - 4x cheaper than GPT-4V",
        capabilities=["image-analysis", "dashboard-analysis", "visual-qa"],
        api_key_setting="google_api_key",
        models=["gemini-1.5-pro"],
    ),
    ExternalLLMProvider.PRESENTON: ExternalLLMConfig(
        provider=ExternalLLMProvider.PRESENTON,
        name="Presenton",
        description="Self-hosted presentations - 90%+ margin for internal reports",
        capabilities=["presentation-generation"],
        api_key_setting="presenton_base_url",  # URL-based, no API key
    ),
    ExternalLLMProvider.ZHIPU_GLM: ExternalLLMConfig(
        provider=ExternalLLMProvider.ZHIPU_GLM,
        name="GLM-4.7 (Zhipu)",
        description="200K context, 128K output - ideal for code, reports, math. 5x cheaper than Sonnet.",
        capabilities=["code-generation", "long-reports", "math-reasoning", "financial-analysis"],
        api_key_setting="zhipu_api_key",
        models=["glm-4.7", "glm-4.7-thinking", "glm-4.5", "glm-4.5-flash"],
    ),
}


# Agent to External LLM mapping
# Maps each agent to the external LLMs it can use
#
# Model tier recommendations:
#   - High-stakes (legal, finance, clients, knowledge): Use Claude Opus 4.5
#   - Standard reasoning: Use Claude Sonnet 4
#   - Routing/classification: Use Google Gemini Flash (50x cheaper)
#   - Real-time social: Use Grok (native X/Twitter data)
#
AGENT_EXTERNAL_LLMS: dict[str, list[ExternalLLMProvider]] = {
    # ==========================================================================
    # VIDEO MODULE
    # ==========================================================================
    "video_production_agent": [ExternalLLMProvider.HIGGSFIELD, ExternalLLMProvider.RUNWAY],
    "video_storyboard_agent": [ExternalLLMProvider.HIGGSFIELD],
    "video_script_agent": [ExternalLLMProvider.ELEVENLABS, ExternalLLMProvider.GOOGLE_TTS],

    # ==========================================================================
    # STUDIO MODULE (Images, Presentations)
    # ==========================================================================
    "image_agent": [
        ExternalLLMProvider.OPENAI_DALLE,  # Premium quality
        ExternalLLMProvider.REPLICATE_FLUX,  # Flux-schnell for drafts ($0.003)
        ExternalLLMProvider.STABILITY,
        ExternalLLMProvider.XAI_AURORA,  # Good at text-in-image
        ExternalLLMProvider.GOOGLE_IMAGEN,  # 50% cheaper than DALL-E
    ],
    "brand_visual_agent": [
        ExternalLLMProvider.OPENAI_DALLE,
        ExternalLLMProvider.REPLICATE_FLUX,
        ExternalLLMProvider.STABILITY,
        ExternalLLMProvider.GOOGLE_IMAGEN,
    ],
    "presentation_agent": [
        ExternalLLMProvider.PRESENTON,  # Self-hosted, 90%+ margin
        ExternalLLMProvider.GAMMA,  # Client-facing
        ExternalLLMProvider.BEAUTIFUL_AI,  # Premium
        ExternalLLMProvider.OPENAI_DALLE,
    ],

    # ==========================================================================
    # VOICE MODULE
    # ==========================================================================
    "copy_agent": [
        ExternalLLMProvider.GOOGLE_TTS,  # Draft voice previews (75x cheaper)
        ExternalLLMProvider.ELEVENLABS,  # Final quality
        ExternalLLMProvider.OPENAI_TTS,
    ],
    "brand_voice_agent": [ExternalLLMProvider.ELEVENLABS],  # Premium voice cloning
    "localization_agent": [
        ExternalLLMProvider.GOOGLE_TTS,  # Budget voiceover
        ExternalLLMProvider.ELEVENLABS,  # Premium
        ExternalLLMProvider.OPENAI_WHISPER,
    ],
    "accessibility_agent": [
        ExternalLLMProvider.GOOGLE_TTS,
        ExternalLLMProvider.ELEVENLABS,
        ExternalLLMProvider.OPENAI_WHISPER,
    ],

    # ==========================================================================
    # RESEARCH MODULE (+ Grok for real-time social)
    # ==========================================================================
    "social_listening_agent": [
        ExternalLLMProvider.XAI_GROK,  # Real-time X/Twitter data
        ExternalLLMProvider.PERPLEXITY,
    ],
    "competitor_agent": [
        ExternalLLMProvider.XAI_GROK,  # Social competitor monitoring
        ExternalLLMProvider.PERPLEXITY,
        ExternalLLMProvider.GOOGLE_GEMINI_VISION,  # Dashboard analysis
    ],
    "pr_agent": [
        ExternalLLMProvider.XAI_GROK,  # Breaking news detection
        ExternalLLMProvider.PERPLEXITY,
    ],
    "rfp_agent": [ExternalLLMProvider.PERPLEXITY],
    "influencer_agent": [
        ExternalLLMProvider.PERPLEXITY,
        ExternalLLMProvider.GOOGLE_GEMINI_VISION,  # Profile analysis
        ExternalLLMProvider.XAI_GROK,  # Social reach
    ],

    # ==========================================================================
    # ANALYTICS MODULE (Gemini Vision - 4x cheaper, 2M context)
    # ==========================================================================
    "social_analytics_agent": [ExternalLLMProvider.GOOGLE_GEMINI_VISION],
    "campaign_analytics_agent": [ExternalLLMProvider.GOOGLE_GEMINI_VISION],
    "brand_performance_agent": [ExternalLLMProvider.GOOGLE_GEMINI_VISION],
    "qa_agent": [
        ExternalLLMProvider.GOOGLE_GEMINI_VISION,  # Bulk screenshot analysis
        ExternalLLMProvider.OPENAI_VISION,  # Fallback
    ],

    # ==========================================================================
    # DISTRIBUTION MODULE
    # ==========================================================================
    "report_agent": [
        ExternalLLMProvider.GAMMA,  # Client-facing presentations
        ExternalLLMProvider.ZHIPU_GLM,  # Long-form report generation (128K output)
    ],
    "ops_reporting_agent": [
        ExternalLLMProvider.PRESENTON,  # Internal reports (90%+ margin)
        ExternalLLMProvider.ZHIPU_GLM,  # Long-form report generation
    ],
    "community_agent": [
        ExternalLLMProvider.OPENAI_DALLE,
        ExternalLLMProvider.GOOGLE_IMAGEN,
    ],

    # ==========================================================================
    # CAMPAIGN MODULE
    # ==========================================================================
    "campaign_agent": [
        ExternalLLMProvider.HIGGSFIELD,
        ExternalLLMProvider.OPENAI_DALLE,
        ExternalLLMProvider.GOOGLE_IMAGEN,
    ],
    "media_buying_agent": [
        ExternalLLMProvider.OPENAI_DALLE,
        ExternalLLMProvider.GOOGLE_IMAGEN,
    ],
    "events_agent": [
        ExternalLLMProvider.OPENAI_DALLE,
        ExternalLLMProvider.BEAUTIFUL_AI,
    ],

    # ==========================================================================
    # CONTENT MODULE
    # ==========================================================================
    "content_agent": [
        ExternalLLMProvider.OPENAI_DALLE,
        ExternalLLMProvider.GOOGLE_IMAGEN,
        ExternalLLMProvider.PERPLEXITY,
    ],

    # ==========================================================================
    # HIGH-STAKES AGENTS (Use Claude Opus 4.5 - no external LLMs needed)
    # These agents require maximum reasoning accuracy, not external tools.
    # Configure via model_tier in agent config, not here.
    # ==========================================================================
    # "legal_agent": [],  # Opus 4.5 - contract accuracy, compliance
    # "invoice_agent": [],  # Opus 4.5 - financial precision
    # "budget_agent": [],  # Opus 4.5 - financial planning
    # "forecast_agent": [],  # Opus 4.5 - projections
    # "crm_agent": [],  # Opus 4.5 - client relationships
    # "onboarding_agent": [],  # Opus 4.5 - client setup
    # "scope_agent": [],  # Opus 4.5 - scope accuracy
    # "knowledge_agent": [],  # Opus 4.5 - institutional knowledge
    # "training_agent": [],  # Opus 4.5 - training accuracy
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
