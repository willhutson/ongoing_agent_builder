"""Tests for 9 marketplace module agents."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

MARKETPLACE_AGENTS = [
    "board_manager", "workflow_designer", "social_listener", "nps_analyst",
    "chat_operator", "portal_manager", "delegation_coordinator",
    "access_admin", "module_builder",
]

MC_TRANSLATIONS = [
    ("module-boards-assistant", "board_manager"),
    ("module-workflows-assistant", "workflow_designer"),
    ("module-listening-assistant", "social_listener"),
    ("module-nps-assistant", "nps_analyst"),
    ("module-spokechat-assistant", "chat_operator"),
    ("module-client-portal-assistant", "portal_manager"),
    ("module-delegation-assistant", "delegation_coordinator"),
    ("module-access-control-assistant", "access_admin"),
    ("module-builder-assistant", "module_builder"),
]


class TestMCTranslation:

    @pytest.mark.parametrize("mc_type,expected", MC_TRANSLATIONS)
    def test_mc_to_canonical(self, mc_type, expected):
        from src.services.agent_registry import MC_TO_CANONICAL_MAP
        assert MC_TO_CANONICAL_MAP[mc_type] == expected


class TestAgentInstantiation:

    def test_board_manager(self):
        from src.agents.marketplace_agents import BoardManagerAgent
        agent = BoardManagerAgent.__new__(BoardManagerAgent)
        assert agent.name == "board_manager_agent"

    def test_workflow_designer(self):
        from src.agents.marketplace_agents import WorkflowDesignerAgent
        agent = WorkflowDesignerAgent.__new__(WorkflowDesignerAgent)
        assert agent.name == "workflow_designer_agent"

    def test_social_listener(self):
        from src.agents.marketplace_agents import SocialListenerAgent
        agent = SocialListenerAgent.__new__(SocialListenerAgent)
        assert agent.name == "social_listener_agent"

    def test_nps_analyst(self):
        from src.agents.marketplace_agents import NpsAnalystAgent
        agent = NpsAnalystAgent.__new__(NpsAnalystAgent)
        assert agent.name == "nps_analyst_agent"

    def test_chat_operator(self):
        from src.agents.marketplace_agents import ChatOperatorAgent
        agent = ChatOperatorAgent.__new__(ChatOperatorAgent)
        assert agent.name == "chat_operator_agent"

    def test_portal_manager(self):
        from src.agents.marketplace_agents import PortalManagerAgent
        agent = PortalManagerAgent.__new__(PortalManagerAgent)
        assert agent.name == "portal_manager_agent"

    def test_delegation_coordinator(self):
        from src.agents.marketplace_agents import DelegationCoordinatorAgent
        agent = DelegationCoordinatorAgent.__new__(DelegationCoordinatorAgent)
        assert agent.name == "delegation_coordinator_agent"

    def test_access_admin(self):
        from src.agents.marketplace_agents import AccessAdminAgent
        agent = AccessAdminAgent.__new__(AccessAdminAgent)
        assert agent.name == "access_admin_agent"

    def test_module_builder(self):
        from src.agents.marketplace_agents import ModuleBuilderAgent
        agent = ModuleBuilderAgent.__new__(ModuleBuilderAgent)
        assert agent.name == "module_builder_agent"


class TestAgentPrompts:

    @pytest.mark.parametrize("agent_type", MARKETPLACE_AGENTS)
    def test_prompt_not_empty(self, agent_type):
        from src.api.core_router import _load_agent_class
        cls = _load_agent_class(agent_type)
        agent = cls.__new__(cls)
        assert len(agent.system_prompt) > 100, f"{agent_type} prompt too short"


class TestAgentClassLoading:

    @pytest.mark.parametrize("agent_type", MARKETPLACE_AGENTS)
    def test_loadable(self, agent_type):
        from src.api.core_router import _load_agent_class
        cls = _load_agent_class(agent_type)
        assert cls is not None


class TestAgentToolsAssignment:

    def test_all_marketplace_agents_in_agent_tools(self):
        from src.tools.agent_tool_assignment import AGENT_TOOLS
        for agent_type in MARKETPLACE_AGENTS:
            assert agent_type in AGENT_TOOLS, f"{agent_type} missing from AGENT_TOOLS"
            assert len(AGENT_TOOLS[agent_type]) >= 5, f"{agent_type} has too few tools"

    def test_board_manager_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("board_manager")
        assert "create_board" in tools
        assert "add_card" in tools
        assert "move_card" in tools
        assert "list_boards" in tools

    def test_workflow_designer_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("workflow_designer")
        assert "create_workflow_def" in tools
        assert "list_workflows" in tools
        assert "create_trigger" in tools

    def test_social_listener_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("social_listener")
        assert "log_mention" in tools
        assert "search_mentions" in tools
        assert "create_alert" in tools

    def test_nps_analyst_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("nps_analyst")
        assert "create_survey" in tools
        assert "log_response" in tools
        assert "calculate_nps" in tools

    def test_chat_operator_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("chat_operator")
        assert "create_canned_response" in tools
        assert "create_routing_rule" in tools
        assert "create_escalation" in tools

    def test_portal_manager_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("portal_manager")
        assert "create_deliverable_entry" in tools
        assert "list_deliverables" in tools
        assert "update_approval_status" in tools

    def test_delegation_coordinator_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("delegation_coordinator")
        assert "delegate_task" in tools
        assert "reassign_task" in tools
        assert "check_workload" in tools

    def test_access_admin_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("access_admin")
        assert "create_role" in tools
        assert "assign_permission" in tools
        assert "audit_access" in tools

    def test_module_builder_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("module_builder")
        assert "create_module_manifest" in tools
        assert "scaffold_agent_config" in tools

    @pytest.mark.parametrize("agent_type", MARKETPLACE_AGENTS)
    def test_openai_format(self, agent_type):
        from src.tools.agent_tool_assignment import get_openai_tools_for_agent
        tools = get_openai_tools_for_agent(agent_type)
        assert len(tools) >= 5
        assert all(t["type"] == "function" for t in tools)


class TestAgentMetadata:

    def test_all_marketplace_agents_have_metadata(self):
        from src.services.agent_registry import AGENT_METADATA
        for agent_type in MARKETPLACE_AGENTS:
            assert agent_type in AGENT_METADATA, f"Missing metadata: {agent_type}"

    def test_registry_includes_marketplace_agents(self):
        from src.services.agent_registry import build_registry_response
        response = build_registry_response()
        types = {a["type"] for a in response["agents"]}
        for agent_type in MARKETPLACE_AGENTS:
            assert agent_type in types, f"Missing from registry: {agent_type}"

    def test_all_mc_types_resolve_to_agent_tools(self):
        from src.services.agent_registry import MC_TO_CANONICAL_MAP
        from src.tools.agent_tool_assignment import AGENT_TOOLS
        for mc_type, canonical in MC_TRANSLATIONS:
            assert canonical in AGENT_TOOLS, f"{mc_type}→{canonical} not in AGENT_TOOLS"


class TestToolDefinitions:

    def test_total_tool_count(self):
        from src.tools.spokestack_crud_tools import TOOLS
        assert len(TOOLS) >= 100, f"Expected 100+ tools, got {len(TOOLS)}"

    def test_marketplace_tools_exist(self):
        from src.tools.spokestack_crud_tools import TOOLS
        marketplace_tools = [
            "create_board", "add_card", "move_card", "list_boards",
            "create_workflow_def", "list_workflows", "create_trigger",
            "log_mention", "search_mentions", "create_alert",
            "create_survey", "log_response", "calculate_nps",
            "create_canned_response", "create_routing_rule",
            "create_deliverable_entry", "list_deliverables",
            "delegate_task", "reassign_task", "check_workload",
            "create_role", "assign_permission", "audit_access",
            "create_module_manifest", "scaffold_agent_config",
        ]
        for tool in marketplace_tools:
            assert tool in TOOLS, f"Missing tool: {tool}"

    def test_fixed_body_merge_tools(self):
        from src.tools.spokestack_crud_tools import TOOLS
        merge_tools = [
            ("create_board", "board"), ("log_mention", "social_mention"),
            ("create_survey", "nps_survey"), ("create_canned_response", "canned_response"),
            ("create_role", "access_role"), ("create_module_manifest", "module_manifest"),
        ]
        for tool_name, expected_category in merge_tools:
            assert "fixed_body_merge" in TOOLS[tool_name], f"{tool_name} missing fixed_body_merge"
            assert TOOLS[tool_name]["fixed_body_merge"]["category"] == expected_category


class TestToolExecution:

    @pytest.mark.asyncio
    async def test_create_board_via_executor(self):
        from src.tools.tool_executor import execute_tool
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "ctx_board_1"}

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await execute_tool("create_board", {
                "key": "board_sprint_q2",
                "value": {"name": "Q2 Sprint", "board_type": "sprint"},
            }, "org_123")

            body = mock_client.post.call_args.kwargs["json"]
            assert body["entryType"] == "ENTITY"
            assert body["category"] == "board"
            assert body["key"] == "board_sprint_q2"

    @pytest.mark.asyncio
    async def test_log_mention_via_executor(self):
        from src.tools.tool_executor import execute_tool
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "ctx_mention_1"}

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await execute_tool("log_mention", {
                "key": "mention_20260403_twitter",
                "value": {"platform": "twitter", "content": "Great product!", "sentiment": "positive"},
            }, "org_123")

            body = mock_client.post.call_args.kwargs["json"]
            assert body["category"] == "social_mention"

    @pytest.mark.asyncio
    async def test_delegate_task_via_executor(self):
        from src.tools.tool_executor import execute_tool
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "task_del_1", "title": "Review docs"}

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await execute_tool("delegate_task", {
                "title": "Review docs",
                "assigneeId": "user_456",
                "priority": "HIGH",
            }, "org_123")

            call_url = mock_client.post.call_args.args[0]
            assert "/api/v1/tasks" in call_url
