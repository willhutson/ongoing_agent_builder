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
    UserTier,
    Module,
    MonthlyPlan,
    CreditUsage,
    PLANS,
    cost_to_credits,
    credits_to_revenue,
    calculate_video_credits,
    calculate_image_credits,
    calculate_voice_credits,
    calculate_presentation_credits,
    calculate_research_credits,
    get_credit_estimates,
    get_plan_comparison,
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
    # Credits
    "UserTier",
    "Module",
    "MonthlyPlan",
    "CreditUsage",
    "PLANS",
    "cost_to_credits",
    "credits_to_revenue",
    "calculate_video_credits",
    "calculate_image_credits",
    "calculate_voice_credits",
    "calculate_presentation_credits",
    "calculate_research_credits",
    "get_credit_estimates",
    "get_plan_comparison",
    "estimate_monthly_usage",
]
