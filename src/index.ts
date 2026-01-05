/**
 * Agent System for SpokeStack ERP
 *
 * Main entry point and public API
 */

// ============================================
// TYPES
// ============================================

export type {
  // Core types
  AgentIssue,
  AgentJob,
  AgentArtifact,
  AgentLog,
  AgentSession,

  // Enums
  IssueSource,
  IssueType,
  IssuePriority,
  IssueStatus,
  JobStatus,
  ArtifactType,
  LogLevel,
  ModelChoice,

  // Input/Output types
  CreateIssueInput,
  IssueContext,
  JobConfig,
  JobResult,
  ClassificationResult,

  // Agent types
  AgentDefinition,
  AgentExample,

  // Queue types
  QueueJobData,
  QueueStats,

  // API types
  SubmitIssueResponse,
  IssueStatusResponse,
  HealthCheckResponse,
} from './types/index.js';

// ============================================
// CONFIGURATION
// ============================================

export {
  getConfig,
  getFeatureFlags,
  MODEL_IDS,
  MODEL_LIMITS,
  RATE_LIMITS,
  AGENT_VERSION,
} from './config/index.js';

export type { EnvConfig, FeatureFlags } from './config/index.js';

// ============================================
// ORCHESTRATOR
// ============================================

export { AgentOrchestrator, getOrchestrator } from './core/orchestrator.js';

// ============================================
// CLASSIFIER
// ============================================

export {
  classify,
  estimateComplexity,
  selectModelByComplexity,
} from './core/classifier.js';

// ============================================
// EXECUTOR
// ============================================

export { AgentExecutor } from './core/executor.js';

// ============================================
// AGENT REGISTRY
// ============================================

export {
  getAgentDefinition,
  getAgentsForModule,
  getAllAgentIds,
  getAgentCountByModule,
  registerAgent,
  hasAgent,
} from './agents/registry.js';

// ============================================
// TOOLS
// ============================================

export {
  getToolDefinitions,
  getAvailableTools,
  executeToolCall,
} from './tools/index.js';

export type { ToolContext } from './tools/index.js';

// ============================================
// TELEMETRY
// ============================================

export {
  agentLog,
  startMetrics,
  recordToolCall,
  recordTokens,
  completeMetrics,
  captureError,
  checkHealth,
} from './lib/telemetry.js';

export type { HealthStatus } from './lib/telemetry.js';

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize the agent system with Prisma client
 */
export function initAgentSystem(prisma: unknown): void {
  // Store prisma client globally for telemetry and tools
  (globalThis as any).__prisma = prisma;
  console.log('🤖 Agent system initialized');
}
