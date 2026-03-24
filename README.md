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

## Agent Ecosystem (50 Agents)

> See [`docs/AGENTS.md`](docs/AGENTS.md) for the complete directory with tools and details.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AGENT ECOSYSTEM                                │
│                     Built on Claude Agent SDK                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FOUNDATION (4)              BRAND (3)               STUDIO (7)          │
│  ├── RFP                     ├── Voice               ├── Presentation    │
│  ├── Brief                   ├── Visual              ├── Copy            │
│  ├── Content                 └── Guidelines          ├── Image           │
│  └── Commercial                                      └── Video (3)       │
│                                                                          │
│  DISTRIBUTION (3+4)          OPERATIONS (3)          CLIENT (6)          │
│  ├── Report                  ├── Resource            ├── CRM             │
│  ├── Approve                 ├── Workflow            ├── Scope           │
│  ├── Brief Update            └── Reporting           ├── Onboarding      │
│  └── Gateways (4)                                    └── Instance (3)    │
│                                                                          │
│  MEDIA (2)                   SOCIAL (3)              PERFORMANCE (3)     │
│  ├── Media Buying            ├── Listening           ├── Brand           │
│  └── Campaign                ├── Community           ├── Campaign        │
│                              └── Analytics           └── Competitor      │
│                                                                          │
│  FINANCE (3)                 QUALITY (2)             KNOWLEDGE (2)       │
│  ├── Invoice                 ├── QA                  ├── Knowledge       │
│  ├── Forecast                └── Legal               └── Training        │
│  └── Budget                                                              │
│                                                                          │
│  SPECIALIZED (5)             META (1) ⭐ NEW                              │
│  ├── Influencer              └── PromptHelper        Skills Library      │
│  ├── PR                          (helps craft        ├── 40+ skills      │
│  ├── Events                       better prompts)    ├── Positioning     │
│  ├── Localization                                    └── Frameworks      │
│  └── Accessibility                                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## New: Integration Services

### AgentManager
Central orchestration for the agent ecosystem:
- Agent discovery and recommendations
- Multi-agent workflow support
- Usage analytics and monitoring
- Economy/Standard/Premium tier mapping

### PromptHelper Agent
Meta-agent that helps users craft better prompts:
- Knows all 47 agents and 14 LLM providers
- Suggests optimal agents for tasks
- Analyzes and improves prompts
- Provides cost-aware provider recommendations

### Skills Library
40+ invokable marketing skills:
- Organized by ERP module (Video, Analytics, Brand, etc.)
- Positioning frameworks and value prop formulas
- Brainstorm mode with frameworks injected

> See [`docs/ERP_STAGING_INTEGRATION.md`](docs/ERP_STAGING_INTEGRATION.md) for full integration details.

## New: ERP Toolkit (Live Data Access)

Real HTTP access to ERP module data, replacing mock tool calls with actual API requests.

- **16 async methods** via `ERPToolkit` (10 read, 6 write) using `httpx.AsyncClient`
- **8 read tools** injected into ALL agents via `BaseAgent`: `get_client_context`, `list_briefs`, `list_content_posts`, `list_projects`, `get_analytics`, `get_pending_reviews`, `get_workload`, `search_modules`
- **5 write tools** selectively injected per agent type via `AGENT_WRITE_TOOL_MAP`: `create_brief`, `create_content_posts`, `create_project`, `schedule_post`, `create_media_plan`
- Canvas context injection for multi-step workflows
- Auth: `X-API-Key` header (service-to-service), `X-Organization-Id` / `X-User-Id` per request

```
src/tools/erp_toolkit.py          ← ERPToolkit class (16 async HTTP methods)
src/tools/erp_tool_definitions.py ← OpenAI-format tool schemas + AGENT_WRITE_TOOL_MAP
```

| Env Var | Required | Description |
|---------|----------|-------------|
| `SPOKESTACK_ERP_URL` | Yes | Base URL of the ERP service API |
| `SPOKESTACK_SERVICE_KEY` | Yes | Service-to-service API key |

## New: Creative Production Pipeline

AI-powered creative asset generation with provider fallback chains and quality tiers.

- **CreativeRegistry** routes requests to the cheapest available provider per `(asset_type, quality_tier)`
- **4 providers**: FalProvider (Wan/Kling/Flux/Seedream), OpenAICreativeProvider (GPT Image/TTS), ElevenLabsProvider (Flash/Multilingual v2), BeautifulAIProvider
- **5 creative tools**: `generate_image`, `generate_video`, `generate_voiceover`, `generate_presentation`, `generate_video_composition`
- **3 quality tiers**: DRAFT (cheapest), STANDARD, PREMIUM — agents request a tier, registry picks the provider
- Selective injection via `AGENT_CREATIVE_TOOL_MAP` (e.g. `video_production` gets all 4 tools, `image` gets only `generate_image`)

```
src/providers/creative_registry.py           ← CreativeRegistry + provider ABC
src/providers/creative/fal_provider.py       ← Fal (Flux, Seedream, Wan, Kling)
src/providers/creative/openai_creative_provider.py ← GPT Image 1 + TTS
src/providers/creative/elevenlabs_provider.py      ← ElevenLabs voice
src/providers/creative/beautiful_provider.py       ← Beautiful.ai presentations
src/tools/creative_tool_definitions.py       ← Tool schemas + AGENT_CREATIVE_TOOL_MAP
```

### Creative Cost Reference

| Asset | Draft | Standard | Premium |
|-------|-------|----------|---------|
| **Image** | $0.003 (Flux Schnell) | $0.02 (Seedream) | $0.04–0.05 (GPT Image 1 / Flux Pro) |
| **Video** | $0.30 (Wan 2.5) | $0.50 (Kling Turbo) | $1.00 (Kling Pro) |
| **Voice** | $0.003 (OpenAI TTS) | $0.015/1k chars (ElevenLabs Flash) | $0.03/1k chars (ElevenLabs Multilingual) |
| **Presentation** | ~$1.00 (10 slides) | ~$1.00 | ~$1.00 |

| Env Var | Required | Description |
|---------|----------|-------------|
| `FAL_API_KEY` | Yes (for image/video) | fal.ai API key |
| `ELEVENLABS_API_KEY` | Yes (for premium voice) | ElevenLabs API key |
| `BEAUTIFUL_AI_API_KEY` | Optional | Beautiful.ai API key |
| `RUNWAY_API_KEY` | Optional | Runway API key (future) |

## External LLM Providers (14 Integrated)

Agents use Claude for reasoning + specialized external LLMs for capabilities Claude lacks:

> See [`docs/PROVIDERS.md`](docs/PROVIDERS.md) for setup instructions and [`docs/PRICING.md`](docs/PRICING.md) for cost details.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL LLM PROVIDERS                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  VIDEO                        IMAGE                   VOICE              │
│  ├── Higgsfield (12 models)   ├── OpenAI DALL-E 3    ├── ElevenLabs     │
│  │   Sora 2, Veo 3, Kling,    ├── Replicate Flux     ├── Google TTS     │
│  │   WAN, Minimax, Luma...    ├── Stability AI       └── OpenAI TTS     │
│  └── Runway Gen-3             ├── xAI Aurora                            │
│                               └── Google Imagen 3                       │
│                                                                          │
│  RESEARCH                     VISION/ANALYTICS       PRESENTATIONS      │
│  ├── Perplexity (search)      ├── Google Gemini      ├── Presenton      │
│  └── xAI Grok (real-time X)   │   Vision (2M ctx)    ├── Gamma          │
│                               └── OpenAI GPT-4V      └── Beautiful.ai   │
│                                                                          │
│  ROUTING (ultra-cheap)                                                   │
│  └── Google Gemini Flash (50x cheaper than GPT-4o)                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Module → Provider Mapping

| Module | Agents | External Providers |
|--------|--------|-------------------|
| **Video** | video_production, video_storyboard, video_script | Higgsfield, Runway, ElevenLabs |
| **Studio** | image, brand_visual, presentation | DALL-E, Flux, Stability, Aurora, Imagen, Presenton, Gamma |
| **Voice** | copy, brand_voice, localization, accessibility | ElevenLabs, Google TTS, OpenAI TTS/Whisper |
| **Research** | social_listening, competitor, pr, influencer, rfp | Perplexity, Grok (real-time X) |
| **Analytics** | social_analytics, campaign_analytics, brand_performance, qa | Google Gemini Vision |
| **Distribution** | report, ops_reporting, community | Gamma, Presenton, DALL-E |
| **High-Stakes** | legal, finance, clients, knowledge | Claude Opus 4.5 (no external) |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ERP Instances (Multi-Tenant)                          │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│    │ Tenant A │  │ Tenant B │  │ Tenant C │  │    ...   │              │
│    └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└─────────┼─────────────┼─────────────┼─────────────┼─────────────────────┘
          └─────────────┼─────────────┼─────────────┘
                        ▼             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     AGENT SERVICE (Standalone)                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        REST API Layer                              │  │
│  │  POST /api/v1/agent/execute    GET /api/v1/agents                 │  │
│  │  GET  /api/v1/agent/status/:id GET /api/v1/providers/status       │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                  │                                       │
│  ┌───────────────────────────────▼───────────────────────────────────┐  │
│  │                    Claude Agent SDK                                │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │              Agent Loop (Orchestrator)                       │  │  │
│  │  │      Think → Tool Selection → Execute → Feedback → Loop      │  │  │
│  │  └─────────────────────────────────────────────────────────────┘  │  │
│  │                                │                                   │  │
│  │  ┌─────────────────────────────▼─────────────────────────────────┐│  │
│  │  │                  46 Specialized Agents                         ││  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         ││  │
│  │  │  │Foundation│ │  Studio  │ │  Social  │ │  Media   │   ...   ││  │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         ││  │
│  │  └────────────────────────────────────────────────────────────────┘│  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                       │
│  ┌───────────────────────────────▼───────────────────────────────────┐  │
│  │                      ERP Toolkit (Live Data)                       │  │
│  │  8 read tools (all agents) + 5 write tools (selective injection)   │  │
│  │  httpx → ERP Service API (X-API-Key auth, multi-tenant headers)    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                       │
│  ┌───────────────────────────────▼───────────────────────────────────┐  │
│  │                Creative Production Pipeline                        │  │
│  │  CreativeRegistry → fallback chains per (asset_type, quality_tier) │  │
│  │  ┌─────────┐ ┌─────────┐ ┌───────────┐ ┌──────────────┐          │  │
│  │  │ fal.ai  │ │ OpenAI  │ │ElevenLabs │ │Beautiful.ai  │          │  │
│  │  │Flux/Wan/│ │GPT Img/ │ │Flash/ML v2│ │presentations │          │  │
│  │  │Kling    │ │  TTS    │ │  voice    │ │              │          │  │
│  │  └─────────┘ └─────────┘ └───────────┘ └──────────────┘          │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                       │
│  ┌───────────────────────────────▼───────────────────────────────────┐  │
│  │                   External LLM Clients                             │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │  │
│  │  │Higgsfield│ │ OpenAI  │ │ Google  │ │   xAI   │ │Perplexity│    │  │
│  │  │ (video) │ │(img/tts)│ │(all-in-1)│ │(social) │ │(research)│    │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘     │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Model Tiers

| Tier | Model | Cost | Use Case |
|------|-------|------|----------|
| **Premium** | Claude Opus 4.5 | $15/M in, $75/M out | Legal, Finance, Clients, Knowledge |
| **Standard** | Claude Sonnet 4 | $3/M in, $15/M out | Most agents |
| **Fast** | Claude Haiku 3.5 | $0.25/M in, $1.25/M out | Simple tasks |
| **Routing** | Gemini Flash | $0.10/M in, $0.40/M out | Intent classification |
| **Social** | Grok 2 | $2/M in, $10/M out | Real-time X/Twitter |

## Credit-Based Pricing

SpokeStack uses a credit system for client billing:

| Plan | Price | Credits | Best For |
|------|-------|---------|----------|
| **Starter** | $49/mo | 2,000 | Solo users |
| **Brand** | $199/mo | 10,000 | Mid-size brands |
| **Agency** | $499/mo | 35,000 | Agencies |
| **Enterprise** | $1,499/mo | 150,000 | Enterprise |

> See [`docs/PRICING.md`](docs/PRICING.md) for full cost breakdown and margin analysis.

## Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/willhutson/ongoing_agent_builder.git
cd ongoing_agent_builder
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# ERP Toolkit (live data access)
SPOKESTACK_ERP_URL=https://your-erp-instance.com
SPOKESTACK_SERVICE_KEY=your-service-key

# External LLMs (add as needed)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
XAI_API_KEY=xai-...
HIGGSFIELD_API_KEY=hf-...
REPLICATE_API_KEY=r8-...
STABILITY_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
GAMMA_API_KEY=...
PRESENTON_BASE_URL=http://localhost:8080/api/v1

# Creative Production Pipeline
FAL_API_KEY=...
ELEVENLABS_API_KEY=...
BEAUTIFUL_AI_API_KEY=...
RUNWAY_API_KEY=...          # optional, future
```

### 3. Run

```bash
uvicorn main:app --reload
```

API docs at http://localhost:8000/docs

## Quick Examples

### Execute an Agent (ERP Integration)

```bash
# POST /api/v1/agent/execute - Execute an agent with ERP context
curl -X POST http://localhost:8000/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -H "X-Organization-Id: tenant-123" \
  -d '{
    "agent": "brief",
    "task": "Create a campaign brief for a luxury watch launch",
    "model": "claude-sonnet-4-20250514",
    "tier": "standard",
    "tenant_id": "tenant-123",
    "user_id": "user-456",
    "session_id": "session-789",
    "context": {"client": "luxury_brand"}
  }'
```

### Chat with Agent (Session-based)

```bash
# POST /api/v1/agent/chat - Chat with an agent
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "instance_onboarding",
    "message": "We are a mid-sized creative agency with 25 employees",
    "tenant_id": "tenant-123",
    "user_id": "user-456"
  }'

# GET /api/v1/agent/chat/{session_id} - Get chat history
curl http://localhost:8000/api/v1/agent/chat/session-abc
```

### Check Health & Provider Status

```bash
# GET /api/v1/health - Health check with provider latency
curl http://localhost:8000/api/v1/health

# Response:
# {
#   "status": "healthy",
#   "agents_available": 46,
#   "providers": [{"provider": "anthropic", "status": "healthy", "latency_ms": 50}, ...]
# }
```

### Get Agent Registry

```bash
# GET /api/v1/agents/registry - All 46 agents with tier annotations
curl http://localhost:8000/api/v1/agents/registry

# Response includes agents organized by layer with tier info:
# {
#   "total_agents": 46,
#   "layers": {
#     "foundation": {"agents": [{"type": "rfp", "tier": "standard"}, ...]}
#   }
# }
```

## Documentation

| Doc | Description |
|-----|-------------|
| [`docs/AGENTS.md`](docs/AGENTS.md) | Full agent ecosystem (47 agents) |
| [`docs/PROVIDERS.md`](docs/PROVIDERS.md) | External LLM setup guide (14 providers) |
| [`docs/ERP_STAGING_INTEGRATION.md`](docs/ERP_STAGING_INTEGRATION.md) | Integration guide for SpokeStack ERP |
| [`docs/PRICING.md`](docs/PRICING.md) | Cost breakdown and margin analysis |
| [`docs/API.md`](docs/API.md) | LLM clients API reference |
| [`docs/TRAINING_SPEC.md`](docs/TRAINING_SPEC.md) | Training program specification |

## Tech Stack

- **Runtime**: Python 3.11+
- **Agent Framework**: Claude Agent SDK (Anthropic)
- **Primary Model**: Claude Sonnet 4 / Opus 4.5
- **API**: FastAPI (async)
- **HTTP Client**: httpx (async)
- **Validation**: Pydantic
- **Config**: JSON-driven pricing (`pricing_config.json`)

## Related

- [ERP Staging LMTD](https://github.com/willhutson/erp_staging_lmtd) - The ERP platform this service supports
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) - Agent framework
