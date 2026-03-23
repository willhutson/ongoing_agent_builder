# CLAUDE.md — Agent Builder Repo Guide

## Key Patterns

### Artifact Streaming
`stream()` needs `asyncio.Queue` + `_sse_callback` for artifact events to flow through SSE. Without this wiring, artifact events are silently dropped (fixed in PR #36).

When `artifact_format` is set, `tool_choice` is forced to `{"type": "tool", "name": "emit_artifact"}` to ensure structured artifact output (PR #37).

### Redis
Connected on Railway. Used for session state, rate limiting, and pub/sub for real-time events.

### Billing
All agent execution endpoints report usage to:
```
POST /api/v1/billing/usage/report
Header: X-Service-Key: <service_key>
```
Do NOT change billing rates or token pricing without explicit authorization.

### Deployment
- **Agent Builder URL**: https://ongoingagentbuilder-production.up.railway.app
- Agents live in the Agent Builder repo, NOT the ERP repo
- ERP calls Agent Builder via REST with HMAC-signed callbacks

## Architecture

### Two Agent Layers
1. **Production agents** (`src/agents/`): Full implementation with HTTP clients, ERP integration, browser automation. 50 agents registered in `src/services/agent_factory.py`.
2. **Module agents** (`modules/*/agents.py`): Lightweight BaseAgent subclasses for the research/strategy/operations modules. Tools return structured data for LLM analysis.

### Agent Factory (3-Tier)
- **Layer 1**: Core agent code from `AGENT_REGISTRY` in `agent_factory.py`
- **Layer 2**: Instance configuration from database (per-tenant)
- **Layer 3**: Custom skills from database (executed via webhook)

### Social Suite Data Flow
```
Observer Agent (collect from platforms)
    → Source Adapters (Twitter, Reddit, App Store, Google, News)
    → Normalized Mention/MentionBatch
    → Social Listening / Analytics / Competitor agents consume
    → Publisher Agent schedules and publishes content
```

### Artifact Protocol
Defined in `src/protocols/artifacts.py`. 20 artifact types with JSON schemas and standard actions. Social Suite added: `social_post`, `social_report`, `listening_report`.

Events flow: `artifact:create` → `artifact:update` → `artifact:complete` via SSE.

## File Locations

| What | Where |
|------|-------|
| Production agents | `src/agents/*.py` |
| Agent registry | `src/agents/__init__.py` |
| Agent factory | `src/services/agent_factory.py` |
| ERP tier map | `src/api/erp_integration.py` |
| Artifact types | `src/protocols/artifacts.py` |
| Module agents | `modules/*/agents.py` |
| Observer + adapters | `modules/research/observer_agent.py`, `source_adapters.py` |
| Module tests | `modules/tests/test_agents.py` |
| Pricing config | `src/services/llm_clients/pricing_config.json` |

## Testing

```bash
# Module agent tests (research, foundation, etc.)
cd modules && python -m pytest tests/test_agents.py -v

# Syntax check all files
python -c "import ast; ast.parse(open('path/to/file.py').read())"
```

## Conventions

- Agent class names: `CamelCaseAgent` (e.g., `PublisherAgent`)
- Registry keys: `snake_case` (e.g., `publisher`)
- Agent `.name` property: `snake_case_agent` (e.g., `publisher_agent`)
- Tools: dict with `name`, `description`, `input_schema` (JSON Schema object)
- Tool execution: `async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any`
- ERP integration: `httpx.AsyncClient` with Bearer auth, 60s timeout
- LLM-based tools: Return structured dict with `instruction` field for the agent loop
