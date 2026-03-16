"""Tests for the module registry (subdomain architecture)."""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.services.module_registry import (
    MODULE_REGISTRY,
    get_module_config,
    get_default_agent,
    get_available_agents,
    is_agent_allowed_for_module,
    resolve_agent_for_module,
    ModuleConfig,
)


# =============================================================================
# MODULE REGISTRY STRUCTURE
# =============================================================================

class TestModuleRegistryStructure:
    """Verify the registry has all expected modules and valid data."""

    EXPECTED_SUBDOMAINS = [
        "studio", "crm", "briefs", "projects", "analytics",
        "lms", "publisher", "time", "finance", "resources",
        "surveys", "marketing", "app",
    ]

    def test_all_subdomains_present(self):
        for subdomain in self.EXPECTED_SUBDOMAINS:
            assert subdomain in MODULE_REGISTRY, f"Missing subdomain: {subdomain}"

    def test_total_module_count(self):
        assert len(MODULE_REGISTRY) == 13

    def test_each_module_has_required_fields(self):
        for subdomain, config in MODULE_REGISTRY.items():
            assert isinstance(config, ModuleConfig)
            assert config.subdomain == subdomain
            assert config.display_name, f"{subdomain} missing display_name"
            assert config.default_agent, f"{subdomain} missing default_agent"
            assert len(config.available_agents) > 0, f"{subdomain} has no available agents"

    def test_default_agent_is_in_available_list(self):
        for subdomain, config in MODULE_REGISTRY.items():
            assert config.default_agent in config.available_agents, (
                f"{subdomain}: default agent '{config.default_agent}' "
                f"not in available agents {config.available_agents}"
            )

    def test_app_module_has_all_agents(self):
        """The 'app' subdomain should have all 46 agent types."""
        app_agents = MODULE_REGISTRY["app"].available_agents
        assert len(app_agents) >= 46, f"app module only has {len(app_agents)} agents"


# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================

class TestModuleLookups:

    def test_get_module_config_valid(self):
        config = get_module_config("studio")
        assert config is not None
        assert config.subdomain == "studio"
        assert config.display_name == "SpokeStudio"

    def test_get_module_config_invalid(self):
        assert get_module_config("nonexistent") is None

    def test_get_default_agent(self):
        assert get_default_agent("studio") == "content"
        assert get_default_agent("crm") == "crm"
        assert get_default_agent("briefs") == "brief"
        assert get_default_agent("finance") == "invoice"

    def test_get_default_agent_invalid(self):
        assert get_default_agent("nonexistent") is None

    def test_get_available_agents_valid(self):
        agents = get_available_agents("studio")
        assert "content" in agents
        assert "copy" in agents
        assert "image" in agents
        assert "presentation" in agents

    def test_get_available_agents_unknown_falls_back_to_app(self):
        agents = get_available_agents("nonexistent")
        # Should return app's full agent list
        assert len(agents) >= 46

    def test_is_agent_allowed(self):
        assert is_agent_allowed_for_module("content", "studio") is True
        assert is_agent_allowed_for_module("copy", "studio") is True

    def test_is_agent_not_allowed(self):
        # invoice shouldn't be in studio
        assert is_agent_allowed_for_module("invoice", "studio") is False

    def test_is_agent_allowed_finance_module(self):
        assert is_agent_allowed_for_module("invoice", "finance") is True
        assert is_agent_allowed_for_module("forecast", "finance") is True
        assert is_agent_allowed_for_module("budget", "finance") is True


# =============================================================================
# AGENT RESOLUTION
# =============================================================================

class TestAgentResolution:

    def test_explicit_agent_no_module(self):
        """When no module, explicit agent_type is returned as-is."""
        result = resolve_agent_for_module("rfp", None)
        assert result == "rfp"

    def test_no_agent_no_module_raises(self):
        """When no module and no agent, should raise."""
        with pytest.raises(ValueError, match="agent_type is required"):
            resolve_agent_for_module(None, None)

    def test_no_agent_with_module_returns_default(self):
        """When module is set but no agent, returns module default."""
        assert resolve_agent_for_module(None, "studio") == "content"
        assert resolve_agent_for_module(None, "crm") == "crm"
        assert resolve_agent_for_module(None, "finance") == "invoice"

    def test_allowed_agent_with_module(self):
        """When agent is allowed for the module, returns it."""
        assert resolve_agent_for_module("copy", "studio") == "copy"

    def test_disallowed_agent_with_module_raises(self):
        """When agent is not allowed for the module, raises ValueError."""
        with pytest.raises(ValueError, match="not available"):
            resolve_agent_for_module("invoice", "studio")

    def test_unknown_module_allows_any_agent(self):
        """Unknown subdomains require explicit agent but allow anything."""
        result = resolve_agent_for_module("legal", "unknown_module")
        assert result == "legal"

    def test_unknown_module_no_agent_raises(self):
        with pytest.raises(ValueError, match="agent_type is required"):
            resolve_agent_for_module(None, "unknown_module")


# =============================================================================
# MODULE-AGENT CROSS-REFERENCES
# =============================================================================

class TestModuleAgentMapping:
    """Verify specific module-agent assignments match the SUBDOMAIN_MODULES.md spec."""

    def test_studio_agents(self):
        agents = get_available_agents("studio")
        expected = ["content", "copy", "image", "presentation",
                    "video_script", "video_storyboard", "video_production",
                    "brand_voice", "brand_visual", "brand_guidelines", "accessibility"]
        for a in expected:
            assert a in agents, f"Studio missing agent: {a}"

    def test_marketing_agents(self):
        agents = get_available_agents("marketing")
        expected = ["campaign", "media_buying", "influencer", "social_listening",
                    "brand_performance", "campaign_analytics", "competitor", "pr", "events"]
        for a in expected:
            assert a in agents, f"Marketing missing agent: {a}"

    def test_finance_agents(self):
        agents = get_available_agents("finance")
        expected = ["invoice", "forecast", "budget", "commercial"]
        for a in expected:
            assert a in agents, f"Finance missing agent: {a}"

    def test_briefs_agents(self):
        agents = get_available_agents("briefs")
        expected = ["brief", "brief_update", "rfp", "scope"]
        for a in expected:
            assert a in agents, f"Briefs missing agent: {a}"
