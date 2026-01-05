/**
 * Core type definitions for the Agent System
 */

// ============================================
// ENUMS
// ============================================

export type IssueSource = 'MANUAL' | 'ERP_TRIGGER' | 'GITHUB' | 'WEBHOOK' | 'SCHEDULED';

export type IssueType = 'BUG' | 'FEATURE' | 'ENHANCEMENT' | 'QUESTION' | 'TASK' | 'DEPLOYMENT';

export type IssuePriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type IssueStatus = 'PENDING' | 'QUEUED' | 'PROCESSING' | 'REVIEW' | 'COMPLETED' | 'FAILED' | 'CANCELLED';

export type JobStatus = 'PENDING' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'FAILED' | 'CANCELLED';

export type ArtifactType = 'CODE_CHANGE' | 'ANALYSIS' | 'RECOMMENDATION' | 'DOCUMENTATION' | 'PULL_REQUEST' | 'CONFIG';

export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

export type ModelChoice = 'haiku' | 'sonnet' | 'opus';

// ============================================
// CORE INTERFACES
// ============================================

/**
 * An issue/request submitted to the agent system
 */
export interface AgentIssue {
  id: string;
  externalId?: string;
  source: IssueSource;
  type: IssueType;
  priority: IssuePriority;
  title: string;
  description: string;
  context: IssueContext;
  status: IssueStatus;
  organizationId: string;
  createdById?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface IssueContext {
  module?: string;
  affectedFiles?: string[];
  relatedIssues?: string[];
  errorLogs?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Input for creating a new issue
 */
export interface CreateIssueInput {
  source?: IssueSource;
  type: IssueType;
  priority?: IssuePriority;
  title: string;
  description: string;
  context?: Partial<IssueContext>;
  externalId?: string;
}

/**
 * An agent job in the processing queue
 */
export interface AgentJob {
  id: string;
  issueId: string;
  agentType: string;
  model: ModelChoice;
  status: JobStatus;
  priority: number;
  attempts: number;
  maxAttempts: number;
  config: JobConfig;
  result?: JobResult;
  error?: string;
  organizationId: string;
  startedAt?: Date;
  completedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface JobConfig {
  timeout?: number;
  maxTokens?: number;
  tools?: string[];
  systemPrompt?: string;
}

export interface JobResult {
  summary: string;
  artifacts: AgentArtifact[];
  pullRequestUrl?: string;
  recommendations?: string[];
  nextSteps?: string[];
}

/**
 * An artifact produced by an agent
 */
export interface AgentArtifact {
  id: string;
  jobId: string;
  type: ArtifactType;
  name: string;
  content: string;
  filePath?: string;
  diffPatch?: string;
  metadata?: Record<string, unknown>;
  createdAt: Date;
}

/**
 * A log entry from agent execution
 */
export interface AgentLog {
  id: string;
  jobId: string;
  level: LogLevel;
  message: string;
  data?: Record<string, unknown>;
  timestamp: Date;
}

// ============================================
// AGENT DEFINITIONS
// ============================================

/**
 * Definition of an agent type
 */
export interface AgentDefinition {
  id: string;
  name: string;
  description: string;
  module: string;
  defaultModel: ModelChoice;
  capabilities: string[];
  tools: string[];
  systemPrompt: string;
  examples?: AgentExample[];
}

export interface AgentExample {
  input: string;
  expectedBehavior: string;
}

/**
 * Classification result from the triage agent
 */
export interface ClassificationResult {
  issueType: IssueType;
  priority: IssuePriority;
  complexity: number; // 1-10
  module: string;
  suggestedAgent: string;
  suggestedModel: ModelChoice;
  confidence: number; // 0-1
  reasoning: string;
}

// ============================================
// QUEUE INTERFACES
// ============================================

export interface QueueJobData {
  issueId: string;
  jobId: string;
  agentType: string;
  model: ModelChoice;
  config: JobConfig;
  organizationId: string;
}

export interface QueueStats {
  waiting: number;
  active: number;
  completed: number;
  failed: number;
  delayed: number;
}

// ============================================
// SESSION & AUTH
// ============================================

export interface AgentSession {
  user: {
    id: string;
    email: string;
    name: string | null;
    organizationId: string;
    permissionLevel: string;
  };
}

// ============================================
// API RESPONSES
// ============================================

export interface SubmitIssueResponse {
  id: string;
  status: IssueStatus;
  jobId?: string;
  estimatedWait?: string;
  trackingUrl: string;
}

export interface IssueStatusResponse {
  id: string;
  status: IssueStatus;
  job?: {
    id: string;
    agentType: string;
    status: JobStatus;
    progress?: number;
    currentStep?: string;
    logs: Pick<AgentLog, 'level' | 'message' | 'timestamp'>[];
  };
  result?: JobResult;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: {
    version: string;
    commit: string;
    deployedAt: string;
  };
  stats: {
    pending: number;
    running: number;
    failedLastHour: number;
    queue: QueueStats;
  };
  timestamp: string;
}
