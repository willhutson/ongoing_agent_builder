# External LLM Providers

This document covers all 13 external LLM providers integrated into the agent system.

## Overview

Agents use **Claude** (Sonnet/Opus) for reasoning and orchestration, plus **external LLMs** for specialized capabilities:

| Capability | Providers | Why External |
|------------|-----------|--------------|
| Video Generation | Higgsfield, Runway | Claude cannot generate video |
| Image Generation | DALL-E, Flux, Stability, Aurora, Imagen | Claude cannot generate images |
| Voice/TTS | ElevenLabs, Google TTS, OpenAI TTS | Claude cannot synthesize speech |
| Real-time Data | Grok (xAI) | Native X/Twitter access |
| Web Search | Perplexity | Search-augmented research |
| Presentations | Presenton, Gamma, Beautiful.ai | Specialized deck generation |

---

## Provider Setup

### Required Environment Variables

```env
# Primary (required)
ANTHROPIC_API_KEY=sk-ant-...

# Video
HIGGSFIELD_API_KEY=hf-...
RUNWAY_API_KEY=...

# Image
OPENAI_API_KEY=sk-...
REPLICATE_API_KEY=r8-...
STABILITY_API_KEY=sk-...

# Multi-capability (image + voice + chat)
GOOGLE_API_KEY=AIza...
XAI_API_KEY=xai-...

# Voice
ELEVENLABS_API_KEY=...

# Research
PERPLEXITY_API_KEY=pplx-...

# Presentations
BEAUTIFUL_AI_API_KEY=...
GAMMA_API_KEY=...
PRESENTON_BASE_URL=http://localhost:8080/api/v1
```

---

## Video Providers

### Higgsfield

Multi-model video generation platform with 12+ models.

| Model | Cost/sec | Duration | Best For |
|-------|----------|----------|----------|
| Sora 2 | $0.20 | 5-20s | Premium, complex scenes |
| Veo 3.1 | $0.18 | 5-16s | High quality |
| Veo 3 | $0.15 | 5-16s | Quality/cost balance |
| Kling 1.6 | $0.10 | 5-10s | Good quality, mid-price |
| Kling | $0.08 | 5-10s | Reliable |
| Minimax | $0.07 | 5-60s | Long videos |
| WAN 2.1 | $0.06 | 5-10s | Budget with quality |
| WAN | $0.05 | 5-10s | Budget |
| Hunyuan | $0.05 | 5-10s | Budget |
| Luma | $0.10 | 5-10s | Stylized |
| Pika | $0.04 | 3-10s | Cheapest |
| Seedance | $0.04 | 5-10s | Cheapest |

**Setup:**
```env
HIGGSFIELD_API_KEY=hf-your-key
HIGGSFIELD_BASE_URL=https://api.higgsfield.ai/v1  # optional
```

**Usage:**
```python
from src.services.llm_clients import HiggsfieldClient

client = HiggsfieldClient()
video = await client.generate_video(
    prompt="Product showcase of sneakers",
    model="veo3",
    duration=10
)
```

### Runway

Video editing and Gen-3 generation.

| Model | Cost/sec | Duration | Best For |
|-------|----------|----------|----------|
| Gen-3 Alpha | $0.10 | 5-10s | Quality video |
| Gen-3 Turbo | $0.05 | 5-10s | Fast drafts |

**Setup:**
```env
RUNWAY_API_KEY=your-key
```

---

## Image Providers

### OpenAI DALL-E 3

| Size | Quality | Cost |
|------|---------|------|
| 1024x1024 | Standard | $0.04 |
| 1024x1024 | HD | $0.08 |
| 1792x1024 | Standard | $0.08 |
| 1792x1024 | HD | $0.12 |

**Setup:**
```env
OPENAI_API_KEY=sk-your-key
```

### Replicate Flux

| Model | Cost | Best For |
|-------|------|----------|
| Flux 1.1 Pro | $0.04 | High quality |
| Flux Dev | $0.025 | Development |
| Flux Schnell | $0.003 | **Drafts (cheapest)** |

**Setup:**
```env
REPLICATE_API_KEY=r8-your-key
```

**Usage (quick drafts):**
```python
from src.services.llm_clients import ReplicateClient

client = ReplicateClient()
images = await client.generate_image(
    prompt="Product photo",
    model="flux-schnell",  # Only $0.003!
    num_outputs=4
)
```

### Stability AI

| Model | Cost | Best For |
|-------|------|----------|
| SD3 Large | $0.065 | Best quality |
| SD3 Large Turbo | $0.04 | Fast, good quality |
| SD3 Medium | $0.035 | Balanced |
| SDXL 1.0 | $0.02 | Budget |
| Stable Image Ultra | $0.08 | Premium |

**Setup:**
```env
STABILITY_API_KEY=sk-your-key
```

### xAI Aurora

Grok's image generation - strong at text-in-image.

| Model | Cost | Best For |
|-------|------|----------|
| Aurora | $0.04 | Text overlays, banners |

**Setup:**
```env
XAI_API_KEY=xai-your-key
```

**Usage:**
```python
from src.services.llm_clients import grok_image

images = await grok_image("Sale banner with '50% OFF' text")
```

### Google Imagen 3

50% cheaper than DALL-E with comparable quality.

| Model | Cost | Best For |
|-------|------|----------|
| Imagen 3 | $0.02 | **Budget quality images** |

**Setup:**
```env
GOOGLE_API_KEY=AIza-your-key
```

**Usage:**
```python
from src.services.llm_clients import imagen_generate

images = await imagen_generate("Product photo of sneakers", n=4)
```

---

## Voice Providers

### ElevenLabs (Premium)

Best quality voice synthesis and cloning.

| Feature | Cost | Best For |
|---------|------|----------|
| TTS | $0.30/1k chars | Client-facing audio |
| Voice Clone | $0.30/1k chars | Brand voice |
| Sound Effects | $0.10/gen | SFX |

**Setup:**
```env
ELEVENLABS_API_KEY=your-key
```

### Google Cloud TTS (Budget)

**75x cheaper** than ElevenLabs.

| Voice Type | Cost/1M chars | Best For |
|------------|---------------|----------|
| Standard | $4.00 | Drafts, internal |
| WaveNet | $16.00 | Better quality |
| Neural2 | $16.00 | Best Google quality |

**Setup:**
```env
GOOGLE_API_KEY=AIza-your-key
```

**Usage:**
```python
from src.services.llm_clients import google_tts

audio = await google_tts("Welcome to SpokeStack", voice="en-US-Neural2-J")
```

### OpenAI TTS

| Model | Cost/1k chars | Best For |
|-------|---------------|----------|
| TTS-1 | $0.015 | Standard |
| TTS-1-HD | $0.03 | Higher quality |

### OpenAI Whisper

| Model | Cost | Best For |
|-------|------|----------|
| Whisper-1 | $0.006/min | Transcription |

---

## Research Providers

### Perplexity

Search-augmented research with citations.

| Model | Input/1k | Output/1k | Best For |
|-------|----------|-----------|----------|
| Sonar Pro | $0.003 | $0.015 | Deep research |
| Sonar | $0.001 | $0.001 | Quick search |
| Sonar Reasoning | $0.001 | $0.005 | Analysis |

**Setup:**
```env
PERPLEXITY_API_KEY=pplx-your-key
```

### xAI Grok (Real-time Social)

**Native X/Twitter data access** - unique capability.

| Model | Input/1M | Output/1M | Best For |
|-------|----------|-----------|----------|
| Grok 3 | $3.00 | $15.00 | Best reasoning |
| Grok 3 Fast | $1.00 | $5.00 | Fast |
| Grok 2 | $2.00 | $10.00 | **Real-time social** |
| Grok 2 Mini | $0.50 | $2.50 | Budget |

**Setup:**
```env
XAI_API_KEY=xai-your-key
```

**Usage:**
```python
from src.services.llm_clients import grok_realtime

# Get real-time X/Twitter data
response = await grok_realtime("What's trending about Nike right now?")
```

---

## Vision/Analytics Providers

### Google Gemini Vision

**4x cheaper** than GPT-4V with **2M token context** for bulk dashboard analysis.

| Model | Input/1k | Output/1k | Context | Best For |
|-------|----------|-----------|---------|----------|
| Gemini 1.5 Pro | $0.00125 | $0.005 | 2M | **Dashboard analysis** |

**Setup:**
```env
GOOGLE_API_KEY=AIza-your-key
```

### OpenAI GPT-4 Vision

| Model | Input/1k | Output/1k | Best For |
|-------|----------|-----------|----------|
| GPT-4o | $0.005 | $0.015 | General vision |
| GPT-4 Turbo | $0.01 | $0.03 | Complex analysis |

---

## Presentation Providers

### Presenton (Self-Hosted)

**90%+ margin** - only pay for underlying AI tokens.

| Cost Component | Price |
|----------------|-------|
| Base | $0 (self-hosted) |
| AI tokens | ~$0.01-0.05/slide |
| Total ~10 slides | ~$0.10-0.50 |

**Setup:**
```env
PRESENTON_BASE_URL=http://localhost:8080/api/v1
```

**Best for:** Internal reports, ops reporting

### Gamma

| Component | Cost |
|-----------|------|
| Per deck | $2.00 |
| Per slide | $0.20 |
| 10-slide deck | ~$4.00 |

**Best for:** Client-facing reports

### Beautiful.ai

| Component | Cost |
|-----------|------|
| Per deck | $3.00 |
| Per slide | $0.30 |
| 10-slide deck | ~$6.00 |

**Best for:** Premium client presentations

---

## Routing/Classification

### Google Gemini Flash

**50x cheaper** than GPT-4o for routing and classification.

| Model | Input/1M | Output/1M | Best For |
|-------|----------|-----------|----------|
| Gemini 2.0 Flash | $0.10 | $0.40 | **Routing (cheapest)** |
| Gemini 1.5 Flash | $0.075 | $0.30 | Fast tasks |
| Gemini 1.5 Flash 8B | $0.0375 | $0.15 | **Ultra-cheap** |

**Usage:**
```python
from src.services.llm_clients import gemini_classify

intent = await gemini_classify(
    "I want to cancel my subscription",
    categories=["billing", "support", "sales", "other"]
)
# Cost: ~$0.0001 per classification
```

---

## Provider Selection Guide

### By Use Case

| Use Case | Recommended | Cost | Why |
|----------|-------------|------|-----|
| **Video drafts** | Pika/Seedance | $0.04/s | Cheapest |
| **Video final** | Veo 3 | $0.15/s | Quality/cost balance |
| **Image drafts** | Flux Schnell | $0.003 | **13x cheaper** than DALL-E |
| **Image final** | DALL-E 3 HD | $0.08 | Best quality |
| **Voice drafts** | Google TTS | $4/M | **75x cheaper** |
| **Voice final** | ElevenLabs | $300/M | Best quality |
| **Internal reports** | Presenton | ~$0.10 | **90% margin** |
| **Client reports** | Gamma | ~$4 | Good quality |
| **Routing** | Gemini Flash | $0.10/M | **50x cheaper** |
| **Real-time social** | Grok 2 | $2/M in | **Only option** |
| **Dashboard analysis** | Gemini Vision | $1.25/M | **4x cheaper**, 2M context |

### By Margin Priority

| Priority | Providers | Margin |
|----------|-----------|--------|
| **Highest** | Presenton, Flux Schnell, Gemini Flash | 85-95% |
| **High** | Google TTS, Imagen, SDXL | 70-85% |
| **Medium** | DALL-E, Perplexity, Grok | 50-70% |
| **Lower** | ElevenLabs, Sora 2, Beautiful.ai | 40-50% |

---

## Checking Provider Status

### API Endpoint

```bash
curl http://localhost:8000/api/v1/providers/status
```

### Programmatic

```python
from src.services.external_llm_registry import get_provider_status

status = get_provider_status()
for provider in status:
    print(f"{provider['name']}: {'Configured' if provider['configured'] else 'Missing'}")
```

### Check Missing for Agent

```python
from src.services.external_llm_registry import list_unconfigured_for_agent

missing = list_unconfigured_for_agent("video_production_agent")
for provider in missing:
    print(f"Missing: {provider['name']} - set {provider['api_key_setting']}")
```
