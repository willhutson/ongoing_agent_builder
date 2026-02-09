# ERP Staging Integration Specification

Integration guide for `ongoing_agent_builder` with `erp_staging_lmtd`.

> **See also:** [Agent Builder Integration Spec v2.0](../spokestack/docs/AGENT_BUILDER_INTEGRATION_SPEC.md) - The comprehensive tech spec covering state machine protocol, Agent Work Protocol (screen share paradigm), SpokeStack tool definitions, artifact streaming, WebSocket events, and vision support.

## Architecture Overview

```
┌─────────────────────────────────────┐
│         erp_staging_lmtd            │
│  (ERP System / User Interface)      │
│  ┌──────────────┐ ┌──────────────┐  │
│  │ ModelSelector│ │ PromptHelper │  │
│  │  Component   │ │  Component   │  │
│  └──────┬───────┘ └──────┬───────┘  │
└─────────┼────────────────┼──────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────┐
│       ongoing_agent_builder         │
│     (Agent Infrastructure)          │
│  ┌──────────────┐ ┌──────────────┐  │
│  │AgentManager  │ │PromptHelper  │  │
│  │   Service    │ │   Agent      │  │
│  └──────────────┘ └──────────────┘  │
│  ┌──────────────────────────────┐   │
│  │   47 Agents + 14 LLM Providers│   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

## Model Tier Mapping

### External Tiers (erp_staging_lmtd UI)

| Tier | Cost | Best For |
|------|------|----------|
| **Premium** | $$$ | Complex analysis, strategic decisions, legal |
| **Standard** | $$ | Most tasks - balanced capability and cost |
| **Economy** | $ | High-volume, simple operations, gateways |

### Internal → External Mapping

| Internal (Claude) | External (UI) | Model ID |
|-------------------|---------------|----------|
| OPUS | Premium | claude-opus-4-5-20250514 |
| SONNET | Standard | claude-sonnet-4-20250514 |
| HAIKU | Economy | claude-haiku-3-5-20241022 |

### API Usage

```python
from src.services.model_registry import (
    ExternalModelTier,
    get_external_tier,
    get_external_model_info,
)

# Get tier for agent
tier = get_external_tier("rfp_agent")  # Returns ExternalModelTier.PREMIUM

# Get full info for UI
info = get_external_model_info()  # Returns tiers with cost indicators
```

## External LLM Providers (14 Total)

### By Category

| Category | Providers | Cost Range |
|----------|-----------|------------|
| **Video** | Higgsfield (12 models), Runway | $0.40-$2.00/10s |
| **Image** | DALL-E, Flux, Stability, Aurora, Imagen | $0.003-$0.08/img |
| **Voice** | ElevenLabs, OpenAI TTS, Google TTS | $4-$300/1M chars |
| **Vision** | GPT-4V, Gemini Vision (2M context) | Per-token pricing |
| **Presentation** | Beautiful.ai, Gamma, Presenton | $0.10-$6/10 slides |
| **Research** | Perplexity, Grok (real-time X) | $1-$8/1k queries |
| **Text/Code** | Zhipu GLM (128K output) | 5x cheaper than Sonnet |

## AgentManager Service

Central orchestration for the agent ecosystem.

### Key Features

1. **Agent Discovery** - List and recommend agents
2. **Execution Management** - Track agent runs
3. **Multi-Agent Workflows** - Orchestrate agent chains
4. **Usage Analytics** - Cost and performance monitoring

### API Examples

```python
from src.services.agent_manager import get_agent_manager, AgentTier

manager = get_agent_manager(factory)

# List agents by module
agents = manager.list_agents(module="studio")

# Get agent recommendations
recommendations = manager.recommend_agents("I need to create a video ad")

# Execute with tier override
execution = await manager.execute_agent(
    agent_type="video_production",
    task="Create 30s product video",
    instance_id=uuid,
    tier_override=AgentTier.PREMIUM,
)

# Get usage stats
stats = manager.get_usage_stats(instance_id=uuid)
```

## PromptHelper Agent

Meta-agent that helps users craft better prompts.

### Capabilities

1. **Agent Selection** - Find the right agent for any task
2. **Prompt Optimization** - Analyze and improve prompts
3. **Provider Guidance** - Recommend cost-optimal providers
4. **Template Generation** - Structured prompt templates

### API Usage

```python
POST /api/v1/agent/execute
{
    "agent_type": "prompt_helper",
    "task": "I need to create a video for our product launch"
}

# Returns:
# - Recommended agents (video_script, video_storyboard, video_production)
# - Missing information to gather
# - Optimized prompt template
# - Provider recommendations by tier
```

## Module Integration Matrix

| ERP Module | Agents | Default Tier | External LLMs |
|------------|--------|--------------|---------------|
| **Foundation** | rfp, brief, content, commercial | Standard/Premium | Perplexity |
| **Studio** | presentation, copy, image | Standard | DALL-E, Flux, Imagen, Presenton, Gamma |
| **Video** | video_script, video_storyboard, video_production | Standard | Higgsfield, Runway, ElevenLabs |
| **Social** | social_listening, community, social_analytics | Standard | Grok, Gemini Vision |
| **Analytics** | campaign_analytics, brand_performance, competitor | Standard/Premium | Gemini Vision, Perplexity |
| **Finance** | invoice, forecast, budget | Standard/Premium | - |
| **Quality** | qa, legal | Standard/Premium | Gemini Vision, GPT-4V |
| **Distribution** | report, approve, brief_update, ops_reporting | Economy | Gamma, Zhipu GLM, Presenton |
| **Operations** | resource, workflow | Standard | - |
| **Client** | crm, scope, onboarding | Standard | - |
| **Brand** | brand_voice, brand_visual, brand_guidelines | Standard | ElevenLabs, DALL-E, Flux |
| **Gateways** | whatsapp, email, slack, sms | Economy | - |
| **Specialized** | influencer, pr, events, localization, accessibility | Standard | Various |
| **Meta** | prompt_helper | Standard | - |

## REST API Endpoints

### Core Endpoints (ERP Integration)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agent/execute` | POST | Execute an agent (main entry point) |
| `/api/v1/agent/status/{id}` | GET | Poll for execution results |
| `/api/v1/agent/chat` | POST | Chat with agent (session-based) |
| `/api/v1/agent/chat/{id}` | GET | Get chat session history |
| `/api/v1/health` | GET | Health check with provider latency |
| `/api/v1/agents/registry` | GET | All 46 agents with tier annotations |
| `/api/v1/agents/{type}` | GET | Get agent details with inputs |

### Request Schema: POST `/api/v1/agent/execute`

```json
{
  "agent": "brief",
  "task": "Create a campaign brief",
  "model": "claude-sonnet-4-20250514",
  "tier": "standard",
  "tenant_id": "org-123",
  "user_id": "user-456",
  "session_id": "session-789",
  "context": {},
  "callback_url": "https://erp.example.com/api/v1/invocations/inv-123",
  "invocation_id": "inv-123"
}
```

### Response Schema

```json
{
  "execution_id": "exec-abc",
  "status": "pending",
  "session_id": "session-789"
}
```

### Callback Mechanism

When `callback_url` and `invocation_id` are provided, Agent Builder sends results via PATCH:

```json
{
  "invocation_id": "inv-123",
  "status": "completed",
  "output": "Generated content...",
  "token_usage": {"input_tokens": 500, "output_tokens": 1200, "total_tokens": 1700},
  "duration_ms": 3500,
  "error": null,
  "completed_at": "2026-01-20T12:00:00Z"
}
```

**Callback Headers:**
- `X-Signature`: HMAC-SHA256 signature using shared `ERP_CALLBACK_SECRET`

### Legacy/Additional Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agents` | GET | List all agents with metadata |
| `/api/v1/agents/recommend` | POST | Get agent recommendations |
| `/api/v1/models/tiers` | GET | Get tier info with cost indicators |
| `/api/v1/providers/status` | GET | External LLM provider status |
| `/api/v1/manager/stats` | GET | Usage statistics |

## Files Added/Modified

### New Files
- `src/agents/prompt_helper_agent.py` - PromptHelper meta-agent
- `src/services/agent_manager.py` - AgentManager service
- `docs/ERP_STAGING_INTEGRATION.md` - This document

### Modified Files
- `src/agents/__init__.py` - Added PromptHelperAgent export
- `src/services/agent_factory.py` - Added prompt_helper to registry
- `src/services/model_registry.py` - Added external tier mapping

---

# Agent Gap Analysis

Based on analysis of [marketingskills](https://github.com/coreyhaines31/marketingskills) repository.

## Existing Coverage

These skills are already covered by our 47 agents:

| Skill | Covered By |
|-------|-----------|
| copywriting | CopyAgent |
| copy-editing | CopyAgent, QAAgent |
| competitor-alternatives | CompetitorAgent |
| social-content | CommunityAgent, SocialListeningAgent |
| pricing-strategy | CommercialAgent |
| paid-ads | MediaBuyingAgent |

## Recommended New Agents

High-value additions based on gap analysis:

### Priority 1: Growth & Conversion

| Agent | Purpose | Tier | External LLMs |
|-------|---------|------|---------------|
| **CROAgent** | Landing page & form conversion optimization | Standard | Gemini Vision |
| **ABTestAgent** | Experiment design and statistical analysis | Standard | - |
| **LaunchAgent** | Go-to-market orchestration | Standard | Perplexity |

### Priority 2: Retention & Growth

| Agent | Purpose | Tier | External LLMs |
|-------|---------|------|---------------|
| **EmailSequenceAgent** | Drip campaigns and nurture flows | Standard | - |
| **ReferralAgent** | Referral/affiliate program design | Standard | - |
| **ActivationAgent** | User onboarding and activation CRO | Standard | Gemini Vision |

### Priority 3: SEO & Discovery

| Agent | Purpose | Tier | External LLMs |
|-------|---------|------|---------------|
| **SEOAuditAgent** | Technical and on-page SEO audit | Standard | Perplexity |
| **ProgrammaticSEOAgent** | Template-based SEO at scale | Standard | Zhipu GLM |
| **SchemaAgent** | Structured data and rich snippets | Economy | - |

### Priority 4: Analytics & Tracking

| Agent | Purpose | Tier | External LLMs |
|-------|---------|------|---------------|
| **TrackingAgent** | GA4/GTM event instrumentation | Standard | - |
| **MarketingPsychAgent** | Mental models and persuasion frameworks | Standard | - |

## Implementation Notes

### New Agent Template

```python
from .base import BaseAgent

class NewAgent(BaseAgent):
    """Purpose description."""

    @property
    def name(self) -> str:
        return "new_agent"

    @property
    def system_prompt(self) -> str:
        return """Agent system prompt..."""

    def _define_tools(self) -> list[dict]:
        return [...]

    async def _execute_tool(self, tool_name: str, tool_input: dict):
        ...
```

### Registration Checklist

1. Create agent file in `src/agents/`
2. Add to `src/agents/__init__.py`
3. Add to `AGENT_REGISTRY` in `src/services/agent_factory.py`
4. Add to `AGENT_MODEL_RECOMMENDATIONS` in `src/services/model_registry.py`
5. Add to `AGENT_EXTERNAL_LLMS` in `src/services/external_llm_registry.py` (if using external LLMs)
6. Update `docs/AGENTS.md`

## Summary

- **Current Agents:** 47 (46 + 1 meta)
- **External LLM Providers:** 14
- **Recommended New Agents:** 11 (prioritized)
- **Total Potential:** 58 agents
