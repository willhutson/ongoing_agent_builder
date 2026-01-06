# Ongoing Agent Builder - Architecture

## Overview

A **standalone instance framework** built on the Claude Agent SDK that creates, manages, and deploys agents for ERP automation tasks. The framework follows a **one-to-many** relationship: a single agent builder serves multiple `erp_staging_lmtd` instances, enabling centralized agent improvements that propagate to all connected ERP systems in real-time (version control dependent).

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

This triad enables **real problem solving** - agents don't just respond, they understand context, take meaningful action, and build new capabilities.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ONGOING AGENT BUILDER                       │
│                   (Standalone Instance Framework)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Claude Agent SDK                        │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │   │
│  │  │ SDKClient   │ │   Hooks     │ │  Session Mgmt   │    │   │
│  │  └─────────────┘ └─────────────┘ └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────┴───────────────────────────┐     │
│  │                  Agent Registry                        │     │
│  │  ┌──────────────────────────────────────────────────┐ │     │
│  │  │ Task Agents        │ Workflow Agents             │ │     │
│  │  │ ├─ Invoicing       │ ├─ Custom per client        │ │     │
│  │  │ ├─ Inventory       │ ├─ Approval chains          │ │     │
│  │  │ ├─ Purchasing      │ └─ Multi-step processes     │ │     │
│  │  │ └─ Reporting       │                             │ │     │
│  │  └──────────────────────────────────────────────────┘ │     │
│  └───────────────────────────────────────────────────────┘     │
│                              │                                  │
│  ┌───────────────────────────┴───────────────────────────┐     │
│  │                  Builder Capabilities                  │     │
│  │  • Feature builder (within tasks)                      │     │
│  │  • Workflow designer                                   │     │
│  │  • Form generator                                      │     │
│  │  • Button/action creator                               │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │ API Connections
                               │ (Direct API/DB)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ERP STAGING INSTANCES                        │
│                      (erp_staging_lmtd)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Instance A  │  │ Instance B  │  │ Instance C  │   ...       │
│  │ (Client 1)  │  │ (Client 2)  │  │ (Client 3)  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  Each instance receives:                                        │
│  • Same core agent capabilities                                 │
│  • Custom workflow configurations                               │
│  • Client-specific forms/buttons                                │
│  • Real-time agent upgrades (version controlled)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Claude Agent SDK Integration

The framework is built **on top of** the Claude Agent SDK, not alongside it:

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class ERPAgent:
    """Base class for all ERP agents, wrapping Claude Agent SDK."""

    def __init__(self, agent_spec: AgentSpec, erp_connection: ERPConnection):
        self.options = ClaudeAgentOptions(
            system_prompt=self._build_system_prompt(agent_spec),
            allowed_tools=agent_spec.tools,
            hooks={
                "PreToolUse": [self._validate_erp_action],
                "PostToolUse": [self._log_erp_action],
            }
        )
        self.client = ClaudeSDKClient(options=self.options)
        self.erp = erp_connection
```

**Why**: Enables continued use of Claude Code as primary development driver while agents leverage the same battle-tested harness.

### 2. Standalone Instance Pattern

Each agent runs as an independent instance with:
- Own session management
- Own ERP connection context
- Shared agent definitions (from registry)

**Why**: Isolation prevents cross-client data leakage while centralized definitions enable fleet-wide upgrades.

### 3. One-to-Many Deployment

```
Agent Definition (v1.2.0)
         │
         ├──► Instance A (Client 1) ──► erp_staging_lmtd_client1
         ├──► Instance B (Client 2) ──► erp_staging_lmtd_client2
         └──► Instance C (Client 3) ──► erp_staging_lmtd_client3
```

Agent upgrades propagate to all instances based on version control:
- **Pinned versions**: Client stays on specific version until manually upgraded
- **Latest tracking**: Client automatically receives improvements
- **Canary releases**: Test new versions on subset before fleet-wide rollout

### 4. Direct API/DB Connection to ERP

Agents connect to `erp_staging_lmtd` via direct API calls:

```python
class ERPConnection:
    """Direct connection to an erp_staging_lmtd instance."""

    def __init__(self, base_url: str, api_key: str, db_config: dict = None):
        self.api = ERPApiClient(base_url, api_key)
        self.db = ERPDatabase(db_config) if db_config else None

    async def get_invoices(self, filters: dict) -> list[Invoice]:
        return await self.api.get("/invoices", params=filters)

    async def create_workflow(self, workflow_def: WorkflowDefinition) -> Workflow:
        return await self.api.post("/workflows", json=workflow_def.dict())
```

**Why**: Direct connections offer lower latency and full access to ERP capabilities without MCP server overhead.

## Agent Types

### Task Agents
Focused agents for specific ERP operations:

| Agent | Think | Do/Act | Create |
|-------|-------|--------|--------|
| **Invoicing** | Analyze billing data, identify discrepancies | Generate invoices, process payments | Build invoice templates, custom fields |
| **Inventory** | Forecast demand, detect anomalies | Update stock, trigger reorders | Design inventory views, alerts |
| **Purchasing** | Evaluate vendors, optimize costs | Create POs, approve requests | Build approval workflows |
| **Reporting** | Identify insights, correlate data | Generate reports, schedule delivery | Create custom dashboards |

### Workflow Agents
Configurable per-client for custom business processes:

- Multi-step approval chains
- Conditional branching based on business rules
- Integration with external systems
- Human-in-the-loop checkpoints

### Builder Agents
Meta-agents that create/modify ERP components:

- **Feature Builder**: Adds capabilities within existing task agents
- **Form Generator**: Creates data entry forms with validation
- **Button Creator**: Adds action buttons with custom logic
- **Workflow Designer**: Builds multi-step automated processes

## Directory Structure

```
ongoing_agent_builder/
├── ARCHITECTURE.md          # This document
├── README.md                 # Project overview
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent_base.py    # ERPAgent base class (wraps Claude SDK)
│   │   ├── registry.py      # Agent registry and versioning
│   │   └── connection.py    # ERPConnection for erp_staging_lmtd
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── task/
│   │   │   ├── invoicing.py
│   │   │   ├── inventory.py
│   │   │   ├── purchasing.py
│   │   │   └── reporting.py
│   │   ├── workflow/
│   │   │   └── base_workflow.py
│   │   └── builder/
│   │       ├── feature_builder.py
│   │       ├── form_generator.py
│   │       ├── button_creator.py
│   │       └── workflow_designer.py
│   ├── specs/               # Agent specifications (YAML/JSON)
│   │   └── ...
│   └── api/                 # API layer for ERP integration
│       └── ...
├── tests/
│   └── ...
└── pyproject.toml
```

## Integration with Claude Code

This framework is designed to be developed and operated via Claude Code:

1. **Development**: Use Claude Code to build/refine agents
2. **Testing**: Claude Code runs agents against test ERP instances
3. **Deployment**: Claude Code manages version control and rollouts
4. **Operations**: Claude Code monitors agent performance and issues

The Claude Agent SDK integration means agents share the same foundation, enabling seamless development workflows.

## Next Steps

1. [ ] Set up Python project structure with pyproject.toml
2. [ ] Implement `ERPAgent` base class wrapping Claude SDK
3. [ ] Create `ERPConnection` for erp_staging_lmtd API
4. [ ] Build first task agent (suggest: Invoicing)
5. [ ] Define agent spec format (YAML schema)
6. [ ] Implement agent registry with versioning

---

*Document created: 2026-01-06*
*Last updated: 2026-01-06*
