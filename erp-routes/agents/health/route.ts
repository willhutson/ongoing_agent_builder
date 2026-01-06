/**
 * Agent API - Health Check
 *
 * GET /api/agents/health - Check agent system health
 *
 * Copy this file to: spokestack/src/app/api/agents/health/route.ts
 */

import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import { Redis } from '@upstash/redis';

const AGENT_VERSION = {
  version: '0.1.0',
  commit: process.env.VERCEL_GIT_COMMIT_SHA?.slice(0, 7) || 'local',
  deployedAt: process.env.VERCEL_GIT_COMMIT_DATE || new Date().toISOString(),
};

export async function GET() {
  const checks = {
    database: false,
    queue: false,
    anthropic: false,
  };

  const errors: string[] = [];

  // Check database
  try {
    await prisma.$queryRaw`SELECT 1`;
    checks.database = true;
  } catch (error) {
    errors.push(`Database: ${error}`);
  }

  // Check queue (Upstash)
  try {
    if (process.env.UPSTASH_REDIS_REST_URL) {
      const redis = new Redis({
        url: process.env.UPSTASH_REDIS_REST_URL,
        token: process.env.UPSTASH_REDIS_REST_TOKEN!,
      });
      await redis.ping();
      checks.queue = true;
    } else {
      errors.push('Queue: UPSTASH_REDIS_REST_URL not configured');
    }
  } catch (error) {
    errors.push(`Queue: ${error}`);
  }

  // Check Anthropic API key exists
  if (process.env.ANTHROPIC_API_KEY) {
    checks.anthropic = true;
  } else {
    errors.push('Anthropic: API key not configured');
  }

  // Get queue stats
  let queueStats = { waiting: 0, processing: 0 };
  try {
    if (checks.queue) {
      const redis = new Redis({
        url: process.env.UPSTASH_REDIS_REST_URL!,
        token: process.env.UPSTASH_REDIS_REST_TOKEN!,
      });
      queueStats.waiting = await redis.llen('agent-jobs');
    }
  } catch {
    // Ignore queue stats errors
  }

  // Get recent job stats
  let jobStats = { pending: 0, running: 0, completedToday: 0, failedToday: 0 };
  try {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const [pending, running, completedToday, failedToday] = await Promise.all([
      prisma.agentJob.count({ where: { status: 'PENDING' } }),
      prisma.agentJob.count({ where: { status: 'RUNNING' } }),
      prisma.agentJob.count({
        where: { status: 'COMPLETED', completedAt: { gte: today } },
      }),
      prisma.agentJob.count({
        where: { status: 'FAILED', completedAt: { gte: today } },
      }),
    ]);

    jobStats = { pending, running, completedToday, failedToday };
  } catch {
    // Ignore job stats errors
  }

  // Determine overall status
  const allChecks = Object.values(checks);
  const passedChecks = allChecks.filter(Boolean).length;

  let status: 'healthy' | 'degraded' | 'unhealthy';
  if (passedChecks === allChecks.length) {
    status = 'healthy';
  } else if (passedChecks > 0) {
    status = 'degraded';
  } else {
    status = 'unhealthy';
  }

  return NextResponse.json(
    {
      status,
      version: AGENT_VERSION,
      enabled: process.env.AGENT_ENABLED === 'true',
      checks,
      queue: queueStats,
      jobs: jobStats,
      errors: errors.length > 0 ? errors : undefined,
      timestamp: new Date().toISOString(),
    },
    {
      status: status === 'healthy' ? 200 : status === 'degraded' ? 200 : 503,
    }
  );
}
