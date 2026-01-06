# Ongoing Agent Builder

Standalone API agent service for [TeamLMTD ERP](https://github.com/willhutson/erp_staging_lmtd) - built on the **Claude Agent SDK**.

## Vision

A multi-tenant agent service that operates across all ERP instances, following the core paradigm:

```
THINK → ACT → CREATE
```

- **Think**: Analyze context, understand requirements, plan approach
- **Act**: Execute tools, query data, validate, iterate
- **Create**: Combine thinking + action into deliverables (documents, assets, recommendations)

### Flexibility First

Every agent can be specialized:
- **By Vertical**: Beauty, Fashion, Food, Tech, Finance, etc.
- **By Region**: UAE, KSA, US, UK, APAC, etc.
- **By Language**: English, Arabic, French, etc.
- **By Client**: Client-specific rules, voice, preferences

## Agent Ecosystem (43+ Agents)

> See [`docs/AGENTS.md`](docs/AGENTS.md) for the complete directory with tools and details.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AGENT ECOSYSTEM                                │
│                     Built on Claude Agent SDK                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FOUNDATION (4) ✅         BRAND (3)              STUDIO (7)             │
│  ├── RFP                   ├── Voice              ├── Presentation       │
│  ├── Brief                 ├── Visual             ├── Copy (multi-lang)  │
│  ├── Content               └── Guidelines         ├── Image              │
│  └── Commercial                                   └── Video (3 agents)   │
│                                                                          │
│  DISTRIBUTION (3+4)        OPERATIONS (3)         CLIENT (3)             │
│  ├── Report                ├── Resource           ├── CRM                │
│  ├── Approve               ├── Workflow           ├── Scope              │
│  ├── Brief Update          └── Reporting          └── Onboarding         │
│  └── Gateways: WhatsApp,                                                 │
│      Email, Slack, SMS                                                   │
│                                                                          │
│  MEDIA (2)                 SOCIAL (3)             PERFORMANCE (3)        │
│  ├── Media Buying          ├── Listening          ├── Brand Performance  │
│  └── Campaign              ├── Community          ├── Campaign Analytics │
│                            └── Social Analytics   └── Competitor         │
│                                                                          │
│  FINANCE (3)               QUALITY (2)            KNOWLEDGE (2)          │
│  ├── Invoice               ├── QA                 ├── Knowledge          │
│  ├── Forecast              └── Legal              └── Training           │
│  └── Budget                                                              │
│                                                                          │
│  INFLUENCER (1+)           PR (1)                 EVENTS (1)             │
│  └── Specializable by      └── Media Relations    └── Planning           │
│      vertical/region                                                     │
│                            LOCALIZATION (1+)      ACCESSIBILITY (1)      │
│                            └── Multi-market       └── WCAG Compliance    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              ERP Instances (Multi-Tenant)                   │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│    │ Tenant A │  │ Tenant B │  │ Tenant C │                │
│    └────┬─────┘  └────┬─────┘  └────┬─────┘                │
└─────────┼─────────────┼─────────────┼───────────────────────┘
          │             │             │
          └─────────────┼─────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              AGENT SERVICE (Standalone)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   REST API Layer                        │ │
│  │  POST /api/v1/agent/execute                            │ │
│  │  GET  /api/v1/agent/status/:id                         │ │
│  │  GET  /api/v1/agents                                   │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       ▼                                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Claude Agent SDK                           │ │
│  │  ┌─────────────────────────────────────────────────┐   │ │
│  │  │            Agent Loop (Orchestrator)             │   │ │
│  │  │  Think → Tool Selection → Execute → Feedback     │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  │                       │                                 │ │
│  │  ┌────────────────────▼────────────────────────────┐   │ │
│  │  │           43+ Specialized Agents                 │   │ │
│  │  │  (Foundation, Studio, Social, Media, etc.)      │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Status

### ✅ All 43 Agents Built

| Layer | Agents | Status |
|-------|--------|--------|
| **Foundation** | RFP, Brief, Content, Commercial | ✅ |
| **Studio** | Presentation, Copy (multi-lang), Image | ✅ |
| **Video** | Script, Storyboard, Production | ✅ |
| **Distribution** | Report, Approve, Brief Update | ✅ |
| **Gateways** | WhatsApp, Email, Slack, SMS | ✅ |
| **Brand** | Voice, Visual, Guidelines | ✅ |
| **Operations** | Resource, Workflow, Ops Reporting | ✅ |
| **Client** | CRM, Scope, Onboarding | ✅ |
| **Media** | Media Buying, Campaign | ✅ |
| **Social** | Listening, Community, Analytics | ✅ |
| **Performance** | Brand Performance, Campaign Analytics, Competitor | ✅ |
| **Finance** | Invoice, Forecast, Budget | ✅ |
| **Quality** | QA, Legal | ✅ |
| **Knowledge** | Knowledge, Training | ✅ |
| **Specialized** | Influencer, PR, Events, Localization, Accessibility | ✅ |

## Moodboard Integration

Moodboards are human-curated inspiration that feed into creative agents:

```
Human curates moodboard (canvas) → Moodboard saved → Agents consume as input
                                                      ├── Copy Agent (tone)
                                                      ├── Image Agent (style)
                                                      ├── Video Agent (look/feel)
                                                      └── Presentation Agent (aesthetic)
```

## Tech Stack

- **Runtime**: Python 3.11+
- **Agent Framework**: Claude Agent SDK (Anthropic)
- **API**: FastAPI (async)
- **Model**: Claude Opus 4.5
- **HTTP Client**: httpx (async)
- **Validation**: Pydantic
- **Deployment**: Containerized

## ERP Module Coverage (28 Total)

```
ai              briefs          builder         chat
complaints      content-engine  content         crm
dam             dashboard       delegation      files
forms           integrations    leave           notifications
nps             onboarding      reporting       resources
retainer        rfp             scope-changes   settings
studio          time-tracking   whatsapp        workflows
```

## Getting Started

```bash
# Clone
git clone https://github.com/willhutson/ongoing_agent_builder.git
cd ongoing_agent_builder

# Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Run
uvicorn main:app --reload

# API docs at http://localhost:8000/docs
```

## Documentation

- [`docs/AGENTS.md`](docs/AGENTS.md) - Full agent ecosystem directory (43+ agents)
- [`CONTEXT.md`](CONTEXT.md) - Session context recovery file

## Related

- [ERP Staging LMTD](https://github.com/willhutson/erp_staging_lmtd) - The ERP platform this service supports
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) - Agent framework
