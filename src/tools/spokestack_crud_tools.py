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

    # ══════════════════════════════════════════════════════
    # PR / COMMUNICATIONS TOOLS
    # ══════════════════════════════════════════════════════

    # ── Media Relations ────────────────────────────
    "add_journalist": {
        "description": "Add a journalist to the media database",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "journalist"},
        "parameters": {
            "key": {"type": "string", "required": True, "description": "Unique key like journalist_sarah_ahmed"},
            "value": {"type": "object", "required": True, "description": "{ name, outlet, beat, email, phone, twitter, linkedin, relationship_score (1-10), notes }"},
        },
    },
    "search_journalists": {
        "description": "Search the journalist database by beat, outlet, or name",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {
            "category": {"type": "string", "default": "journalist", "in": "query"},
            "entryType": {"type": "string", "default": "ENTITY", "in": "query"},
        },
    },
    "create_media_list": {
        "description": "Create a named media list (grouped journalists for outreach)",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "media_list"},
        "parameters": {
            "key": {"type": "string", "required": True, "description": "Unique key like list_tech_journalists_uae"},
            "value": {"type": "object", "required": True, "description": "{ name, description, journalistKeys: string[], purpose }"},
        },
    },
    "create_pitch": {
        "description": "Create a media pitch (stored as a Brief)",
        "method": "POST",
        "path": "/api/v1/briefs",
        "parameters": {
            "title": {"type": "string", "required": True, "description": "Pitch headline"},
            "description": {"type": "string", "description": "Pitch body/angle"},
            "clientId": {"type": "string", "description": "Client the pitch is for"},
        },
    },
    "log_coverage": {
        "description": "Log a media coverage hit",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "coverage"},
        "parameters": {
            "key": {"type": "string", "required": True, "description": "Unique key like coverage_20260403_thenational"},
            "value": {"type": "object", "required": True, "description": "{ headline, outlet, journalist, url, date, sentiment, reach_estimate, ave_aed }"},
        },
    },
    "get_coverage_report": {
        "description": "Get all coverage entries for analysis",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "coverage", "in": "query"}},
    },
    "list_pitches": {
        "description": "List all active pitches",
        "method": "GET",
        "path": "/api/v1/briefs",
        "parameters": {"status": {"type": "string", "in": "query"}},
    },
    "create_followup_task": {
        "description": "Create a follow-up task for a pitch or action item",
        "method": "POST",
        "path": "/api/v1/tasks",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string"},
            "dueDate": {"type": "string", "description": "ISO date"},
            "priority": {"type": "string", "default": "MEDIUM"},
        },
    },

    # ── Press Releases ─────────────────────────────
    "draft_press_release": {
        "description": "Create a new press release draft",
        "method": "POST",
        "path": "/api/v1/briefs",
        "parameters": {
            "title": {"type": "string", "required": True, "description": "PR headline"},
            "description": {"type": "string", "required": True, "description": "Full press release text"},
            "clientId": {"type": "string"},
        },
    },
    "update_press_release": {
        "description": "Update/edit a press release draft",
        "method": "PATCH",
        "path": "/api/v1/briefs/{briefId}",
        "parameters": {
            "briefId": {"type": "string", "required": True, "in": "path"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "status": {"type": "string", "enum": ["DRAFT", "ACTIVE", "IN_REVIEW", "COMPLETED"]},
        },
    },
    "submit_for_approval": {
        "description": "Submit a press release for client approval",
        "method": "PATCH",
        "path": "/api/v1/briefs/{briefId}",
        "parameters": {"briefId": {"type": "string", "required": True, "in": "path"}},
        "fixed_body": {"status": "IN_REVIEW"},
    },
    "approve_release": {
        "description": "Approve a press release for distribution",
        "method": "PATCH",
        "path": "/api/v1/briefs/{briefId}",
        "parameters": {"briefId": {"type": "string", "required": True, "in": "path"}},
        "fixed_body": {"status": "COMPLETED"},
    },
    "list_press_releases": {
        "description": "List all press releases",
        "method": "GET",
        "path": "/api/v1/briefs",
        "parameters": {"status": {"type": "string", "in": "query"}},
    },
    "schedule_distribution": {
        "description": "Schedule a press release for distribution to a media list",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "pr_distribution"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ briefId, mediaListKey, scheduledDate, embargoDate }"},
        },
    },

    # ── Crisis Management ──────────────────────────
    "activate_crisis": {
        "description": "Create a crisis situation (as a Project)",
        "method": "POST",
        "path": "/api/v1/projects",
        "parameters": {
            "name": {"type": "string", "required": True, "description": "Crisis name/identifier"},
            "description": {"type": "string", "required": True, "description": "Situation summary"},
        },
    },
    "draft_holding_statement": {
        "description": "Draft an immediate holding statement",
        "method": "POST",
        "path": "/api/v1/briefs",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string", "required": True, "description": "Holding statement text"},
            "clientId": {"type": "string"},
        },
    },
    "map_stakeholder": {
        "description": "Add a stakeholder to the crisis map",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "crisis_stakeholder"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ name, role, contact, priority (1-5), status, notes }"},
        },
    },
    "create_crisis_task": {
        "description": "Create an urgent task in the crisis response",
        "method": "POST",
        "path": "/api/v1/tasks",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string"},
            "priority": {"type": "string", "default": "URGENT"},
            "dueDate": {"type": "string"},
        },
    },
    "update_crisis_status": {
        "description": "Update the crisis situation status",
        "method": "PATCH",
        "path": "/api/v1/projects/{projectId}",
        "parameters": {
            "projectId": {"type": "string", "required": True, "in": "path"},
            "status": {"type": "string", "required": True, "enum": ["PLANNING", "ACTIVE", "ON_HOLD", "COMPLETED"]},
        },
    },
    "get_stakeholders": {
        "description": "Get all stakeholders for the current crisis",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "crisis_stakeholder", "in": "query"}},
    },

    # ── Client Reporting ───────────────────────────
    "generate_report": {
        "description": "Create a monthly client report brief",
        "method": "POST",
        "path": "/api/v1/briefs",
        "parameters": {
            "title": {"type": "string", "required": True, "description": "e.g. 'March 2026 Monthly Report - Client'"},
            "description": {"type": "string", "required": True, "description": "Full report content"},
            "clientId": {"type": "string", "required": True},
        },
    },
    "get_coverage_data": {
        "description": "Get all coverage entries for a period",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "coverage", "in": "query"}},
    },
    "get_activity_data": {
        "description": "Get recent workspace activity for the report",
        "method": "GET",
        "path": "/api/v1/activity",
        "parameters": {"limit": {"type": "integer", "default": 50, "in": "query"}},
    },
    "get_client_briefs": {
        "description": "Get all briefs for a specific client",
        "method": "GET",
        "path": "/api/v1/briefs",
        "parameters": {},
    },
    "save_report_metrics": {
        "description": "Save calculated report metrics to context",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "INSIGHT", "category": "report_metric"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ clientId, period, coverageCount, aveTotal, sovPercentage, sentimentScore }"},
        },
    },

    # ── Influencer Management ──────────────────────
    "add_influencer": {
        "description": "Add an influencer to the database",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "influencer"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ name, handle, platform, followers, engagementRate, niche, location, rateCard, pastCampaigns[] }"},
        },
    },
    "search_influencers": {
        "description": "Search the influencer database",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "influencer", "in": "query"}},
    },
    "create_influencer_campaign": {
        "description": "Create an influencer campaign (as a Project)",
        "method": "POST",
        "path": "/api/v1/projects",
        "parameters": {
            "name": {"type": "string", "required": True},
            "description": {"type": "string"},
        },
    },
    "create_deliverable": {
        "description": "Create a deliverable task for an influencer",
        "method": "POST",
        "path": "/api/v1/tasks",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string"},
            "dueDate": {"type": "string"},
            "priority": {"type": "string", "default": "HIGH"},
        },
    },
    "create_influencer_contract": {
        "description": "Create a contract/payment order for an influencer",
        "method": "POST",
        "path": "/api/v1/orders",
        "parameters": {
            "clientId": {"type": "string", "required": True, "description": "The brand client paying for this"},
            "items": {"type": "array", "required": True, "description": "[{description, quantity, unitPriceCents}]"},
            "notes": {"type": "string"},
        },
    },
    "list_campaigns": {
        "description": "List influencer campaigns",
        "method": "GET",
        "path": "/api/v1/projects",
        "parameters": {"status": {"type": "string", "in": "query"}},
    },

    # ── Event Planning ─────────────────────────────
    "create_event": {
        "description": "Create a new event (as a Project)",
        "method": "POST",
        "path": "/api/v1/projects",
        "parameters": {
            "name": {"type": "string", "required": True, "description": "Event name"},
            "description": {"type": "string", "description": "Event details, venue, format"},
        },
    },
    "add_guest": {
        "description": "Add a guest to the event guest list",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "event_guest"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ eventProjectId, name, email, company, tier, rsvpStatus, dietary, tableAssignment }"},
        },
    },
    "get_guest_list": {
        "description": "Get the guest list for an event",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "event_guest", "in": "query"}},
    },
    "create_run_of_show_item": {
        "description": "Add an item to the event run of show",
        "method": "POST",
        "path": "/api/v1/tasks",
        "parameters": {
            "title": {"type": "string", "required": True, "description": "e.g. '7:00 PM - Doors open'"},
            "description": {"type": "string", "description": "Details, responsible person"},
            "priority": {"type": "string", "default": "HIGH"},
        },
    },
    "add_vendor": {
        "description": "Add a vendor/supplier for the event (as an Order)",
        "method": "POST",
        "path": "/api/v1/orders",
        "parameters": {
            "clientId": {"type": "string", "description": "The brand client funding this event"},
            "items": {"type": "array", "required": True, "description": "[{description, quantity, unitPriceCents}]"},
            "notes": {"type": "string"},
        },
    },
    "update_event_status": {
        "description": "Update the event status",
        "method": "PATCH",
        "path": "/api/v1/projects/{projectId}",
        "parameters": {
            "projectId": {"type": "string", "required": True, "in": "path"},
            "status": {"type": "string", "required": True},
        },
    },
    "list_events": {
        "description": "List all events",
        "method": "GET",
        "path": "/api/v1/projects",
        "parameters": {},
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
