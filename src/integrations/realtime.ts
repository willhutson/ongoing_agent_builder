/**
 * Real-time Event System
 *
 * Provides live observability into the agent feedback loop using Pusher.
 * Allows users to watch the system work through feedback → card → improvement.
 */

import type { PusherConfig, PusherEvent } from './types.js';

// ============================================
// EVENT TYPES
// ============================================

export const AGENT_EVENTS = {
  // Job lifecycle
  JOB_QUEUED: 'agent:job:queued',
  JOB_STARTED: 'agent:job:started',
  JOB_PROGRESS: 'agent:job:progress',
  JOB_TOOL_CALL: 'agent:job:tool_call',
  JOB_COMPLETED: 'agent:job:completed',
  JOB_FAILED: 'agent:job:failed',

  // Feedback loop
  FEEDBACK_RECEIVED: 'feedback:received',
  CARD_CREATED: 'feedback:card:created',
  CARD_MOVED: 'feedback:card:moved',
  ANALYSIS_STARTED: 'feedback:analysis:started',
  ANALYSIS_COMPLETE: 'feedback:analysis:complete',
  IMPROVEMENT_APPLIED: 'feedback:improvement:applied',

  // Agent thinking (live stream)
  AGENT_THINKING: 'agent:thinking',
  AGENT_ACTION: 'agent:action',

  // System health
  SYSTEM_HEALTH: 'system:health',
  QUEUE_STATS: 'system:queue:stats',
} as const;

export type AgentEventType = typeof AGENT_EVENTS[keyof typeof AGENT_EVENTS];

// ============================================
// EVENT PAYLOADS
// ============================================

export interface JobQueuedEvent {
  jobId: string;
  issueId: string;
  agentType: string;
  priority: number;
  queuePosition: number;
  estimatedWait: string;
}

export interface JobStartedEvent {
  jobId: string;
  agentType: string;
  model: string;
  startedAt: string;
}

export interface JobProgressEvent {
  jobId: string;
  step: string;
  progress: number; // 0-100
  message: string;
  details?: Record<string, unknown>;
}

export interface JobToolCallEvent {
  jobId: string;
  tool: string;
  input: Record<string, unknown>;
  status: 'started' | 'completed' | 'error';
  result?: unknown;
  duration?: number;
}

export interface AgentThinkingEvent {
  jobId: string;
  thought: string;
  timestamp: string;
}

export interface AgentActionEvent {
  jobId: string;
  action: string;
  description: string;
  timestamp: string;
}

export interface FeedbackReceivedEvent {
  feedbackId: string;
  jobId: string;
  agentType: string;
  rating: number;
  outcome: string;
  tags: string[];
}

export interface CardCreatedEvent {
  cardId: string;
  feedbackId: string;
  title: string;
  column: string;
  agentType: string;
  priority: string;
}

export interface CardMovedEvent {
  cardId: string;
  fromColumn: string;
  toColumn: string;
  movedBy: 'user' | 'system' | 'agent';
  reason?: string;
}

export interface AnalysisEvent {
  cardId: string;
  agentType: string;
  status: 'started' | 'analyzing' | 'complete';
  findings?: string[];
  suggestions?: string[];
}

export interface ImprovementAppliedEvent {
  cardId: string;
  agentType: string;
  improvementType: string;
  description: string;
  beforeVersion: string;
  afterVersion: string;
}

// ============================================
// CHANNEL HELPERS
// ============================================

/**
 * Get the channel name for an organization's agent events
 */
export function getAgentChannel(organizationId: string): string {
  return `private-agents-${organizationId}`;
}

/**
 * Get the channel name for a specific job's live stream
 */
export function getJobChannel(jobId: string): string {
  return `private-job-${jobId}`;
}

/**
 * Get the channel for the improvement board
 */
export function getImprovementBoardChannel(organizationId: string): string {
  return `private-improvements-${organizationId}`;
}

/**
 * Get the channel for system-wide events (admin only)
 */
export function getSystemChannel(): string {
  return 'private-system';
}

// ============================================
// PUSHER CLIENT (Server-side)
// ============================================

let pusherServer: PusherServerLike | null = null;

interface PusherServerLike {
  trigger(channel: string | string[], event: string, data: unknown): Promise<void>;
}

/**
 * Initialize Pusher server client
 */
export function initPusher(config: PusherConfig): void {
  // Dynamic import to avoid issues when Pusher isn't installed
  import('pusher').then((Pusher) => {
    pusherServer = new Pusher.default({
      appId: config.appId,
      key: config.key,
      secret: config.secret,
      cluster: config.cluster,
      useTLS: true,
    });
    console.log('✅ Pusher initialized for real-time events');
  }).catch(() => {
    console.warn('⚠️ Pusher not available, real-time events disabled');
  });
}

/**
 * Emit an event to a channel
 */
export async function emitEvent<T>(
  channel: string,
  event: AgentEventType,
  data: T
): Promise<void> {
  if (!pusherServer) {
    // Fallback: log to console in development
    console.log(`[Event] ${channel} → ${event}:`, data);
    return;
  }

  try {
    await pusherServer.trigger(channel, event, {
      ...data,
      _timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Failed to emit event:', error);
  }
}

// ============================================
// EVENT EMITTERS
// ============================================

/**
 * Emit job lifecycle events
 */
export const jobEvents = {
  queued: (orgId: string, data: JobQueuedEvent) =>
    emitEvent(getAgentChannel(orgId), AGENT_EVENTS.JOB_QUEUED, data),

  started: (orgId: string, data: JobStartedEvent) => {
    emitEvent(getAgentChannel(orgId), AGENT_EVENTS.JOB_STARTED, data);
    emitEvent(getJobChannel(data.jobId), AGENT_EVENTS.JOB_STARTED, data);
  },

  progress: (jobId: string, data: JobProgressEvent) =>
    emitEvent(getJobChannel(jobId), AGENT_EVENTS.JOB_PROGRESS, data),

  toolCall: (jobId: string, data: JobToolCallEvent) =>
    emitEvent(getJobChannel(jobId), AGENT_EVENTS.JOB_TOOL_CALL, data),

  thinking: (jobId: string, thought: string) =>
    emitEvent(getJobChannel(jobId), AGENT_EVENTS.AGENT_THINKING, {
      jobId,
      thought,
      timestamp: new Date().toISOString(),
    }),

  action: (jobId: string, action: string, description: string) =>
    emitEvent(getJobChannel(jobId), AGENT_EVENTS.AGENT_ACTION, {
      jobId,
      action,
      description,
      timestamp: new Date().toISOString(),
    }),

  completed: (orgId: string, jobId: string, result: unknown) => {
    const data = { jobId, result, completedAt: new Date().toISOString() };
    emitEvent(getAgentChannel(orgId), AGENT_EVENTS.JOB_COMPLETED, data);
    emitEvent(getJobChannel(jobId), AGENT_EVENTS.JOB_COMPLETED, data);
  },

  failed: (orgId: string, jobId: string, error: string) => {
    const data = { jobId, error, failedAt: new Date().toISOString() };
    emitEvent(getAgentChannel(orgId), AGENT_EVENTS.JOB_FAILED, data);
    emitEvent(getJobChannel(jobId), AGENT_EVENTS.JOB_FAILED, data);
  },
};

/**
 * Emit feedback loop events
 */
export const feedbackEvents = {
  received: (orgId: string, data: FeedbackReceivedEvent) =>
    emitEvent(getImprovementBoardChannel(orgId), AGENT_EVENTS.FEEDBACK_RECEIVED, data),

  cardCreated: (orgId: string, data: CardCreatedEvent) =>
    emitEvent(getImprovementBoardChannel(orgId), AGENT_EVENTS.CARD_CREATED, data),

  cardMoved: (orgId: string, data: CardMovedEvent) =>
    emitEvent(getImprovementBoardChannel(orgId), AGENT_EVENTS.CARD_MOVED, data),

  analysisStarted: (orgId: string, cardId: string, agentType: string) =>
    emitEvent(getImprovementBoardChannel(orgId), AGENT_EVENTS.ANALYSIS_STARTED, {
      cardId,
      agentType,
      status: 'started',
    }),

  analysisComplete: (orgId: string, data: AnalysisEvent) =>
    emitEvent(getImprovementBoardChannel(orgId), AGENT_EVENTS.ANALYSIS_COMPLETE, data),

  improvementApplied: (orgId: string, data: ImprovementAppliedEvent) =>
    emitEvent(getImprovementBoardChannel(orgId), AGENT_EVENTS.IMPROVEMENT_APPLIED, data),
};

/**
 * Emit system health events
 */
export const systemEvents = {
  health: (status: 'healthy' | 'degraded' | 'unhealthy', details: Record<string, unknown>) =>
    emitEvent(getSystemChannel(), AGENT_EVENTS.SYSTEM_HEALTH, { status, details }),

  queueStats: (stats: { waiting: number; active: number; completed: number; failed: number }) =>
    emitEvent(getSystemChannel(), AGENT_EVENTS.QUEUE_STATS, stats),
};

// ============================================
// LIVE STREAM HELPER
// ============================================

/**
 * Create a live stream context for a job
 * Returns functions to emit events during agent execution
 */
export function createJobStream(jobId: string, orgId: string) {
  return {
    thinking: (thought: string) => jobEvents.thinking(jobId, thought),
    action: (action: string, description: string) => jobEvents.action(jobId, action, description),
    progress: (step: string, progress: number, message: string) =>
      jobEvents.progress(jobId, { jobId, step, progress, message }),
    toolStart: (tool: string, input: Record<string, unknown>) =>
      jobEvents.toolCall(jobId, { jobId, tool, input, status: 'started' }),
    toolComplete: (tool: string, input: Record<string, unknown>, result: unknown, duration: number) =>
      jobEvents.toolCall(jobId, { jobId, tool, input, status: 'completed', result, duration }),
    toolError: (tool: string, input: Record<string, unknown>, error: string) =>
      jobEvents.toolCall(jobId, { jobId, tool, input, status: 'error', result: error }),
    complete: (result: unknown) => jobEvents.completed(orgId, jobId, result),
    fail: (error: string) => jobEvents.failed(orgId, jobId, error),
  };
}

// ============================================
// TYPES FOR CLIENT-SIDE
// ============================================

/**
 * Client-side subscription helper types
 * (Used in React components)
 */
export interface AgentStreamCallbacks {
  onThinking?: (thought: string) => void;
  onAction?: (action: string, description: string) => void;
  onProgress?: (step: string, progress: number, message: string) => void;
  onToolCall?: (tool: string, status: 'started' | 'completed' | 'error', data: unknown) => void;
  onComplete?: (result: unknown) => void;
  onError?: (error: string) => void;
}

export interface FeedbackStreamCallbacks {
  onFeedbackReceived?: (data: FeedbackReceivedEvent) => void;
  onCardCreated?: (data: CardCreatedEvent) => void;
  onCardMoved?: (data: CardMovedEvent) => void;
  onAnalysisUpdate?: (data: AnalysisEvent) => void;
  onImprovementApplied?: (data: ImprovementAppliedEvent) => void;
}
