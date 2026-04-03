"""Tests for PR/Communications agents — tool definitions, assignments, registry."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


PR_AGENT_TYPES = [
    "media_relations_manager", "press_release_writer", "crisis_manager",
    "client_reporter", "influencer_manager", "event_planner",
]


class TestPRToolDefinitions:

    def test_all_pr_tools_exist(self):
        from src.tools.spokestack_crud_tools import TOOLS
        pr_tools = [
            # Media relations
            "add_journalist", "search_journalists", "create_media_list",
            "create_pitch", "log_coverage", "get_coverage_report",
            "list_pitches", "create_followup_task",
            # Press releases
            "draft_press_release", "update_press_release", "submit_for_approval",
            "approve_release", "list_press_releases", "schedule_distribution",
            # Crisis
            "activate_crisis", "draft_holding_statement", "map_stakeholder",
            "create_crisis_task", "update_crisis_status", "get_stakeholders",
            # Reporting
            "generate_report", "get_coverage_data", "get_activity_data",
            "get_client_briefs", "save_report_metrics",
            # Influencer
            "add_influencer", "search_influencers", "create_influencer_campaign",
            "create_deliverable", "create_influencer_contract", "list_campaigns",
            # Events
            "create_event", "add_guest", "get_guest_list",
            "create_run_of_show_item", "add_vendor", "update_event_status", "list_events",
        ]
        for tool in pr_tools:
            assert tool in TOOLS, f"Missing PR tool: {tool}"

    def test_fixed_body_merge_tools(self):
        from src.tools.spokestack_crud_tools import TOOLS
        assert TOOLS["add_journalist"]["fixed_body_merge"]["category"] == "journalist"
        assert TOOLS["log_coverage"]["fixed_body_merge"]["category"] == "coverage"
        assert TOOLS["map_stakeholder"]["fixed_body_merge"]["category"] == "crisis_stakeholder"
        assert TOOLS["add_influencer"]["fixed_body_merge"]["category"] == "influencer"
        assert TOOLS["add_guest"]["fixed_body_merge"]["category"] == "event_guest"

    def test_fixed_body_tools(self):
        from src.tools.spokestack_crud_tools import TOOLS
        assert TOOLS["submit_for_approval"]["fixed_body"] == {"status": "IN_REVIEW"}
        assert TOOLS["approve_release"]["fixed_body"] == {"status": "COMPLETED"}

    def test_total_tool_count_increased(self):
        from src.tools.spokestack_crud_tools import TOOLS
        assert len(TOOLS) >= 65  # 33 base + 32+ PR tools


class TestPRAgentAssignment:

    def test_all_pr_agents_have_tools(self):
        from src.tools.agent_tool_assignment import AGENT_TOOLS
        for agent_type in PR_AGENT_TYPES:
            assert agent_type in AGENT_TOOLS, f"Missing agent: {agent_type}"
            assert len(AGENT_TOOLS[agent_type]) >= 5, f"{agent_type} has too few tools"

    def test_media_relations_has_journalist_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("media_relations_manager")
        assert "add_journalist" in tools
        assert "search_journalists" in tools
        assert "create_media_list" in tools
        assert "log_coverage" in tools

    def test_crisis_manager_has_crisis_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("crisis_manager")
        assert "activate_crisis" in tools
        assert "draft_holding_statement" in tools
        assert "map_stakeholder" in tools
        assert "write_context" in tools

    def test_event_planner_has_event_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("event_planner")
        assert "create_event" in tools
        assert "add_guest" in tools
        assert "create_run_of_show_item" in tools
        assert "add_vendor" in tools

    def test_influencer_manager_has_contract_tool(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("influencer_manager")
        assert "create_influencer_contract" in tools

    def test_openai_format_works_for_pr_agents(self):
        from src.tools.agent_tool_assignment import get_openai_tools_for_agent
        for agent_type in PR_AGENT_TYPES:
            tools = get_openai_tools_for_agent(agent_type)
            assert len(tools) >= 5, f"{agent_type} OpenAI tools too few"
            assert all(t["type"] == "function" for t in tools)


class TestPRAgentRegistry:

    def test_pr_agents_in_metadata(self):
        from src.services.agent_registry import AGENT_METADATA
        for agent_type in PR_AGENT_TYPES:
            assert agent_type in AGENT_METADATA, f"Missing metadata: {agent_type}"
            assert AGENT_METADATA[agent_type]["category"] == "pr_comms"

    def test_mc_translation_for_pr_modules(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("module-media-relations-assistant") == "media_relations_manager"
        assert resolve_agent_type("module-press-releases-assistant") == "press_release_writer"
        assert resolve_agent_type("module-crisis-comms-assistant") == "crisis_manager"
        assert resolve_agent_type("module-client-reporting-assistant") == "client_reporter"
        assert resolve_agent_type("module-influencer-mgmt-assistant") == "influencer_manager"
        assert resolve_agent_type("module-events-assistant") == "event_planner"

    def test_canonical_passthrough(self):
        from src.services.agent_registry import resolve_agent_type
        for agent_type in PR_AGENT_TYPES:
            assert resolve_agent_type(agent_type) == agent_type

    def test_registry_response_includes_pr_agents(self):
        from src.services.agent_registry import build_registry_response
        response = build_registry_response()
        types = {a["type"] for a in response["agents"]}
        for agent_type in PR_AGENT_TYPES:
            assert agent_type in types, f"Missing from registry: {agent_type}"

    def test_all_pr_mc_types_in_agent_tools(self):
        from src.services.agent_registry import MC_TO_CANONICAL_MAP
        from src.tools.agent_tool_assignment import AGENT_TOOLS
        pr_mc_types = [
            "module-media-relations-assistant", "module-press-releases-assistant",
            "module-crisis-comms-assistant", "module-client-reporting-assistant",
            "module-influencer-mgmt-assistant", "module-events-assistant",
        ]
        for mc_type in pr_mc_types:
            canonical = MC_TO_CANONICAL_MAP[mc_type]
            assert canonical in AGENT_TOOLS, f"{mc_type}→{canonical} not in AGENT_TOOLS"


class TestPRAgentClasses:

    def test_agent_classes_loadable(self):
        from src.api.core_router import _load_agent_class
        for agent_type in PR_AGENT_TYPES:
            cls = _load_agent_class(agent_type)
            assert cls is not None, f"Failed to load {agent_type}"

    def test_agent_prompts_not_empty(self):
        from src.agents.comms_pr_agents import (
            MediaRelationsAgent, PressReleaseAgent, CrisisManagerAgent,
            ClientReporterAgent, InfluencerManagerAgent, EventPlannerAgent,
        )
        # Each agent's system_prompt should be substantial
        for cls in [MediaRelationsAgent, PressReleaseAgent, CrisisManagerAgent,
                    ClientReporterAgent, InfluencerManagerAgent, EventPlannerAgent]:
            agent = cls.__new__(cls)
            prompt = agent.system_prompt
            assert len(prompt) > 100, f"{cls.__name__} prompt too short"

    def test_media_relations_knows_gulf_outlets(self):
        from src.agents.comms_pr_agents import MediaRelationsAgent
        agent = MediaRelationsAgent.__new__(MediaRelationsAgent)
        prompt = agent.system_prompt
        assert "The National" in prompt
        assert "Gulf News" in prompt
        assert "Sky News Arabia" in prompt

    def test_crisis_manager_has_severity_levels(self):
        from src.agents.comms_pr_agents import CrisisManagerAgent
        agent = CrisisManagerAgent.__new__(CrisisManagerAgent)
        prompt = agent.system_prompt
        assert "LOW" in prompt
        assert "MEDIUM" in prompt
        assert "HIGH" in prompt
        assert "CRITICAL" in prompt

    def test_event_planner_knows_venues(self):
        from src.agents.comms_pr_agents import EventPlannerAgent
        agent = EventPlannerAgent.__new__(EventPlannerAgent)
        prompt = agent.system_prompt
        assert "Madinat Jumeirah" in prompt
        assert "ADNEC" in prompt
        assert "Emirates Palace" in prompt

    def test_influencer_manager_knows_tiers(self):
        from src.agents.comms_pr_agents import InfluencerManagerAgent
        agent = InfluencerManagerAgent.__new__(InfluencerManagerAgent)
        prompt = agent.system_prompt
        assert "Mega" in prompt
        assert "Micro" in prompt
        assert "AED" in prompt


class TestToolExecutorFixedBodyMerge:

    @pytest.mark.asyncio
    async def test_fixed_body_merge(self):
        """fixed_body_merge merges fixed fields with user params."""
        from src.tools.tool_executor import execute_tool
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "ctx_1"}

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await execute_tool("add_journalist", {
                "key": "journalist_sarah",
                "value": {"name": "Sarah Ahmed", "outlet": "The National"},
            }, "org_123")

            # Verify the body has both fixed fields AND user params
            call_kwargs = mock_client.post.call_args
            body = call_kwargs.kwargs["json"]
            assert body["entryType"] == "ENTITY"  # from fixed_body_merge
            assert body["category"] == "journalist"  # from fixed_body_merge
            assert body["key"] == "journalist_sarah"  # from user
            assert body["value"]["name"] == "Sarah Ahmed"  # from user
