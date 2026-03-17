"""
Shared configuration for all modules.

Each module imports this and extends with module-specific settings.
OpenRouter is the single LLM gateway — one key, any model.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class BaseModuleSettings(BaseSettings):
    """Base settings every module inherits."""

    # OpenRouter — the only LLM key you need
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Default models by tier (OpenRouter model IDs)
    model_premium: str = "anthropic/claude-opus-4-20250514"
    model_standard: str = "anthropic/claude-sonnet-4-20250514"
    model_economy: str = "anthropic/claude-haiku-3.5"
    model_creative: str = "moonshotai/kimi-k2.5"
    model_vision: str = "openai/gpt-5-image-mini"

    # Module identity
    module_name: str = "unknown"
    module_port: int = 8000

    # Mission Control registration
    mission_control_url: str = "http://mission-control:8000"

    # Database (optional per module)
    database_url: Optional[str] = None

    # Redis (optional per module)
    redis_url: str = "redis://redis:6379/0"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Model tier mapping
MODEL_TIERS = {
    "premium": "model_premium",
    "standard": "model_standard",
    "economy": "model_economy",
    "creative": "model_creative",
    "vision": "model_vision",
}


def get_model_id(settings: BaseModuleSettings, tier: str = "standard") -> str:
    """Get the OpenRouter model ID for a tier."""
    attr = MODEL_TIERS.get(tier, "model_standard")
    return getattr(settings, attr)
