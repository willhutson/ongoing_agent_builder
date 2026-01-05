/**
 * Telemetry and Logging
 *
 * Provides structured logging for agent execution with:
 * - Console output for debugging
 * - Database persistence for audit trail
 * - Optional external telemetry integration
 */

import type { LogLevel } from '../types/index.js';
import { getConfig } from '../config/index.js';

// ============================================
// LOG PREFIXES
// ============================================

const LOG_PREFIXES: Record<LogLevel, string> = {
  DEBUG: '🔍',
  INFO: 'ℹ️',
  WARN: '⚠️',
  ERROR: '❌',
};

// ============================================
// LOGGING FUNCTIONS
// ============================================

/**
 * Log an agent event
 *
 * @param jobId - The job ID for context
 * @param level - Log level
 * @param message - Log message
 * @param data - Optional structured data
 */
export async function agentLog(
  jobId: string,
  level: LogLevel,
  message: string,
  data?: Record<string, unknown>
): Promise<void> {
  const config = getConfig();
  const timestamp = new Date().toISOString();
  const prefix = LOG_PREFIXES[level];

  // Always log to console
  const consoleMessage = `${prefix} [${timestamp}] [Job:${jobId.slice(0, 8)}] ${message}`;

  if (level === 'DEBUG' && !config.AGENT_DEBUG) {
    // Skip debug logs unless debug mode is enabled
    return;
  }

  switch (level) {
    case 'DEBUG':
      console.debug(consoleMessage, data || '');
      break;
    case 'INFO':
      console.info(consoleMessage, data || '');
      break;
    case 'WARN':
      console.warn(consoleMessage, data || '');
      break;
    case 'ERROR':
      console.error(consoleMessage, data || '');
      break;
  }

  // Persist to database if telemetry enabled
  if (config.AGENT_TELEMETRY_ENABLED) {
    await persistLog(jobId, level, message, data);
  }
}

/**
 * Persist log to database
 */
async function persistLog(
  jobId: string,
  level: LogLevel,
  message: string,
  data?: Record<string, unknown>
): Promise<void> {
  try {
    // This will be connected to Prisma when deployed in ERP
    // For now, we'll use a no-op or external service

    // If running in ERP context, use the global prisma client
    const prisma = (globalThis as any).__prisma;
    if (prisma?.agentLog) {
      await prisma.agentLog.create({
        data: {
          jobId,
          level,
          message,
          data: data ? JSON.stringify(data) : null,
        },
      });
    }
  } catch (error) {
    // Don't fail the main operation if logging fails
    console.error('Failed to persist log:', error);
  }
}

// ============================================
// METRICS
// ============================================

interface AgentMetrics {
  jobId: string;
  agentType: string;
  model: string;
  startTime: number;
  endTime?: number;
  tokenUsage?: {
    input: number;
    output: number;
  };
  toolCalls: number;
  success: boolean;
  error?: string;
}

const metricsStore = new Map<string, AgentMetrics>();

/**
 * Start tracking metrics for a job
 */
export function startMetrics(
  jobId: string,
  agentType: string,
  model: string
): void {
  metricsStore.set(jobId, {
    jobId,
    agentType,
    model,
    startTime: Date.now(),
    toolCalls: 0,
    success: false,
  });
}

/**
 * Record a tool call
 */
export function recordToolCall(jobId: string): void {
  const metrics = metricsStore.get(jobId);
  if (metrics) {
    metrics.toolCalls++;
  }
}

/**
 * Record token usage
 */
export function recordTokens(
  jobId: string,
  input: number,
  output: number
): void {
  const metrics = metricsStore.get(jobId);
  if (metrics) {
    metrics.tokenUsage = { input, output };
  }
}

/**
 * Complete metrics tracking
 */
export function completeMetrics(
  jobId: string,
  success: boolean,
  error?: string
): AgentMetrics | undefined {
  const metrics = metricsStore.get(jobId);
  if (metrics) {
    metrics.endTime = Date.now();
    metrics.success = success;
    metrics.error = error;

    // Log final metrics
    const duration = metrics.endTime - metrics.startTime;
    agentLog(jobId, 'INFO', 'Job metrics', {
      duration: `${duration}ms`,
      toolCalls: metrics.toolCalls,
      tokens: metrics.tokenUsage,
      success: metrics.success,
    });

    // Clean up
    metricsStore.delete(jobId);

    return metrics;
  }
  return undefined;
}

// ============================================
// ERROR TRACKING
// ============================================

/**
 * Capture an error with context
 */
export async function captureError(
  error: Error,
  context: {
    jobId?: string;
    agentType?: string;
    operation?: string;
    extra?: Record<string, unknown>;
  }
): Promise<void> {
  const errorData = {
    name: error.name,
    message: error.message,
    stack: error.stack,
    ...context,
  };

  console.error('❌ Agent error captured:', errorData);

  // TODO: Send to error tracking service (Sentry, etc.)
  // if (process.env.SENTRY_DSN) {
  //   Sentry.captureException(error, { extra: context });
  // }

  if (context.jobId) {
    await agentLog(context.jobId, 'ERROR', error.message, errorData);
  }
}

// ============================================
// HEALTH CHECK HELPERS
// ============================================

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  checks: {
    database: boolean;
    queue: boolean;
    claude: boolean;
  };
  timestamp: string;
}

/**
 * Check system health
 */
export async function checkHealth(): Promise<HealthStatus> {
  const checks = {
    database: false,
    queue: false,
    claude: false,
  };

  // Check database
  try {
    const prisma = (globalThis as any).__prisma;
    if (prisma) {
      await prisma.$queryRaw`SELECT 1`;
      checks.database = true;
    }
  } catch {
    // Database check failed
  }

  // Check queue (Redis)
  try {
    // TODO: Implement queue health check
    checks.queue = true; // Optimistic for now
  } catch {
    // Queue check failed
  }

  // Check Claude API
  try {
    const config = getConfig();
    if (config.ANTHROPIC_API_KEY) {
      // Just verify the key exists
      checks.claude = true;
    }
  } catch {
    // Claude check failed
  }

  // Determine overall status
  const failedChecks = Object.values(checks).filter((v) => !v).length;
  let status: 'healthy' | 'degraded' | 'unhealthy';

  if (failedChecks === 0) {
    status = 'healthy';
  } else if (failedChecks < Object.keys(checks).length) {
    status = 'degraded';
  } else {
    status = 'unhealthy';
  }

  return {
    status,
    checks,
    timestamp: new Date().toISOString(),
  };
}
