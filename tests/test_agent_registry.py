"""Tests for canonical agent registry + MC translation (updated Phase 10B)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.services.agent_registry import (
    MC_TO_CANONICAL_MAP, AGENT_METADATA, resolve_agent_type,
    build_registry_response,
)
from src.tools.agent_tool_assignment import AGENT_TOOLS


class TestMCTranslationMap:
    """Verify MC type → canonical type translation."""

    def test_mc_general_resolves(self):
        assert resolve_agent_type("mc-general") == "assistant"

    def test_mc_planner_resolves(self):
        assert resolve_agent_type("mc-planner") == "project_manager"

    def test_mc_analyst_resolves(self):
        assert resolve_agent_type("mc-analyst") == "analyst"

    def test_mc_reviewer_resolves(self):
        assert resolve_agent_type("mc-reviewer") == "brief_writer"

    def test_mc_strategist_resolves(self):
        assert resolve_agent_type("mc-strategist") == "content_creator"

    def test_mc_communicator_resolves(self):
        assert resolve_agent_type("mc-communicator") == "assistant"

    def test_module_crm_assistant_resolves(self):
        assert resolve_agent_type("module-crm-assistant") == "crm_manager"

    def test_module_briefs_assistant_resolves(self):
        assert resolve_agent_type("module-briefs-assistant") == "brief_writer"

    def test_module_tasks_assistant_resolves(self):
        assert resolve_agent_type("module-tasks-assistant") == "assistant"

    def test_module_projects_assistant_resolves(self):
        assert resolve_agent_type("module-projects-assistant") == "project_manager"

    def test_module_orders_assistant_resolves(self):
        assert resolve_agent_type("module-orders-assistant") == "order_manager"

    def test_module_finance_assistant_resolves(self):
        assert resolve_agent_type("module-finance-assistant") == "order_manager"

    def test_module_social_publishing_resolves(self):
        assert resolve_agent_type("module-social-publishing-assistant") == "assistant"

    def test_onboarding_resolves(self):
        assert resolve_agent_type("onboarding") == "core_onboarding"
        assert resolve_agent_type("onboarding-publisher-setup") == "core_onboarding"

    def test_canonical_type_passes_through(self):
        assert resolve_agent_type("assistant") == "assistant"
        assert resolve_agent_type("brief_writer") == "brief_writer"
        assert resolve_agent_type("project_manager") == "project_manager"

    def test_unknown_type_passes_through(self):
        assert resolve_agent_type("some-new-type") == "some-new-type"

    def test_legacy_mc_names_included(self):
        assert resolve_agent_type("brief_writer") == "brief_writer"
        assert resolve_agent_type("analyst") == "analyst"
        assert resolve_agent_type("resource_planner") == "project_manager"

    def test_all_mc_types_resolve_to_agent_tool_key(self):
        """Every MC type maps to a key in AGENT_TOOLS."""
        for mc_type, canonical in MC_TO_CANONICAL_MAP.items():
            assert canonical in AGENT_TOOLS, (
                f"MC type '{mc_type}' → '{canonical}' but '{canonical}' not in AGENT_TOOLS"
            )


class TestRegistryResponse:

    def test_response_has_agents(self):
        response = build_registry_response()
        assert "agents" in response
        assert len(response["agents"]) > 0

    def test_response_has_total(self):
        response = build_registry_response()
        assert response["total"] == len(response["agents"])

    def test_response_has_mc_translation_map(self):
        response = build_registry_response()
        assert "mcTranslationMap" in response
        assert "mc-general" in response["mcTranslationMap"]

    def test_agent_entry_has_tools(self):
        response = build_registry_response()
        for agent in response["agents"]:
            assert "tools" in agent, f"Agent {agent['type']} missing tools"

    def test_includes_canonical_types(self):
        response = build_registry_response()
        types = {a["type"] for a in response["agents"]}
        for expected in ["assistant", "brief_writer", "project_manager", "order_manager", "crm_manager", "analyst"]:
            assert expected in types, f"Missing canonical type: {expected}"


class TestAuthAlignment:

    def test_auth_middleware_checks_agent_secret(self):
        with open("src/api/auth.py") as f:
            content = f.read()
        assert "X-Agent-Secret" in content
        assert "AGENT_RUNTIME_SECRET" in content
