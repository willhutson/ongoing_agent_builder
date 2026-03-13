"""Tests for agent instantiation and tool definitions across all modules."""

import pytest
from shared.base_agent import BaseAgent, AgentContext, AgentResult


# ── Agent factories ──────────────────────────────────────────────────────

MODULES = {
    "foundation": ("foundation.agents", "create_agents", 4),
    "studio": ("studio.agents", "create_agents", 5),
    "brand": ("brand.agents", "create_agents", 4),
    "research": ("research.agents", "create_agents", 6),
    "strategy": ("strategy.agents", "create_agents", 6),
    "operations": ("operations.agents", "create_agents", 7),
    "client": ("client.agents", "create_agents", 7),
    "distribution": ("distribution.agents", "create_agents", 7),
}


@pytest.fixture(params=MODULES.keys())
def module_agents(request, llm_client, settings):
    """Instantiate agents for a module."""
    module_name = request.param
    module_path, factory_name, expected_count = MODULES[module_name]

    import importlib
    mod = importlib.import_module(module_path)
    factory = getattr(mod, factory_name)
    agents = factory(llm_client, settings)
    return module_name, agents, expected_count


def test_module_agent_count(module_agents):
    """Each module creates the expected number of agents."""
    name, agents, expected = module_agents
    assert len(agents) == expected, f"{name} expected {expected} agents, got {len(agents)}"


def test_all_agents_are_base_agent(module_agents):
    """Every agent inherits from BaseAgent."""
    _, agents, _ = module_agents
    for agent_name, agent in agents.items():
        assert isinstance(agent, BaseAgent), f"{agent_name} is not a BaseAgent"


def test_all_agents_have_name_and_prompt(module_agents):
    """Every agent has a non-empty name and system prompt."""
    _, agents, _ = module_agents
    for agent_name, agent in agents.items():
        assert agent.name, f"{agent_name} has empty name"
        assert agent.system_prompt, f"{agent_name} has empty system_prompt"
        assert len(agent.system_prompt) > 20, f"{agent_name} system_prompt too short"


def test_all_agents_have_tools(module_agents):
    """Every agent defines at least one tool."""
    _, agents, _ = module_agents
    for agent_name, agent in agents.items():
        assert len(agent.tools) >= 1, f"{agent_name} has no tools"


def test_tool_schema_valid(module_agents):
    """Every tool has name, description, and input_schema."""
    _, agents, _ = module_agents
    for agent_name, agent in agents.items():
        for tool in agent.tools:
            assert "name" in tool, f"{agent_name}: tool missing name"
            assert "description" in tool, f"{agent_name}: tool missing description"
            assert "input_schema" in tool, f"{agent_name}: tool missing input_schema"
            schema = tool["input_schema"]
            assert schema.get("type") == "object", f"{agent_name}/{tool['name']}: schema type must be object"


# ── Tool execution (sync, no LLM calls) ────────────────────────────────

@pytest.mark.asyncio
async def test_brief_agent_tools(llm_client, settings):
    """BriefAgent tools execute without error."""
    from foundation.agents import BriefAgent
    from shared.config import get_model_id

    agent = BriefAgent(llm_client, get_model_id(settings, "standard"))

    result = await agent._execute_tool("parse_brief", {"raw_input": "We need a campaign for Q4"})
    assert result["status"] == "parsed"

    result = await agent._execute_tool("estimate_complexity", {"deliverables": ["a", "b", "c", "d", "e", "f"]})
    assert result["complexity"] == "high"

    result = await agent._execute_tool("unknown_tool", {})
    assert "error" in result


# ── Wizard ──────────────────────────────────────────────────────────────

def test_wizard_creation(llm_client, settings):
    """Wizard agent creates with platform state."""
    from wizard.agent import create_wizard

    platform_state = {
        "total_agents": 46,
        "modules": {"foundation": {"agents": 4}},
        "integrations": {},
        "mcp_servers": {},
        "documents": [],
        "onboarding": {},
    }
    wizard = create_wizard(llm_client, settings, platform_state)
    assert wizard.name == "wizard"
    assert len(wizard.tools) >= 10


# ── Data classes ────────────────────────────────────────────────────────

def test_agent_context_defaults():
    ctx = AgentContext(tenant_id="t1", user_id="u1", task="do stuff")
    assert ctx.tenant_id == "t1"
    assert ctx.chat_id  # auto-generated UUID
    assert ctx.metadata == {}


def test_agent_result():
    r = AgentResult(success=True, output="done", agent="test")
    assert r.success
    assert r.artifacts == []
