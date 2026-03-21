# Agent Builder: Mission Control Routing Companion Spec

**Version:** 1.0
**Companion to:** ERP Mission Control Routing Architecture v1.1
**Scope:** Agent Builder endpoints, artifact protocol enforcement, and format-aware creation for the Mission Control routing contract.

> This document covers the Agent Builder's responsibilities in the two-MC routing system. The ERP owns persistence, UI, and format detection; the Agent Builder owns execution, artifact streaming, and orchestration.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Endpoint: POST /api/v1/handoff](#endpoint-post-apiv1handoff)
- [Endpoint: POST /api/v1/orchestrate](#endpoint-post-apiv1orchestrate)
- [Endpoint: POST /api/v1/orchestrate/{execution_id}/resume](#endpoint-post-apiv1orchestrateexecution_idresume)
- [Artifact Protocol Enforcement](#artifact-protocol-enforcement)
- [Format-Aware Creation Loop](#format-aware-creation-loop)
- [Billing Usage Reporting](#billing-usage-reporting)
- [SSE Event Catalog](#sse-event-catalog)
- [Implementation Sequence](#implementation-sequence)

---

## Architecture Overview

```
ERP (Mission Control)                  Agent Builder
┌────────────────────────┐            ┌────────────────────────┐
│  General MC / Module MC│            │  3 New Endpoints       │
│  Router + Format Detect│──REST────> │    /handoff            │
│  Canvas Persistence    │            │    /orchestrate        │
│  Artifact Cards        │<──SSE───── │    /orchestrate/resume │
│  Approval UI           │            │                        │
│                        │            │  Existing Endpoints    │
│                        │──REST────> │    /agent/execute      │
│                        │<──SSE───── │    /agent/status       │
└────────────────────────┘            │                        │
                                      │  Agent Execution       │
                                      │  - 45 agents + base    │
                                      │  - emit_artifact tool  │
                                      │  - Orchestrator engine │
                                      └────────────────────────┘
```

**Design principles:**
- ERP owns persistence and UI; Agent Builder owns execution
- REST inbound (ERP → Agent Builder), SSE outbound (Agent Builder → ERP)
- Backward compatibility: `/api/v1/agent/execute` continues unchanged
- Module-scoped agent validation via `module_registry.py`

---

## Endpoint: POST /api/v1/handoff

Accepts cross-agent handoff requests from the ERP router when one agent needs to spawn another with context.

### Request Model

Uses the existing `HandoffRequest` from `src/protocols/handoffs.py`:

```python
class HandoffRequest(BaseModel):
    from_chat_id: str
    from_agent_type: str
    to_agent_type: str                  # Must exist in AgentType enum
    context: HandoffContext
    requires_user_approval: bool = True
    auto_start: bool = False

class HandoffContext(BaseModel):
    parent_chat_id: str
    parent_agent_type: str
    parent_summary: str
    artifacts: list[dict] = []          # Cross-agent artifact references
    relevant_messages: list[dict] = []
    task: str
    constraints: Optional[list[str]] = None
    artifact_format: Optional[str] = None   # NEW — format passthrough
```

### Request Example

```json
{
  "from_chat_id": "chat-abc-123",
  "from_agent_type": "brief",
  "to_agent_type": "content",
  "context": {
    "parent_chat_id": "chat-abc-123",
    "parent_agent_type": "brief",
    "parent_summary": "Created Q3 campaign brief for Acme Corp",
    "artifacts": [
      {"id": "art-001", "type": "brief", "title": "Q3 Campaign Brief"}
    ],
    "task": "Create a content calendar based on the approved brief",
    "artifact_format": "calendar"
  },
  "requires_user_approval": false,
  "auto_start": true
}
```

### Processing Logic

1. **Validate target agent** — confirm `to_agent_type` exists in `AgentType` enum (from `src/api/routes.py`)
2. **Module-scope check** — if the request carries module context, call `is_agent_allowed_for_module(to_agent_type, subdomain)` from `src/services/module_registry.py`; reject with 403 if the agent isn't available in that module
3. **Build AgentContext** — map `HandoffContext` fields:
   - `context.task` → `AgentContext.task`
   - `context.artifacts` → `AgentContext.metadata["parent_artifacts"]`
   - `context.parent_summary` → `AgentContext.metadata["parent_summary"]`
   - `context.artifact_format` → `AgentContext.artifact_format` (new field)
   - Generate new `chat_id` for the child session
4. **Auto-start path** (`auto_start=True` and `requires_user_approval=False`):
   - Invoke agent via existing streaming path (same as `/api/v1/agent/execute` with `stream=True`)
   - Return `StreamingResponse` with SSE events
5. **Approval-required path**:
   - Return `HandoffResponse` with `approved=False` and the `new_chat_id` for the ERP to present approval UI

### Response Model

Uses the existing `HandoffResponse` from `src/protocols/handoffs.py`:

```python
class HandoffResponse(BaseModel):
    approved: bool
    new_chat_id: Optional[str] = None
    new_agent_type: Optional[str] = None
    message: str = ""
```

### Response Example (approval required)

```json
{
  "approved": false,
  "new_chat_id": "chat-def-456",
  "new_agent_type": "content",
  "message": "Handoff to content agent queued pending user approval"
}
```

### Error Responses

| Status | Condition |
|--------|-----------|
| 400 | `to_agent_type` not in `AgentType` enum |
| 403 | Agent not allowed for the module subdomain |
| 422 | Invalid `HandoffContext` (missing required fields) |

---

## Endpoint: POST /api/v1/orchestrate

Bridges the ERP Canvas persistence layer to the Agent Builder's `AgentOrchestrator`. Enables multi-agent workflow execution triggered from the Canvas UI.

### Request Model

New `OrchestrateRequest`:

```python
class OrchestrateRequest(BaseModel):
    workflow_id: Optional[str] = None       # Template name from WorkflowTemplates
    workflow: Optional[dict] = None         # Inline workflow definition (from Canvas)
    context: dict = Field(default_factory=dict)  # Initial workflow context
    organization_id: str
    user_id: str
    stream: bool = True
```

One of `workflow_id` or `workflow` must be provided. If both are set, `workflow` takes precedence (custom Canvas-created workflow).

### Request Example (template)

```json
{
  "workflow_id": "content_approval",
  "context": {
    "content_id": "doc-789",
    "client_id": "acme-corp",
    "content_type": "social_post"
  },
  "organization_id": "org-123",
  "user_id": "user-456",
  "stream": true
}
```

### Request Example (inline workflow)

```json
{
  "workflow": {
    "id": "custom-canvas-wf-001",
    "name": "Client Report Pipeline",
    "description": "Generate competitive analysis then monthly report",
    "steps": [
      {
        "id": "step-1",
        "name": "Competitive Analysis",
        "agent": "competitor_agent",
        "tool": "run_competitive_analysis",
        "input_mapping": {"competitors": "$context.competitors"},
        "output_key": "competitor_results",
        "next_steps": ["step-2"]
      },
      {
        "id": "step-2",
        "name": "Monthly Report",
        "agent": "report_agent",
        "tool": "generate_monthly_report",
        "input_mapping": {
          "competitor_data": "$competitor_results",
          "client_id": "$context.client_id"
        },
        "output_key": "report_result"
      }
    ],
    "trigger": {"type": "manual"}
  },
  "context": {
    "client_id": "acme-corp",
    "competitors": ["competitor-a", "competitor-b"]
  },
  "organization_id": "org-123",
  "user_id": "user-456"
}
```

### Processing Logic

1. **Resolve workflow** — if `workflow_id` is set, look up via `WorkflowTemplates.get_all_templates()[workflow_id]`; if inline `workflow` is set, deserialize into a `Workflow` instance
2. **Validate** — call `workflow.validate()` (returns `(bool, list[str])`); reject with 422 if invalid
3. **Instantiate orchestrator** — create `AgentOrchestrator` with `agent_factory` wrapping the existing `get_agent()` function from `src/api/routes.py`
4. **Wire notifications** — set `notification_callback` on the orchestrator to emit workflow SSE events
5. **Execute** — call `orchestrator.run_workflow(workflow, context, initiated_by=user_id, organization_id=organization_id)`
6. **Stream or return**:
   - Streaming: return `StreamingResponse` with workflow SSE events (see [SSE Event Catalog](#sse-event-catalog))
   - Non-streaming: return `WorkflowExecution` snapshot with `execution_id`

### Response Example (non-streaming)

```json
{
  "execution_id": "exec-abc-123",
  "workflow_id": "content_approval",
  "status": "running",
  "current_steps": ["step-1"],
  "initiated_by": "user-456",
  "organization_id": "org-123"
}
```

### Available Templates

Resolved from `WorkflowTemplates.get_all_templates()`:

| Template ID | Description |
|-------------|-------------|
| `campaign_launch_checklist` | Pre-launch verification: page, audit, accessibility, SEO, UTM, GDPR, review |
| `competitive_analysis` | Multi-competitor analysis pipeline |
| `client_monthly_report` | Monthly reporting with data aggregation |
| `content_approval` | Content review and approval flow |
| `ab_test_analysis` | A/B test setup and results analysis |
| `new_client_onboarding` | Client onboarding checklist |
| `gdpr_compliance_audit` | GDPR compliance verification |
| `social_content_verification` | Social media content pre-publish checks |

---

## Endpoint: POST /api/v1/orchestrate/{execution_id}/resume

Resumes a paused workflow after human review (e.g., the `HUMAN_REVIEW` step type in workflow definitions).

### Request Model

New `ResumeRequest`:

```python
class ResumeRequest(BaseModel):
    approval: bool
    review_notes: str = ""
    reviewer_id: str
```

### Request Example

```json
{
  "approval": true,
  "review_notes": "All assets verified, approved for launch",
  "reviewer_id": "user-789"
}
```

### Processing Logic

1. Look up `WorkflowExecution` by `execution_id`
2. Validate status is `PAUSED` (reject with 409 otherwise)
3. Call `orchestrator.resume_workflow(execution_id, approval, review_notes)`
4. If approved: set status to `RUNNING`, find the paused review step's `next_steps`, and execute them
5. If rejected: set status to `CANCELLED`
6. Return updated `WorkflowExecution` snapshot

### Known Gap

The current `resume_workflow()` implementation (orchestrator.py:356-389) sets the status back to `RUNNING` but does **not** re-execute remaining steps. The enhancement needed:

```python
if approval:
    execution.status = WorkflowStatus.RUNNING
    # Retrieve the workflow definition (must be stored on the execution)
    workflow = self._workflows.get(execution.workflow_id)
    review_step = workflow.get_step(execution.pending_review)
    if review_step and review_step.next_steps:
        remaining = [workflow.get_step(sid) for sid in review_step.next_steps]
        await self._execute_steps(execution, remaining, execution.context)
    execution.pending_review = None
```

### Response Example

```json
{
  "execution_id": "exec-abc-123",
  "workflow_id": "campaign_launch_checklist",
  "status": "running",
  "completed_steps": ["verify_landing", "run_audit", "run_a11y", "check_seo", "check_utms", "check_gdpr", "human_review"],
  "current_steps": ["capture_proof"],
  "review_notes": "All assets verified, approved for launch"
}
```

### Error Responses

| Status | Condition |
|--------|-----------|
| 404 | `execution_id` not found |
| 409 | Execution is not in `PAUSED` status |

---

## Artifact Protocol Enforcement

### The Problem

`BaseAgent` has `_emit_artifact_create`, `_emit_artifact_update`, and `_emit_artifact_complete` helpers (base.py:333-362) but no concrete agent calls them. Agents produce unstructured text output — even when they generate structured data internally, they serialize it as inline text. The ERP Mission Control needs structured `artifact:create`/`artifact:complete` SSE events to render artifact cards in the Canvas.

### Solution: Universal `emit_artifact` Tool

Instead of modifying all 45+ concrete agents, add a universal `emit_artifact` tool to `BaseAgent` that the LLM uses when instructed by the system prompt.

#### Tool Definition

Added to `BaseAgent._define_tools()` (or equivalent tool list):

```python
{
    "type": "function",
    "function": {
        "name": "emit_artifact",
        "description": "Emit a structured artifact for display in Mission Control. Use this instead of including full artifact content as inline text.",
        "parameters": {
            "type": "object",
            "properties": {
                "artifact_type": {
                    "type": "string",
                    "enum": ["calendar", "brief", "document", "deck", "moodboard",
                             "script", "storyboard", "shot_list", "report", "table",
                             "chart", "contract", "survey", "course", "workflow"],
                    "description": "Type of artifact being created"
                },
                "title": {
                    "type": "string",
                    "description": "Human-readable title for the artifact"
                },
                "data": {
                    "type": "object",
                    "description": "Structured artifact data matching the schema for this type"
                },
                "preview_type": {
                    "type": "string",
                    "enum": ["html", "markdown", "json"],
                    "description": "Format of the preview content"
                },
                "preview_content": {
                    "type": "string",
                    "description": "Short preview/summary for UI card display"
                }
            },
            "required": ["artifact_type", "title", "data"]
        }
    }
}
```

#### Tool Dispatch

In `BaseAgent.run()` and `BaseAgent.stream()`, intercept `emit_artifact` tool calls:

```python
if tool_name == "emit_artifact":
    artifact = Artifact(
        id=str(uuid4()),
        type=ArtifactType(tool_input["artifact_type"]),
        title=tool_input["title"],
        data=tool_input["data"],
        status="final",
        preview=ArtifactPreview(
            type=tool_input.get("preview_type", "markdown"),
            content=tool_input.get("preview_content", ""),
        ) if tool_input.get("preview_content") else None,
        client_id=context.client_id,
        project_id=context.project_id,
    )
    await self._emit_artifact_create(context, artifact)
    await self._emit_artifact_complete(context, artifact)
    return {"status": "artifact_emitted", "artifact_id": artifact.id}
```

#### System Prompt Injection

Appended to `_build_system_prompt()` (base.py:582):

```
## Artifact Output Protocol
When you produce a deliverable (brief, calendar, deck, report, table, chart,
contract, document, etc.), you MUST emit it as a structured artifact using the
`emit_artifact` tool rather than including the full content as inline text.

Steps:
1. Call emit_artifact with the artifact_type, title, and structured data
2. Continue with a brief text summary in your response
3. Do NOT dump the full artifact content as text

Available artifact types: calendar, brief, document, deck, moodboard, script,
storyboard, shot_list, report, table, chart, contract, survey, course, workflow
```

### Artifact Data Schemas

Added to `src/protocols/artifacts.py` as `ARTIFACT_DATA_SCHEMAS`. Each entry maps an `ArtifactType` to the expected JSON schema for the `data` field of the `Artifact` model.

| ArtifactType | Required Fields | Key Data Fields |
|-------------|----------------|-----------------|
| `BRIEF` | `client_name`, `project_name`, `objectives` | `deliverables`, `timeline`, `budget_indication`, `complexity`, `gaps` |
| `CALENDAR` | `entries` | `entries[].date`, `entries[].title`, `entries[].description`, `entries[].assignee`, `date_range` |
| `DECK` | `title`, `slides` | `slides[].title`, `slides[].content`, `slides[].notes`, `slides[].layout` |
| `REPORT` | `title`, `sections` | `sections[].heading`, `sections[].content`, `sections[].data`, `executive_summary`, `recommendations` |
| `DOCUMENT` | `title`, `body` | `body` (markdown), `metadata` |
| `TABLE` | `columns`, `rows` | `columns[].name`, `columns[].type`, `rows[][]`, `summary` |
| `CHART` | `chart_type`, `data` | `chart_type` (bar/line/pie/etc.), `data.labels`, `data.datasets`, `options` |
| `CONTRACT` | `title`, `parties`, `clauses` | `clauses[].title`, `clauses[].content`, `effective_date`, `terms` |
| `SCRIPT` | `title`, `scenes` | `scenes[].number`, `scenes[].heading`, `scenes[].action`, `scenes[].dialogue` |
| `STORYBOARD` | `title`, `frames` | `frames[].number`, `frames[].description`, `frames[].camera`, `frames[].audio` |
| `SHOT_LIST` | `title`, `shots` | `shots[].number`, `shots[].type`, `shots[].description`, `shots[].equipment` |
| `MOODBOARD` | `title`, `elements` | `elements[].type` (image/color/texture/typography), `elements[].description`, `theme` |
| `SURVEY` | `title`, `questions` | `questions[].type` (multiple_choice/scale/open), `questions[].text`, `questions[].options` |
| `COURSE` | `title`, `modules` | `modules[].title`, `modules[].lessons`, `modules[].duration`, `objectives` |
| `WORKFLOW` | `title`, `steps` | `steps[].name`, `steps[].agent`, `steps[].description`, `steps[].dependencies` |

---

## Format-Aware Creation Loop

When the ERP router detects that a user's request should produce a specific format (calendar vs deck vs report), it passes the format to the Agent Builder so the same underlying agent can shape its output accordingly.

### New Field on AgentContext

```python
@dataclass
class AgentContext:
    # ... existing fields ...

    # Format-aware creation (Mission Control routing)
    artifact_format: Optional[str] = None  # e.g., "calendar", "deck", "brief"
```

Valid values correspond to `ArtifactType` enum values: `calendar`, `brief`, `document`, `deck`, `moodboard`, `script`, `storyboard`, `shot_list`, `report`, `table`, `chart`, `contract`, `survey`, `course`, `workflow`.

### System Prompt Addition

When `context.artifact_format` is set, `_build_system_prompt()` appends:

```
## Output Format
The user's request should be delivered as a {artifact_format} artifact.
Expected data structure:
{JSON schema from ARTIFACT_DATA_SCHEMAS[artifact_format]}

Emit the result using the emit_artifact tool with type="{artifact_format}".
```

This instructs the LLM to shape its output into the specified format. For example, the same content agent asked to produce a "calendar" will structure its output as date-keyed entries, while "deck" will produce slides.

### Format Passthrough in Endpoints

| Endpoint | How format is passed |
|----------|---------------------|
| `POST /api/v1/agent/execute` | New optional `artifact_format` field on `ExecuteRequest` |
| `POST /api/v1/handoff` | `HandoffContext.artifact_format` (new optional field) |
| `POST /api/v1/orchestrate` | Per-step `output_artifact_format` in `WorkflowStep.input_mapping` |

### Execute Request Extension

```python
class ExecuteRequest(BaseModel):
    # ... existing fields ...
    artifact_format: Optional[str] = Field(
        default=None,
        description="Desired output format: calendar, deck, brief, report, etc."
    )
```

---

## Billing Usage Reporting

### Background

The existing `ERPCallbackService` (erp_integration.py:234-308) piggybacks token usage onto the per-request `callback_url` via HMAC-signed PATCH. This works for `/api/v1/agent/execute` but doesn't generalize — the new endpoints (`/handoff`, `/orchestrate`) don't always have a callback URL, and the callback payload lacks model/agent/module context needed for granular billing.

Billing is unified: **all endpoints** report usage to the new dedicated billing endpoint. The existing HMAC callback remains for completion notification but is no longer the source of truth for billing.

### ERP Billing Endpoint Contract

```
POST {erp_api_base_url}/api/v1/billing/usage/report
Headers:
  X-Service-Key: <AGENT_BUILDER_SERVICE_KEY>
  Content-Type: application/json
```

### Request Body

```json
{
  "organizationId": "org-123",
  "tokenInput": 1234,
  "tokenOutput": 5678,
  "model": "claude-sonnet-4-20250514",
  "agentType": "content",
  "module": "studio"
}
```

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `organizationId` | string | `AgentContext.organization_id` or `ExecuteRequest.tenant_id` | Tenant for billing |
| `tokenInput` | int | `BaseAgent._input_tokens` (accumulated at base.py:109, 406-410) | Prompt tokens consumed |
| `tokenOutput` | int | `BaseAgent._output_tokens` (accumulated at base.py:110, 406-410) | Completion tokens consumed |
| `model` | string | `get_model_for_agent()` from `src/services/model_registry.py` | Model ID used for execution |
| `agentType` | string | `AgentType` enum value (e.g., `"content"`, `"brief"`) | Which agent ran |
| `module` | string | `AgentContext.module_subdomain` (e.g., `"studio"`, `"briefs"`) | Module context; `null` if general MC |

### Auth: X-Service-Key

Unlike the existing HMAC callback (which signs each payload with `erp_callback_secret`), the billing endpoint uses a static service key:

- New config field: `erp_service_key: str` in `Settings` (config.py)
- Sent as `X-Service-Key` header on every billing POST
- The ERP validates this key against the Agent Builder's registered service identity

### Implementation: UsageReportService

New class in `src/api/erp_integration.py`, alongside the existing `ERPCallbackService`:

```python
class UsageReportService:
    """Reports token usage to the ERP billing endpoint."""

    def __init__(self, service_key: str = None, base_url: str = None):
        settings = get_settings()
        self.service_key = service_key or settings.erp_service_key
        self.base_url = base_url or settings.erp_api_base_url
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def report_usage(
        self,
        organization_id: str,
        token_input: int,
        token_output: int,
        model: str,
        agent_type: str,
        module: Optional[str] = None,
        max_retries: int = 3,
    ) -> bool:
        """Report usage to ERP billing. Fire-and-forget with retry."""
        payload = {
            "organizationId": organization_id,
            "tokenInput": token_input,
            "tokenOutput": token_output,
            "model": model,
            "agentType": agent_type,
            "module": module,
        }

        headers = {
            "X-Service-Key": self.service_key,
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/api/v1/billing/usage/report"

        for attempt in range(max_retries + 1):
            try:
                response = await self.http_client.post(
                    url, json=payload, headers=headers,
                )
                if response.status_code in (200, 201, 204):
                    return True
                if 400 <= response.status_code < 500:
                    logger.error(f"Billing rejected: {response.status_code}")
                    return False
            except Exception as e:
                logger.warning(f"Billing attempt {attempt + 1} error: {e}")

            if attempt < max_retries:
                await asyncio.sleep(2 ** (attempt + 1))

        return False
```

### Integration Points

| Endpoint | When | What |
|----------|------|------|
| `POST /api/v1/agent/execute` | After agent completes (in background task) | Single report with agent's accumulated tokens |
| `POST /api/v1/handoff` | After child agent completes | Report with `agentType=to_agent_type`, module from handoff context |
| `POST /api/v1/orchestrate` | After each workflow step completes | Per-step report; each step may use a different agent/model |
| `POST /api/v1/orchestrate/{id}/resume` | After resumed steps complete | Per-step report for the post-review steps |

### Orchestration: Per-Step Reporting

For workflow orchestration, usage is reported per step rather than aggregated, since each step may use a different agent and model:

```
Workflow: Campaign Launch Checklist
├─ Step 1: qa_agent (haiku) → report: {tokenInput: 800, tokenOutput: 200, model: "haiku", agentType: "qa"}
├─ Step 2: qa_agent (haiku) → report: {tokenInput: 600, tokenOutput: 150, ...}
├─ Step 3: legal_agent (opus) → report: {tokenInput: 2000, tokenOutput: 800, model: "opus", agentType: "legal"}
└─ Step 4: report_agent (sonnet) → report: {tokenInput: 1500, tokenOutput: 3000, model: "sonnet", agentType: "report"}
```

### Relationship to Existing Callback

| Aspect | HMAC Callback (`ERPCallbackService`) | Billing Report (`UsageReportService`) |
|--------|--------------------------------------|--------------------------------------|
| Purpose | Completion notification + result delivery | Usage/cost tracking |
| Auth | Per-payload HMAC signature | Static `X-Service-Key` |
| Method | PATCH to per-request `callback_url` | POST to fixed `/api/v1/billing/usage/report` |
| Payload | status, output, token counts, duration | token counts, model, agent, module |
| Trigger | Only when `callback_url` provided | Always (all endpoints) |
| Required | Optional (ERP-integrated mode only) | Always |

Both continue to operate. The HMAC callback delivers results; the billing service reports usage.

---

## SSE Event Catalog

### Existing Events (unchanged)

| Event | Source | Description |
|-------|--------|-------------|
| `state_update` | `BaseAgent` | Agent state machine transitions (IDLE → THINKING → ACTING → CREATING → COMPLETE) |
| `work_start` | `BaseAgent` | Agent begins processing |
| `work_action` | `BaseAgent` | Agent performs an action (tool call) |
| `entity_created` | `BaseAgent` | Agent creates a resource in the ERP |
| `work_complete` | `BaseAgent` | Agent finishes processing |
| `work_error` | `BaseAgent` | Agent encounters an error |
| `artifact:create` | `BaseAgent` | Artifact creation started |
| `artifact:update` | `BaseAgent` | Artifact data updated (streaming build) |
| `artifact:complete` | `BaseAgent` | Artifact finalized |

### New Events (workflow orchestration)

| Event | Source | Description |
|-------|--------|-------------|
| `workflow_start` | `AgentOrchestrator` | Workflow execution begins |
| `step_progress` | `AgentOrchestrator` | A step starts, completes, or fails |
| `workflow_paused` | `AgentOrchestrator` | Workflow paused for human review |
| `workflow_complete` | `AgentOrchestrator` | Workflow execution finished |

### New Event Payloads

**`workflow_start`**
```json
{
  "event": "workflow_start",
  "data": {
    "execution_id": "exec-abc-123",
    "workflow_id": "campaign_launch_checklist",
    "workflow_name": "Campaign Launch Checklist",
    "step_count": 8,
    "initiated_by": "user-456"
  }
}
```

**`step_progress`**
```json
{
  "event": "step_progress",
  "data": {
    "execution_id": "exec-abc-123",
    "step_id": "verify_landing",
    "step_name": "Verify Landing Page",
    "agent": "qa_agent",
    "status": "running",
    "step_index": 1,
    "total_steps": 8
  }
}
```

**`workflow_paused`**
```json
{
  "event": "workflow_paused",
  "data": {
    "execution_id": "exec-abc-123",
    "pending_review_step_id": "human_review",
    "pending_review_step_name": "Human Review Checkpoint",
    "completed_steps": 6,
    "total_steps": 8
  }
}
```

**`workflow_complete`**
```json
{
  "event": "workflow_complete",
  "data": {
    "execution_id": "exec-abc-123",
    "status": "completed",
    "completed_steps": 8,
    "failed_steps": 0,
    "duration_seconds": 45.2,
    "step_results_summary": {
      "verify_landing": "passed",
      "run_audit": "score: 92/100",
      "run_a11y": "2 warnings",
      "check_seo": "passed",
      "check_utms": "passed",
      "check_gdpr": "compliant",
      "human_review": "approved",
      "capture_proof": "3 screenshots captured"
    }
  }
}
```

---

## Implementation Sequence

### Phase 1: Foundation (no breaking changes)

| # | Task | File |
|---|------|------|
| 1 | Add `ARTIFACT_DATA_SCHEMAS` dict mapping each `ArtifactType` to its data JSON schema | `src/protocols/artifacts.py` |
| 2 | Add `artifact_format: Optional[str] = None` field to `AgentContext` | `src/agents/base.py` |
| 3 | Add universal `emit_artifact` tool definition to `BaseAgent` | `src/agents/base.py` |
| 4 | Add `emit_artifact` tool dispatch in `run()` and `stream()` | `src/agents/base.py` |
| 5 | Update `_build_system_prompt()` with artifact protocol instructions and format-specific schema | `src/agents/base.py` |

### Phase 2: New Endpoints + Billing

| # | Task | File |
|---|------|------|
| 6 | Add `artifact_format` field to `ExecuteRequest` | `src/api/routes.py` |
| 7 | Add `artifact_format` field to `HandoffContext` | `src/protocols/handoffs.py` |
| 8 | Add `erp_service_key` config field to `Settings` | `src/config.py` |
| 9 | Implement `UsageReportService` class | `src/api/erp_integration.py` |
| 10 | Implement `POST /api/v1/handoff` endpoint | `src/api/routes.py` |
| 11 | Implement `POST /api/v1/orchestrate` endpoint with `OrchestrateRequest` model | `src/api/routes.py` |
| 12 | Implement `POST /api/v1/orchestrate/{execution_id}/resume` endpoint with `ResumeRequest` model | `src/api/routes.py` |
| 13 | Define workflow SSE event emission in orchestrator `notification_callback` | `src/orchestration/orchestrator.py` |
| 14 | Fix `resume_workflow()` to re-execute remaining steps after approval | `src/orchestration/orchestrator.py` |
| 15 | Wire `UsageReportService.report_usage()` into all four endpoints as background task | `src/api/routes.py` |

### Phase 3: Validation and Testing

| # | Task | File |
|---|------|------|
| 16 | Add module-level agent validation to handoff endpoint | `src/api/routes.py` |
| 17 | Add JSON schema validation for artifact `data` payloads against `ARTIFACT_DATA_SCHEMAS` | `src/protocols/artifacts.py` |
| 18 | Integration tests: handoff flow (auto-start + approval paths) | `tests/` |
| 19 | Integration tests: orchestration flow (template + inline + resume) | `tests/` |
| 20 | Integration tests: artifact emission (verify SSE events contain structured data) | `tests/` |
| 21 | Integration tests: billing reports sent for all endpoints with correct payload | `tests/` |

---

## Appendix: Endpoint Compatibility Matrix

| ERP Feature | Endpoint Used | Response Type | Billing |
|-------------|---------------|---------------|---------|
| Mission Control chat (conversational) | `POST /api/v1/agent/execute` | SSE stream / JSON | `UsageReportService` (background) |
| Mission Control chat (artifact) | `POST /api/v1/agent/execute` + `artifact_format` | SSE stream with `artifact:create`/`artifact:complete` | `UsageReportService` (background) |
| Cross-agent handoff (from artifact actions) | `POST /api/v1/handoff` | SSE stream or `HandoffResponse` | `UsageReportService` (background) |
| Canvas workflow execution | `POST /api/v1/orchestrate` | SSE stream with workflow events | `UsageReportService` per step |
| Canvas workflow resume after review | `POST /api/v1/orchestrate/{id}/resume` | `WorkflowExecution` JSON | `UsageReportService` per step |
