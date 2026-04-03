# Cross-Repo Verification — April 3, 2026

## Status: All Three Repos Aligned

### spokestack-core (main)
- 6 comms module pages deployed (Media Relations, Press Releases, Crisis Comms, Client Reporting, Influencer Mgmt, Events)
- Phase 11 CLI merged (setup, seed, dev, deploy, non-interactive flags)
- Runtime fix merged (all routes hit `/api/v1/core/execute`)
- Env vars: `AGENT_RUNTIME_URL`, `AGENT_RUNTIME_SECRET`

### spokestack-modules (main)
- 38 modules with manifests (4 core + 19 marketplace + 3 engagement + 6 extended + 6 comms)
- 13 suite definitions (16+ industry verticals)
- 309 tests passing
- SDK: factory, registration, discovery, hooks, agent execution

### ongoing_agent_builder (main)
- PR #54 merged: 6 PR/comms agents (media_relations_manager, press_release_writer, crisis_manager, client_reporter, influencer_manager, event_planner)
- 32 new CRUD tools for comms agents
- MC translation map updated for all 6 comms types
- 204 tests passing, CI green

---

## Alignment Verification

### API Path: ALIGNED
- Core sends to: `${AGENT_RUNTIME_URL}/api/v1/core/execute`
- Agent builder exposes: `core_router` prefix `/api/v1/core` + `@router.post("/execute")`

### Auth Headers: ALIGNED
- Core sends: `X-Agent-Secret: ${AGENT_RUNTIME_SECRET}`
- Agent builder checks: `Header(alias="X-Agent-Secret")` against `AGENT_RUNTIME_SECRET` env var

### Request Body: ALIGNED
- Core sends: `{ agent_type, task, org_id, user_id, stream }`
- Agent builder accepts: `CoreExecuteRequest(task, agent_type, org_id, tenant_id, user_id, stream, ...)`
- `org_id`/`tenant_id` both accepted with fallback

### Agent Type Translation: MOSTLY ALIGNED
- 6 comms agents: ALIGNED (module-media-relations-assistant → media_relations_manager, etc.)
- Core marketplace agents: 14 of 23 have explicit MC translations
- 9 marketplace types missing from translation map (fall through as-is):
  - module-access-control-assistant
  - module-boards-assistant
  - module-builder-assistant
  - module-client-portal-assistant
  - module-delegation-assistant
  - module-listening-assistant
  - module-nps-assistant
  - module-spokechat-assistant
  - module-workflows-assistant
- **Impact:** These 9 would fail agent resolution. Should map to `assistant` as fallback.
- **Fix:** Add 9 entries to `MC_TO_CANONICAL_MAP` in agent_registry.py mapping to `"assistant"`

---

## The New Module Framework Pattern

This is the first successful end-to-end module deployment:

```
1. spokestack-modules: Define module manifest (metadata, agent type, tools)
   └── modules/media-relations/manifest.json
   └── modules/media-relations/agent.json (tools + system prompt ref)

2. spokestack-core: Create module page (UI with tabs)
   └── src/app/(dashboard)/media-relations/page.tsx
   └── MC router maps module-media-relations-assistant → agent builder

3. ongoing_agent_builder: Register agent class + tools
   └── src/agents/pr_comms_agents.py (agent classes with system prompts)
   └── src/tools/spokestack_crud_tools.py (CRUD tools against core's API)
   └── src/services/agent_tool_assignment.py (which tools each agent gets)
   └── src/services/agent_registry.py (MC translation + metadata)

4. Runtime: Module installed → user clicks "Ask Agent" → 
   core sends MC type → agent builder translates → 
   executes with tools → tools call back to core's API → 
   results streamed back to user
```

### Key Files Per Repo

**spokestack-modules** (define):
- `modules/{name}/manifest.json` — module metadata
- `sdk/factory/index.ts` — `createModule()` factory
- `sdk/registration/index.ts` — `registerModule()` two-step registration

**spokestack-core** (serve):
- `src/app/(dashboard)/{name}/page.tsx` — module UI page
- `src/lib/mission-control/mc-router.ts` — MC type mapping
- `src/lib/agents/types.ts` — agent type definitions
- `src/app/api/v1/{entity}/route.ts` — CRUD API the agents call

**ongoing_agent_builder** (think):
- `src/agents/{name}_agents.py` — agent classes with system prompts
- `src/tools/spokestack_crud_tools.py` — CRUD tool definitions
- `src/services/agent_tool_assignment.py` — agent → tool mapping
- `src/services/agent_registry.py` — MC translation + metadata

---

## PRs Merged This Session

| # | Repo | Title |
|---|------|-------|
| 9 | spokestack-core | Phase 10A: MC orchestration, agent types, create forms |
| 10 | spokestack-core | Fix: connect API routes to agent builder |
| 11 | spokestack-core | Phase 11: CLI (setup, seed, dev, deploy, non-interactive) |
| — | spokestack-core | 6 comms module pages (direct to main) |
| — | spokestack-core | Settings integrations fix + onboarding nudge |
| 3 | spokestack-modules | Phase 10C: Module SDK |
| — | spokestack-modules | 38 modules + 13 suites (direct to main) |
| 51 | ongoing_agent_builder | Phase 10B: canonical registry + core alignment |
| 53 | ongoing_agent_builder | Tool execution bridge |
| 54 | ongoing_agent_builder | PR/comms agents (6 types, 32 tools) |
