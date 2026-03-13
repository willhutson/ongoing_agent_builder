"""Shared test fixtures."""

import sys
import os
import pytest

# Ensure modules/ is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.config import BaseModuleSettings
from shared.openrouter import OpenRouterClient


@pytest.fixture
def settings():
    """Settings with a dummy API key (no real calls)."""
    return BaseModuleSettings(
        openrouter_api_key="test-key-not-real",
        module_name="test",
    )


@pytest.fixture
def llm_client():
    """OpenRouter client with dummy key (for instantiation tests only)."""
    return OpenRouterClient(api_key="test-key-not-real")
