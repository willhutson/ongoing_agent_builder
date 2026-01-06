from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Claude
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-4-5-20250514"

    # ERP Connection
    erp_api_base_url: str = ""
    erp_api_key: str = ""

    # Service
    service_port: int = 8000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
