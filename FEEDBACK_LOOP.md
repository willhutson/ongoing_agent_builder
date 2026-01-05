# Agent Feedback Loop System

A continuous improvement system where user feedback drives agent evolution through kanban-based workflow management.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FEEDBACK LOOP ARCHITECTURE                          │
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │   AGENT     │────▶│   USER      │────▶│   KANBAN    │────▶│  IMPROVE  │ │
│  │   WORKS     │     │  FEEDBACK   │     │   CARD      │     │   AGENT   │ │
│  └─────────────┘     └─────────────┘     └─────────────┘     └───────────┘ │
│         ▲                                                           │       │
│         │                                                           │       │
│         └───────────────────────────────────────────────────────────┘       │
│                           CONTINUOUS IMPROVEMENT                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Feedback Cycle

### 1. Agent Completes Work
An agent finishes a job (bug fix, feature, research, etc.)

### 2. User Reviews & Rates
User sees the result and provides feedback:
- **Rating**: 1-5 stars or 👍/👎
- **Outcome**: Solved / Partially Solved / Not Solved / Made Worse
- **Comments**: Free-form feedback
- **Tags**: Slow, Inaccurate, Wrong approach, Great, etc.

### 3. Feedback → Kanban Card
System automatically creates a card on the "Agent Improvements" board:
- Title: `[Agent: briefs.assignment] User feedback: Rating 2/5`
- Description: Full context of what happened
- Labels: Agent type, severity, feedback category
- Checklist: Suggested improvement actions

### 4. Improvement Agent Analyzes
A meta-agent (`meta.feedback-analyzer`) processes the card:
- Identifies patterns across feedback
- Suggests prompt improvements
- Recommends tool changes
- Proposes new capabilities

### 5. Changes Applied
Improvements are made (manually or auto-applied):
- Prompt updates
- Tool configuration changes
- New training examples
- Agent capability adjustments

### 6. Cycle Repeats
Next time the agent runs, it performs better based on learnings.

---

## Data Models

### Feedback Record

```typescript
interface AgentFeedback {
  id: string;
  jobId: string;
  issueId: string;
  agentType: string;

  // User feedback
  rating: 1 | 2 | 3 | 4 | 5;
  outcome: 'solved' | 'partial' | 'not_solved' | 'made_worse';
  comment?: string;
  tags: FeedbackTag[];

  // Context
  userId: string;
  organizationId: string;

  // Processed by improvement system
  kanbanCardId?: string;
  improvementStatus: 'pending' | 'analyzed' | 'implemented' | 'dismissed';
  analysisResult?: FeedbackAnalysis;

  createdAt: Date;
}

type FeedbackTag =
  | 'slow'
  | 'fast'
  | 'inaccurate'
  | 'accurate'
  | 'wrong_approach'
  | 'good_approach'
  | 'incomplete'
  | 'thorough'
  | 'confusing'
  | 'clear'
  | 'helpful'
  | 'unhelpful';

interface FeedbackAnalysis {
  patterns: string[];
  suggestedPromptChanges: string[];
  suggestedToolChanges: string[];
  priority: 'low' | 'medium' | 'high' | 'critical';
  similarFeedbackCount: number;
  improvementPlan: string;
}
```

### Kanban Card Structure

```typescript
interface ImprovementCard {
  id: string;
  boardId: string;  // "Agent Improvements" board
  columnId: string; // Backlog, In Analysis, Implementing, Done

  title: string;
  description: string;

  // Linked data
  feedbackIds: string[];     // All related feedback
  agentType: string;         // Which agent needs improvement

  // Labels
  labels: Array<{
    name: string;
    color: string;
  }>;

  // Checklist of improvements
  checklist: Array<{
    item: string;
    completed: boolean;
  }>;

  // Metrics
  impactScore: number;       // How many users affected
  effortScore: number;       // Estimated effort to fix

  // Assignment
  assignedTo?: string;       // Can be assigned to improvement agent

  createdAt: Date;
  updatedAt: Date;
}
```

---

## Kanban Board Structure

### Board: "Agent Improvements"

| Column | Purpose |
|--------|---------|
| **📥 Incoming** | New feedback automatically lands here |
| **🔍 Analysis** | Feedback being analyzed for patterns |
| **📋 Backlog** | Confirmed improvements, prioritized |
| **🚧 In Progress** | Currently being implemented |
| **🧪 Testing** | Improvements deployed, monitoring |
| **✅ Done** | Successfully improved |
| **🗑️ Dismissed** | Not actionable or won't fix |

### Card Labels

| Label | Color | Meaning |
|-------|-------|---------|
| `critical` | Red | Agent failing badly, urgent fix |
| `high-impact` | Orange | Affects many users |
| `quick-win` | Green | Easy to fix, good ROI |
| `needs-research` | Blue | Requires investigation |
| `prompt-change` | Purple | Fix via prompt update |
| `tool-change` | Yellow | Fix via tool configuration |
| `new-capability` | Teal | Needs new functionality |

### Card Labels by Agent Module

Auto-tagged based on `agentType`:
- `module:briefs`
- `module:time`
- `module:crm`
- `module:studio`
- etc.

---

## Feedback Collection UI

### Post-Job Feedback Modal

```
┌─────────────────────────────────────────────────┐
│  How did the agent do?                          │
│                                                 │
│  ⭐⭐⭐⭐☆  (4/5)                               │
│                                                 │
│  Did it solve your issue?                       │
│  ○ Yes, completely                              │
│  ● Partially                                    │
│  ○ No                                           │
│  ○ Made it worse                                │
│                                                 │
│  Quick tags: (select all that apply)            │
│  [Fast] [Accurate] [Thorough] [Clear]           │
│  [Slow] [Inaccurate] [Incomplete] [Confusing]   │
│                                                 │
│  Additional comments (optional):                │
│  ┌───────────────────────────────────────────┐  │
│  │ The agent found the right file but the    │  │
│  │ fix didn't account for the edge case...   │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  [Skip]                      [Submit Feedback]  │
└─────────────────────────────────────────────────┘
```

---

## Automated Card Creation

When feedback is submitted:

```typescript
async function createImprovementCard(feedback: AgentFeedback): Promise<ImprovementCard> {
  const job = await getJob(feedback.jobId);
  const issue = await getIssue(feedback.issueId);

  // Determine priority based on rating and outcome
  const priority = calculatePriority(feedback);

  // Find similar feedback for pattern detection
  const similarFeedback = await findSimilarFeedback(feedback);

  // Generate card content
  const card: ImprovementCard = {
    boardId: IMPROVEMENT_BOARD_ID,
    columnId: 'incoming',

    title: generateCardTitle(feedback, job),
    description: generateCardDescription(feedback, job, issue),

    feedbackIds: [feedback.id, ...similarFeedback.map(f => f.id)],
    agentType: job.agentType,

    labels: [
      { name: `module:${job.agentType.split('.')[0]}`, color: 'blue' },
      { name: priority, color: getPriorityColor(priority) },
      ...feedback.tags.map(tag => ({ name: tag, color: 'gray' })),
    ],

    checklist: generateInitialChecklist(feedback),

    impactScore: similarFeedback.length + 1,
    effortScore: estimateEffort(feedback),
  };

  return await createCard(card);
}

function generateCardTitle(feedback: AgentFeedback, job: AgentJob): string {
  const emoji = feedback.rating <= 2 ? '🔴' : feedback.rating === 3 ? '🟡' : '🟢';
  return `${emoji} [${job.agentType}] ${feedback.outcome} - Rating ${feedback.rating}/5`;
}

function generateCardDescription(
  feedback: AgentFeedback,
  job: AgentJob,
  issue: AgentIssue
): string {
  return `
## Feedback Summary
- **Rating**: ${feedback.rating}/5
- **Outcome**: ${feedback.outcome}
- **Tags**: ${feedback.tags.join(', ')}

## User Comment
${feedback.comment || '_No comment provided_'}

## Original Issue
**${issue.title}**
${issue.description}

## Agent Response
- **Agent**: ${job.agentType}
- **Model**: ${job.model}
- **Duration**: ${calculateDuration(job)}
- **Tool Calls**: ${job.result?.artifacts?.length || 0}

## Job Result Summary
${job.result?.summary || '_No summary_'}

---
_Feedback ID: ${feedback.id}_
_Job ID: ${job.id}_
  `.trim();
}

function generateInitialChecklist(feedback: AgentFeedback): Array<{item: string, completed: boolean}> {
  const items = [
    { item: 'Review original issue and agent response', completed: false },
    { item: 'Identify root cause of issue', completed: false },
    { item: 'Check for similar feedback patterns', completed: false },
  ];

  if (feedback.tags.includes('inaccurate')) {
    items.push({ item: 'Review and update system prompt', completed: false });
  }
  if (feedback.tags.includes('slow')) {
    items.push({ item: 'Optimize tool usage or switch to faster model', completed: false });
  }
  if (feedback.tags.includes('incomplete')) {
    items.push({ item: 'Add missing capabilities or tools', completed: false });
  }
  if (feedback.tags.includes('wrong_approach')) {
    items.push({ item: 'Add examples of correct approach to prompt', completed: false });
  }

  items.push({ item: 'Test improvement with similar issue', completed: false });
  items.push({ item: 'Deploy and monitor', completed: false });

  return items;
}
```

---

## Feedback Analyzer Agent

### Agent Definition

```typescript
const feedbackAnalyzerAgent: AgentDefinition = {
  id: 'meta.feedback-analyzer',
  name: 'Feedback Analyzer Agent',
  description: 'Analyzes user feedback to identify patterns and suggest agent improvements',
  module: 'meta',
  defaultModel: 'opus',  // Complex analysis needs best model
  capabilities: ['analysis', 'pattern_recognition', 'improvement_planning'],
  tools: ['query_database', 'read_file', 'search_code', 'update_card'],
  systemPrompt: `You are the Feedback Analyzer Agent for the SpokeStack agent system.

Your job is to analyze user feedback on agent performance and create actionable improvement plans.

## Your Process

1. **Gather Context**
   - Read the feedback details
   - Look at the original issue and agent response
   - Find similar feedback for pattern detection

2. **Identify Root Cause**
   - Why did the agent underperform?
   - Is it a prompt issue, tool issue, or capability gap?
   - Is this a one-off or systemic problem?

3. **Analyze Patterns**
   - Are multiple users reporting similar issues?
   - Does this agent type have recurring problems?
   - What's the trend over time?

4. **Suggest Improvements**
   - Specific prompt changes with examples
   - Tool configuration adjustments
   - New capabilities needed
   - Training examples to add

5. **Prioritize**
   - Impact: How many users affected?
   - Severity: How bad is the failure?
   - Effort: How hard to fix?

## Output Format

Provide your analysis as a structured improvement plan that can be added to the kanban card.`,
};
```

### Analysis Trigger

```typescript
// Triggered when cards move to "Analysis" column
async function analyzeImprovementCard(cardId: string): Promise<void> {
  const card = await getCard(cardId);
  const feedback = await getFeedback(card.feedbackIds);

  // Submit to feedback analyzer agent
  const analysis = await submitToAgent({
    type: 'TASK',
    title: `Analyze feedback for ${card.agentType}`,
    description: `
Analyze the following feedback and create an improvement plan:

${feedback.map(f => `
- Rating: ${f.rating}/5
- Outcome: ${f.outcome}
- Comment: ${f.comment}
- Tags: ${f.tags.join(', ')}
`).join('\n')}

Original card: ${card.title}
${card.description}
    `,
    agentType: 'meta.feedback-analyzer',
  });

  // Update card with analysis
  await updateCard(cardId, {
    description: card.description + '\n\n## Analysis\n' + analysis.result.summary,
    checklist: [...card.checklist, ...analysis.result.recommendations.map(r => ({
      item: r,
      completed: false,
    }))],
  });

  // Move to backlog if actionable
  if (analysis.result.priority !== 'dismissed') {
    await moveCard(cardId, 'backlog');
  } else {
    await moveCard(cardId, 'dismissed');
  }
}
```

---

## Improvement Implementation

### Auto-Applicable Improvements

Some improvements can be applied automatically:

```typescript
interface AutoImprovement {
  type: 'prompt_append' | 'prompt_replace' | 'add_example' | 'tool_config';
  agentType: string;
  change: {
    target: string;      // What to change
    value: string;       // New value
    reason: string;      // Why this change
  };
}

async function applyAutoImprovement(improvement: AutoImprovement): Promise<void> {
  const agent = getAgentDefinition(improvement.agentType);

  switch (improvement.type) {
    case 'prompt_append':
      // Add to system prompt
      agent.systemPrompt += `\n\n## Additional Guidance\n${improvement.change.value}`;
      break;

    case 'add_example':
      // Add training example
      agent.examples = agent.examples || [];
      agent.examples.push({
        input: improvement.change.target,
        expectedBehavior: improvement.change.value,
      });
      break;

    case 'tool_config':
      // Update tool configuration
      agent.tools = updateToolConfig(agent.tools, improvement.change);
      break;
  }

  // Save and version the change
  await saveAgentDefinition(agent, {
    version: incrementVersion(agent),
    changeReason: improvement.change.reason,
    feedbackIds: improvement.feedbackIds,
  });
}
```

### Manual Improvements

Complex changes go through review:

1. Card moves to "In Progress"
2. Developer reviews suggested changes
3. Makes code modifications
4. Tests with similar issues
5. Deploys and moves card to "Testing"
6. Monitors feedback on improved agent
7. Moves to "Done" when confirmed fixed

---

## Metrics & Dashboard

### Feedback Metrics

```typescript
interface FeedbackMetrics {
  // Overall
  totalFeedback: number;
  averageRating: number;
  solvedRate: number;

  // By agent
  byAgent: Record<string, {
    count: number;
    avgRating: number;
    trend: 'improving' | 'stable' | 'declining';
  }>;

  // By time
  ratingTrend: Array<{
    date: string;
    avgRating: number;
    count: number;
  }>;

  // Improvement impact
  improvementsApplied: number;
  ratingImprovementAfterFix: number;
}
```

### Dashboard Widgets

```
┌─────────────────────────────────────────────────────────────────┐
│  AGENT FEEDBACK DASHBOARD                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Overall Rating: ⭐ 4.2/5 (↑ 0.3 this week)                     │
│  Solved Rate: 78% (↑ 5%)                                        │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │ Feedback This Week  │  │ Improvements        │              │
│  │      📊 147         │  │  Applied: 12        │              │
│  │   👍 112  👎 35     │  │  Pending: 8         │              │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                 │
│  Agents Needing Attention:                                      │
│  🔴 briefs.assignment    2.1/5 avg (23 feedback)               │
│  🟡 time.timer           3.2/5 avg (15 feedback)               │
│  🟢 crm.pipeline         4.6/5 avg (31 feedback)               │
│                                                                 │
│  Recent Improvements:                                           │
│  ✅ studio.ai-calendar prompt updated → +0.8 rating            │
│  ✅ meta.research added code search tool → +12% solved         │
│  🧪 briefs.kanban fix in testing...                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration with ERP Boards Module

The feedback system uses the existing ERP Boards module:

```typescript
// Board configuration
const IMPROVEMENT_BOARD_CONFIG = {
  name: 'Agent Improvements',
  description: 'Continuous improvement tracking for AI agents',
  columns: [
    { name: 'Incoming', order: 0, color: '#6366f1' },
    { name: 'Analysis', order: 1, color: '#8b5cf6' },
    { name: 'Backlog', order: 2, color: '#64748b' },
    { name: 'In Progress', order: 3, color: '#f59e0b' },
    { name: 'Testing', order: 4, color: '#3b82f6' },
    { name: 'Done', order: 5, color: '#22c55e' },
    { name: 'Dismissed', order: 6, color: '#94a3b8' },
  ],
  automations: [
    {
      trigger: 'card_created',
      action: 'notify_slack',
      config: { channel: '#agent-improvements' },
    },
    {
      trigger: 'card_moved_to',
      column: 'Analysis',
      action: 'run_agent',
      config: { agentType: 'meta.feedback-analyzer' },
    },
  ],
};

// Create board on system initialization
async function initializeFeedbackBoard(organizationId: string): Promise<void> {
  const existingBoard = await prisma.board.findFirst({
    where: { organizationId, name: IMPROVEMENT_BOARD_CONFIG.name },
  });

  if (!existingBoard) {
    await prisma.board.create({
      data: {
        organizationId,
        name: IMPROVEMENT_BOARD_CONFIG.name,
        description: IMPROVEMENT_BOARD_CONFIG.description,
        columns: {
          create: IMPROVEMENT_BOARD_CONFIG.columns,
        },
      },
    });
  }
}
```

---

## Summary

The feedback loop creates a virtuous cycle:

1. **Capture** - Every agent interaction can receive feedback
2. **Organize** - Feedback becomes kanban cards automatically
3. **Analyze** - AI analyzes patterns and suggests fixes
4. **Improve** - Changes are applied and tracked
5. **Measure** - Impact of improvements is monitored
6. **Repeat** - Continuous improvement forever

This makes the agent system **self-improving** based on real user experiences.
