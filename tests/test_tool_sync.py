"""Tests for Phase 15 tool sync — registry endpoint enhancement."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.agent_registry import build_registry_response


class TestToolRegistryInResponse:

    def test_response_has_tool_registry(self):
        response = build_registry_response()
        assert "toolRegistry" in response
        assert isinstance(response["toolRegistry"], dict)

    def test_tool_registry_has_all_tools(self):
        from src.tools.spokestack_crud_tools import TOOLS
        response = build_registry_response()
        registry = response["toolRegistry"]
        for tool_name in TOOLS:
            assert tool_name in registry, f"Missing tool: {tool_name}"

    def test_tool_registry_count(self):
        from src.tools.spokestack_crud_tools import TOOLS
        response = build_registry_response()
        assert len(response["toolRegistry"]) == len(TOOLS)

    def test_tool_entry_has_name(self):
        response = build_registry_response()
        for name, entry in response["toolRegistry"].items():
            assert entry["name"] == name

    def test_http_tool_has_method_and_path(self):
        response = build_registry_response()
        for name, entry in response["toolRegistry"].items():
            if entry.get("handler") == "local":
                continue
            assert "method" in entry, f"{name} missing method"
            assert "path" in entry, f"{name} missing path"

    def test_fixed_body_merge_serialized_as_camel_case(self):
        response = build_registry_response()
        # add_journalist has fixed_body_merge
        journalist_tool = response["toolRegistry"].get("add_journalist")
        assert journalist_tool is not None
        assert "fixedBodyMerge" in journalist_tool
        assert journalist_tool["fixedBodyMerge"]["category"] == "journalist"

    def test_fixed_body_serialized_as_camel_case(self):
        response = build_registry_response()
        # approve_brief has fixed_body
        approve_tool = response["toolRegistry"].get("approve_brief")
        assert approve_tool is not None
        assert "fixedBody" in approve_tool
        assert approve_tool["fixedBody"]["status"] == "COMPLETED"


class TestAgentToolsInResponse:

    def test_response_has_agent_tools(self):
        response = build_registry_response()
        assert "agentTools" in response
        assert isinstance(response["agentTools"], dict)

    def test_agent_tools_has_all_agents(self):
        from src.tools.agent_tool_assignment import AGENT_TOOLS
        response = build_registry_response()
        for agent_type in AGENT_TOOLS:
            assert agent_type in response["agentTools"], f"Missing agent: {agent_type}"

    def test_agent_tools_count(self):
        from src.tools.agent_tool_assignment import AGENT_TOOLS
        response = build_registry_response()
        assert len(response["agentTools"]) == len(AGENT_TOOLS)

    def test_agent_tools_are_lists(self):
        response = build_registry_response()
        for agent_type, tools in response["agentTools"].items():
            assert isinstance(tools, list), f"{agent_type} tools not a list"
            assert len(tools) > 0, f"{agent_type} has no tools"

    def test_agent_tool_names_exist_in_registry(self):
        """Every tool name referenced by an agent must exist in toolRegistry."""
        response = build_registry_response()
        registry = response["toolRegistry"]
        for agent_type, tools in response["agentTools"].items():
            for tool_name in tools:
                assert tool_name in registry, (
                    f"Agent '{agent_type}' references tool '{tool_name}' "
                    f"which is not in toolRegistry"
                )


class TestBackwardsCompat:

    def test_existing_fields_still_present(self):
        response = build_registry_response()
        assert "agents" in response
        assert "total" in response
        assert "mcTranslationMap" in response

    def test_agents_still_have_tools_field(self):
        response = build_registry_response()
        for agent in response["agents"]:
            assert "tools" in agent
