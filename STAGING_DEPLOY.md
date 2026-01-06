# Staging Deployment Checklist

## Overview

To deploy the agent system to staging, we need to:
1. Add Prisma schema to ERP
2. Set up Upstash Redis (queue)
3. Copy agent module into ERP
4. Add API routes
5. Configure environment variables
6. Deploy and test

---

## Phase 1: Infrastructure Setup (Do First)

### 1.1 Create Upstash Redis Instance

1. Go to [upstash.com](https://upstash.com)
2. Create a new Redis database
3. Copy the credentials:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`

**Time:** 5 minutes

### 1.2 Get Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. Copy `ANTHROPIC_API_KEY`

**Time:** 2 minutes

---

## Phase 2: Database Schema (Prisma)

Add these models to `spokestack/prisma/schema.prisma`:

```prisma
// ============================================
// AGENT SYSTEM
// ============================================

model AgentIssue {
  id              String        @id @default(cuid())
  externalId      String?
  source          IssueSource   @default(MANUAL)
  type            IssueType
  priority        IssuePriority @default(MEDIUM)
  title           String
  description     String        @db.Text
  context         Json          @default("{}")
  status          IssueStatus   @default(PENDING)

  organizationId  String
  organization    Organization  @relation(fields: [organizationId], references: [id])
  createdById     String?
  createdBy       User?         @relation(fields: [createdById], references: [id])

  jobs            AgentJob[]

  createdAt       DateTime      @default(now())
  updatedAt       DateTime      @updatedAt

  @@index([organizationId])
  @@index([status])
  @@map("agent_issues")
}

model AgentJob {
  id              String      @id @default(cuid())
  issueId         String
  issue           AgentIssue  @relation(fields: [issueId], references: [id], onDelete: Cascade)

  agentType       String
  model           String
  status          JobStatus   @default(PENDING)
  priority        Int         @default(5)

  attempts        Int         @default(0)
  maxAttempts     Int         @default(3)
  config          Json        @default("{}")
  result          Json?
  error           String?     @db.Text

  organizationId  String

  artifacts       AgentArtifact[]
  logs            AgentLog[]

  startedAt       DateTime?
  completedAt     DateTime?
  createdAt       DateTime    @default(now())
  updatedAt       DateTime    @updatedAt

  @@index([issueId])
  @@index([status])
  @@index([organizationId])
  @@map("agent_jobs")
}

model AgentArtifact {
  id              String        @id @default(cuid())
  jobId           String
  job             AgentJob      @relation(fields: [jobId], references: [id], onDelete: Cascade)

  type            ArtifactType
  name            String
  content         String        @db.Text
  filePath        String?
  diffPatch       String?       @db.Text
  metadata        Json          @default("{}")

  createdAt       DateTime      @default(now())

  @@index([jobId])
  @@map("agent_artifacts")
}

model AgentLog {
  id              String      @id @default(cuid())
  jobId           String
  job             AgentJob    @relation(fields: [jobId], references: [id], onDelete: Cascade)

  level           LogLevel    @default(INFO)
  message         String
  data            Json?

  timestamp       DateTime    @default(now())

  @@index([jobId])
  @@index([timestamp])
  @@map("agent_logs")
}

model AgentFeedback {
  id              String              @id @default(cuid())
  jobId           String
  issueId         String
  agentType       String

  rating          Int                 // 1-5
  outcome         FeedbackOutcome
  comment         String?             @db.Text
  tags            String[]            @default([])

  userId          String
  organizationId  String

  kanbanCardId    String?
  improvementStatus ImprovementStatus @default(PENDING)
  analysisResult  Json?

  createdAt       DateTime            @default(now())

  @@index([organizationId])
  @@index([agentType])
  @@index([improvementStatus])
  @@map("agent_feedback")
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

enum FeedbackOutcome {
  SOLVED
  PARTIAL
  NOT_SOLVED
  MADE_WORSE
}

enum ImprovementStatus {
  PENDING
  ANALYZED
  IMPLEMENTED
  DISMISSED
}
```

Then run:
```bash
cd spokestack
npx prisma migrate dev --name add_agent_system
```

**Time:** 10 minutes

---

## Phase 3: Copy Agent Module to ERP

### Option A: Git Submodule (Recommended)
```bash
cd /path/to/erp_staging_lmtd/spokestack/src/modules
git submodule add https://github.com/willhutson/ongoing_agent_builder agents
```

### Option B: Direct Copy
```bash
# Copy source files
cp -r /path/to/ongoing_agent_builder/src/* \
  /path/to/erp_staging_lmtd/spokestack/src/modules/agents/

# Copy docs
cp /path/to/ongoing_agent_builder/*.md \
  /path/to/erp_staging_lmtd/spokestack/src/modules/agents/
```

**Time:** 5 minutes

---

## Phase 4: Add API Routes

Create these files in `spokestack/src/app/api/agents/`:

### `route.ts` - Submit Issue
```typescript
// spokestack/src/app/api/agents/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { getOrchestrator } from '@/modules/agents/core/orchestrator';
import prisma from '@/lib/prisma';

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const body = await request.json();
  const orchestrator = getOrchestrator(prisma);

  const result = await orchestrator.submitIssue(
    body,
    session.user.organizationId,
    session.user.id
  );

  return NextResponse.json(result);
}

export async function GET(request: NextRequest) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const issues = await prisma.agentIssue.findMany({
    where: { organizationId: session.user.organizationId },
    include: { jobs: { take: 1, orderBy: { createdAt: 'desc' } } },
    orderBy: { createdAt: 'desc' },
    take: 50,
  });

  return NextResponse.json(issues);
}
```

### `[id]/route.ts` - Get Status
```typescript
// spokestack/src/app/api/agents/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { getOrchestrator } from '@/modules/agents/core/orchestrator';
import prisma from '@/lib/prisma';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const orchestrator = getOrchestrator(prisma);
  const status = await orchestrator.getIssueStatus(
    params.id,
    session.user.organizationId
  );

  if (!status) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }

  return NextResponse.json(status);
}
```

### `health/route.ts` - Health Check
```typescript
// spokestack/src/app/api/agents/health/route.ts
import { NextResponse } from 'next/server';
import { checkHealth, AGENT_VERSION } from '@/modules/agents';

export async function GET() {
  const health = await checkHealth();

  return NextResponse.json({
    ...health,
    version: AGENT_VERSION,
  }, {
    status: health.status === 'healthy' ? 200 : 503,
  });
}
```

**Time:** 15 minutes

---

## Phase 5: Environment Variables

Add to Vercel (or `.env.local` for local testing):

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
AGENT_ENABLED=true

# Optional (for full features)
AGENT_DEBUG=false
AGENT_MAX_CONCURRENCY=5
AGENT_DEFAULT_MODEL=sonnet

# GitHub (for PR creation)
GITHUB_TOKEN=ghp_xxx
```

**Time:** 5 minutes

---

## Phase 6: Install Dependencies

```bash
cd spokestack
pnpm add @anthropic-ai/sdk @upstash/redis @upstash/ratelimit bullmq zod
```

**Time:** 2 minutes

---

## Phase 7: Deploy to Staging

```bash
# Commit all changes
git add .
git commit -m "Add agent system module"

# Push to staging branch
git push origin staging

# Vercel auto-deploys from staging branch
```

**Time:** 5 minutes (deploy takes ~2-3 min)

---

## Phase 8: Test It!

### Quick Test via API
```bash
# Submit a test issue
curl -X POST https://your-staging-url.vercel.app/api/agents \
  -H "Content-Type: application/json" \
  -H "Cookie: your-auth-cookie" \
  -d '{
    "type": "BUG",
    "title": "Test issue",
    "description": "Testing the agent system",
    "context": { "module": "briefs" }
  }'

# Check status
curl https://your-staging-url.vercel.app/api/agents/ISSUE_ID
```

### Or Add a Quick UI Button
Add to any page in the ERP:
```tsx
<button onClick={async () => {
  const res = await fetch('/api/agents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      type: 'BUG',
      title: 'Test agent',
      description: 'Testing the agent system works',
    }),
  });
  console.log(await res.json());
}}>
  Test Agent
</button>
```

---

## Total Time Estimate

| Phase | Time |
|-------|------|
| Infrastructure (Upstash, Anthropic) | 10 min |
| Database Schema | 10 min |
| Copy Module | 5 min |
| API Routes | 15 min |
| Environment Variables | 5 min |
| Dependencies | 2 min |
| Deploy | 5 min |
| **Total** | **~50 minutes** |

---

## What Works After Deployment

✅ Submit issues via API
✅ Issues classified by AI
✅ Jobs queued and processed
✅ Agents execute with tools
✅ Results stored in database
✅ Health check endpoint

## What Needs More Work (Phase 2)

- [ ] Feedback collection UI
- [ ] Agent dashboard in admin
- [ ] Improvement board automation
- [ ] Slack notifications
- [ ] Real-time status updates (Pusher)

---

## Quick Start Commands

```bash
# 1. Set up infrastructure (do once)
# - Create Upstash Redis at upstash.com
# - Get Anthropic API key at console.anthropic.com

# 2. In ERP repo
cd /path/to/erp_staging_lmtd/spokestack

# 3. Add dependencies
pnpm add @anthropic-ai/sdk @upstash/redis bullmq zod

# 4. Copy agent module
cp -r /path/to/ongoing_agent_builder/src src/modules/agents

# 5. Add schema to prisma/schema.prisma (copy from above)

# 6. Run migration
npx prisma migrate dev --name add_agent_system

# 7. Add API routes (copy from above)
mkdir -p src/app/api/agents

# 8. Add env vars to .env.local
echo "ANTHROPIC_API_KEY=your-key" >> .env.local
echo "UPSTASH_REDIS_REST_URL=your-url" >> .env.local
echo "UPSTASH_REDIS_REST_TOKEN=your-token" >> .env.local
echo "AGENT_ENABLED=true" >> .env.local

# 9. Test locally
pnpm dev

# 10. Deploy
git add . && git commit -m "Add agent system" && git push
```
