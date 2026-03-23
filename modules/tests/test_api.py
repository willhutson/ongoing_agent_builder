"""Tests for the combined FastAPI app — endpoints, routing, health."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from contextlib import asynccontextmanager


@pytest_asyncio.fixture
async def client():
    """Create test client with lifespan triggered."""
    from combined import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # Trigger lifespan startup
        async with app.router.lifespan_context(app):
            yield c


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "spokestack-combined"
    assert data["agents"] > 0
    assert data["modules"] == 8


@pytest.mark.asyncio
async def test_list_agents(client):
    resp = await client.get("/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 48  # 46 module agents + wizard + observer
    assert "wizard" in str(data["by_module"])


@pytest.mark.asyncio
async def test_list_modules(client):
    resp = await client.get("/modules")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 8
    assert "foundation" in data["modules"]


@pytest.mark.asyncio
async def test_state(client):
    resp = await client.get("/state")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_agents" in data
    assert "modules" in data


@pytest.mark.asyncio
async def test_dashboard_html(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "SpokeStack" in resp.text
    assert "Mission Control" in resp.text


@pytest.mark.asyncio
async def test_execute_unknown_agent(client):
    resp = await client.post("/execute", json={
        "agent_type": "nonexistent_agent",
        "task": "hello",
    })
    assert resp.status_code == 404
