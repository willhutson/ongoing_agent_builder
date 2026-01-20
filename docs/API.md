# API Reference

Complete API reference for the agent service.

## Table of Contents

- [REST API Endpoints](#rest-api-endpoints)
  - [Agent Execution](#agent-execution)
  - [Chat Sessions](#chat-sessions)
  - [Health & Registry](#health--registry)
  - [Callback Mechanism](#callback-mechanism)
- [Agent Services](#agent-services)
  - [AgentManager](#agentmanager)
  - [SkillLibrary](#skilllibrary)
- [LLM Clients](#llm-clients)
  - [Quick Start](#quick-start)
  - [Factory Pattern](#factory-pattern)
  - [Provider Clients](#provider-clients)
  - [Convenience Functions](#convenience-functions)
  - [Billing API](#billing-api)
  - [Credits API](#credits-api)
  - [Data Classes](#data-classes)

---

## REST API Endpoints

Base URL: `http://localhost:8000` (or your deployed URL)

### Agent Execution

#### POST `/api/v1/agent/execute`

Execute an agent task. Supports both ERP-integrated and standalone modes.

**Headers:**
| Header | Required | Description |
|--------|----------|-------------|
| `X-Organization-Id` | No | Organization identifier |
| `X-Request-Id` | No | Request tracking ID |

**Request Body:**
```json
{
  "agent": "brief",
  "task": "Create a campaign brief for product launch",
  "model": "claude-sonnet-4-20250514",
  "tier": "standard",
  "tenant_id": "tenant-123",
  "user_id": "user-456",
  "session_id": "session-789",
  "context": {"client_id": "acme-corp"},
  "callback_url": "https://erp.example.com/api/v1/invocations/inv-123",
  "invocation_id": "inv-123"
}
```

**Response:**
```json
{
  "execution_id": "exec-abc-123",
  "status": "pending",
  "session_id": "session-789"
}
```

#### GET `/api/v1/agent/status/{execution_id}`

Poll for execution results.

**Response:**
```json
{
  "execution_id": "exec-abc-123",
  "status": "completed",
  "output": "Generated brief content...",
  "token_usage": {"input_tokens": 500, "output_tokens": 1200, "total_tokens": 1700},
  "duration_ms": 3500
}
```

### Chat Sessions

#### POST `/api/v1/agent/chat`

Start or continue a chat session with an agent.

```json
{
  "message": "We are a creative agency with 25 employees",
  "agent_type": "instance_onboarding",
  "tenant_id": "tenant-123",
  "user_id": "user-456",
  "session_id": "existing-session-id"
}
```

#### GET `/api/v1/agent/chat/{session_id}`

Get chat session history.

#### DELETE `/api/v1/agent/chat/{session_id}`

Delete a chat session.

### Health & Registry

#### GET `/api/v1/health`

Health check with provider status.

```json
{
  "status": "healthy",
  "service": "ongoing-agent-builder",
  "agents_available": 46,
  "providers": [
    {"provider": "anthropic", "status": "healthy", "latency_ms": 50}
  ]
}
```

#### GET `/api/v1/agents/registry`

Get all 46 agents organized by layer with tier annotations.

#### GET `/api/v1/agents/{agent_type}`

Get details for a specific agent including recommended inputs.

### Callback Mechanism

When `callback_url` and `invocation_id` are provided, results are sent via PATCH with HMAC signature:

**Headers:** `X-Signature` (HMAC-SHA256)

**Payload:**
```json
{
  "invocation_id": "inv-123",
  "status": "completed",
  "output": "...",
  "token_usage": {...},
  "duration_ms": 3500,
  "completed_at": "2026-01-20T12:00:00Z"
}
```

---

## Agent Services

### AgentManager

Central orchestration service for the agent ecosystem.

```python
from src.services.agent_manager import get_agent_manager, AgentTier

manager = get_agent_manager()
```

#### List & Discover Agents

```python
# List all agents
agents = manager.list_agents()

# Filter by category
studio_agents = manager.list_agents(category="studio")

# Search agents
results = manager.list_agents(search="video")

# Get agent info
info = manager.get_agent_info("video_production_agent")
# Returns: id, name, category, tools, tier, external_providers, recommended_for

# Recommend agents for a task
recommendations = manager.recommend_agents("I need to create a product video for sneakers")
# Returns: [{"agent": "video_production_agent", "confidence": 0.95, "reason": "..."}]
```

#### Execute Agents

```python
# Execute an agent
result = await manager.execute_agent(
    agent_id="image_agent",
    input_text="Create a product photo for sneakers",
    instance_id="tenant-123",
    context={"brand_guidelines": {...}},
)
# Returns: AgentExecution(execution_id, status, result, cost, duration)

# Check status
status = await manager.get_execution_status(execution_id)
```

#### Multi-Agent Workflows

```python
from src.services.agent_manager import WorkflowStep, AgentWorkflow

# Create workflow
workflow = manager.create_workflow(
    name="Video Production Pipeline",
    steps=[
        WorkflowStep(agent_id="video_script_agent", input_key="brief"),
        WorkflowStep(agent_id="video_storyboard_agent", input_key="script", depends_on="video_script_agent"),
        WorkflowStep(agent_id="video_production_agent", input_key="storyboard", depends_on="video_storyboard_agent"),
    ]
)

# Execute workflow
results = await manager.execute_workflow(
    workflow_id=workflow.id,
    initial_input={"brief": "Create a 30-second product video..."},
    instance_id="tenant-123",
)
```

#### Usage Analytics

```python
# Get usage statistics
stats = manager.get_usage_stats(
    instance_id="tenant-123",
    start_date="2025-01-01",
    end_date="2025-01-31",
)
# Returns: total_executions, total_cost, by_agent, by_tier, by_day

# Get tier summary
tiers = manager.get_tier_summary()
# Returns: {"economy": [...], "standard": [...], "premium": [...]}

# Check provider status
status = manager.get_provider_status()
# Returns: {"higgsfield": "healthy", "openai": "healthy", ...}
```

#### Tier Mapping

| External Tier | Internal Model | Use Cases |
|--------------|----------------|-----------|
| **Premium** | Claude Opus 4.5 | Legal, Finance, Knowledge, Complex reasoning |
| **Standard** | Claude Sonnet 4 | Most agents, general tasks |
| **Economy** | Claude Haiku 3.5 | Simple routing, classification |

---

### SkillLibrary

Service for skill discovery and invocation.

```python
from src.services.skill_library import get_skill_library

library = get_skill_library()
```

#### Discover Skills

```python
# List all skills
skills = library.list_skills()

# Filter by category
content_skills = library.list_skills(category=SkillCategory.CONTENT)

# Search skills
results = library.list_skills(search="email")

# Get skill details
details = library.get_skill_details("email_sequence")
# Returns: id, name, description, category, use_cases, key_questions, deliverables, best_practices
```

#### Invoke Skills

```python
# Invoke a skill (prepares context for agent execution)
invocation = library.invoke_skill(
    skill_id="landing_page_cro",
    user_input="Optimize our product page for conversions",
    context={"url": "https://example.com/product"},
)
# Returns: SkillInvocation(
#     skill_id, skill_name, agent_to_use, context_to_inject, suggested_prompt, key_questions
# )

# Use the invocation with AgentManager
result = await manager.execute_agent(
    agent_id=invocation.agent_to_use,
    input_text=invocation.suggested_prompt,
    instance_id="tenant-123",
    context=invocation.context_to_inject,
)
```

#### Brainstorm Mode

```python
# Start a brainstorming session with frameworks pre-loaded
context = library.start_brainstorm(
    task_type="landing_page",  # landing_page, email, pricing, launch
    market_stage="crowded",    # new, growing, crowded, jaded, mature
    audience="B2B SaaS founders",
    product="Analytics platform",
)
# Returns: mode, task_type, context (with positioning frameworks, value props, headlines)
```

#### Framework Access

```python
# Get positioning angles
angles = library.get_positioning_angles()
# [{"angle": "contrarian", "template": "Everything you know about [X] is wrong", ...}]

# Get headline formulas
headlines = library.get_headline_formulas()
# {"how_to": {"template": "How to [outcome] [without pain]", ...}}

# Get value prop formulas
value_props = library.get_value_prop_formulas()
# {"classic": {"template": "We help [customer] [achieve outcome] by [mechanism]", ...}}
```

---

## LLM Clients

---

## Quick Start

```python
from src.services.llm_clients import (
    # Factory
    get_llm_factory,
    get_video_clients,
    get_image_clients,

    # Direct functions
    grok_chat,
    grok_image,
    grok_realtime,
    gemini_chat,
    gemini_classify,
    imagen_generate,
    google_tts,

    # Billing
    calculate_video_cost,
    calculate_image_cost,
    suggest_client_pricing,

    # Credits
    cost_to_credits,
    calculate_video_credits,
    get_margin,
)
```

---

## Factory Pattern

### ExternalLLMFactory

Central factory for creating and managing external LLM clients.

```python
from src.services.llm_clients import ExternalLLMFactory, get_llm_factory

# Get singleton instance
factory = get_llm_factory()

# Get specific clients
higgsfield = factory.get_higgsfield()
openai = factory.get_openai()
xai = factory.get_xai()
google = factory.get_google()
presenton = factory.get_presenton()

# Check configuration
if factory.is_configured(ExternalLLMProvider.HIGGSFIELD):
    # Provider is ready
    pass

# Get all clients for an agent
clients = factory.get_clients_for_agent("video_production_agent")

# Get missing providers
missing = factory.get_missing_for_agent("video_production_agent")
```

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_higgsfield()` | `HiggsfieldClient` | Video generation (12 models) |
| `get_openai()` | `OpenAIClient` | DALL-E, Vision, TTS, Whisper |
| `get_replicate()` | `ReplicateClient` | Flux image generation |
| `get_stability()` | `StabilityClient` | Stable Diffusion |
| `get_elevenlabs()` | `ElevenLabsClient` | Premium voice synthesis |
| `get_runway()` | `RunwayClient` | Gen-3 video |
| `get_beautiful_ai()` | `BeautifulAIClient` | Premium presentations |
| `get_gamma()` | `GammaClient` | Client-facing decks |
| `get_perplexity()` | `PerplexityClient` | Search-augmented research |
| `get_xai()` | `XAIClient` | Grok chat + Aurora images |
| `get_google()` | `GoogleClient` | Gemini + Imagen + TTS |
| `get_presenton()` | `PresentonClient` | Self-hosted presentations |
| `get_clients_for_agent(name)` | `dict` | All clients for an agent |
| `get_missing_for_agent(name)` | `list` | Unconfigured providers |
| `is_configured(provider)` | `bool` | Check if provider ready |
| `health_check_all()` | `dict` | Health check all providers |
| `close_all()` | `None` | Close all connections |

---

## Provider Clients

### HiggsfieldClient

Multi-model video generation platform.

```python
from src.services.llm_clients import HiggsfieldClient

client = HiggsfieldClient(api_key="hf-...")

# Generate video
result = await client.generate_video(
    prompt="Product showcase of sneakers",
    model="veo3",           # sora2, veo3, kling, wan, pika, etc.
    duration=10,            # seconds
    aspect_ratio="16:9",
    resolution="1080p",
)

# Check status
status = await client.get_status(task_id)

# Health check
healthy = await client.health_check()
```

**Available models**: sora2, veo3, veo3.1, kling, kling1.6, wan, wan2.1, minimax, luma, pika, hunyuan, seedance

### RunwayClient

Gen-3 video generation and editing.

```python
from src.services.llm_clients import RunwayClient

client = RunwayClient(api_key="...")

result = await client.generate_video(
    prompt="Cinematic landscape",
    model="gen3a",          # gen3a or gen3a_turbo
    duration=5,
)
```

### OpenAIClient

DALL-E, Vision, TTS, and Whisper.

```python
from src.services.llm_clients import OpenAIClient

client = OpenAIClient(api_key="sk-...")

# Generate image
image = await client.generate_image(
    prompt="Product photo of sneakers",
    model="dall-e-3",
    size="1024x1024",
    quality="hd",
)

# Analyze image
analysis = await client.analyze_image(
    image_url="https://...",
    prompt="Describe this image",
)

# Text-to-speech
audio = await client.text_to_speech(
    text="Hello world",
    model="tts-1-hd",
    voice="alloy",
)

# Transcribe audio
transcript = await client.transcribe(audio_file)
```

### XAIClient

Grok chat, Aurora images, and real-time X/Twitter data.

```python
from src.services.llm_clients import XAIClient, grok_chat, grok_image, grok_realtime

client = XAIClient(api_key="xai-...")

# Chat completion
response = await client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="grok-2",         # grok-3, grok-3-fast, grok-2, grok-2-mini
)

# Image generation
images = await client.generate_image(
    prompt="Sale banner with '50% OFF' text",
    model="aurora",
    n=1,
)

# Real-time social data (unique capability)
social = await client.search_realtime(
    query="What's trending about Nike right now?",
    model="grok-2",
)
```

**Convenience functions:**

```python
# Quick chat
response = await grok_chat("What's 2+2?", model="grok-2")

# Quick image (great for text-in-image)
images = await grok_image("Banner with 'SALE' text")

# Real-time X/Twitter data
trends = await grok_realtime("Nike trending topics")
```

### GoogleClient

Gemini chat, Imagen images, Google TTS.

```python
from src.services.llm_clients import (
    GoogleClient,
    gemini_chat,
    gemini_classify,
    imagen_generate,
    google_tts,
)

client = GoogleClient(api_key="AIza...")

# Chat completion
response = await client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="gemini-2.0-flash-exp",  # or gemini-1.5-pro
)

# Image generation
images = await client.generate_image(
    prompt="Product photo",
    model="imagen-3",
    n=4,
)

# Text-to-speech
audio = await client.text_to_speech(
    text="Welcome to SpokeStack",
    voice="en-US-Neural2-J",
)
```

**Convenience functions:**

```python
# Quick chat
response = await gemini_chat("What's 2+2?")

# Ultra-cheap classification (~$0.0001 per call)
intent = await gemini_classify(
    "I want to cancel my subscription",
    categories=["billing", "support", "sales", "other"]
)
# Returns: "billing"

# Image generation (50% cheaper than DALL-E)
images = await imagen_generate("Product photo", n=4)

# Budget TTS (75x cheaper than ElevenLabs)
audio = await google_tts("Hello world", voice="en-US-Neural2-J")
```

### ReplicateClient

Flux image generation.

```python
from src.services.llm_clients import ReplicateClient

client = ReplicateClient(api_key="r8-...")

images = await client.generate_image(
    prompt="Product photo",
    model="flux-schnell",   # flux-1.1-pro, flux-dev, flux-schnell
    num_outputs=4,
)
```

### StabilityClient

Stable Diffusion image generation.

```python
from src.services.llm_clients import StabilityClient

client = StabilityClient(api_key="sk-...")

images = await client.generate_image(
    prompt="Product photo",
    model="sd3-large",      # sd3-large, sd3-medium, sdxl-1.0
)

# Upscale
upscaled = await client.upscale(image_data)
```

### ElevenLabsClient

Premium voice synthesis and cloning.

```python
from src.services.llm_clients import ElevenLabsClient

client = ElevenLabsClient(api_key="...")

# Text-to-speech
audio = await client.text_to_speech(
    text="Welcome to our product",
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
)

# Sound effect
sfx = await client.generate_sound_effect(
    prompt="Door creaking open",
)
```

### PerplexityClient

Search-augmented research with citations.

```python
from src.services.llm_clients import PerplexityClient

client = PerplexityClient(api_key="pplx-...")

response = await client.search(
    query="Latest AI developments in 2025",
    model="sonar-pro",      # sonar, sonar-pro, sonar-reasoning
)
# Response includes citations and sources
```

### PresentonClient

Self-hosted presentation generation (90%+ margin).

```python
from src.services.llm_clients import PresentonClient

client = PresentonClient(base_url="http://localhost:8080/api/v1")

# Generate presentation
result = await client.generate_presentation(
    topic="Q4 Revenue Report",
    num_slides=10,
    style="corporate",
    include_images=True,
    ai_model="gpt-4o",
)

# Get cost estimate (for billing)
cost = client.estimate_cost(num_slides=10, include_images=True)
```

### GammaClient

Client-facing presentations and documents.

```python
from src.services.llm_clients import GammaClient

client = GammaClient(api_key="...")

result = await client.generate_presentation(
    topic="Brand Strategy 2025",
    num_slides=12,
)
```

### BeautifulAIClient

Premium presentations.

```python
from src.services.llm_clients import BeautifulAIClient

client = BeautifulAIClient(api_key="...")

result = await client.generate_presentation(
    topic="Investor Pitch",
    num_slides=15,
    template="pitch_deck",
)
```

---

## Convenience Functions

Quick access without factory setup.

### Category Getters

```python
from src.services.llm_clients import (
    get_video_clients,
    get_image_clients,
    get_voice_clients,
    get_presentation_clients,
    get_research_clients,
)

# Get all configured video clients
videos = get_video_clients()
# {"higgsfield": HiggsfieldClient, "runway": RunwayClient}

# Get all configured image clients
images = get_image_clients()
# {"dalle": OpenAIClient, "flux": ReplicateClient, "aurora": XAIClient, "imagen": GoogleClient}

# Get all configured voice clients
voices = get_voice_clients()
# {"elevenlabs": ElevenLabsClient, "openai_tts": OpenAIClient, "google_tts": GoogleClient}

# Get all presentation clients
presentations = get_presentation_clients()
# {"beautiful_ai": BeautifulAIClient, "gamma": GammaClient, "presenton": PresentonClient}

# Get research clients
research = get_research_clients()
# {"perplexity": PerplexityClient}
```

---

## Billing API

Cost calculation and client pricing.

### Cost Calculation Functions

```python
from src.services.llm_clients import (
    calculate_video_cost,
    calculate_image_cost,
    calculate_voice_cost,
    calculate_vision_cost,
    calculate_research_cost,
    calculate_presentation_cost,
)

# Video cost
cost = calculate_video_cost(
    provider="higgsfield",
    model="veo3",
    duration_seconds=10,
    resolution="1080p",
)
# Returns CostBreakdown with total_cost_usd

# Image cost
cost = calculate_image_cost(
    provider="openai",
    model="dall-e-3",
    size="1024x1024",
    quality="hd",
    num_images=4,
)

# Voice cost
cost = calculate_voice_cost(
    provider="elevenlabs",
    operation="tts",
    quantity=5000,  # characters
)

# Vision cost
cost = calculate_vision_cost(
    model="gpt-4o",
    input_tokens=500,
    output_tokens=200,
    num_images=3,
)

# Research cost
cost = calculate_research_cost(
    model="sonar-pro",
    input_tokens=1000,
    output_tokens=2000,
)

# Presentation cost
cost = calculate_presentation_cost(
    provider="presenton",
    num_slides=10,
    include_images=True,
)
```

### Client Pricing

```python
from src.services.llm_clients import suggest_client_pricing

cost = calculate_video_cost("higgsfield", "veo3", 10)

pricing = suggest_client_pricing(
    cost,
    margin_percent=200,     # 3x markup
    minimum_price=1.00,
)
# ClientBillingRate(
#     our_cost=1.50,
#     suggested_price=4.50,
#     margin_percent=66.7,
#     margin_usd=3.00,
# )
```

### Pricing Tables

```python
from src.services.llm_clients import get_full_pricing_summary

summary = get_full_pricing_summary()
# {
#     "video": [...],
#     "image": [...],
#     "voice": [...],
#     "presentation": [...],
#     "research": [...],
# }
```

---

## Credits API

Credit-based billing system.

### Credit Conversion

```python
from src.services.llm_clients import (
    cost_to_credits,
    credits_to_revenue,
    get_margin,
)

# Convert API cost to credits
credits = cost_to_credits(cost_usd=1.50, tier="brand")
# Returns: 135 credits (with tier multiplier)

# Calculate revenue from credits
revenue = credits_to_revenue(credits=135, tier="brand")
# Returns: $3.38 (135 * $0.025)

# Calculate margin
margin = get_margin(api_cost=1.50, credits_used=135, tier="brand")
# {
#     "api_cost": 1.50,
#     "credits_used": 135,
#     "revenue": 3.38,
#     "margin_usd": 1.88,
#     "margin_percent": 55.6,
# }
```

### Credit Calculations

```python
from src.services.llm_clients import (
    calculate_video_credits,
    calculate_image_credits,
    calculate_voice_credits,
    calculate_presentation_credits,
    calculate_research_credits,
)

# Video credits
usage = calculate_video_credits(
    provider="higgsfield",
    model="veo3",
    duration_seconds=10,
    tier="brand",
)
# CreditUsage(
#     operation="video_veo3",
#     category="video",
#     module="video",
#     credits_used=135,
#     api_cost_usd=1.50,
#     tier="brand",
# )

# Image credits
usage = calculate_image_credits(
    provider="openai",
    model="dall-e-3",
    num_images=4,
    tier="agency",
)

# Voice credits
usage = calculate_voice_credits(
    provider="elevenlabs",
    operation="tts",
    quantity=5000,
    tier="starter",
)

# Presentation credits
usage = calculate_presentation_credits(
    provider="presenton",
    num_slides=10,
    tier="brand",
)

# Research credits
usage = calculate_research_credits(
    model="sonar-pro",
    input_tokens=1000,
    output_tokens=2000,
    tier="brand",
)
```

### Plan & Tier Info

```python
from src.services.llm_clients import (
    get_all_plans,
    get_all_tiers,
    get_credit_estimates,
    estimate_monthly_usage,
    PlanInfo,
)

# Get all plans
plans = get_all_plans()
# [
#     {"key": "starter", "name": "Starter", "price": "$49/mo", "credits": 2000, ...},
#     {"key": "brand", "name": "Brand", "price": "$199/mo", "credits": 10000, ...},
#     ...
# ]

# Get all tiers
tiers = get_all_tiers()

# Get credit estimates for common operations
estimates = get_credit_estimates(tier="brand")
# {
#     "video": {"5s_wan_video": 23, "5s_veo3_video": 68, ...},
#     "image": {"dalle3_standard": 4, "flux_schnell": 1, ...},
#     ...
# }

# Estimate monthly usage
estimate = estimate_monthly_usage(
    videos_per_month=10,
    images_per_month=100,
    voice_chars_per_month=50000,
    presentations_per_month=5,
    research_queries_per_month=50,
    tier="brand",
)
# {
#     "total_credits": 12500,
#     "breakdown": {"video": 1350, "images": 400, ...},
#     "recommended_plan": "agency",
#     "plan_credits": 35000,
#     "overage_credits": 0,
# }

# Get plan info
plan = PlanInfo.from_config("brand")
```

### Config Management

```python
from src.services.llm_clients import (
    get_config,
    get_tier_config,
    get_plan_config,
    reload_pricing_config,
    update_pricing,
)

# Get full config
config = get_config()

# Get tier config
tier = get_tier_config("brand")
# {"credit_multiplier": 0.9, "credit_price_usd": 0.025, ...}

# Get plan config
plan = get_plan_config("agency")

# Reload config from file
config = reload_pricing_config()

# Update pricing programmatically
update_pricing({
    "tiers": {
        "brand": {"credit_price_usd": 0.028}
    }
})
```

---

## Data Classes

### GenerationResult

```python
@dataclass
class GenerationResult:
    success: bool
    task_id: Optional[str] = None
    status: TaskStatus = TaskStatus.COMPLETED
    output_url: Optional[str] = None
    output_data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None
```

### TaskStatus

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

### CostBreakdown

```python
@dataclass
class CostBreakdown:
    provider: str
    operation: str
    category: CostCategory
    base_cost_usd: float
    quantity: float = 1.0
    unit: str = "item"
    total_cost_usd: float = 0.0
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

### CreditUsage

```python
@dataclass
class CreditUsage:
    operation: str
    category: str
    module: str
    credits_used: int
    api_cost_usd: float
    tier: str = "brand"
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

### PlanInfo

```python
@dataclass
class PlanInfo:
    name: str
    tier: str
    base_price_usd: float
    included_credits: int
    max_users: int
    modules: list[str]
    overage_rate: float
```

---

## Response Types

### GrokResponse (xAI)

```python
@dataclass
class GrokResponse:
    content: str
    model: str
    usage: dict
    finish_reason: str
```

### AuroraImage (xAI)

```python
@dataclass
class AuroraImage:
    url: str
    revised_prompt: Optional[str]
```

### GeminiResponse (Google)

```python
@dataclass
class GeminiResponse:
    content: str
    model: str
    usage: dict
    finish_reason: str
```

### ImagenImage (Google)

```python
@dataclass
class ImagenImage:
    data: bytes
    mime_type: str
```

### GoogleTTSAudio (Google)

```python
@dataclass
class GoogleTTSAudio:
    audio_data: bytes
    encoding: str
```

---

## Error Handling

All clients raise standard exceptions:

```python
import httpx

try:
    result = await client.generate_video(...)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 429:
        print("Rate limited")
    else:
        print(f"API error: {e}")
except httpx.TimeoutException:
    print("Request timed out")
```

For async generation tasks, check `GenerationResult`:

```python
result = await client.generate_video(...)

if not result.success:
    print(f"Generation failed: {result.error}")
elif result.status == TaskStatus.FAILED:
    print(f"Task failed: {result.error}")
else:
    print(f"Output: {result.output_url}")
```
