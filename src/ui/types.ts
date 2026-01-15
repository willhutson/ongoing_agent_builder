/**
 * TypeScript type definitions for SpokeStack Agent UI Components
 *
 * Use these types in the ERP frontend for type-safe agent integration.
 */

// =============================================================================
// Enums
// =============================================================================

export type ActionPriority = 'low' | 'medium' | 'high' | 'urgent';

export type ModuleType =
  | 'projects'
  | 'campaigns'
  | 'clients'
  | 'deliverables'
  | 'reports'
  | 'compliance'
  | 'content_studio'
  | 'sales_pipeline'
  | 'resource_planning';

export type WorkflowStatus =
  | 'pending'
  | 'running'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'cancelled';

// =============================================================================
// Agent Capability Types
// =============================================================================

export interface AgentCapabilityCard {
  agentId: string;
  agentName: string;
  toolName: string;
  toolDescription: string;
  category: string;
  icon: string;
  color: string;
  estimatedDuration: string;
  requiresBrowser: boolean;
  examplePrompt: string;
}

export interface AgentContextualSuggestion {
  id: string;
  agentId: string;
  agentName: string;
  toolName: string;
  suggestionText: string;
  whySuggested: string;
  priority: ActionPriority;
  moduleContext: ModuleType;
  prefilledParams: Record<string, unknown>;
  icon: string;
  color: string;
  dismissable: boolean;
  showLearnMore: boolean;
}

export interface AgentQuickAction {
  id: string;
  label: string;
  agentId: string;
  toolName: string;
  icon: string;
  shortcut?: string;
  tooltip: string;
  requiresSelection: boolean;
  availableInModules: ModuleType[];
}

// =============================================================================
// Workflow Types
// =============================================================================

export interface WorkflowProgressCard {
  executionId: string;
  workflowName: string;
  status: WorkflowStatus;
  progressPercentage: number;
  currentStep: string;
  currentAgent: string;
  stepsCompleted: number;
  stepsTotal: number;
  startedAt: string;
  estimatedCompletion?: string;
  awaitingReview: boolean;
  reviewStepName?: string;
}

export interface WorkflowStep {
  id: string;
  name: string;
  agentId: string;
  toolName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  result?: Record<string, unknown>;
  error?: string;
}

// =============================================================================
// Agent Panel Data
// =============================================================================

export interface AgentPanelData {
  module: ModuleType;
  capabilities: AgentCapabilityCard[];
  quickActions: AgentQuickAction[];
}

// =============================================================================
// Training Types
// =============================================================================

export type CourseLevel = 'beginner' | 'intermediate' | 'advanced';
export type LessonType = 'video' | 'interactive' | 'reading' | 'hands_on' | 'quiz';
export type LessonStatus = 'not_started' | 'in_progress' | 'completed' | 'failed';

export interface TrainingLesson {
  id: string;
  title: string;
  description: string;
  lessonType: LessonType;
  durationMinutes: number;
  order: number;
  requiresCompletion: boolean;
  passingScore?: number;
}

export interface TrainingModule {
  id: string;
  title: string;
  description: string;
  lessons: TrainingLesson[];
  order: number;
  prerequisites: string[];
  totalDurationMinutes: number;
}

export interface TrainingCourse {
  id: string;
  agentId: string;
  title: string;
  description: string;
  level: CourseLevel;
  modules: TrainingModule[];
  version: string;
  certificateOnCompletion: boolean;
  requiredForAgentAccess: boolean;
  targetRoles: string[];
  totalDurationMinutes: number;
  totalLessons: number;
}

export interface LessonProgress {
  lessonId: string;
  status: LessonStatus;
  startedAt?: string;
  completedAt?: string;
  timeSpentSeconds: number;
  quizScore?: number;
  attempts: number;
}

export interface CourseProgress {
  courseId: string;
  userId: string;
  organizationId: string;
  completionPercentage: number;
  isComplete: boolean;
  enrolledAt: string;
  startedAt?: string;
  completedAt?: string;
  certificateIssued: boolean;
}

// =============================================================================
// API Response Types
// =============================================================================

export interface AgentExecutionRequest {
  agentId: string;
  toolName: string;
  params: Record<string, unknown>;
  organizationId: string;
  userId: string;
  contextId?: string; // e.g., projectId, campaignId
}

export interface AgentExecutionResponse {
  success: boolean;
  executionId: string;
  result?: Record<string, unknown>;
  error?: string;
  screenshot?: string;
  duration: number;
}

export interface WorkflowExecutionRequest {
  workflowId: string;
  context: Record<string, unknown>;
  organizationId: string;
  userId: string;
}

export interface WorkflowExecutionResponse {
  success: boolean;
  executionId: string;
  status: WorkflowStatus;
  results: Record<string, unknown>;
  error?: string;
}
