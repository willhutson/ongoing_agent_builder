# Chat Context Recovery File

Last updated: 2026-01-06

## Current Session Summary

Building a standalone API agent service for TeamLMTD ERP using **Claude Agent SDK**.

### Key Decisions Made

1. **Standalone service** - Not embedded in ERP, supports multi-tenant architecture
2. **Claude Agent SDK** - Python-based, using Anthropic client with agentic tool loop
3. **Core paradigm**: Think → Act → Create
4. **Maximum flexibility** - Agents can specialize by vertical, region, language, or client
5. **Moodboard as input** - Human-curated moodboards feed into creative agents as inspiration

### What's Been Built

```
ongoing_agent_builder/
├── main.py                 # FastAPI entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── .gitignore
├── README.md              # Architecture docs
├── CONTEXT.md             # This file (chat recovery)
├── docs/
│   └── AGENTS.md          # Full agent ecosystem directory (43+ agents)
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

### Agent Ecosystem (43+ Agents)

See `docs/AGENTS.md` for full details.

| Layer | Agents | Status |
|-------|--------|--------|
| **Foundation** | RFP, Brief, Content, Commercial | ✅ Built |
| **Brand** | Voice, Visual, Guidelines | Planned |
| **Studio** | Presentation, Copy (EN/AR/+), Image, Video (Script/Storyboard/Production) | Planned |
| **Distribution** | Report, Approve, Brief Update, WhatsApp Gateway | Planned |
| **Operations** | Resource, Workflow, Reporting | Planned |
| **Client** | CRM, Scope, Onboarding | Planned |
| **Media** | Media Buying, Campaign | Planned |
| **Social** | Listening, Community, Social Analytics | Planned |
| **Performance** | Brand Performance, Campaign Analytics, Competitor | Planned |
| **Finance** | Invoice, Forecast, Budget | Planned |
| **Quality** | QA, Legal | Planned |
| **Knowledge** | Knowledge, Training | Planned |
| **Influencer** | Base + vertical specializations (Beauty, Fashion, Food, Tech, etc.) | Planned |
| **PR** | Press Release, Media Outreach, Coverage | Planned |
| **Events** | Planning, Logistics, Attendee | Planned |
| **Localization** | Multi-market adaptation | Planned |
| **Accessibility** | WCAG compliance, alt text, captions | Planned |

### Key Architecture Decisions

#### Moodboard Flow
```
Human curates moodboard (canvas) → Moodboard saved → Agents consume as inspiration
                                                      ├── Copy Agent (tone)
                                                      ├── Image Agent (style)
                                                      ├── Video Agent (look/feel)
                                                      └── Presentation Agent (aesthetic)
```

#### Agent Specialization
```python
# Agents can be specialized by vertical, region, language, or client
InfluencerAgent(vertical="beauty", region="uae", language="ar")
CopyAgent(language="ar", client_id="client_123")
```

#### WhatsApp Architecture
```
Report Agent ────┐
Approve Agent ───┼──▶ WhatsApp Gateway ──▶ WhatsApp Business API
Brief Update ────┘
```

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

28 modules to support - see `docs/AGENTS.md` for full mapping.

### Completed This Session

- [x] Scaffold project structure
- [x] Define RFP Agent (5 tools)
- [x] Define Brief Agent (6 tools)
- [x] Define Content Agent (7 tools)
- [x] Define Commercial Agent (8 tools)
- [x] Design API contract
- [x] Plan full agent ecosystem (43+ agents)
- [x] Document agent directory

### Next Steps

1. [ ] Build Studio agents (Presentation, Copy, Image)
2. [ ] Build Distribution agents (WhatsApp)
3. [ ] Build Video pipeline (Script, Storyboard, Production)
4. [ ] Implement ERP API client with actual endpoints
5. [ ] Add authentication/tenant isolation
6. [ ] Docker containerization
7. [ ] Tests

### Tech Stack

- Python 3.11+
- FastAPI (async)
- **Claude Agent SDK** (Anthropic client with tool loop)
- httpx for async HTTP
- Pydantic for settings/validation
- Claude Opus 4.5 model

### User Preferences

- User: willhutson
- Prefers practical, working code over extensive planning
- Multi-tenant is critical (ERP designed for multiple instances)
- Wants agents to help "out of the box"
- Wants maximum flexibility for specialization

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
