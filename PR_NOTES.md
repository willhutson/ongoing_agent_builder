# PR: Add Comprehensive Agent Builder Guide for SpokeStack Platform

## Summary

Complete developer documentation (~4,700 lines) for building, deploying, and managing agents on the SpokeStack platform. This guide powers the Agent Builder interface and establishes the architecture for multi-tenant agent deployment.

## What's Included

### 1. Core Agent Development (Sections 1-8)

- **Think → Act → Create** paradigm for agent behavior
- Agent anatomy: system prompts, tool definitions, specialization
- 46-agent ecosystem architecture
- ERP module integration patterns
- Tool schema design with Pydantic validation
- Testing strategies and best practices

### 2. Instance-Level Deployment & Scaling (Sections 9.1-9.11)

**Three-Layer Architecture:**

| Layer | Scope | Update Method |
|-------|-------|---------------|
| Layer 1: Core Agents | Global | Container deployment via CI/CD |
| Layer 2: Instance Config | Per-tenant | Database-stored, hot-reloadable |
| Layer 3: Skill Extensions | Per-instance | Webhook-based custom tools |

**Key Components:**

- `InstanceAgentConfig` - Per-tenant agent configuration
- `InstanceSkill` - Custom webhook-based tools
- `AgentFactory` - Runtime agent assembly
- `SkillExecutor` - Secure webhook execution

### 3. Agent Version Control System (Sections 9.12-9.21)

**Problem Solved:** Global agent updates (e.g., reach-focused) can break instance-specific optimizations (e.g., performance/ROAS-focused for ecommerce).

**Features:**

| Feature | Description |
|---------|-------------|
| Semantic Versioning | `major.minor.patch` with optimization tags |
| Update Notifications | Instance owners notified of changes + impact |
| Impact Analysis | Detects skill conflicts and optimization mismatches |
| Sandbox Testing | Side-by-side comparison before going live |
| Version Pinning | Lock to specific version, skip problematic updates |
| Rollback | Instant revert to previous version |

**Update Policies:**

- `auto` - Immediate deployment (for non-critical agents)
- `staged` - Sandbox first, then promote
- `manual` - Full control, explicit approval required

**Skill-to-Core Promotion:** High-performing instance skills can be promoted to core agents for all instances.

### 4. Agent Fine-Tuning Model (Sections 9.22-9.34)

**Three-Tier Tuning Hierarchy:**

| Tier | Owner | Controls |
|------|-------|----------|
| 1. Agent Builder | SpokeStack Platform Team | Core prompts, safety constraints, model selection, compliance |
| 2. Instance | Agency Admins | Vertical knowledge, agency voice, behavior params, regional defaults |
| 3. Client | Account Managers / Clients | Brand voice, tone keywords, content rules, learned preferences |

**Auto-Learning System:**

| User Action | Result |
|-------------|--------|
| Approve output | Reinforce style, increase weight |
| Reject output | Identify issue, add to "never" rules |
| Correct output | Extract pattern, add to content rules |

**Governance:**

- Role-based permissions (platform_admin → instance_admin → client_admin → client_user)
- Parameter-level access control
- Complete audit trail of all tuning changes

**Client Tuning UI:** Simple dashboard for non-technical users with brand voice, tone keywords, and always/never/prefer content rules.

## Data Models

| Model | Purpose |
|-------|---------|
| `InstanceAgentConfig` | Per-tenant agent settings |
| `InstanceSkill` | Custom webhook tools |
| `AgentVersion` | Version metadata + optimization tags |
| `InstanceVersionConfig` | Update policy, pinned version |
| `AgentBuilderConfig` | Tier 1: Platform defaults |
| `InstanceTuningConfig` | Tier 2: Agency customization |
| `ClientTuningConfig` | Tier 3: Client preferences |
| `AgentOutputFeedback` | Feedback loop data |
| `TuningAuditLog` | Change tracking |

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /instances/{id}/agents` | List configured agents |
| `PUT /instances/{id}/agents/{type}` | Update agent config |
| `POST /instances/{id}/skills` | Add custom skill |
| `GET /agents/{type}/versions` | List available versions |
| `POST /instances/{id}/agents/{type}/sandbox` | Create sandbox test |
| `POST /sandbox/{id}/promote` | Promote sandbox to live |
| `PUT /instances/{id}/tuning` | Update instance tuning |
| `PUT /clients/{id}/tuning` | Update client tuning |
| `POST /feedback` | Submit output feedback |

## Why This Matters

- **Scalability** - Single codebase serves unlimited instances with per-tenant customization
- **Safety** - Version control prevents breaking changes from disrupting client workflows
- **Flexibility** - Three-tier tuning lets each level optimize without stepping on others
- **Learning** - Feedback loops continuously improve agent outputs per client
- **Governance** - Clear permissions model for enterprise compliance

## Files Changed

```
spokestack/docs/AGENT_BUILDER_GUIDE.md  +4,744 lines (new file)
```

## Commits

1. `5f0b6f1` - Add comprehensive Agent Builder Guide for SpokeStack platform
2. `45469dc` - Add Instance-Level Deployment & Scaling architecture (Section 9)
3. `5addc7b` - Add Agent Version Control System (Sections 9.12-9.21)
4. `7e169ee` - Add Agent Fine-Tuning Model (Sections 9.22-9.34)

## Test Plan

- [ ] Review guide structure and completeness
- [ ] Validate code examples compile/run
- [ ] Confirm data models align with existing schema patterns
- [ ] Test API endpoint designs against FastAPI patterns
