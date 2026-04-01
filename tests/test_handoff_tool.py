"""Tests for the agent handoff tool."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.spokestack_handoff import (
    HANDOFF_TOOLS, HANDOFF_TOOL_NAMES, VALID_TARGET_AGENTS,
    is_handoff_tool_call, build_handoff_response,
)


def test_handoff_tool_definition_is_valid():
    assert len(HANDOFF_TOOLS) == 1
    tool = HANDOFF_TOOLS[0]
    assert tool["type"] == "function"
    assert tool["function"]["name"] == "delegate_to_agent"
    assert "parameters" in tool["function"]
    assert "target_agent" in tool["function"]["parameters"]["properties"]
    assert "context_summary" in tool["function"]["parameters"]["properties"]
    assert "reason" in tool["function"]["parameters"]["properties"]


def test_required_fields():
    tool = HANDOFF_TOOLS[0]
    required = tool["function"]["parameters"]["required"]
    assert "target_agent" in required
    assert "context_summary" in required
    assert "reason" in required


def test_valid_target_agents():
    assert "core_projects" in VALID_TARGET_AGENTS
    assert "core_briefs" in VALID_TARGET_AGENTS
    assert "core_orders" in VALID_TARGET_AGENTS
    assert "core_tasks" in VALID_TARGET_AGENTS
    assert "core_onboarding" in VALID_TARGET_AGENTS


def test_target_agent_enum_matches_valid_list():
    tool = HANDOFF_TOOLS[0]
    enum_values = tool["function"]["parameters"]["properties"]["target_agent"]["enum"]
    assert set(enum_values) == set(VALID_TARGET_AGENTS)


def test_is_handoff_tool_call():
    assert is_handoff_tool_call("delegate_to_agent") is True
    assert is_handoff_tool_call("read_context") is False
    assert is_handoff_tool_call("create_task") is False
    assert is_handoff_tool_call("") is False


def test_handoff_tool_names_set():
    assert HANDOFF_TOOL_NAMES == {"delegate_to_agent"}


def test_build_handoff_response():
    result = build_handoff_response({
        "target_agent": "core_projects",
        "context_summary": "User wants Q2 planning help",
        "reason": "Project planning detected",
    })
    assert result["type"] == "handoff"
    assert result["target_agent"] == "core_projects"
    assert result["context_summary"] == "User wants Q2 planning help"
    assert result["reason"] == "Project planning detected"


def test_build_handoff_response_with_missing_fields():
    result = build_handoff_response({})
    assert result["type"] == "handoff"
    assert result["target_agent"] == ""
    assert result["context_summary"] == ""
    assert result["reason"] == ""


def test_handoff_tool_in_tier_tool_map():
    """Verify handoff tool is in every tier."""
    from src.tools.core_tool_definitions import TIER_TOOL_MAP
    for tier, tool_groups in TIER_TOOL_MAP.items():
        all_tools = []
        for group in tool_groups:
            all_tools.extend(group)
        tool_names = {t["function"]["name"] for t in all_tools}
        assert "delegate_to_agent" in tool_names, f"delegate_to_agent missing from {tier} tier"


def test_handoff_tool_in_agent_core_tool_map():
    """Verify all core agents have access to the handoff tool."""
    from src.tools.core_tool_definitions import AGENT_CORE_TOOL_MAP
    for agent_type, tool_names in AGENT_CORE_TOOL_MAP.items():
        assert "delegate_to_agent" in tool_names, f"delegate_to_agent missing from {agent_type}"
