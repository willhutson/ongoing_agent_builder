/**
 * Agent Orchestrator
 *
 * Central coordination point for agent execution. Handles:
 * - Issue classification and routing
 * - Agent selection and spawning
 * - Job lifecycle management
 * - Result aggregation
 */

import type {
  AgentIssue,
  AgentJob,
  ClassificationResult,
  CreateIssueInput,
  JobConfig,
  ModelChoice,
  SubmitIssueResponse,
} from '../types/index.js';
import { getConfig, getFeatureFlags, MODEL_LIMITS } from '../config/index.js';
import { classify } from './classifier.js';
import { AgentExecutor } from './executor.js';
import { agentLog } from '../lib/telemetry.js';

// ============================================
// ORCHESTRATOR
// ============================================

export class AgentOrchestrator {
  private executor: AgentExecutor;
  private runningJobs: Map<string, AbortController> = new Map();

  constructor(
    private prisma: PrismaLike,
    private queueClient?: QueueLike
  ) {
    this.executor = new AgentExecutor(prisma);
  }

  /**
   * Submit a new issue for processing
   */
  async submitIssue(
    input: CreateIssueInput,
    organizationId: string,
    userId?: string
  ): Promise<SubmitIssueResponse> {
    const flags = getFeatureFlags();

    if (!flags.enabled) {
      throw new Error('Agent system is currently disabled');
    }

    // Create the issue record
    const issue = await this.prisma.agentIssue.create({
      data: {
        source: input.source || 'MANUAL',
        type: input.type,
        priority: input.priority || 'MEDIUM',
        title: input.title,
        description: input.description,
        context: input.context || {},
        externalId: input.externalId,
        status: 'PENDING',
        organizationId,
        createdById: userId,
      },
    });

    // Classify the issue to determine routing
    const classification = await this.classifyIssue(issue);

    // Create the job
    const job = await this.createJob(issue, classification);

    // Queue the job for processing
    if (this.queueClient) {
      await this.queueClient.add('agent-job', {
        issueId: issue.id,
        jobId: job.id,
        agentType: job.agentType,
        model: job.model,
        config: job.config,
        organizationId,
      }, {
        priority: this.getPriorityScore(issue.priority),
        attempts: job.maxAttempts,
      });

      await this.updateIssueStatus(issue.id, 'QUEUED');
    } else {
      // Direct execution (no queue)
      this.executeJobAsync(job);
    }

    return {
      id: issue.id,
      status: 'QUEUED',
      jobId: job.id,
      trackingUrl: `/api/agents/${issue.id}`,
    };
  }

  /**
   * Classify an issue to determine routing
   */
  private async classifyIssue(issue: AgentIssue): Promise<ClassificationResult> {
    try {
      return await classify(issue);
    } catch (error) {
      // Fallback classification if AI fails
      console.warn('Classification failed, using fallback:', error);
      return {
        issueType: issue.type,
        priority: issue.priority,
        complexity: 5,
        module: issue.context.module || 'general',
        suggestedAgent: 'meta.research',
        suggestedModel: 'sonnet',
        confidence: 0.5,
        reasoning: 'Fallback classification due to error',
      };
    }
  }

  /**
   * Create a job for the classified issue
   */
  private async createJob(
    issue: AgentIssue,
    classification: ClassificationResult
  ): Promise<AgentJob> {
    const config = getConfig();
    const modelLimits = MODEL_LIMITS[classification.suggestedModel];

    const jobConfig: JobConfig = {
      timeout: modelLimits.timeout,
      maxTokens: modelLimits.maxTokens,
      tools: this.getToolsForAgent(classification.suggestedAgent),
    };

    return this.prisma.agentJob.create({
      data: {
        issueId: issue.id,
        agentType: classification.suggestedAgent,
        model: classification.suggestedModel,
        status: 'PENDING',
        priority: this.getPriorityScore(issue.priority),
        attempts: 0,
        maxAttempts: 3,
        config: jobConfig,
        organizationId: issue.organizationId,
      },
    });
  }

  /**
   * Execute a job (async, non-blocking)
   */
  private async executeJobAsync(job: AgentJob): Promise<void> {
    const abortController = new AbortController();
    this.runningJobs.set(job.id, abortController);

    try {
      await this.updateJobStatus(job.id, 'RUNNING');
      await this.updateIssueStatus(job.issueId, 'PROCESSING');

      const result = await this.executor.execute(job, abortController.signal);

      await this.prisma.agentJob.update({
        where: { id: job.id },
        data: {
          status: 'COMPLETED',
          result,
          completedAt: new Date(),
        },
      });

      await this.updateIssueStatus(job.issueId, 'COMPLETED');
      await agentLog(job.id, 'INFO', 'Job completed successfully', { result });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);

      await this.prisma.agentJob.update({
        where: { id: job.id },
        data: {
          status: 'FAILED',
          error: errorMessage,
          attempts: { increment: 1 },
        },
      });

      await this.updateIssueStatus(job.issueId, 'FAILED');
      await agentLog(job.id, 'ERROR', 'Job failed', { error: errorMessage });

    } finally {
      this.runningJobs.delete(job.id);
    }
  }

  /**
   * Cancel a running job
   */
  async cancelJob(jobId: string): Promise<void> {
    const controller = this.runningJobs.get(jobId);
    if (controller) {
      controller.abort();
      this.runningJobs.delete(jobId);
    }

    await this.updateJobStatus(jobId, 'CANCELLED');
  }

  /**
   * Get status of an issue and its job
   */
  async getIssueStatus(issueId: string, organizationId: string) {
    const issue = await this.prisma.agentIssue.findFirst({
      where: { id: issueId, organizationId },
      include: {
        jobs: {
          include: {
            logs: {
              orderBy: { timestamp: 'desc' },
              take: 20,
            },
            artifacts: true,
          },
          orderBy: { createdAt: 'desc' },
          take: 1,
        },
      },
    });

    if (!issue) {
      return null;
    }

    const job = issue.jobs[0];

    return {
      id: issue.id,
      status: issue.status,
      job: job ? {
        id: job.id,
        agentType: job.agentType,
        status: job.status,
        logs: job.logs.map((l) => ({
          level: l.level,
          message: l.message,
          timestamp: l.timestamp,
        })),
      } : undefined,
      result: job?.result,
    };
  }

  /**
   * Get tools available for an agent type
   */
  private getToolsForAgent(agentType: string): string[] {
    const baseTools = ['read', 'search', 'analyze'];

    // Code agents get file editing tools
    if (agentType.includes('code') || agentType.includes('fix')) {
      return [...baseTools, 'edit', 'write', 'git'];
    }

    // Research agents get extended search
    if (agentType.includes('research')) {
      return [...baseTools, 'web_search', 'grep'];
    }

    // Deployment agent gets full access
    if (agentType === 'meta.deployment') {
      return [...baseTools, 'edit', 'write', 'git', 'database', 'config'];
    }

    return baseTools;
  }

  /**
   * Convert priority to numeric score (lower = higher priority)
   */
  private getPriorityScore(priority: string): number {
    const scores: Record<string, number> = {
      CRITICAL: 1,
      HIGH: 2,
      MEDIUM: 5,
      LOW: 10,
    };
    return scores[priority] || 5;
  }

  private async updateIssueStatus(issueId: string, status: string): Promise<void> {
    await this.prisma.agentIssue.update({
      where: { id: issueId },
      data: { status },
    });
  }

  private async updateJobStatus(jobId: string, status: string): Promise<void> {
    await this.prisma.agentJob.update({
      where: { id: jobId },
      data: {
        status,
        ...(status === 'RUNNING' ? { startedAt: new Date() } : {}),
      },
    });
  }
}

// ============================================
// TYPE STUBS (replaced by real Prisma in ERP)
// ============================================

interface PrismaLike {
  agentIssue: {
    create: (args: any) => Promise<AgentIssue>;
    update: (args: any) => Promise<AgentIssue>;
    findFirst: (args: any) => Promise<any>;
  };
  agentJob: {
    create: (args: any) => Promise<AgentJob>;
    update: (args: any) => Promise<AgentJob>;
  };
}

interface QueueLike {
  add: (name: string, data: any, options: any) => Promise<void>;
}

// ============================================
// SINGLETON
// ============================================

let orchestrator: AgentOrchestrator | null = null;

export function getOrchestrator(prisma: PrismaLike, queue?: QueueLike): AgentOrchestrator {
  if (!orchestrator) {
    orchestrator = new AgentOrchestrator(prisma, queue);
  }
  return orchestrator;
}
