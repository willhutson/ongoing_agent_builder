"""API endpoint integration tests — verify FastAPI routes respond correctly."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import os


@pytest.fixture
def test_client():
    """Create a FastAPI TestClient."""
    # Set required env vars before importing the app
    os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
    os.environ.setdefault("AGENT_RUNTIME_SECRET", "test-secret")

    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


class TestAgentsRegistryEndpoint:

    def test_registry_returns_200(self, test_client):
        response = test_client.get(
            "/api/v1/agents/registry",
            headers={"X-Agent-Secret": "test-secret"},
        )
        assert response.status_code == 200

    def test_registry_has_agents(self, test_client):
        response = test_client.get(
            "/api/v1/agents/registry",
            headers={"X-Agent-Secret": "test-secret"},
        )
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) > 0
        assert "total" in data
        assert "mcTranslationMap" in data

    def test_registry_agent_has_tools(self, test_client):
        response = test_client.get(
            "/api/v1/agents/registry",
            headers={"X-Agent-Secret": "test-secret"},
        )
        data = response.json()
        for agent in data["agents"]:
            assert "tools" in agent, f"Agent {agent['type']} missing tools"


class TestAuthValidation:

    def test_reject_without_auth(self, test_client):
        """Requests without X-Agent-Secret or X-API-Key should be rejected."""
        response = test_client.get("/api/v1/agents/registry")
        assert response.status_code == 401

    def test_reject_with_bad_secret(self, test_client):
        response = test_client.get(
            "/api/v1/agents/registry",
            headers={"X-Agent-Secret": "wrong-secret"},
        )
        assert response.status_code == 401

    def test_health_no_auth_required(self, test_client):
        response = test_client.get("/health")
        assert response.status_code == 200


class TestCoreExecuteEndpoint:

    def test_execute_rejects_without_task(self, test_client):
        """Missing required field should return 422."""
        response = test_client.post(
            "/api/v1/core/execute",
            headers={"X-Agent-Secret": "test-secret"},
            json={"org_id": "org_1"},
        )
        assert response.status_code == 422

    @pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="Requires DB connection")
    def test_execute_accepts_tenant_id(self, test_client):
        """tenant_id should be accepted as org_id alias — not a 422."""
        response = test_client.post(
            "/api/v1/core/execute",
            headers={"X-Agent-Secret": "test-secret"},
            json={
                "task": "hello",
                "tenant_id": "org_test",
                "agent_type": "assistant",
            },
        )
        # Should not be 422 (validation error) — may be 500 from LLM/DB unavailable
        assert response.status_code != 422


class TestModuleRegistrationEndpoint:

    @pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="Requires DB connection")
    def test_module_register_endpoint_exists(self, test_client):
        """POST /api/v1/core/modules/register should not 404/405."""
        response = test_client.post(
            "/api/v1/core/modules/register",
            headers={"X-Agent-Secret": "test-secret"},
            json={
                "org_id": "org_test",
                "module_type": "TEST_MODULE",
            },
        )
        # Should not be 404 (not found) or 405 (method not allowed)
        # May be 200 (success) or 500 (DB unavailable in test env)
        assert response.status_code not in (404, 405)
