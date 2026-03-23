"""
Per-tenant source configuration for the Observer Agent.

Credentials flow from ERP tenant metadata into context.metadata["source_config"].
When a key is None, the corresponding source adapter returns mock data.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SourceConfig:
    """API credentials and settings for external data sources."""

    # Twitter / X
    twitter_bearer_token: Optional[str] = None

    # Reddit
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "SpokeStack Observer/1.0"

    # Google (Maps reviews, News)
    google_api_key: Optional[str] = None

    # App Store / Google Play
    app_store_app_ids: dict[str, str] = field(default_factory=dict)  # display_name -> app_id

    # Defaults
    default_period: str = "week"
    max_results_per_source: int = 50

    @classmethod
    def from_metadata(cls, metadata: dict) -> "SourceConfig":
        """Build config from agent context metadata."""
        raw = metadata.get("source_config", {})
        if not raw:
            return cls()
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in raw.items() if k in known_fields}
        return cls(**filtered)
