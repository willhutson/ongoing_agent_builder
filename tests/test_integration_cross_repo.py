"""
Cross-Repo Integration Tests — Agent Builder Side

Tests the full agent-builder path for each cross-repo integration scenario:
- CoreToolkit methods call the right endpoints with the right payloads
- Context injection includes events, integrations, and client data
- Agent event handler processes incoming events
- Intent routing sends DAM/event queries to the right agents
- Module guard + upsell works for enterprise modules

All tests mock the HTTP layer (no live spokestack-core needed).
Run with: pytest tests/test_integration_cross_repo.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock


# ══════════════════════════════════════════════════════════════
# Test 1: Client Lifecycle (Customer → Client migration)
# ══════════════════════════════════════════════════════════════

class TestClientLifecycle:
    """Validates Client model migration end-to-end."""

    @pytest.mark.asyncio
    async def test_create_client_calls_clients_endpoint(self):
        """POST /api/v1/clients (not /customers)."""
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"id": "cli_1", "name": "Acme Corp", "industry": "Technology", "isActive": True}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            with patch.object(CoreToolkit, "_report", new_callable=AsyncMock):
                result = await toolkit.create_client({"name": "Acme Corp", "email": "hello@acme.com"})

                # Verify it calls /api/v1/clients, NOT /api/v1/customers
                mock_req.assert_called_once()
                assert mock_req.call_args.args[1] == "/api/v1/clients"
                assert result["name"] == "Acme Corp"

    @pytest.mark.asyncio
    async def test_create_customer_alias_routes_to_clients(self):
        """Backwards compat: create_customer still works."""
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"id": "cli_2", "name": "Legacy Inc"}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            with patch.object(CoreToolkit, "_report", new_callable=AsyncMock):
                result = await toolkit.create_customer({"name": "Legacy Inc"})
                assert mock_req.call_args.args[1] == "/api/v1/clients"

    @pytest.mark.asyncio
    async def test_create_order_uses_client_id(self):
        """create_order sends clientId (not customerId) to core."""
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"id": "ord_1", "status": "PENDING"}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            with patch.object(CoreToolkit, "_report", new_callable=AsyncMock):
                await toolkit.create_order({"client_id": "cli_1", "total": 5000})
                payload = mock_req.call_args.kwargs["json"]
                assert "clientId" in payload
                assert payload["clientId"] == "cli_1"
                assert "customerId" not in payload

    @pytest.mark.asyncio
    async def test_action_reporter_fires_on_client_create(self):
        """Creating a client fires a client.created action report."""
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"id": "cli_3", "name": "Reported Inc"}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response):
            with patch.object(CoreToolkit, "_report", new_callable=AsyncMock) as mock_report:
                await toolkit.create_client({"name": "Reported Inc"})
                mock_report.assert_called_once_with("client.created", "CLIENT", mock_response, "core_crm")


# ══════════════════════════════════════════════════════════════
# Test 3: Integration Tools (Nango proxy)
# ══════════════════════════════════════════════════════════════

class TestNangoIntegration:
    """Validates listIntegrations and proxyIntegration tools."""

    @pytest.mark.asyncio
    async def test_list_integrations_calls_correct_endpoint(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"connections": [
            {"provider": "asana", "status": "ACTIVE", "providerLabel": "Asana"},
            {"provider": "hubspot", "status": "ACTIVE", "providerLabel": "HubSpot"},
        ]}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.list_integrations()
            mock_req.assert_called_once_with("GET", "/api/v1/integrations")
            assert len(result["connections"]) == 2
            assert result["connections"][0]["provider"] == "asana"

    @pytest.mark.asyncio
    async def test_proxy_integration_sends_correct_payload(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"data": [{"gid": "12345", "name": "Design homepage"}]}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.proxy_integration("asana", "/api/1.0/tasks", method="GET")
            mock_req.assert_called_once_with("POST", "/api/v1/integrations/proxy", json={
                "provider": "asana",
                "endpoint": "/api/1.0/tasks",
                "method": "GET",
            })

    @pytest.mark.asyncio
    async def test_proxy_integration_with_body(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"data": {"gid": "99"}}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            await toolkit.proxy_integration(
                "hubspot", "/crm/v3/objects/contacts", method="POST",
                body={"properties": {"email": "test@example.com"}},
            )
            payload = mock_req.call_args.kwargs["json"]
            assert payload["method"] == "POST"
            assert payload["body"]["properties"]["email"] == "test@example.com"

    def test_integration_context_injection_with_active_connections(self):
        """Agent prompt includes connected integrations."""
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are a helpful assistant."
        integrations = [
            {"provider": "asana", "providerLabel": "Asana", "status": "ACTIVE", "moduleType": "TASKS"},
            {"provider": "slack", "status": "INACTIVE"},
        ]
        result = inject_context_into_prompt(prompt, [], integrations=integrations)
        assert "Asana" in result
        assert "proxy_integration" in result
        # INACTIVE connections should be filtered
        assert "slack" not in result.lower().split("connected integrations")[1] if "Connected Integrations" in result else True


# ══════════════════════════════════════════════════════════════
# Test 6: Project Completion Chain (event context)
# ══════════════════════════════════════════════════════════════

class TestProjectCompletionChain:
    """Validates event context injection for status changes."""

    def test_event_context_shows_status_transition(self):
        """Agent prompt includes Project.status_changed with from→to."""
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are a project manager."
        events = [{
            "entityType": "Project",
            "action": "status_changed",
            "entityId": "proj_q2",
            "metadata": {"fromStatus": "ACTIVE", "toStatus": "COMPLETED", "title": "Q2 Campaign"},
        }]
        result = inject_context_into_prompt(prompt, [], events=events)
        assert "Project.status_changed" in result
        assert "ACTIVE → COMPLETED" in result

    def test_multiple_events_in_context(self):
        """Multiple recent events all appear in prompt."""
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are an assistant."
        events = [
            {"entityType": "Task", "action": "created", "entityId": "t1", "metadata": {}},
            {"entityType": "Project", "action": "status_changed", "entityId": "p1",
             "metadata": {"fromStatus": "ACTIVE", "toStatus": "COMPLETED"}},
            {"entityType": "Client", "action": "created", "entityId": "c1", "metadata": {"title": "Acme"}},
        ]
        result = inject_context_into_prompt(prompt, [], events=events)
        assert "Task.created" in result
        assert "Project.status_changed" in result
        assert "Client.created" in result


# ══════════════════════════════════════════════════════════════
# Test 8: DAM Full Cycle (manage_assets tool)
# ══════════════════════════════════════════════════════════════

class TestDAMFullCycle:
    """Validates all manageAssets actions route correctly."""

    @pytest.mark.asyncio
    async def test_search_assets_by_query(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"data": [{"id": "a1", "name": "logo-dark.svg", "assetType": "IMAGE"}]}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.manage_assets("searchAssets", query="logo", asset_type="IMAGE")
            mock_req.assert_called_once()
            assert mock_req.call_args.args[1] == "/api/v1/assets"
            params = mock_req.call_args.kwargs["params"]
            assert params["q"] == "logo"
            assert params["assetType"] == "IMAGE"

    @pytest.mark.asyncio
    async def test_list_libraries(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"data": [{"id": "lib1", "name": "Brand Kit", "libraryType": "BRAND"}]}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.manage_assets("listLibraries")
            mock_req.assert_called_once_with("GET", "/api/v1/assets/libraries")

    @pytest.mark.asyncio
    async def test_get_asset_by_id(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"id": "a1", "name": "logo-dark.svg", "versions": [{"version": 1}, {"version": 2}]}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.manage_assets("getAsset", asset_id="a1")
            mock_req.assert_called_once_with("GET", "/api/v1/assets/a1")
            assert result["name"] == "logo-dark.svg"
            assert len(result["versions"]) == 2

    @pytest.mark.asyncio
    async def test_list_folder(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"id": "f1", "name": "Logos", "assets": []}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.manage_assets("listFolder", folder_id="f1")
            mock_req.assert_called_once_with("GET", "/api/v1/assets/folders/f1")

    @pytest.mark.asyncio
    async def test_list_folder_by_library(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"id": "lib1", "folders": []}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.manage_assets("listFolder", library_id="lib1")
            mock_req.assert_called_once_with("GET", "/api/v1/assets/libraries/lib1")

    def test_dam_query_routes_to_content_studio(self):
        """'find our brand logo' routes to content_studio module."""
        import asyncio
        from src.api.core_router import classify_intent
        result = asyncio.get_event_loop().run_until_complete(
            classify_intent("find our brand logo", "STARTER")
        )
        assert result == "content_studio"

    def test_asset_query_routes_to_content_studio(self):
        import asyncio
        from src.api.core_router import classify_intent
        result = asyncio.get_event_loop().run_until_complete(
            classify_intent("show me the brand assets library", "STARTER")
        )
        assert result == "content_studio"


# ══════════════════════════════════════════════════════════════
# Test 9: Event Subscription via Agent
# ══════════════════════════════════════════════════════════════

class TestEventSubscriptionViaAgent:
    """Validates subscribeToEvent tool and agent-events endpoint."""

    @pytest.mark.asyncio
    async def test_subscribe_to_event_creates_subscription(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = {"id": "sub_1", "entityType": "Project", "action": "status_changed", "enabled": True}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.subscribe_to_event(
                entity_type="Project",
                action="status_changed",
                conditions={"toStatus": "COMPLETED"},
                description="Watch for project completions",
            )
            mock_req.assert_called_once()
            payload = mock_req.call_args.kwargs["json"]
            assert payload["entityType"] == "Project"
            assert payload["action"] == "status_changed"
            assert payload["config"]["conditions"]["toStatus"] == "COMPLETED"
            assert payload["enabled"] is True

    @pytest.mark.asyncio
    async def test_list_recent_events_with_filters(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit("org_test", "user_test")

        mock_response = [{"entityType": "Project", "action": "status_changed", "entityId": "p1"}]
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.list_recent_events(
                entity_type="Project", action="status_changed", limit=5,
            )
            params = mock_req.call_args.kwargs["params"]
            assert params["entityType"] == "Project"
            assert params["action"] == "status_changed"
            assert params["limit"] == "5"

    def test_agent_event_handler_formats_status_change(self):
        """POST /api/v1/agent-events formats status_changed correctly."""
        from src.api.agent_events import format_event_for_agent, EventPayload
        event = EventPayload(
            entityType="Project",
            entityId="proj_q2",
            action="status_changed",
            metadata={"fromStatus": "ACTIVE", "toStatus": "COMPLETED"},
            organizationId="org_test",
        )
        msg = format_event_for_agent(event)
        assert "Project" in msg
        assert "ACTIVE" in msg
        assert "COMPLETED" in msg

    def test_agent_event_handler_formats_field_changes(self):
        from src.api.agent_events import format_event_for_agent, EventPayload
        event = EventPayload(
            entityType="Client",
            entityId="cli_1",
            action="updated",
            metadata={"changedFields": ["industry", "accountManagerId"]},
            organizationId="org_test",
        )
        msg = format_event_for_agent(event)
        assert "industry" in msg
        assert "accountManagerId" in msg


# ══════════════════════════════════════════════════════════════
# Test: Enterprise Module Guard
# ══════════════════════════════════════════════════════════════

class TestEnterpriseModuleGuard:
    """Validates enterprise module routing and upsell."""

    def test_enterprise_modules_in_routing(self):
        from src.api.core_router import MODULE_AGENT_TYPES
        assert MODULE_AGENT_TYPES["spokechat"] == "SPOKECHAT"
        assert MODULE_AGENT_TYPES["delegation"] == "DELEGATION"
        assert MODULE_AGENT_TYPES["access_control"] == "ACCESS_CONTROL"
        assert MODULE_AGENT_TYPES["api_management"] == "API_MANAGEMENT"
        assert MODULE_AGENT_TYPES["builder"] == "BUILDER"

    def test_enterprise_upsell_messages_are_specific(self):
        from src.modules.upsell_messages import get_upsell_message
        for mod in ["SPOKECHAT", "DELEGATION", "ACCESS_CONTROL", "API_MANAGEMENT", "BUILDER"]:
            msg = get_upsell_message(mod, "FREE")
            assert len(msg) > 20, f"Upsell for {mod} is too short"
            assert "Enterprise" in msg, f"Upsell for {mod} doesn't mention Enterprise"

    def test_spokechat_intent_routing(self):
        import asyncio
        from src.api.core_router import classify_intent
        result = asyncio.get_event_loop().run_until_complete(
            classify_intent("create a team chat channel", "ENTERPRISE")
        )
        assert result == "spokechat"

    def test_delegation_intent_routing(self):
        import asyncio
        from src.api.core_router import classify_intent
        result = asyncio.get_event_loop().run_until_complete(
            classify_intent("I need to delegate my approvals while I'm out of office", "ENTERPRISE")
        )
        assert result == "delegation"

    def test_access_control_intent_routing(self):
        import asyncio
        from src.api.core_router import classify_intent
        result = asyncio.get_event_loop().run_until_complete(
            classify_intent("who can access the finance module?", "ENTERPRISE")
        )
        assert result == "access_control"


# ══════════════════════════════════════════════════════════════
# Test: Full Context Injection Stack
# ══════════════════════════════════════════════════════════════

class TestFullContextInjectionStack:
    """Validates all three context layers inject together."""

    def test_all_three_layers_inject(self):
        """Context entries + integrations + events all appear in prompt."""
        from src.services.context_injector import inject_context_into_prompt

        prompt = "You are a tasks agent."
        entries = [
            {"entryType": "PREFERENCE", "key": "tone", "value": "concise"},
            {"entryType": "ENTITY", "key": "team.sarah", "value": {"name": "Sarah K."}, "confidence": 0.9},
        ]
        integrations = [
            {"provider": "asana", "providerLabel": "Asana", "status": "ACTIVE"},
        ]
        events = [
            {"entityType": "Task", "action": "completed", "entityId": "t99", "metadata": {"title": "Ship v2"}},
        ]

        result = inject_context_into_prompt(prompt, entries, integrations=integrations, events=events)

        # All three layers present
        assert "ORGANIZATIONAL CONTEXT" in result
        assert "[PREFERENCE] tone: concise" in result
        assert "[ENTITY] team.sarah" in result
        assert "Connected Integrations" in result
        assert "Asana" in result
        assert "Recent Activity" in result
        assert "Task.completed" in result

    def test_empty_layers_dont_add_noise(self):
        """If no entries/integrations/events, prompt is unchanged."""
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are a tasks agent."
        result = inject_context_into_prompt(prompt, [], integrations=[], events=[])
        assert result == prompt

    def test_idempotent_injection(self):
        """Injecting twice doesn't duplicate the context block."""
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are a tasks agent."
        entries = [{"entryType": "PREFERENCE", "key": "tone", "value": "concise"}]

        first = inject_context_into_prompt(prompt, entries)
        second = inject_context_into_prompt(first, entries)
        assert first == second
        assert first.count("ORGANIZATIONAL CONTEXT") == 1
