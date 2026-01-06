# Chat Context Recovery File

Last updated: 2026-01-06

## Current Session Summary

Building a standalone API agent service for TeamLMTD ERP using Claude Agent SDK patterns.

### Key Decisions Made

1. **Standalone service** - Not embedded in ERP, supports multi-tenant architecture
2. **Claude SDK patterns** - Python-based, using Anthropic client with agentic tool loop
3. **Core paradigm**: Think → Act → Create
4. **Priority capabilities**:
   - RFP processing (analyze, extract requirements, draft responses)
   - Brief intake (AI-assisted creation)
   - Document generation (proposals, SOWs, reports)
   - Draft assets (creative starting points for teams)

### What's Been Built

```
ongoing_agent_builder/
├── main.py                 # FastAPI entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── .gitignore
├── README.md              # Architecture docs
├── CONTEXT.md             # This file (chat recovery)
└── src/
    ├── config.py          # Pydantic settings
    ├── agents/
    │   ├── base.py        # BaseAgent (Think→Act→Create loop)
    │   └── rfp_agent.py   # RFP Agent with 5 tools
    ├── api/
    │   └── routes.py      # REST API endpoints
    └── tools/             # (placeholder for shared tools)
```

### API Endpoints (Implemented)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agent/execute` | Run agent (sync or streaming) |
| GET | `/api/v1/agent/status/:id` | Poll task status |
| DELETE | `/api/v1/agent/task/:id` | Cancel task |
| GET | `/api/v1/agents` | List available agents |
| GET | `/api/v1/health` | Health check |

### RFP Agent Tools

1. `query_past_projects` - Search ERP for relevant case studies
2. `get_team_capabilities` - Fetch team skills/expertise
3. `get_client_history` - Check CRM for past relationship
4. `create_proposal_draft` - Save draft to ERP
5. `analyze_document` - Extract requirements from RFP docs

### ERP Integration Points

Target repo: https://github.com/willhutson/erp_staging_lmtd

28 modules to support (see README.md for full list)

Agent-ready hooks already in ERP:
- `.claude/commands` directory
- `/knowledge/agents/skills` folder

### Completed This Session

- [x] Scaffold project structure
- [x] Define first agent (RFP Agent)
- [x] Design API contract/spec

### Next Steps

1. [ ] Add Brief Agent
2. [ ] Add Content Agent
3. [ ] Implement ERP API client with actual endpoints
4. [ ] Add authentication/tenant isolation
5. [ ] Docker containerization
6. [ ] Tests

### Tech Stack

- Python 3.11+
- FastAPI (async)
- Anthropic SDK (direct client with tool loop)
- httpx for async HTTP
- Pydantic for settings/validation
- Claude Opus 4.5 model

### User Preferences

- User: willhutson
- Prefers practical, working code over extensive planning
- Multi-tenant is critical (ERP designed for multiple instances)
- Wants agents to help "out of the box"

---

## How to Run

```bash
# Install deps
pip install -r requirements.txt

# Copy and configure env
cp .env.example .env
# Edit .env with your API keys

# Run
python main.py
# or
uvicorn main:app --reload

# API docs at http://localhost:8000/docs
```

---

## How to Use This File

If chat is lost, new session can read this file to understand:
- What we're building
- Decisions already made
- Where we left off
- What to do next

Update this file before ending sessions or after major decisions.
