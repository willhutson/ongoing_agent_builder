"""Tests for Phase 6C: client migration, integrations, enterprise routing."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, patch


# ══════════════════════════════════════════════════════════════
# Task 1: Customer → Client migration
# ══════════════════════════════════════════════════════════════

class TestClientMigration:
    """Verify customer → client rename is complete."""

    def test_create_client_tool_exists(self):
        from src.tools.core_tool_definitions import ORDERS_TOOLS
        tool_names = {t["function"]["name"] for t in ORDERS_TOOLS}
        assert "create_client" in tool_names
        assert "create_customer" not in tool_names

    def test_create_order_uses_client_id(self):
        from src.tools.core_tool_definitions import ORDERS_TOOLS
        create_order = next(t for t in ORDERS_TOOLS if t["function"]["name"] == "create_order")
        props = create_order["function"]["parameters"]["properties"]
        assert "client_id" in props
        assert "customer_id" not in props

    def test_core_tool_names_has_create_client(self):
        from src.tools.core_tool_definitions import CORE_TOOL_NAMES
        assert "create_client" in CORE_TOOL_NAMES

    def test_orders_agent_prompt_says_client(self):
        with open("src/agents/core_orders_agent.py") as f:
            content = f.read()
        # "client" in the data entity sense should be present
        assert "Client management" in content
        assert "client record" in content

    def test_toolkit_create_client_method_exists(self):
        from src.tools.core_toolkit import CoreToolkit
        assert hasattr(CoreToolkit, "create_client")

    def test_toolkit_create_customer_alias_exists(self):
        """Backwards compat — create_customer still works."""
        from src.tools.core_toolkit import CoreToolkit
        assert hasattr(CoreToolkit, "create_customer")

    def test_intent_patterns_use_client_not_customer(self):
        from src.tools.core_tool_definitions import CORE_INTENT_PATTERNS
        orders_patterns = CORE_INTENT_PATTERNS["core_orders"]
        assert "client" in orders_patterns
        assert "customer" not in orders_patterns


# ══════════════════════════════════════════════════════════════
# Task 2: Integration tools
# ══════════════════════════════════════════════════════════════

class TestIntegrationTools:
    """Verify integration tools are registered and available."""

    def test_integration_tools_defined(self):
        from src.tools.core_tool_definitions import INTEGRATION_TOOLS
        names = {t["function"]["name"] for t in INTEGRATION_TOOLS}
        assert "list_integrations" in names
        assert "proxy_integration" in names

    def test_integration_tools_in_core_tool_names(self):
        from src.tools.core_tool_definitions import CORE_TOOL_NAMES
        assert "list_integrations" in CORE_TOOL_NAMES
        assert "proxy_integration" in CORE_TOOL_NAMES

    def test_integration_tools_in_starter_tier(self):
        from src.tools.core_tool_definitions import TIER_TOOL_MAP
        starter_tools = []
        for group in TIER_TOOL_MAP["STARTER"]:
            starter_tools.extend(group)
        names = {t["function"]["name"] for t in starter_tools}
        assert "list_integrations" in names
        assert "proxy_integration" in names

    def test_integration_tools_not_in_free_tier(self):
        from src.tools.core_tool_definitions import TIER_TOOL_MAP
        free_tools = []
        for group in TIER_TOOL_MAP["FREE"]:
            free_tools.extend(group)
        names = {t["function"]["name"] for t in free_tools}
        assert "list_integrations" not in names
        assert "proxy_integration" not in names

    def test_all_agents_have_integration_tools(self):
        from src.tools.core_tool_definitions import AGENT_CORE_TOOL_MAP
        for agent_type, tool_names in AGENT_CORE_TOOL_MAP.items():
            assert "list_integrations" in tool_names, f"{agent_type} missing list_integrations"
            assert "proxy_integration" in tool_names, f"{agent_type} missing proxy_integration"

    def test_proxy_integration_requires_provider_and_endpoint(self):
        from src.tools.core_tool_definitions import INTEGRATION_TOOLS
        proxy = next(t for t in INTEGRATION_TOOLS if t["function"]["name"] == "proxy_integration")
        required = proxy["function"]["parameters"]["required"]
        assert "provider" in required
        assert "endpoint" in required

    @pytest.mark.asyncio
    async def test_toolkit_list_integrations(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"
        toolkit._client = None

        mock_response = {"connections": [{"provider": "asana", "status": "ACTIVE"}]}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response):
            result = await toolkit.list_integrations()
            assert result["connections"][0]["provider"] == "asana"

    @pytest.mark.asyncio
    async def test_toolkit_proxy_integration(self):
        from src.tools.core_toolkit import CoreToolkit
        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"
        toolkit._client = None

        mock_response = {"data": [{"id": "1", "name": "My Task"}]}
        with patch.object(CoreToolkit, "_request", new_callable=AsyncMock, return_value=mock_response) as mock_req:
            result = await toolkit.proxy_integration("asana", "/api/1.0/tasks")
            mock_req.assert_called_once_with("POST", "/api/v1/integrations/proxy", json={
                "provider": "asana",
                "endpoint": "/api/1.0/tasks",
                "method": "GET",
            })


# ══════════════════════════════════════════════════════════════
# Task 3: Integration-aware context injection
# ══════════════════════════════════════════════════════════════

class TestIntegrationContextInjection:
    """Verify integration info is injected into prompts."""

    def test_format_integrations_with_active_connections(self):
        from src.services.context_injector import format_integrations
        integrations = [
            {"provider": "asana", "providerLabel": "Asana", "status": "ACTIVE", "moduleType": "TASKS"},
            {"provider": "hubspot", "providerLabel": "HubSpot", "status": "ACTIVE", "moduleType": "CRM"},
            {"provider": "slack", "status": "INACTIVE"},
        ]
        result = format_integrations(integrations)
        assert "asana" in result
        assert "HubSpot" in result
        # INACTIVE without seededData should be filtered
        assert "proxy_integration" in result

    def test_format_integrations_empty(self):
        from src.services.context_injector import format_integrations
        assert format_integrations([]) == ""
        assert format_integrations(None) == ""

    def test_format_integrations_all_inactive(self):
        from src.services.context_injector import format_integrations
        integrations = [{"provider": "slack", "status": "INACTIVE"}]
        assert format_integrations(integrations) == ""

    def test_inject_with_integrations(self):
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are an assistant."
        entries = [{"entryType": "PREFERENCE", "key": "tone", "value": "concise"}]
        integrations = [{"provider": "asana", "status": "ACTIVE"}]

        result = inject_context_into_prompt(prompt, entries, integrations=integrations)
        assert "ORGANIZATIONAL CONTEXT" in result
        assert "asana" in result
        assert "proxy_integration" in result


# ══════════════════════════════════════════════════════════════
# Task 4: Enterprise module routing
# ══════════════════════════════════════════════════════════════

class TestEnterpriseModuleRouting:
    """Verify enterprise modules are routed correctly."""

    def test_enterprise_intent_patterns_exist(self):
        from src.tools.core_tool_definitions import ENTERPRISE_INTENT_PATTERNS
        assert "SPOKECHAT" in ENTERPRISE_INTENT_PATTERNS
        assert "DELEGATION" in ENTERPRISE_INTENT_PATTERNS
        assert "ACCESS_CONTROL" in ENTERPRISE_INTENT_PATTERNS
        assert "API_MANAGEMENT" in ENTERPRISE_INTENT_PATTERNS
        assert "BUILDER" in ENTERPRISE_INTENT_PATTERNS

    def test_enterprise_modules_in_module_agent_types(self):
        from src.api.core_router import MODULE_AGENT_TYPES
        assert MODULE_AGENT_TYPES.get("spokechat") == "SPOKECHAT"
        assert MODULE_AGENT_TYPES.get("delegation") == "DELEGATION"
        assert MODULE_AGENT_TYPES.get("access_control") == "ACCESS_CONTROL"
        assert MODULE_AGENT_TYPES.get("api_management") == "API_MANAGEMENT"
        assert MODULE_AGENT_TYPES.get("builder") == "BUILDER"

    def test_enterprise_module_agent_map(self):
        from src.api.core_router import ENTERPRISE_MODULE_AGENT_MAP
        assert ENTERPRISE_MODULE_AGENT_MAP["SPOKECHAT"] == "gateway_slack"
        assert ENTERPRISE_MODULE_AGENT_MAP["DELEGATION"] == "resource"
        assert ENTERPRISE_MODULE_AGENT_MAP["ACCESS_CONTROL"] == "instance_onboarding"
        assert ENTERPRISE_MODULE_AGENT_MAP["API_MANAGEMENT"] == "instance_onboarding"
        assert ENTERPRISE_MODULE_AGENT_MAP["BUILDER"] == "prompt_helper"

    def test_enterprise_upsell_messages_exist(self):
        from src.modules.upsell_messages import get_upsell_message
        for mod in ["SPOKECHAT", "DELEGATION", "ACCESS_CONTROL", "API_MANAGEMENT", "BUILDER"]:
            msg = get_upsell_message(mod, "FREE")
            assert len(msg) > 0
            assert "Enterprise" in msg

    def test_spokechat_keywords_match(self):
        from src.tools.core_tool_definitions import ENTERPRISE_INTENT_PATTERNS
        patterns = ENTERPRISE_INTENT_PATTERNS["SPOKECHAT"]
        assert "internal chat" in patterns
        assert "team chat" in patterns
        assert "channels" in patterns

    def test_delegation_keywords_match(self):
        from src.tools.core_tool_definitions import ENTERPRISE_INTENT_PATTERNS
        patterns = ENTERPRISE_INTENT_PATTERNS["DELEGATION"]
        assert "delegate" in patterns
        assert "out of office" in patterns

    def test_access_control_keywords_match(self):
        from src.tools.core_tool_definitions import ENTERPRISE_INTENT_PATTERNS
        patterns = ENTERPRISE_INTENT_PATTERNS["ACCESS_CONTROL"]
        assert "permissions" in patterns
        assert "rbac" in patterns
