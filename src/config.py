from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from enum import Enum


class ClaudeModelTier(str, Enum):
    """Claude model tiers for different complexity levels."""
    OPUS = "opus"      # Complex reasoning, analysis, strategy
    SONNET = "sonnet"  # Balanced - most tasks
    HAIKU = "haiku"    # Fast, simple operations


# Claude model IDs by tier
CLAUDE_MODELS = {
    ClaudeModelTier.OPUS: "claude-opus-4-5-20250514",
    ClaudeModelTier.SONNET: "claude-sonnet-4-20250514",
    ClaudeModelTier.HAIKU: "claude-haiku-3-5-20241022",
}


class Settings(BaseSettings):
    # Claude (Primary LLM)
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"  # Default to Sonnet for balance

    # Model tier overrides (allows forcing all agents to use a specific tier)
    force_model_tier: Optional[str] = None  # "opus", "sonnet", "haiku", or None

    # ===========================================
    # External LLM Providers (Claude blindspots)
    # ===========================================

    # Higgsfield - Video Generation (Sora 2, Veo 3.1, WAN, Kling, Minimax)
    higgsfield_api_key: Optional[str] = None
    higgsfield_base_url: str = "https://api.higgsfield.ai/v1"

    # OpenAI - DALL-E 3 (images), GPT-4V (vision), Whisper (transcription)
    openai_api_key: Optional[str] = None

    # Replicate - Flux, SDXL, other image models
    replicate_api_key: Optional[str] = None

    # Stability AI - Stable Diffusion, image upscaling
    stability_api_key: Optional[str] = None

    # ElevenLabs - Voice synthesis, voice cloning
    elevenlabs_api_key: Optional[str] = None

    # Runway - Video editing, Gen-2
    runway_api_key: Optional[str] = None

    # Beautiful.ai - Presentation generation
    beautiful_ai_api_key: Optional[str] = None

    # Gamma.app - Presentation/doc generation
    gamma_api_key: Optional[str] = None

    # Perplexity - Research/search augmentation
    perplexity_api_key: Optional[str] = None

    # Google - Gemini chat, Imagen 3 images, Google TTS
    google_api_key: Optional[str] = None

    # xAI - Grok chat, Aurora images, real-time X/Twitter search
    xai_api_key: Optional[str] = None

    # Zhipu - GLM-4.7 chat, long-form reports, code generation
    zhipu_api_key: Optional[str] = None

    # Presenton - Self-hosted presentation generation (uses your AI keys)
    presenton_base_url: str = "http://localhost:8080/api/v1"

    # ===========================================
    # ERP Connection (erp_staging_lmtd integration)
    # ===========================================
    erp_api_base_url: str = ""
    erp_api_key: str = ""
    erp_callback_secret: str = ""  # HMAC secret for callback signature verification

    # Database
    database_url: Optional[str] = None  # Full URL (takes precedence)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "spokestack"
    db_user: str = "spokestack"
    db_password: str = "spokestack"

    # Redis (for production task queue)
    redis_url: str = "redis://localhost:6379/0"

    # Service
    service_port: int = 8000
    log_level: str = "INFO"

    # Multi-tenant settings
    max_skills_per_instance: int = 50
    max_clients_per_instance: int = 100
    default_agent_timeout: int = 300

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
