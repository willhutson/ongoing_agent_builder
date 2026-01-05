/**
 * Integration Types
 *
 * Type definitions for all ERP integrations that agents can use
 */

// ============================================
// INTEGRATION PROVIDERS
// ============================================

export type IntegrationProvider =
  | 'google'
  | 'slack'
  | 'openai'
  | 'anthropic'
  | 'pusher'
  | 'resend'
  | 'bigquery'
  | 'phyllo'
  | 'whatsapp'
  | 'meta'
  | 'figma'
  | 'cloudflare'
  | 'custom';

// ============================================
// GOOGLE WORKSPACE
// ============================================

export interface GoogleTokens {
  access_token: string;
  refresh_token: string;
  expiry_date: number;
  scope?: string;
}

export interface GoogleCalendarEvent {
  id?: string;
  summary: string;
  description?: string;
  location?: string;
  start: {
    dateTime: string;
    timeZone?: string;
  };
  end: {
    dateTime: string;
    timeZone?: string;
  };
  attendees?: Array<{ email: string }>;
}

export interface GoogleDriveFile {
  id: string;
  name: string;
  mimeType: string;
  webViewLink?: string;
  parents?: string[];
}

export type GoogleDocType = 'document' | 'spreadsheet' | 'presentation';

// ============================================
// SLACK
// ============================================

export interface SlackMessage {
  channel: string;
  text: string;
  blocks?: SlackBlock[];
  thread_ts?: string;
  unfurl_links?: boolean;
}

export interface SlackBlock {
  type: 'section' | 'header' | 'divider' | 'context' | 'actions';
  text?: {
    type: 'plain_text' | 'mrkdwn';
    text: string;
  };
  elements?: unknown[];
  accessory?: unknown;
}

export interface SlackChannel {
  id: string;
  name: string;
  is_private: boolean;
  is_member: boolean;
}

export interface SlackWorkspaceConfig {
  teamId: string;
  teamName: string;
  accessToken: string;
  botUserId: string;
  defaultChannelId?: string;
}

// ============================================
// OPENAI
// ============================================

export type AIAction =
  | 'translate_ar'
  | 'translate_en'
  | 'polish'
  | 'expand'
  | 'summarize'
  | 'simplify'
  | 'formal'
  | 'casual'
  | 'generate_caption'
  | 'analyze'
  | 'code_review'
  | 'generate_code';

export interface AIOptions {
  action: AIAction;
  text: string;
  context?: string;
  platform?: string;
  maxLength?: number;
  useFastModel?: boolean;
}

export interface AIResult {
  success: boolean;
  result?: string;
  error?: string;
  tokensUsed?: number;
  model?: string;
}

export interface TranscriptionResult {
  text: string;
  language: string;
  confidence: number;
  duration: number;
  cost: number;
}

// ============================================
// PUSHER (Real-time)
// ============================================

export interface PusherEvent {
  channel: string;
  event: string;
  data: unknown;
}

export interface PusherConfig {
  appId: string;
  key: string;
  secret: string;
  cluster: string;
}

// ============================================
// RESEND (Email)
// ============================================

export interface EmailOptions {
  to: string | string[];
  subject: string;
  html?: string;
  text?: string;
  from?: string;
  replyTo?: string;
  tags?: Array<{ name: string; value: string }>;
}

export interface EmailResult {
  id: string;
  success: boolean;
  error?: string;
}

// ============================================
// BIGQUERY
// ============================================

export interface BigQueryConfig {
  projectId: string;
  credentials: Record<string, unknown>;
}

export interface BigQueryResult<T = unknown> {
  rows: T[];
  totalRows: number;
  schema: Array<{ name: string; type: string }>;
}

// ============================================
// PHYLLO (Creator Data)
// ============================================

export interface PhylloConfig {
  clientId: string;
  clientSecret: string;
  environment: 'sandbox' | 'production';
}

export interface CreatorProfile {
  id: string;
  platform: 'instagram' | 'tiktok' | 'youtube' | 'twitter';
  username: string;
  followers: number;
  engagementRate: number;
  profileUrl: string;
}

// ============================================
// WHATSAPP
// ============================================

export interface WhatsAppMessage {
  to: string;
  type: 'text' | 'template' | 'media';
  content: string;
  templateName?: string;
  templateParams?: string[];
  mediaUrl?: string;
}

export interface WhatsAppConversation {
  id: string;
  phoneNumber: string;
  displayName?: string;
  status: 'active' | 'closed';
  lastMessageAt?: Date;
}

// ============================================
// NOTIFICATION TYPES
// ============================================

export type NotificationChannel = 'in_app' | 'email' | 'slack' | 'push';

export interface NotificationOptions {
  type: string;
  recipientId?: string;
  recipientEmail?: string;
  title: string;
  body: string;
  actionUrl?: string;
  channels: NotificationChannel[];
  priority?: 'low' | 'normal' | 'high';
  metadata?: Record<string, unknown>;
}

// ============================================
// INTEGRATION RECORD
// ============================================

export interface Integration {
  id: string;
  organizationId: string;
  provider: IntegrationProvider;
  isEnabled: boolean;
  credentials?: Record<string, unknown>;
  settings: Record<string, unknown>;
  lastSyncAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

// ============================================
// WEBHOOK TYPES
// ============================================

export interface WebhookSubscription {
  id: string;
  organizationId: string;
  url: string;
  events: string[];
  secret: string;
  isActive: boolean;
}

export interface WebhookPayload {
  event: string;
  timestamp: string;
  data: unknown;
  signature: string;
}
