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
   - Commercial/pricing intelligence (learn from past RFP pricing outcomes)

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
    │   ├── base.py            # BaseAgent (Think→Act→Create loop)
    │   ├── rfp_agent.py       # RFP Agent (5 tools)
    │   ├── brief_agent.py     # Brief Agent (6 tools)
    │   ├── content_agent.py   # Content Agent (7 tools)
    │   └── commercial_agent.py # Commercial Agent (8 tools)
    ├── api/
    │   └── routes.py      # REST API endpoints
    └── tools/             # (placeholder for shared tools)
```

### Agents Implemented

| Agent | Tools | Purpose |
|-------|-------|---------|
| **RFP Agent** | 5 | Analyze RFPs, extract requirements, draft proposals |
| **Brief Agent** | 6 | Parse briefs, find similar work, generate clarifying questions |
| **Content Agent** | 7 | Generate documents, presentations, reports from templates |
| **Commercial Agent** | 8 | Pricing intelligence from past RFP → negotiation → contract data |

### Commercial Agent (Pricing Intelligence)

Key workflow:
1. Upload historical data: RFP + submitted commercial + negotiated contract
2. Agent learns pricing patterns by industry/scope/client type
3. For new RFPs: suggests pricing based on similar past outcomes
4. Tracks win/loss rates by pricing strategy

Tools:
- `search_similar_commercials` - Find past pricing + outcomes
- `get_pricing_history` - Client/service patterns
- `calculate_estimate` - Build estimates with margin targets
- `get_win_rate_analysis` - Win/loss by strategy
- `create_commercial_document` - Save pricing proposals

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agent/execute` | Run agent (sync or streaming) |
| GET | `/api/v1/agent/status/:id` | Poll task status |
| DELETE | `/api/v1/agent/task/:id` | Cancel task |
| GET | `/api/v1/agents` | List available agents + tools |
| GET | `/api/v1/health` | Health check |

### ERP Integration Points

Target repo: https://github.com/willhutson/erp_staging_lmtd

28 modules to support (see README.md for full list)

### Completed This Session

- [x] Scaffold project structure
- [x] Define RFP Agent
- [x] Design API contract
- [x] Add Brief Agent
- [x] Add Content Agent
- [x] Add Commercial Agent (pricing intelligence)

### Next Steps

1. [ ] Implement ERP API client with actual endpoints
2. [ ] Add authentication/tenant isolation
3. [ ] Add Resource Agent
4. [ ] Docker containerization
5. [ ] Tests
6. [ ] Historical data import for Commercial Agent training

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
