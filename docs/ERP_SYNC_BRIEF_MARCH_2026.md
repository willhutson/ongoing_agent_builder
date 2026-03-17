# ERP Sync Brief — Agent Builder → erp_staging_lmtd

**Generated:** 2026-03-17
**Branch:** `claude/align-erp-integration-61aci`
**Status:** Ready for ERP-side integration

---

## What Changed Since Last Handoff (Jan 2026)

| Change | Impact on ERP |
|--------|---------------|
| **5-tier model system** (was 3-tier) | New `creative` and `vision` tiers in tier enum |
| **Platform Skills** (Layer 2) | New `/api/v1/skills` endpoints to consume |
| **13 module subdomains** | `X-Module-Subdomain` header scopes agent availability |
| **47 agents** (was 46) | Updated registry response shape |
| **OpenRouter consolidation** | All LLM routing via OpenRouter — ERP billing simplified |
| **HMAC callback signature** | `X-Webhook-Signature: v1=<hmac>` on PATCH callbacks |

---

## 1. Tier Contract (5-Tier)

The ERP `ModelSelector` component must now support 5 tiers:

| ERP Tier (send this) | Internal Tier | Model | Use Case |
|----------------------|---------------|-------|----------|
| `premium` | OPUS | `claude-opus-4-5-20250514` | Legal, finance, knowledge — complex reasoning |
| `standard` | SONNET | `claude-sonnet-4-20250514` | Default for most agents |
| `economy` | HAIKU | `claude-haiku-3-5-20241022` | Gateways, approvals, high-volume |
| `creative` | CREATIVE | `moonshotai/kimi-k2.5` | Copywriting, presentations, brand voice, video scripts |
| `vision` | VISION | `openai/gpt-5-image-mini` | Image generation, visual understanding |

**Cost indicators for UI:**

```json
{
  "premium":  { "level": 3, "label": "$$$" },
  "standard": { "level": 2, "label": "$$" },
  "economy":  { "level": 1, "label": "$" },
  "creative": { "level": 2, "label": "$$" },
  "vision":   { "level": 2, "label": "$$" }
}
```

**Credit mapping suggestion:**

| Tier | Credits/Request (base) |
|------|----------------------|
| economy | 1-2 |
| standard | 5 |
| premium | 15 |
| creative | 5 |
| vision | 20 (image gen) |

---

## 2. Execute Endpoint Contract

### `POST /api/v1/agent/execute`

**Request:**
```json
{
  "agent_type": "brief",
  "task": "Create a Q2 campaign brief for sneaker launch",
  "model": "claude-sonnet-4-20250514",
  "tier": "standard",
  "tenant_id": "org-123",
  "user_id": "user-456",
  "user_role": "ADMIN",
  "session_id": "session-789",
  "context": {
    "moduleSubdomain": "briefs",
    "clientId": "client-abc",
    "projectId": "proj-def"
  },
  "callback_url": "https://erp.spokestack.app/api/v1/invocations/inv-123",
  "invocation_id": "inv-123",
  "stream": false
}
```

**Key rules:**
- `agent_type` is optional if `context.moduleSubdomain` is set (defaults to module's default agent)
- `model` field uses alias — send as `"model"` in JSON, received as `llm_model` internally
- `stream: true` returns SSE (`text/event-stream`) instead of background task
- `callback_url` + `invocation_id` = async mode — Agent Builder PATCHes results back

**Response (sync/immediate):**
```json
{
  "execution_id": "exec-abc123",
  "status": "pending",
  "session_id": "session-789"
}
```

**Callback PATCH payload (async):**
```json
{
  "invocation_id": "inv-123",
  "status": "COMPLETED",
  "output": "Generated brief content...",
  "inputTokens": 500,
  "outputTokens": 1200,
  "durationMs": 3500,
  "completedAt": "2026-03-17T12:00:00Z"
}
```

**Callback signature header:**
```
X-Webhook-Signature: v1=<HMAC-SHA256(body, ERP_CALLBACK_SECRET)>
```

---

## 3. Module Subdomain Registry

The ERP middleware should set `X-Module-Subdomain` header based on request origin.

| Subdomain | Default Agent | Agent Count | Description |
|-----------|--------------|-------------|-------------|
| `studio` | `content` | 11 | Creative production |
| `crm` | `crm` | 5 | Client management |
| `briefs` | `brief` | 6 | Brief creation |
| `projects` | `workflow` | 5 | Project management |
| `analytics` | `campaign_analytics` | 6 | Analytics & reporting |
| `lms` | `training` | 3 | Learning management |
| `publisher` | `campaign` | 9 | Publishing & distribution |
| `time` | `resource` | 3 | Time tracking |
| `finance` | `invoice` | 5 | Financial management |
| `resources` | `resource` | 3 | Resource allocation |
| `surveys` | `community` | 3 | Surveys & feedback |
| `marketing` | `campaign` | 11 | Marketing & media |
| `app` | `content` | 46+ | Full platform (all agents) |

**Discovery endpoint:** `GET /api/v1/modules` — returns full registry
**Per-module:** `GET /api/v1/modules/{subdomain}` — returns agents for that module

---

## 4. Platform Skills

New capability — skills are lightweight, composable tools that agents can invoke.

| Skill | Description | Use From |
|-------|-------------|----------|
| `brief_quality_scorer` | Score briefs against quality criteria | briefs, studio |
| `smart_assigner` | AI-powered team member assignment | projects, resources |
| `scope_creep_detector` | Detect project scope deviation | projects, briefs |
| `timeline_estimator` | Estimate project timelines | projects, time |

**Endpoints:**
- `GET /api/v1/skills` — list all platform skills
- `GET /api/v1/skills/{name}` — skill details with input schema

---

## 5. Agent Registry (47 Agents by Tier)

### Premium (4 agents)
`legal`, `forecast`, `budget`, `knowledge`

### Creative (7 agents)
`presentation`, `copy`, `brand_voice`, `brand_visual`, `brand_guidelines`, `video_script`, `video_storyboard`

### Vision (1 agent)
`image`

### Standard (29 agents)
`rfp`, `brief`, `content`, `commercial`, `video_production`, `resource`, `workflow`, `ops_reporting`, `crm`, `scope`, `onboarding`, `instance_onboarding`, `instance_analytics`, `instance_success`, `media_buying`, `campaign`, `social_listening`, `community`, `social_analytics`, `brand_performance`, `campaign_analytics`, `competitor`, `invoice`, `qa`, `training`, `influencer`, `pr`, `events`, `localization`, `accessibility`, `report`

### Economy (6 agents)
`approve`, `brief_update`, `gateway_whatsapp`, `gateway_email`, `gateway_slack`, `gateway_sms`

### Meta (1)
`prompt_helper` (standard tier — routes users to correct agent)

---

## 6. Discovery Endpoints (for ERP to consume)

| Endpoint | Method | Returns |
|----------|--------|---------|
| `GET /api/v1/agents/registry` | GET | All 47 agents with tier annotations |
| `GET /api/v1/agents/{type}` | GET | Agent details + input schema |
| `GET /api/v1/modules` | GET | 13 module subdomains with agent mappings |
| `GET /api/v1/modules/{subdomain}` | GET | Module-specific agent list |
| `GET /api/v1/skills` | GET | Platform skills registry |
| `GET /api/v1/skills/{name}` | GET | Skill details |
| `GET /api/v1/models/tiers` | GET | 5-tier model info with cost indicators |
| `GET /api/health` | GET | Health + provider latency |

---

## 7. ERP Environment Variables

```env
# Agent Builder connection
AGENT_SERVICE_URL=https://agent-builder.spokestack.app
AGENT_SERVICE_API_KEY=<shared-api-key>
ERP_CALLBACK_SECRET=<shared-hmac-secret>

# Feature flags
AI_ENABLED=true
AI_DEFAULT_TIER=standard
AI_STREAMING_ENABLED=true

# Rate limits
AI_RATE_LIMIT_PER_MINUTE=60
AI_MAX_CONCURRENT_REQUESTS=10
```

---

## 8. ERP-Side Implementation Checklist

```
[ ] Update ModelSelector component to support 5 tiers (add creative, vision)
[ ] Set X-Module-Subdomain header in ERP middleware based on request origin
[ ] Wire /api/v1/agent/execute calls with new tier enum
[ ] Implement HMAC signature verification on callback receiver
[ ] Consume /api/v1/modules for dynamic module→agent mapping
[ ] Consume /api/v1/skills for skills browser UI
[ ] Update credit deduction logic for creative/vision tiers
[ ] Wire SSE streaming for Mission Control embedded chat
[ ] Add agent_type dropdown per module (populated from module registry)
[ ] Test callback flow: execute → poll status → receive PATCH
```

---

## 9. Quick Integration Test

```bash
# Health check
curl https://agent-builder.spokestack.app/api/health

# List modules
curl -H "Authorization: Bearer $API_KEY" \
  https://agent-builder.spokestack.app/api/v1/modules

# Execute agent (sync)
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Module-Subdomain: briefs" \
  https://agent-builder.spokestack.app/api/v1/agent/execute \
  -d '{
    "task": "Create a brief for Q2 sneaker campaign",
    "model": "claude-sonnet-4-20250514",
    "tier": "standard",
    "tenant_id": "org-test",
    "user_id": "user-test"
  }'

# Poll result
curl -H "Authorization: Bearer $API_KEY" \
  https://agent-builder.spokestack.app/api/v1/agent/status/{execution_id}
```
