# Ongoing Agent Builder - Architecture

## Overview

A **standalone orchestration framework** built on the Claude Agent SDK that creates, refines, and deploys agents to `erp_staging_lmtd` instances. Rather than replacing the ERP's existing agent infrastructure, this framework **powers and extends it** - providing the AI backbone for skills, personas, and invocations already defined in the ERP.

**Relationship:**
```
┌─────────────────────────────────────────────────────────────────┐
│                     ONGOING AGENT BUILDER                       │
│            (Claude Agent SDK Orchestration Layer)               │
│                                                                 │
│   • Develops/refines agent skills                               │
│   • Powers AgentPersona execution                               │
│   • Manages skill versioning & deployment                       │
│   • One-to-many: serves multiple ERP instances                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │ API Integration
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      erp_staging_lmtd                           │
│              (Multi-tenant ERP Platform)                        │
│                                                                 │
│   Existing Infrastructure:                                      │
│   • AgentSkill, AgentPersona, AgentInvocation models           │
│   • FormTemplate, ContentTrigger systems                        │
│   • Builder, Workflows, Forms modules                           │
│   • YAML+MD skill definitions in /knowledge/agents/skills       │
└─────────────────────────────────────────────────────────────────┘
```

## Core Philosophy

Agents operate across three capability domains:

```
┌─────────────────────────────────────────────────────────┐
│                    AGENT CAPABILITIES                   │
├─────────────────┬─────────────────┬─────────────────────┤
│      THINK      │    DO / ACT     │       CREATE        │
├─────────────────┼─────────────────┼─────────────────────┤
│ • Analyze data  │ • Execute tasks │ • Build workflows   │
│ • Plan approach │ • Call APIs     │ • Generate forms    │
│ • Reason about  │ • Update records│ • Create buttons    │
│   constraints   │ • Trigger flows │ • Design features   │
│ • Problem-solve │ • Validate work │ • Extend system     │
└─────────────────┴─────────────────┴─────────────────────┘
```

This triad enables **real problem solving** - agents understand context, take meaningful action, and build new capabilities within the ERP.

## erp_staging_lmtd Integration

### Existing Agent Infrastructure

The ERP already has a comprehensive agent system. We integrate with, not replace, these components:

**Database Models (Prisma):**

```prisma
model AgentSkill {
  id            String   @id
  organizationId String
  slug          String
  name          String
  category      String
  triggers      Json     // Event triggers that activate skill
  inputs        Json     // Required input parameters
  outputs       Json     // Expected output structure
  isEnabled     Boolean
}

model AgentPersona {
  id            String   @id
  organizationId String
  slug          String
  name          String
  systemPrompt  String   // AI personality/instructions
  allowedSkills String[] // Skills this persona can use
  isEnabled     Boolean
}

model AgentInvocation {
  id            String   @id
  organizationId String
  skillId       String
  triggeredBy   String
  entityType    String   // Brief, Client, Deal, etc.
  entityId      String
  status        String   // pending, running, completed, failed
  input         Json
  output        Json
}
```

**Existing Skills in `/knowledge/agents/skills/`:**
- `brief-creator.md` - Creates project briefs from client requests
- `client-analyzer.md` - Analyzes client data and patterns
- `deadline-tracker.md` - Monitors and alerts on deadlines
- `quality-checker.md` - Reviews deliverables for quality
- `resource-scanner.md` - Finds available team resources

**Related Modules (28 total):**
- `Builder` - Form builder UI
- `Workflows` - Workflow automation
- `Forms` - Form definitions and submissions
- `Briefs`, `CRM`, `Resources`, `Retainers`, etc.

### Skill Definition Format

Skills use a YAML+Markdown hybrid format with founder knowledge capture:

```yaml
---
id: brief-creator
type: skill
version: 1.0.0
status: active
category: briefs

triggers:
  - event: client_request_received
  - event: manual_invoke

inputs:
  - name: client_context
    type: object
    required: true
  - name: request_details
    type: string
    required: true
  - name: resource_availability
    type: object
    required: false

outputs:
  - name: draft_brief
    type: Brief
  - name: resource_suggestions
    type: User[]
  - name: timeline_estimate
    type: object
  - name: quality_warnings
    type: string[]

dependencies:
  - timeline_estimator
  - resource_scanner

permissions:
  - brief:create
  - client:read
  - user:read
---

# Brief Creator

## Purpose
Creates comprehensive project briefs from client requests...

## Founder Knowledge
> "A brief is complete when it has actionable deliverables,
> clear timeline, and comparable reference work."

## Process
1. Analyze client request
2. Scan for similar past briefs
3. Identify required resources
4. Estimate timeline
5. Generate draft with quality checks

## Error Handling
| Error | Action |
|-------|--------|
| Missing client context | Request additional info |
| No available resources | Flag for manual review |
...
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ONGOING AGENT BUILDER                            │
│                    (Standalone Orchestration Framework)                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Claude Agent SDK                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │   │
│  │  │ SDKClient    │  │    Hooks     │  │   Session Management  │  │   │
│  │  │              │  │ • PreToolUse │  │   • Multi-tenant      │  │   │
│  │  │ • query()    │  │ • PostToolUse│  │   • Org isolation     │  │   │
│  │  │ • resume()   │  │ • Validation │  │   • State persistence │  │   │
│  │  └──────────────┘  └──────────────┘  └───────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  ┌─────────────────────────────────┴─────────────────────────────┐     │
│  │                      Skill Engine                              │     │
│  │  ┌─────────────────────────────────────────────────────────┐  │     │
│  │  │ Skill Compiler                                          │  │     │
│  │  │ • Parse YAML+MD skill definitions                       │  │     │
│  │  │ • Generate ClaudeAgentOptions from skill spec           │  │     │
│  │  │ • Wire triggers to ERP ContentTrigger system            │  │     │
│  │  └─────────────────────────────────────────────────────────┘  │     │
│  │  ┌─────────────────────────────────────────────────────────┐  │     │
│  │  │ Skill Runner                                            │  │     │
│  │  │ • Execute skills via Claude SDK                         │  │     │
│  │  │ • Handle inputs/outputs per skill spec                  │  │     │
│  │  │ • Record AgentInvocation for audit                      │  │     │
│  │  └─────────────────────────────────────────────────────────┘  │     │
│  │  ┌─────────────────────────────────────────────────────────┐  │     │
│  │  │ Skill Builder (Meta-Agent)                              │  │     │
│  │  │ • Create new skill definitions                          │  │     │
│  │  │ • Refine existing skills from feedback                  │  │     │
│  │  │ • Capture founder knowledge                             │  │     │
│  │  └─────────────────────────────────────────────────────────┘  │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                    │                                    │
│  ┌─────────────────────────────────┴─────────────────────────────┐     │
│  │                    Persona Engine                              │     │
│  │  • Load AgentPersona from ERP                                  │     │
│  │  • Apply systemPrompt to Claude SDK                            │     │
│  │  • Enforce allowedSkills permissions                           │     │
│  │  • Handle persona-specific conversation style                  │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                    │                                    │
│  ┌─────────────────────────────────┴─────────────────────────────┐     │
│  │                    Builder Agents                              │     │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐  │     │
│  │  │ Form        │ │ Workflow    │ │ Feature                 │  │     │
│  │  │ Generator   │ │ Designer    │ │ Builder                 │  │     │
│  │  │             │ │             │ │                         │  │     │
│  │  │ Creates     │ │ Creates     │ │ Extends skills with     │  │     │
│  │  │ FormTemplate│ │ Content-    │ │ new capabilities        │  │     │
│  │  │ entries     │ │ Trigger     │ │                         │  │     │
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘  │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                    │                                    │
│  ┌─────────────────────────────────┴─────────────────────────────┐     │
│  │                  Version Control & Deployment                  │     │
│  │  • Skill versioning (semver)                                   │     │
│  │  • Deploy to specific ERP instances                            │     │
│  │  • Canary/gradual rollout                                      │     │
│  │  • Rollback capabilities                                       │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ REST API / Direct DB
                                     │ (Multi-tenant, org-isolated)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         erp_staging_lmtd                                │
│                    (Next.js 14 + Prisma + Supabase)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Instance A  │  │ Instance B  │  │ Instance C  │  │ Instance D  │    │
│  │ (Org: acme) │  │ (Org: beta) │  │ (Org: corp) │  │ (Org: demo) │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                                         │
│  Shared Infrastructure:                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ AgentSkill │ AgentPersona │ AgentInvocation │ FormTemplate      │   │
│  │ ContentTrigger │ KnowledgeDocument │ Brief │ Deliverable │ ... │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Modules: AI, Briefs, Builder, Workflows, Forms, CRM, Resources...     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Claude Agent SDK as Execution Engine

The framework wraps Claude Agent SDK to execute ERP-defined skills:

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class SkillRunner:
    """Executes AgentSkill definitions using Claude Agent SDK."""

    def __init__(self, erp_client: ERPClient):
        self.erp = erp_client

    async def run_skill(
        self,
        skill: AgentSkill,
        persona: AgentPersona,
        invocation_input: dict,
        org_id: str
    ) -> AgentInvocation:
        # Create invocation record
        invocation = await self.erp.create_invocation(
            skill_id=skill.id,
            org_id=org_id,
            status="running",
            input=invocation_input
        )

        # Build Claude options from skill + persona
        options = ClaudeAgentOptions(
            system_prompt=self._build_prompt(skill, persona),
            allowed_tools=self._map_permissions_to_tools(skill.permissions),
            hooks={
                "PreToolUse": [self._validate_org_access(org_id)],
                "PostToolUse": [self._log_action(invocation.id)],
            }
        )

        # Execute via Claude SDK
        async with ClaudeSDKClient(options=options) as client:
            result = await client.query(
                self._format_input(skill, invocation_input)
            )
            output = await self._collect_output(result, skill.outputs)

        # Update invocation with result
        await self.erp.update_invocation(
            invocation.id,
            status="completed",
            output=output
        )

        return invocation

    def _build_prompt(self, skill: AgentSkill, persona: AgentPersona) -> str:
        """Combine persona systemPrompt with skill context."""
        return f"""
{persona.system_prompt}

## Current Skill: {skill.name}

{skill.founder_knowledge}

## Expected Outputs
{self._format_outputs(skill.outputs)}

## Constraints
- Only use allowed permissions: {skill.permissions}
- Record all actions for audit
- Respect organization boundaries
"""
```

### 2. Skill Compiler

Transforms YAML+MD skill definitions into executable Claude configurations:

```python
class SkillCompiler:
    """Compiles skill definitions from /knowledge/agents/skills/"""

    def compile(self, skill_path: str) -> CompiledSkill:
        raw = self._parse_yaml_md(skill_path)

        return CompiledSkill(
            metadata=raw.frontmatter,
            system_context=self._extract_context(raw.body),
            founder_knowledge=self._extract_founder_knowledge(raw.body),
            tool_permissions=self._map_to_claude_tools(raw.frontmatter.permissions),
            input_schema=self._build_input_schema(raw.frontmatter.inputs),
            output_schema=self._build_output_schema(raw.frontmatter.outputs),
            triggers=self._compile_triggers(raw.frontmatter.triggers),
        )

    def deploy_to_erp(self, compiled: CompiledSkill, org_id: str):
        """Sync compiled skill to ERP AgentSkill table."""
        self.erp.upsert_agent_skill(
            org_id=org_id,
            slug=compiled.metadata.id,
            name=compiled.metadata.id.replace("-", " ").title(),
            category=compiled.metadata.category,
            triggers=compiled.triggers,
            inputs=compiled.input_schema,
            outputs=compiled.output_schema,
            is_enabled=compiled.metadata.status == "active"
        )
```

### 3. Builder Agents (Meta-Agents)

Agents that create/modify ERP components by calling ERP APIs:

**Form Generator:**
```python
class FormGeneratorAgent:
    """Creates FormTemplate entries in ERP."""

    async def generate_form(self, requirements: str, org_id: str) -> FormTemplate:
        # Use Claude to design form structure
        options = ClaudeAgentOptions(
            system_prompt=FORM_DESIGNER_PROMPT,
            allowed_tools=["erp_create_form_template", "erp_list_form_templates"]
        )

        async with ClaudeSDKClient(options=options) as client:
            result = await client.query(f"""
                Design a form for: {requirements}

                Use erp_create_form_template to create the form in the ERP.
                The form should follow existing patterns in the organization.
            """)

        return self._extract_created_form(result)
```

**Workflow Designer:**
```python
class WorkflowDesignerAgent:
    """Creates ContentTrigger workflows in ERP."""

    async def design_workflow(self, requirements: str, org_id: str) -> list[ContentTrigger]:
        # Use Claude to design trigger chain
        options = ClaudeAgentOptions(
            system_prompt=WORKFLOW_DESIGNER_PROMPT,
            allowed_tools=[
                "erp_create_content_trigger",
                "erp_list_content_triggers",
                "erp_list_agent_skills"  # Can wire skills into workflows
            ]
        )

        async with ClaudeSDKClient(options=options) as client:
            result = await client.query(f"""
                Design a workflow for: {requirements}

                Create ContentTrigger entries that chain together.
                Can invoke existing AgentSkills as actions.
            """)

        return self._extract_created_triggers(result)
```

### 4. Multi-Tenant Isolation

All operations are scoped to `organizationId`:

```python
class ERPClient:
    """Organization-scoped ERP API client."""

    def __init__(self, base_url: str, api_key: str, org_id: str):
        self.base_url = base_url
        self.api_key = api_key
        self.org_id = org_id  # All requests scoped to this org

    async def get_skills(self) -> list[AgentSkill]:
        return await self._get(f"/api/v1/agent-skills?organizationId={self.org_id}")

    async def create_invocation(self, **kwargs) -> AgentInvocation:
        return await self._post("/api/v1/agent-invocations", {
            "organizationId": self.org_id,
            **kwargs
        })
```

### 5. One-to-Many Deployment

```
Skill Definition (v1.2.0) in ongoing_agent_builder
         │
         │ deploy_to_erp()
         │
         ├──► Organization: acme    ──► AgentSkill record (acme)
         ├──► Organization: beta    ──► AgentSkill record (beta)
         └──► Organization: corp    ──► AgentSkill record (corp)
```

Version control strategies:
- **Pinned**: Org stays on specific skill version
- **Latest**: Org auto-receives improvements
- **Canary**: Test on subset before fleet-wide

## API Integration with erp_staging_lmtd

### Required ERP Endpoints

The agent builder needs these API endpoints in erp_staging_lmtd:

```typescript
// Agent Skills
GET    /api/v1/agent-skills?organizationId=...
POST   /api/v1/agent-skills
PATCH  /api/v1/agent-skills/:id
DELETE /api/v1/agent-skills/:id

// Agent Personas
GET    /api/v1/agent-personas?organizationId=...
POST   /api/v1/agent-personas
PATCH  /api/v1/agent-personas/:id

// Agent Invocations
GET    /api/v1/agent-invocations?organizationId=...
POST   /api/v1/agent-invocations
PATCH  /api/v1/agent-invocations/:id  // Update status, output

// Form Templates (for Form Generator)
GET    /api/v1/form-templates?organizationId=...
POST   /api/v1/form-templates

// Content Triggers (for Workflow Designer)
GET    /api/v1/content-triggers?organizationId=...
POST   /api/v1/content-triggers

// Knowledge Documents (for skill context)
GET    /api/v1/knowledge?organizationId=...&path=...
```

### Authentication

```python
class ERPAuth:
    """Service-to-service auth for agent builder."""

    def __init__(self, service_key: str):
        self.service_key = service_key  # Long-lived service account key

    def get_headers(self, org_id: str) -> dict:
        return {
            "Authorization": f"Bearer {self.service_key}",
            "X-Organization-Id": org_id,  # Impersonate org for multi-tenant access
        }
```

## Directory Structure

```
ongoing_agent_builder/
├── ARCHITECTURE.md              # This document
├── README.md                    # Project overview
├── pyproject.toml
│
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── sdk_client.py        # Claude Agent SDK wrapper
│   │   ├── erp_client.py        # erp_staging_lmtd API client
│   │   └── auth.py              # Service authentication
│   │
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── compiler.py          # YAML+MD → CompiledSkill
│   │   ├── runner.py            # Execute skills via Claude SDK
│   │   ├── deployer.py          # Sync skills to ERP instances
│   │   └── schemas.py           # Pydantic models for skill specs
│   │
│   ├── personas/
│   │   ├── __init__.py
│   │   └── engine.py            # Load and apply AgentPersona
│   │
│   ├── builders/
│   │   ├── __init__.py
│   │   ├── form_generator.py    # Creates FormTemplate in ERP
│   │   ├── workflow_designer.py # Creates ContentTrigger chains
│   │   ├── feature_builder.py   # Extends skills with new capabilities
│   │   └── skill_builder.py     # Meta-agent that creates new skills
│   │
│   ├── versioning/
│   │   ├── __init__.py
│   │   ├── registry.py          # Track skill versions
│   │   └── deployment.py        # Rollout strategies (pinned/latest/canary)
│   │
│   └── api/
│       ├── __init__.py
│       └── routes.py            # API for external invocation (optional)
│
├── skills/                      # Local skill definitions (synced from/to ERP)
│   ├── brief-creator.md
│   ├── client-analyzer.md
│   └── ...
│
└── tests/
    ├── test_compiler.py
    ├── test_runner.py
    └── ...
```

## Integration with Claude Code

This framework is designed to be developed and operated via Claude Code:

1. **Development**: Use Claude Code to build/refine skills and agents
2. **Testing**: Claude Code runs skills against test ERP instances
3. **Deployment**: Claude Code manages version control and rollouts
4. **Operations**: Claude Code monitors AgentInvocation status and issues

The shared Claude Agent SDK foundation enables seamless development—the same SDK powers both the development environment (Claude Code) and production execution.

## Security Considerations

### Multi-Tenant Data Isolation
- All ERP queries filtered by `organizationId`
- Agent builder service account has cross-org access, but each skill execution is org-scoped
- AgentInvocation audit trail tracks all actions per org

### Permission Boundaries
- Skills declare required permissions in YAML frontmatter
- SkillRunner validates permissions before execution
- PreToolUse hooks enforce org access boundaries

### Sensitive Data
- No secrets in skill definitions (use ERP's secure storage)
- API keys via environment variables
- Audit logging for all ERP mutations

## Next Steps

1. [ ] Add agent-related API endpoints to erp_staging_lmtd
2. [ ] Set up Python project structure with pyproject.toml
3. [ ] Implement ERPClient for API communication
4. [ ] Build SkillCompiler for YAML+MD parsing
5. [ ] Create SkillRunner with Claude SDK integration
6. [ ] Build first builder agent (suggest: Skill Builder meta-agent)
7. [ ] Set up versioning and deployment system

---

*Document created: 2026-01-06*
*Last updated: 2026-01-06*
