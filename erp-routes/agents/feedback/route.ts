/**
 * Agent API - Submit Feedback
 *
 * POST /api/agents/feedback - Submit feedback on agent performance
 *
 * Copy this file to: spokestack/src/app/api/agents/feedback/route.ts
 */

import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import prisma from '@/lib/prisma';

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const { jobId, rating, outcome, comment, tags } = body;

    // Validate required fields
    if (!jobId || !rating || !outcome) {
      return NextResponse.json(
        { error: 'Missing required fields: jobId, rating, outcome' },
        { status: 400 }
      );
    }

    // Validate rating
    if (rating < 1 || rating > 5) {
      return NextResponse.json(
        { error: 'Rating must be between 1 and 5' },
        { status: 400 }
      );
    }

    // Get the job to verify ownership and get details
    const job = await prisma.agentJob.findFirst({
      where: {
        id: jobId,
        organizationId: session.user.organizationId,
      },
    });

    if (!job) {
      return NextResponse.json({ error: 'Job not found' }, { status: 404 });
    }

    // Create feedback record
    const feedback = await prisma.agentFeedback.create({
      data: {
        jobId,
        issueId: job.issueId,
        agentType: job.agentType,
        rating,
        outcome,
        comment: comment || null,
        tags: tags || [],
        userId: session.user.id,
        organizationId: session.user.organizationId,
        improvementStatus: 'PENDING',
      },
    });

    // Log the feedback
    await prisma.agentLog.create({
      data: {
        jobId,
        level: 'INFO',
        message: `Feedback received: ${rating}/5 - ${outcome}`,
        data: { feedbackId: feedback.id, tags },
      },
    });

    return NextResponse.json({
      id: feedback.id,
      message: 'Feedback submitted successfully',
    });
  } catch (error) {
    console.error('Feedback API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * GET /api/agents/feedback - Get feedback for an organization
 */
export async function GET(request: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const agentType = searchParams.get('agentType');
    const limit = parseInt(searchParams.get('limit') || '50');

    const feedback = await prisma.agentFeedback.findMany({
      where: {
        organizationId: session.user.organizationId,
        ...(agentType ? { agentType } : {}),
      },
      orderBy: { createdAt: 'desc' },
      take: Math.min(limit, 100),
    });

    // Calculate aggregate stats
    const stats = {
      total: feedback.length,
      averageRating:
        feedback.length > 0
          ? feedback.reduce((sum, f) => sum + f.rating, 0) / feedback.length
          : 0,
      outcomes: {
        solved: feedback.filter((f) => f.outcome === 'SOLVED').length,
        partial: feedback.filter((f) => f.outcome === 'PARTIAL').length,
        notSolved: feedback.filter((f) => f.outcome === 'NOT_SOLVED').length,
        madeWorse: feedback.filter((f) => f.outcome === 'MADE_WORSE').length,
      },
    };

    return NextResponse.json({
      feedback,
      stats,
    });
  } catch (error) {
    console.error('Feedback API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
