# Pricing & Margin Analysis

Complete cost breakdown for the agent ecosystem with margin calculations.

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

## AI Model Tiers

### Claude (Primary Reasoning)

| Model | Input/1k | Output/1k | Tier | Use For |
|-------|----------|-----------|------|---------|
| Claude Opus 4.5 | $0.015 | $0.075 | Premium | Legal, Finance, Clients, Knowledge |
| Claude Sonnet 4 | $0.003 | $0.015 | Standard | Most agents |
| Claude Haiku 3.5 | $0.00025 | $0.00125 | Fast | Simple tasks |

### Routing (Ultra-Cheap Classification)

| Model | Input/1M | Output/1M | vs GPT-4o |
|-------|----------|-----------|-----------|
| Gemini 2.0 Flash | $0.10 | $0.40 | **50x cheaper** |
| Gemini 1.5 Flash | $0.075 | $0.30 | **67x cheaper** |
| Gemini 1.5 Flash 8B | $0.0375 | $0.15 | **133x cheaper** |

### Social/Real-time

| Model | Input/1M | Output/1M | Special |
|-------|----------|-----------|---------|
| Grok 3 | $3.00 | $15.00 | Best reasoning |
| Grok 3 Fast | $1.00 | $5.00 | Fast |
| Grok 2 | $2.00 | $10.00 | **Real-time X/Twitter** |
| Grok 2 Mini | $0.50 | $2.50 | Budget |

---

## Provider Cost Tables

### Video Generation

| Provider | Model | Cost/sec | 10s Video | Credits |
|----------|-------|----------|-----------|---------|
| Higgsfield | Sora 2 | $0.20 | $2.00 | 200 |
| Higgsfield | Veo 3.1 | $0.18 | $1.80 | 180 |
| Higgsfield | Veo 3 | $0.15 | $1.50 | 150 |
| Higgsfield | Kling 1.6 | $0.10 | $1.00 | 100 |
| Higgsfield | Kling | $0.08 | $0.80 | 80 |
| Higgsfield | Minimax | $0.07 | $0.70 | 70 |
| Higgsfield | WAN 2.1 | $0.06 | $0.60 | 60 |
| Higgsfield | WAN | $0.05 | $0.50 | 50 |
| Higgsfield | Hunyuan | $0.05 | $0.50 | 50 |
| Higgsfield | Luma | $0.10 | $1.00 | 100 |
| Higgsfield | Pika | $0.04 | $0.40 | 40 |
| Higgsfield | Seedance | $0.04 | $0.40 | 40 |
| Runway | Gen-3 Alpha | $0.10 | $1.00 | 100 |
| Runway | Gen-3 Turbo | $0.05 | $0.50 | 50 |

**Recommendation**: Use Pika/Seedance for drafts ($0.40), Veo 3 for finals ($1.50)

### Image Generation

| Provider | Model | Cost/Image | Credits |
|----------|-------|------------|---------|
| Replicate | Flux Schnell | $0.003 | 0.3 |
| Stability | SDXL 1.0 | $0.020 | 2 |
| Google | Imagen 3 | $0.020 | 2 |
| Replicate | Flux Dev | $0.025 | 2.5 |
| Stability | SD3 Medium | $0.035 | 3.5 |
| OpenAI | DALL-E 3 Std | $0.040 | 4 |
| xAI | Aurora | $0.040 | 4 |
| Replicate | Flux 1.1 Pro | $0.040 | 4 |
| Stability | SD3 Large Turbo | $0.040 | 4 |
| Stability | SD3 Large | $0.065 | 6.5 |
| OpenAI | DALL-E 3 HD | $0.080 | 8 |
| Stability | Stable Image Ultra | $0.080 | 8 |

**Recommendation**: Use Flux Schnell for drafts ($0.003), DALL-E 3 HD for finals ($0.08)

### Voice/TTS

| Provider | Model | Unit Cost | Per 1000 chars | Credits |
|----------|-------|-----------|----------------|---------|
| Google | Standard | $4/M chars | $0.004 | 0.4 |
| Google | WaveNet | $16/M chars | $0.016 | 1.6 |
| Google | Neural2 | $16/M chars | $0.016 | 1.6 |
| OpenAI | TTS-1 | $15/M chars | $0.015 | 1.5 |
| OpenAI | TTS-1-HD | $30/M chars | $0.030 | 3 |
| ElevenLabs | TTS | $300/M chars | $0.300 | 30 |

**Recommendation**: Use Google Standard for drafts ($0.004/1k), ElevenLabs for finals ($0.30/1k)

### Presentations

| Provider | Base | Per Slide | 10-Slide Deck | Credits |
|----------|------|-----------|---------------|---------|
| Presenton | $0 | ~$0.01-0.05 | ~$0.10-0.50 | 10-50 |
| Gamma | $2.00 | $0.20 | ~$4.00 | 400 |
| Beautiful.ai | $3.00 | $0.30 | ~$6.00 | 600 |

**Recommendation**: Use Presenton for internal (~$0.30), Gamma for clients (~$4.00)

### Research

| Provider | Model | Input/1k | Output/1k |
|----------|-------|----------|-----------|
| Perplexity | Sonar | $0.001 | $0.001 |
| Perplexity | Sonar Reasoning | $0.001 | $0.005 |
| Perplexity | Sonar Pro | $0.003 | $0.015 |

### Vision/Analytics

| Provider | Model | Input/1k | Output/1k | Context |
|----------|-------|----------|-----------|---------|
| Google | Gemini 1.5 Pro Vision | $0.00125 | $0.005 | 2M |
| OpenAI | GPT-4o | $0.005 | $0.015 | 128k |
| OpenAI | GPT-4 Turbo | $0.01 | $0.03 | 128k |

**Recommendation**: Use Gemini Vision (4x cheaper, 16x more context)

---

## Margin Analysis by Module

### Video Module

| Scenario | Our Cost | Starter Revenue | Margin |
|----------|----------|-----------------|--------|
| Draft video (Pika, 10s) | $0.40 | $1.20 | **67%** |
| Final video (Veo 3, 10s) | $1.50 | $4.50 | **67%** |
| Premium video (Sora 2, 10s) | $2.00 | $6.00 | **67%** |

### Studio Module (Images)

| Scenario | Our Cost | Starter Revenue | Margin |
|----------|----------|-----------------|--------|
| Draft (Flux Schnell) | $0.003 | $0.009 | **67%** |
| Standard (Imagen 3) | $0.02 | $0.06 | **67%** |
| Premium (DALL-E 3 HD) | $0.08 | $0.24 | **67%** |

### Voice Module

| Scenario | Our Cost | Starter Revenue | Margin |
|----------|----------|-----------------|--------|
| Internal (Google Standard, 1k) | $0.004 | $0.012 | **67%** |
| Client (ElevenLabs, 1k) | $0.30 | $0.90 | **67%** |

### Presentations Module

| Scenario | Our Cost | Starter Revenue | Margin |
|----------|----------|-----------------|--------|
| Internal (Presenton, 10 slides) | ~$0.30 | $0.90 | **67%** |
| Client (Gamma, 10 slides) | ~$4.00 | $12.00 | **67%** |
| Premium (Beautiful.ai, 10 slides) | ~$6.00 | $18.00 | **67%** |

### Research Module

| Scenario | Our Cost | Starter Revenue | Margin |
|----------|----------|-----------------|--------|
| Quick search (Sonar, 2k tokens) | ~$0.004 | $0.012 | **67%** |
| Deep research (Sonar Pro, 10k) | ~$0.18 | $0.54 | **67%** |
| Real-time social (Grok 2, 5k) | ~$0.06 | $0.18 | **67%** |

---

## Margin by Tier

All tiers maintain healthy margins due to credit multipliers:

| Tier | Credit Price | Markup | Min Margin |
|------|--------------|--------|------------|
| Starter | $0.03 | 3x | **67%** |
| Brand | $0.025 | 2.5x | **60%** |
| Agency | $0.02 | 2x | **50%** |
| Enterprise | $0.015 | 1.5x | **33%** |

---

## Cost Optimization Strategies

### 1. Draft vs Final Pipeline

Always use cheap models for drafts, premium only for finals:

```
Draft → Review → Final

Image:  Flux Schnell ($0.003) → Approval → DALL-E 3 HD ($0.08)
Video:  Pika ($0.40/10s) → Approval → Veo 3 ($1.50/10s)
Voice:  Google TTS ($0.004/1k) → Approval → ElevenLabs ($0.30/1k)
```

**Savings**: 90%+ on iterations

### 2. Smart Routing

Use Gemini Flash for classification before expensive operations:

```python
# Cost: ~$0.0001 per classification
intent = await gemini_classify(user_input, categories)

# Route to appropriate (expensive) model
if intent == "complex":
    response = await claude_opus(...)  # $0.015/1k in
else:
    response = await claude_haiku(...)  # $0.00025/1k in
```

**Savings**: 50-90% on simple queries

### 3. Batch Operations

Aggregate requests where possible:

```python
# Instead of 10 separate image calls
images = await client.generate_image(prompt, n=10)  # One API call
```

### 4. Context Reuse

For analytics, use Gemini's 2M context to batch dashboard analysis:

```python
# Analyze multiple dashboards in one call
analysis = await gemini_vision(
    images=[dashboard1, dashboard2, dashboard3],
    prompt="Analyze all dashboards and provide insights"
)
```

**Savings**: 60-70% vs individual calls

---

## Sample Monthly Costs

### Starter Plan ($49/mo, 2,000 credits)

| Activity | Quantity | Credits | Cost |
|----------|----------|---------|------|
| Image drafts (Flux Schnell) | 100 | 30 | $0.30 |
| Image finals (DALL-E 3) | 20 | 80 | $0.80 |
| Voice (Google TTS) | 50k chars | 20 | $0.20 |
| Presentations (Presenton) | 5 decks | 100 | $1.00 |
| Claude Sonnet reasoning | 500k tokens | 1,000 | $10.00 |
| **Total** | | **1,230** | **$12.30** |

Revenue: $49.00, Cost: $12.30, **Margin: 75%**

### Agency Plan ($499/mo, 35,000 credits)

| Activity | Quantity | Credits | Cost |
|----------|----------|---------|------|
| Video drafts (Pika) | 50 | 2,000 | $20.00 |
| Video finals (Veo 3) | 10 | 1,500 | $15.00 |
| Image drafts | 500 | 150 | $1.50 |
| Image finals | 100 | 400 | $4.00 |
| Voice (mixed) | 200k chars | 300 | $3.00 |
| Presentations (Gamma) | 20 decks | 8,000 | $80.00 |
| Research (Perplexity) | 100 queries | 500 | $5.00 |
| Real-time social (Grok) | 50 queries | 300 | $3.00 |
| Analytics (Gemini Vision) | 200 analyses | 400 | $4.00 |
| Claude reasoning | 5M tokens | 15,000 | $150.00 |
| **Total** | | **28,550** | **$285.50** |

Revenue: $499.00, Cost: $285.50, **Margin: 43%**

---

## Credit Estimation Reference

Quick reference for planning:

| Operation | Credits (approx) |
|-----------|------------------|
| Simple image (draft) | 1 |
| Quality image | 4-8 |
| 10s video (draft) | 40-50 |
| 10s video (quality) | 100-150 |
| 10s video (premium) | 180-200 |
| 1k chars voice (budget) | 1-2 |
| 1k chars voice (premium) | 30 |
| 10-slide deck (internal) | 10-50 |
| 10-slide deck (client) | 400-600 |
| Research query | 2-10 |
| Real-time social query | 5-15 |
| Claude Sonnet (1k tokens) | 3-5 |
| Claude Opus (1k tokens) | 15-25 |

---

## Updating Pricing

Pricing is config-driven via `pricing_config.json`. To update:

```python
from src.services.llm_clients import update_pricing, reload_pricing_config

# Update a specific cost
update_pricing("provider_costs.video.higgsfield.veo3.per_second", 0.12)

# Or reload entire config
reload_pricing_config()
```

See [`API.md`](API.md) for full pricing API reference.
