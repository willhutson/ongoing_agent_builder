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
9. [ERP Integration Patterns](#9-erp-integration-patterns)
10. [Advanced Patterns](#10-advanced-patterns)
11. [Testing & Validation](#11-testing--validation)
12. [Deployment & Operations](#12-deployment--operations)
13. [Best Practices](#13-best-practices)
14. [Troubleshooting](#14-troubleshooting)
15. [Reference](#15-reference)

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

## 9. ERP Integration Patterns

### 9.1 HTTP Client Setup

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

### 9.2 Common ERP Operations

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

### 9.3 Module-to-Agent Mapping

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

### 9.4 Error Handling Pattern

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

## 10. Advanced Patterns

### 10.1 Agent Chaining

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

### 10.2 Streaming Responses

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

### 10.3 Conditional Tool Access

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

### 10.4 Tool Result Caching

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

### 10.5 Handoff Pattern

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

---

## 11. Testing & Validation

### 11.1 Unit Testing Tools

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

### 11.2 Integration Testing

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

### 11.3 Prompt Testing

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

### 11.4 Tool Schema Validation

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

## 12. Deployment & Operations

### 12.1 Configuration

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

### 12.2 Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 12.3 Monitoring Metrics

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

### 12.4 Health Checks

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

## 13. Best Practices

### 13.1 System Prompt Guidelines

| Do | Don't |
|-----|-------|
| Be specific about capabilities | Be vague about what agent can do |
| Include domain expertise | Assume common knowledge |
| Define output format expectations | Leave format ambiguous |
| Specify error handling behavior | Ignore edge cases |
| Use structured sections (##) | Write as prose |

### 13.2 Tool Design Guidelines

| Do | Don't |
|-----|-------|
| Write descriptive tool descriptions | Use terse descriptions |
| Include parameter descriptions | Rely on parameter names alone |
| Return structured data | Return unstructured strings |
| Handle errors gracefully | Let exceptions propagate |
| Use appropriate timeouts | Use infinite timeouts |

### 13.3 Security Guidelines

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

### 13.4 Performance Guidelines

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

## 14. Troubleshooting

### 14.1 Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Agent loops** | Agent repeats same action | Add loop detection, max iterations |
| **Wrong tool selection** | Agent uses wrong tool | Improve tool descriptions |
| **Timeout errors** | Tool execution times out | Increase timeout, optimize query |
| **Hallucination** | Agent invents data | Ground in tool results, validate |
| **Context loss** | Agent forgets info | Improve context management |
| **Format errors** | Wrong output format | Add examples to prompt |

### 14.2 Debugging Tools

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

### 14.3 Error Recovery

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

## 15. Reference

### 15.1 Agent Template

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

### 15.2 Tool Count by Agent

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

### 15.3 API Endpoints

```
POST /api/v1/agent/execute     - Execute agent task
GET  /api/v1/agent/status/:id  - Get task status
DELETE /api/v1/agent/task/:id  - Cancel task
GET  /api/v1/agents            - List all agents
GET  /api/v1/health            - Health check
```

### 15.4 Execute Request Format

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

### 15.5 Glossary

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
