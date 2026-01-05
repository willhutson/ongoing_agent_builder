# Ongoing Agent Builder

An AI-powered agent system that integrates with [SpokeStack ERP](https://github.com/willhutson/erp_staging_lmtd) to autonomously handle bugs, feature requests, and platform operations.

## Overview

This system deploys **embedded within the ERP** and provides:

- **104 Specialized Agents** across 17 modules (6+ per module)
- **Intelligent Triage** - AI classifies and routes incoming issues
- **Dynamic Model Selection** - Uses Haiku/Sonnet/Opus based on complexity
- **Multi-Tenant Isolation** - Safe for SaaS deployment
- **Instance Deployment Agent** - Automates new client onboarding

## Key Features

### 🤖 Agent Types

| Category | Purpose | Example Agents |
|----------|---------|----------------|
| **Meta** | Platform-wide operations | Triage, Research, Deployment, Review |
| **Module-Specific** | Feature/bug handling | Briefs, Time, CRM, Studio, LMS, etc. |

### 🚀 Instance Deployment Agent

A comprehensive onboarding agent that:
- Conducts interview with new clients
- Analyzes business needs and recommends modules
- Configures initial instance settings
- Seeds database with org-specific data
- Generates custom onboarding documentation

### 📊 Adaptive Intelligence

- **Complexity Analysis**: Scores issues 1-10 for model selection
- **Token Optimization**: Haiku for simple, Opus for complex
- **Historical Learning**: Improves routing based on outcomes

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design and data models |
| [AGENTS.md](./AGENTS.md) | Full catalog of 104 agents |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | ERP integration and deployment guide |

## Quick Start

### 1. Deploy to ERP

```bash
# Clone into ERP modules
cd /path/to/erp_staging_lmtd/spokestack/src/modules
git clone https://github.com/willhutson/ongoing_agent_builder agents

# Install dependencies
pnpm add @anthropic-ai/sdk @upstash/redis bullmq

# Run migrations
npx prisma migrate dev --name add_agent_system
```

### 2. Configure Environment

```env
# Required
ANTHROPIC_API_KEY=sk-ant-xxx
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
AGENT_ENABLED=true

# Optional
AGENT_MAX_CONCURRENCY=5
AGENT_DEFAULT_MODEL=sonnet
GITHUB_TOKEN=ghp_xxx  # For PR creation
```

### 3. Submit an Issue

```typescript
// Via API
const response = await fetch('/api/agents', {
  method: 'POST',
  body: JSON.stringify({
    type: 'BUG',
    title: 'Brief status not updating',
    description: 'When I click submit, the status stays on draft...',
    context: { module: 'briefs' }
  })
});

// Via Server Action
import { submitIssue } from '@/modules/agents/actions';
await submitIssue({ type: 'BUG', title: '...', description: '...' });
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPOKESTACK ERP (Vercel)                      │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   AGENT MODULE                           │  │
│   │                                                          │  │
│   │  Issue → Triage → Queue → Agent → Review → PR/Complete  │  │
│   │                                                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   Shared: Auth (Supabase) • DB (Prisma) • Queue (Upstash)      │
└─────────────────────────────────────────────────────────────────┘
```

## Module Coverage

| Module | Agents | Key Capabilities |
|--------|--------|------------------|
| Briefs | 7 | Status workflow, assignment, kanban, notifications |
| Time Tracking | 6 | Timer, timesheets, billable hours, reports |
| Resources | 6 | Capacity grid, workload balancing, forecasting |
| Leave | 6 | Requests, approvals, balance tracking, policies |
| RFP | 6 | Pipeline, documents, estimation, conversion |
| Retainers | 6 | Burn rate, scope changes, health monitoring |
| Studio | 7 | Content calendar, AI generation, publishing |
| CRM | 6 | Pipeline, contacts, activities, automation |
| LMS | 6 | Courses, assessments, enrollment, certificates |
| Boards | 6 | Cards, checklists, automation, views |
| Workflow | 6 | Designer, triggers, execution, approvals |
| Chat | 6 | Channels, messages, notifications, search |
| Analytics | 6 | Dashboards, widgets, metrics, alerts |
| Surveys | 6 | Builder, distribution, analytics, NPS |
| Integrations | 6 | Slack, Google, webhooks, API keys |
| Admin | 6 | Users, permissions, audit, notifications |

## Tech Stack

- **Runtime**: Node.js 20+ / TypeScript
- **Framework**: Next.js 14 (embedded in ERP)
- **AI**: Claude API (Anthropic SDK)
- **Queue**: Upstash Redis / BullMQ
- **Database**: PostgreSQL (Supabase) via Prisma
- **Auth**: Supabase Auth (shared with ERP)

## Development

```bash
# Run locally
pnpm dev

# Type check
pnpm exec tsc --noEmit

# Test
pnpm test
```

## Roadmap

- [x] Architecture design
- [x] Agent catalog (104 agents)
- [x] Deployment strategy
- [ ] Core engine implementation
- [ ] Agent SDK integration
- [ ] Queue system
- [ ] Triage agent
- [ ] Module-specific agents
- [ ] Instance Deployment agent
- [ ] Admin dashboard

## License

Proprietary - TeamLMTD / SpokeStack
