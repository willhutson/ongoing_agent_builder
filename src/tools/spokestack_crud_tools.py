"""
SpokeStack CRUD Tool Definitions — 30+ tools mapped to spokestack-core REST APIs.

Each tool = one CRUD operation. The tool executor resolves path params,
query params, and body from the parameter definitions.

Tools are assigned to agents via AGENT_TOOLS in agent_tool_assignment.py.
"""

import os

SPOKESTACK_CORE_URL = os.environ.get("SPOKESTACK_CORE_URL", "https://spokestack-core.vercel.app")

TOOLS: dict[str, dict] = {
    # ── Tasks ──────────────────────────────────────
    "create_task": {
        "description": "Create a new task in the workspace",
        "parameters": {
            "title": {"type": "string", "required": True, "description": "Task title"},
            "description": {"type": "string", "description": "Task description"},
            "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"]},
            "status": {"type": "string", "enum": ["TODO", "IN_PROGRESS", "DONE"]},
            "assigneeId": {"type": "string", "description": "User ID to assign to"},
            "dueDate": {"type": "string", "description": "Due date in ISO format"},
        },
        "method": "POST",
        "path": "/api/v1/tasks",
    },
    "update_task": {
        "description": "Update a task's status, priority, assignee, or other fields",
        "parameters": {
            "taskId": {"type": "string", "required": True, "in": "path"},
            "status": {"type": "string", "enum": ["TODO", "IN_PROGRESS", "DONE"]},
            "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"]},
            "title": {"type": "string"},
            "assigneeId": {"type": "string"},
        },
        "method": "PATCH",
        "path": "/api/v1/tasks/{taskId}",
    },
    "complete_task": {
        "description": "Mark a task as done",
        "parameters": {"taskId": {"type": "string", "required": True, "in": "path"}},
        "method": "PATCH",
        "path": "/api/v1/tasks/{taskId}",
        "fixed_body": {"status": "DONE"},
    },
    "delete_task": {
        "description": "Delete a task permanently",
        "parameters": {"taskId": {"type": "string", "required": True, "in": "path"}},
        "method": "DELETE",
        "path": "/api/v1/tasks/{taskId}",
    },
    "list_tasks": {
        "description": "List tasks with optional status filter",
        "parameters": {
            "status": {"type": "string", "in": "query"},
            "assigneeId": {"type": "string", "in": "query"},
        },
        "method": "GET",
        "path": "/api/v1/tasks",
    },

    # ── Projects ───────────────────────────────────
    "create_project": {
        "description": "Create a new project",
        "parameters": {
            "name": {"type": "string", "required": True},
            "description": {"type": "string"},
            "startDate": {"type": "string"},
            "endDate": {"type": "string"},
            "clientId": {"type": "string"},
        },
        "method": "POST",
        "path": "/api/v1/projects",
    },
    "update_project": {
        "description": "Update a project's details or status",
        "parameters": {
            "projectId": {"type": "string", "required": True, "in": "path"},
            "name": {"type": "string"},
            "status": {"type": "string", "enum": ["PLANNING", "ACTIVE", "ON_HOLD", "COMPLETED", "ARCHIVED"]},
            "description": {"type": "string"},
        },
        "method": "PATCH",
        "path": "/api/v1/projects/{projectId}",
    },
    "complete_project": {
        "description": "Mark a project as completed",
        "parameters": {"projectId": {"type": "string", "required": True, "in": "path"}},
        "method": "PATCH",
        "path": "/api/v1/projects/{projectId}",
        "fixed_body": {"status": "COMPLETED"},
    },
    "list_projects": {
        "description": "List all projects, optionally filtered by status",
        "parameters": {"status": {"type": "string", "in": "query"}},
        "method": "GET",
        "path": "/api/v1/projects",
    },

    # ── Briefs ─────────────────────────────────────
    "create_brief": {
        "description": "Create a new creative brief",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string"},
            "clientId": {"type": "string"},
        },
        "method": "POST",
        "path": "/api/v1/briefs",
    },
    "update_brief": {
        "description": "Update a brief's title, description, or status",
        "parameters": {
            "briefId": {"type": "string", "required": True, "in": "path"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "status": {"type": "string", "enum": ["DRAFT", "ACTIVE", "IN_REVIEW", "COMPLETED", "ARCHIVED"]},
        },
        "method": "PATCH",
        "path": "/api/v1/briefs/{briefId}",
    },
    "approve_brief": {
        "description": "Approve a brief — moves status to COMPLETED",
        "parameters": {"briefId": {"type": "string", "required": True, "in": "path"}},
        "method": "PATCH",
        "path": "/api/v1/briefs/{briefId}",
        "fixed_body": {"status": "COMPLETED"},
    },
    "request_revisions": {
        "description": "Send a brief back for revisions — moves status to DRAFT",
        "parameters": {"briefId": {"type": "string", "required": True, "in": "path"}},
        "method": "PATCH",
        "path": "/api/v1/briefs/{briefId}",
        "fixed_body": {"status": "DRAFT"},
    },
    "list_briefs": {
        "description": "List all briefs, optionally filtered by status",
        "parameters": {"status": {"type": "string", "in": "query"}},
        "method": "GET",
        "path": "/api/v1/briefs",
    },

    # ── Orders ─────────────────────────────────────
    "create_order": {
        "description": "Create an order for a client with line items",
        "parameters": {
            "clientId": {"type": "string", "required": True},
            "items": {"type": "array", "required": True, "description": "Array of {description, quantity, unitPriceCents}"},
            "notes": {"type": "string"},
        },
        "method": "POST",
        "path": "/api/v1/orders",
    },
    "update_order_status": {
        "description": "Update an order's fulfillment status",
        "parameters": {
            "orderId": {"type": "string", "required": True, "in": "path"},
            "status": {"type": "string", "required": True, "enum": ["PENDING", "CONFIRMED", "IN_PROGRESS", "COMPLETED", "CANCELED"]},
        },
        "method": "PATCH",
        "path": "/api/v1/orders/{orderId}",
    },
    "generate_invoice": {
        "description": "Generate an invoice from a completed order",
        "parameters": {"orderId": {"type": "string", "required": True, "in": "path"}},
        "method": "POST",
        "path": "/api/v1/orders/{orderId}/invoice",
    },
    "list_orders": {
        "description": "List all orders",
        "parameters": {"status": {"type": "string", "in": "query"}},
        "method": "GET",
        "path": "/api/v1/orders",
    },

    # ── Clients ────────────────────────────────────
    "create_client": {
        "description": "Create a new client",
        "parameters": {
            "name": {"type": "string", "required": True},
            "email": {"type": "string"},
            "phone": {"type": "string"},
            "company": {"type": "string"},
            "industry": {"type": "string"},
        },
        "method": "POST",
        "path": "/api/v1/clients",
    },
    "update_client": {
        "description": "Update client information",
        "parameters": {
            "clientId": {"type": "string", "required": True, "in": "path"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "company": {"type": "string"},
            "industry": {"type": "string"},
        },
        "method": "PATCH",
        "path": "/api/v1/clients/{clientId}",
    },
    "list_clients": {
        "description": "List all clients in the workspace",
        "parameters": {},
        "method": "GET",
        "path": "/api/v1/clients",
    },

    # ── Invoices ───────────────────────────────────
    "list_invoices": {
        "description": "List all invoices",
        "parameters": {"status": {"type": "string", "in": "query"}},
        "method": "GET",
        "path": "/api/v1/invoices",
    },

    # ── Context Graph ──────────────────────────────
    "read_context": {
        "description": "Read organizational context — team patterns, client info, preferences, insights",
        "parameters": {
            "category": {"type": "string", "in": "query"},
            "entryType": {"type": "string", "in": "query", "enum": ["ENTITY", "PATTERN", "PREFERENCE", "INSIGHT"]},
        },
        "method": "GET",
        "path": "/api/v1/context",
    },
    "write_context": {
        "description": "Write a new insight, pattern, or entity to the organizational context graph",
        "parameters": {
            "entryType": {"type": "string", "required": True, "enum": ["ENTITY", "PATTERN", "PREFERENCE", "INSIGHT"]},
            "category": {"type": "string", "required": True},
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True},
            "confidence": {"type": "number"},
        },
        "method": "POST",
        "path": "/api/v1/context",
    },

    # ── Modules ────────────────────────────────────
    "install_module": {
        "description": "Install a marketplace module for the workspace",
        "parameters": {"moduleType": {"type": "string", "required": True}},
        "method": "POST",
        "path": "/api/v1/modules/install",
    },
    "list_installed_modules": {
        "description": "List all installed modules",
        "parameters": {},
        "method": "GET",
        "path": "/api/v1/modules/installed",
    },

    # ── Events / Workflows ─────────────────────────
    "create_workflow": {
        "description": "Create an automation workflow (event subscription)",
        "parameters": {
            "entityType": {"type": "string", "required": True, "description": "Entity to watch: Task, Project, Brief, Order, Client, or * for all"},
            "action": {"type": "string", "required": True, "description": "Action: created, updated, deleted, status_changed, or * for all"},
            "handler": {"type": "string", "required": True, "description": "Handler: webhook:URL, agent:ID, or module:TYPE"},
        },
        "method": "POST",
        "path": "/api/v1/events/subscriptions",
    },

    # ── Team ───────────────────────────────────────
    "list_team_members": {
        "description": "List all team members in the workspace",
        "parameters": {},
        "method": "GET",
        "path": "/api/v1/members",
    },

    # ── Activity ───────────────────────────────────
    "get_recent_activity": {
        "description": "Get recent activity across all entities in the workspace",
        "parameters": {"limit": {"type": "integer", "in": "query", "default": 20}},
        "method": "GET",
        "path": "/api/v1/activity",
    },

    # ── Search ─────────────────────────────────────
    "search_workspace": {
        "description": "Search across tasks, projects, briefs, clients, and orders",
        "parameters": {
            "q": {"type": "string", "required": True, "in": "query", "description": "Search query"},
        },
        "method": "GET",
        "path": "/api/v1/search",
    },
}


def tool_to_openai_function(name: str, tool: dict) -> dict:
    """Convert a tool definition to OpenAI function-calling format."""
    params = tool.get("parameters", {})
    properties = {}
    required = []

    for param_name, param_def in params.items():
        prop: dict = {"type": param_def.get("type", "string")}
        if "description" in param_def:
            prop["description"] = param_def["description"]
        if "enum" in param_def:
            prop["enum"] = param_def["enum"]
        properties[param_name] = prop
        if param_def.get("required"):
            required.append(param_name)

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": tool["description"],
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def get_openai_tools(tool_names: list[str]) -> list[dict]:
    """Convert a list of tool names to OpenAI function-calling format."""
    return [
        tool_to_openai_function(name, TOOLS[name])
        for name in tool_names
        if name in TOOLS
    ]
