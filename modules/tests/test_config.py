"""Tests for shared config and model tier system."""

from shared.config import BaseModuleSettings, get_model_id, MODEL_TIERS


def test_default_models(settings):
    assert "claude-opus" in settings.model_premium
    assert "claude-sonnet" in settings.model_standard
    assert "claude-haiku" in settings.model_economy


def test_get_model_id_tiers(settings):
    assert get_model_id(settings, "premium") == settings.model_premium
    assert get_model_id(settings, "standard") == settings.model_standard
    assert get_model_id(settings, "economy") == settings.model_economy


def test_get_model_id_unknown_tier_defaults_to_standard(settings):
    assert get_model_id(settings, "nonexistent") == settings.model_standard


def test_custom_models():
    custom = BaseModuleSettings(
        openrouter_api_key="test",
        model_standard="openai/gpt-4o",
        model_economy="google/gemini-2.0-flash",
    )
    assert get_model_id(custom, "standard") == "openai/gpt-4o"
    assert get_model_id(custom, "economy") == "google/gemini-2.0-flash"


def test_model_tiers_mapping():
    assert set(MODEL_TIERS.keys()) == {"premium", "standard", "economy"}
