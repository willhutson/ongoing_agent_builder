# ERP Staging Integration Handoff

Use this prompt to start a new Claude session for integrating the ongoing_agent_builder with erp_staging_lmtd.

---

## Context for Claude

```
You are helping integrate two repositories:

1. **ongoing_agent_builder** (https://github.com/willhutson/ongoing_agent_builder)
   - Standalone agent service built on Claude Agent SDK
   - 47 agents across 18 layers (Foundation, Brand, Studio, etc.)
   - 14 external LLM providers integrated
   - New services added:
     - PromptHelperAgent: Meta-agent that helps users craft better prompts
     - AgentManager: Central orchestration service
     - SkillLibrary: 40+ invokable marketing skills

2. **erp_staging_lmtd** (https://github.com/willhutson/erp_staging_lmtd)
   - The ERP platform (SpokeStack)
   - PR #280 merged: Multi-model integration prep with Economy/Standard/Premium tiers
   - Uses credit-based pricing (Starter $49/2k credits, Brand $199/10k, Agency $499/35k, Enterprise $1,499/150k)
   - Modules: rfp, briefs, content, studio, dam, crm, resources, reporting, workflows, whatsapp, video, analytics, etc.

## Integration Tasks

### 1. API Endpoints to Create in erp_staging_lmtd

Connect to ongoing_agent_builder's REST API:

```python
# Required endpoints to wire up:

POST /api/v1/ai/agent/execute
# Body: {"agent": "agent_id", "input": "...", "instance_id": "...", "tier": "standard"}
# Response: {"execution_id": "...", "status": "...", "result": {...}}

GET /api/v1/ai/agents
# List all available agents with categories and tiers

GET /api/v1/ai/agents/{agent_id}
# Get agent details including tools and recommended inputs

POST /api/v1/ai/prompt-helper
# Body: {"input": "user's raw request", "context": {...}}
# Response: {"recommended_agents": [...], "improved_prompt": "...", "provider_suggestions": [...]}

GET /api/v1/ai/skills
# List all invokable skills

POST /api/v1/ai/skills/{skill_id}/invoke
# Body: {"input": "...", "context": {...}}
# Response: {"agent_to_use": "...", "context_to_inject": {...}, "suggested_prompt": "..."}

POST /api/v1/ai/brainstorm
# Body: {"task_type": "landing_page", "market_stage": "crowded", "audience": "...", "product": "..."}
# Response: {"mode": "brainstorm", "context": {frameworks, angles, formulas}}

GET /api/v1/ai/providers/status
# Check health of all external LLM providers
```

### 2. Model Tier Mapping

Map erp_staging_lmtd's pricing tiers to ongoing_agent_builder's model selection:

| ERP Tier | Plan | Agent Model | Use Cases |
|----------|------|-------------|-----------|
| Economy | Starter | Claude Haiku 3.5 | Simple tasks, routing |
| Standard | Brand/Agency | Claude Sonnet 4 | Most agents |
| Premium | Enterprise | Claude Opus 4.5 | Legal, Finance, Knowledge |

```python
# In erp_staging_lmtd: src/services/ai_service.py
TIER_TO_MODEL = {
    "economy": "haiku",
    "standard": "sonnet",
    "premium": "opus",
}

def get_tier_for_plan(plan: str) -> str:
    return {
        "starter": "economy",
        "brand": "standard",
        "agency": "standard",
        "enterprise": "premium",
    }.get(plan, "standard")
```

### 3. Module Integration Points

Each ERP module should have access to relevant agents:

| Module | Primary Agents | Skills |
|--------|---------------|--------|
| `/video` | video_script, video_storyboard, video_production | video_storyboard, video_script, voiceover |
| `/studio` | presentation, image, copy | presentation_design, image_generation |
| `/content` | content, copy, brief | copywriting, content_strategy |
| `/analytics` | social_analytics, campaign_analytics, brand_performance | analytics_dashboard, competitor_analysis |
| `/crm` | crm, scope, client_onboarding | client_health_scoring |
| `/rfp` | rfp, commercial, brief | proposal_writing, pricing_strategy |
| `/social` | social_listening, community, social_analytics | social_content, community_management |
| `/media` | media_buying, campaign | media_planning, campaign_optimization |
| `/legal` | legal | contract_review, compliance_check |
| `/finance` | invoice, forecast, budget | financial_forecasting, budget_tracking |

### 4. UI Components to Add

Add AI assistance in these locations:

```
1. Global AI Chat (floating button)
   - Uses PromptHelper to route requests
   - Available on all pages
   - Remembers context per module

2. Module-specific AI panels
   - /video: "Generate script", "Create storyboard", "Produce video"
   - /studio: "Generate image", "Create presentation"
   - /content: "Write copy", "Improve text"
   - /analytics: "Analyze data", "Generate report"

3. Inline suggestions
   - In text editors: "Improve with AI"
   - In forms: "Auto-fill with AI"
   - In dashboards: "Explain this metric"

4. Skills browser
   - Show available skills per module
   - Let users invoke skills directly
   - Display skill details and best practices
```

### 5. Credit Deduction Logic

```python
# Calculate credits based on operation
async def calculate_credits(
    operation: str,
    agent_id: str,
    input_length: int,
    output_length: int,
    external_provider: str = None,
) -> int:
    # Base credit cost
    base_credits = get_base_credits(agent_id)

    # Token multiplier
    token_credits = (input_length + output_length) * TOKEN_CREDIT_RATE

    # External provider surcharge
    if external_provider:
        provider_cost = get_provider_cost(external_provider, operation)
        provider_credits = cost_to_credits(provider_cost)
    else:
        provider_credits = 0

    return int(base_credits + token_credits + provider_credits)

# Credit rates by category
CREDIT_RATES = {
    "text_generation": 5,      # Base per request
    "image_generation": 20,    # Per image
    "video_generation": 100,   # Per 5 seconds
    "voice_synthesis": 10,     # Per 1000 chars
    "research_query": 15,      # Per query with citations
    "presentation": 30,        # Per deck
}
```

### 6. Files to Create/Modify in erp_staging_lmtd

```
src/
  services/
    ai_service.py          # NEW - Main AI service wrapper
    agent_client.py        # NEW - HTTP client for ongoing_agent_builder
  components/
    ai/
      AIChatPanel.tsx      # NEW - Global AI chat interface
      AgentSelector.tsx    # NEW - Agent picker component
      SkillBrowser.tsx     # NEW - Skills discovery UI
      BrainstormMode.tsx   # NEW - Brainstorming interface
  routes/
    api/
      ai/
        +server.ts         # NEW - AI API routes
  lib/
    ai/
      credits.ts           # UPDATE - Add AI credit calculations
      tiers.ts             # UPDATE - Add tier mapping
```

### 7. Environment Variables

Add to erp_staging_lmtd's .env:

```env
# Agent Service
AGENT_SERVICE_URL=http://localhost:8000
AGENT_SERVICE_API_KEY=your-api-key

# Enable AI features
AI_ENABLED=true
AI_DEFAULT_TIER=standard

# Rate limiting
AI_RATE_LIMIT_PER_MINUTE=60
AI_MAX_CONCURRENT_REQUESTS=10
```

### 8. Testing the Integration

```bash
# 1. Start ongoing_agent_builder
cd ongoing_agent_builder
uvicorn main:app --port 8000

# 2. Start erp_staging_lmtd
cd erp_staging_lmtd
npm run dev

# 3. Test agent execution
curl -X POST http://localhost:5173/api/ai/agent/execute \
  -H "Content-Type: application/json" \
  -d '{"agent": "prompt_helper", "input": "Help me create a video ad"}'

# 4. Test skills invocation
curl http://localhost:5173/api/ai/skills/copywriting/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "Write a headline for our new product"}'
```

## Key Integration Patterns

### Pattern 1: Direct Agent Execution

```typescript
// In erp_staging_lmtd component
import { executeAgent } from '$lib/ai/agent-client';

const result = await executeAgent({
  agent: 'image_agent',
  input: 'Create a product photo for sneakers',
  instanceId: getCurrentInstanceId(),
  tier: getUserTier(),
});
```

### Pattern 2: Skill-Based Invocation

```typescript
// User selects a skill from the UI
import { invokeSkill, executeAgent } from '$lib/ai/agent-client';

// Get skill context
const invocation = await invokeSkill('landing_page_cro', {
  input: 'Optimize our checkout page',
  context: { url: pageUrl }
});

// Execute with skill context injected
const result = await executeAgent({
  agent: invocation.agent_to_use,
  input: invocation.suggested_prompt,
  context: invocation.context_to_inject,
  instanceId: getCurrentInstanceId(),
});
```

### Pattern 3: PromptHelper Flow

```typescript
// User types natural language request
import { promptHelper, executeAgent } from '$lib/ai/agent-client';

// PromptHelper analyzes and recommends
const analysis = await promptHelper({
  input: userInput,
  context: { currentModule, brandGuidelines }
});

// Show recommendations to user
// User confirms or adjusts

// Execute recommended agent
const result = await executeAgent({
  agent: analysis.recommended_agents[0].agent,
  input: analysis.improved_prompt,
  instanceId: getCurrentInstanceId(),
});
```

### Pattern 4: Multi-Agent Workflow

```typescript
// Video production pipeline
import { createWorkflow, executeWorkflow } from '$lib/ai/agent-client';

const workflow = await createWorkflow({
  name: 'Video Production',
  steps: [
    { agent: 'video_script_agent', inputKey: 'brief' },
    { agent: 'video_storyboard_agent', inputKey: 'script', dependsOn: 'video_script_agent' },
    { agent: 'video_production_agent', inputKey: 'storyboard', dependsOn: 'video_storyboard_agent' },
  ]
});

const results = await executeWorkflow(workflow.id, {
  brief: 'Create a 30-second product video for our new sneakers...',
});
```

## Summary

This integration connects erp_staging_lmtd's ERP interface with ongoing_agent_builder's AI capabilities:

1. **47 agents** available through a unified API
2. **14 external LLM providers** for specialized tasks (video, image, voice, research)
3. **40+ marketing skills** invokable from ERP modules
4. **Credit-based billing** aligned with ERP pricing tiers
5. **PromptHelper** for intelligent routing and prompt improvement

Start by creating the `ai_service.py` client in erp_staging_lmtd that communicates with ongoing_agent_builder's REST API, then build out the UI components for each module.
```

---

## Quick Start Command

Copy this into a new Claude session with the erp_staging_lmtd repository:

```
Please help me integrate the AI agent service from ongoing_agent_builder into this ERP.

Key context:
- ongoing_agent_builder is at https://github.com/willhutson/ongoing_agent_builder (branch: claude/prep-agents-integration-970Nn)
- It has 47 agents, 14 LLM providers, and 40+ skills
- PR #280 already prepped this repo for multi-model integration

Start by:
1. Creating src/services/ai_service.py - the main wrapper for agent calls
2. Creating src/services/agent_client.py - HTTP client for the agent service
3. Adding the AI API routes in src/routes/api/ai/

Focus on:
- Tier mapping (economy/standard/premium to haiku/sonnet/opus)
- Credit deduction per operation
- Module-specific agent recommendations
```
