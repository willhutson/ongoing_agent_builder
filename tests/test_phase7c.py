"""Tests for Phase 7C: event-aware agents, DAM tools, agent event handler."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, patch


# ══════════════════════════════════════════════════════════════
# Event tool definitions
# ══════════════════════════════════════════════════════════════

class TestEventToolDefinitions:

    def test_event_tools_defined(self):
        from src.tools.spokestack_events import EVENT_AND_ASSET_TOOLS, EVENT_TOOL_NAMES
        names = {t["function"]["name"] for t in EVENT_AND_ASSET_TOOLS}
        assert "list_recent_events" in names
        assert "subscribe_to_event" in names
        assert "manage_assets" in names
        assert EVENT_TOOL_NAMES == names

    def test_event_tools_in_core_tool_names(self):
        from src.tools.core_tool_definitions import CORE_TOOL_NAMES
        assert "list_recent_events" in CORE_TOOL_NAMES
        assert "subscribe_to_event" in CORE_TOOL_NAMES
        assert "manage_assets" in CORE_TOOL_NAMES

    def test_list_recent_events_in_free_tier(self):
        from src.tools.core_tool_definitions import TIER_TOOL_MAP
        free_tools = []
        for group in TIER_TOOL_MAP["FREE"]:
            free_tools.extend(group)
        names = {t["function"]["name"] for t in free_tools}
        assert "list_recent_events" in names
        assert "subscribe_to_event" in names

    def test_manage_assets_not_in_free_tier(self):
        from src.tools.core_tool_definitions import TIER_TOOL_MAP
        free_tools = []
        for group in TIER_TOOL_MAP["FREE"]:
            free_tools.extend(group)
        names = {t["function"]["name"] for t in free_tools}
        assert "manage_assets" not in names

    def test_manage_assets_in_starter_tier(self):
        from src.tools.core_tool_definitions import TIER_TOOL_MAP
        starter_tools = []
        for group in TIER_TOOL_MAP["STARTER"]:
            starter_tools.extend(group)
        names = {t["function"]["name"] for t in starter_tools}
        assert "manage_assets" in names

    def test_all_agents_have_event_tools(self):
        from src.tools.core_tool_definitions import AGENT_CORE_TOOL_MAP
        for agent_type, tool_names in AGENT_CORE_TOOL_MAP.items():
            assert "list_recent_events" in tool_names, f"{agent_type} missing list_recent_events"
            assert "subscribe_to_event" in tool_names, f"{agent_type} missing subscribe_to_event"
            assert "manage_assets" in tool_names, f"{agent_type} missing manage_assets"

    def test_subscribe_to_event_requires_entity_type_and_action(self):
        from src.tools.spokestack_events import SUBSCRIBE_TO_EVENT_TOOL
        required = SUBSCRIBE_TO_EVENT_TOOL["function"]["parameters"]["required"]
        assert "entity_type" in required
        assert "action" in required


# ══════════════════════════════════════════════════════════════
# CoreToolkit event/asset methods
# ══════════════════════════════════════════════════════════════

class TestCoreToolkitEvents:

    @pytest.mark.asyncio
    async def test_list_recent_events(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"
        toolkit._client = None

        mock_response = [{"entityType": "Task", "action": "created", "entityId": "t1"}]
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response):
            result = await toolkit.list_recent_events(entity_type="Task", limit=5)
            assert result[0]["entityType"] == "Task"

    @pytest.mark.asyncio
    async def test_subscribe_to_event(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"
        toolkit._client = None

        mock_response = {"id": "sub_1", "entityType": "Project", "action": "status_changed"}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.subscribe_to_event("Project", "status_changed", description="Watch completions")
            mock_req.assert_called_once()
            assert "subscriptions" in mock_req.call_args.args[1]

    @pytest.mark.asyncio
    async def test_manage_assets_search(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"
        toolkit._client = None

        mock_response = {"data": [{"id": "a1", "name": "logo.png"}]}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.manage_assets("searchAssets", query="logo")
            mock_req.assert_called_once()
            assert "assets" in mock_req.call_args.args[1]

    @pytest.mark.asyncio
    async def test_manage_assets_list_libraries(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"
        toolkit._client = None

        mock_response = {"data": [{"id": "lib1", "name": "Brand Assets"}]}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.manage_assets("listLibraries")
            mock_req.assert_called_once_with("GET", "/api/v1/assets/libraries")

    @pytest.mark.asyncio
    async def test_manage_assets_get_asset(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"
        toolkit._client = None

        mock_response = {"id": "a1", "name": "logo.png", "url": "https://..."}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.manage_assets("getAsset", asset_id="a1")
            mock_req.assert_called_once_with("GET", "/api/v1/assets/a1")

    @pytest.mark.asyncio
    async def test_manage_assets_unknown_action(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"
        toolkit._client = None

        result = await toolkit.manage_assets("unknownAction")
        assert "error" in result


# ══════════════════════════════════════════════════════════════
# Event-aware context injection
# ══════════════════════════════════════════════════════════════

class TestEventContextInjection:

    def test_format_events_with_data(self):
        from src.services.context_injector import format_events
        events = [
            {"entityType": "Task", "action": "created", "entityId": "t1", "metadata": {"title": "New task"}},
            {"entityType": "Project", "action": "status_changed", "entityId": "p1",
             "metadata": {"fromStatus": "ACTIVE", "toStatus": "COMPLETED"}},
        ]
        result = format_events(events)
        assert "Task.created" in result
        assert "ACTIVE → COMPLETED" in result
        assert "list_recent_events" in result

    def test_format_events_empty(self):
        from src.services.context_injector import format_events
        assert format_events([]) == ""
        assert format_events(None) == ""

    def test_format_events_caps_at_10(self):
        from src.services.context_injector import format_events
        events = [{"entityType": "Task", "action": "created", "entityId": f"t{i}"} for i in range(20)]
        result = format_events(events)
        # Should have at most 10 event lines (plus header + footer)
        event_lines = [l for l in result.split("\n") if l.startswith("- ")]
        assert len(event_lines) <= 10

    def test_inject_with_events(self):
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are an assistant."
        entries = [{"entryType": "PREFERENCE", "key": "tone", "value": "concise"}]
        events = [{"entityType": "Task", "action": "completed", "entityId": "t1"}]

        result = inject_context_into_prompt(prompt, entries, events=events)
        assert "Recent Activity" in result
        assert "Task.completed" in result


# ══════════════════════════════════════════════════════════════
# Agent event handler endpoint
# ══════════════════════════════════════════════════════════════

class TestAgentEventHandler:

    def test_format_event_for_agent(self):
        from src.api.agent_events import format_event_for_agent, EventPayload
        event = EventPayload(
            entityType="Project",
            entityId="proj_123",
            action="status_changed",
            metadata={"fromStatus": "ACTIVE", "toStatus": "COMPLETED", "title": "Q2 Campaign"},
            organizationId="org_1",
        )
        msg = format_event_for_agent(event)
        assert "Project" in msg
        assert "status_changed" in msg
        assert "ACTIVE" in msg
        assert "COMPLETED" in msg

    def test_format_event_with_changed_fields(self):
        from src.api.agent_events import format_event_for_agent, EventPayload
        event = EventPayload(
            entityType="Task",
            entityId="task_456",
            action="updated",
            metadata={"changedFields": ["title", "priority"]},
            organizationId="org_1",
        )
        msg = format_event_for_agent(event)
        assert "title, priority" in msg

    def test_format_event_minimal(self):
        from src.api.agent_events import format_event_for_agent, EventPayload
        event = EventPayload(
            entityType="Client",
            entityId="c_789",
            action="created",
            organizationId="org_1",
        )
        msg = format_event_for_agent(event)
        assert "Client" in msg
        assert "created" in msg
        assert "c_789" in msg


# ══════════════════════════════════════════════════════════════
# DAM intent routing
# ══════════════════════════════════════════════════════════════

class TestDAMIntentRouting:

    def test_dam_intent_patterns_exist(self):
        from src.tools.core_tool_definitions import DAM_INTENT_PATTERNS
        assert "asset" in DAM_INTENT_PATTERNS
        assert "brand files" in DAM_INTENT_PATTERNS
        assert "logo" in DAM_INTENT_PATTERNS

    def test_event_intent_patterns_exist(self):
        from src.tools.core_tool_definitions import EVENT_INTENT_PATTERNS
        assert "recent activity" in EVENT_INTENT_PATTERNS
        assert "what happened" in EVENT_INTENT_PATTERNS
        assert "what changed" in EVENT_INTENT_PATTERNS

    @pytest.mark.asyncio
    async def test_dam_query_routes_to_content_studio(self):
        from src.api.core_router import classify_intent
        result = await classify_intent("find the logo for Acme Corp", "STARTER")
        assert result == "content_studio"

    @pytest.mark.asyncio
    async def test_activity_query_routes_to_tasks(self):
        from src.api.core_router import classify_intent
        result = await classify_intent("what happened today", "FREE")
        assert result == "core_tasks"
