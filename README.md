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
│  SPECIALIZED (5)                                                         │
│  ├── Influencer    ├── PR    ├── Events    ├── Localization             │
│  └── Accessibility                                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## External LLM Providers (13 Integrated)

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

# External LLMs (add as needed)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
XAI_API_KEY=xai-...
HIGGSFIELD_API_KEY=hf-...
REPLICATE_API_KEY=r8-...
STABILITY_API_KEY=sk-...
ELEVENLABS_API_KEY=...
PERPLEXITY_API_KEY=pplx-...
RUNWAY_API_KEY=...
BEAUTIFUL_AI_API_KEY=...
GAMMA_API_KEY=...
PRESENTON_BASE_URL=http://localhost:8080/api/v1
```

### 3. Run

```bash
uvicorn main:app --reload
```

API docs at http://localhost:8000/docs

## Quick Examples

### Execute an Agent

```bash
curl -X POST http://localhost:8000/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "image_agent",
    "input": "Create a product photo for sneakers",
    "instance_id": "tenant-123"
  }'
```

### Check Provider Status

```bash
curl http://localhost:8000/api/v1/providers/status
```

### Generate Image with Specific Provider

```python
from src.services.llm_clients import imagen_generate, grok_image

# Google Imagen (cheapest at $0.02)
images = await imagen_generate("Product photo of sneakers")

# xAI Aurora (good for text-in-image)
images = await grok_image("Sale banner with '50% OFF' text")
```

### Use Gemini for Cheap Classification

```python
from src.services.llm_clients import gemini_classify

intent = await gemini_classify(
    "I want to cancel my subscription",
    categories=["billing", "support", "sales", "other"]
)
# Cost: ~$0.0001 per classification
```

## Documentation

| Doc | Description |
|-----|-------------|
| [`docs/AGENTS.md`](docs/AGENTS.md) | Full agent ecosystem (46 agents) |
| [`docs/PROVIDERS.md`](docs/PROVIDERS.md) | External LLM setup guide (13 providers) |
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
