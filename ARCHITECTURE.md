# Agent Issue System - Architecture Plan

## Overview

This system serves as an **agent backend** for the [erp_staging_lmtd](https://github.com/willhutson/erp_staging_lmtd) ERP platform. It receives requests, bugs, and feature asks from the ERP system and spawns autonomous agents to work on them in the background.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ERP STAGING LMTD                                  │
│  (Next.js 14 / Supabase / Prisma)                                          │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Briefs    │  │    CRM      │  │  Retainers  │  │   Studio    │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │                │
│         └────────────────┴────────────────┴────────────────┘                │
│                                    │                                        │
│                           Issues / Requests                                 │
│                           (webhook/API push)                                │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ONGOING AGENT BUILDER (This System)                     │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         INTAKE LAYER                                  │  │
│  │  • REST API endpoints for issue/request submission                   │  │
│  │  • Webhook receivers from ERP                                        │  │
│  │  • GitHub issue sync (optional)                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                     │                                       │
│                                     ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      CLASSIFICATION ENGINE                            │  │
│  │  • Analyzes incoming requests                                        │  │
│  │  • Categorizes: bug, feature, enhancement, question                  │  │
│  │  • Estimates complexity and required capabilities                    │  │
│  │  • Routes to appropriate agent type                                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                     │                                       │
│                                     ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         JOB QUEUE                                     │  │
│  │  • Priority-based queue (Redis/BullMQ)                               │  │
│  │  • Job persistence and retry logic                                   │  │
│  │  • Concurrency management                                            │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                     │                                       │
│                                     ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      AGENT ORCHESTRATOR                               │  │
│  │  • Spawns appropriate agent types                                    │  │
│  │  • Manages agent lifecycle (start, monitor, terminate)              │  │
│  │  • Resource allocation and limits                                    │  │
│  │  • Progress tracking                                                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                     │                                       │
│           ┌─────────────────────────┼─────────────────────────┐            │
│           ▼                         ▼                         ▼            │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │  CODE AGENT     │    │  RESEARCH AGENT │    │  TRIAGE AGENT   │        │
│  │                 │    │                 │    │                 │        │
│  │  • Bug fixes    │    │  • Investigation│    │  • Quick assess │        │
│  │  • Features     │    │  • Root cause   │    │  • Prioritize   │        │
│  │  • Refactoring  │    │  • Solutions    │    │  • Escalate     │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                       RESULTS & REPORTING                             │  │
│  │  • Agent work summaries                                              │  │
│  │  • Pull request creation                                             │  │
│  │  • Status updates back to ERP                                        │  │
│  │  • Human review queue                                                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Runtime** | Node.js 20+ / TypeScript | Matches ERP stack, async-first |
| **Framework** | Fastify | High-performance API server |
| **Job Queue** | BullMQ + Redis | Robust, battle-tested, supports priorities |
| **Database** | PostgreSQL (shared with ERP or separate) | Prisma ORM for consistency |
| **Agent Engine** | Claude Agent SDK | Powers autonomous agents |
| **Process Mgmt** | PM2 / Docker | Production process management |
| **Monitoring** | OpenTelemetry + Grafana | Observability |

---

## Data Models

### Core Entities

```typescript
// Issue/Request coming from ERP
interface AgentIssue {
  id: string;
  externalId: string;          // ID from ERP system
  source: 'erp' | 'github' | 'manual';
  type: 'bug' | 'feature' | 'enhancement' | 'question' | 'task';
  priority: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  context: {
    module: string;            // e.g., 'briefs', 'crm', 'studio'
    affectedFiles?: string[];
    relatedIssues?: string[];
    metadata: Record<string, unknown>;
  };
  status: 'pending' | 'queued' | 'processing' | 'review' | 'completed' | 'failed';
  organizationId: string;      // Multi-tenant support
  createdAt: Date;
  updatedAt: Date;
}

// Agent job in the queue
interface AgentJob {
  id: string;
  issueId: string;
  agentType: 'code' | 'research' | 'triage' | 'review';
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed';
  priority: number;
  attempts: number;
  maxAttempts: number;
  config: {
    model: string;
    maxTokens: number;
    timeout: number;
    tools: string[];
  };
  result?: {
    summary: string;
    artifacts: Artifact[];
    pullRequestUrl?: string;
    recommendations?: string[];
  };
  logs: AgentLog[];
  startedAt?: Date;
  completedAt?: Date;
}

// Work product from agent
interface Artifact {
  id: string;
  jobId: string;
  type: 'code_change' | 'analysis' | 'recommendation' | 'documentation';
  content: string;
  filePath?: string;
  diffPatch?: string;
}
```

---

## Module Breakdown

### 1. Intake Layer (`/src/intake/`)

Handles incoming requests from multiple sources:

```
/src/intake/
├── routes/
│   ├── issues.ts          # POST /api/issues - submit new issues
│   ├── webhooks.ts        # POST /api/webhooks/erp - ERP webhooks
│   └── github.ts          # POST /api/webhooks/github - GitHub sync
├── validators/
│   └── issue.validator.ts # Zod schemas for validation
└── services/
    └── intake.service.ts  # Processing incoming requests
```

**API Endpoints:**
- `POST /api/issues` - Submit a new issue/request
- `POST /api/webhooks/erp` - Receive ERP system webhooks
- `GET /api/issues/:id` - Get issue status
- `GET /api/issues` - List issues with filters

### 2. Classification Engine (`/src/classification/`)

AI-powered request analysis:

```
/src/classification/
├── classifier.ts          # Main classification logic
├── prompts/
│   └── classify.prompt.ts # Classification prompts
└── types.ts               # Classification types
```

**Responsibilities:**
- Analyze issue content to determine type and priority
- Identify affected ERP modules
- Estimate complexity (simple/medium/complex)
- Suggest agent type and capabilities needed

### 3. Job Queue (`/src/queue/`)

BullMQ-based job management:

```
/src/queue/
├── queues/
│   ├── agent.queue.ts     # Main agent job queue
│   └── notification.queue.ts
├── workers/
│   ├── agent.worker.ts    # Processes agent jobs
│   └── notification.worker.ts
└── config.ts              # Queue configuration
```

**Features:**
- Priority queuing (critical issues first)
- Retry with exponential backoff
- Concurrency limits per organization
- Dead letter queue for failed jobs

### 4. Agent Orchestrator (`/src/agents/`)

Core agent management:

```
/src/agents/
├── orchestrator.ts        # Main orchestrator
├── types/
│   ├── code-agent.ts      # Code modification agent
│   ├── research-agent.ts  # Investigation agent
│   ├── triage-agent.ts    # Quick assessment agent
│   └── review-agent.ts    # Code review agent
├── tools/
│   ├── file-tools.ts      # File read/write/edit
│   ├── git-tools.ts       # Git operations
│   ├── search-tools.ts    # Code search
│   └── erp-tools.ts       # ERP API integration
├── prompts/
│   └── system-prompts.ts  # Agent system prompts
└── lifecycle.ts           # Start, monitor, terminate
```

**Agent Types:**

| Agent | Purpose | Capabilities |
|-------|---------|--------------|
| **Code Agent** | Fix bugs, implement features | File edit, Git, Tests |
| **Research Agent** | Investigate issues, find root cause | Search, Read, Analyze |
| **Triage Agent** | Quick assessment, routing | Classify, Prioritize |
| **Review Agent** | Review agent work, validate | Read, Compare, Validate |

### 5. ERP Integration (`/src/erp/`)

Communication with erp_staging_lmtd:

```
/src/erp/
├── client.ts              # ERP API client
├── types.ts               # ERP types/interfaces
├── sync/
│   ├── issues.sync.ts     # Sync issues bidirectionally
│   └── status.sync.ts     # Update statuses
└── webhooks/
    └── handlers.ts        # Webhook event handlers
```

**Integration Points:**
- Fetch context from ERP (project details, user info, module data)
- Push status updates back to ERP
- Create notifications in ERP
- Sync with ERP's issue tracking (if exists)

### 6. Results & Reporting (`/src/reporting/`)

Output handling:

```
/src/reporting/
├── github/
│   ├── pr-creator.ts      # Create pull requests
│   └── branch-manager.ts  # Branch management
├── notifications/
│   └── notifier.ts        # Send notifications
└── dashboard/
    ├── api.ts             # Dashboard API
    └── types.ts           # Dashboard types
```

---

## API Design

### Submit Issue
```http
POST /api/issues
Content-Type: application/json
Authorization: Bearer <token>

{
  "source": "erp",
  "externalId": "brief-123",
  "type": "bug",
  "priority": "high",
  "title": "Brief PDF export failing for large documents",
  "description": "When exporting briefs with more than 50 pages...",
  "context": {
    "module": "briefs",
    "organizationId": "org_xxx",
    "metadata": {
      "affectedUsers": ["user_123"],
      "errorLogs": "..."
    }
  }
}
```

### Response
```json
{
  "id": "issue_abc123",
  "status": "queued",
  "jobId": "job_xyz789",
  "estimatedWait": "2 minutes",
  "trackingUrl": "/api/issues/issue_abc123"
}
```

### Get Status
```http
GET /api/issues/issue_abc123
```

```json
{
  "id": "issue_abc123",
  "status": "processing",
  "job": {
    "id": "job_xyz789",
    "agentType": "code",
    "progress": 65,
    "currentStep": "Analyzing affected files",
    "logs": [
      { "time": "...", "message": "Started analysis" },
      { "time": "...", "message": "Found root cause in src/modules/briefs/export.ts" }
    ]
  }
}
```

---

## ERP Integration Setup

### In erp_staging_lmtd

Add webhook configuration to send issues to this system:

```typescript
// erp_staging_lmtd/src/lib/agent-integration.ts

const AGENT_BACKEND_URL = process.env.AGENT_BACKEND_URL;

export async function submitToAgentSystem(issue: {
  type: 'bug' | 'feature' | 'task';
  title: string;
  description: string;
  module: string;
  priority: string;
}) {
  const response = await fetch(`${AGENT_BACKEND_URL}/api/issues`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.AGENT_API_KEY}`,
    },
    body: JSON.stringify({
      source: 'erp',
      ...issue,
      context: {
        module: issue.module,
        organizationId: await getOrgContext(),
      },
    }),
  });

  return response.json();
}
```

---

## File Structure (Final)

```
/home/user/ongoing_agent_builder/
├── README.md
├── ARCHITECTURE.md              # This file
├── package.json
├── tsconfig.json
├── .env.example
├── docker-compose.yml           # Redis + optional services
├── prisma/
│   ├── schema.prisma            # Database schema
│   └── migrations/
├── src/
│   ├── index.ts                 # Entry point
│   ├── config/
│   │   ├── index.ts
│   │   └── env.ts               # Environment validation
│   ├── intake/
│   │   ├── routes/
│   │   ├── validators/
│   │   └── services/
│   ├── classification/
│   │   ├── classifier.ts
│   │   └── prompts/
│   ├── queue/
│   │   ├── queues/
│   │   ├── workers/
│   │   └── config.ts
│   ├── agents/
│   │   ├── orchestrator.ts
│   │   ├── types/
│   │   ├── tools/
│   │   ├── prompts/
│   │   └── lifecycle.ts
│   ├── erp/
│   │   ├── client.ts
│   │   ├── types.ts
│   │   └── sync/
│   ├── reporting/
│   │   ├── github/
│   │   ├── notifications/
│   │   └── dashboard/
│   └── utils/
│       ├── logger.ts
│       └── errors.ts
└── tests/
    ├── unit/
    └── integration/
```

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Project setup (TypeScript, ESLint, dependencies)
- [ ] Database schema with Prisma
- [ ] Basic API server with Fastify
- [ ] Redis + BullMQ setup

### Phase 2: Core Engine
- [ ] Issue intake endpoints
- [ ] Classification engine
- [ ] Job queue implementation
- [ ] Basic agent orchestrator

### Phase 3: Agents
- [ ] Triage agent (simplest first)
- [ ] Research agent
- [ ] Code agent
- [ ] Agent tools (file, git, search)

### Phase 4: Integration
- [ ] ERP API client
- [ ] Webhook handlers
- [ ] Status sync back to ERP
- [ ] GitHub PR creation

### Phase 5: Polish
- [ ] Dashboard API
- [ ] Monitoring/observability
- [ ] Error handling & retries
- [ ] Documentation

---

## Questions for Clarification

Before proceeding, please confirm or adjust:

1. **Database**: Should this system share the same Supabase/PostgreSQL as the ERP, or have its own database?

2. **Authentication**: Use the same NextAuth.js as ERP, or separate API key-based auth?

3. **GitHub Integration**: Do you want agents to create PRs directly to the erp_staging_lmtd repo?

4. **Agent Model**: Which Claude model should agents use? (claude-sonnet-4-20250514, claude-opus-4-5-20250101, etc.)

5. **Concurrency**: How many agents should be allowed to run simultaneously?

6. **Hosting**: Where will this run? (Same server as ERP, separate server, Docker, etc.)

---

## Next Steps

Once you approve this architecture, I'll begin implementing Phase 1:
1. Initialize the Node.js/TypeScript project
2. Set up Prisma with the database schema
3. Create the Fastify API server skeleton
4. Configure BullMQ with Redis
