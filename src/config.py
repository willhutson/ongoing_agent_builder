from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Claude
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-4-5-20250514"

    # ERP Connection
    erp_api_base_url: str = ""
    erp_api_key: str = ""

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
