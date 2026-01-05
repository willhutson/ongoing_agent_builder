/**
 * Agent System Configuration
 */

import { z } from 'zod';
import type { ModelChoice } from '../types/index.js';

// ============================================
// ENVIRONMENT SCHEMA
// ============================================

const envSchema = z.object({
  // Anthropic
  ANTHROPIC_API_KEY: z.string().min(1, 'ANTHROPIC_API_KEY is required'),

  // Agent settings
  AGENT_ENABLED: z.string().transform((v) => v === 'true').default('true'),
  AGENT_DEBUG: z.string().transform((v) => v === 'true').default('false'),
  AGENT_MAX_CONCURRENCY: z.string().transform(Number).default('5'),
  AGENT_DEFAULT_MODEL: z.enum(['haiku', 'sonnet', 'opus']).default('sonnet'),
  AGENT_JOB_TIMEOUT: z.string().transform(Number).default('300000'), // 5 minutes

  // Queue (Upstash Redis)
  UPSTASH_REDIS_REST_URL: z.string().url().optional(),
  UPSTASH_REDIS_REST_TOKEN: z.string().optional(),

  // GitHub
  GITHUB_TOKEN: z.string().optional(),
  GITHUB_REPO_OWNER: z.string().default('willhutson'),
  GITHUB_REPO_NAME: z.string().default('erp_staging_lmtd'),

  // Telemetry
  AGENT_TELEMETRY_ENABLED: z.string().transform((v) => v === 'true').default('true'),
});

export type EnvConfig = z.infer<typeof envSchema>;

// ============================================
// CONFIGURATION
// ============================================

function loadConfig(): EnvConfig {
  const result = envSchema.safeParse(process.env);

  if (!result.success) {
    console.error('❌ Invalid environment configuration:');
    console.error(result.error.format());
    throw new Error('Invalid environment configuration');
  }

  return result.data;
}

// Lazy-load config to allow for testing
let _config: EnvConfig | null = null;

export function getConfig(): EnvConfig {
  if (!_config) {
    _config = loadConfig();
  }
  return _config;
}

// ============================================
// MODEL CONFIGURATION
// ============================================

export const MODEL_IDS: Record<ModelChoice, string> = {
  haiku: 'claude-3-5-haiku-20241022',
  sonnet: 'claude-sonnet-4-20250514',
  opus: 'claude-opus-4-5-20250101',
};

export const MODEL_LIMITS: Record<ModelChoice, { maxTokens: number; timeout: number }> = {
  haiku: { maxTokens: 4096, timeout: 60000 },
  sonnet: { maxTokens: 8192, timeout: 180000 },
  opus: { maxTokens: 16384, timeout: 300000 },
};

// ============================================
// RATE LIMITS
// ============================================

export const RATE_LIMITS = {
  // Per organization
  org: {
    requestsPerHour: 100,
    concurrentJobs: 3,
  },
  // Global
  global: {
    concurrentJobs: 10,
  },
};

// ============================================
// FEATURE FLAGS
// ============================================

export interface FeatureFlags {
  enabled: boolean;
  agents: Record<string, boolean>;
  features: {
    parallelExecution: boolean;
    githubPRCreation: boolean;
    slackNotifications: boolean;
    autoRetry: boolean;
  };
}

export function getFeatureFlags(): FeatureFlags {
  const config = getConfig();

  return {
    enabled: config.AGENT_ENABLED,
    agents: {
      // All agents enabled by default
      'meta.triage': true,
      'meta.research': true,
      'meta.deployment': true,
      'meta.review': true,
      'briefs.*': true,
      'time.*': true,
      'resources.*': true,
      'crm.*': true,
      'studio.*': true,
      'lms.*': true,
    },
    features: {
      parallelExecution: true,
      githubPRCreation: !!config.GITHUB_TOKEN,
      slackNotifications: false, // Enable when Slack integration added
      autoRetry: true,
    },
  };
}

// ============================================
// VERSION
// ============================================

export const AGENT_VERSION = {
  version: '0.1.0',
  commit: process.env.VERCEL_GIT_COMMIT_SHA?.slice(0, 7) || 'local',
  deployedAt: process.env.VERCEL_GIT_COMMIT_DATE || new Date().toISOString(),
};

// Log version on import
console.log(`🤖 Agent System v${AGENT_VERSION.version} (${AGENT_VERSION.commit})`);
