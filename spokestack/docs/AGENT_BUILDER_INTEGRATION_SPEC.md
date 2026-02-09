# Agent Builder Integration Specification

**For:** ongoing_agent_builder repository
**From:** SpokeStack Platform
**Version:** 2.0
**Date:** February 2025

---

## Overview

This specification defines how agents from the Agent Builder integrate with SpokeStack's Mission Control interface. It covers:

1. Agent state management and status reporting
2. Artifact creation and streaming
3. Post-completion action routing
4. Multi-model support
5. Skill stack configuration
6. Agent-to-agent handoffs
7. **Agent Work Protocol** - Live SpokeStack operation with work events and tool definitions

---

## 1. Agent State Protocol

### 1.1 State Machine

Agents must report their state to SpokeStack via the following state machine:

```
                    ┌──────────────┐
                    │    IDLE      │
                    └──────┬───────┘
                           │ start()
                           ▼
                    ┌──────────────┐
          ┌────────│   THINKING   │────────┐
          │        └──────┬───────┘        │
          │               │                │
          │ needsInput()  │ work()         │ error()
          │               ▼                │
          │        ┌──────────────┐        │
          │        │   WORKING    │────────┤
          │        └──────┬───────┘        │
          │               │                │
          ▼               │ complete()     ▼
   ┌──────────────┐       │         ┌──────────────┐
   │   WAITING    │       │         │    ERROR     │
   │  (PENDING)   │       │         └──────────────┘
   └──────────────┘       │
          │               │
          │ userInput()   │
          │               ▼
          │        ┌──────────────┐
          └───────▶│   COMPLETE   │
                   └──────────────┘
```

### 1.2 State Payload

Agents must emit state updates via WebSocket or webhook:

```typescript
interface AgentStateUpdate {
  chatId: string;
  agentId: string;
  agentType: AgentType;
  timestamp: string;               // ISO 8601

  state: 'idle' | 'thinking' | 'working' | 'waiting' | 'complete' | 'error';

  // For WORKING state
  progress?: {
    current: number;               // e.g., 5
    total: number;                 // e.g., 12
    label: string;                 // e.g., "Building slide 5/12"
    percentage: number;            // e.g., 41.67
  };

  // For WAITING state (triggers 🔴 PENDING indicator)
  waitingFor?: {
    type: 'user_input' | 'approval' | 'selection' | 'confirmation';
    prompt: string;                // "Which client is this for?"
    options?: string[];            // ["CCAD", "DET", "ADEK"]
    required: boolean;
    timeout_minutes?: number;      // Optional timeout
  };

  // For COMPLETE state (triggers 🟢 COMPLETE indicator)
  completion?: {
    summary: string;               // "Created 20 calendar entries"
    artifact_ids: string[];        // References to created artifacts
    suggested_actions: SuggestedAction[];
    metrics?: {
      duration_ms: number;
      tokens_used: number;
      cost_estimate: number;
    };
  };

  // For ERROR state (triggers 🟠 ERROR indicator)
  error?: {
    code: string;                  // "API_RATE_LIMIT"
    message: string;               // "Meta API rate limited"
    recoverable: boolean;
    retry_after_seconds?: number;
    user_action_required?: string; // "Please reconnect Meta account"
  };
}
```

### 1.3 Status Indicator Mapping

| Agent State | UI Indicator | Color | Behavior |
|-------------|--------------|-------|----------|
| `idle` | ⚪ IDLE | Gray | Static |
| `thinking` | 🔵 RUNNING | Blue | Pulse animation |
| `working` | 🔵 RUNNING | Blue | Pulse + progress bar |
| `waiting` | 🔴 PENDING | Red | Continuous pulse until resolved |
| `complete` | 🟢 COMPLETE | Green | Flash 3x on completion |
| `error` | 🟠 ERROR | Orange | Pulse until acknowledged |

---

## 2. Artifact Protocol

### 2.1 Artifact Creation

Agents create artifacts by emitting artifact events:

```typescript
interface ArtifactEvent {
  event: 'artifact:create' | 'artifact:update' | 'artifact:complete';
  chatId: string;
  agentId: string;

  artifact: {
    id: string;                    // UUID
    type: ArtifactType;
    moduleType: ModuleType;
    title: string;
    status: 'building' | 'draft' | 'final';
    version: number;

    // Module-specific structured data
    data: Record<string, unknown>;

    // Optional preview for UI rendering
    preview?: {
      type: 'html' | 'markdown' | 'json';
      content: string;
    };

    // Metadata
    clientId?: string;
    projectId?: string;
  };
}
```

### 2.2 Artifact Types

```typescript
type ArtifactType =
  // Content
  | 'calendar'           // Content calendar entries
  | 'brief'              // Work brief
  | 'document'           // Rich text document
  | 'deck'               // Presentation slides
  | 'moodboard'          // Visual inspiration board

  // Video
  | 'script'             // Video script
  | 'storyboard'         // Storyboard frames
  | 'shot_list'          // Production shot list

  // Data
  | 'report'             // Analytics report
  | 'table'              // Data table
  | 'chart'              // Visualization

  // Operations
  | 'contract'           // Legal contract
  | 'survey'             // Survey/quiz
  | 'course'             // LMS course
  | 'workflow'           // Automation workflow
```

### 2.3 Streaming Artifacts

For real-time artifact building, use streaming updates:

```typescript
// Initial creation
emit('artifact:create', {
  artifact: {
    id: 'abc-123',
    type: 'calendar',
    title: 'CCAD February Calendar',
    status: 'building',
    data: { entries: [] }
  }
});

// Incremental updates (stream as content is generated)
emit('artifact:update', {
  artifact: {
    id: 'abc-123',
    data: {
      entries: [
        { date: '2025-02-03', platform: 'instagram', ... }
      ]
    }
  }
});

// More entries...
emit('artifact:update', { ... });

// Final completion
emit('artifact:complete', {
  artifact: {
    id: 'abc-123',
    status: 'draft',
    data: { entries: [...all 20 entries...] }
  }
});
```

---

## 3. Post-Completion Actions

### 3.1 Suggested Actions

When an agent completes, it must provide suggested next actions:

```typescript
interface SuggestedAction {
  id: string;
  type: ActionType;
  label: string;                   // "Share with Client for Approval"
  description?: string;            // "Send to CCAD contacts via email/portal"
  icon?: string;                   // "send" | "users" | "file-plus"

  // Action configuration
  config: ActionConfig;

  // Ordering
  priority: number;                // 1 = primary action

  // Conditional display
  conditions?: {
    requires_client?: boolean;
    requires_project?: boolean;
    user_roles?: string[];         // ["ADMIN", "LEADERSHIP"]
  };
}

type ActionType =
  | 'share_client'          // Send to client for review/approval
  | 'share_internal'        // Share with internal team
  | 'assign_team'           // Assign to team member(s)
  | 'handoff_agent'         // Spawn another agent
  | 'add_to_module'         // Save to a module (calendar, projects, etc.)
  | 'export'                // Export to file format
  | 'approve'               // Mark as approved/final
  | 'schedule'              // Schedule for future action
  | 'custom'                // Custom action with callback
```

### 3.2 Standard Actions by Artifact Type

Agents should suggest these actions based on artifact type:

```typescript
const STANDARD_ACTIONS: Record<ArtifactType, ActionType[]> = {
  calendar: [
    'share_client',
    'handoff_agent',        // → Brief Writer
    'add_to_module',        // → /studio/calendar
    'export',               // → CSV, PDF
  ],

  brief: [
    'assign_team',
    'share_client',
    'add_to_module',        // → /briefs
    'handoff_agent',        // → relevant production agent
  ],

  deck: [
    'share_client',
    'share_internal',       // → leadership review
    'export',               // → PPTX, PDF
    'add_to_module',        // → /studio/decks
  ],

  report: [
    'share_client',
    'share_internal',
    'schedule',             // → recurring report
    'export',
  ],

  contract: [
    'share_internal',       // → legal review
    'handoff_agent',        // → signature workflow
    'add_to_module',        // → /contracts
  ],

  // ... etc
};
```

### 3.3 Action Execution

When user selects an action, SpokeStack calls the agent builder:

```typescript
// Request from SpokeStack to Agent Builder
interface ExecuteActionRequest {
  chatId: string;
  artifactId: string;
  action: {
    type: ActionType;
    config: ActionConfig;
  };
  context: {
    userId: string;
    organizationId: string;
    clientId?: string;
  };
}

// Response from Agent Builder
interface ExecuteActionResponse {
  success: boolean;

  // For handoff_agent actions
  newChatId?: string;
  newAgentType?: AgentType;

  // For external actions
  externalUrl?: string;

  // For module actions
  moduleUrl?: string;              // e.g., "/briefs/abc-123"

  // For share actions
  shareResult?: {
    recipients: string[];
    channel: 'portal' | 'email' | 'both';
    notificationSent: boolean;
  };

  error?: string;
}
```

---

## 4. Multi-Model Support

### 4.1 Model Configuration

Agents must support configurable models:

```typescript
interface AgentModelConfig {
  // Available models the agent can use
  supportedModels: ModelConfig[];

  // Default model
  defaultModel: string;

  // Model switching capability
  allowMidConversationSwitch: boolean;

  // Auto-switch recommendations
  autoSwitchRules?: AutoSwitchRule[];
}

interface ModelConfig {
  id: string;                      // "claude-opus-4"
  name: string;                    // "Claude Opus 4"
  provider: 'anthropic' | 'openai' | 'google';
  capabilities: string[];          // ["reasoning", "creative", "code"]
  costTier: 'low' | 'medium' | 'high';
  speedTier: 'fast' | 'medium' | 'slow';
  contextWindow: number;

  // When to recommend this model
  recommendedFor: string[];        // ["strategy", "complex_analysis"]
}

interface AutoSwitchRule {
  trigger: string;                 // "user mentions 'iterate quickly'"
  fromModel: string;
  toModel: string;
  promptUser: boolean;             // Ask before switching?
}
```

### 4.2 Model Selection API

SpokeStack sends model preference when starting a chat:

```typescript
interface StartChatRequest {
  agentType: AgentType;
  organizationId: string;
  userId: string;

  // Model configuration
  model: {
    id: string;                    // Selected model
    allowAutoSwitch: boolean;
  };

  // Skill configuration
  skills: {
    platformSkills: string[];      // IDs of platform skills to use
    instanceSkills: string[];      // IDs of org-specific skills
    clientSkills?: string[];       // IDs of client-specific skills
    disabledSkills?: string[];     // Skills to exclude
  };

  // Context
  context: {
    clientId?: string;
    projectId?: string;
    relatedArtifacts?: string[];
  };
}
```

### 4.3 Mid-Conversation Model Switch

```typescript
interface SwitchModelRequest {
  chatId: string;
  newModelId: string;
  reason?: string;                 // "User requested faster iterations"
}

// Agent should acknowledge the switch
interface SwitchModelAck {
  chatId: string;
  previousModel: string;
  newModel: string;
  contextPreserved: boolean;
  message: string;                 // "Switched to Sonnet 4 for faster iterations"
}
```

---

## 5. Skill Stack Protocol

### 5.1 Skill Layers

Agents receive skills organized in layers:

```typescript
interface SkillStack {
  // Layer 2: Platform skills (from agent builder)
  platformSkills: Skill[];

  // Layer 3: Instance skills (from SpokeStack org)
  instanceSkills: Skill[];

  // Layer 4: Client knowledge (from SpokeStack)
  clientKnowledge: KnowledgeDocument[];
}

interface Skill {
  id: string;
  slug: string;                    // "deck-narrative-structure"
  name: string;
  description: string;

  // Skill definition
  type: 'tool' | 'prompt' | 'workflow';
  definition: SkillDefinition;

  // Metadata
  category: string;
  enabled: boolean;

  // For instance skills extending platform skills
  extends?: string;                // Platform skill slug
}

interface KnowledgeDocument {
  id: string;
  path: string;                    // "/clients/ccad/brand-guide"
  title: string;
  type: 'brand_guide' | 'procedure' | 'policy' | 'reference';
  content: string;
  metadata: Record<string, unknown>;
}
```

### 5.2 Runtime Skill Toggle

Users can toggle skills during a conversation:

```typescript
interface ToggleSkillRequest {
  chatId: string;
  skillId: string;
  enabled: boolean;
  reason?: string;                 // "User doesn't want case studies"
}

// Agent acknowledges and adjusts behavior
interface ToggleSkillAck {
  chatId: string;
  skillId: string;
  enabled: boolean;
  message: string;                 // "Disabled case-study-library for this session"
}
```

---

## 6. Agent-to-Agent Handoffs

### 6.1 Handoff Protocol

When an agent needs to spawn another agent:

```typescript
interface HandoffRequest {
  fromChatId: string;
  fromAgentType: AgentType;

  // Target agent
  toAgentType: AgentType;

  // Context to pass
  context: {
    artifacts: string[];           // Artifact IDs to reference
    summary: string;               // What was accomplished
    instructions: string;          // What the new agent should do
    clientId?: string;
    projectId?: string;
  };

  // User involvement
  requiresUserApproval: boolean;
  autoStart: boolean;              // Start immediately after approval?
}

interface HandoffResponse {
  approved: boolean;
  newChatId?: string;
  newAgentType?: AgentType;
  message: string;
}
```

### 6.2 Cross-Agent Context

The new agent receives context from the parent:

```typescript
interface HandoffContext {
  parentChatId: string;
  parentAgentType: AgentType;
  parentSummary: string;

  // Inherited context
  artifacts: Artifact[];           // Full artifact data
  relevantMessages: ChatMessage[]; // Key messages from parent

  // Instructions
  task: string;                    // "Create briefs for calendar entries"
  constraints?: string[];          // Any limitations
}
```

---

## 7. WebSocket Events

### 7.1 Event Types

All communication uses these WebSocket events:

```typescript
// From Agent Builder → SpokeStack
type AgentEvent =
  | { type: 'state:update'; payload: AgentStateUpdate }
  | { type: 'message:stream'; payload: MessageChunk }
  | { type: 'message:complete'; payload: ChatMessage }
  | { type: 'artifact:create'; payload: ArtifactEvent }
  | { type: 'artifact:update'; payload: ArtifactEvent }
  | { type: 'artifact:complete'; payload: ArtifactEvent }
  | { type: 'handoff:request'; payload: HandoffRequest }
  | { type: 'model:switch:suggest'; payload: SwitchSuggestion }
  | { type: 'skill:toggle:ack'; payload: ToggleSkillAck };

// From SpokeStack → Agent Builder
type PlatformEvent =
  | { type: 'chat:start'; payload: StartChatRequest }
  | { type: 'message:send'; payload: UserMessage }
  | { type: 'action:execute'; payload: ExecuteActionRequest }
  | { type: 'model:switch'; payload: SwitchModelRequest }
  | { type: 'skill:toggle'; payload: ToggleSkillRequest }
  | { type: 'handoff:approve'; payload: HandoffApproval }
  | { type: 'chat:cancel'; payload: { chatId: string } };
```

### 7.2 Connection Management

```typescript
// Connection URL
wss://agent-builder.spokestack.io/v1/ws

// Auth header
Authorization: Bearer <organization_api_key>
X-Organization-Id: <organization_id>

// Heartbeat every 30s
{ type: 'ping' }
{ type: 'pong' }

// Reconnection: exponential backoff 1s, 2s, 4s, 8s, max 30s
```

---

## 8. API Endpoints

### 8.1 REST API (for non-streaming operations)

```
Base URL: https://agent-builder.spokestack.io/api/v1

# List available agents
GET /agents
→ AgentConfig[]

# Get agent configuration
GET /agents/:agentType
→ AgentConfig

# Start new chat (returns WebSocket URL)
POST /chats
Body: StartChatRequest
→ { chatId, wsUrl }

# Get chat state
GET /chats/:chatId
→ ChatSession

# Execute action
POST /chats/:chatId/actions
Body: ExecuteActionRequest
→ ExecuteActionResponse

# Get artifacts
GET /chats/:chatId/artifacts
→ Artifact[]
```

---

## 9. Error Handling

### 9.1 Error Codes

```typescript
const ERROR_CODES = {
  // Agent errors
  AGENT_NOT_FOUND: 'Agent type not available',
  AGENT_BUSY: 'Agent is processing another request',
  AGENT_TIMEOUT: 'Agent took too long to respond',

  // Model errors
  MODEL_NOT_AVAILABLE: 'Selected model not available',
  MODEL_RATE_LIMITED: 'Model API rate limited',
  MODEL_CONTEXT_EXCEEDED: 'Conversation too long for model',

  // Skill errors
  SKILL_NOT_FOUND: 'Skill not found',
  SKILL_EXECUTION_FAILED: 'Skill failed to execute',

  // Action errors
  ACTION_NOT_SUPPORTED: 'Action not supported for this artifact',
  ACTION_FAILED: 'Action execution failed',

  // Auth errors
  UNAUTHORIZED: 'Invalid or expired token',
  FORBIDDEN: 'Insufficient permissions',
  ORG_NOT_FOUND: 'Organization not found',
};
```

### 9.2 Error Response Format

```typescript
interface AgentError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  recoverable: boolean;
  retryAfter?: number;             // Seconds
  userActionRequired?: string;
}
```

---

## 10. Example Flow

### Complete Calendar Creation Flow

```
1. User starts new chat
   → SpokeStack sends: chat:start (Content Strategist, Claude Opus 4)
   → Agent responds: state:update (THINKING)

2. User sends message: "Create February calendar for CCAD"
   → SpokeStack sends: message:send
   → Agent responds: state:update (WORKING, progress: 0/20)

3. Agent creates artifact
   → Agent sends: artifact:create (calendar, building)

4. Agent streams updates
   → Agent sends: artifact:update (entry 1)
   → Agent sends: state:update (WORKING, progress: 1/20)
   → Agent sends: artifact:update (entry 2)
   → Agent sends: state:update (WORKING, progress: 2/20)
   → ... (repeat for all entries)

5. Agent completes
   → Agent sends: artifact:complete (calendar, draft)
   → Agent sends: state:update (COMPLETE)
   → Agent sends: message:complete (summary + suggested_actions)

6. User sees 🟢 COMPLETE and action options

7. User selects "Create Briefs from Calendar"
   → SpokeStack sends: action:execute (handoff_agent)
   → Agent sends: handoff:request (Brief Writer)

8. SpokeStack creates new chat for Brief Writer
   → New WebSocket connection
   → Brief Writer receives handoff context
   → Process repeats
```

---

## 11. Agent Work Protocol (Live Operations)

### 11.1 The "Screen Share" Paradigm

Mission Control now operates with a **3-column layout**:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  MISSION CONTROL                                                              │
├────────────┬───────────────────────┬──────────────────┬──────────────────────┤
│  SIDEBAR   │     CHAT PANE         │  AGENT WORK PANE │   ARTIFACT PANE      │
│            │                       │                  │                      │
│  Chat List │  Conversation with    │  LIVE view of    │  Preview of          │
│  + Agent   │  agent (streaming     │  agent operating │  generated           │
│  Switcher  │  text responses)      │  SpokeStack      │  artifacts           │
│            │                       │  (screen share)  │                      │
└────────────┴───────────────────────┴──────────────────┴──────────────────────┘
```

**Key Insight:** Agents don't just generate text responses—they **operate SpokeStack on behalf of users**. The Agent Work pane shows this operation in real-time, like watching someone use the software for you.

### 11.2 Agent Work State

Agents must track and emit work state for the screen-share view:

```typescript
interface AgentWorkState {
  chatId: string;
  isWorking: boolean;

  // Current location in SpokeStack
  currentModule?: AgentWorkModule;
  currentRoute?: string;
  currentEntity?: string;

  // Action tracking
  actions: AgentAction[];

  // Form field tracking (for forms being filled)
  pendingFields: string[];
  completedFields: string[];

  // Created entities
  createdEntities: CreatedEntity[];

  // Error state
  error?: string;
}

type AgentWorkModule =
  | "briefs"
  | "studio/calendar"
  | "studio/decks"
  | "projects"
  | "clients"
  | "deals"
  | "rfp"
  | "time"
  | "resources"
  | "lms/courses"
  | "team";

interface AgentAction {
  id: string;
  type: AgentActionType;
  timestamp: string;
  module?: AgentWorkModule;
  route?: string;

  // For fill_field actions
  field?: string;
  fieldLabel?: string;
  value?: unknown;
  displayValue?: string;

  // Status
  status: "pending" | "filling" | "filled" | "success" | "error";
  message?: string;
}

type AgentActionType =
  | "navigate"      // Moving to a route
  | "open_form"     // Opening a creation form
  | "fill_field"    // Filling a form field
  | "select_option" // Selecting from dropdown/multi-select
  | "create"        // Creating an entity
  | "update"        // Updating an entity
  | "assign"        // Assigning to a user
  | "submit"        // Submitting a form
  | "complete"      // Task completed
  | "error";        // Error occurred

interface CreatedEntity {
  id: string;
  type: string;      // "brief", "calendar_entry", "project", etc.
  title: string;
  module: AgentWorkModule;
  url: string;       // Deep link to entity
}
```

### 11.3 Agent Work SSE Events

Agents emit work events during SSE streaming to update the Agent Work pane:

```typescript
// SSE Event: work_start
// Emit when agent begins operating SpokeStack
{
  "type": "work_start",
  "module": "briefs",
  "route": "/briefs/new",
  "pendingFields": ["title", "client", "type", "description", "deadline"]
}

// SSE Event: action
// Emit for each action taken in SpokeStack
{
  "type": "action",
  "action": {
    "id": "act_123",
    "type": "fill_field",
    "field": "title",
    "fieldLabel": "Brief Title",
    "value": "CCAD February Social Campaign",
    "displayValue": "CCAD February Social Campaign",
    "status": "filled",
    "module": "briefs",
    "route": "/briefs/new"
  }
}

// SSE Event: entity_created
// Emit when an entity is successfully created in SpokeStack
{
  "type": "entity_created",
  "entity": {
    "id": "brief_abc123",
    "type": "brief",
    "title": "CCAD February Social Campaign",
    "module": "briefs",
    "url": "/briefs/brief_abc123"
  }
}

// SSE Event: work_complete
// Emit when agent finishes operating SpokeStack
{
  "type": "work_complete",
  "state": {
    "isWorking": false,
    "createdEntities": [
      { "id": "brief_abc123", "type": "brief", "title": "...", ... }
    ]
  }
}

// SSE Event: work_error
// Emit if an error occurs during operation
{
  "type": "work_error",
  "error": "Failed to create brief: Client not found"
}
```

### 11.4 SpokeStack Tool Definitions

For agents to operate SpokeStack, they need tools that call SpokeStack APIs. Each tool should emit work events during execution.

#### Required Tools for All Agents

```typescript
// Tool: navigate_to
// Navigate to a SpokeStack route
{
  name: "navigate_to",
  description: "Navigate to a specific SpokeStack module or route",
  parameters: {
    module: AgentWorkModule,
    route: string,     // e.g., "/briefs/new", "/briefs/{id}/edit"
    entityId?: string  // For entity-specific routes
  },
  workEvent: {
    type: "action",
    action: { type: "navigate", ... }
  }
}

// Tool: get_form_schema
// Get the form fields for a create/edit form
{
  name: "get_form_schema",
  description: "Get the schema of a form including required fields, types, and options",
  parameters: {
    module: AgentWorkModule,
    formType: "create" | "edit",
    entityId?: string
  },
  returns: {
    fields: Array<{
      name: string,
      label: string,
      type: "text" | "select" | "multiselect" | "date" | "richtext" | ...,
      required: boolean,
      options?: Array<{ value: string, label: string }>,
      validation?: object
    }>
  }
}

// Tool: fill_form_field
// Fill a single field in a form (enables streaming progress)
{
  name: "fill_form_field",
  description: "Fill a field in the current form",
  parameters: {
    field: string,
    value: unknown,
    displayValue?: string  // Human-readable version for Agent Work pane
  },
  workEvent: {
    type: "action",
    action: { type: "fill_field", status: "filling" → "filled", ... }
  }
}

// Tool: submit_form
// Submit the current form
{
  name: "submit_form",
  description: "Submit the currently open form",
  parameters: {
    validate?: boolean  // Whether to validate before submit
  },
  returns: {
    success: boolean,
    entityId?: string,
    entityUrl?: string,
    errors?: Array<{ field: string, message: string }>
  },
  workEvent: {
    type: "entity_created" | "work_error"
  }
}
```

#### Module-Specific Tools

```typescript
// === BRIEFS MODULE ===

// Tool: create_brief
{
  name: "create_brief",
  description: "Create a new brief in SpokeStack",
  parameters: {
    title: string,
    type: "VIDEO_SHOOT" | "VIDEO_EDIT" | "DESIGN" | ...,
    clientId: string,
    assigneeId?: string,
    description?: string,
    deadline?: string,  // ISO date
    priority?: "LOW" | "MEDIUM" | "HIGH" | "URGENT"
  },
  api: "POST /api/v1/briefs",
  workEvents: [
    { type: "work_start", module: "briefs", route: "/briefs/new" },
    { type: "action", action: { type: "fill_field", field: "title", ... } },
    { type: "action", action: { type: "fill_field", field: "type", ... } },
    // ... one event per field
    { type: "action", action: { type: "submit", ... } },
    { type: "entity_created", entity: { type: "brief", ... } },
    { type: "work_complete" }
  ]
}

// === STUDIO/CALENDAR MODULE ===

// Tool: create_calendar_entries
{
  name: "create_calendar_entries",
  description: "Create content calendar entries in SpokeStack",
  parameters: {
    clientId: string,
    entries: Array<{
      date: string,           // ISO date
      platform: "instagram" | "linkedin" | "facebook" | "tiktok" | "twitter" | "youtube",
      contentType: "POST" | "CAROUSEL" | "REEL" | "STORY" | "ARTICLE" | ...,
      caption: string,
      hashtags?: string[],
      visualConcept?: string,
      status?: "IDEA" | "SCHEDULED" | "APPROVED"
    }>
  },
  api: "POST /api/v1/studio/calendar/entries/bulk",
  workEvents: [
    { type: "work_start", module: "studio/calendar" },
    // One action per entry being created
    { type: "action", action: { type: "create", displayValue: "Feb 3 - Instagram Post", ... } },
    { type: "entity_created", entity: { type: "calendar_entry", ... } },
    // ... repeat for each entry
    { type: "work_complete" }
  ]
}

// === PROJECTS MODULE ===

// Tool: create_project
{
  name: "create_project",
  description: "Create a new project in SpokeStack",
  parameters: {
    name: string,
    clientId: string,
    budget?: number,
    startDate?: string,
    endDate?: string,
    description?: string
  },
  api: "POST /api/v1/projects"
}

// Tool: add_project_milestone
{
  name: "add_project_milestone",
  description: "Add a milestone to an existing project",
  parameters: {
    projectId: string,
    name: string,
    dueDate: string,
    description?: string
  },
  api: "POST /api/v1/projects/{projectId}/milestones"
}

// === CLIENTS MODULE ===

// Tool: get_clients
{
  name: "get_clients",
  description: "Get list of clients for the organization",
  parameters: {
    activeOnly?: boolean
  },
  api: "GET /api/v1/clients"
}

// Tool: get_client_context
{
  name: "get_client_context",
  description: "Get full context for a client including brand guide, recent work, and preferences",
  parameters: {
    clientId: string
  },
  returns: {
    client: Client,
    brandGuide?: KnowledgeDocument,
    recentBriefs: Brief[],
    recentCalendarEntries: CalendarEntry[],
    teamMembers: User[]
  }
}

// === TEAM MODULE ===

// Tool: get_team_members
{
  name: "get_team_members",
  description: "Get team members, optionally filtered by department or skill",
  parameters: {
    department?: string,
    skill?: string,
    availableOnly?: boolean
  },
  api: "GET /api/v1/team"
}

// Tool: assign_to_user
{
  name: "assign_to_user",
  description: "Assign an entity (brief, project, etc.) to a team member",
  parameters: {
    entityType: "brief" | "project" | "task",
    entityId: string,
    userId: string,
    message?: string
  },
  workEvent: {
    type: "action",
    action: { type: "assign", displayValue: "Assigned to Sarah Chen", ... }
  }
}
```

### 11.5 Tool Implementation Pattern

When implementing tools in Agent Builder, emit work events at appropriate points:

```python
# Python example for Agent Builder tool implementation

async def create_brief(params: CreateBriefParams, context: AgentContext) -> CreateBriefResult:
    """Create a brief in SpokeStack, emitting work events for the Agent Work pane."""

    # 1. Emit work_start
    await context.emit_sse({
        "type": "work_start",
        "module": "briefs",
        "route": "/briefs/new",
        "pendingFields": ["title", "type", "client", "description", "deadline", "assignee"]
    })

    # 2. Emit action for each field (with "filling" then "filled" status)
    fields_to_fill = [
        ("title", params.title),
        ("type", params.type),
        ("client", params.client_name),  # Use display value
        ("description", params.description or ""),
        ("deadline", params.deadline.isoformat() if params.deadline else ""),
    ]

    for field_name, value in fields_to_fill:
        if value:
            await context.emit_sse({
                "type": "action",
                "action": {
                    "id": f"act_{uuid4().hex[:8]}",
                    "type": "fill_field",
                    "field": field_name,
                    "fieldLabel": field_name.replace("_", " ").title(),
                    "displayValue": str(value)[:50],  # Truncate for display
                    "status": "filled",
                    "module": "briefs",
                    "route": "/briefs/new"
                }
            })
            await asyncio.sleep(0.1)  # Small delay for visual effect

    # 3. Call SpokeStack API
    try:
        response = await spokestack_client.post(
            "/api/v1/briefs",
            json={
                "title": params.title,
                "type": params.type,
                "clientId": params.client_id,
                "description": params.description,
                "deadline": params.deadline.isoformat() if params.deadline else None,
                "assigneeId": params.assignee_id,
            },
            headers={
                "X-Organization-Id": context.organization_id,
                "Authorization": f"Bearer {context.api_token}"
            }
        )
        brief = response.json()

        # 4. Emit entity_created
        await context.emit_sse({
            "type": "entity_created",
            "entity": {
                "id": brief["id"],
                "type": "brief",
                "title": brief["title"],
                "module": "briefs",
                "url": f"/briefs/{brief['id']}"
            }
        })

        # 5. Emit work_complete
        await context.emit_sse({
            "type": "work_complete",
            "state": {
                "isWorking": False,
                "createdEntities": [{
                    "id": brief["id"],
                    "type": "brief",
                    "title": brief["title"],
                    "module": "briefs",
                    "url": f"/briefs/{brief['id']}"
                }]
            }
        })

        return CreateBriefResult(success=True, brief_id=brief["id"], url=f"/briefs/{brief['id']}")

    except Exception as e:
        # Emit work_error
        await context.emit_sse({
            "type": "work_error",
            "error": str(e)
        })
        return CreateBriefResult(success=False, error=str(e))
```

### 11.6 Required Tools Per Agent Type

Each agent type needs specific tools to operate SpokeStack:

| Agent Type | Required Tools |
|------------|----------------|
| `workflow` (assistant) | get_clients, get_team_members, navigate_to, get_form_schema |
| `content` (content_strategist) | create_calendar_entries, get_client_context, get_clients |
| `brief` (brief_writer) | create_brief, get_clients, get_team_members, get_client_context |
| `presentation` (deck_designer) | create_deck, get_client_context |
| `video_script` (video_director) | create_brief (VIDEO_SHOOT type), get_client_context |
| `copy` (document_writer) | create_brief (COPYWRITING type), get_client_context |
| `campaign_analytics` (analyst) | get_client_analytics, create_report |
| `media_buying` (media_buyer) | get_ad_accounts, create_campaign_plan |
| `training` (course_designer) | create_course, create_module, create_lesson |
| `legal` (contract_analyzer) | get_contracts, create_contract_note |
| `resource` (resource_planner) | get_team_capacity, create_resource_allocation |

### 11.7 Agent Type Mapping

Mission Control uses descriptive agent types while Agent Builder uses canonical names:

```typescript
// Mission Control → Agent Builder mapping
const MC_TO_AGENT_BUILDER_MAP = {
  assistant: "workflow",      // General-purpose routing/coordination
  content_strategist: "content",
  brief_writer: "brief",
  deck_designer: "presentation",
  video_director: "video_script",
  document_writer: "copy",
  analyst: "campaign_analytics",
  media_buyer: "media_buying",
  course_designer: "training",
  contract_analyzer: "legal",
  resource_planner: "resource",
};
```

### 11.8 Vision/Attachment Support

Agents can receive image attachments for vision-capable operations:

```typescript
// Request format with attachments
interface MessageWithAttachments {
  content: string;
  attachments?: Array<{
    type: string;        // "image/jpeg", "image/png", etc.
    name: string;
    size: number;
    data: string;        // Base64-encoded image data
    mediaType: string;   // Same as type, for Claude API compatibility
  }>;
}

// Agent Builder should convert to Claude message format
const message = {
  role: "user",
  content: [
    // Text content
    { type: "text", text: userMessage.content },
    // Image attachments (for vision)
    ...attachments.filter(a => a.type.startsWith("image/")).map(a => ({
      type: "image",
      source: {
        type: "base64",
        media_type: a.mediaType,
        data: a.data
      }
    }))
  ]
};
```

---

## Appendix A: Agent Type Registry

```typescript
const AGENT_TYPES = {
  // Content
  content_strategist: 'Content Strategist',
  copy_writer: 'Copy Writer',
  document_writer: 'Document Writer',

  // Creative
  deck_designer: 'Deck Designer',
  visual_curator: 'Visual Curator',

  // Video
  video_director: 'Video Director',
  script_writer: 'Script Writer',
  storyboard_artist: 'Storyboard Artist',
  production_manager: 'Production Manager',

  // Operations
  brief_writer: 'Brief Writer',
  project_planner: 'Project Planner',
  resource_planner: 'Resource Planner',

  // Analysis
  analytics_interpreter: 'Analytics Interpreter',
  cfo_assistant: 'CFO Assistant',
  listening_analyst: 'Listening Analyst',

  // Sales
  sales_assistant: 'Sales Assistant',
  rfp_manager: 'RFP Manager',
  proposal_writer: 'Proposal Writer',

  // Learning
  course_designer: 'Course Designer',
  quiz_generator: 'Quiz Generator',

  // Support
  ticket_handler: 'Ticket Handler',
  response_writer: 'Response Writer',

  // Platform (Superadmin)
  instance_onboarding: 'Instance Builder',   // Creates new tenant instances
  instance_analytics: 'Instance Analytics',  // Platform health scores
  instance_success: 'Success Manager',       // Churn prediction
};
```

---

## Appendix B: Related Documentation

| Document | Purpose |
|----------|---------|
| `PLATFORM_ORCHESTRATION.md` | How Instance Builder, Mission Control, and CI/CD connect |
| `MISSION_CONTROL_UX.md` | Mission Control interface specification |
| `TWO_PANE_AGENT_UX_SPEC.md` | Core two-pane paradigm |
| `TWO_PANE_MODULE_MAPPING.md` | All 30+ modules mapped |
| `INSTANCE_DEPLOYMENT_GUIDE.md` | Deployment procedures |

---

*This specification should be kept in sync between SpokeStack and the Agent Builder repository.*
