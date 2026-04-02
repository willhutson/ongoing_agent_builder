"""Tests for Phase 10B: canonical agent registry + MC translation."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.services.agent_registry import (
    MC_TO_CANONICAL_MAP, AGENT_METADATA, resolve_agent_type,
    build_registry_response, get_default_model,
)
from src.api.routes import AgentType


class TestMCTranslationMap:
    """Verify MC type → canonical type translation."""

    def test_mc_general_resolves(self):
        assert resolve_agent_type("mc-general") == "workflow"

    def test_mc_expert_resolves(self):
        assert resolve_agent_type("mc-expert") == "knowledge"

    def test_mc_planner_resolves(self):
        assert resolve_agent_type("mc-planner") == "brief"

    def test_mc_analyst_resolves(self):
        assert resolve_agent_type("mc-analyst") == "campaign_analytics"

    def test_mc_strategist_resolves(self):
        assert resolve_agent_type("mc-strategist") == "content"

    def test_mc_reviewer_resolves(self):
        assert resolve_agent_type("mc-reviewer") == "qa"

    def test_mc_communicator_resolves(self):
        assert resolve_agent_type("mc-communicator") == "copy"

    def test_module_crm_assistant_resolves(self):
        assert resolve_agent_type("module-crm-assistant") == "crm"

    def test_module_briefs_assistant_resolves(self):
        assert resolve_agent_type("module-briefs-assistant") == "brief"

    def test_module_tasks_assistant_resolves(self):
        assert resolve_agent_type("module-tasks-assistant") == "core_tasks"

    def test_module_projects_assistant_resolves(self):
        assert resolve_agent_type("module-projects-assistant") == "core_projects"

    def test_module_orders_assistant_resolves(self):
        assert resolve_agent_type("module-orders-assistant") == "core_orders"

    def test_module_finance_assistant_resolves(self):
        assert resolve_agent_type("module-finance-assistant") == "invoice"

    def test_module_social_publishing_resolves(self):
        assert resolve_agent_type("module-social-publishing-assistant") == "campaign"

    def test_onboarding_types_resolve(self):
        assert resolve_agent_type("onboarding-publisher-setup") == "onboarding"
        assert resolve_agent_type("onboarding-reply-setup") == "onboarding"
        assert resolve_agent_type("onboarding-channel-setup") == "onboarding"
        assert resolve_agent_type("onboarding-vertical-config") == "onboarding"

    def test_canonical_type_passes_through(self):
        """Canonical types (not in map) pass through unchanged."""
        assert resolve_agent_type("brief") == "brief"
        assert resolve_agent_type("crm") == "crm"
        assert resolve_agent_type("copy") == "copy"

    def test_unknown_type_passes_through(self):
        """Unknown types pass through unchanged (fails gracefully later)."""
        assert resolve_agent_type("some-new-type") == "some-new-type"

    def test_legacy_mc_names_included(self):
        """Legacy names from MC_TO_AGENT_BUILDER_MAP are in the canonical map."""
        assert resolve_agent_type("assistant") == "workflow"
        assert resolve_agent_type("brief_writer") == "brief"
        assert resolve_agent_type("deck_designer") == "presentation"
        assert resolve_agent_type("contract_analyzer") == "legal"

    def test_all_mc_types_resolve_to_valid_agent(self):
        """Every MC type in the map resolves to either an AgentType or a core agent."""
        valid_types = {t.value for t in AgentType} | {"core_tasks", "core_projects", "core_orders", "core_briefs", "core_onboarding"}
        for mc_type, canonical in MC_TO_CANONICAL_MAP.items():
            assert canonical in valid_types, (
                f"MC type '{mc_type}' resolves to '{canonical}' which is not a valid agent type"
            )


class TestRegistryResponse:
    """Verify the /api/v1/agents/registry response shape."""

    def test_response_has_agents(self):
        response = build_registry_response()
        assert "agents" in response
        assert isinstance(response["agents"], list)
        assert len(response["agents"]) > 0

    def test_response_has_total(self):
        response = build_registry_response()
        assert response["total"] == len(response["agents"])

    def test_response_has_mc_translation_map(self):
        response = build_registry_response()
        assert "mcTranslationMap" in response
        assert isinstance(response["mcTranslationMap"], dict)
        assert "mc-general" in response["mcTranslationMap"]
        assert "module-crm-assistant" in response["mcTranslationMap"]

    def test_agent_entry_has_required_fields(self):
        response = build_registry_response()
        for agent in response["agents"]:
            assert "type" in agent, f"Agent missing 'type': {agent}"
            assert "name" in agent, f"Agent missing 'name': {agent}"
            assert "description" in agent, f"Agent missing 'description': {agent}"
            assert "category" in agent, f"Agent missing 'category': {agent}"
            assert "defaultModel" in agent, f"Agent missing 'defaultModel': {agent}"

    def test_includes_all_agent_types(self):
        response = build_registry_response()
        types_in_response = {a["type"] for a in response["agents"]}
        # All AgentType enum values should be present
        for agent_type in AgentType:
            assert agent_type.value in types_in_response, (
                f"AgentType '{agent_type.value}' missing from registry"
            )

    def test_includes_core_agents(self):
        response = build_registry_response()
        types_in_response = {a["type"] for a in response["agents"]}
        for core_type in ["core_onboarding", "core_tasks", "core_projects", "core_briefs", "core_orders"]:
            assert core_type in types_in_response, f"Core agent '{core_type}' missing"

    def test_default_model_is_valid(self):
        response = build_registry_response()
        for agent in response["agents"]:
            model = agent["defaultModel"]
            assert model.startswith("claude-") or model.startswith("deepseek/"), (
                f"Agent '{agent['type']}' has unexpected model: {model}"
            )


class TestAgentMetadata:
    """Verify all agent types have metadata."""

    def test_all_agent_types_have_metadata(self):
        for agent_type in AgentType:
            assert agent_type.value in AGENT_METADATA, (
                f"AgentType '{agent_type.value}' missing from AGENT_METADATA"
            )

    def test_core_agents_have_metadata(self):
        for core_type in ["core_onboarding", "core_tasks", "core_projects", "core_briefs", "core_orders"]:
            assert core_type in AGENT_METADATA, f"Core agent '{core_type}' missing metadata"


class TestAuthAlignment:
    """Verify auth middleware checks X-Agent-Secret."""

    def test_auth_middleware_checks_agent_secret(self):
        with open("src/api/auth.py") as f:
            content = f.read()
        assert "X-Agent-Secret" in content
        assert "AGENT_RUNTIME_SECRET" in content
