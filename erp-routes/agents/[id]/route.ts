/**
 * Agent API - Get Issue Status
 *
 * GET /api/agents/[id] - Get status of a specific issue
 *
 * Copy this file to: spokestack/src/app/api/agents/[id]/route.ts
 */

import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import prisma from '@/lib/prisma';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth();
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const issue = await prisma.agentIssue.findFirst({
      where: {
        id: params.id,
        organizationId: session.user.organizationId,
      },
      include: {
        jobs: {
          orderBy: { createdAt: 'desc' },
          take: 1,
          include: {
            logs: {
              orderBy: { timestamp: 'desc' },
              take: 20,
              select: {
                level: true,
                message: true,
                timestamp: true,
              },
            },
            artifacts: {
              select: {
                id: true,
                type: true,
                name: true,
                filePath: true,
                createdAt: true,
              },
            },
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
    });

    if (!issue) {
      return NextResponse.json({ error: 'Issue not found' }, { status: 404 });
    }

    const job = issue.jobs[0];

    return NextResponse.json({
      id: issue.id,
      title: issue.title,
      description: issue.description,
      type: issue.type,
      priority: issue.priority,
      status: issue.status,
      createdAt: issue.createdAt,
      createdBy: issue.createdBy,

      job: job
        ? {
            id: job.id,
            agentType: job.agentType,
            model: job.model,
            status: job.status,
            attempts: job.attempts,
            startedAt: job.startedAt,
            completedAt: job.completedAt,
            duration: job.completedAt && job.startedAt
              ? new Date(job.completedAt).getTime() - new Date(job.startedAt).getTime()
              : null,
            result: job.result,
            error: job.error,
            logs: job.logs,
            artifacts: job.artifacts,
          }
        : null,
    });
  } catch (error) {
    console.error('Agent status error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/agents/[id] - Cancel an issue
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth();
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const issue = await prisma.agentIssue.findFirst({
      where: {
        id: params.id,
        organizationId: session.user.organizationId,
      },
    });

    if (!issue) {
      return NextResponse.json({ error: 'Issue not found' }, { status: 404 });
    }

    // Can only cancel pending/queued issues
    if (!['PENDING', 'QUEUED'].includes(issue.status)) {
      return NextResponse.json(
        { error: 'Cannot cancel issue in current state' },
        { status: 400 }
      );
    }

    // Update status
    await prisma.agentIssue.update({
      where: { id: params.id },
      data: { status: 'CANCELLED' },
    });

    // Cancel any pending jobs
    await prisma.agentJob.updateMany({
      where: {
        issueId: params.id,
        status: { in: ['PENDING', 'RUNNING'] },
      },
      data: { status: 'CANCELLED' },
    });

    return NextResponse.json({ success: true, status: 'CANCELLED' });
  } catch (error) {
    console.error('Agent cancel error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
