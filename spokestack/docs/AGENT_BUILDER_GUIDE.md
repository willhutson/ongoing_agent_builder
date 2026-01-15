# SpokeStack Agent Builder Guide

> Complete developer guide for building, customizing, and deploying agents on the SpokeStack platform.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture Overview](#2-architecture-overview)
3. [Core Paradigm: Think → Act → Create](#3-core-paradigm-think--act--create)
4. [Quick Start: Building Your First Agent](#4-quick-start-building-your-first-agent)
5. [Agent Anatomy](#5-agent-anatomy)
6. [System Prompt Design](#6-system-prompt-design)
7. [Tool Definition & Implementation](#7-tool-definition--implementation)
8. [Agent Specialization](#8-agent-specialization)
9. [**Instance-Level Deployment & Scaling**](#9-instance-level-deployment--scaling) ⭐ NEW
10. [ERP Integration Patterns](#10-erp-integration-patterns)
11. [Advanced Patterns](#11-advanced-patterns)
12. [Testing & Validation](#12-testing--validation)
13. [Deployment & Operations](#13-deployment--operations)
14. [Best Practices](#14-best-practices)
15. [Troubleshooting](#15-troubleshooting)
16. [Reference](#16-reference)

---

## 1. Introduction

### 1.1 What is an Agent?

An **agent** is an AI-powered specialist that performs specific tasks autonomously. Built on the Claude Agent SDK, each agent:

- Has a **defined purpose** (e.g., analyze RFPs, generate copy, manage campaigns)
- Possesses **domain expertise** encoded in its system prompt
- Can **execute tools** to interact with the ERP and external systems
- Follows the **Think → Act → Create** paradigm

### 1.2 Why Build Custom Agents?

| Use Case | Example |
|----------|---------|
| **Automate workflows** | Auto-generate proposals from RFP documents |
| **Domain specialization** | Create industry-specific copy agents (beauty, tech, finance) |
| **Integration bridging** | Connect external platforms to ERP workflows |
| **Knowledge synthesis** | Analyze data across multiple sources |
| **Client customization** | Build client-specific agents with unique rules |

### 1.3 Agent Categories

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     SPOKESTACK AGENT ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TIER 1: FOUNDATION          TIER 2: CORE OPERATIONS                   │
│  ├── RFP Agent               ├── Brief Agent                           │
│  ├── Content Agent           ├── Workflow Agent                        │
│  └── Commercial Agent        └── Resource Agent                        │
│                                                                         │
│  TIER 3: SPECIALIZED         TIER 4: EXTENDED                          │
│  ├── Studio Agents           ├── Entities Manager                      │
│  ├── Media Agents            ├── Scheduler Agent                       │
│  ├── Social Agents           └── Contract Agent                        │
│  └── Analytics Agents                                                   │
│                                                                         │
│  TIER 5: ENGAGEMENT          PLATFORM LIFECYCLE                        │
│  ├── Publisher Agent         ├── Instance Onboarding                   │
│  ├── Reply Agent             ├── Instance Analytics                    │
│  └── Channel Agent           └── Instance Success                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Overview

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ERP INSTANCES                                   │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐                            │
│    │ Tenant A │  │ Tenant B │  │ Tenant C │                            │
│    └────┬─────┘  └────┬─────┘  └────┬─────┘                            │
└─────────┼─────────────┼─────────────┼───────────────────────────────────┘
          │             │             │
          └─────────────┼─────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT SERVICE (Standalone)                           │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │                         REST API Layer                              ││
│  │  POST /api/v1/agent/execute   - Execute agent task                 ││
│  │  GET  /api/v1/agent/status    - Poll task status                   ││
│  │  GET  /api/v1/agents          - List available agents              ││
│  └──────────────────────────┬─────────────────────────────────────────┘│
│                              ▼                                          │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │                      Claude Agent SDK                               ││
│  │  ┌──────────────────────────────────────────────────────────────┐  ││
│  │  │                  Agent Loop (Orchestrator)                    │  ││
│  │  │     Think → Tool Selection → Execute → Feedback → Iterate    │  ││
│  │  └──────────────────────────────────────────────────────────────┘  ││
│  │                              │                                      ││
│  │  ┌──────────────────────────▼───────────────────────────────────┐  ││
│  │  │                   49+ Specialized Agents                      │  ││
│  │  │        BaseAgent → YourAgent(tools, system_prompt)           │  ││
│  │  └──────────────────────────────────────────────────────────────┘  ││
│  └────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
User Request
     │
     ▼
┌──────────────┐
│ API Gateway  │  Authentication, rate limiting, routing
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Agent Router │  Select appropriate agent based on request
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  BaseAgent   │  Core agent loop: Think → Act → Create
│              │
│  ┌─────────┐ │
│  │ Claude  │◄├──── Model inference
│  └────┬────┘ │
│       │      │
│       ▼      │
│  ┌─────────┐ │
│  │  Tools  │◄├──── Tool execution
│  └────┬────┘ │
│       │      │
└───────┼──────┘
        │
        ▼
┌──────────────┐
│   ERP API    │  Database operations, external integrations
└──────────────┘
```

### 2.3 Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **BaseAgent** | Abstract base class for all agents | `src/agents/base.py` |
| **AgentContext** | Request context (tenant, user, metadata) | `src/agents/base.py` |
| **AgentResult** | Response structure (output, artifacts) | `src/agents/base.py` |
| **Tool Definitions** | JSON Schema for tool inputs | Agent `_define_tools()` |
| **System Prompt** | Agent personality and behavior | Agent `system_prompt` property |

---

## 3. Core Paradigm: Think → Act → Create

Every SpokeStack agent follows this paradigm:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       THINK → ACT → CREATE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ THINK                                                            │   │
│  │ ├── Analyze the context (brief, client, project)                │   │
│  │ ├── Understand requirements and constraints                      │   │
│  │ ├── Plan the approach (which tools, what order)                 │   │
│  │ └── Consider specializations (vertical, region, language)       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                  │                                      │
│                                  ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ ACT                                                              │   │
│  │ ├── Execute tools (API calls, data queries, validations)       │   │
│  │ ├── Iterate based on feedback                                   │   │
│  │ ├── Handle errors gracefully                                    │   │
│  │ └── Gather all necessary information                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                  │                                      │
│                                  ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ CREATE                                                           │   │
│  │ ├── Synthesize thinking + action into deliverables              │   │
│  │ ├── Generate documents, assets, recommendations                 │   │
│  │ ├── Format output appropriately                                 │   │
│  │ └── Provide actionable next steps                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### How It Works in Code

```python
async def run(self, context: AgentContext) -> AgentResult:
    """
    Execute the agent loop: Think → Act → Create
    """
    messages = [{"role": "user", "content": context.task}]

    while True:
        # THINK: Get Claude's response
        response = await self.client.messages.create(
            model=self.model,
            system=self._build_system_prompt(context),
            tools=self.tools,
            messages=messages,
        )

        # Check if we're done (no more tool calls)
        if response.stop_reason == "end_turn":
            # CREATE: Extract final output
            final_text = self._extract_text(response)
            break

        # ACT: Process tool calls
        for block in response.content:
            if block.type == "tool_use":
                result = await self._execute_tool(block.name, block.input)
                # Feed result back into conversation
```

---

## 4. Quick Start: Building Your First Agent

### 4.1 Minimal Agent Template

Create a new file `src/agents/my_agent.py`:

```python
from typing import Any
import httpx
from .base import BaseAgent


class MyAgent(BaseAgent):
    """
    Description of what your agent does.
    """

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=30.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "my_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert in [domain].

Your role is to [primary purpose].

## Capabilities
- Capability 1
- Capability 2

## Approach
- Be [adjective]
- Always [behavior]
"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "my_tool",
                "description": "What this tool does",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Description of param1",
                        },
                    },
                    "required": ["param1"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "my_tool":
            return await self._my_tool_impl(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    async def _my_tool_impl(self, params: dict) -> dict:
        # Your implementation here
        return {"result": "success"}

    async def close(self):
        await self.http_client.aclose()
```

### 4.2 Register Your Agent

Update `src/agents/__init__.py`:

```python
from .my_agent import MyAgent

__all__ = [
    # ... existing agents
    "MyAgent",
]
```

### 4.3 Add API Route (Optional)

If you need a dedicated endpoint:

```python
# In src/api/routes.py
@router.post("/agent/my-agent/execute")
async def execute_my_agent(request: AgentRequest):
    agent = MyAgent(
        client=anthropic_client,
        model=settings.model,
        erp_base_url=settings.erp_base_url,
        erp_api_key=settings.erp_api_key,
    )
    try:
        result = await agent.run(AgentContext(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            task=request.task,
            metadata=request.metadata,
        ))
        return result
    finally:
        await agent.close()
```

---

## 5. Agent Anatomy

### 5.1 Four Essential Components

Every agent consists of four key components:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AGENT COMPONENTS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. IDENTITY                                                            │
│     @property                                                           │
│     def name(self) -> str:                                              │
│         return "my_agent"                                               │
│                                                                         │
│  2. SYSTEM PROMPT                                                       │
│     @property                                                           │
│     def system_prompt(self) -> str:                                     │
│         return "You are an expert..."                                   │
│                                                                         │
│  3. TOOL DEFINITIONS                                                    │
│     def _define_tools(self) -> list[dict]:                             │
│         return [{"name": "...", "input_schema": {...}}]                │
│                                                                         │
│  4. TOOL EXECUTION                                                      │
│     async def _execute_tool(self, name, input) -> Any:                 │
│         if name == "my_tool": return await self._impl(input)           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 BaseAgent Class Reference

```python
class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, client: AsyncAnthropic, model: str):
        self.client = client
        self.model = model
        self.tools = self._define_tools()

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt defining agent behavior."""
        pass

    @abstractmethod
    def _define_tools(self) -> list[dict]:
        """Define tools available to this agent."""
        pass

    @abstractmethod
    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute a tool and return result."""
        pass

    async def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent loop."""
        # Implementation in base.py

    async def stream(self, context: AgentContext) -> AsyncIterator[str]:
        """Stream agent responses."""
        # Implementation in base.py
```

### 5.3 Context and Results

```python
@dataclass
class AgentContext:
    """Context passed to agent during execution."""
    tenant_id: str          # Multi-tenant isolation
    user_id: str            # User making request
    task: str               # The actual task/prompt
    metadata: dict = field(default_factory=dict)  # Additional context


@dataclass
class AgentResult:
    """Result from agent execution."""
    success: bool           # Whether task completed successfully
    output: str             # Text output from agent
    artifacts: list[dict]   # Generated documents, assets, etc.
    metadata: dict          # Additional response metadata
```

---

## 6. System Prompt Design

### 6.1 System Prompt Structure

A well-designed system prompt has these sections:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     SYSTEM PROMPT STRUCTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. ROLE DEFINITION                                                     │
│     "You are an expert [role] specializing in [domain]."               │
│                                                                         │
│  2. PRIMARY PURPOSE                                                     │
│     "Your role is to [main objective]."                                │
│                                                                         │
│  3. CAPABILITIES LIST                                                   │
│     ## Capabilities                                                     │
│     - Capability 1: Description                                         │
│     - Capability 2: Description                                         │
│                                                                         │
│  4. KNOWLEDGE AREAS                                                     │
│     ## Domain Knowledge                                                 │
│     - Area 1                                                            │
│     - Area 2                                                            │
│                                                                         │
│  5. BEHAVIORAL GUIDELINES                                               │
│     ## Approach                                                         │
│     - Be [adjective]                                                    │
│     - Always [action]                                                   │
│     - Never [action]                                                    │
│                                                                         │
│  6. OUTPUT EXPECTATIONS                                                 │
│     ## Output Format                                                    │
│     - Format specifications                                             │
│     - Quality standards                                                 │
│                                                                         │
│  7. EXAMPLES (Optional)                                                 │
│     ## Examples                                                         │
│     - Example request → Example response                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Example: RFP Agent System Prompt

```python
@property
def system_prompt(self) -> str:
    return """You are an expert RFP (Request for Proposal) analyst and response drafter.

Your role is to help agencies win new business by:
1. Thoroughly analyzing RFP documents to understand client needs
2. Identifying key requirements, evaluation criteria, and deadlines
3. Finding relevant past work and case studies from the ERP
4. Drafting compelling, tailored proposal responses
5. Highlighting competitive differentiators

## Capabilities
- Parse and analyze RFP documents of any format
- Extract mandatory and optional requirements
- Match requirements to team capabilities and past work
- Generate persuasive proposal sections
- Calculate effort estimates and resource needs

## Domain Knowledge
- RFP/RFI/RFQ processes across industries
- Proposal best practices (executive summary, pricing, team bios)
- Evaluation criteria interpretation
- Competitive positioning strategies

## Approach
When analyzing an RFP:
- Extract ALL requirements (mandatory and optional)
- Note evaluation criteria and weightings
- Identify submission requirements (format, deadline, contact)
- Flag any clarification questions needed

When drafting responses:
- Address each requirement explicitly
- Use concrete examples from past projects
- Quantify results where possible
- Match the client's language and priorities
- Keep tone professional but engaging

## Quality Standards
- Never fabricate case studies or results
- Always cite specific project references from the database
- Maintain brand voice consistency
- Flag uncertainties rather than making assumptions"""
```

### 6.3 Context Injection

The base agent automatically injects context into the system prompt:

```python
def _build_system_prompt(self, context: AgentContext) -> str:
    return f"""{self.system_prompt}

## Context
- Tenant ID: {context.tenant_id}
- User ID: {context.user_id}
- Additional context: {context.metadata}

## Approach
Follow the Think → Act → Create paradigm:
1. THINK: Analyze the request, understand requirements
2. ACT: Use tools to gather data, validate, iterate
3. CREATE: Synthesize findings into actionable output
"""
```

### 6.4 Dynamic System Prompts

For specialized agents, build prompts dynamically:

```python
@property
def system_prompt(self) -> str:
    base = """You are an expert copywriter."""

    # Add vertical-specific knowledge
    if self.vertical == "beauty":
        base += """

## Beauty Industry Expertise
- Understand ingredient trends and claims regulations
- Know key beauty influencers and brand positioning
- Apply sensory-rich, aspirational language
- Consider seasonal campaigns and product launches"""

    elif self.vertical == "technology":
        base += """

## Technology Industry Expertise
- Understand technical specifications and benefits
- Translate complex features into user value
- Balance innovation messaging with reliability
- Consider B2B vs B2C audience differences"""

    # Add language-specific guidance
    if self.language == "ar":
        base += """

## Arabic Language Guidelines
- Use Modern Standard Arabic for formal content
- Apply RTL formatting considerations
- Consider cultural context for GCC regions
- Maintain appropriate honorifics and formality"""

    return base
```

---

## 7. Tool Definition & Implementation

### 7.1 Tool Definition Schema

Tools are defined using JSON Schema:

```python
def _define_tools(self) -> list[dict]:
    return [
        {
            "name": "tool_name",           # Unique identifier
            "description": "...",           # What the tool does (Claude reads this!)
            "input_schema": {
                "type": "object",
                "properties": {
                    "required_param": {
                        "type": "string",
                        "description": "Description for Claude",
                    },
                    "optional_param": {
                        "type": "integer",
                        "description": "Description",
                        "default": 10,
                    },
                    "enum_param": {
                        "type": "string",
                        "enum": ["option1", "option2", "option3"],
                        "description": "Choose one of the options",
                    },
                    "array_param": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of items",
                    },
                    "object_param": {
                        "type": "object",
                        "properties": {
                            "nested_field": {"type": "string"},
                        },
                        "description": "Nested object",
                    },
                },
                "required": ["required_param"],  # Required parameters
            },
        },
    ]
```

### 7.2 Tool Description Best Practices

The description is critical—it's how Claude decides when and how to use the tool:

```python
# ❌ Bad: Vague description
{
    "name": "search",
    "description": "Search for things",
    ...
}

# ✅ Good: Specific, actionable description
{
    "name": "query_past_projects",
    "description": "Search ERP for past projects relevant to an RFP. "
                   "Use this tool to find case studies, similar work, and "
                   "proof points that match client requirements. Returns "
                   "project summaries with outcomes and team involved.",
    ...
}
```

### 7.3 Tool Implementation Pattern

```python
async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
    """Execute tool against ERP API."""
    try:
        if tool_name == "query_past_projects":
            return await self._query_past_projects(tool_input)
        elif tool_name == "get_team_capabilities":
            return await self._get_team_capabilities(tool_input)
        elif tool_name == "create_proposal_draft":
            return await self._create_proposal_draft(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except httpx.TimeoutException:
        return {"error": "Request timed out", "retry": True}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error: {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


async def _query_past_projects(self, params: dict) -> dict:
    """Query ERP for past projects."""
    response = await self.http_client.get(
        "/api/v1/projects/search",
        params={
            "industry": params.get("industry"),
            "service_type": params.get("service_type"),
            "keywords": ",".join(params.get("keywords", [])),
            "limit": params.get("limit", 5),
        },
    )

    if response.status_code == 200:
        return response.json()

    # Return structured error
    return {
        "projects": [],
        "note": "No matching projects found",
        "suggestion": "Try broader search terms",
    }
```

### 7.4 Tool Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **Query Tools** | Fetch data from ERP/external APIs | `query_projects`, `get_client_info` |
| **Create Tools** | Generate new records | `create_draft`, `save_document` |
| **Update Tools** | Modify existing records | `update_status`, `add_comment` |
| **Analyze Tools** | Process and interpret data | `analyze_document`, `calculate_metrics` |
| **Validate Tools** | Check compliance/rules | `validate_brand`, `check_compliance` |
| **Integration Tools** | Connect external services | `send_email`, `post_to_slack` |

### 7.5 Complex Tool Example

```python
{
    "name": "generate_sample_instance",
    "description": "Create a sample instance with realistic dummy data for demos. "
                   "Use this to help prospects visualize what the ERP would look "
                   "like for their business.",
    "input_schema": {
        "type": "object",
        "properties": {
            "instance_id": {
                "type": "string",
                "description": "Instance ID to populate",
            },
            "company_profile": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Fictional company name",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["agency", "studio", "in_house", "freelancer"],
                    },
                    "industry_focus": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Industries: technology, retail, healthcare...",
                    },
                    "size": {
                        "type": "string",
                        "enum": ["solo", "small", "medium", "large", "enterprise"],
                    },
                },
                "description": "Profile of the fictional company",
            },
            "data_to_generate": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["clients", "projects", "briefs", "team", "content"],
                },
                "description": "Types of sample data to generate",
            },
            "data_volume": {
                "type": "string",
                "enum": ["minimal", "moderate", "comprehensive"],
                "description": "How much sample data to create",
                "default": "moderate",
            },
        },
        "required": ["instance_id", "company_profile"],
    },
}
```

---

## 8. Agent Specialization

### 8.1 Specialization Dimensions

Agents can be specialized across multiple dimensions:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     SPECIALIZATION MATRIX                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  VERTICAL (Industry)         REGION (Geography)                        │
│  ├── Beauty                  ├── UAE, KSA (GCC)                        │
│  ├── Fashion                 ├── MENA                                  │
│  ├── Food & Beverage         ├── Europe                                │
│  ├── Technology              ├── Americas                              │
│  ├── Finance                 └── APAC                                  │
│  ├── Healthcare                                                        │
│  └── Retail                  CLIENT                                    │
│                              ├── Brand voice                           │
│  LANGUAGE                    ├── Past work                             │
│  ├── English (en)            ├── Preferences                           │
│  ├── Arabic (ar)             └── Custom rules                          │
│  ├── French (fr)                                                       │
│  └── German (de)                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Implementing Specializations

```python
class InfluencerAgent(BaseAgent):
    """
    Influencer discovery and campaign agent.
    Specializable by vertical, region, and language.
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        # Specialization options
        vertical: str = None,      # e.g., "beauty", "fashion", "tech"
        region: str = None,        # e.g., "uae", "ksa", "us"
        language: str = "en",      # e.g., "en", "ar"
        client_id: str = None,     # For client-specific rules
    ):
        self.vertical = vertical
        self.region = region
        self.language = language
        self.client_id = client_id

        self.http_client = httpx.AsyncClient(...)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        parts = ["influencer_agent"]
        if self.vertical:
            parts.append(self.vertical)
        if self.region:
            parts.append(self.region)
        return "_".join(parts)

    @property
    def system_prompt(self) -> str:
        base = "You are an expert influencer marketing specialist."

        # Vertical expertise
        vertical_knowledge = {
            "beauty": """
## Beauty Industry Expertise
- Know top beauty influencers by tier (mega, macro, micro, nano)
- Understand ingredient trends (clean beauty, K-beauty, sustainable)
- Track beauty brand partnerships and exclusivity
- Consider seasonal campaigns (summer skincare, holiday collections)""",

            "fashion": """
## Fashion Industry Expertise
- Know fashion influencers by style (streetwear, luxury, sustainable)
- Track fashion week coverage and brand relationships
- Understand sizing and fit considerations for campaigns
- Consider seasonal trends and collection launches""",

            "food": """
## Food & Beverage Expertise
- Know food influencers by cuisine and content type
- Understand dietary trends (vegan, keto, local sourcing)
- Track restaurant and brand partnerships
- Consider cultural food preferences by region""",
        }

        if self.vertical and self.vertical in vertical_knowledge:
            base += vertical_knowledge[self.vertical]

        # Regional expertise
        if self.region in ["uae", "ksa", "gcc"]:
            base += """

## GCC Region Expertise
- Know local regulations for influencer disclosure
- Understand Ramadan and cultural calendar impacts
- Track top GCC influencers and engagement rates
- Consider Arabic/English content mix preferences"""

        # Language considerations
        if self.language == "ar":
            base += """

## Arabic Content Guidelines
- Generate culturally appropriate messaging
- Use formal/informal register appropriately
- Consider dialect preferences (Gulf, Levantine, Egyptian)"""

        return base
```

### 8.3 Usage Patterns

```python
# General influencer agent
agent = InfluencerAgent(client, model, erp_url, erp_key)

# Beauty-focused for UAE market
agent = InfluencerAgent(
    client, model, erp_url, erp_key,
    vertical="beauty",
    region="uae",
    language="ar",
)

# Tech-focused for US market
agent = InfluencerAgent(
    client, model, erp_url, erp_key,
    vertical="technology",
    region="us",
    language="en",
)

# Client-specific agent
agent = InfluencerAgent(
    client, model, erp_url, erp_key,
    vertical="fashion",
    region="eu",
    client_id="luxury_brand_123",  # Loads client-specific rules
)
```

### 8.4 Specialization Reference

| Vertical | Key Considerations |
|----------|-------------------|
| **Beauty** | Ingredient claims, regulations, influencer tiers, seasonal campaigns |
| **Fashion** | Style categories, fashion week, sizing, sustainability |
| **Food** | Dietary trends, cuisine types, restaurant partnerships |
| **Technology** | Technical accuracy, B2B vs B2C, product launch cycles |
| **Finance** | Compliance requirements, regulatory language, trust building |
| **Healthcare** | Medical accuracy, regulatory compliance, sensitivity |

| Region | Key Considerations |
|--------|-------------------|
| **GCC** | Arabic content, Ramadan calendar, local regulations |
| **MENA** | Cultural sensitivity, language dialects, regional influencers |
| **US** | FTC disclosure requirements, platform preferences |
| **EU** | GDPR, multi-language, cultural diversity |
| **APAC** | Platform differences (WeChat, LINE), cultural nuances |

---

## 9. Instance-Level Deployment & Scaling

This section addresses the critical question: **How do agents scale across SpokeStack instances while allowing instance-specific customization?**

### 9.1 The Scaling Challenge

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE SCALING CHALLENGE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GLOBAL LEVEL (SpokeStack Platform)                                        │
│  ├── Core agents maintained by SpokeStack team                             │
│  ├── Bug fixes and improvements pushed to all instances                    │
│  └── New capabilities added without breaking customizations                │
│                                                                             │
│  INSTANCE LEVEL (Per Tenant)                                               │
│  ├── Custom skills added for specific workflows                            │
│  ├── Client-specific rules and preferences                                 │
│  └── Industry/vertical specializations                                     │
│                                                                             │
│  QUESTION: How do we update globally WITHOUT breaking instance configs?    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Three-Layer Architecture

SpokeStack uses a **three-layer inheritance model** that separates concerns:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THREE-LAYER AGENT ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 1: CORE AGENTS (Global - Immutable by Instances)                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Base agent classes (Python code)                                  │   │
│  │  • Core tools and capabilities                                       │   │
│  │  • Default system prompts                                            │   │
│  │  • Deployed via container updates                                    │   │
│  │  • Version controlled, tested, stable                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼ inherits                               │
│  LAYER 2: INSTANCE CONFIGURATION (Per-Tenant - Database)                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Enabled/disabled agents per instance                              │   │
│  │  • Enabled/disabled skills per agent                                 │   │
│  │  • Instance-level prompt extensions                                  │   │
│  │  • Custom tool configurations                                        │   │
│  │  • Stored in tenant database, hot-reloadable                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼ extends                                │
│  LAYER 3: SKILL EXTENSIONS (Instance-Defined - Database/Code)              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Custom skills (new tools) added by instance                       │   │
│  │  • Client-specific integrations                                      │   │
│  │  • Webhook-based tool execution                                      │   │
│  │  • Can be added without platform deployment                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.3 Data Model for Instance Configuration

```python
# Database schema for instance-level agent configuration

class InstanceAgentConfig(Base):
    """Per-instance agent configuration stored in database."""
    __tablename__ = "instance_agent_configs"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"), nullable=False)
    agent_type = Column(String, nullable=False)  # e.g., "rfp", "copy", "influencer"

    # Enable/disable
    enabled = Column(Boolean, default=True)

    # Prompt extensions (appended to base system prompt)
    prompt_extension = Column(Text, nullable=True)

    # Specialization overrides
    default_vertical = Column(String, nullable=True)
    default_region = Column(String, nullable=True)
    default_language = Column(String, default="en")

    # Tool access control
    disabled_tools = Column(ARRAY(String), default=[])  # Tools to hide

    # Skill extensions (references to InstanceSkill records)
    skills = relationship("InstanceSkill", back_populates="agent_config")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class InstanceSkill(Base):
    """Custom skills added at the instance level."""
    __tablename__ = "instance_skills"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"), nullable=False)
    agent_config_id = Column(UUID, ForeignKey("instance_agent_configs.id"))

    # Skill definition
    name = Column(String, nullable=False)  # e.g., "query_custom_crm"
    description = Column(Text, nullable=False)  # For Claude to understand
    input_schema = Column(JSONB, nullable=False)  # JSON Schema

    # Execution method
    execution_type = Column(String, nullable=False)  # "webhook", "internal", "script"
    webhook_url = Column(String, nullable=True)  # For webhook execution
    webhook_auth = Column(JSONB, nullable=True)  # Encrypted auth config
    internal_handler = Column(String, nullable=True)  # For internal execution

    # Access control
    enabled = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)

    # Metadata
    created_by = Column(UUID, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    agent_config = relationship("InstanceAgentConfig", back_populates="skills")
```

### 9.4 Runtime Agent Assembly

When an agent is invoked, it's **assembled at runtime** from all three layers:

```python
class AgentFactory:
    """Factory that assembles agents with instance-specific configuration."""

    def __init__(self, db: AsyncSession, skill_executor: SkillExecutor):
        self.db = db
        self.skill_executor = skill_executor

    async def create_agent(
        self,
        agent_type: str,
        instance_id: str,
        client: AsyncAnthropic,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
    ) -> BaseAgent:
        """
        Assemble an agent with instance-specific configuration.

        1. Load base agent class (Layer 1)
        2. Load instance config from database (Layer 2)
        3. Load instance skills (Layer 3)
        4. Return configured agent
        """
        # Layer 1: Get base agent class
        agent_class = self._get_agent_class(agent_type)

        # Layer 2: Load instance configuration
        config = await self._load_instance_config(instance_id, agent_type)

        # Layer 3: Load instance skills
        skills = await self._load_instance_skills(instance_id, agent_type)

        # Create agent with all layers
        agent = agent_class(
            client=client,
            model=model,
            erp_base_url=erp_base_url,
            erp_api_key=erp_api_key,
            # Pass instance configuration
            instance_config=config,
            instance_skills=skills,
            skill_executor=self.skill_executor,
        )

        return agent

    def _get_agent_class(self, agent_type: str) -> type[BaseAgent]:
        """Map agent type to class (Layer 1)."""
        AGENT_REGISTRY = {
            "rfp": RFPAgent,
            "copy": CopyAgent,
            "influencer": InfluencerAgent,
            "brief": BriefAgent,
            # ... all agents
        }
        return AGENT_REGISTRY[agent_type]

    async def _load_instance_config(
        self, instance_id: str, agent_type: str
    ) -> InstanceAgentConfig | None:
        """Load instance config from database (Layer 2)."""
        result = await self.db.execute(
            select(InstanceAgentConfig).where(
                InstanceAgentConfig.instance_id == instance_id,
                InstanceAgentConfig.agent_type == agent_type,
            )
        )
        return result.scalar_one_or_none()

    async def _load_instance_skills(
        self, instance_id: str, agent_type: str
    ) -> list[InstanceSkill]:
        """Load instance skills from database (Layer 3)."""
        result = await self.db.execute(
            select(InstanceSkill)
            .join(InstanceAgentConfig)
            .where(
                InstanceAgentConfig.instance_id == instance_id,
                InstanceAgentConfig.agent_type == agent_type,
                InstanceSkill.enabled == True,
            )
        )
        return result.scalars().all()
```

### 9.5 Skill Extension System

Skills are **instance-defined tools** that extend agent capabilities without modifying core code:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SKILL EXTENSION SYSTEM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SKILL TYPES:                                                               │
│                                                                             │
│  1. WEBHOOK SKILLS                                                          │
│     ├── Tool calls external HTTP endpoint                                   │
│     ├── Instance provides URL + auth                                        │
│     ├── Response mapped back to agent                                       │
│     └── Example: Query custom CRM, trigger Zapier workflow                  │
│                                                                             │
│  2. INTERNAL SKILLS                                                         │
│     ├── Tool calls registered internal handler                              │
│     ├── Runs within agent service                                           │
│     ├── Access to ERP data                                                  │
│     └── Example: Custom report generator, specialized analyzer              │
│                                                                             │
│  3. SCRIPT SKILLS (Future)                                                  │
│     ├── Sandboxed code execution                                            │
│     ├── Instance uploads transformation logic                               │
│     └── Example: Custom data transformations                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Webhook Skill Example

```python
# Instance adds this skill via API or UI

skill_definition = {
    "name": "query_hubspot_deals",
    "description": "Query HubSpot CRM for deal information. Use this when "
                   "the user asks about sales pipeline, deal status, or "
                   "revenue projections.",
    "input_schema": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["open", "won", "lost", "all"],
                "description": "Filter by deal status",
            },
            "min_value": {
                "type": "number",
                "description": "Minimum deal value",
            },
            "owner_email": {
                "type": "string",
                "description": "Filter by deal owner email",
            },
        },
    },
    "execution_type": "webhook",
    "webhook_url": "https://instance-api.example.com/hubspot/deals",
    "webhook_auth": {
        "type": "bearer",
        "token_env": "HUBSPOT_INTEGRATION_TOKEN",  # Stored encrypted
    },
}
```

#### Skill Executor

```python
class SkillExecutor:
    """Executes instance-defined skills."""

    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def execute(
        self,
        skill: InstanceSkill,
        input_data: dict,
        context: AgentContext,
    ) -> dict:
        """Execute a skill based on its type."""

        if skill.execution_type == "webhook":
            return await self._execute_webhook(skill, input_data, context)
        elif skill.execution_type == "internal":
            return await self._execute_internal(skill, input_data, context)
        else:
            return {"error": f"Unknown execution type: {skill.execution_type}"}

    async def _execute_webhook(
        self,
        skill: InstanceSkill,
        input_data: dict,
        context: AgentContext,
    ) -> dict:
        """Execute webhook-based skill."""
        headers = {"Content-Type": "application/json"}

        # Add authentication
        if skill.webhook_auth:
            auth_type = skill.webhook_auth.get("type")
            if auth_type == "bearer":
                token = await self._get_secret(skill.webhook_auth["token_env"])
                headers["Authorization"] = f"Bearer {token}"
            elif auth_type == "api_key":
                headers[skill.webhook_auth["header"]] = await self._get_secret(
                    skill.webhook_auth["key_env"]
                )

        try:
            response = await self.http_client.post(
                skill.webhook_url,
                json={
                    "input": input_data,
                    "context": {
                        "instance_id": context.tenant_id,
                        "user_id": context.user_id,
                    },
                },
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            return {"error": "Skill webhook timed out", "retry": True}
        except httpx.HTTPStatusError as e:
            return {"error": f"Skill webhook error: {e.response.status_code}"}
```

### 9.6 Agent with Instance Configuration

Here's how a base agent incorporates instance configuration:

```python
class BaseAgent(ABC):
    """Base agent with instance configuration support."""

    def __init__(
        self,
        client: AsyncAnthropic,
        model: str,
        # Instance configuration (Layer 2 & 3)
        instance_config: InstanceAgentConfig | None = None,
        instance_skills: list[InstanceSkill] | None = None,
        skill_executor: SkillExecutor | None = None,
    ):
        self.client = client
        self.model = model
        self.instance_config = instance_config
        self.instance_skills = instance_skills or []
        self.skill_executor = skill_executor

        # Build final tool list (core + instance skills)
        self.tools = self._build_tools()

    def _build_tools(self) -> list[dict]:
        """Assemble tools from core + instance skills."""
        # Start with core tools
        tools = self._define_tools()

        # Remove disabled tools (from instance config)
        if self.instance_config and self.instance_config.disabled_tools:
            tools = [
                t for t in tools
                if t["name"] not in self.instance_config.disabled_tools
            ]

        # Add instance skills as tools
        for skill in self.instance_skills:
            tools.append({
                "name": skill.name,
                "description": skill.description,
                "input_schema": skill.input_schema,
                "_is_instance_skill": True,  # Internal marker
                "_skill_id": str(skill.id),
            })

        return tools

    @property
    def system_prompt(self) -> str:
        """Build system prompt with instance extensions."""
        base_prompt = self._base_system_prompt()

        # Add instance prompt extension
        if self.instance_config and self.instance_config.prompt_extension:
            base_prompt += f"\n\n## Instance-Specific Instructions\n\n"
            base_prompt += self.instance_config.prompt_extension

        return base_prompt

    @abstractmethod
    def _base_system_prompt(self) -> str:
        """Core system prompt (Layer 1)."""
        pass

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool - core or instance skill."""
        # Check if this is an instance skill
        for skill in self.instance_skills:
            if skill.name == tool_name:
                return await self.skill_executor.execute(
                    skill, tool_input, self.current_context
                )

        # Otherwise execute core tool
        return await self._execute_core_tool(tool_name, tool_input)

    @abstractmethod
    async def _execute_core_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute core tool (Layer 1)."""
        pass
```

### 9.7 Update Propagation Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        UPDATE PROPAGATION MODEL                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GLOBAL UPDATES (Layer 1)                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. SpokeStack team updates core agent code                          │   │
│  │  2. New container image built and tested                             │   │
│  │  3. Rolling deployment to all instances                              │   │
│  │  4. Instance configs (Layer 2) preserved - stored in database       │   │
│  │  5. Instance skills (Layer 3) preserved - stored in database        │   │
│  │                                                                       │   │
│  │  Result: All instances get improvements, customizations intact       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  INSTANCE UPDATES (Layer 2 & 3)                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. Instance admin updates config via API/UI                         │   │
│  │  2. Changes saved to instance database                               │   │
│  │  3. Next agent invocation picks up new config (hot reload)          │   │
│  │  4. No platform deployment required                                  │   │
│  │                                                                       │   │
│  │  Result: Instance customization without affecting other instances    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  CONFLICT RESOLUTION                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Instance config EXTENDS, never replaces core behavior            │   │
│  │  • Disabled tools respected (instance can hide, not add core tools) │   │
│  │  • Prompt extensions appended, not replaced                         │   │
│  │  • Skill names must not conflict with core tool names               │   │
│  │  • Version compatibility checked on deployment                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.8 Instance Configuration API

```python
# API endpoints for instance configuration

@router.get("/api/v1/instance/{instance_id}/agents")
async def list_agent_configs(instance_id: str):
    """List all agent configurations for an instance."""
    return await agent_config_service.list_configs(instance_id)


@router.put("/api/v1/instance/{instance_id}/agents/{agent_type}")
async def update_agent_config(
    instance_id: str,
    agent_type: str,
    config: AgentConfigUpdate,
):
    """
    Update agent configuration for an instance.

    Example:
    {
        "enabled": true,
        "prompt_extension": "Always respond in formal British English.",
        "default_vertical": "luxury_fashion",
        "default_region": "eu",
        "disabled_tools": ["generate_budget"]
    }
    """
    return await agent_config_service.update_config(
        instance_id, agent_type, config
    )


@router.post("/api/v1/instance/{instance_id}/agents/{agent_type}/skills")
async def add_skill(
    instance_id: str,
    agent_type: str,
    skill: SkillCreate,
):
    """
    Add a custom skill to an agent for this instance.

    Example:
    {
        "name": "query_salesforce",
        "description": "Query Salesforce for opportunity data...",
        "input_schema": {...},
        "execution_type": "webhook",
        "webhook_url": "https://...",
        "webhook_auth": {"type": "bearer", "token_env": "SF_TOKEN"}
    }
    """
    return await skill_service.create_skill(instance_id, agent_type, skill)


@router.delete("/api/v1/instance/{instance_id}/skills/{skill_id}")
async def remove_skill(instance_id: str, skill_id: str):
    """Remove a custom skill."""
    return await skill_service.delete_skill(instance_id, skill_id)


@router.post("/api/v1/instance/{instance_id}/skills/{skill_id}/test")
async def test_skill(instance_id: str, skill_id: str, test_input: dict):
    """Test a skill with sample input."""
    return await skill_service.test_skill(instance_id, skill_id, test_input)
```

### 9.9 Real-World Scaling Example

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REAL-WORLD SCALING EXAMPLE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SPOKESTACK PLATFORM                                                        │
│  └── Core RFP Agent (v2.3.1)                                               │
│      ├── Core tools: analyze_rfp, query_projects, draft_response (5 total)│
│      └── Base prompt: "You are an expert RFP analyst..."                   │
│                                                                             │
│  INSTANCE: Agency Alpha (Dubai)                                             │
│  └── RFP Agent Config:                                                      │
│      ├── enabled: true                                                      │
│      ├── default_region: "gcc"                                              │
│      ├── default_language: "ar"                                             │
│      ├── prompt_extension: "Focus on government RFP formats common in UAE" │
│      └── skills: []                                                         │
│                                                                             │
│  INSTANCE: Agency Beta (London)                                             │
│  └── RFP Agent Config:                                                      │
│      ├── enabled: true                                                      │
│      ├── default_region: "eu"                                               │
│      ├── prompt_extension: "Include GDPR compliance considerations"        │
│      ├── disabled_tools: ["query_competitors"]  # Disabled by choice       │
│      └── skills:                                                            │
│          └── "query_salesforce" (webhook to their Salesforce instance)     │
│                                                                             │
│  INSTANCE: Agency Gamma (New York)                                          │
│  └── RFP Agent Config:                                                      │
│      ├── enabled: true                                                      │
│      ├── default_vertical: "technology"                                     │
│      ├── prompt_extension: "Emphasize innovation and digital transformation"│
│      └── skills:                                                            │
│          ├── "query_hubspot" (webhook to HubSpot)                          │
│          └── "check_conflicts" (internal - checks for client conflicts)    │
│                                                                             │
│  WHEN SPOKESTACK UPDATES RFP AGENT TO v2.4.0:                              │
│  ├── New core tool added: "estimate_timeline"                              │
│  ├── Bug fix in analyze_rfp                                                │
│  ├── Deploy new container                                                   │
│  └── All instances automatically get update + keep their customizations    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.10 Client-Specific Agent Rules

For deeper client-specific behavior within an instance:

```python
class ClientRules(Base):
    """Client-specific rules within an instance."""
    __tablename__ = "client_rules"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"))
    client_id = Column(UUID, ForeignKey("clients.id"))
    agent_type = Column(String)

    # Rules
    prompt_additions = Column(Text)  # Added to prompt when working on this client
    required_approvals = Column(ARRAY(String))  # Tools requiring approval
    data_restrictions = Column(JSONB)  # Fields to redact/hide

    # Preferences
    preferred_tone = Column(String)  # "formal", "casual", "technical"
    preferred_language = Column(String)
    brand_guidelines_doc_id = Column(UUID)  # Reference to uploaded guidelines


# In agent execution
async def _build_system_prompt(self, context: AgentContext) -> str:
    prompt = self.system_prompt

    # Add client-specific rules if client_id provided
    if context.metadata.get("client_id"):
        client_rules = await self._load_client_rules(
            context.tenant_id,
            context.metadata["client_id"],
        )
        if client_rules:
            prompt += f"\n\n## Client-Specific Requirements\n\n"
            prompt += client_rules.prompt_additions
            if client_rules.preferred_tone:
                prompt += f"\n\nTone: {client_rules.preferred_tone}"

    return prompt
```

### 9.11 Scaling Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SCALING ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    ┌──────────────────────────────────┐                    │
│                    │     SPOKESTACK PLATFORM          │                    │
│                    │  ┌────────────────────────────┐  │                    │
│                    │  │   Core Agent Images        │  │                    │
│                    │  │   (Container Registry)     │  │                    │
│                    │  │   v2.3.1, v2.4.0, etc.    │  │                    │
│                    │  └────────────────────────────┘  │                    │
│                    └──────────────────────────────────┘                    │
│                                    │                                        │
│           ┌────────────────────────┼────────────────────────┐              │
│           │                        │                        │              │
│           ▼                        ▼                        ▼              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │ Instance Alpha  │    │ Instance Beta   │    │ Instance Gamma  │        │
│  │ (Dubai)         │    │ (London)        │    │ (New York)      │        │
│  ├─────────────────┤    ├─────────────────┤    ├─────────────────┤        │
│  │ Agent Service   │    │ Agent Service   │    │ Agent Service   │        │
│  │ (same image)    │    │ (same image)    │    │ (same image)    │        │
│  ├─────────────────┤    ├─────────────────┤    ├─────────────────┤        │
│  │ Instance DB     │    │ Instance DB     │    │ Instance DB     │        │
│  │ ├─ Configs      │    │ ├─ Configs      │    │ ├─ Configs      │        │
│  │ ├─ Skills       │    │ ├─ Skills       │    │ ├─ Skills       │        │
│  │ └─ Client Rules │    │ └─ Client Rules │    │ └─ Client Rules │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│           │                        │                        │              │
│           ▼                        ▼                        ▼              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │ Skill Webhooks  │    │ Skill Webhooks  │    │ Skill Webhooks  │        │
│  │ (instance-own)  │    │ ├─ Salesforce   │    │ ├─ HubSpot      │        │
│  │                 │    │ └─ Custom APIs  │    │ └─ Slack        │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.12 Agent Version Control System

**Problem**: Global updates might break instance-specific optimizations.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE VERSION CONTROL PROBLEM                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SCENARIO: Media Buying Agent v2.3 → v2.4                                  │
│                                                                             │
│  Global Update (v2.4):                                                      │
│  ├── Optimized for: REACH campaigns                                        │
│  ├── New tool: audience_expansion                                          │
│  └── Changed: bid_strategy defaults to "maximize_reach"                    │
│                                                                             │
│  Instance: E-commerce Agency                                                │
│  ├── Optimized for: PERFORMANCE/ROAS campaigns                             │
│  ├── Custom skill: roas_optimizer (compensates for v2.3 blind spot)        │
│  └── Their clients expect: conversion-focused recommendations              │
│                                                                             │
│  RISK: v2.4 update could BREAK their optimized workflow!                   │
│  ├── roas_optimizer skill might conflict with new reach focus              │
│  ├── Bid strategy change affects all client campaigns                      │
│  └── Instance owner has no warning, no way to test first                   │
│                                                                             │
│  SOLUTION: Version Control + Sandbox + Notification System                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Version Control Principles

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VERSION CONTROL PRINCIPLES                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. INSTANCE OWNERS CONTROL THEIR UPGRADES                                 │
│     ├── Pin to specific version                                            │
│     ├── Choose update policy (auto, staged, manual)                        │
│     └── Roll back if needed                                                │
│                                                                             │
│  2. TRANSPARENCY BEFORE UPDATES                                            │
│     ├── What changed (tools, prompts, behavior)                            │
│     ├── Impact analysis on YOUR instance skills                            │
│     └── Recommendation (safe to update, review first, potential conflict)  │
│                                                                             │
│  3. TEST BEFORE DEPLOY                                                     │
│     ├── Sandbox environment with real instance data                        │
│     ├── Side-by-side comparison (current vs new)                           │
│     └── Approval workflow before promotion                                 │
│                                                                             │
│  4. PRESERVE WHAT WORKS                                                    │
│     ├── Instance skills that outperform global may be kept                 │
│     ├── Skill-to-core promotion path (good skills → platform features)    │
│     └── Version branches for different use cases                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.13 Version Data Model

```python
class AgentVersion(Base):
    """Tracks versions of core agents."""
    __tablename__ = "agent_versions"

    id = Column(UUID, primary_key=True)
    agent_type = Column(String, nullable=False)  # e.g., "media_buying"

    # Semantic versioning
    version = Column(String, nullable=False)  # e.g., "2.4.0"
    major = Column(Integer, nullable=False)
    minor = Column(Integer, nullable=False)
    patch = Column(Integer, nullable=False)

    # Version metadata
    release_date = Column(DateTime, nullable=False)
    release_notes = Column(Text)  # Markdown changelog
    breaking_changes = Column(Boolean, default=False)

    # What this version optimizes for (capability tags)
    optimization_tags = Column(ARRAY(String), default=[])
    # e.g., ["reach", "brand_awareness"] or ["performance", "roas", "conversions"]

    # Detailed changes
    changes = Column(JSONB, nullable=False)
    # Structure:
    # {
    #   "tools_added": ["audience_expansion"],
    #   "tools_removed": [],
    #   "tools_modified": ["bid_strategy"],
    #   "prompt_changes": ["Added reach optimization guidance"],
    #   "behavior_changes": ["Default bid strategy now maximize_reach"],
    #   "deprecations": []
    # }

    # Compatibility
    min_platform_version = Column(String)  # Minimum SpokeStack version
    deprecated = Column(Boolean, default=False)
    sunset_date = Column(DateTime, nullable=True)

    # Container reference
    container_image = Column(String)  # e.g., "spokestack/agents:media-buying-2.4.0"


class InstanceVersionConfig(Base):
    """Per-instance version control settings."""
    __tablename__ = "instance_version_configs"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"), nullable=False)
    agent_type = Column(String, nullable=False)

    # Version pinning
    pinned_version = Column(String, nullable=True)  # null = latest
    update_policy = Column(String, default="staged")
    # Policies: "auto" (immediate), "staged" (sandbox first), "manual" (explicit approval)

    # Current state
    current_version = Column(String, nullable=False)
    sandbox_version = Column(String, nullable=True)  # Version being tested

    # Preferences
    optimization_preference = Column(ARRAY(String), default=[])
    # e.g., ["performance", "roas"] - used for conflict detection

    # History
    version_history = Column(JSONB, default=[])
    # [{version, activated_at, activated_by, rollback_reason?}]

    # Notifications
    notify_on_updates = Column(Boolean, default=True)
    notify_contacts = Column(ARRAY(String), default=[])  # Email addresses


class VersionUpdateNotification(Base):
    """Notifications about available updates."""
    __tablename__ = "version_update_notifications"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"), nullable=False)
    agent_type = Column(String, nullable=False)

    # Update details
    from_version = Column(String, nullable=False)
    to_version = Column(String, nullable=False)

    # Analysis results
    impact_analysis = Column(JSONB)
    # {
    #   "skill_conflicts": [...],
    #   "optimization_mismatch": true/false,
    #   "recommendation": "safe" | "review" | "caution",
    #   "recommendation_reason": "...",
    #   "affected_skills": ["roas_optimizer"],
    # }

    # Status
    status = Column(String, default="pending")
    # "pending", "reviewed", "sandbox_testing", "approved", "rejected", "applied"

    reviewed_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
```

### 9.14 Update Notification & Impact Analysis

```python
class UpdateAnalyzer:
    """Analyzes impact of agent updates on instances."""

    async def analyze_update_impact(
        self,
        instance_id: str,
        agent_type: str,
        from_version: str,
        to_version: str,
    ) -> UpdateImpactReport:
        """
        Analyze how an update will affect this specific instance.
        """
        # Load instance configuration
        instance_config = await self._load_instance_config(instance_id, agent_type)
        instance_skills = await self._load_instance_skills(instance_id, agent_type)

        # Load version details
        from_ver = await self._load_version(agent_type, from_version)
        to_ver = await self._load_version(agent_type, to_version)

        # Analyze conflicts
        conflicts = []
        affected_skills = []

        # 1. Check optimization mismatch
        optimization_mismatch = self._check_optimization_mismatch(
            instance_config.optimization_preference,
            to_ver.optimization_tags,
        )

        # 2. Check skill conflicts with new/modified tools
        for skill in instance_skills:
            conflict = self._check_skill_conflict(skill, to_ver.changes)
            if conflict:
                conflicts.append(conflict)
                affected_skills.append(skill.name)

        # 3. Check for tool removals that skills depend on
        if to_ver.changes.get("tools_removed"):
            for skill in instance_skills:
                if self._skill_depends_on_tools(skill, to_ver.changes["tools_removed"]):
                    conflicts.append({
                        "type": "dependency_removed",
                        "skill": skill.name,
                        "removed_tools": to_ver.changes["tools_removed"],
                        "severity": "critical",
                    })

        # 4. Generate recommendation
        recommendation = self._generate_recommendation(
            conflicts,
            optimization_mismatch,
            to_ver.breaking_changes,
        )

        return UpdateImpactReport(
            instance_id=instance_id,
            agent_type=agent_type,
            from_version=from_version,
            to_version=to_version,
            skill_conflicts=conflicts,
            affected_skills=affected_skills,
            optimization_mismatch=optimization_mismatch,
            breaking_changes=to_ver.breaking_changes,
            recommendation=recommendation.level,  # "safe", "review", "caution"
            recommendation_reason=recommendation.reason,
            changes_summary=to_ver.changes,
            release_notes=to_ver.release_notes,
        )

    def _check_optimization_mismatch(
        self,
        instance_prefs: list[str],
        version_tags: list[str],
    ) -> bool:
        """
        Check if version optimization focus conflicts with instance preferences.
        """
        # Define conflicting optimization pairs
        CONFLICTS = {
            "reach": ["performance", "roas", "conversions"],
            "brand_awareness": ["direct_response", "conversions"],
            "performance": ["reach", "brand_awareness"],
        }

        for pref in instance_prefs:
            conflicting = CONFLICTS.get(pref, [])
            if any(tag in conflicting for tag in version_tags):
                return True
        return False

    def _check_skill_conflict(
        self,
        skill: InstanceSkill,
        changes: dict,
    ) -> dict | None:
        """
        Check if a skill conflicts with version changes.
        """
        conflicts = []

        # Check if skill name conflicts with new tool
        if skill.name in changes.get("tools_added", []):
            return {
                "type": "name_collision",
                "skill": skill.name,
                "reason": f"New core tool '{skill.name}' has same name as your skill",
                "severity": "critical",
                "suggestion": "Rename your skill or disable to use core version",
            }

        # Check if skill does same thing as modified tool
        modified_tools = changes.get("tools_modified", [])
        skill_purpose = self._extract_skill_purpose(skill.description)

        for tool in modified_tools:
            if self._purposes_overlap(skill_purpose, tool):
                return {
                    "type": "functionality_overlap",
                    "skill": skill.name,
                    "core_tool": tool,
                    "reason": f"Core tool '{tool}' was modified and may now cover what your skill does",
                    "severity": "review",
                    "suggestion": "Test if core tool now meets your needs",
                }

        # Check if behavior changes affect skill assumptions
        behavior_changes = changes.get("behavior_changes", [])
        for change in behavior_changes:
            if self._skill_assumes_old_behavior(skill, change):
                return {
                    "type": "behavior_assumption",
                    "skill": skill.name,
                    "change": change,
                    "reason": "Your skill may assume old behavior that has changed",
                    "severity": "review",
                    "suggestion": "Verify skill still works correctly with new behavior",
                }

        return None

    def _generate_recommendation(
        self,
        conflicts: list,
        optimization_mismatch: bool,
        breaking_changes: bool,
    ) -> Recommendation:
        """Generate update recommendation based on analysis."""

        critical_conflicts = [c for c in conflicts if c.get("severity") == "critical"]
        review_conflicts = [c for c in conflicts if c.get("severity") == "review"]

        if critical_conflicts:
            return Recommendation(
                level="caution",
                reason=f"{len(critical_conflicts)} critical conflict(s) detected. "
                       f"Review required before updating. Consider keeping current "
                       f"version or updating skills first.",
            )

        if optimization_mismatch:
            return Recommendation(
                level="caution",
                reason="This update optimizes for different goals than your instance. "
                       "Your performance-focused skills may conflict with new reach-focused behavior. "
                       "Recommend sandbox testing before deploying.",
            )

        if breaking_changes or review_conflicts:
            return Recommendation(
                level="review",
                reason=f"{'Breaking changes in this version. ' if breaking_changes else ''}"
                       f"{len(review_conflicts)} item(s) to review. "
                       f"Sandbox testing recommended.",
            )

        return Recommendation(
            level="safe",
            reason="No conflicts detected. Update should be safe to apply.",
        )
```

### 9.15 Notification Delivery

```python
class UpdateNotificationService:
    """Delivers update notifications to instance owners."""

    async def notify_available_update(
        self,
        instance_id: str,
        agent_type: str,
        to_version: str,
    ):
        """
        Notify instance about available update with impact analysis.
        """
        # Get instance config
        config = await self._get_version_config(instance_id, agent_type)
        if not config.notify_on_updates:
            return

        # Run impact analysis
        impact = await self.analyzer.analyze_update_impact(
            instance_id,
            agent_type,
            config.current_version,
            to_version,
        )

        # Create notification record
        notification = await self._create_notification(
            instance_id=instance_id,
            agent_type=agent_type,
            from_version=config.current_version,
            to_version=to_version,
            impact_analysis=impact.to_dict(),
        )

        # Build notification content
        content = self._build_notification_content(impact)

        # Send via configured channels
        for contact in config.notify_contacts:
            await self._send_email(
                to=contact,
                subject=f"[SpokeStack] {agent_type} Agent Update Available: v{to_version}",
                body=content,
            )

        # Also create in-app notification
        await self._create_in_app_notification(instance_id, notification)

    def _build_notification_content(self, impact: UpdateImpactReport) -> str:
        """Build human-readable notification content."""
        content = f"""
## Agent Update Available

**Agent**: {impact.agent_type}
**Current Version**: {impact.from_version}
**New Version**: {impact.to_version}

---

### What's New

{impact.release_notes}

### Changes Summary

**Tools Added**: {', '.join(impact.changes_summary.get('tools_added', [])) or 'None'}
**Tools Modified**: {', '.join(impact.changes_summary.get('tools_modified', [])) or 'None'}
**Tools Removed**: {', '.join(impact.changes_summary.get('tools_removed', [])) or 'None'}

**Behavior Changes**:
{chr(10).join('- ' + c for c in impact.changes_summary.get('behavior_changes', [])) or '- None'}

---

### Impact on Your Instance

**Recommendation**: {impact.recommendation.upper()}

{impact.recommendation_reason}

"""
        if impact.affected_skills:
            content += f"""
### Affected Skills

The following custom skills may be affected by this update:

{chr(10).join('- **' + s + '**' for s in impact.affected_skills)}

"""
        if impact.skill_conflicts:
            content += """
### Detailed Conflicts

"""
            for conflict in impact.skill_conflicts:
                content += f"""
**{conflict['skill']}** ({conflict['severity'].upper()})
- Type: {conflict['type']}
- Reason: {conflict['reason']}
- Suggestion: {conflict['suggestion']}

"""

        if impact.optimization_mismatch:
            content += """
### ⚠️ Optimization Mismatch

This update focuses on different optimization goals than your instance preferences.
Your instance is optimized for **performance/ROAS**, but this update emphasizes **reach/awareness**.

We recommend sandbox testing to ensure your workflows aren't negatively impacted.

"""

        content += """
---

### Next Steps

1. **Review changes** in your SpokeStack dashboard
2. **Test in sandbox** (if staged update policy)
3. **Approve or skip** the update

[View in Dashboard →](https://app.spokestack.io/updates)
"""
        return content
```

### 9.16 Sandbox Testing Environment

```python
class SandboxEnvironment:
    """
    Isolated environment for testing agent updates before deploying.
    """

    async def create_sandbox(
        self,
        instance_id: str,
        agent_type: str,
        test_version: str,
    ) -> SandboxSession:
        """
        Create a sandbox for testing a new agent version.
        """
        # Get current production config
        prod_config = await self._get_instance_config(instance_id, agent_type)
        prod_skills = await self._get_instance_skills(instance_id, agent_type)

        # Create isolated sandbox session
        sandbox_id = str(uuid.uuid4())

        session = SandboxSession(
            id=sandbox_id,
            instance_id=instance_id,
            agent_type=agent_type,
            production_version=prod_config.current_version,
            test_version=test_version,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            status="active",
        )

        await self._save_sandbox_session(session)

        return session

    async def run_comparison_test(
        self,
        sandbox_id: str,
        test_task: str,
        test_context: dict,
    ) -> ComparisonResult:
        """
        Run same task on both production and test versions.
        Compare outputs side-by-side.
        """
        session = await self._get_sandbox_session(sandbox_id)

        # Create both agent versions
        prod_agent = await self.factory.create_agent(
            agent_type=session.agent_type,
            instance_id=session.instance_id,
            version=session.production_version,
        )

        test_agent = await self.factory.create_agent(
            agent_type=session.agent_type,
            instance_id=session.instance_id,
            version=session.test_version,
        )

        # Run task on both
        context = AgentContext(
            tenant_id=session.instance_id,
            task=test_task,
            metadata={**test_context, "sandbox_mode": True},
        )

        prod_result, test_result = await asyncio.gather(
            prod_agent.run(context),
            test_agent.run(context),
        )

        # Analyze differences
        diff_analysis = self._analyze_differences(
            prod_result,
            test_result,
            session.agent_type,
        )

        comparison = ComparisonResult(
            sandbox_id=sandbox_id,
            test_task=test_task,
            production_output=prod_result.output,
            test_output=test_result.output,
            production_tools_used=prod_result.metadata.get("tools_used", []),
            test_tools_used=test_result.metadata.get("tools_used", []),
            differences=diff_analysis,
            timestamp=datetime.utcnow(),
        )

        # Save for review
        await self._save_comparison_result(comparison)

        return comparison

    def _analyze_differences(
        self,
        prod_result: AgentResult,
        test_result: AgentResult,
        agent_type: str,
    ) -> DiffAnalysis:
        """Analyze differences between production and test outputs."""
        differences = []

        # Compare tools used
        prod_tools = set(prod_result.metadata.get("tools_used", []))
        test_tools = set(test_result.metadata.get("tools_used", []))

        if prod_tools != test_tools:
            differences.append({
                "type": "tools_used",
                "production": list(prod_tools),
                "test": list(test_tools),
                "added": list(test_tools - prod_tools),
                "removed": list(prod_tools - test_tools),
            })

        # Compare output length/structure
        if len(test_result.output) != len(prod_result.output):
            differences.append({
                "type": "output_length",
                "production": len(prod_result.output),
                "test": len(test_result.output),
                "change_percent": ((len(test_result.output) - len(prod_result.output))
                                   / len(prod_result.output) * 100),
            })

        # Agent-specific comparisons
        if agent_type == "media_buying":
            differences.extend(self._compare_media_buying_outputs(
                prod_result, test_result
            ))
        elif agent_type == "rfp":
            differences.extend(self._compare_rfp_outputs(
                prod_result, test_result
            ))

        return DiffAnalysis(
            has_differences=len(differences) > 0,
            difference_count=len(differences),
            details=differences,
            recommendation=self._recommend_from_diff(differences),
        )


class SandboxSession(Base):
    """Tracks sandbox testing sessions."""
    __tablename__ = "sandbox_sessions"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"), nullable=False)
    agent_type = Column(String, nullable=False)

    production_version = Column(String, nullable=False)
    test_version = Column(String, nullable=False)

    status = Column(String, default="active")  # active, completed, expired, promoted
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)

    # Test results summary
    tests_run = Column(Integer, default=0)
    tests_passed = Column(Integer, default=0)  # Where outputs were acceptable
    comparison_results = Column(JSONB, default=[])

    # Decision
    decision = Column(String, nullable=True)  # "promote", "reject", "defer"
    decision_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    decision_reason = Column(Text, nullable=True)
```

### 9.17 Version Promotion Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VERSION PROMOTION WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. NEW VERSION RELEASED                                              │   │
│  │    SpokeStack releases Media Buying Agent v2.4.0                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 2. IMPACT ANALYSIS (Automatic)                                       │   │
│  │    For each instance:                                                │   │
│  │    ├── Analyze skill conflicts                                       │   │
│  │    ├── Check optimization mismatch                                   │   │
│  │    └── Generate recommendation                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 3. NOTIFICATION                                                      │   │
│  │    Instance owner receives:                                          │   │
│  │    ├── What changed                                                  │   │
│  │    ├── Impact on their skills                                        │   │
│  │    └── Recommendation (safe/review/caution)                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│              ┌─────────────────────┴─────────────────────┐                 │
│              ▼                                           ▼                 │
│  ┌──────────────────────┐                 ┌──────────────────────┐        │
│  │ UPDATE POLICY: AUTO  │                 │ UPDATE POLICY: STAGED│        │
│  │                      │                 │ or MANUAL             │        │
│  │ If recommendation    │                 │                      │        │
│  │ is "safe":           │                 │ 4. SANDBOX TESTING   │        │
│  │ → Auto-apply         │                 │    ├── Create sandbox│        │
│  │                      │                 │    ├── Run test tasks │        │
│  │ Otherwise:           │                 │    ├── Compare outputs│        │
│  │ → Create sandbox     │                 │    └── Review diffs   │        │
│  └──────────────────────┘                 └──────────┬───────────┘        │
│                                                       │                    │
│                                                       ▼                    │
│                                    ┌─────────────────────────────────────┐ │
│                                    │ 5. DECISION                         │ │
│                                    │    Instance owner chooses:          │ │
│                                    │    ├── PROMOTE: Apply update        │ │
│                                    │    ├── REJECT: Stay on current      │ │
│                                    │    └── DEFER: Review later          │ │
│                                    └─────────────────────────────────────┘ │
│                                                       │                    │
│                                                       ▼                    │
│                                    ┌─────────────────────────────────────┐ │
│                                    │ 6. APPLY OR PIN                     │ │
│                                    │    If PROMOTE:                      │ │
│                                    │    → Update current_version         │ │
│                                    │    → Log in version_history         │ │
│                                    │                                     │ │
│                                    │    If REJECT:                       │ │
│                                    │    → Pin to current version         │ │
│                                    │    → Mark notification rejected     │ │
│                                    └─────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.18 Version Control API

```python
# API endpoints for version control

@router.get("/api/v1/instance/{instance_id}/agents/{agent_type}/versions")
async def list_available_versions(instance_id: str, agent_type: str):
    """List all available versions for an agent."""
    return await version_service.list_versions(agent_type)


@router.get("/api/v1/instance/{instance_id}/agents/{agent_type}/version")
async def get_current_version(instance_id: str, agent_type: str):
    """Get current version configuration for an instance."""
    return await version_service.get_instance_version_config(instance_id, agent_type)


@router.put("/api/v1/instance/{instance_id}/agents/{agent_type}/version")
async def update_version_config(
    instance_id: str,
    agent_type: str,
    config: VersionConfigUpdate,
):
    """
    Update version configuration.

    Example:
    {
        "pinned_version": "2.3.1",  # null to follow latest
        "update_policy": "staged",  # "auto", "staged", "manual"
        "optimization_preference": ["performance", "roas"],
        "notify_on_updates": true,
        "notify_contacts": ["admin@agency.com"]
    }
    """
    return await version_service.update_config(instance_id, agent_type, config)


@router.post("/api/v1/instance/{instance_id}/agents/{agent_type}/version/rollback")
async def rollback_version(
    instance_id: str,
    agent_type: str,
    request: RollbackRequest,
):
    """
    Roll back to a previous version.

    Example:
    {
        "target_version": "2.3.1",
        "reason": "v2.4.0 caused issues with ROAS optimization"
    }
    """
    return await version_service.rollback(
        instance_id, agent_type,
        request.target_version, request.reason
    )


# Notifications
@router.get("/api/v1/instance/{instance_id}/updates")
async def list_pending_updates(instance_id: str):
    """List all pending update notifications."""
    return await notification_service.list_pending(instance_id)


@router.post("/api/v1/instance/{instance_id}/updates/{notification_id}/review")
async def review_update(
    instance_id: str,
    notification_id: str,
    review: UpdateReview,
):
    """
    Review an update notification.

    Example:
    {
        "decision": "sandbox",  # "approve", "reject", "sandbox", "defer"
        "notes": "Need to test with our ROAS workflows first"
    }
    """
    return await notification_service.review_update(
        instance_id, notification_id, review
    )


# Sandbox
@router.post("/api/v1/instance/{instance_id}/sandbox")
async def create_sandbox(
    instance_id: str,
    request: CreateSandboxRequest,
):
    """
    Create a sandbox for testing a version.

    Example:
    {
        "agent_type": "media_buying",
        "test_version": "2.4.0"
    }
    """
    return await sandbox_service.create_sandbox(
        instance_id, request.agent_type, request.test_version
    )


@router.post("/api/v1/instance/{instance_id}/sandbox/{sandbox_id}/test")
async def run_sandbox_test(
    instance_id: str,
    sandbox_id: str,
    test: SandboxTestRequest,
):
    """
    Run a comparison test in the sandbox.

    Example:
    {
        "task": "Create a media buying recommendation for this campaign brief",
        "context": {"campaign_type": "ecommerce", "goal": "roas"}
    }
    """
    return await sandbox_service.run_comparison_test(
        sandbox_id, test.task, test.context
    )


@router.post("/api/v1/instance/{instance_id}/sandbox/{sandbox_id}/promote")
async def promote_sandbox_version(
    instance_id: str,
    sandbox_id: str,
    request: PromoteRequest,
):
    """
    Promote tested version to production.

    Example:
    {
        "confirm": true,
        "notes": "Tested with 5 real campaign scenarios, all performed well"
    }
    """
    return await sandbox_service.promote_version(sandbox_id, request.notes)
```

### 9.19 Instance Owner Dashboard View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INSTANCE OWNER DASHBOARD: AGENTS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ MEDIA BUYING AGENT                                          v2.3.1  │   │
│  │                                                                      │   │
│  │ Status: ✅ Production                                               │   │
│  │ Update Policy: Staged                                               │   │
│  │ Optimization: Performance, ROAS                                     │   │
│  │                                                                      │   │
│  │ ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │ │ ⚠️  UPDATE AVAILABLE: v2.4.0                                    │ │   │
│  │ │                                                                 │ │   │
│  │ │ Recommendation: CAUTION                                         │ │   │
│  │ │                                                                 │ │   │
│  │ │ This update focuses on REACH optimization, which may conflict  │ │   │
│  │ │ with your PERFORMANCE/ROAS preferences.                        │ │   │
│  │ │                                                                 │ │   │
│  │ │ Affected Skills:                                               │ │   │
│  │ │ • roas_optimizer (functionality overlap with new bid_strategy) │ │   │
│  │ │                                                                 │ │   │
│  │ │ [View Details] [Test in Sandbox] [Skip This Version]           │ │   │
│  │ └─────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │ Your Skills (3):                                                    │   │
│  │ • roas_optimizer - Optimizes bids for ROAS targets                 │   │
│  │ • audience_excluder - Excludes low-converting audiences            │   │
│  │ • budget_pacer - Paces budget for consistent daily spend           │   │
│  │                                                                      │   │
│  │ Version History:                                                    │   │
│  │ • v2.3.1 (current) - Activated Jan 5, 2026                         │   │
│  │ • v2.3.0 - Activated Dec 12, 2025                                  │   │
│  │ • v2.2.0 - Activated Nov 1, 2025 (rolled back due to bid issues)  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SANDBOX: Testing v2.4.0                               Active (22h)  │   │
│  │                                                                      │   │
│  │ Tests Run: 5                                                        │   │
│  │ Results:                                                            │   │
│  │ • Test 1: E-commerce campaign ✅ Similar output                    │   │
│  │ • Test 2: Brand awareness     ⚠️  Different tool selection         │   │
│  │ • Test 3: Retargeting         ✅ Similar output                    │   │
│  │ • Test 4: Prospecting         ⚠️  Higher reach, lower ROAS focus   │   │
│  │ • Test 5: Lead gen            ✅ Similar output                    │   │
│  │                                                                      │   │
│  │ [Run Another Test] [View Comparison Details]                        │   │
│  │                                                                      │   │
│  │ Decision: [Promote to Production] [Reject & Stay on v2.3.1]        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.20 Skill-to-Core Promotion Path

When instance skills consistently outperform core functionality:

```python
class SkillPromotionService:
    """
    Identifies high-performing instance skills that could become core features.
    """

    async def analyze_skill_performance(
        self,
        skill_id: str,
    ) -> SkillPerformanceReport:
        """
        Analyze if a skill is outperforming core agent capabilities.
        """
        skill = await self._get_skill(skill_id)

        # Get usage metrics
        usage = await self._get_skill_usage_metrics(skill_id)

        # Get outcome metrics (if tracked)
        outcomes = await self._get_skill_outcome_metrics(skill_id)

        # Compare to core tool (if similar exists)
        core_comparison = None
        similar_core_tool = await self._find_similar_core_tool(skill)
        if similar_core_tool:
            core_comparison = await self._compare_to_core(skill, similar_core_tool)

        return SkillPerformanceReport(
            skill=skill,
            usage_count=usage.total_calls,
            success_rate=usage.success_rate,
            avg_response_time=usage.avg_response_time,
            core_comparison=core_comparison,
            promotion_candidate=self._is_promotion_candidate(usage, outcomes, core_comparison),
        )

    async def submit_for_core_consideration(
        self,
        skill_id: str,
        instance_id: str,
        notes: str,
    ) -> PromotionSubmission:
        """
        Submit a skill for consideration as a core platform feature.
        Instance gets credit/recognition if adopted.
        """
        skill = await self._get_skill(skill_id)
        performance = await self.analyze_skill_performance(skill_id)

        submission = PromotionSubmission(
            skill_id=skill_id,
            instance_id=instance_id,
            skill_definition=skill.to_dict(),
            performance_report=performance.to_dict(),
            submitter_notes=notes,
            status="submitted",
            created_at=datetime.utcnow(),
        )

        await self._save_submission(submission)
        await self._notify_platform_team(submission)

        return submission
```

### 9.21 Key Takeaways (Updated)

| Concern | Solution |
|---------|----------|
| **Global updates** | Core agents in container images, deployed to all |
| **Instance customization** | Configuration stored in instance database |
| **Custom tools/skills** | Webhook-based skills, added per-instance |
| **Client-specific rules** | Client rules table, injected at runtime |
| **Hot reload** | Config loaded on each agent invocation |
| **Isolation** | Each instance has separate database |
| **No code changes** | Skills defined via API, not deployment |
| **Version control** | Pin versions, staged rollouts, rollback support |
| **Update transparency** | Notifications with impact analysis |
| **Conflict detection** | Automatic skill vs update conflict checking |
| **Safe testing** | Sandbox environment with side-by-side comparison |
| **Optimization alignment** | Match updates to instance goals |
| **Skill recognition** | Path to promote great skills to core |

### 9.22 Agent Fine-Tuning Model

Three distinct levels of tuning, each with different permissions and scope:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THREE-TIER TUNING HIERARCHY                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ TIER 1: AGENT BUILDER (SpokeStack Platform Team)                    │   │
│  │                                                                      │   │
│  │ WHO: SpokeStack engineers and AI specialists                        │   │
│  │ WHAT: Core agent architecture, base prompts, default behaviors      │   │
│  │ HOW: Code changes, version releases, platform-wide deployment       │   │
│  │                                                                      │   │
│  │ Controls:                                                            │   │
│  │ ├── Base system prompts (the foundation)                            │   │
│  │ ├── Core tool definitions and implementations                       │   │
│  │ ├── Default parameters and behaviors                                │   │
│  │ ├── Model selection and configuration                               │   │
│  │ ├── Safety guardrails and compliance rules                          │   │
│  │ └── Performance optimization and cost controls                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼ provides foundation for               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ TIER 2: SPOKESTACK INSTANCE (Agency/Company Admin)                  │   │
│  │                                                                      │   │
│  │ WHO: Instance administrators, operations leads                      │   │
│  │ WHAT: Instance-wide customization, vertical specialization          │   │
│  │ HOW: Admin UI, API, configuration database                          │   │
│  │                                                                      │   │
│  │ Controls:                                                            │   │
│  │ ├── Prompt extensions (appended to base)                            │   │
│  │ ├── Default vertical/region/language                                │   │
│  │ ├── Tool enable/disable per agent                                   │   │
│  │ ├── Custom skills (webhook tools)                                   │   │
│  │ ├── Instance-wide brand voice and style                             │   │
│  │ ├── Approval workflows and governance                               │   │
│  │ └── Version control preferences                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼ provides foundation for               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ TIER 3: CLIENT TUNING (Client/Account Manager)                      │   │
│  │                                                                      │   │
│  │ WHO: Account managers, client success, client contacts              │   │
│  │ WHAT: Client-specific preferences, brand rules, feedback            │   │
│  │ HOW: Client settings UI, feedback buttons, preference forms         │   │
│  │                                                                      │   │
│  │ Controls:                                                            │   │
│  │ ├── Client brand voice and tone                                     │   │
│  │ ├── Preferred output formats                                        │   │
│  │ ├── Do/don't rules (topics, competitors, language)                 │   │
│  │ ├── Reference materials (brand guidelines, past work)               │   │
│  │ ├── Feedback on outputs (approve/reject/correct)                    │   │
│  │ └── Client-specific integrations                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.23 What's Tunable at Each Tier

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TUNING PARAMETER MATRIX                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PARAMETER              │ AGENT BUILDER │ INSTANCE │ CLIENT                │
│  ───────────────────────┼───────────────┼──────────┼───────────────────────│
│                                                                             │
│  SYSTEM PROMPT                                                              │
│  ├─ Base prompt         │      ✓        │          │                       │
│  ├─ Instance extension  │               │    ✓     │                       │
│  └─ Client additions    │               │          │       ✓               │
│                                                                             │
│  TOOLS                                                                      │
│  ├─ Core tools          │      ✓        │          │                       │
│  ├─ Enable/disable      │               │    ✓     │                       │
│  ├─ Custom skills       │               │    ✓     │                       │
│  └─ Client integrations │               │          │       ✓               │
│                                                                             │
│  BEHAVIOR                                                                   │
│  ├─ Default parameters  │      ✓        │          │                       │
│  ├─ Parameter overrides │               │    ✓     │                       │
│  └─ Client preferences  │               │          │       ✓               │
│                                                                             │
│  OUTPUT                                                                     │
│  ├─ Format templates    │      ✓        │    ✓     │       ✓               │
│  ├─ Tone/voice          │               │    ✓     │       ✓               │
│  └─ Length/detail       │               │    ✓     │       ✓               │
│                                                                             │
│  MODEL                                                                      │
│  ├─ Model selection     │      ✓        │          │                       │
│  ├─ Temperature         │      ✓        │    ✓*    │                       │
│  └─ Max tokens          │      ✓        │    ✓*    │                       │
│                                                                             │
│  SAFETY                                                                     │
│  ├─ Guardrails          │      ✓        │          │                       │
│  ├─ Content filters     │      ✓        │    ✓+    │                       │
│  └─ Approval gates      │               │    ✓     │                       │
│                                                                             │
│  * = within platform limits                                                │
│  + = can only make more restrictive, not less                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.24 Tier 1: Agent Builder Tuning

Platform-level tuning done by SpokeStack engineering:

```python
class AgentBuilderConfig:
    """
    Platform-level configuration set by SpokeStack team.
    Deployed via code changes, versioned releases.
    """

    # Model configuration
    default_model: str = "claude-sonnet-4-20250514"
    fallback_model: str = "claude-3-haiku-20240307"
    max_tokens: int = 4096
    temperature: float = 0.7

    # Safety guardrails (cannot be relaxed by instances)
    safety_config: SafetyConfig = SafetyConfig(
        max_iterations=25,  # Prevent infinite loops
        max_tool_calls_per_turn=10,
        require_tool_confirmation=["delete_*", "publish_*"],
        blocked_topics=["illegal_activity", "harmful_content"],
        pii_handling="redact",  # or "warn", "block"
    )

    # Cost controls
    cost_config: CostConfig = CostConfig(
        max_tokens_per_request=8000,
        max_requests_per_minute=60,
        cost_tier="standard",  # Instances can upgrade
    )

    # Base system prompt (the foundation)
    base_system_prompt: str = """You are an expert {agent_type} agent.

Your role is to help creative agencies {primary_purpose}.

## Core Capabilities
{capabilities}

## Approach
Follow the Think → Act → Create paradigm:
1. THINK: Understand the request, analyze context
2. ACT: Use tools to gather data, validate, iterate
3. CREATE: Synthesize into actionable deliverables

## Quality Standards
- Be accurate and grounded in data
- Cite sources when making claims
- Flag uncertainty rather than guessing
- Respect brand guidelines and preferences
"""

    # Tool definitions (core functionality)
    core_tools: list[ToolDefinition]

    # Default behaviors
    default_behaviors: dict = {
        "output_format": "markdown",
        "include_sources": True,
        "max_output_length": "comprehensive",
        "error_handling": "graceful_with_explanation",
    }
```

### 9.25 Tier 2: Instance Tuning

Instance administrators customize for their agency:

```python
class InstanceTuningConfig(Base):
    """
    Instance-level tuning stored in database.
    Configured by instance admins via UI/API.
    """
    __tablename__ = "instance_tuning_configs"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"), nullable=False)
    agent_type = Column(String, nullable=False)

    # ═══════════════════════════════════════════════════════════════════════
    # PROMPT TUNING
    # ═══════════════════════════════════════════════════════════════════════

    # Appended to base system prompt
    prompt_extension = Column(Text, nullable=True)
    # Example: "Our agency specializes in luxury brands. Always maintain
    # an elevated, sophisticated tone. Never use casual language or emojis."

    # Specific instructions that override defaults
    instruction_overrides = Column(JSONB, default={})
    # Example: {
    #   "output_format": "Always structure responses with executive summary first",
    #   "citation_style": "Include specific project names and dates",
    # }

    # ═══════════════════════════════════════════════════════════════════════
    # SPECIALIZATION
    # ═══════════════════════════════════════════════════════════════════════

    default_vertical = Column(String, nullable=True)  # "luxury", "tech", "healthcare"
    default_region = Column(String, nullable=True)    # "gcc", "eu", "us"
    default_language = Column(String, default="en")

    # Vertical-specific knowledge injection
    vertical_knowledge = Column(Text, nullable=True)
    # Example: "## Luxury Brand Expertise\n- Understand heritage and craftsmanship...'

    # ═══════════════════════════════════════════════════════════════════════
    # TOOL CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════

    disabled_tools = Column(ARRAY(String), default=[])
    tool_config_overrides = Column(JSONB, default={})
    # Example: {
    #   "search_past_projects": {"default_limit": 10, "include_archived": false},
    #   "generate_copy": {"max_variations": 5},
    # }

    # ═══════════════════════════════════════════════════════════════════════
    # BEHAVIOR TUNING
    # ═══════════════════════════════════════════════════════════════════════

    behavior_params = Column(JSONB, default={})
    # Example: {
    #   "verbosity": "detailed",  # "concise", "standard", "detailed"
    #   "creativity": "conservative",  # "conservative", "balanced", "creative"
    #   "proactivity": "high",  # Suggest next steps, alternatives
    # }

    # Output preferences
    output_preferences = Column(JSONB, default={})
    # Example: {
    #   "default_format": "structured_doc",
    #   "include_rationale": true,
    #   "max_length": "no_limit",
    # }

    # ═══════════════════════════════════════════════════════════════════════
    # BRAND VOICE (Instance-wide defaults)
    # ═══════════════════════════════════════════════════════════════════════

    agency_brand_voice = Column(Text, nullable=True)
    # Example: "We are Apex Creative. Our voice is confident but not arrogant,
    # innovative but grounded, professional but approachable."

    agency_terminology = Column(JSONB, default={})
    # Example: {
    #   "use": ["client partners", "creative solutions", "strategic insights"],
    #   "avoid": ["customers", "stuff", "basically"],
    # }

    # ═══════════════════════════════════════════════════════════════════════
    # GOVERNANCE
    # ═══════════════════════════════════════════════════════════════════════

    require_approval_for = Column(ARRAY(String), default=[])
    # Example: ["publish_content", "send_to_client", "create_campaign"]

    audit_all_outputs = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(UUID, ForeignKey("users.id"))


# Instance Tuning API
@router.put("/api/v1/instance/{instance_id}/agents/{agent_type}/tuning")
async def update_instance_tuning(
    instance_id: str,
    agent_type: str,
    tuning: InstanceTuningUpdate,
):
    """
    Update instance-level tuning for an agent.

    Example:
    {
        "prompt_extension": "We are a Dubai-based agency specializing in luxury...",
        "default_vertical": "luxury",
        "default_region": "gcc",
        "behavior_params": {
            "verbosity": "detailed",
            "creativity": "conservative"
        },
        "agency_brand_voice": "Sophisticated, confident, innovative...",
        "disabled_tools": ["competitor_analysis"]
    }
    """
    return await tuning_service.update_instance_tuning(
        instance_id, agent_type, tuning
    )
```

### 9.26 Tier 3: Client Tuning

Client-specific customization within an instance:

```python
class ClientTuningConfig(Base):
    """
    Client-level tuning within an instance.
    Configured by account managers, refined by feedback.
    """
    __tablename__ = "client_tuning_configs"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"), nullable=False)
    client_id = Column(UUID, ForeignKey("clients.id"), nullable=False)
    agent_type = Column(String, nullable=True)  # null = applies to all agents

    # ═══════════════════════════════════════════════════════════════════════
    # CLIENT BRAND VOICE
    # ═══════════════════════════════════════════════════════════════════════

    brand_voice = Column(Text, nullable=True)
    # Example: "Nike's voice is bold, inspirational, and athletic. Use active
    # verbs, short punchy sentences. Emphasize achievement and perseverance."

    tone_keywords = Column(ARRAY(String), default=[])
    # Example: ["bold", "inspirational", "empowering", "athletic"]

    # ═══════════════════════════════════════════════════════════════════════
    # DO/DON'T RULES
    # ═══════════════════════════════════════════════════════════════════════

    content_rules = Column(JSONB, default={})
    # Example: {
    #   "always": [
    #       "Include 'Just Do It' spirit in messaging",
    #       "Reference athletic achievement",
    #       "Use inclusive language"
    #   ],
    #   "never": [
    #       "Mention competitor brands by name",
    #       "Use passive voice",
    #       "Reference political topics",
    #       "Use discount-focused language"
    #   ],
    #   "prefer": [
    #       "Action-oriented headlines",
    #       "Athlete testimonials over celebrity",
    #       "Performance benefits over fashion"
    #   ]
    # }

    competitor_rules = Column(JSONB, default={})
    # Example: {
    #   "never_mention": ["Adidas", "Puma", "Under Armour"],
    #   "positioning": "Premium performance leader",
    #   "differentiation": ["Innovation", "Athlete partnerships", "Heritage"]
    # }

    # ═══════════════════════════════════════════════════════════════════════
    # OUTPUT PREFERENCES
    # ═══════════════════════════════════════════════════════════════════════

    format_preferences = Column(JSONB, default={})
    # Example: {
    #   "headlines": {"max_words": 8, "style": "imperative"},
    #   "body_copy": {"max_paragraphs": 3, "reading_level": "8th_grade"},
    #   "social": {"hashtag_style": "branded", "emoji_usage": "minimal"}
    # }

    length_preferences = Column(JSONB, default={})
    # Example: {
    #   "default": "concise",
    #   "proposals": "comprehensive",
    #   "social_copy": "minimal"
    # }

    # ═══════════════════════════════════════════════════════════════════════
    # REFERENCE MATERIALS
    # ═══════════════════════════════════════════════════════════════════════

    brand_guidelines_doc_id = Column(UUID, nullable=True)  # Uploaded PDF
    style_guide_doc_id = Column(UUID, nullable=True)
    approved_examples = Column(JSONB, default=[])
    # Example: [
    #   {"type": "headline", "text": "Find Your Greatness", "context": "campaign"},
    #   {"type": "tagline", "text": "Just Do It", "context": "brand"},
    # ]

    # ═══════════════════════════════════════════════════════════════════════
    # LEARNED PREFERENCES (from feedback)
    # ═══════════════════════════════════════════════════════════════════════

    learned_preferences = Column(JSONB, default={})
    # Auto-populated from feedback patterns:
    # {
    #   "preferred_headline_styles": ["imperative", "question"],
    #   "rejected_patterns": ["discount language", "long sentences"],
    #   "successful_approaches": ["athlete stories", "challenge framing"],
    #   "confidence_score": 0.85
    # }

    feedback_summary = Column(JSONB, default={})
    # {
    #   "total_outputs": 150,
    #   "approved": 120,
    #   "rejected": 15,
    #   "corrected": 15,
    #   "approval_rate": 0.80,
    #   "common_corrections": ["too formal", "missing CTA"]
    # }

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# Client Tuning API
@router.put("/api/v1/instance/{instance_id}/clients/{client_id}/tuning")
async def update_client_tuning(
    instance_id: str,
    client_id: str,
    tuning: ClientTuningUpdate,
):
    """
    Update client-level tuning.

    Example:
    {
        "brand_voice": "Bold, inspirational, athletic...",
        "tone_keywords": ["bold", "empowering"],
        "content_rules": {
            "always": ["Include Just Do It spirit"],
            "never": ["Mention competitors"]
        },
        "format_preferences": {
            "headlines": {"max_words": 8}
        }
    }
    """
    return await tuning_service.update_client_tuning(
        instance_id, client_id, tuning
    )
```

### 9.27 Prompt Assembly Pipeline

How the three tiers combine at runtime:

```python
class PromptAssembler:
    """
    Assembles the final system prompt from all three tuning tiers.
    """

    async def assemble_prompt(
        self,
        agent_type: str,
        instance_id: str,
        client_id: str | None = None,
    ) -> str:
        """
        Assemble prompt from:
        1. Base prompt (Agent Builder)
        2. Instance tuning (SpokeStack Instance)
        3. Client tuning (Client-specific)
        """
        # ═══════════════════════════════════════════════════════════════════
        # TIER 1: Base prompt from Agent Builder
        # ═══════════════════════════════════════════════════════════════════
        base_config = self.get_agent_builder_config(agent_type)
        prompt = base_config.base_system_prompt

        # ═══════════════════════════════════════════════════════════════════
        # TIER 2: Instance tuning
        # ═══════════════════════════════════════════════════════════════════
        instance_tuning = await self.load_instance_tuning(instance_id, agent_type)

        if instance_tuning:
            # Add instance prompt extension
            if instance_tuning.prompt_extension:
                prompt += f"\n\n## Agency-Specific Guidelines\n\n"
                prompt += instance_tuning.prompt_extension

            # Add vertical knowledge
            if instance_tuning.vertical_knowledge:
                prompt += f"\n\n## Industry Expertise\n\n"
                prompt += instance_tuning.vertical_knowledge

            # Add agency brand voice
            if instance_tuning.agency_brand_voice:
                prompt += f"\n\n## Agency Voice\n\n"
                prompt += instance_tuning.agency_brand_voice

            # Add behavior instructions
            if instance_tuning.behavior_params:
                prompt += self._format_behavior_instructions(
                    instance_tuning.behavior_params
                )

        # ═══════════════════════════════════════════════════════════════════
        # TIER 3: Client tuning
        # ═══════════════════════════════════════════════════════════════════
        if client_id:
            client_tuning = await self.load_client_tuning(
                instance_id, client_id, agent_type
            )

            if client_tuning:
                prompt += f"\n\n## Client: {client_tuning.client_name}\n\n"

                # Add brand voice
                if client_tuning.brand_voice:
                    prompt += f"### Brand Voice\n{client_tuning.brand_voice}\n\n"

                # Add tone keywords
                if client_tuning.tone_keywords:
                    prompt += f"### Tone\n"
                    prompt += f"Key attributes: {', '.join(client_tuning.tone_keywords)}\n\n"

                # Add content rules
                if client_tuning.content_rules:
                    prompt += self._format_content_rules(client_tuning.content_rules)

                # Add competitor rules
                if client_tuning.competitor_rules:
                    prompt += self._format_competitor_rules(
                        client_tuning.competitor_rules
                    )

                # Add format preferences
                if client_tuning.format_preferences:
                    prompt += self._format_output_preferences(
                        client_tuning.format_preferences
                    )

                # Add learned preferences (from feedback)
                if client_tuning.learned_preferences:
                    prompt += self._format_learned_preferences(
                        client_tuning.learned_preferences
                    )

                # Add approved examples
                if client_tuning.approved_examples:
                    prompt += self._format_examples(client_tuning.approved_examples)

        return prompt

    def _format_content_rules(self, rules: dict) -> str:
        """Format do/don't rules for the prompt."""
        output = "### Content Rules\n\n"

        if rules.get("always"):
            output += "**Always:**\n"
            for rule in rules["always"]:
                output += f"- {rule}\n"
            output += "\n"

        if rules.get("never"):
            output += "**Never:**\n"
            for rule in rules["never"]:
                output += f"- {rule}\n"
            output += "\n"

        if rules.get("prefer"):
            output += "**Prefer:**\n"
            for rule in rules["prefer"]:
                output += f"- {rule}\n"
            output += "\n"

        return output

    def _format_learned_preferences(self, learned: dict) -> str:
        """Format preferences learned from feedback."""
        output = "### Learned from Feedback\n\n"
        output += "*These preferences were learned from past approvals/corrections:*\n\n"

        if learned.get("preferred_headline_styles"):
            output += f"- Preferred headline styles: {', '.join(learned['preferred_headline_styles'])}\n"

        if learned.get("successful_approaches"):
            output += f"- Approaches that work well: {', '.join(learned['successful_approaches'])}\n"

        if learned.get("rejected_patterns"):
            output += f"- Patterns to avoid: {', '.join(learned['rejected_patterns'])}\n"

        return output + "\n"
```

### 9.28 Feedback Loop System

How client feedback improves tuning over time:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FEEDBACK LOOP SYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. AGENT OUTPUT                                                      │   │
│  │    Agent generates content/recommendation for client                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 2. USER FEEDBACK                                                     │   │
│  │                                                                      │   │
│  │    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐       │   │
│  │    │    👍    │  │    👎    │  │   ✏️    │  │  💬 Comment  │       │   │
│  │    │ Approve  │  │  Reject  │  │  Correct │  │              │       │   │
│  │    └──────────┘  └──────────┘  └──────────┘  └──────────────┘       │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 3. FEEDBACK STORAGE                                                  │   │
│  │                                                                      │   │
│  │    feedback_records: [                                               │   │
│  │      {                                                               │   │
│  │        output_id: "...",                                            │   │
│  │        agent_type: "copy",                                          │   │
│  │        client_id: "nike",                                           │   │
│  │        output_text: "Find Your Inner Champion...",                  │   │
│  │        feedback_type: "approved",                                   │   │
│  │        corrections: null,                                           │   │
│  │        comment: "Great energy, on brand",                           │   │
│  │        feedback_by: "account_manager_1",                            │   │
│  │        feedback_at: "2026-01-13T10:30:00Z"                         │   │
│  │      },                                                              │   │
│  │      {                                                               │   │
│  │        output_id: "...",                                            │   │
│  │        feedback_type: "corrected",                                  │   │
│  │        original_text: "Get 20% off today...",                       │   │
│  │        corrected_text: "Unlock your potential...",                  │   │
│  │        correction_reason: "Nike doesn't use discount language",     │   │
│  │      }                                                               │   │
│  │    ]                                                                 │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 4. PATTERN ANALYSIS (Automatic)                                      │   │
│  │                                                                      │   │
│  │    Analyze feedback to identify patterns:                            │   │
│  │    ├── What gets approved consistently?                              │   │
│  │    ├── What gets rejected? Why?                                      │   │
│  │    ├── Common corrections (indicates missing rules)                 │   │
│  │    └── Emerging preferences                                         │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 5. TUNING SUGGESTIONS                                                │   │
│  │                                                                      │   │
│  │    System suggests tuning updates:                                   │   │
│  │                                                                      │   │
│  │    "Based on 15 corrections for Nike, we suggest adding:            │   │
│  │     • Never rule: 'discount language'                               │   │
│  │     • Prefer rule: 'achievement framing'                            │   │
│  │                                                                      │   │
│  │    [Apply Suggestions] [Review Details] [Dismiss]"                  │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 6. LEARNED PREFERENCES UPDATE                                        │   │
│  │                                                                      │   │
│  │    Auto-update or human-approved update to:                         │   │
│  │    ClientTuningConfig.learned_preferences                           │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│                          IMPROVED FUTURE OUTPUTS                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.29 Feedback Data Model

```python
class AgentOutputFeedback(Base):
    """Stores feedback on agent outputs for learning."""
    __tablename__ = "agent_output_feedback"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"), nullable=False)
    client_id = Column(UUID, ForeignKey("clients.id"), nullable=True)

    # What was generated
    agent_type = Column(String, nullable=False)
    task_id = Column(UUID, nullable=False)  # Reference to original task
    output_text = Column(Text, nullable=False)
    output_metadata = Column(JSONB, default={})  # Tools used, context, etc.

    # Feedback
    feedback_type = Column(String, nullable=False)
    # "approved", "rejected", "corrected", "partial_approved"

    # For corrections
    corrected_text = Column(Text, nullable=True)
    correction_reason = Column(Text, nullable=True)
    correction_category = Column(String, nullable=True)
    # "tone", "factual", "format", "brand_voice", "missing_info", "too_long", etc.

    # For rejections
    rejection_reason = Column(Text, nullable=True)
    rejection_category = Column(String, nullable=True)

    # Optional detailed feedback
    comment = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 stars

    # Who gave feedback
    feedback_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    feedback_at = Column(DateTime, default=datetime.utcnow)

    # Analysis (populated by pattern analyzer)
    analysis = Column(JSONB, default={})
    # {
    #   "identified_patterns": ["discount_language", "passive_voice"],
    #   "suggested_rules": [...],
    #   "similar_corrections": [...]
    # }


class FeedbackPatternAnalysis(Base):
    """Aggregated pattern analysis from feedback."""
    __tablename__ = "feedback_pattern_analysis"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"), nullable=False)
    client_id = Column(UUID, ForeignKey("clients.id"), nullable=True)
    agent_type = Column(String, nullable=True)

    # Analysis period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Metrics
    total_outputs = Column(Integer, default=0)
    approved_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)
    corrected_count = Column(Integer, default=0)
    approval_rate = Column(Float, default=0.0)

    # Identified patterns
    common_corrections = Column(JSONB, default=[])
    # [{"pattern": "discount language", "count": 15, "examples": [...]}]

    common_rejections = Column(JSONB, default=[])
    successful_patterns = Column(JSONB, default=[])

    # Suggested tuning changes
    suggested_rules = Column(JSONB, default=[])
    # [
    #   {"type": "never", "rule": "Use discount language", "confidence": 0.9},
    #   {"type": "prefer", "rule": "Achievement framing", "confidence": 0.85}
    # ]

    suggestion_status = Column(String, default="pending")
    # "pending", "applied", "dismissed", "partial_applied"

    applied_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    applied_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
```

### 9.30 Feedback Analysis Service

```python
class FeedbackAnalyzer:
    """Analyzes feedback to identify patterns and suggest tuning."""

    async def analyze_client_feedback(
        self,
        instance_id: str,
        client_id: str,
        lookback_days: int = 30,
    ) -> FeedbackAnalysisReport:
        """
        Analyze recent feedback for a client to identify patterns.
        """
        # Get recent feedback
        feedback = await self._get_recent_feedback(
            instance_id, client_id, lookback_days
        )

        if len(feedback) < 10:
            return FeedbackAnalysisReport(
                status="insufficient_data",
                message="Need at least 10 feedback items for analysis",
            )

        # Calculate metrics
        metrics = self._calculate_metrics(feedback)

        # Identify patterns in corrections
        correction_patterns = await self._analyze_corrections(
            [f for f in feedback if f.feedback_type == "corrected"]
        )

        # Identify patterns in rejections
        rejection_patterns = await self._analyze_rejections(
            [f for f in feedback if f.feedback_type == "rejected"]
        )

        # Identify successful patterns
        success_patterns = await self._analyze_successes(
            [f for f in feedback if f.feedback_type == "approved"]
        )

        # Generate suggestions
        suggestions = self._generate_suggestions(
            correction_patterns,
            rejection_patterns,
            success_patterns,
        )

        return FeedbackAnalysisReport(
            status="complete",
            period_start=datetime.utcnow() - timedelta(days=lookback_days),
            period_end=datetime.utcnow(),
            metrics=metrics,
            correction_patterns=correction_patterns,
            rejection_patterns=rejection_patterns,
            success_patterns=success_patterns,
            suggestions=suggestions,
        )

    async def _analyze_corrections(
        self,
        corrections: list[AgentOutputFeedback],
    ) -> list[Pattern]:
        """Use Claude to identify patterns in corrections."""
        if not corrections:
            return []

        # Prepare examples for analysis
        examples = [
            {
                "original": c.output_text[:500],
                "corrected": c.corrected_text[:500] if c.corrected_text else None,
                "reason": c.correction_reason,
                "category": c.correction_category,
            }
            for c in corrections[:50]  # Limit for analysis
        ]

        # Use Claude to identify patterns
        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system="""You are analyzing corrections made to AI-generated content.
            Identify patterns in what was corrected and why.
            Output structured JSON with identified patterns.""",
            messages=[{
                "role": "user",
                "content": f"""Analyze these corrections and identify patterns:

{json.dumps(examples, indent=2)}

Return JSON with:
- patterns: list of {{pattern_name, description, frequency, examples}}
- suggested_rules: list of {{type: "always"|"never"|"prefer", rule, confidence}}
"""
            }],
        )

        return self._parse_pattern_response(response)

    def _generate_suggestions(
        self,
        correction_patterns: list,
        rejection_patterns: list,
        success_patterns: list,
    ) -> list[TuningSuggestion]:
        """Generate tuning suggestions from patterns."""
        suggestions = []

        # High-frequency corrections → "never" rules
        for pattern in correction_patterns:
            if pattern.frequency >= 3 and pattern.confidence >= 0.8:
                suggestions.append(TuningSuggestion(
                    type="never",
                    rule=pattern.description,
                    confidence=pattern.confidence,
                    evidence_count=pattern.frequency,
                    examples=pattern.examples[:3],
                ))

        # High-frequency rejections → "never" rules
        for pattern in rejection_patterns:
            if pattern.frequency >= 3 and pattern.confidence >= 0.8:
                suggestions.append(TuningSuggestion(
                    type="never",
                    rule=pattern.description,
                    confidence=pattern.confidence,
                    evidence_count=pattern.frequency,
                    examples=pattern.examples[:3],
                ))

        # Success patterns → "prefer" rules
        for pattern in success_patterns:
            if pattern.frequency >= 5 and pattern.confidence >= 0.7:
                suggestions.append(TuningSuggestion(
                    type="prefer",
                    rule=pattern.description,
                    confidence=pattern.confidence,
                    evidence_count=pattern.frequency,
                    examples=pattern.examples[:3],
                ))

        return sorted(suggestions, key=lambda s: s.confidence, reverse=True)
```

### 9.31 Tuning Governance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TUNING GOVERNANCE MODEL                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WHO CAN TUNE WHAT                                                          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ROLE                     │ TIER 1 │ TIER 2 │ TIER 3                 │   │
│  │                          │ (Core) │ (Inst) │ (Client)               │   │
│  │──────────────────────────┼────────┼────────┼────────────────────────│   │
│  │ SpokeStack Engineer      │   ✓    │   ✓*   │   ✓*                   │   │
│  │ Instance Admin           │        │   ✓    │   ✓                    │   │
│  │ Instance Manager         │        │   👁    │   ✓                    │   │
│  │ Account Manager          │        │        │   ✓                    │   │
│  │ Client Contact           │        │        │   ✓**                  │   │
│  │                                                                      │   │
│  │ ✓* = for support/debugging only                                     │   │
│  │ ✓** = limited to feedback, approved examples, preferences           │   │
│  │ 👁 = view only                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  CHANGE APPROVAL REQUIREMENTS                                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ CHANGE TYPE                         │ APPROVAL NEEDED               │   │
│  │─────────────────────────────────────┼──────────────────────────────│   │
│  │ Core agent prompt change            │ Engineering + QA review       │   │
│  │ New core tool                       │ Engineering + Security review │   │
│  │ Instance prompt extension           │ Instance Admin                │   │
│  │ Instance skill addition             │ Instance Admin                │   │
│  │ Client brand voice update           │ Account Manager               │   │
│  │ Client "never" rule                 │ Account Manager               │   │
│  │ Auto-learned preference             │ Auto or Account Manager*      │   │
│  │                                                                      │   │
│  │ * Configurable: auto_apply_learned_preferences = true/false        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  AUDIT TRAIL                                                                │
│                                                                             │
│  All tuning changes logged with:                                           │
│  ├── Who made the change                                                   │
│  ├── What was changed (before/after)                                       │
│  ├── When it was changed                                                   │
│  ├── Why (optional reason/ticket)                                          │
│  └── Impact assessment (which clients affected)                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

```python
class TuningAuditLog(Base):
    """Audit trail for all tuning changes."""
    __tablename__ = "tuning_audit_logs"

    id = Column(UUID, primary_key=True)
    instance_id = Column(UUID, ForeignKey("instances.id"), nullable=False)

    # What tier was changed
    tier = Column(String, nullable=False)  # "agent_builder", "instance", "client"

    # What was changed
    entity_type = Column(String, nullable=False)  # "prompt", "tool", "rule", "preference"
    entity_id = Column(String, nullable=True)
    agent_type = Column(String, nullable=True)
    client_id = Column(UUID, nullable=True)

    # Change details
    change_type = Column(String, nullable=False)  # "create", "update", "delete"
    field_changed = Column(String, nullable=True)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)

    # Who and why
    changed_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    change_reason = Column(Text, nullable=True)
    ticket_reference = Column(String, nullable=True)

    # Impact
    affected_clients = Column(ARRAY(UUID), default=[])
    requires_review = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)


# Governance enforcement
class TuningGovernance:
    """Enforces tuning governance rules."""

    PERMISSIONS = {
        "spokestack_engineer": {
            "agent_builder": ["read", "write"],
            "instance": ["read", "write_support"],
            "client": ["read", "write_support"],
        },
        "instance_admin": {
            "agent_builder": ["read"],
            "instance": ["read", "write"],
            "client": ["read", "write"],
        },
        "instance_manager": {
            "agent_builder": ["read"],
            "instance": ["read"],
            "client": ["read", "write"],
        },
        "account_manager": {
            "agent_builder": [],
            "instance": [],
            "client": ["read", "write"],
        },
        "client_contact": {
            "agent_builder": [],
            "instance": [],
            "client": ["read", "write_limited"],  # Only feedback, examples
        },
    }

    async def check_permission(
        self,
        user_id: str,
        tier: str,
        action: str,
        instance_id: str = None,
        client_id: str = None,
    ) -> bool:
        """Check if user has permission for tuning action."""
        user = await self._get_user(user_id)
        role = user.role

        permissions = self.PERMISSIONS.get(role, {})
        tier_permissions = permissions.get(tier, [])

        if action in tier_permissions:
            return True

        # Check for limited write permissions
        if action == "write" and "write_limited" in tier_permissions:
            # Only allow specific fields
            return False  # Caller must use write_limited endpoint

        return False
```

### 9.32 Tuning UI Wireframe

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLIENT TUNING DASHBOARD                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Client: Nike                                           [Edit] [History]   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ BRAND VOICE                                                          │   │
│  │                                                                      │   │
│  │ ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │ │ Bold, inspirational, and athletic. Use active verbs, short      │ │   │
│  │ │ punchy sentences. Emphasize achievement and perseverance.       │ │   │
│  │ │ The Nike voice challenges and empowers.                         │ │   │
│  │ └─────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │ Tone Keywords: [bold] [inspirational] [empowering] [+ Add]          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ CONTENT RULES                                                        │   │
│  │                                                                      │   │
│  │ ✅ Always                           ❌ Never                        │   │
│  │ ├─ Include "Just Do It" spirit      ├─ Mention competitor brands    │   │
│  │ ├─ Reference athletic achievement   ├─ Use discount language        │   │
│  │ ├─ Use inclusive language           ├─ Use passive voice            │   │
│  │ └─ [+ Add rule]                     └─ [+ Add rule]                 │   │
│  │                                                                      │   │
│  │ ⭐ Prefer                                                           │   │
│  │ ├─ Action-oriented headlines                                        │   │
│  │ ├─ Athlete testimonials over celebrity                              │   │
│  │ └─ [+ Add rule]                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 💡 SUGGESTED IMPROVEMENTS                          Based on feedback │   │
│  │                                                                      │   │
│  │ ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │ │ ⚠️  Add "Never" rule: "Use urgency language (limited time)"    │ │   │
│  │ │                                                                 │ │   │
│  │ │ Based on 8 corrections in the last 30 days where urgency       │ │   │
│  │ │ language was removed.                                          │ │   │
│  │ │                                                                 │ │   │
│  │ │ Examples:                                                       │ │   │
│  │ │ • "Hurry, sale ends soon" → "Elevate your game"               │ │   │
│  │ │ • "Don't miss out" → "Step into greatness"                    │ │   │
│  │ │                                                                 │ │   │
│  │ │ [Apply Rule] [Dismiss] [View All 8]                            │ │   │
│  │ └─────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 📊 FEEDBACK METRICS                                    Last 30 days │   │
│  │                                                                      │   │
│  │ Approval Rate: ████████████████████░░░░ 82%                         │   │
│  │                                                                      │   │
│  │ Total Outputs: 145    Approved: 119    Corrected: 18    Rejected: 8│   │
│  │                                                                      │   │
│  │ Top Correction Reasons:                                             │   │
│  │ 1. Too formal (6)                                                   │   │
│  │ 2. Missing CTA (5)                                                  │   │
│  │ 3. Urgency language (4)                                             │   │
│  │                                                                      │   │
│  │ [View Detailed Analysis]                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 📝 APPROVED EXAMPLES                                                 │   │
│  │                                                                      │   │
│  │ Headline: "Find Your Greatness" ⭐ Campaign: Summer 2025            │   │
│  │ Headline: "Victory Loves Preparation" ⭐ Campaign: Training         │   │
│  │ Tagline: "Just Do It" ⭐ Brand                                      │   │
│  │                                                                      │   │
│  │ [+ Add Example]                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.33 Tuning API Summary

```python
# ═══════════════════════════════════════════════════════════════════════════
# TIER 2: INSTANCE TUNING API
# ═══════════════════════════════════════════════════════════════════════════

# Get/update instance tuning
GET  /api/v1/instance/{instance_id}/tuning
PUT  /api/v1/instance/{instance_id}/tuning

# Per-agent instance tuning
GET  /api/v1/instance/{instance_id}/agents/{agent_type}/tuning
PUT  /api/v1/instance/{instance_id}/agents/{agent_type}/tuning

# ═══════════════════════════════════════════════════════════════════════════
# TIER 3: CLIENT TUNING API
# ═══════════════════════════════════════════════════════════════════════════

# Get/update client tuning
GET  /api/v1/instance/{instance_id}/clients/{client_id}/tuning
PUT  /api/v1/instance/{instance_id}/clients/{client_id}/tuning

# Client rules management
POST /api/v1/instance/{instance_id}/clients/{client_id}/rules
DELETE /api/v1/instance/{instance_id}/clients/{client_id}/rules/{rule_id}

# Approved examples
POST /api/v1/instance/{instance_id}/clients/{client_id}/examples
DELETE /api/v1/instance/{instance_id}/clients/{client_id}/examples/{example_id}

# ═══════════════════════════════════════════════════════════════════════════
# FEEDBACK API
# ═══════════════════════════════════════════════════════════════════════════

# Submit feedback on output
POST /api/v1/instance/{instance_id}/feedback
# Body: {output_id, feedback_type, corrected_text?, comment?, rating?}

# Get feedback analysis
GET  /api/v1/instance/{instance_id}/clients/{client_id}/feedback/analysis

# Apply suggested tuning from feedback
POST /api/v1/instance/{instance_id}/clients/{client_id}/feedback/apply-suggestions
# Body: {suggestion_ids: [...]}

# ═══════════════════════════════════════════════════════════════════════════
# AUDIT API
# ═══════════════════════════════════════════════════════════════════════════

# Get tuning change history
GET  /api/v1/instance/{instance_id}/tuning/audit
GET  /api/v1/instance/{instance_id}/clients/{client_id}/tuning/audit

# Rollback tuning change
POST /api/v1/instance/{instance_id}/tuning/rollback/{audit_id}
```

### 9.34 Key Takeaways: Fine-Tuning Model

| Tier | Who | What They Tune | How |
|------|-----|----------------|-----|
| **Agent Builder** | SpokeStack Engineers | Core prompts, tools, defaults, guardrails | Code + releases |
| **Instance** | Agency Admins | Prompt extensions, specialization, skills, brand voice | Admin UI/API |
| **Client** | Account Managers | Brand voice, do/don't rules, format prefs, examples | Client UI/API |

| Feature | Description |
|---------|-------------|
| **Prompt Assembly** | Three tiers merge at runtime: base + instance + client |
| **Feedback Loop** | Approve/reject/correct → pattern analysis → suggestions |
| **Auto-Learning** | System suggests tuning rules from feedback patterns |
| **Governance** | Role-based permissions, audit trail, approval workflows |
| **Client Isolation** | Each client's tuning is separate within an instance |

---

## 10. ERP Integration Patterns

### 10.1 HTTP Client Setup

```python
def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
    self.erp_base_url = erp_base_url
    self.erp_api_key = erp_api_key
    self.http_client = httpx.AsyncClient(
        base_url=erp_base_url,
        headers={
            "Authorization": f"Bearer {erp_api_key}",
            "Content-Type": "application/json",
        },
        timeout=httpx.Timeout(30.0, connect=10.0),
    )
```

### 10.2 Common ERP Operations

```python
# GET - Fetch data
async def _get_client(self, client_id: str) -> dict:
    response = await self.http_client.get(f"/api/v1/clients/{client_id}")
    if response.status_code == 200:
        return response.json()
    return {"error": "Client not found"}

# POST - Create record
async def _create_project(self, data: dict) -> dict:
    response = await self.http_client.post("/api/v1/projects", json=data)
    if response.status_code in (200, 201):
        return response.json()
    return {"error": "Failed to create project"}

# PUT - Update record
async def _update_status(self, project_id: str, status: str) -> dict:
    response = await self.http_client.put(
        f"/api/v1/projects/{project_id}",
        json={"status": status},
    )
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to update"}

# DELETE - Remove record
async def _delete_draft(self, draft_id: str) -> dict:
    response = await self.http_client.delete(f"/api/v1/drafts/{draft_id}")
    return {"deleted": response.status_code == 204}
```

### 10.3 Module-to-Agent Mapping

| ERP Module | Primary Agent(s) | Supporting Agents |
|------------|------------------|-------------------|
| `briefs` | Brief Agent | Content, RFP |
| `rfp` | RFP Agent | Commercial |
| `crm` | CRM Agent | Onboarding |
| `studio` | All Studio Agents | Brand agents |
| `dam` | Image Agent | Video Production |
| `resources` | Resource Agent | Workflow |
| `workflows` | Workflow Agent | All agents |
| `reporting` | Ops Reporting | Instance Analytics |
| `publisher` | Publisher Agent | Content, Calendar |
| `reply` | Reply Agent | CRM, Channel |
| `channel` | Channel Agent | All gateways |

### 10.4 Error Handling Pattern

```python
async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
    try:
        if tool_name == "fetch_data":
            return await self._fetch_data(tool_input)
    except httpx.TimeoutException:
        return {
            "error": "Request timed out",
            "suggestion": "Try again or reduce the scope of the request",
            "retry": True,
        }
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 401:
            return {"error": "Authentication failed", "action_required": "refresh_token"}
        elif status == 403:
            return {"error": "Permission denied", "required_permission": "..."}
        elif status == 404:
            return {"error": "Resource not found", "resource": tool_input.get("id")}
        elif status >= 500:
            return {"error": "Server error", "retry": True}
        return {"error": f"HTTP {status}"}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}
```

---

## 11. Advanced Patterns

### 11.1 Agent Chaining

Agents can invoke other agents for complex workflows:

```python
class OrchestrationAgent(BaseAgent):
    """Orchestrates multiple agents for complex workflows."""

    def __init__(self, client, model, erp_base_url, erp_api_key):
        # Initialize sub-agents
        self.rfp_agent = RFPAgent(client, model, erp_base_url, erp_api_key)
        self.commercial_agent = CommercialAgent(client, model, erp_base_url, erp_api_key)
        self.copy_agent = CopyAgent(client, model, erp_base_url, erp_api_key)
        super().__init__(client, model)

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "run_rfp_analysis",
                "description": "Delegate RFP analysis to specialized RFP agent",
                "input_schema": {...},
            },
            {
                "name": "run_pricing",
                "description": "Delegate pricing to Commercial agent",
                "input_schema": {...},
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "run_rfp_analysis":
            result = await self.rfp_agent.run(AgentContext(
                tenant_id=self.current_context.tenant_id,
                user_id=self.current_context.user_id,
                task=tool_input["task"],
            ))
            return {"rfp_analysis": result.output}
```

### 11.2 Streaming Responses

For real-time feedback:

```python
async def handle_streaming_request(request):
    agent = MyAgent(...)
    context = AgentContext(...)

    async def event_stream():
        async for chunk in agent.stream(context):
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )
```

### 11.3 Conditional Tool Access

Expose tools based on context:

```python
def _define_tools(self) -> list[dict]:
    tools = [
        # Always available
        {"name": "read_brief", ...},
        {"name": "search_projects", ...},
    ]

    # Role-based tools
    if self.user_role in ["admin", "manager"]:
        tools.append({
            "name": "approve_budget",
            "description": "Approve budget allocations (managers only)",
            ...
        })

    # Feature-flag tools
    if self.features.get("ai_generation_enabled"):
        tools.append({
            "name": "generate_creative",
            "description": "Generate AI creative assets",
            ...
        })

    return tools
```

### 11.4 Tool Result Caching

For expensive operations:

```python
from functools import lru_cache
import hashlib

class CachingAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        # Create cache key
        cache_key = hashlib.md5(
            f"{tool_name}:{json.dumps(tool_input, sort_keys=True)}".encode()
        ).hexdigest()

        # Check cache (for read-only tools)
        if tool_name in ["search_projects", "get_guidelines"]:
            if cache_key in self._cache:
                return self._cache[cache_key]

        # Execute tool
        result = await self._do_execute_tool(tool_name, tool_input)

        # Cache result
        if tool_name in ["search_projects", "get_guidelines"]:
            self._cache[cache_key] = result

        return result
```

### 11.5 Handoff Pattern

For transitioning between agent phases:

```python
# Instance Onboarding → Instance Success handoff
{
    "name": "handoff_to_success",
    "description": "Complete onboarding and hand off to Instance Success agent",
    "input_schema": {
        "type": "object",
        "properties": {
            "instance_id": {"type": "string"},
            "onboarding_summary": {
                "type": "object",
                "properties": {
                    "modules_configured": {"type": "array"},
                    "users_invited": {"type": "integer"},
                    "integrations_connected": {"type": "array"},
                    "sample_data_generated": {"type": "boolean"},
                },
            },
            "initial_goals": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Goals identified during onboarding",
            },
            "notes_for_csm": {
                "type": "string",
                "description": "Any important notes for the success manager",
            },
        },
        "required": ["instance_id", "onboarding_summary"],
    },
}
```

### 11.6 Browser Automation Skill

For agents that need to interact with web pages, SpokeStack provides the `AgentBrowserSkill` - a Python wrapper around the `agent-browser` CLI that reduces context by 93% using a Snapshot + Refs pattern.

#### Installation

```bash
# Install the agent-browser CLI globally
npm install -g @anthropic-ai/agent-browser
```

#### Basic Usage

```python
from src.skills.agent_browser import AgentBrowserSkill

class SocialListeningAgent(BaseAgent):
    """Agent with browser automation capability."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Each agent gets an isolated browser session
        self.browser = AgentBrowserSkill(session_name="social-listener")

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "scrape_trending":
            return await self._scrape_trending(tool_input["platform"])
        ...

    async def _scrape_trending(self, platform: str):
        """Scrape trending content using browser automation."""
        urls = {
            "instagram": "https://instagram.com/explore",
            "tiktok": "https://tiktok.com/discover",
        }

        # 1. Navigate
        await self.browser.open(urls[platform])

        # 2. Snapshot (returns refs like @e1, @e2, @e3)
        snapshot = await self.browser.snapshot(interactive_only=True)

        # 3. Interact using refs
        await self.browser.click("@e3")
        text = await self.browser.get_text("@e5")

        # 4. Capture proof
        await self.browser.screenshot(f"trending_{platform}.png")

        # 5. Cleanup
        await self.browser.close()

        return {"snapshot": snapshot.raw, "extracted": text}
```

#### Key Concepts

**Snapshot + Refs Pattern**:
- `snapshot()` returns element refs like `@e1`, `@e2`, `@e3`
- Refs are deterministic selectors that work until page changes
- Use `-i` flag (interactive_only) for 93% context reduction

```python
# Minimal context - only interactive elements
snapshot = await browser.snapshot(interactive_only=True)
# Output: @e1 button "Sign In", @e2 textbox "Email", @e3 button "Submit"

# Full tree for content extraction
snapshot = await browser.snapshot(interactive_only=False)
```

**Session Isolation for Multi-Tenancy**:
```python
# Instance A's agents run in isolated sessions
instance_a_social = AgentBrowserSkill(session_name="inst_a_social")
instance_a_competitor = AgentBrowserSkill(session_name="inst_a_competitor")

# Instance B's agents are completely isolated
instance_b_social = AgentBrowserSkill(session_name="inst_b_social")

# All can run simultaneously
await asyncio.gather(
    instance_a_social.open("https://instagram.com"),
    instance_a_competitor.open("https://similarweb.com"),
    instance_b_social.open("https://tiktok.com"),
)
```

#### Available Methods

| Method | Description |
|--------|-------------|
| `open(url)` | Navigate to URL |
| `snapshot(interactive_only, compact)` | Get element refs |
| `click(ref)` | Click element by ref |
| `fill(ref, text)` | Fill input field |
| `get_text(ref)` | Extract text content |
| `screenshot(path)` | Capture screenshot |
| `wait_for_text(text)` | Wait for content |
| `capture_proof(url, dir, prefix)` | Timestamped proof screenshot |

#### Agent Use Cases

| Agent | Browser Capability |
|-------|-------------------|
| Social Listening | Scrape trending content, competitor posts |
| Competitor | Navigate SimilarWeb, Meta Ad Library, SpyFu |
| Media Buying | Verify campaign setup, screenshot live ads |
| QA | Visual regression testing, landing page verification |
| Instance Onboarding | OAuth flow automation, platform verification |
| CRM | Contact enrichment from LinkedIn, company sites |
| Legal | Capture T&C pages, compliance documentation |

#### Proof-of-Work Pattern

```python
async def verify_and_document(self, campaign_id: str, url: str):
    """Capture proof that work was done."""
    await self.browser.open(url)
    await self.browser.wait(2000)  # Let page settle

    # Timestamped proof screenshot
    filepath = await self.browser.capture_proof(
        url=url,
        output_dir=f"/proofs/campaign_{campaign_id}",
        prefix="live_ad"
    )
    # Returns: /proofs/campaign_123/live_ad_20260115_143022.png

    return {"verified": True, "proof": filepath}
```

See `knowledge/agents/skills/BROWSER_SKILL.md` for full command reference and `knowledge/BROWSER_ENABLED_CAPABILITIES.md` for advanced multi-tenant patterns.

---

## 12. Testing & Validation

### 12.1 Unit Testing Tools

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestRFPAgent:
    @pytest.fixture
    def agent(self):
        client = AsyncMock()
        return RFPAgent(
            client=client,
            model="claude-3-opus",
            erp_base_url="https://api.test.com",
            erp_api_key="test_key",
        )

    @pytest.mark.asyncio
    async def test_query_past_projects(self, agent):
        # Mock HTTP response
        with patch.object(agent.http_client, 'get') as mock_get:
            mock_get.return_value = AsyncMock(
                status_code=200,
                json=lambda: {"projects": [{"id": "1", "name": "Test"}]},
            )

            result = await agent._query_past_projects({
                "industry": "technology",
                "keywords": ["ai", "automation"],
            })

            assert "projects" in result
            assert len(result["projects"]) == 1

    def test_tool_definitions(self, agent):
        tools = agent._define_tools()

        # Verify all tools have required fields
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert tool["input_schema"]["type"] == "object"
```

### 12.2 Integration Testing

```python
@pytest.mark.integration
class TestRFPAgentIntegration:
    @pytest.fixture
    def real_agent(self):
        # Use test environment
        return RFPAgent(
            client=anthropic.AsyncAnthropic(),
            model="claude-3-haiku",  # Use faster model for tests
            erp_base_url=os.environ["TEST_ERP_URL"],
            erp_api_key=os.environ["TEST_ERP_KEY"],
        )

    @pytest.mark.asyncio
    async def test_full_rfp_analysis(self, real_agent):
        context = AgentContext(
            tenant_id="test_tenant",
            user_id="test_user",
            task="Analyze the RFP in document doc_123 and identify key requirements",
        )

        result = await real_agent.run(context)

        assert result.success
        assert "requirements" in result.output.lower()
```

### 12.3 Prompt Testing

```python
class TestSystemPrompts:
    def test_rfp_agent_prompt_structure(self):
        agent = RFPAgent(...)
        prompt = agent.system_prompt

        # Verify key sections
        assert "Your role is to" in prompt
        assert "Capabilities" in prompt or "## " in prompt

        # Verify no hallucination triggers
        assert "I don't know" not in prompt
        assert "make up" not in prompt

    def test_specialized_prompt_includes_vertical(self):
        agent = InfluencerAgent(..., vertical="beauty")
        prompt = agent.system_prompt

        assert "beauty" in prompt.lower()
        assert "influencer" in prompt.lower()
```

### 12.4 Tool Schema Validation

```python
import jsonschema

class TestToolSchemas:
    def test_all_tools_have_valid_schemas(self):
        agent = RFPAgent(...)

        for tool in agent._define_tools():
            schema = tool["input_schema"]

            # Validate schema structure
            assert schema["type"] == "object"
            assert "properties" in schema

            # Validate JSON Schema compliance
            jsonschema.Draft7Validator.check_schema(schema)
```

---

## 13. Deployment & Operations

### 13.1 Configuration

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Anthropic
    anthropic_api_key: str
    model: str = "claude-3-opus-20240229"

    # ERP
    erp_base_url: str
    erp_api_key: str

    # Performance
    max_concurrent_agents: int = 10
    tool_timeout_seconds: int = 30
    max_iterations: int = 20

    class Config:
        env_file = ".env"

settings = Settings()
```

### 13.2 Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 13.3 Monitoring Metrics

```python
from prometheus_client import Counter, Histogram

# Metrics
agent_requests = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['agent_name', 'status'],
)

agent_latency = Histogram(
    'agent_latency_seconds',
    'Agent execution latency',
    ['agent_name'],
)

tool_executions = Counter(
    'tool_executions_total',
    'Total tool executions',
    ['agent_name', 'tool_name', 'status'],
)

# Usage in agent
async def run(self, context: AgentContext) -> AgentResult:
    with agent_latency.labels(agent_name=self.name).time():
        try:
            result = await self._run_internal(context)
            agent_requests.labels(agent_name=self.name, status="success").inc()
            return result
        except Exception as e:
            agent_requests.labels(agent_name=self.name, status="error").inc()
            raise
```

### 13.4 Health Checks

```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents_available": len(REGISTERED_AGENTS),
    }

@router.get("/health/ready")
async def readiness_check():
    # Check dependencies
    checks = {
        "anthropic": await check_anthropic_connection(),
        "erp": await check_erp_connection(),
    }

    all_healthy = all(checks.values())
    return {
        "ready": all_healthy,
        "checks": checks,
    }
```

---

## 14. Best Practices

### 14.1 System Prompt Guidelines

| Do | Don't |
|-----|-------|
| Be specific about capabilities | Be vague about what agent can do |
| Include domain expertise | Assume common knowledge |
| Define output format expectations | Leave format ambiguous |
| Specify error handling behavior | Ignore edge cases |
| Use structured sections (##) | Write as prose |

### 14.2 Tool Design Guidelines

| Do | Don't |
|-----|-------|
| Write descriptive tool descriptions | Use terse descriptions |
| Include parameter descriptions | Rely on parameter names alone |
| Return structured data | Return unstructured strings |
| Handle errors gracefully | Let exceptions propagate |
| Use appropriate timeouts | Use infinite timeouts |

### 14.3 Security Guidelines

```python
# ✅ Good: Validate and sanitize inputs
async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
    # Validate tenant access
    if not await self._verify_tenant_access(tool_input.get("resource_id")):
        return {"error": "Access denied"}

    # Sanitize inputs
    if "query" in tool_input:
        tool_input["query"] = self._sanitize_query(tool_input["query"])

    return await self._do_execute(tool_name, tool_input)

# ✅ Good: Never expose raw credentials
def _define_tools(self) -> list[dict]:
    return [{
        "name": "connect_platform",
        "description": "Connect to external platform (OAuth flow)",
        "input_schema": {
            "properties": {
                "platform": {"type": "string"},
                # DON'T include raw credential fields
                # "api_key": {"type": "string"},  ❌
            },
        },
    }]
```

### 14.4 Performance Guidelines

```python
# ✅ Good: Parallel tool execution when possible
async def _batch_operation(self, items: list) -> list:
    tasks = [self._process_item(item) for item in items]
    return await asyncio.gather(*tasks)

# ✅ Good: Connection pooling
def __init__(self, ...):
    self.http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_connections=100),
        ...
    )

# ✅ Good: Appropriate timeouts
self.http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0, connect=5.0, read=25.0),
)
```

---

## 15. Troubleshooting

### 15.1 Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Agent loops** | Agent repeats same action | Add loop detection, max iterations |
| **Wrong tool selection** | Agent uses wrong tool | Improve tool descriptions |
| **Timeout errors** | Tool execution times out | Increase timeout, optimize query |
| **Hallucination** | Agent invents data | Ground in tool results, validate |
| **Context loss** | Agent forgets info | Improve context management |
| **Format errors** | Wrong output format | Add examples to prompt |

### 15.2 Debugging Tools

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebuggableAgent(BaseAgent):
    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        logger.debug(f"Executing tool: {tool_name}")
        logger.debug(f"Input: {json.dumps(tool_input, indent=2)}")

        result = await super()._execute_tool(tool_name, tool_input)

        logger.debug(f"Result: {json.dumps(result, indent=2)}")
        return result
```

### 15.3 Error Recovery

```python
async def run(self, context: AgentContext) -> AgentResult:
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            return await self._run_internal(context)
        except httpx.TimeoutException:
            retry_count += 1
            if retry_count < max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
            else:
                return AgentResult(
                    success=False,
                    output="Request timed out after multiple retries",
                )
        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Error: {str(e)}",
                metadata={"error_type": type(e).__name__},
            )
```

---

## 16. Reference

### 16.1 Agent Template

```python
"""
Agent: [Name]
Purpose: [What it does]
Tools: [Number of tools]
Specializations: [Supported specializations]
"""

from typing import Any
import httpx
from .base import BaseAgent


class MyAgent(BaseAgent):
    """[Docstring describing the agent]"""

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        # Specialization options
        vertical: str = None,
        region: str = None,
        language: str = "en",
        client_id: str = None,
    ):
        self.vertical = vertical
        self.region = region
        self.language = language
        self.client_id = client_id

        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=30.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "my_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert in [domain]...."""

    def _define_tools(self) -> list[dict]:
        return [
            # Tool definitions
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "tool_1":
                return await self._tool_1_impl(tool_input)
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    # Tool implementations
    async def _tool_1_impl(self, params: dict) -> dict:
        pass

    async def close(self):
        await self.http_client.aclose()
```

### 16.2 Tool Count by Agent

| Agent | Tools | Category |
|-------|-------|----------|
| Instance Onboarding | 32 | Platform & Lifecycle |
| Instance Success | 33 | Platform & Lifecycle |
| Instance Analytics | 25 | Platform & Lifecycle |
| Channel Agent | 12 | Engagement Suite |
| Reply Agent | 10 | Engagement Suite |
| Publisher Agent | 8 | Engagement Suite |
| Commercial Agent | 8 | Business Operations |
| Content Agent | 7 | Business Operations |
| Brief Agent | 6 | Business Operations |
| RFP Agent | 5 | Business Operations |

### 16.3 API Endpoints

```
POST /api/v1/agent/execute     - Execute agent task
GET  /api/v1/agent/status/:id  - Get task status
DELETE /api/v1/agent/task/:id  - Cancel task
GET  /api/v1/agents            - List all agents
GET  /api/v1/health            - Health check
```

### 16.4 Execute Request Format

```json
{
  "agent_type": "rfp",
  "task": "Analyze this RFP and extract requirements",
  "tenant_id": "tenant-123",
  "user_id": "user-456",
  "metadata": {
    "project_id": "project-789",
    "document_url": "https://..."
  },
  "stream": false,
  "specialization": {
    "language": "en",
    "vertical": "technology",
    "region": "uae"
  }
}
```

### 16.5 Glossary

| Term | Definition |
|------|------------|
| **Agent** | AI-powered specialist performing specific tasks |
| **Tool** | Action an agent can take (API call, query, validation) |
| **System Prompt** | Instructions defining agent personality and behavior |
| **Specialization** | Configuration adapting agent for vertical/region/language |
| **Context** | Request metadata (tenant, user, project) |
| **Artifact** | Generated output (document, asset, report) |
| **Handoff** | Transfer of context between agents |
| **Gateway** | Channel-specific delivery agent (WhatsApp, Email) |

---

## Appendix A: Checklist for New Agents

- [ ] Agent class extends `BaseAgent`
- [ ] `name` property returns unique identifier
- [ ] `system_prompt` property defines behavior
- [ ] `_define_tools()` returns tool list with JSON Schema
- [ ] `_execute_tool()` handles all defined tools
- [ ] Error handling in all tool implementations
- [ ] HTTP client cleanup in `close()` method
- [ ] Unit tests for tool implementations
- [ ] Integration tests for full agent flow
- [ ] Documentation in docstring
- [ ] Registered in `__init__.py`

---

## Appendix B: Migration Guide

### From Hardcoded Logic to Agent

Before (hardcoded):
```python
def process_rfp(document):
    # Hardcoded extraction logic
    requirements = extract_requirements(document)
    # Hardcoded matching logic
    case_studies = find_matching_projects(requirements)
    # Hardcoded template
    return generate_proposal(requirements, case_studies)
```

After (agent-based):
```python
agent = RFPAgent(client, model, erp_url, erp_key)
result = await agent.run(AgentContext(
    tenant_id=tenant_id,
    user_id=user_id,
    task=f"Analyze this RFP and draft a proposal: {document_url}",
))
# Agent decides how to analyze, what to search, how to format
```

### Adding Specialization to Existing Agent

```python
# Before
class CopyAgent(BaseAgent):
    def __init__(self, client, model, erp_url, erp_key):
        ...

# After
class CopyAgent(BaseAgent):
    def __init__(
        self,
        client,
        model,
        erp_url,
        erp_key,
        language: str = "en",      # NEW
        vertical: str = None,       # NEW
        client_id: str = None,      # NEW
    ):
        self.language = language
        self.vertical = vertical
        self.client_id = client_id
        ...

    @property
    def system_prompt(self) -> str:
        base = "You are an expert copywriter."
        if self.vertical:
            base += f"\n\nSpecializing in {self.vertical} industry."
        if self.language == "ar":
            base += "\n\nGenerate all copy in Arabic."
        return base
```

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-13
**Maintained By**: SpokeStack Platform Team
**Review Cycle**: Monthly
