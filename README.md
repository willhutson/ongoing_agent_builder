# Ongoing Agent Builder

Standalone API agent service for [TeamLMTD ERP](https://github.com/willhutson/erp_staging_lmtd) - built on the **Claude Agent SDK**.

## Vision

A multi-tenant agent service that operates across all ERP instances, following the core paradigm:

```
THINK → ACT → CREATE
```

- **Think**: Analyze context, understand requirements, plan approach
- **Act**: Execute tools, query data, validate, iterate
- **Create**: Combine thinking + action into deliverables (documents, assets, recommendations)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              ERP Instances (Multi-Tenant)                   │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│    │ Tenant A │  │ Tenant B │  │ Tenant C │                │
│    └────┬─────┘  └────┬─────┘  └────┬─────┘                │
└─────────┼─────────────┼─────────────┼───────────────────────┘
          │             │             │
          └─────────────┼─────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              AGENT SERVICE (Standalone)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   REST API Layer                        │ │
│  │  POST /api/v1/agent/execute                            │ │
│  │  POST /api/v1/agent/stream                             │ │
│  │  GET  /api/v1/agent/status/:id                         │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       ▼                                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Claude Agent SDK                           │ │
│  │  ┌─────────────────────────────────────────────────┐   │ │
│  │  │            Agent Loop (Orchestrator)             │   │ │
│  │  │  Think → Tool Selection → Execute → Feedback     │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  │                       │                                 │ │
│  │  ┌────────────────────▼────────────────────────────┐   │ │
│  │  │              Subagent Pool                       │   │ │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐           │   │ │
│  │  │  │   RFP   │ │  Brief  │ │ Content │  ...      │   │ │
│  │  │  │  Agent  │ │  Agent  │ │  Agent  │           │   │ │
│  │  │  └─────────┘ └─────────┘ └─────────┘           │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────┘ │
│                       │                                      │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │           In-Process MCP Tools                          │ │
│  │  @tool("query_erp")      @tool("generate_document")    │ │
│  │  @tool("analyze_brief")  @tool("create_asset_draft")   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Priority Agent Capabilities

### Phase 1: Foundation
| Capability | ERP Module | Agent Role |
|------------|------------|------------|
| **RFP Processing** | `rfp` | Analyze RFPs, extract requirements, draft responses |
| **Brief Intake** | `briefs` | AI-assisted brief creation, requirement extraction |
| **Document Generation** | `content`, `studio` | Create proposals, reports, SOWs |
| **Draft Assets** | `dam`, `content-engine` | Generate creative starting points for teams |

### Phase 2: Operations
| Capability | ERP Module | Agent Role |
|------------|------------|------------|
| **Resource Optimization** | `resources`, `delegation` | Smart allocation, workload balancing |
| **Reporting** | `reporting`, `dashboard` | Automated insights, KPI analysis |
| **Workflow Automation** | `workflows` | Trigger-based agent actions |

### Phase 3: Intelligence
| Capability | ERP Module | Agent Role |
|------------|------------|------------|
| **CRM Insights** | `crm` | Client health, opportunity detection |
| **Scope Analysis** | `scope-changes`, `retainer` | Scope creep detection, utilization alerts |
| **Predictive** | `nps`, `complaints` | Churn risk, satisfaction trends |

## ERP Module Coverage (28 Total)

```
ai              briefs          builder         chat
complaints      content-engine  content         crm
dam             dashboard       delegation      files
forms           integrations    leave           notifications
nps             onboarding      reporting       resources
retainer        rfp             scope-changes   settings
studio          time-tracking   whatsapp        workflows
```

## Tech Stack

- **Runtime**: Python 3.11+
- **Agent Framework**: Claude Agent SDK (`claude-agent-sdk`)
- **API**: FastAPI (async)
- **Model**: Claude Opus 4.5 (recommended for agents)
- **Tools**: In-process MCP servers (no subprocess overhead)
- **Deployment**: Containerized, stateless per-request or session-persistent

## Agent Paradigm: Think → Act → Create

```python
# Conceptual flow for each agent task
async def agent_task(task: str):
    # THINK: Analyze and plan
    context = await gather_context(task)
    plan = await reason_about_approach(context)

    # ACT: Execute with tools
    while not complete:
        tool = select_best_tool(plan)
        result = await execute_tool(tool)
        feedback = evaluate_result(result)
        plan = adjust_plan(feedback)

    # CREATE: Synthesize output
    deliverable = combine_results(all_results)
    return deliverable
```

## Living Feature Pipeline

Features and scope requests flow from:
1. GitHub Issues (tagged for agent development)
2. ERP `/knowledge/agents/skills` directory
3. This repository's issue tracker

---

## Getting Started

```bash
# Clone
git clone https://github.com/willhutson/ongoing_agent_builder.git
cd ongoing_agent_builder

# Setup (coming soon)
pip install -r requirements.txt

# Run (coming soon)
uvicorn main:app --reload
```

## Related

- [ERP Staging LMTD](https://github.com/willhutson/erp_staging_lmtd) - The ERP platform this service supports
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) - Agent framework
