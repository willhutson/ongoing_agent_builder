# Deployment Strategy

This document outlines how to deploy the Agent System into the SpokeStack ERP platform, ensuring reliability, debuggability, and seamless upgrades.

---

## Deployment Architecture

The agent system deploys **embedded within the ERP** rather than as a separate service. This approach:

- ✅ Shares authentication (Supabase Auth)
- ✅ Shares database (same Prisma schema)
- ✅ Simplifies multi-tenant isolation
- ✅ Reduces infrastructure complexity
- ✅ Enables direct access to ERP data and context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VERCEL DEPLOYMENT                                    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SPOKESTACK ERP                                    │   │
│  │                    (Next.js 14 App)                                  │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │   │
│  │  │   Frontend   │  │  API Routes  │  │    AGENT MODULE          │  │   │
│  │  │   (React)    │  │   (/api/*)   │  │  /src/modules/agents/    │  │   │
│  │  └──────────────┘  └──────────────┘  │                          │  │   │
│  │                                       │  • Agent Orchestrator    │  │   │
│  │                                       │  • Agent Types           │  │   │
│  │                                       │  • Queue Workers         │  │   │
│  │                                       │  • Tools & Prompts       │  │   │
│  │                                       └──────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│    Supabase      │  │      Redis       │  │    GitHub        │
│   PostgreSQL     │  │   (Upstash)      │  │   (PR Creation)  │
│   + Auth         │  │   Job Queue      │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## Integration Points

### 1. Directory Structure in ERP

```
spokestack/
├── src/
│   ├── app/
│   │   └── api/
│   │       └── agents/                    # Agent API routes
│   │           ├── route.ts               # POST /api/agents - Submit issue
│   │           ├── [id]/
│   │           │   └── route.ts           # GET /api/agents/:id - Status
│   │           ├── webhook/
│   │           │   └── route.ts           # Internal webhook receiver
│   │           └── admin/
│   │               └── route.ts           # Admin controls
│   │
│   ├── modules/
│   │   └── agents/                        # 🆕 AGENT MODULE
│   │       ├── CLAUDE.md                  # Module documentation
│   │       ├── README.md                  # Developer guide
│   │       │
│   │       ├── config/
│   │       │   ├── index.ts               # Agent configuration
│   │       │   ├── models.ts              # Model selection config
│   │       │   └── limits.ts              # Rate limits, concurrency
│   │       │
│   │       ├── core/
│   │       │   ├── orchestrator.ts        # Main orchestration logic
│   │       │   ├── classifier.ts          # Issue classification
│   │       │   ├── executor.ts            # Agent execution engine
│   │       │   └── lifecycle.ts           # Start, monitor, terminate
│   │       │
│   │       ├── queue/
│   │       │   ├── client.ts              # Queue client (Upstash/BullMQ)
│   │       │   ├── producer.ts            # Job submission
│   │       │   └── consumer.ts            # Job processing
│   │       │
│   │       ├── agents/
│   │       │   ├── base.ts                # Base agent class
│   │       │   ├── meta/
│   │       │   │   ├── triage.ts
│   │       │   │   ├── research.ts
│   │       │   │   ├── deployment.ts      # Instance deployment agent
│   │       │   │   └── review.ts
│   │       │   ├── briefs/
│   │       │   │   ├── status-workflow.ts
│   │       │   │   ├── assignment.ts
│   │       │   │   └── ...
│   │       │   ├── time/
│   │       │   ├── resources/
│   │       │   └── [other-modules]/
│   │       │
│   │       ├── tools/
│   │       │   ├── file.ts                # File read/write/edit
│   │       │   ├── git.ts                 # Git operations
│   │       │   ├── search.ts              # Code search
│   │       │   ├── database.ts            # Prisma queries
│   │       │   └── erp.ts                 # ERP-specific operations
│   │       │
│   │       ├── prompts/
│   │       │   ├── system/
│   │       │   │   ├── base.ts
│   │       │   │   └── [module].ts
│   │       │   └── templates/
│   │       │
│   │       ├── types/
│   │       │   ├── index.ts
│   │       │   ├── agent.ts
│   │       │   ├── job.ts
│   │       │   └── issue.ts
│   │       │
│   │       ├── actions/                   # Server Actions
│   │       │   ├── submit-issue.ts
│   │       │   ├── get-status.ts
│   │       │   └── admin-actions.ts
│   │       │
│   │       ├── components/                # UI components
│   │       │   ├── AgentStatus.tsx
│   │       │   ├── AgentLogs.tsx
│   │       │   ├── IssueSubmitForm.tsx
│   │       │   └── AgentDashboard.tsx
│   │       │
│   │       └── lib/
│   │           ├── claude.ts              # Claude SDK wrapper
│   │           ├── github.ts              # GitHub PR creation
│   │           └── telemetry.ts           # Observability
│   │
│   └── lib/
│       └── agents.ts                      # Re-exports for easy imports
│
├── prisma/
│   └── schema.prisma                      # Add agent tables
│
└── package.json                           # Add dependencies
```

---

### 2. Prisma Schema Additions

Add to `/spokestack/prisma/schema.prisma`:

```prisma
// ============================================
// AGENT SYSTEM MODELS
// ============================================

model AgentIssue {
  id              String        @id @default(cuid())
  externalId      String?       // ID from external source
  source          IssueSource   @default(MANUAL)
  type            IssueType
  priority        IssuePriority @default(MEDIUM)
  title           String
  description     String
  context         Json          @default("{}")
  status          IssueStatus   @default(PENDING)

  // Multi-tenant
  organizationId  String
  organization    Organization  @relation(fields: [organizationId], references: [id])

  // Relationships
  jobs            AgentJob[]
  createdById     String?
  createdBy       User?         @relation(fields: [createdById], references: [id])

  // Timestamps
  createdAt       DateTime      @default(now())
  updatedAt       DateTime      @updatedAt

  @@index([organizationId])
  @@index([status])
  @@index([type])
}

model AgentJob {
  id              String        @id @default(cuid())
  issueId         String
  issue           AgentIssue    @relation(fields: [issueId], references: [id])

  agentType       String        // e.g., "briefs.status-workflow"
  model           String        // e.g., "sonnet", "opus", "haiku"
  status          JobStatus     @default(PENDING)
  priority        Int           @default(5)

  // Execution
  attempts        Int           @default(0)
  maxAttempts     Int           @default(3)
  startedAt       DateTime?
  completedAt     DateTime?
  error           String?

  // Configuration
  config          Json          @default("{}")

  // Results
  result          Json?
  artifacts       AgentArtifact[]
  logs            AgentLog[]

  // Multi-tenant
  organizationId  String

  // Timestamps
  createdAt       DateTime      @default(now())
  updatedAt       DateTime      @updatedAt

  @@index([issueId])
  @@index([status])
  @@index([organizationId])
}

model AgentArtifact {
  id              String        @id @default(cuid())
  jobId           String
  job             AgentJob      @relation(fields: [jobId], references: [id])

  type            ArtifactType
  name            String
  content         String        @db.Text
  filePath        String?
  diffPatch       String?       @db.Text
  metadata        Json          @default("{}")

  createdAt       DateTime      @default(now())

  @@index([jobId])
}

model AgentLog {
  id              String        @id @default(cuid())
  jobId           String
  job             AgentJob      @relation(fields: [jobId], references: [id])

  level           LogLevel      @default(INFO)
  message         String
  data            Json?
  timestamp       DateTime      @default(now())

  @@index([jobId])
  @@index([timestamp])
}

// Enums
enum IssueSource {
  MANUAL
  ERP_TRIGGER
  GITHUB
  WEBHOOK
  SCHEDULED
}

enum IssueType {
  BUG
  FEATURE
  ENHANCEMENT
  QUESTION
  TASK
  DEPLOYMENT
}

enum IssuePriority {
  CRITICAL
  HIGH
  MEDIUM
  LOW
}

enum IssueStatus {
  PENDING
  QUEUED
  PROCESSING
  REVIEW
  COMPLETED
  FAILED
  CANCELLED
}

enum JobStatus {
  PENDING
  RUNNING
  PAUSED
  COMPLETED
  FAILED
  CANCELLED
}

enum ArtifactType {
  CODE_CHANGE
  ANALYSIS
  RECOMMENDATION
  DOCUMENTATION
  PULL_REQUEST
  CONFIG
}

enum LogLevel {
  DEBUG
  INFO
  WARN
  ERROR
}
```

---

### 3. Package Dependencies

Add to `/spokestack/package.json`:

```json
{
  "dependencies": {
    "@anthropic-ai/sdk": "^0.30.0",
    "@upstash/redis": "^1.28.0",
    "@upstash/ratelimit": "^1.0.0",
    "bullmq": "^5.0.0",
    "ioredis": "^5.3.0",
    "octokit": "^3.1.0",
    "zod": "^3.22.0"
  }
}
```

---

### 4. Environment Variables

Add to Vercel environment:

```env
# Agent System
ANTHROPIC_API_KEY=sk-ant-xxx
AGENT_ENABLED=true
AGENT_MAX_CONCURRENCY=5
AGENT_DEFAULT_MODEL=sonnet

# Queue (Upstash Redis)
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx

# GitHub (for PR creation)
GITHUB_TOKEN=ghp_xxx
GITHUB_REPO_OWNER=willhutson
GITHUB_REPO_NAME=erp_staging_lmtd

# Telemetry (optional)
AGENT_TELEMETRY_ENABLED=true
```

---

## Deployment Process

### Initial Setup

```bash
# 1. Clone this repo into the ERP
cd /path/to/erp_staging_lmtd/spokestack/src/modules
git clone https://github.com/willhutson/ongoing_agent_builder agents

# 2. Or copy as a module
cp -r /path/to/ongoing_agent_builder/src/* agents/

# 3. Update Prisma schema
# Copy schema additions to prisma/schema.prisma

# 4. Run migration
npx prisma migrate dev --name add_agent_system

# 5. Install dependencies
pnpm add @anthropic-ai/sdk @upstash/redis bullmq ioredis octokit

# 6. Set environment variables in Vercel
# Add all AGENT_* and ANTHROPIC_* vars

# 7. Deploy
git add .
git commit -m "Add agent system module"
git push
```

### Automated Deployment Script

Create `/spokestack/scripts/deploy-agents.sh`:

```bash
#!/bin/bash
set -e

echo "🤖 Deploying Agent System..."

# Variables
AGENT_REPO="https://github.com/willhutson/ongoing_agent_builder.git"
AGENT_DIR="src/modules/agents"
BACKUP_DIR=".agent-backup-$(date +%Y%m%d-%H%M%S)"

# Backup existing
if [ -d "$AGENT_DIR" ]; then
  echo "📦 Backing up existing agent module..."
  cp -r "$AGENT_DIR" "$BACKUP_DIR"
fi

# Pull latest
echo "⬇️  Pulling latest agent code..."
if [ -d "$AGENT_DIR/.git" ]; then
  cd "$AGENT_DIR"
  git pull origin main
  cd -
else
  rm -rf "$AGENT_DIR"
  git clone "$AGENT_REPO" "$AGENT_DIR"
fi

# Install deps
echo "📦 Installing dependencies..."
pnpm install

# Generate Prisma
echo "🗄️  Generating Prisma client..."
npx prisma generate

# Run migrations (if any)
echo "🗄️  Running migrations..."
npx prisma migrate deploy

# Verify
echo "✅ Verifying deployment..."
pnpm exec tsc --noEmit

echo "🎉 Agent system deployed successfully!"
echo ""
echo "To rollback: cp -r $BACKUP_DIR $AGENT_DIR"
```

---

## Debugging Strategy

### 1. Log Levels and Structured Logging

```typescript
// src/modules/agents/lib/telemetry.ts

import { prisma } from '@/lib/prisma';

export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

export async function agentLog(
  jobId: string,
  level: LogLevel,
  message: string,
  data?: Record<string, unknown>
) {
  // Console log for immediate visibility
  const prefix = {
    DEBUG: '🔍',
    INFO: 'ℹ️',
    WARN: '⚠️',
    ERROR: '❌',
  }[level];

  console.log(`${prefix} [Agent:${jobId}] ${message}`, data || '');

  // Persist to database
  await prisma.agentLog.create({
    data: {
      jobId,
      level,
      message,
      data: data ? JSON.stringify(data) : null,
    },
  });
}

// Usage
await agentLog(job.id, 'INFO', 'Starting code analysis', {
  files: ['src/modules/briefs/actions/index.ts'],
  issue: issue.title,
});
```

### 2. Debug Mode

```typescript
// src/modules/agents/config/index.ts

export const agentConfig = {
  debug: process.env.AGENT_DEBUG === 'true',

  // When debug is enabled:
  // - Verbose logging
  // - No parallel execution
  // - Extended timeouts
  // - Dry-run mode for destructive operations
};
```

### 3. Admin Debug Panel

Create `/spokestack/src/app/(platform)/admin/agents/page.tsx`:

```typescript
// Real-time agent monitoring dashboard
export default function AgentDebugPanel() {
  return (
    <div>
      <h1>Agent System Debug</h1>

      {/* Active Jobs */}
      <section>
        <h2>Active Jobs</h2>
        <AgentJobList status="RUNNING" />
      </section>

      {/* Job Queue */}
      <section>
        <h2>Queue Status</h2>
        <QueueStats />
      </section>

      {/* Recent Logs */}
      <section>
        <h2>Recent Logs</h2>
        <AgentLogStream />
      </section>

      {/* Debug Actions */}
      <section>
        <h2>Debug Actions</h2>
        <button onClick={pauseAllAgents}>Pause All</button>
        <button onClick={resumeAllAgents}>Resume All</button>
        <button onClick={clearQueue}>Clear Queue</button>
      </section>
    </div>
  );
}
```

### 4. Error Tracking

```typescript
// src/modules/agents/core/executor.ts

export async function executeAgent(job: AgentJob) {
  try {
    await agentLog(job.id, 'INFO', 'Agent execution started');

    // ... execution logic

  } catch (error) {
    // Structured error capture
    const errorDetails = {
      name: error.name,
      message: error.message,
      stack: error.stack,
      context: {
        jobId: job.id,
        agentType: job.agentType,
        issueId: job.issueId,
        attempt: job.attempts,
      },
    };

    await agentLog(job.id, 'ERROR', 'Agent execution failed', errorDetails);

    // Update job status
    await prisma.agentJob.update({
      where: { id: job.id },
      data: {
        status: 'FAILED',
        error: JSON.stringify(errorDetails),
      },
    });

    // Optional: Send to error tracking service
    // await Sentry.captureException(error, { extra: errorDetails });

    throw error;
  }
}
```

---

## Hot Upgrade Strategy

### 1. Feature Flags

```typescript
// src/modules/agents/config/flags.ts

export const agentFlags = {
  // Master kill switch
  enabled: process.env.AGENT_ENABLED === 'true',

  // Per-agent-type flags
  agents: {
    'briefs.status-workflow': true,
    'meta.deployment': true,
    // Disable specific agents during issues
    'time.timer': process.env.AGENT_TIME_TIMER !== 'false',
  },

  // Feature flags
  features: {
    parallelExecution: true,
    githubPRCreation: true,
    slackNotifications: true,
  },
};
```

### 2. Version Tracking

```typescript
// src/modules/agents/config/version.ts

export const AGENT_VERSION = {
  version: '1.2.3',
  commit: process.env.VERCEL_GIT_COMMIT_SHA?.slice(0, 7) || 'local',
  deployedAt: process.env.VERCEL_GIT_COMMIT_DATE || new Date().toISOString(),
};

// Log version on startup
console.log(`🤖 Agent System v${AGENT_VERSION.version} (${AGENT_VERSION.commit})`);
```

### 3. Rolling Upgrades

For zero-downtime upgrades:

```typescript
// src/modules/agents/core/lifecycle.ts

export async function gracefulShutdown() {
  console.log('🛑 Agent system shutting down gracefully...');

  // 1. Stop accepting new jobs
  await pauseQueue();

  // 2. Wait for running jobs to complete (with timeout)
  const runningJobs = await prisma.agentJob.findMany({
    where: { status: 'RUNNING' },
  });

  if (runningJobs.length > 0) {
    console.log(`⏳ Waiting for ${runningJobs.length} jobs to complete...`);

    // Wait up to 5 minutes
    await Promise.race([
      waitForJobsToComplete(runningJobs),
      sleep(5 * 60 * 1000),
    ]);
  }

  // 3. Mark any still-running jobs for retry
  await prisma.agentJob.updateMany({
    where: { status: 'RUNNING' },
    data: { status: 'PENDING' }, // Will be picked up after upgrade
  });

  console.log('✅ Agent system shutdown complete');
}
```

### 4. Rollback Procedure

```bash
#!/bin/bash
# scripts/rollback-agents.sh

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
  echo "Usage: ./rollback-agents.sh <backup-dir>"
  echo ""
  echo "Available backups:"
  ls -la .agent-backup-*
  exit 1
fi

echo "🔄 Rolling back to $BACKUP_DIR..."

# Pause agents
curl -X POST "$VERCEL_URL/api/agents/admin" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"action": "pause"}'

# Swap directories
rm -rf src/modules/agents
cp -r "$BACKUP_DIR" src/modules/agents

# Deploy
git add .
git commit -m "Rollback agent system to $BACKUP_DIR"
git push

echo "✅ Rollback complete. Agents will resume after Vercel deployment."
```

---

## Monitoring & Alerting

### 1. Health Check Endpoint

```typescript
// src/app/api/agents/health/route.ts

import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { getQueueStats } from '@/modules/agents/queue/client';

export async function GET() {
  const [
    pendingJobs,
    runningJobs,
    failedRecently,
    queueStats,
  ] = await Promise.all([
    prisma.agentJob.count({ where: { status: 'PENDING' } }),
    prisma.agentJob.count({ where: { status: 'RUNNING' } }),
    prisma.agentJob.count({
      where: {
        status: 'FAILED',
        updatedAt: { gte: new Date(Date.now() - 60 * 60 * 1000) },
      },
    }),
    getQueueStats(),
  ]);

  const healthy = failedRecently < 10 && runningJobs <= 10;

  return NextResponse.json({
    status: healthy ? 'healthy' : 'degraded',
    version: AGENT_VERSION,
    stats: {
      pending: pendingJobs,
      running: runningJobs,
      failedLastHour: failedRecently,
      queue: queueStats,
    },
    timestamp: new Date().toISOString(),
  }, {
    status: healthy ? 200 : 503,
  });
}
```

### 2. Vercel Cron for Monitoring

```json
// vercel.json
{
  "crons": [
    {
      "path": "/api/agents/cron/health-check",
      "schedule": "*/5 * * * *"
    },
    {
      "path": "/api/agents/cron/cleanup",
      "schedule": "0 3 * * *"
    }
  ]
}
```

---

## Multi-Tenant Considerations

### 1. Tenant Isolation

```typescript
// Every agent operation includes organizationId

export async function submitIssue(data: IssueInput, session: Session) {
  return prisma.agentIssue.create({
    data: {
      ...data,
      organizationId: session.user.organizationId, // Always scoped
      createdById: session.user.id,
    },
  });
}

export async function getIssues(session: Session) {
  return prisma.agentIssue.findMany({
    where: {
      organizationId: session.user.organizationId, // Always filtered
    },
  });
}
```

### 2. Rate Limiting per Tenant

```typescript
// src/modules/agents/config/limits.ts

import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

// Per-organization rate limits
export const orgRateLimiter = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(100, '1 h'), // 100 agent jobs per hour per org
  analytics: true,
  prefix: 'agent:ratelimit:org',
});

export async function checkRateLimit(organizationId: string) {
  const { success, remaining, reset } = await orgRateLimiter.limit(organizationId);

  if (!success) {
    throw new Error(`Rate limit exceeded. Resets in ${reset - Date.now()}ms`);
  }

  return { remaining };
}
```

### 3. Resource Quotas

```typescript
// Different tiers get different agent capabilities

interface OrgAgentQuotas {
  maxConcurrentJobs: number;
  maxJobsPerDay: number;
  allowedModels: ('haiku' | 'sonnet' | 'opus')[];
  allowedAgentTypes: string[];
}

const quotasByTier: Record<string, OrgAgentQuotas> = {
  free: {
    maxConcurrentJobs: 1,
    maxJobsPerDay: 10,
    allowedModels: ['haiku'],
    allowedAgentTypes: ['meta.triage', 'meta.research'],
  },
  pro: {
    maxConcurrentJobs: 3,
    maxJobsPerDay: 100,
    allowedModels: ['haiku', 'sonnet'],
    allowedAgentTypes: ['*'], // All agents
  },
  enterprise: {
    maxConcurrentJobs: 10,
    maxJobsPerDay: 1000,
    allowedModels: ['haiku', 'sonnet', 'opus'],
    allowedAgentTypes: ['*'],
  },
};
```

---

## Answers to Your Questions

### GitHub PRs for Multi-Tenant

**Recommendation: No direct PRs to main repo**

For multi-tenant SaaS, agents should NOT create PRs directly to `erp_staging_lmtd`. Instead:

1. **Org-Specific Branches**: Create branches like `agent/org-{orgId}/{issue-id}`
2. **Fork Model** (for true multi-tenant): Each org could have a fork
3. **Config-Only Changes**: Agents modify org-specific config, not core code
4. **Review Queue**: Agent suggestions go to a review queue, not auto-merged

The Instance Deployment Agent is the exception - it operates at the platform level, not tenant level.

### Model Selection

Dynamic selection based on:
- Issue complexity score (1-10)
- Historical success rates
- Token cost optimization
- Latency requirements

### Concurrency

**Recommended: 5 concurrent agents globally, 2 per organization**

This balances:
- API rate limits
- Database load
- User experience (queue wait times)
- Cost management

Can be adjusted via `AGENT_MAX_CONCURRENCY` env var.

---

## Checklist for Deployment

### Pre-Deployment
- [ ] Anthropic API key configured
- [ ] Upstash Redis configured
- [ ] GitHub token (if PR creation enabled)
- [ ] Prisma schema updated
- [ ] Migrations applied
- [ ] Dependencies installed

### Deployment
- [ ] Code merged to main
- [ ] Vercel deployment successful
- [ ] Health check passing
- [ ] Test agent submission

### Post-Deployment
- [ ] Monitor error rates
- [ ] Check queue processing
- [ ] Verify multi-tenant isolation
- [ ] Test rollback procedure

---

## Support & Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Jobs stuck in PENDING | Redis connection | Check Upstash credentials |
| Agent timeout | Complex issue | Increase timeout or use Opus |
| PR creation fails | GitHub token | Verify token permissions |
| Multi-tenant leak | Missing orgId filter | Check all queries |

### Getting Help

1. Check agent logs: `/admin/agents/logs`
2. Review health check: `/api/agents/health`
3. Check Vercel function logs
4. Review this documentation
