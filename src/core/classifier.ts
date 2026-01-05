/**
 * Issue Classifier
 *
 * Uses AI to analyze incoming issues and determine:
 * - Issue type and priority
 * - Complexity score
 * - Target module
 * - Recommended agent
 * - Appropriate model
 */

import Anthropic from '@anthropic-ai/sdk';
import type { AgentIssue, ClassificationResult, ModelChoice } from '../types/index.js';
import { getConfig, MODEL_IDS } from '../config/index.js';

// ============================================
// CLASSIFICATION PROMPT
// ============================================

const CLASSIFICATION_PROMPT = `You are an issue classifier for the SpokeStack ERP platform. Analyze the following issue and provide a classification.

## Available Modules
- briefs: Work request management (VIDEO_SHOOT, VIDEO_EDIT, DESIGN, COPYWRITING, etc.)
- time: Time tracking, timers, timesheets
- resources: Resource planning, capacity, availability
- leave: Leave management, requests, approvals
- rfp: Request for proposals, pipeline, estimation
- retainers: Retainer management, burn rates, scope changes
- studio: Content creation, calendars, video projects, moodboards
- crm: Customer relationship management, deals, contacts
- lms: Learning management, courses, assessments
- boards: Kanban boards, cards, checklists
- workflow: Workflow automation, triggers, approvals
- chat: Internal messaging, channels
- analytics: Dashboards, metrics, reports
- surveys: Survey creation, distribution, NPS
- integrations: Slack, Google, webhooks
- admin: User management, permissions, settings

## Agent Types
For each module, there are specialized agents like:
- {module}.status-workflow - Status transitions
- {module}.assignment - Assignment logic
- {module}.reports - Reporting and analytics
- {module}.notifications - Notification handling
- meta.triage - Quick assessment and routing
- meta.research - Deep investigation
- meta.deployment - Instance deployment (for new clients)
- meta.review - Code review

## Complexity Scale (1-10)
1-3: Simple config change, typo fix, small bug
4-6: Moderate feature, multi-file change
7-8: Complex feature, architectural change
9-10: System-wide change, major refactoring

## Model Selection
- haiku: Simple issues (complexity 1-3)
- sonnet: Moderate issues (complexity 4-7)
- opus: Complex issues (complexity 8-10) or creative/strategic tasks

Analyze the issue and respond with a JSON object:
{
  "issueType": "BUG" | "FEATURE" | "ENHANCEMENT" | "QUESTION" | "TASK" | "DEPLOYMENT",
  "priority": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "complexity": 1-10,
  "module": "module-name",
  "suggestedAgent": "module.agent-type",
  "suggestedModel": "haiku" | "sonnet" | "opus",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of classification"
}`;

// ============================================
// CLASSIFIER
// ============================================

export async function classify(issue: AgentIssue): Promise<ClassificationResult> {
  const config = getConfig();

  const client = new Anthropic({
    apiKey: config.ANTHROPIC_API_KEY,
  });

  const issueContext = `
## Issue Details
- Title: ${issue.title}
- Type: ${issue.type}
- Priority: ${issue.priority}
- Description: ${issue.description}
${issue.context.module ? `- Mentioned Module: ${issue.context.module}` : ''}
${issue.context.errorLogs ? `- Error Logs: ${issue.context.errorLogs.slice(0, 500)}` : ''}
`;

  const response = await client.messages.create({
    model: MODEL_IDS.haiku, // Use haiku for fast classification
    max_tokens: 1024,
    messages: [
      {
        role: 'user',
        content: `${CLASSIFICATION_PROMPT}\n\n${issueContext}`,
      },
    ],
  });

  // Extract JSON from response
  const textContent = response.content.find((c) => c.type === 'text');
  if (!textContent || textContent.type !== 'text') {
    throw new Error('No text content in classification response');
  }

  const jsonMatch = textContent.text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error('No JSON found in classification response');
  }

  const result = JSON.parse(jsonMatch[0]) as ClassificationResult;

  // Validate and normalize
  return {
    issueType: result.issueType || issue.type,
    priority: result.priority || issue.priority,
    complexity: Math.min(10, Math.max(1, result.complexity || 5)),
    module: result.module || issue.context.module || 'general',
    suggestedAgent: result.suggestedAgent || 'meta.research',
    suggestedModel: validateModel(result.suggestedModel),
    confidence: Math.min(1, Math.max(0, result.confidence || 0.5)),
    reasoning: result.reasoning || 'No reasoning provided',
  };
}

function validateModel(model: string | undefined): ModelChoice {
  if (model === 'haiku' || model === 'sonnet' || model === 'opus') {
    return model;
  }
  return 'sonnet'; // Default to sonnet
}

// ============================================
// COMPLEXITY ESTIMATOR
// ============================================

/**
 * Estimate complexity based on heuristics (fallback when AI unavailable)
 */
export function estimateComplexity(issue: AgentIssue): number {
  let score = 5; // Start at medium

  // Adjust based on type
  if (issue.type === 'BUG') score -= 1;
  if (issue.type === 'FEATURE') score += 1;
  if (issue.type === 'DEPLOYMENT') score += 3;

  // Adjust based on description length
  const wordCount = issue.description.split(/\s+/).length;
  if (wordCount < 20) score -= 1;
  if (wordCount > 100) score += 1;
  if (wordCount > 300) score += 2;

  // Adjust based on keywords
  const complexKeywords = ['refactor', 'architecture', 'migration', 'integration', 'performance'];
  const simpleKeywords = ['typo', 'text', 'label', 'color', 'spacing'];

  for (const kw of complexKeywords) {
    if (issue.description.toLowerCase().includes(kw)) score += 1;
  }
  for (const kw of simpleKeywords) {
    if (issue.description.toLowerCase().includes(kw)) score -= 1;
  }

  return Math.min(10, Math.max(1, score));
}

/**
 * Select model based on complexity
 */
export function selectModelByComplexity(complexity: number): ModelChoice {
  if (complexity <= 3) return 'haiku';
  if (complexity <= 7) return 'sonnet';
  return 'opus';
}
