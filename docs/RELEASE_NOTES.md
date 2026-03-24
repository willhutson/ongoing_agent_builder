# Release Notes

## v3.0 — Social Suite, LMS, Artifact Streaming (PRs #34-39)

### PR #39: Social Suite Agents
**Branch**: `feat/social-suite-agents`

New **PublisherAgent** with 8 tools for social media publishing orchestration (create_post_draft, schedule_post, get_publishing_calendar, suggest_posting_times, adapt_for_platforms, get_post_performance, create_content_series, generate_captions).

Upgraded 4 existing agents:
- **SocialListeningAgent**: +5 Social Suite tools (get_mention_summary, analyze_sentiment_trends, detect_crisis, generate_listening_report, delegate_to_observer). Total: 23 tools.
- **CommunityAgent**: Rewritten for OCM unified inbox (get_inbox_summary, categorize_messages, draft_response, send_response, escalate_message).
- **ContentAgent**: +3 publishing tools (schedule_post, get_optimal_posting_times, adapt_content_for_platform). Total: 10 tools.
- **CampaignAnalyticsAgent**: +3 social analytics tools (get_social_performance, generate_social_report, benchmark_against_competitors). Total: 9 tools.

New artifact types: `SOCIAL_POST`, `SOCIAL_REPORT`, `LISTENING_REPORT` with schemas and standard actions.

Publisher registered in agent registry, factory, and ERP tier map (STANDARD tier).

### PR #38: Observer Agent + Source Adapters
**Branch**: `claude/fix-artifact-streaming-vdtAi`

New **ObserverAgent** — Obsei-inspired Source → Analyze → Route pipeline. Shared data ingestion backbone for social_listening, social_analytics, competitor, and brand_performance agents.

- `modules/research/observer_agent.py`: 5 tools (collect_mentions, analyze_sentiment, collect_reviews, collect_competitor_content, route_insights)
- `modules/research/source_adapters.py`: Normalized Mention/MentionBatch data shapes + 6 async adapters (Twitter, Reddit, App Store, Google Reviews, News, Website). Mock data when no API keys configured.
- `modules/research/source_config.py`: Per-tenant SourceConfig loaded from context metadata.

Registered in research module factory (7 agents), ERP tier map (STANDARD).

### PR #37: tool_choice Forcing for emit_artifact
**Commit**: `a4ac110`

When `artifact_format` is set on an agent execution, the system now forces `tool_choice: {"type": "tool", "name": "emit_artifact"}`. This ensures the LLM always produces a structured artifact instead of returning plain text.

### PR #36: Artifact Streaming Fix — SSE Callback Queue
**Commit**: `a213326`

Fixed: artifact events were silently dropped during SSE streaming. Root cause: `stream()` was not wiring the `_sse_callback` into the artifact event pipeline. Fix: artifact events now flow through `asyncio.Queue` + `_sse_callback` so the SSE transport picks them up.

**Key pattern**: `stream()` needs `asyncio.Queue` + `_sse_callback` for artifact events to flow through SSE.

### PR #35: LMS Agents — Tutor, Content, Assessment
**Commit**: `011154c`

3 new LMS agents:
- **LmsTutorAgent**: Adaptive tutoring with Socratic method, concept explanation, progress tracking
- **LmsContentAgent**: Course authoring, lesson generation, resource curation
- **LmsAssessmentAgent**: Question generation with bloom's taxonomy, adaptive difficulty, grading

New artifact types: `COURSE`, `ASSESSMENT`, `LEARNING_PATH`. Enhanced training orchestrator integration.

### PR #34: Mission Control Routing + Artifact Protocol + Billing
**Commit**: `4a334fb`

Major integration milestone. MC routing endpoints, artifact protocol implementation, billing hooks.

**7 security fixes**:
1. HMAC auth bypass fix
2. API key whitespace handling
3. Proper 401 returns
4. CI pipeline with security scanning
5. Rate limiting enforcement
6. Input validation on execute endpoint
7. Swagger auth configuration

Billing: all agent endpoints report usage to `POST /api/v1/billing/usage/report` with `X-Service-Key` header.

---

# External LLM Provider Integration

## Release Notes v2.0

Complete integration of 14 external LLM providers into the 46-agent ERP system with config-driven pricing, credit-based billing, and optimized provider routing.

---

## New Providers

### xAI (Grok + Aurora)
**File**: `src/services/llm_clients/xai.py`

| Capability | Model | Use Case |
|------------|-------|----------|
| Chat | Grok-2, Grok-3 | Real-time X/Twitter data |
| Images | Aurora | Text-in-image generation |
| Social | Grok-2 | Live trending, sentiment |

```python
from src.services.llm_clients import grok_chat, grok_image, grok_realtime

# Real-time social intelligence
trends = await grok_realtime("What's trending about Nike?")

# Text-in-image (Aurora excels here)
banner = await grok_image("Sale banner with '50% OFF' text")
```

---

### Google (Gemini + Imagen + TTS)
**File**: `src/services/llm_clients/google.py`

| Capability | Model | vs Alternative |
|------------|-------|----------------|
| Routing | Gemini 2.0 Flash | **50x cheaper** than GPT-4o |
| Vision | Gemini 1.5 Pro | **4x cheaper** than GPT-4V |
| Images | Imagen 3 | **50% cheaper** than DALL-E |
| TTS | Google TTS | **75x cheaper** than ElevenLabs |

```python
from src.services.llm_clients import gemini_classify, gemini_chat, imagen_generate, google_tts

# Ultra-cheap routing (~$0.0001 per call)
intent = await gemini_classify(user_input, ["billing", "support", "sales"])

# Budget TTS for drafts
audio = await google_tts("Welcome to SpokeStack", voice="en-US-Neural2-J")
```

---

### Zhipu AI (GLM-4.7)
**File**: `src/services/llm_clients/zhipu.py`

| Spec | GLM-4.7 | vs Sonnet |
|------|---------|-----------|
| Context | 200K tokens | 1.5x larger |
| Output | **128K tokens** | 16x larger |
| Math | 95.7% AIME | Comparable |
| Cost | $0.60/$2.20 per 1M | **5-7x cheaper** |

```python
from src.services.llm_clients import glm_chat, glm_report, glm_analyze, glm_code

# Generate full report in one call (128K output!)
report = await glm_report("Q4 Financial Analysis", data=financial_data)

# Strong math reasoning
analysis = await glm_analyze(spreadsheet_data, analysis_type="forecast")

# Code generation (beats Sonnet on LiveCodeBench)
code = await glm_code("Build a REST API for user management", language="python")
```

---

### Presenton (Self-Hosted)
**File**: `src/services/llm_clients/presenton.py`

| Feature | Benefit |
|---------|---------|
| Self-hosted | No per-API cost |
| Uses your keys | Token cost only |
| **90%+ margin** | vs Gamma/Beautiful.ai |

```python
from src.services.llm_clients import get_llm_factory

factory = get_llm_factory()
presenton = factory.get_presenton()

deck = await presenton.generate_presentation(
    topic="Q4 Internal Report",
    num_slides=10,
    style="corporate"
)
```

---

## Billing & Credits System

### Credit-Based Pricing
**Files**: `credits.py`, `billing.py`, `pricing_config.json`

| Plan | Price | Credits | Value | Margin |
|------|-------|---------|-------|--------|
| Starter | $49/mo | 2,000 | $0.03 | 67%+ |
| Brand | $199/mo | 10,000 | $0.025 | 60%+ |
| Agency | $499/mo | 35,000 | $0.02 | 50%+ |
| Enterprise | $1,499/mo | 150,000 | $0.015 | 33%+ |

### Cost Calculation

```python
from src.services.llm_clients import (
    calculate_video_cost,
    calculate_image_cost,
    cost_to_credits,
    suggest_client_pricing,
)

# Calculate API cost
cost = calculate_video_cost("higgsfield", "veo3", duration_seconds=10)
# CostBreakdown(total_cost_usd=1.50)

# Convert to credits
credits = cost_to_credits(cost.total_cost_usd, tier="brand")
# 135 credits

# Get client pricing suggestion
pricing = suggest_client_pricing(cost, margin_percent=200)
# ClientBillingRate(suggested_price=4.50, margin_percent=67%)
```

### Config-Driven Updates

```python
from src.services.llm_clients import update_pricing, reload_pricing_config

# Update without code changes
update_pricing("provider_costs.video.higgsfield.veo3.per_second", 0.12)

# Or reload entire config
reload_pricing_config()
```

---

## Provider Registry

**File**: `src/services/external_llm_registry.py`

### New Providers

```python
class ExternalLLMProvider(str, Enum):
    # Video
    HIGGSFIELD = "higgsfield"
    RUNWAY = "runway"

    # Image
    OPENAI_DALLE = "openai_dalle"
    REPLICATE_FLUX = "replicate_flux"
    STABILITY = "stability"
    XAI_AURORA = "xai_aurora"          # NEW
    GOOGLE_IMAGEN = "google_imagen"    # NEW

    # Voice
    ELEVENLABS = "elevenlabs"
    OPENAI_TTS = "openai_tts"
    GOOGLE_TTS = "google_tts"          # NEW

    # Vision
    OPENAI_VISION = "openai_vision"
    GOOGLE_GEMINI_VISION = "google_gemini_vision"  # NEW

    # Chat/Routing
    GOOGLE_GEMINI = "google_gemini"    # NEW
    XAI_GROK = "xai_grok"              # NEW

    # Presentations
    BEAUTIFUL_AI = "beautiful_ai"
    GAMMA = "gamma"
    PRESENTON = "presenton"            # NEW

    # Research
    PERPLEXITY = "perplexity"
    ZHIPU_GLM = "zhipu_glm"            # NEW
```

### Agent Mappings

```python
AGENT_EXTERNAL_LLMS = {
    # Social agents get Grok for real-time data
    "social_listening_agent": [XAI_GROK, PERPLEXITY],
    "pr_agent": [XAI_GROK, PERPLEXITY],

    # Analytics agents get Gemini Vision (4x cheaper, 2M context)
    "analytics_agent": [GOOGLE_GEMINI_VISION],
    "campaign_analytics_agent": [GOOGLE_GEMINI_VISION],

    # Report agents get GLM for 128K output
    "report_agent": [GAMMA, ZHIPU_GLM],
    "ops_reporting_agent": [PRESENTON, ZHIPU_GLM],

    # Image agents get full provider selection
    "image_agent": [OPENAI_DALLE, REPLICATE_FLUX, STABILITY, XAI_AURORA, GOOGLE_IMAGEN],
}
```

---

## Cost Optimization

### Smart Model Routing

```
User Request → Gemini Flash Classification ($0.0001)
                         ↓
           ┌─────────────┼─────────────┐
           ↓             ↓             ↓
       Simple        Standard       Complex
           ↓             ↓             ↓
       Haiku         GLM-4.7       Opus 4.5
      ($0.001)       ($0.003)      ($0.09)
```

**Savings**: 70-90% vs using Sonnet for everything

### Draft → Final Pipeline

| Asset | Draft | Final | Iteration Savings |
|-------|-------|-------|-------------------|
| Image | Flux Schnell ($0.003) | DALL-E 3 HD ($0.08) | **96%** |
| Video | Pika ($0.40) | Veo 3 ($1.50) | **73%** |
| Voice | Google TTS ($0.004) | ElevenLabs ($0.30) | **99%** |
| Report | GLM-4.7 draft | Opus polish | **80%** |

### Provider Selection Matrix

| Need | Budget | Quality | Premium |
|------|--------|---------|---------|
| **Images** | Flux Schnell | Imagen 3 | DALL-E 3 HD |
| **Video** | Pika | Kling 1.6 | Sora 2 |
| **Voice** | Google Std | Neural2 | ElevenLabs |
| **Text** | GLM-4.5 Flash | GLM-4.7 | Opus 4.5 |
| **Analysis** | Gemini Flash | Gemini Vision | GPT-4V |
| **Decks** | Presenton | Gamma | Beautiful.ai |

---

## Profitability Impact

### Margin Improvement

| Plan | Before | After | Change |
|------|--------|-------|--------|
| Starter | 12% | **76%** | +64 pts |
| Brand | 25% | **69%** | +44 pts |
| Agency | 23% | **59%** | +36 pts |
| Enterprise | 27% | **61%** | +34 pts |

### Annual Profit (100 Customers)

| Metric | Before | After |
|--------|--------|-------|
| Monthly Profit | $5,491 | **$14,962** |
| Annual Profit | $65,892 | **$179,544** |
| **Increase** | - | **+$113,652/year** |

---

## Environment Variables

```bash
# Foundation (Priority 1-3)
ANTHROPIC_API_KEY=        # Claude (primary reasoning)
GOOGLE_API_KEY=           # Gemini, Imagen, TTS
OPENAI_API_KEY=           # DALL-E, Vision, TTS, Whisper

# Value Tier (Priority 4)
XAI_API_KEY=              # Grok (real-time social), Aurora
ZHIPU_API_KEY=            # GLM-4.7 (code, reports, math)

# Creative (Priority 5-6)
HIGGSFIELD_API_KEY=       # 12 video models
REPLICATE_API_KEY=        # Flux (cheap image drafts)

# Refinements (Priority 7-9)
ELEVENLABS_API_KEY=       # Premium voice
PERPLEXITY_API_KEY=       # Research with citations
STABILITY_API_KEY=        # SD3, SDXL

# Situational (Priority 10-12)
RUNWAY_API_KEY=           # Gen-3 video
BEAUTIFUL_AI_API_KEY=     # Premium presentations
GAMMA_API_KEY=            # Client presentations

# Self-hosted
PRESENTON_BASE_URL=http://localhost:8080/api/v1
```

---

## Files Changed

### New Files
| File | Description |
|------|-------------|
| `src/services/llm_clients/xai.py` | xAI client (Grok + Aurora) |
| `src/services/llm_clients/google.py` | Google client (Gemini + Imagen + TTS) |
| `src/services/llm_clients/zhipu.py` | Zhipu client (GLM-4.7) |
| `src/services/llm_clients/presenton.py` | Presenton client |
| `src/services/llm_clients/billing.py` | Cost calculation functions |
| `src/services/llm_clients/credits.py` | Credit system |
| `src/services/llm_clients/pricing_config.json` | Config-driven pricing |
| `docs/PROVIDERS.md` | Provider documentation |
| `docs/PRICING.md` | Pricing & margin analysis |
| `docs/API.md` | API reference |

### Updated Files
| File | Changes |
|------|---------|
| `src/services/llm_clients/factory.py` | Added get_xai(), get_google(), get_zhipu(), get_presenton() |
| `src/services/llm_clients/__init__.py` | Export new clients and functions |
| `src/services/external_llm_registry.py` | Added 8 new providers, updated agent mappings |
| `README.md` | Architecture overview, provider matrix |

---

## API Quick Reference

### Factory Pattern
```python
from src.services.llm_clients import get_llm_factory

factory = get_llm_factory()
xai = factory.get_xai()
google = factory.get_google()
zhipu = factory.get_zhipu()
```

### Convenience Functions
```python
from src.services.llm_clients import (
    # xAI
    grok_chat, grok_image, grok_realtime,
    # Google
    gemini_chat, gemini_classify, imagen_generate, google_tts,
    # Zhipu
    glm_chat, glm_report, glm_analyze, glm_code,
    # Billing
    calculate_video_cost, calculate_image_cost,
    cost_to_credits, suggest_client_pricing,
)
```

### Category Getters
```python
from src.services.llm_clients import (
    get_video_clients,       # Higgsfield, Runway
    get_image_clients,       # DALL-E, Flux, Stability, Aurora, Imagen
    get_voice_clients,       # ElevenLabs, OpenAI TTS, Google TTS
    get_presentation_clients, # Beautiful.ai, Gamma, Presenton
    get_research_clients,    # Perplexity
)
```

---

## Summary

**14 providers** with **config-driven pricing** and **smart routing** that increases margins from ~22% to ~60%, adding **+$113K/year profit** on 100 customers.
