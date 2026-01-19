# Ongoing Agent Builder

Standalone API agent service for [SpokeStack](https://github.com/willhutson/erp_staging_lmtd) - built on the **Claude Agent SDK**.

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

## Agent Ecosystem (46 Agents)

> See [`docs/AGENTS.md`](docs/AGENTS.md) for the complete directory with tools and details.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AGENT ECOSYSTEM                                │
│                     Built on Claude Agent SDK                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FOUNDATION (4) ✅         BRAND (3) ✅           STUDIO (7) ✅          │
│  ├── RFP                   ├── Voice              ├── Presentation       │
│  ├── Brief                 ├── Visual             ├── Copy (multi-lang)  │
│  ├── Content               └── Guidelines         ├── Image              │
│  └── Commercial                                   └── Video (3 agents)   │
│                                                                          │
│  DISTRIBUTION (3+4) ✅     OPERATIONS (3) ✅      CLIENT (6) ✅          │
│  ├── Report                ├── Resource           ├── CRM                │
│  ├── Approve               ├── Workflow           ├── Scope              │
│  ├── Brief Update          └── Reporting          ├── Onboarding         │
│  └── Gateways: WhatsApp,                          ├── Instance Onboarding│
│      Email, Slack, SMS                            ├── Instance Analytics │
│                                                   └── Instance Success   │
│  MEDIA (2) ✅              SOCIAL (3) ✅          PERFORMANCE (3) ✅     │
│  ├── Media Buying          ├── Listening          ├── Brand Performance  │
│  └── Campaign              ├── Community          ├── Campaign Analytics │
│                            └── Social Analytics   └── Competitor         │
│                                                                          │
│  FINANCE (3) ✅            QUALITY (2) ✅         KNOWLEDGE (2) ✅       │
│  ├── Invoice               ├── QA                 ├── Knowledge          │
│  ├── Forecast              └── Legal              └── Training           │
│  └── Budget                                                              │
│                                                                          │
│  INFLUENCER (1+) ✅        PR (1) ✅              EVENTS (1) ✅          │
│  └── Specializable by      └── Media Relations    └── Planning           │
│      vertical/region                                                     │
│                            LOCALIZATION (1+) ✅   ACCESSIBILITY (1) ✅   │
│                            └── Multi-market       └── WCAG Compliance    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Instance Lifecycle

Three agents manage the complete ERP instance lifecycle:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        INSTANCE LIFECYCLE                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────┐                                                  │
│  │ INSTANCE ONBOARDING│  New tenant setup                                │
│  │      (32 tools)    │  ├── Business assessment & module selection      │
│  │                    │  ├── Infrastructure provisioning (DB, storage)   │
│  │                    │  ├── Platform credentials (Google Ads, Meta...)  │
│  │                    │  ├── SSO/Auth configuration                      │
│  │                    │  └── Sample data generation for demos            │
│  └─────────┬──────────┘                                                  │
│            │ handoff                                                     │
│            ▼                                                             │
│  ┌────────────────────┐                                                  │
│  │  INSTANCE SUCCESS  │  Ongoing success management                      │
│  │      (33 tools)    │  ├── Health monitoring & proactive outreach      │
│  │                    │  ├── Churn risk detection & intervention         │
│  │                    │  ├── Feature recommendations & training          │
│  │                    │  ├── Expansion opportunity identification        │
│  │                    │  └── QBR preparation & renewal management        │
│  └─────────┬──────────┘                                                  │
│            │ data                                                        │
│            ▼                                                             │
│  ┌────────────────────┐                                                  │
│  │ INSTANCE ANALYTICS │  Platform intelligence                           │
│  │      (25 tools)    │  ├── Usage metrics (DAU/MAU, sessions, API)      │
│  │                    │  ├── Health scoring & benchmarking               │
│  │                    │  ├── Anomaly detection & alerting                │
│  │                    │  ├── Growth forecasting & capacity planning      │
│  │                    │  └── ROI calculation & executive reporting       │
│  └────────────────────┘                                                  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
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
│  │  │           46 Specialized Agents                  │   │ │
│  │  │  (Foundation, Studio, Social, Media, etc.)      │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Status

### ✅ All 46 Agents Built

| Layer | Agents | Status |
|-------|--------|--------|
| **Foundation** | RFP, Brief, Content, Commercial | ✅ |
| **Studio** | Presentation, Copy (multi-lang), Image | ✅ |
| **Video** | Script, Storyboard, Production | ✅ |
| **Distribution** | Report, Approve, Brief Update | ✅ |
| **Gateways** | WhatsApp, Email, Slack, SMS | ✅ |
| **Brand** | Voice, Visual, Guidelines | ✅ |
| **Operations** | Resource, Workflow, Ops Reporting | ✅ |
| **Client** | CRM, Scope, Onboarding, Instance Onboarding, Instance Analytics, Instance Success | ✅ |
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

- [`docs/AGENTS.md`](docs/AGENTS.md) - Full agent ecosystem directory (46 agents)
- [`docs/TRAINING_SPEC.md`](docs/TRAINING_SPEC.md) - Comprehensive training program specification
- [`CONTEXT.md`](CONTEXT.md) - Session context recovery file

## Related

- [ERP Staging LMTD](https://github.com/willhutson/erp_staging_lmtd) - The ERP platform this service supports
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) - Agent framework
