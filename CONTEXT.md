# Chat Context Recovery File

Last updated: 2026-01-06

## Current Session Summary

Building a standalone API agent service for TeamLMTD ERP using Claude Agent SDK.

### Key Decisions Made

1. **Standalone service** - Not embedded in ERP, supports multi-tenant architecture
2. **Claude Agent SDK** - Python-based, using in-process MCP tools
3. **Core paradigm**: Think → Act → Create
4. **Priority capabilities**:
   - RFP processing (analyze, extract requirements, draft responses)
   - Brief intake (AI-assisted creation)
   - Document generation (proposals, SOWs, reports)
   - Draft assets (creative starting points for teams)

### ERP Integration Points

Target repo: https://github.com/willhutson/erp_staging_lmtd

28 modules to eventually support:
- ai, briefs, builder, chat, complaints, content-engine, content, crm
- dam, dashboard, delegation, files, forms, integrations, leave, notifications
- nps, onboarding, reporting, resources, retainer, rfp, scope-changes, settings
- studio, time-tracking, whatsapp, workflows

Agent-ready hooks already in ERP:
- `.claude/commands` directory
- `/knowledge/agents/skills` folder

### Next Steps (In Progress)

1. [ ] Scaffold project structure (main.py, requirements.txt, folders)
2. [ ] Define first agent (RFP or Brief)
3. [ ] Design API contract/spec

### Tech Stack

- Python 3.11+
- FastAPI (async)
- Claude Agent SDK (`claude-agent-sdk`)
- Claude Opus 4.5 model
- In-process MCP tools
- Containerized deployment

### Architecture Pattern

```
ERP Instances → REST API → Claude Agent SDK → Orchestrator → Subagents → MCP Tools → Back to ERP
```

### User Preferences

- User: willhutson
- Prefers practical, working code over extensive planning
- Multi-tenant is critical (ERP designed for multiple instances)
- Wants agents to help "out of the box"

---

## How to Use This File

If chat is lost, new session can read this file to understand:
- What we're building
- Decisions already made
- Where we left off
- What to do next

Update this file before ending sessions or after major decisions.
