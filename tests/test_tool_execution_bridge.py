"""Tests for Phase 10B: Tool Execution Bridge."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


# ══════════════════════════════════════════════════════════════
# Tool Definitions
# ══════════════════════════════════════════════════════════════

class TestToolDefinitions:

    def test_all_30_plus_tools_defined(self):
        from src.tools.spokestack_crud_tools import TOOLS
        assert len(TOOLS) >= 30

    def test_each_tool_has_required_fields(self):
        from src.tools.spokestack_crud_tools import TOOLS
        for name, tool in TOOLS.items():
            assert "description" in tool, f"{name} missing description"
            assert "method" in tool, f"{name} missing method"
            assert "path" in tool, f"{name} missing path"
            assert tool["method"] in ("GET", "POST", "PATCH", "DELETE"), f"{name} bad method: {tool['method']}"

    def test_task_tools_exist(self):
        from src.tools.spokestack_crud_tools import TOOLS
        for name in ["create_task", "update_task", "complete_task", "delete_task", "list_tasks"]:
            assert name in TOOLS

    def test_brief_tools_exist(self):
        from src.tools.spokestack_crud_tools import TOOLS
        for name in ["create_brief", "update_brief", "approve_brief", "request_revisions", "list_briefs"]:
            assert name in TOOLS

    def test_project_tools_exist(self):
        from src.tools.spokestack_crud_tools import TOOLS
        for name in ["create_project", "update_project", "complete_project", "list_projects"]:
            assert name in TOOLS

    def test_order_tools_exist(self):
        from src.tools.spokestack_crud_tools import TOOLS
        for name in ["create_order", "update_order_status", "generate_invoice", "list_orders"]:
            assert name in TOOLS

    def test_client_tools_exist(self):
        from src.tools.spokestack_crud_tools import TOOLS
        for name in ["create_client", "update_client", "list_clients"]:
            assert name in TOOLS

    def test_context_tools_exist(self):
        from src.tools.spokestack_crud_tools import TOOLS
        assert "read_context" in TOOLS
        assert "write_context" in TOOLS

    def test_fixed_body_tools(self):
        from src.tools.spokestack_crud_tools import TOOLS
        assert TOOLS["complete_task"]["fixed_body"] == {"status": "DONE"}
        assert TOOLS["approve_brief"]["fixed_body"] == {"status": "COMPLETED"}
        assert TOOLS["request_revisions"]["fixed_body"] == {"status": "DRAFT"}
        assert TOOLS["complete_project"]["fixed_body"] == {"status": "COMPLETED"}


# ══════════════════════════════════════════════════════════════
# OpenAI Function Format Conversion
# ══════════════════════════════════════════════════════════════

class TestOpenAIConversion:

    def test_tool_to_openai_format(self):
        from src.tools.spokestack_crud_tools import tool_to_openai_function, TOOLS
        result = tool_to_openai_function("create_task", TOOLS["create_task"])
        assert result["type"] == "function"
        assert result["function"]["name"] == "create_task"
        assert "properties" in result["function"]["parameters"]
        assert "title" in result["function"]["parameters"]["properties"]
        assert "title" in result["function"]["parameters"]["required"]

    def test_get_openai_tools(self):
        from src.tools.spokestack_crud_tools import get_openai_tools
        tools = get_openai_tools(["create_task", "list_tasks"])
        assert len(tools) == 2
        names = {t["function"]["name"] for t in tools}
        assert names == {"create_task", "list_tasks"}

    def test_get_openai_tools_ignores_unknown(self):
        from src.tools.spokestack_crud_tools import get_openai_tools
        tools = get_openai_tools(["create_task", "nonexistent_tool"])
        assert len(tools) == 1


# ══════════════════════════════════════════════════════════════
# Tool Executor
# ══════════════════════════════════════════════════════════════

class TestToolExecutor:

    @pytest.mark.asyncio
    async def test_execute_get_tool(self):
        from src.tools.tool_executor import execute_tool
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "t1", "title": "Test"}]}

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get = AsyncMock(return_value=mock_response)

            result = await execute_tool("list_tasks", {"status": "TODO"}, "org_123")
            assert result["data"][0]["title"] == "Test"
            mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_post_tool(self):
        from src.tools.tool_executor import execute_tool
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "t2", "title": "New task"}

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await execute_tool("create_task", {"title": "New task", "priority": "HIGH"}, "org_123")
            assert result["id"] == "t2"

    @pytest.mark.asyncio
    async def test_execute_patch_with_path_param(self):
        from src.tools.tool_executor import execute_tool
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "b1", "status": "COMPLETED"}

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.patch = AsyncMock(return_value=mock_response)

            result = await execute_tool("approve_brief", {"briefId": "b1"}, "org_123")
            assert result["status"] == "COMPLETED"
            # Verify path param was substituted
            call_args = mock_client.patch.call_args
            assert "b1" in call_args.args[0]

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self):
        from src.tools.tool_executor import execute_tool
        result = await execute_tool("nonexistent_tool", {}, "org_123")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_includes_auth_headers(self):
        from src.tools.tool_executor import execute_tool
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get = AsyncMock(return_value=mock_response)

            await execute_tool("list_clients", {}, "org_xyz")
            headers = mock_client.get.call_args.kwargs["headers"]
            assert "X-Agent-Secret" in headers
            assert headers["X-Organization-Id"] == "org_xyz"

    @pytest.mark.asyncio
    async def test_execute_error_response(self):
        from src.tools.tool_executor import execute_tool
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get = AsyncMock(return_value=mock_response)

            result = await execute_tool("list_clients", {}, "org_123")
            assert "error" in result
            assert "404" in result["error"]


# ══════════════════════════════════════════════════════════════
# Agent Tool Assignment
# ══════════════════════════════════════════════════════════════

class TestAgentToolAssignment:

    def test_assistant_has_list_and_create_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("assistant")
        assert "list_tasks" in tools
        assert "create_task" in tools
        assert "list_projects" in tools

    def test_brief_writer_has_brief_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("brief_writer")
        assert "create_brief" in tools
        assert "approve_brief" in tools
        assert "request_revisions" in tools

    def test_project_manager_has_project_and_task_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("project_manager")
        assert "create_project" in tools
        assert "create_task" in tools

    def test_order_manager_has_order_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("order_manager")
        assert "create_order" in tools
        assert "generate_invoice" in tools

    def test_crm_manager_has_client_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("crm_manager")
        assert "create_client" in tools
        assert "update_client" in tools

    def test_unknown_agent_gets_assistant_tools(self):
        from src.tools.agent_tool_assignment import get_tools_for_agent
        tools = get_tools_for_agent("some_unknown_type")
        assistant_tools = get_tools_for_agent("assistant")
        assert tools == assistant_tools

    def test_openai_format_tools_for_agent(self):
        from src.tools.agent_tool_assignment import get_openai_tools_for_agent
        tools = get_openai_tools_for_agent("brief_writer")
        assert all(t["type"] == "function" for t in tools)
        names = {t["function"]["name"] for t in tools}
        assert "create_brief" in names
        assert "approve_brief" in names


# ══════════════════════════════════════════════════════════════
# MC Translation Map (updated for spec canonical types)
# ══════════════════════════════════════════════════════════════

class TestMCTranslationUpdated:

    def test_mc_general_to_assistant(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("mc-general") == "assistant"

    def test_mc_planner_to_project_manager(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("mc-planner") == "project_manager"

    def test_mc_reviewer_to_brief_writer(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("mc-reviewer") == "brief_writer"

    def test_mc_analyst_to_analyst(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("mc-analyst") == "analyst"

    def test_module_crm_to_crm_manager(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("module-crm-assistant") == "crm_manager"

    def test_module_briefs_to_brief_writer(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("module-briefs-assistant") == "brief_writer"

    def test_module_orders_to_order_manager(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("module-orders-assistant") == "order_manager"

    def test_module_finance_to_order_manager(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("module-finance-assistant") == "order_manager"

    def test_onboarding_to_core_onboarding(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("onboarding") == "core_onboarding"

    def test_canonical_passthrough(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("assistant") == "assistant"
        assert resolve_agent_type("brief_writer") == "brief_writer"
        assert resolve_agent_type("project_manager") == "project_manager"

    def test_all_mc_types_resolve_to_agent_tool_key(self):
        """Every MC type maps to a key in AGENT_TOOLS."""
        from src.services.agent_registry import MC_TO_CANONICAL_MAP
        from src.tools.agent_tool_assignment import AGENT_TOOLS
        for mc_type, canonical in MC_TO_CANONICAL_MAP.items():
            assert canonical in AGENT_TOOLS, (
                f"MC type '{mc_type}' → '{canonical}' but '{canonical}' not in AGENT_TOOLS"
            )


# ══════════════════════════════════════════════════════════════
# Registry Response
# ══════════════════════════════════════════════════════════════

class TestRegistryResponse:

    def test_response_includes_tools_per_agent(self):
        from src.services.agent_registry import build_registry_response
        response = build_registry_response()
        for agent in response["agents"]:
            assert "tools" in agent, f"Agent {agent['type']} missing tools"
            assert isinstance(agent["tools"], list)

    def test_response_includes_mc_translation_map(self):
        from src.services.agent_registry import build_registry_response
        response = build_registry_response()
        mc_map = response["mcTranslationMap"]
        assert mc_map["mc-general"] == "assistant"
        assert mc_map["mc-planner"] == "project_manager"
        assert mc_map["module-crm-assistant"] == "crm_manager"


# ══════════════════════════════════════════════════════════════
# CoreExecuteRequest field compat
# ══════════════════════════════════════════════════════════════

class TestCoreExecuteRequestCompat:

    def test_accepts_org_id(self):
        from src.api.core_router import CoreExecuteRequest
        req = CoreExecuteRequest(task="test", org_id="org_1")
        assert req.resolved_org_id == "org_1"

    def test_accepts_tenant_id(self):
        from src.api.core_router import CoreExecuteRequest
        req = CoreExecuteRequest(task="test", tenant_id="org_2")
        assert req.resolved_org_id == "org_2"

    def test_org_id_takes_precedence(self):
        from src.api.core_router import CoreExecuteRequest
        req = CoreExecuteRequest(task="test", org_id="org_1", tenant_id="org_2")
        assert req.resolved_org_id == "org_1"

    def test_user_id_defaults_to_system(self):
        from src.api.core_router import CoreExecuteRequest
        req = CoreExecuteRequest(task="test", org_id="org_1")
        assert req.user_id == "system"

    def test_conversation_history_accepted(self):
        from src.api.core_router import CoreExecuteRequest
        req = CoreExecuteRequest(
            task="test", org_id="org_1",
            conversation_history=[{"role": "user", "content": "hello"}],
        )
        assert req.conversation_history is not None
