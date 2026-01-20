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
from .xai import XAIClient, GrokResponse, AuroraImage, grok_chat, grok_image, grok_realtime
from .google import GoogleClient, GeminiResponse, ImagenImage, GoogleTTSAudio, gemini_chat, gemini_classify, imagen_generate, google_tts
from .zhipu import ZhipuClient, GLMResponse, glm_chat, glm_report, glm_analyze, glm_code
from .factory import (
    ExternalLLMFactory,
    get_llm_factory,
    get_video_clients,
    get_image_clients,
    get_voice_clients,
    get_presentation_clients,
    get_research_clients,
)
from .billing import (
    CostBreakdown,
    CostCategory,
    calculate_video_cost,
    calculate_image_cost,
    calculate_voice_cost,
    calculate_vision_cost,
    calculate_research_cost,
    calculate_presentation_cost,
    suggest_client_pricing,
    get_full_pricing_summary,
)
from .credits import (
    # Data classes
    CreditUsage,
    PlanInfo,
    # Config access
    get_config,
    get_tier_config,
    get_plan_config,
    reload_pricing_config,
    update_pricing,
    # Credit conversion
    cost_to_credits,
    credits_to_revenue,
    get_margin,
    # Credit calculations
    calculate_video_credits,
    calculate_image_credits,
    calculate_voice_credits,
    calculate_presentation_credits,
    calculate_research_credits,
    # Reference functions
    get_all_plans,
    get_all_tiers,
    get_credit_estimates,
    estimate_monthly_usage,
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
    "XAIClient",
    "GrokResponse",
    "AuroraImage",
    "grok_chat",
    "grok_image",
    "grok_realtime",
    # Google
    "GoogleClient",
    "GeminiResponse",
    "ImagenImage",
    "GoogleTTSAudio",
    "gemini_chat",
    "gemini_classify",
    "imagen_generate",
    "google_tts",
    # Zhipu/GLM
    "ZhipuClient",
    "GLMResponse",
    "glm_chat",
    "glm_report",
    "glm_analyze",
    "glm_code",
    # Factory
    "ExternalLLMFactory",
    "get_llm_factory",
    "get_video_clients",
    "get_image_clients",
    "get_voice_clients",
    "get_presentation_clients",
    "get_research_clients",
    # Billing
    "CostBreakdown",
    "CostCategory",
    "calculate_video_cost",
    "calculate_image_cost",
    "calculate_voice_cost",
    "calculate_vision_cost",
    "calculate_research_cost",
    "calculate_presentation_cost",
    "suggest_client_pricing",
    "get_full_pricing_summary",
    # Credits - Data classes
    "CreditUsage",
    "PlanInfo",
    # Credits - Config access
    "get_config",
    "get_tier_config",
    "get_plan_config",
    "reload_pricing_config",
    "update_pricing",
    # Credits - Conversion
    "cost_to_credits",
    "credits_to_revenue",
    "get_margin",
    # Credits - Calculations
    "calculate_video_credits",
    "calculate_image_credits",
    "calculate_voice_credits",
    "calculate_presentation_credits",
    "calculate_research_credits",
    # Credits - Reference
    "get_all_plans",
    "get_all_tiers",
    "get_credit_estimates",
    "estimate_monthly_usage",
]
