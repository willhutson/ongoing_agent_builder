# Upstash Setup Guide

## What is Upstash?

Upstash is **serverless Redis** - a managed Redis database designed for serverless environments like Vercel.

### Why Redis for Agents?

```
Without Queue:
User → API → Agent runs (30 sec) → Response
         ↑ User waits 30 seconds 😫

With Queue:
User → API → Queue job → Response (instant!)
              ↓
         Worker picks up job
              ↓
         Agent runs in background
              ↓
         Results saved to DB
```

Redis holds the job queue. Workers process jobs asynchronously.

### Why Upstash vs Regular Redis?

| Regular Redis | Upstash |
|--------------|---------|
| Needs persistent connection | HTTP-based (REST API) |
| Doesn't work well with serverless | Built for Vercel/serverless |
| You manage the server | Fully managed |
| Pay for always-on server | Pay per request |

---

## Setup Steps

### 1. Create Account

1. Go to [upstash.com](https://console.upstash.com)
2. Sign up (GitHub login works)
3. You're in the console

### 2. Create Database

1. Click **"Create Database"**
2. Settings:
   - **Name:** `spokestack-agents` (or whatever)
   - **Type:** Regional (cheaper) or Global (if users worldwide)
   - **Region:** Choose closest to your Vercel deployment
     - If Vercel is `iad1` (US East) → choose `us-east-1`
   - **Eviction:** No eviction (we want jobs to persist)
3. Click **Create**

### 3. Get Credentials

After creation, you'll see the database details page:

```
Endpoint: https://alive-fish-12345.upstash.io
Password: AaBbCcDdEeFf123456...

REST API:
UPSTASH_REDIS_REST_URL=https://alive-fish-12345.upstash.io
UPSTASH_REDIS_REST_TOKEN=AaBbCcDdEeFf123456...
```

**Copy these two values** - that's all you need!

### 4. Add to Environment

In your `.env.local` (local dev):
```bash
UPSTASH_REDIS_REST_URL=https://alive-fish-12345.upstash.io
UPSTASH_REDIS_REST_TOKEN=AaBbCcDdEeFf123456...
```

In Vercel:
1. Go to Project Settings → Environment Variables
2. Add both variables
3. Select which environments (Production, Preview, Development)

---

## How We Use It

### Simple Version (What We're Doing)

```typescript
import { Redis } from '@upstash/redis';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

// Add job to queue
await redis.lpush('agent-jobs', JSON.stringify({
  jobId: 'job_123',
  issueId: 'issue_456',
  agentType: 'briefs.assignment',
}));

// Worker picks up job
const job = await redis.rpop('agent-jobs');
```

### With BullMQ (More Features)

BullMQ adds:
- Retries with backoff
- Job priorities
- Progress tracking
- Scheduled jobs
- Rate limiting

```typescript
import { Queue, Worker } from 'bullmq';

const queue = new Queue('agents', {
  connection: { url: process.env.UPSTASH_REDIS_REST_URL }
});

// Add job
await queue.add('process-issue', { issueId: '123' }, {
  priority: 1,        // Higher = processed first
  attempts: 3,        // Retry 3 times
  backoff: {
    type: 'exponential',
    delay: 1000,      // 1s, 2s, 4s...
  },
});

// Worker
const worker = new Worker('agents', async (job) => {
  // Process the job
  await processIssue(job.data.issueId);
}, { connection });
```

---

## Upstash Dashboard

Once set up, you can see:

- **Data Browser:** View what's in Redis
- **CLI:** Run Redis commands
- **Metrics:** Requests, latency, memory
- **Logs:** Recent operations

Super helpful for debugging!

---

## Cost

### Free Tier
- 10,000 commands/day
- 256MB storage
- 1 database

**More than enough for staging and light production.**

### Pro ($10/month)
- 10,000 commands/day included
- $0.20 per 100K additional commands
- Unlimited databases

---

## Quick Test

After setup, test it works:

```typescript
// test-upstash.ts
import { Redis } from '@upstash/redis';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

async function test() {
  // Set a value
  await redis.set('test-key', 'Hello from Upstash!');

  // Get it back
  const value = await redis.get('test-key');
  console.log(value); // "Hello from Upstash!"

  // Clean up
  await redis.del('test-key');

  console.log('✅ Upstash is working!');
}

test();
```

---

## TL;DR

1. Go to [console.upstash.com](https://console.upstash.com)
2. Create database (pick region near your Vercel)
3. Copy `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`
4. Add to `.env.local` and Vercel
5. Done! 🎉
