/**
 * Agent API - Submit and List Issues
 *
 * POST /api/agents - Submit a new issue for agent processing
 * GET /api/agents - List recent issues
 *
 * Copy this file to: spokestack/src/app/api/agents/route.ts
 */

import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import prisma from '@/lib/prisma';
import { Redis } from '@upstash/redis';
import Anthropic from '@anthropic-ai/sdk';

// ============================================
// CONFIGURATION
// ============================================

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

const QUEUE_NAME = 'agent-jobs';

// ============================================
// POST - Submit Issue
// ============================================

export async function POST(request: NextRequest) {
  try {
    // Auth check
    const session = await auth();
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Check if agents are enabled
    if (process.env.AGENT_ENABLED !== 'true') {
      return NextResponse.json(
        { error: 'Agent system is disabled' },
        { status: 503 }
      );
    }

    // Parse body
    const body = await request.json();
    const { type, title, description, priority, context, externalId } = body;

    // Validate required fields
    if (!type || !title || !description) {
      return NextResponse.json(
        { error: 'Missing required fields: type, title, description' },
        { status: 400 }
      );
    }

    // Create issue record
    const issue = await prisma.agentIssue.create({
      data: {
        type,
        title,
        description,
        priority: priority || 'MEDIUM',
        context: context || {},
        externalId,
        source: 'MANUAL',
        status: 'PENDING',
        organizationId: session.user.organizationId,
        createdById: session.user.id,
      },
    });

    // Quick classification to determine agent type
    const classification = await classifyIssue(issue);

    // Create job record
    const job = await prisma.agentJob.create({
      data: {
        issueId: issue.id,
        agentType: classification.agentType,
        model: classification.model,
        status: 'PENDING',
        priority: getPriorityScore(priority),
        config: {
          maxTokens: 8192,
          timeout: 300000,
        },
        organizationId: session.user.organizationId,
      },
    });

    // Update issue status
    await prisma.agentIssue.update({
      where: { id: issue.id },
      data: { status: 'QUEUED' },
    });

    // Add to queue
    await redis.lpush(
      QUEUE_NAME,
      JSON.stringify({
        jobId: job.id,
        issueId: issue.id,
        agentType: classification.agentType,
        model: classification.model,
        organizationId: session.user.organizationId,
        createdAt: new Date().toISOString(),
      })
    );

    // Log
    await prisma.agentLog.create({
      data: {
        jobId: job.id,
        level: 'INFO',
        message: `Issue queued for processing by ${classification.agentType}`,
        data: { classification },
      },
    });

    return NextResponse.json({
      id: issue.id,
      status: 'QUEUED',
      jobId: job.id,
      agentType: classification.agentType,
      trackingUrl: `/api/agents/${issue.id}`,
    });
  } catch (error) {
    console.error('Agent API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// ============================================
// GET - List Issues
// ============================================

export async function GET(request: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    const limit = parseInt(searchParams.get('limit') || '20');

    const issues = await prisma.agentIssue.findMany({
      where: {
        organizationId: session.user.organizationId,
        ...(status ? { status: status as any } : {}),
      },
      include: {
        jobs: {
          take: 1,
          orderBy: { createdAt: 'desc' },
          select: {
            id: true,
            agentType: true,
            status: true,
            startedAt: true,
            completedAt: true,
          },
        },
        createdBy: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
      take: Math.min(limit, 100),
    });

    return NextResponse.json({
      issues,
      count: issues.length,
    });
  } catch (error) {
    console.error('Agent API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// ============================================
// HELPERS
// ============================================

interface Classification {
  agentType: string;
  model: string;
  confidence: number;
}

async function classifyIssue(issue: any): Promise<Classification> {
  // If module specified in context, use module-specific agent
  const module = issue.context?.module;
  if (module) {
    const agentType = getAgentForModule(module, issue.type);
    return {
      agentType,
      model: issue.priority === 'CRITICAL' ? 'opus' : 'sonnet',
      confidence: 0.9,
    };
  }

  // Otherwise, use AI to classify
  try {
    const anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY!,
    });

    const response = await anthropic.messages.create({
      model: 'claude-3-5-haiku-20241022',
      max_tokens: 256,
      messages: [
        {
          role: 'user',
          content: `Classify this issue for the SpokeStack ERP system.

Issue Type: ${issue.type}
Title: ${issue.title}
Description: ${issue.description}

Available modules: briefs, time, resources, leave, rfp, retainers, studio, crm, lms, boards, workflow, chat, analytics, surveys, integrations, admin

Respond with JSON only:
{"module": "module_name", "agentType": "module.specific-agent", "model": "haiku|sonnet|opus"}`,
        },
      ],
    });

    const text =
      response.content[0].type === 'text' ? response.content[0].text : '';
    const match = text.match(/\{[\s\S]*\}/);
    if (match) {
      const result = JSON.parse(match[0]);
      return {
        agentType: result.agentType || 'meta.research',
        model: result.model || 'sonnet',
        confidence: 0.8,
      };
    }
  } catch (error) {
    console.warn('Classification failed, using fallback:', error);
  }

  // Fallback
  return {
    agentType: 'meta.research',
    model: 'sonnet',
    confidence: 0.5,
  };
}

function getAgentForModule(module: string, issueType: string): string {
  const moduleAgents: Record<string, Record<string, string>> = {
    briefs: {
      BUG: 'briefs.status-workflow',
      FEATURE: 'briefs.assignment',
      default: 'briefs.status-workflow',
    },
    time: {
      BUG: 'time.timer',
      FEATURE: 'time.timesheet',
      default: 'time.timer',
    },
    crm: {
      BUG: 'crm.pipeline',
      FEATURE: 'crm.contacts',
      default: 'crm.pipeline',
    },
    studio: {
      BUG: 'studio.calendar',
      FEATURE: 'studio.ai-calendar',
      default: 'studio.calendar',
    },
    lms: {
      BUG: 'lms.courses',
      FEATURE: 'lms.assessment',
      default: 'lms.courses',
    },
  };

  const agents = moduleAgents[module];
  if (agents) {
    return agents[issueType] || agents.default;
  }

  return 'meta.research';
}

function getPriorityScore(priority: string): number {
  const scores: Record<string, number> = {
    CRITICAL: 1,
    HIGH: 2,
    MEDIUM: 5,
    LOW: 10,
  };
  return scores[priority] || 5;
}
