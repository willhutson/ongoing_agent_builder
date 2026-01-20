# Pricing & Margin Analysis

Complete cost breakdown for the 14-provider agent ecosystem with margin calculations and profit projections.

## Credit System Overview

SpokeStack uses a credit-based billing system where:
- **1 credit = $0.01 of API cost** at base rate
- Tiers get volume discounts via multipliers
- Revenue = Credits used × Credit price (varies by tier)

---

## Subscription Plans

| Plan | Price | Credits | Credit Value | Effective Rate | Overage |
|------|-------|---------|--------------|----------------|---------|
| **Starter** | $49/mo | 2,000 | $0.03/credit | 3x markup | $0.035 |
| **Brand** | $199/mo | 10,000 | $0.025/credit | 2.5x markup | $0.028 |
| **Agency** | $499/mo | 35,000 | $0.02/credit | 2x markup | $0.022 |
| **Enterprise** | $1,499/mo | 150,000 | $0.015/credit | 1.5x markup | $0.018 |

### Plan Features

| Plan | Max Users | Modules |
|------|-----------|---------|
| Starter | 3 | Studio, Voice |
| Brand | 10 | Video, Studio, Voice, Research |
| Agency | 50 | Video, Studio, Voice, Research, Analytics |
| Enterprise | 999 | All modules |

---

## Complete AI Model Matrix

### Primary Reasoning (Claude)

| Model | Input/1k | Output/1k | Tier | Use For |
|-------|----------|-----------|------|---------|
| Claude Opus 4.5 | $0.015 | $0.075 | Premium | Legal, Finance, Clients, Knowledge |
| Claude Sonnet 4 | $0.003 | $0.015 | Standard | Most agents |
| Claude Haiku 3.5 | $0.00025 | $0.00125 | Fast | Simple tasks |

### Value Tier (GLM-4.7) - NEW

| Model | Input/1k | Output/1k | Context | Output Cap | Use For |
|-------|----------|-----------|---------|------------|---------|
| GLM-4.7 | $0.0006 | $0.0022 | 200K | **128K** | Code, Reports, Math |
| GLM-4.7 Thinking | $0.0006 | $0.0022 | 200K | 128K | Complex reasoning |
| GLM-4.5 | $0.00035 | $0.00155 | 131K | - | General |
| GLM-4.5 Flash | $0.0001 | $0.0005 | - | - | Fast tasks |

**vs Claude Sonnet**: GLM-4.7 is **5x cheaper** on input, **6.8x cheaper** on output

### Routing (Ultra-Cheap Classification)

| Model | Input/1M | Output/1M | vs GPT-4o |
|-------|----------|-----------|-----------|
| Gemini 2.0 Flash | $0.10 | $0.40 | **50x cheaper** |
| Gemini 1.5 Flash | $0.075 | $0.30 | **67x cheaper** |
| Gemini 1.5 Flash 8B | $0.0375 | $0.15 | **133x cheaper** |

### Social/Real-time (Grok)

| Model | Input/1M | Output/1M | Special |
|-------|----------|-----------|---------|
| Grok 3 | $3.00 | $15.00 | Best reasoning |
| Grok 3 Fast | $1.00 | $5.00 | Fast |
| Grok 2 | $2.00 | $10.00 | **Real-time X/Twitter** |
| Grok 2 Mini | $0.50 | $2.50 | Budget |

### Vision/Analytics

| Model | Input/1k | Output/1k | Context | vs GPT-4V |
|-------|----------|-----------|---------|-----------|
| Gemini 1.5 Pro Vision | $0.00125 | $0.005 | **2M** | **4x cheaper** |
| GPT-4o | $0.005 | $0.015 | 128k | Baseline |

---

## Provider Cost Matrix (All 14 Providers)

### Video Generation (Higgsfield + Runway)

| Provider | Model | Cost/sec | 10s Video | Credits |
|----------|-------|----------|-----------|---------|
| Higgsfield | Pika | $0.04 | $0.40 | 40 |
| Higgsfield | Seedance | $0.04 | $0.40 | 40 |
| Higgsfield | WAN | $0.05 | $0.50 | 50 |
| Higgsfield | Hunyuan | $0.05 | $0.50 | 50 |
| Runway | Gen-3 Turbo | $0.05 | $0.50 | 50 |
| Higgsfield | WAN 2.1 | $0.06 | $0.60 | 60 |
| Higgsfield | Minimax | $0.07 | $0.70 | 70 |
| Higgsfield | Kling | $0.08 | $0.80 | 80 |
| Runway | Gen-3 Alpha | $0.10 | $1.00 | 100 |
| Higgsfield | Kling 1.6 | $0.10 | $1.00 | 100 |
| Higgsfield | Luma | $0.10 | $1.00 | 100 |
| Higgsfield | Veo 3 | $0.15 | $1.50 | 150 |
| Higgsfield | Veo 3.1 | $0.18 | $1.80 | 180 |
| Higgsfield | Sora 2 | $0.20 | $2.00 | 200 |

### Image Generation (6 Providers)

| Provider | Model | Cost/Image | Credits | Best For |
|----------|-------|------------|---------|----------|
| Replicate | Flux Schnell | $0.003 | 0.3 | **Drafts** |
| Google | Imagen 3 | $0.020 | 2 | Quality + value |
| Stability | SDXL 1.0 | $0.020 | 2 | Flexibility |
| Replicate | Flux Dev | $0.025 | 2.5 | Development |
| Stability | SD3 Medium | $0.035 | 3.5 | Balance |
| OpenAI | DALL-E 3 Std | $0.040 | 4 | Quality |
| xAI | Aurora | $0.040 | 4 | **Text-in-image** |
| Replicate | Flux 1.1 Pro | $0.040 | 4 | Pro quality |
| Stability | SD3 Large | $0.065 | 6.5 | High quality |
| OpenAI | DALL-E 3 HD | $0.080 | 8 | **Premium** |
| Stability | Ultra | $0.080 | 8 | Ultra quality |

### Voice/TTS (3 Providers)

| Provider | Model | Per 1k chars | Credits | Best For |
|----------|-------|--------------|---------|----------|
| Google | Standard | $0.004 | 0.4 | **Drafts (75x cheaper)** |
| OpenAI | TTS-1 | $0.015 | 1.5 | Mid-tier |
| Google | WaveNet/Neural2 | $0.016 | 1.6 | Quality budget |
| OpenAI | TTS-1-HD | $0.030 | 3 | High quality |
| ElevenLabs | TTS | $0.300 | 30 | **Premium/Cloning** |

### Presentations (3 Providers)

| Provider | 10-Slide Deck | Credits | Margin | Best For |
|----------|---------------|---------|--------|----------|
| Presenton | ~$0.30 | 30 | **90%+** | Internal reports |
| Gamma | ~$4.00 | 400 | 67% | Client-facing |
| Beautiful.ai | ~$6.00 | 600 | 67% | Premium |

### Research (3 Providers)

| Provider | Model | Est. Cost/Query | Credits | Special |
|----------|-------|-----------------|---------|---------|
| Perplexity | Sonar | $0.002-0.01 | 1-2 | Fast search |
| Perplexity | Sonar Pro | $0.02-0.10 | 5-10 | Deep research |
| Grok 2 | Real-time | $0.03-0.08 | 5-10 | **Live X/Twitter** |
| GLM-4.7 | Analysis | $0.01-0.05 | 2-5 | **Math/Data** |

---

## Optimized Model Selection by Agent

| Agent Category | Before | After (Optimized) | Savings |
|----------------|--------|-------------------|---------|
| **High-stakes** (legal, finance) | Opus 4.5 | Opus 4.5 | - (keep quality) |
| **Standard reasoning** | Sonnet | Sonnet | - |
| **Code generation** | Sonnet | **GLM-4.7** | **84%** |
| **Long reports** | Sonnet | **GLM-4.7** | **84%** |
| **Math/analysis** | Sonnet | **GLM-4.7** | **84%** |
| **Routing/classification** | GPT-4o | **Gemini Flash** | **98%** |
| **Dashboard analysis** | GPT-4V | **Gemini Vision** | **75%** |
| **Social monitoring** | Perplexity | **Grok 2** | Real-time data |
| **Draft images** | DALL-E | **Flux Schnell** | **96%** |
| **Draft voice** | OpenAI TTS | **Google TTS** | **73%** |
| **Internal decks** | Gamma | **Presenton** | **92%** |

---

## Margin Analysis: Before vs After Optimization

### Text Generation Tasks (per 50K tokens)

| Task | Before (Sonnet) | After (GLM-4.7) | Cost Reduction |
|------|-----------------|-----------------|----------------|
| API Cost | $0.90 | $0.14 | **84%** |
| Starter Revenue (3x) | $2.70 | $0.42 | - |
| **Starter Margin** | 67% | **95%** | +28 pts |
| Agency Revenue (2x) | $1.80 | $0.28 | - |
| **Agency Margin** | 50% | **86%** | +36 pts |

### Routing Operations (per 1000 classifications)

| Task | Before (GPT-4o) | After (Gemini Flash) | Cost Reduction |
|------|-----------------|----------------------|----------------|
| API Cost | $5.00 | $0.10 | **98%** |
| Starter Margin | 67% | **99%** | +32 pts |

### Image Generation (100 images)

| Mix | Before | After (Optimized) | Cost Reduction |
|-----|--------|-------------------|----------------|
| All DALL-E 3 | $4.00 | - | - |
| 80 drafts + 20 finals | - | $0.84 | **79%** |
| (Flux Schnell + DALL-E HD) | | ($0.24 + $0.60) | |

### Voice Generation (100K characters)

| Mix | Before | After (Optimized) | Cost Reduction |
|-----|--------|-------------------|----------------|
| All ElevenLabs | $30.00 | - | - |
| 80% drafts + 20% final | - | $5.92 | **80%** |
| (Google + ElevenLabs) | | ($0.32 + $5.60) | |

---

## Monthly Profit Projections

### Starter Plan ($49/mo) - Optimized

| Activity | Quantity | Old Cost | New Cost | Credits |
|----------|----------|----------|----------|---------|
| Routing (Gemini Flash) | 500 | $2.50 | $0.05 | 5 |
| Image drafts (Flux Schnell) | 100 | $4.00 | $0.30 | 30 |
| Image finals (DALL-E 3) | 20 | $0.80 | $0.80 | 80 |
| Voice drafts (Google TTS) | 40k chars | $6.00 | $0.16 | 16 |
| Voice finals (ElevenLabs) | 10k chars | $3.00 | $3.00 | 300 |
| Reports (GLM-4.7) | 50k tokens | $0.90 | $0.14 | 14 |
| Presentations (Presenton) | 5 decks | $20.00 | $1.50 | 150 |
| Claude Sonnet | 300k tokens | $6.00 | $6.00 | 600 |
| **Total** | | **$43.20** | **$11.95** | **1,195** |

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Revenue | $49.00 | $49.00 | - |
| API Cost | $43.20 | $11.95 | -$31.25 |
| **Profit** | $5.80 | **$37.05** | **+539%** |
| **Margin** | 12% | **76%** | +64 pts |

### Brand Plan ($199/mo) - Optimized

| Activity | Quantity | Old Cost | New Cost | Credits |
|----------|----------|----------|----------|---------|
| Routing (Gemini Flash) | 2000 | $10.00 | $0.20 | 20 |
| Video drafts (Pika) | 20 | $8.00 | $8.00 | 800 |
| Video finals (Veo 3) | 5 | $7.50 | $7.50 | 750 |
| Image drafts (Flux) | 300 | $12.00 | $0.90 | 90 |
| Image finals (Imagen) | 50 | $4.00 | $1.00 | 100 |
| Voice drafts (Google) | 100k | $15.00 | $0.40 | 40 |
| Voice finals (ElevenLabs) | 20k | $6.00 | $6.00 | 600 |
| Reports (GLM-4.7) | 200k tokens | $3.60 | $0.56 | 56 |
| Research (Perplexity) | 50 queries | $2.50 | $2.50 | 250 |
| Social (Grok) | 30 queries | $1.80 | $1.80 | 180 |
| Analytics (Gemini Vision) | 100 | $12.50 | $3.00 | 300 |
| Presentations (Presenton) | 10 | $40.00 | $3.00 | 300 |
| Claude Sonnet | 1M tokens | $18.00 | $18.00 | 1800 |
| Claude Opus (high-stakes) | 100k tokens | $9.00 | $9.00 | 900 |
| **Total** | | **$149.90** | **$61.86** | **6,186** |

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Revenue | $199.00 | $199.00 | - |
| API Cost | $149.90 | $61.86 | -$88.04 |
| **Profit** | $49.10 | **$137.14** | **+179%** |
| **Margin** | 25% | **69%** | +44 pts |

### Agency Plan ($499/mo) - Optimized

| Activity | Quantity | Old Cost | New Cost | Credits |
|----------|----------|----------|----------|---------|
| Routing (Gemini Flash) | 5000 | $25.00 | $0.50 | 50 |
| Video drafts (Pika) | 50 | $20.00 | $20.00 | 2000 |
| Video finals (Veo 3) | 15 | $22.50 | $22.50 | 2250 |
| Image drafts (Flux) | 500 | $20.00 | $1.50 | 150 |
| Image finals (mixed) | 100 | $8.00 | $3.00 | 300 |
| Voice drafts (Google) | 200k | $30.00 | $0.80 | 80 |
| Voice finals (ElevenLabs) | 50k | $15.00 | $15.00 | 1500 |
| Reports (GLM-4.7) | 500k tokens | $9.00 | $1.40 | 140 |
| Research (Perplexity) | 100 queries | $5.00 | $5.00 | 500 |
| Social (Grok) | 50 queries | $3.00 | $3.00 | 300 |
| Analytics (Gemini Vision) | 200 | $25.00 | $6.00 | 600 |
| Presentations (Presenton) | 20 internal | $80.00 | $6.00 | 600 |
| Presentations (Gamma) | 10 client | $40.00 | $40.00 | 4000 |
| Claude Sonnet | 3M tokens | $54.00 | $54.00 | 5400 |
| Claude Opus (high-stakes) | 300k tokens | $27.00 | $27.00 | 2700 |
| **Total** | | **$383.50** | **$205.70** | **20,570** |

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Revenue | $499.00 | $499.00 | - |
| API Cost | $383.50 | $205.70 | -$177.80 |
| **Profit** | $115.50 | **$293.30** | **+154%** |
| **Margin** | 23% | **59%** | +36 pts |

### Enterprise Plan ($1,499/mo) - Optimized

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Revenue | $1,499.00 | $1,499.00 | - |
| Est. API Cost | $1,100.00 | $580.00 | -$520.00 |
| **Profit** | $399.00 | **$919.00** | **+130%** |
| **Margin** | 27% | **61%** | +34 pts |

---

## Annual Profit Impact (100 Customers)

Assuming customer mix: 50 Starter, 30 Brand, 15 Agency, 5 Enterprise

| Plan | Customers | Old Monthly Profit | New Monthly Profit | Δ/Month |
|------|-----------|--------------------|--------------------|---------|
| Starter | 50 | $290 | $1,853 | +$1,563 |
| Brand | 30 | $1,473 | $4,114 | +$2,641 |
| Agency | 15 | $1,733 | $4,400 | +$2,667 |
| Enterprise | 5 | $1,995 | $4,595 | +$2,600 |
| **Total** | 100 | **$5,491/mo** | **$14,962/mo** | **+$9,471** |

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Monthly Profit** | $5,491 | $14,962 | +172% |
| **Annual Profit** | $65,892 | $179,544 | **+$113,652** |
| **Avg Margin** | 22% | 60% | +38 pts |

---

## Credit Estimation Reference

| Operation | Credits (approx) |
|-----------|------------------|
| Gemini Flash routing | 0.1 |
| Simple image (Flux Schnell) | 0.3 |
| Quality image (Imagen/DALL-E) | 2-8 |
| Text-in-image (Aurora) | 4 |
| 10s video (draft) | 40-50 |
| 10s video (quality) | 100-150 |
| 10s video (premium) | 180-200 |
| 1k chars voice (Google) | 0.4 |
| 1k chars voice (ElevenLabs) | 30 |
| 10-slide deck (Presenton) | 30 |
| 10-slide deck (Gamma) | 400 |
| Research query (Sonar) | 2-5 |
| Real-time social (Grok) | 5-10 |
| GLM-4.7 report (10k tokens) | 3 |
| Claude Sonnet (1k tokens) | 2-3 |
| Claude Opus (1k tokens) | 9-10 |
| Gemini Vision analysis | 3-5 |

---

## Cost Optimization Strategies

### 1. Smart Model Routing

```
User Request → Gemini Flash Classification ($0.0001)
                    ↓
        ┌──────────┼──────────┐
        ↓          ↓          ↓
    Simple     Standard    Complex
        ↓          ↓          ↓
    Haiku      GLM-4.7     Opus 4.5
   ($0.001)    ($0.003)    ($0.09)
```

**Savings**: 70-90% vs using Sonnet for everything

### 2. Draft → Final Pipeline

```
Draft (cheap) → Review → Final (quality)

Image:  Flux Schnell ($0.003) → ✓ → DALL-E 3 HD ($0.08)    = 96% savings on iterations
Video:  Pika ($0.40) → ✓ → Veo 3 ($1.50)                   = 73% savings on iterations
Voice:  Google TTS ($0.004) → ✓ → ElevenLabs ($0.30)       = 99% savings on iterations
Report: GLM-4.7 draft → ✓ → Opus polish                    = 80% savings on iterations
```

### 3. Provider Selection Matrix

| Need | Budget | Quality | Premium |
|------|--------|---------|---------|
| **Images** | Flux Schnell | Imagen 3 | DALL-E 3 HD |
| **Video** | Pika | Kling 1.6 | Sora 2 |
| **Voice** | Google Std | Google Neural2 | ElevenLabs |
| **Text** | GLM-4.5 Flash | GLM-4.7 | Opus 4.5 |
| **Analysis** | Gemini Flash | Gemini Vision | GPT-4V |
| **Decks** | Presenton | Gamma | Beautiful.ai |

---

## Updating Pricing

Pricing is config-driven via `pricing_config.json`:

```python
from src.services.llm_clients import update_pricing, reload_pricing_config

# Update a specific cost
update_pricing("provider_costs.video.higgsfield.veo3.per_second", 0.12)

# Reload entire config
reload_pricing_config()
```

See [`API.md`](API.md) for full pricing API reference.
