"""
Core Tool Definitions — OpenAI-compatible function schemas for spokestack-core agents.

Tools are grouped by domain and injected into agents based on the org's BillingTier:
  FREE:     TASKS_TOOLS + CONTEXT_TOOLS
  STARTER:  + PROJECTS_TOOLS
  PRO:      + BRIEFS_TOOLS
  BUSINESS: + ORDERS_TOOLS

The ONBOARDING_TOOLS are only injected into the Onboarding agent.
"""

# ══════════════════════════════════════════════════════════════
# CONTEXT GRAPH TOOLS — Always available to all core agents
# ══════════════════════════════════════════════════════════════

CONTEXT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_context",
            "description": (
                "Read context graph entries for this organization. Use this to retrieve "
                "learned information about team members, preferences, patterns, and history. "
                "Filter by category (e.g., 'team', 'preferences', 'patterns') and/or type."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by categories: team, preferences, patterns, business, clients, workflows",
                    },
                    "types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by entry types: fact, preference, pattern, entity, metric",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max entries to return (default 50)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_context",
            "description": (
                "Write a context graph entry to remember information about this organization. "
                "Use this whenever you learn something new — team member names, business preferences, "
                "workflow patterns, client details, etc. Entries are upserted by (category, key)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "entry_type": {
                        "type": "string",
                        "enum": ["fact", "preference", "pattern", "entity", "metric"],
                        "description": "Type of context entry",
                    },
                    "category": {
                        "type": "string",
                        "description": "Category: team, preferences, patterns, business, clients, workflows",
                    },
                    "key": {
                        "type": "string",
                        "description": "Unique key within category (e.g., 'team_member:sarah', 'pattern:weekly_standup')",
                    },
                    "value": {
                        "type": "string",
                        "description": "The information to store (can be JSON string for structured data)",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence score 0-1 (default 1.0)",
                    },
                },
                "required": ["entry_type", "category", "key", "value"],
            },
        },
    },
]


# ══════════════════════════════════════════════════════════════
# TASKS TOOLS — Available at FREE tier and above
# ══════════════════════════════════════════════════════════════

TASKS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": (
                "Create a new task. Tasks are flexible — anything the user considers "
                "work to be done. Set priority, assignee, and due date as appropriate."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Detailed description"},
                    "status": {
                        "type": "string",
                        "enum": ["TODO", "IN_PROGRESS", "BLOCKED", "DONE"],
                        "description": "Initial status (default: TODO)",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"],
                        "description": "Priority level (default: MEDIUM)",
                    },
                    "assignee_id": {"type": "string", "description": "Team member ID to assign to"},
                    "project_id": {"type": "string", "description": "Project to associate with"},
                    "due_date": {"type": "string", "description": "Due date (ISO 8601)"},
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Labels/tags for categorization",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task. Only include fields you want to change.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID to update"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string", "enum": ["TODO", "IN_PROGRESS", "BLOCKED", "DONE"]},
                    "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"]},
                    "assignee_id": {"type": "string"},
                    "due_date": {"type": "string"},
                    "labels": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete (sets status to DONE).",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID to complete"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": (
                "List tasks with optional filters. Use to see what's on the board, "
                "check someone's workload, or find tasks by status/project."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["TODO", "IN_PROGRESS", "BLOCKED", "DONE"]},
                    "assignee_id": {"type": "string"},
                    "project_id": {"type": "string"},
                    "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"]},
                    "limit": {"type": "integer", "description": "Max results (default 50)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assign_task",
            "description": "Assign or reassign a task to a team member.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "assignee_id": {"type": "string", "description": "Team member ID"},
                },
                "required": ["task_id", "assignee_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_tasks",
            "description": "Search tasks by title or description text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search text"},
                    "limit": {"type": "integer", "description": "Max results (default 20)"},
                },
                "required": ["query"],
            },
        },
    },
]


# ══════════════════════════════════════════════════════════════
# PROJECTS TOOLS — Available at STARTER tier and above
# ══════════════════════════════════════════════════════════════

PROJECTS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_project",
            "description": "Create a new project to organize related tasks, phases, and milestones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Project name"},
                    "description": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["PLANNING", "ACTIVE", "ON_HOLD", "COMPLETED", "CANCELLED"],
                    },
                    "start_date": {"type": "string", "description": "Start date (ISO 8601)"},
                    "end_date": {"type": "string", "description": "End date (ISO 8601)"},
                    "owner_id": {"type": "string", "description": "Project owner/lead"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_phase",
            "description": "Add a phase to a project. Phases organize work into stages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "name": {"type": "string", "description": "Phase name (e.g., 'Discovery', 'Design', 'Build')"},
                    "description": {"type": "string"},
                    "order": {"type": "integer", "description": "Phase sequence number"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                },
                "required": ["project_id", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_milestone",
            "description": "Add a milestone to a project. Milestones mark key deliverable dates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "name": {"type": "string", "description": "Milestone name (e.g., 'Design Review', 'Beta Launch')"},
                    "description": {"type": "string"},
                    "due_date": {"type": "string", "description": "Target date (ISO 8601)"},
                },
                "required": ["project_id", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_canvas",
            "description": (
                "Create a workflow canvas (WfCanvas) for a project. Pass an ordered list of nodes "
                "representing workflow steps. Nodes are created sequentially to preserve ordering."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["STEP", "DECISION", "PARALLEL", "HANDOFF", "REVIEW"],
                                },
                                "label": {"type": "string"},
                                "description": {"type": "string"},
                                "config": {"type": "object", "description": "Node-specific configuration"},
                            },
                            "required": ["label"],
                        },
                    },
                },
                "required": ["project_id", "nodes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_status",
            "description": (
                "Get full project status including phases, milestones, and task summary counts. "
                "Use for project health checks and status updates."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                },
                "required": ["project_id"],
            },
        },
    },
]


# ══════════════════════════════════════════════════════════════
# BRIEFS TOOLS — Available at PRO tier and above
# ══════════════════════════════════════════════════════════════

BRIEFS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_brief",
            "description": "Create a new brief to scope and manage creative/strategic work.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["GENERAL", "CAMPAIGN", "CONTENT", "DESIGN", "VIDEO", "STRATEGY"],
                    },
                    "client_name": {"type": "string"},
                    "objectives": {"type": "array", "items": {"type": "string"}},
                    "deliverables": {"type": "array", "items": {"type": "string"}},
                    "budget": {"type": "number"},
                    "deadline": {"type": "string", "description": "ISO 8601 date"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_brief_phase",
            "description": "Add a phase to break down brief execution into stages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "brief_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "order": {"type": "integer"},
                    "deliverables": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["brief_id", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_artifact",
            "description": (
                "Generate an artifact draft for a brief — a document, copy, or other deliverable. "
                "The content is AI-generated based on the brief context."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "brief_id": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["DOCUMENT", "COPY", "DESIGN_BRIEF", "STRATEGY", "REPORT"],
                    },
                    "title": {"type": "string"},
                    "content": {"type": "string", "description": "Generated content text"},
                },
                "required": ["brief_id", "type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_for_review",
            "description": "Submit a brief artifact for review approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artifact_id": {"type": "string"},
                },
                "required": ["artifact_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_review",
            "description": "Record a review decision on a brief artifact.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artifact_id": {"type": "string"},
                    "decision": {
                        "type": "string",
                        "enum": ["APPROVED", "REJECTED", "REVISION_REQUESTED"],
                    },
                    "comments": {"type": "string"},
                },
                "required": ["artifact_id", "decision"],
            },
        },
    },
]


# ══════════════════════════════════════════════════════════════
# ORDERS TOOLS — Available at BUSINESS tier and above
# ══════════════════════════════════════════════════════════════

ORDERS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_customer",
            "description": "Create a new customer record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "company": {"type": "string"},
                    "address": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "Create a new order for a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "unit_price": {"type": "number"},
                            },
                        },
                    },
                    "subtotal": {"type": "number"},
                    "tax": {"type": "number"},
                    "total": {"type": "number"},
                    "currency": {"type": "string", "description": "ISO 4217 (default: USD)"},
                    "notes": {"type": "string"},
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_order",
            "description": "Update an existing order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["PENDING", "CONFIRMED", "IN_PROGRESS", "SHIPPED", "DELIVERED", "CANCELLED"],
                    },
                    "items": {"type": "array", "items": {"type": "object"}},
                    "subtotal": {"type": "number"},
                    "tax": {"type": "number"},
                    "total": {"type": "number"},
                    "notes": {"type": "string"},
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_invoice",
            "description": "Generate an invoice from an order. Creates a new invoice record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_payment",
            "description": "Record a payment against an invoice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string"},
                    "amount": {"type": "number"},
                    "method": {
                        "type": "string",
                        "enum": ["BANK_TRANSFER", "CREDIT_CARD", "CASH", "CHECK", "OTHER"],
                    },
                    "reference": {"type": "string", "description": "Payment reference/transaction ID"},
                    "paid_at": {"type": "string", "description": "Payment date (ISO 8601)"},
                },
                "required": ["invoice_id", "amount"],
            },
        },
    },
]


# ══════════════════════════════════════════════════════════════
# TOOL NAME SETS — For dispatch routing in BaseAgent
# ══════════════════════════════════════════════════════════════

CONTEXT_TOOL_NAMES = {t["function"]["name"] for t in CONTEXT_TOOLS}
TASKS_TOOL_NAMES = {t["function"]["name"] for t in TASKS_TOOLS}
PROJECTS_TOOL_NAMES = {t["function"]["name"] for t in PROJECTS_TOOLS}
BRIEFS_TOOL_NAMES = {t["function"]["name"] for t in BRIEFS_TOOLS}
ORDERS_TOOL_NAMES = {t["function"]["name"] for t in ORDERS_TOOLS}

# Union of all core tool names (for dispatch routing)
CORE_TOOL_NAMES = (
    CONTEXT_TOOL_NAMES | TASKS_TOOL_NAMES | PROJECTS_TOOL_NAMES |
    BRIEFS_TOOL_NAMES | ORDERS_TOOL_NAMES
)


# ══════════════════════════════════════════════════════════════
# TIER → TOOL GROUPS — Maps billing tier to available tool groups
# ══════════════════════════════════════════════════════════════

TIER_TOOL_MAP: dict[str, list[list[dict]]] = {
    "FREE":     [TASKS_TOOLS, CONTEXT_TOOLS],
    "STARTER":  [TASKS_TOOLS, PROJECTS_TOOLS, CONTEXT_TOOLS],
    "PRO":      [TASKS_TOOLS, PROJECTS_TOOLS, BRIEFS_TOOLS, CONTEXT_TOOLS],
    "BUSINESS": [TASKS_TOOLS, PROJECTS_TOOLS, BRIEFS_TOOLS, ORDERS_TOOLS, CONTEXT_TOOLS],
}


# ══════════════════════════════════════════════════════════════
# AGENT → CORE TOOL NAMES — Which core tools each agent type uses
# ══════════════════════════════════════════════════════════════

AGENT_CORE_TOOL_MAP: dict[str, set[str]] = {
    "core_onboarding": TASKS_TOOL_NAMES | PROJECTS_TOOL_NAMES | CONTEXT_TOOL_NAMES,
    "core_tasks":      TASKS_TOOL_NAMES | CONTEXT_TOOL_NAMES,
    "core_projects":   PROJECTS_TOOL_NAMES | TASKS_TOOL_NAMES | CONTEXT_TOOL_NAMES,
    "core_briefs":     BRIEFS_TOOL_NAMES | TASKS_TOOL_NAMES | CONTEXT_TOOL_NAMES,
    "core_orders":     ORDERS_TOOL_NAMES | CONTEXT_TOOL_NAMES,
}


# ══════════════════════════════════════════════════════════════
# INTENT PATTERNS — For MC Router classification
# ══════════════════════════════════════════════════════════════

CORE_INTENT_PATTERNS: dict[str, list[str]] = {
    "core_tasks": [
        "create task", "add task", "todo", "to-do", "assign",
        "what's on my plate", "task list", "mark done", "complete task",
        "what do I need to do", "workload", "checklist",
    ],
    "core_projects": [
        "project", "phase", "milestone", "workflow", "canvas",
        "timeline", "project status", "kickoff", "planning",
        "gantt", "roadmap", "deliverable",
    ],
    "core_briefs": [
        "brief", "scope", "proposal", "creative brief",
        "deliverables", "objectives", "review", "approval",
        "artifact", "document", "copy",
    ],
    "core_orders": [
        "order", "invoice", "payment", "customer",
        "purchase", "bill", "receipt", "pricing",
        "quote", "estimate",
    ],
}
