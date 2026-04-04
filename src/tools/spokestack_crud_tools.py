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
        "description": "List all invoices (via orders with invoice data)",
        "parameters": {"status": {"type": "string", "in": "query"}},
        "method": "GET",
        "path": "/api/v1/orders",
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

    # ══════════════════════════════════════════════════════
    # MARKETPLACE MODULE TOOLS
    # ══════════════════════════════════════════════════════

    # ── Board Manager ──────────────────────────────
    "create_board": {
        "description": "Create a new project board (kanban, sprint, or release board)",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "board"},
        "parameters": {
            "key": {"type": "string", "required": True, "description": "Unique board key"},
            "value": {"type": "object", "required": True, "description": "{ name, board_type, columns[], wip_limit, project_id }"},
        },
    },
    "add_card": {
        "description": "Add a card (task) to a board",
        "method": "POST",
        "path": "/api/v1/tasks",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string"},
            "assigneeId": {"type": "string"},
            "dueDate": {"type": "string"},
            "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"]},
        },
    },
    "move_card": {
        "description": "Move a card to a different column on a board",
        "method": "PATCH",
        "path": "/api/v1/tasks/{taskId}",
        "parameters": {
            "taskId": {"type": "string", "required": True, "in": "path"},
            "status": {"type": "string", "description": "New column/status"},
        },
    },
    "list_boards": {
        "description": "List all boards for the organization",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "board", "in": "query"}},
    },
    "list_board_cards": {
        "description": "List all cards on a specific board",
        "method": "GET",
        "path": "/api/v1/tasks",
        "parameters": {"status": {"type": "string", "in": "query"}},
    },
    "create_column": {
        "description": "Add a new column to an existing board",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "board_column"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ boardId, column_name, position, wip_limit }"},
        },
    },

    # ── Workflow Designer ──────────────────────────
    "create_workflow_def": {
        "description": "Create a new workflow definition (trigger → condition → action chain)",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "workflow"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ name, trigger_event, condition, action_type, action_config, enabled }"},
        },
    },
    "list_workflows": {
        "description": "List all workflows for the organization",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "workflow", "in": "query"}},
    },
    "create_trigger": {
        "description": "Create a standalone trigger definition",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "workflow_trigger"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ name, event, condition }"},
        },
    },
    "create_action": {
        "description": "Create an action step that executes as part of a workflow",
        "method": "POST",
        "path": "/api/v1/tasks",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string"},
            "priority": {"type": "string", "default": "MEDIUM"},
        },
    },
    "activate_workflow": {
        "description": "Activate or deactivate a workflow",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "workflow"},
        "parameters": {
            "key": {"type": "string", "required": True, "description": "Workflow context entry key"},
            "value": {"type": "object", "required": True, "description": "{ enabled: true/false }"},
        },
    },

    # ── Social Listener ────────────────────────────
    "log_mention": {
        "description": "Log a brand or keyword mention from social media",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "social_mention"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ platform, author, content, sentiment, url, keywords[], client_id }"},
        },
    },
    "search_mentions": {
        "description": "Search logged social mentions",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "social_mention", "in": "query"}},
    },
    "create_alert": {
        "description": "Create a listening alert for keywords or sentiment thresholds",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "listening_alert"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ name, alert_type, keyword, sentiment, threshold_percent, notify_via }"},
        },
    },
    "generate_listening_report": {
        "description": "Generate a listening report summarizing mentions and sentiment",
        "method": "POST",
        "path": "/api/v1/briefs",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string", "required": True, "description": "Report content"},
        },
    },
    "get_sentiment_summary": {
        "description": "Get sentiment breakdown across logged mentions",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "social_mention", "in": "query"}},
    },

    # ── NPS Analyst ────────────────────────────────
    "create_survey": {
        "description": "Create a new NPS survey",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "nps_survey"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ name, question, follow_up_question, target_client_ids[], closes_at }"},
        },
    },
    "log_response": {
        "description": "Log an NPS survey response",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "nps_response"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ survey_id, score (0-10), comment, client_id, respondent_name }"},
        },
    },
    "calculate_nps": {
        "description": "Get all responses for a survey to calculate NPS",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "nps_response", "in": "query"}},
    },
    "list_surveys": {
        "description": "List all NPS surveys",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "nps_survey", "in": "query"}},
    },
    "create_followup": {
        "description": "Create a follow-up task to close the loop with a detractor",
        "method": "POST",
        "path": "/api/v1/tasks",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string"},
            "priority": {"type": "string", "default": "HIGH"},
        },
    },
    "generate_nps_report": {
        "description": "Generate an NPS report with score, trend, and recommended actions",
        "method": "POST",
        "path": "/api/v1/briefs",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string", "required": True, "description": "Report content"},
        },
    },

    # ── Chat Operator ──────────────────────────────
    "create_canned_response": {
        "description": "Create a canned response template for common chat questions",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "canned_response"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ trigger, title, body, topic, language }"},
        },
    },
    "list_canned_responses": {
        "description": "List all canned responses",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "canned_response", "in": "query"}},
    },
    "create_routing_rule": {
        "description": "Create a routing rule for chat conversations",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "chat_routing"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ name, condition_type, condition_value, route_to, priority }"},
        },
    },
    "list_conversations": {
        "description": "List chat conversations",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "chat_conversation", "in": "query"}},
    },
    "create_escalation": {
        "description": "Create an URGENT escalation task for a chat conversation",
        "method": "POST",
        "path": "/api/v1/tasks",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string"},
            "priority": {"type": "string", "default": "URGENT"},
        },
    },
    "log_conversation": {
        "description": "Log a conversation summary for audit and training",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "chat_conversation"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ client_name, channel, summary, resolution, csat_score, duration_minutes }"},
        },
    },

    # ── Portal Manager ─────────────────────────────
    "create_deliverable_entry": {
        "description": "Create a deliverable entry in the client portal",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "portal_deliverable"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ title, client_id, project_id, deliverable_type, file_url, status }"},
        },
    },
    "list_deliverables": {
        "description": "List deliverables in the client portal",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "portal_deliverable", "in": "query"}},
    },
    "submit_deliverable_for_review": {
        "description": "Submit a deliverable for client review (creates a brief with IN_REVIEW)",
        "method": "POST",
        "path": "/api/v1/briefs",
        "parameters": {
            "title": {"type": "string", "required": True, "description": "Review request title"},
            "description": {"type": "string"},
            "clientId": {"type": "string"},
        },
    },
    "update_approval_status": {
        "description": "Update the approval status of a brief/review request",
        "method": "PATCH",
        "path": "/api/v1/briefs/{briefId}",
        "parameters": {
            "briefId": {"type": "string", "required": True, "in": "path"},
            "status": {"type": "string", "required": True, "enum": ["COMPLETED", "DRAFT", "IN_REVIEW"]},
        },
    },
    "create_client_update": {
        "description": "Create a client update notification in the portal",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "client_update"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ client_id, subject, body, update_type, related_deliverable_id }"},
        },
    },

    # ── Delegation Coordinator ─────────────────────
    "delegate_task": {
        "description": "Delegate a new task to a specific team member",
        "method": "POST",
        "path": "/api/v1/tasks",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string"},
            "assigneeId": {"type": "string", "required": True},
            "dueDate": {"type": "string"},
            "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"]},
        },
    },
    "reassign_task": {
        "description": "Reassign an existing task to a different team member",
        "method": "PATCH",
        "path": "/api/v1/tasks/{taskId}",
        "parameters": {
            "taskId": {"type": "string", "required": True, "in": "path"},
            "assigneeId": {"type": "string", "required": True},
        },
    },
    "check_workload": {
        "description": "Check task workload for a team member or all members",
        "method": "GET",
        "path": "/api/v1/tasks",
        "parameters": {
            "assigneeId": {"type": "string", "in": "query"},
            "status": {"type": "string", "in": "query"},
        },
    },
    "create_escalation_rule": {
        "description": "Create an escalation rule for overdue tasks",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "escalation_rule"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ name, trigger_after_hours, level_1_notify, level_2_notify, applies_to_priority }"},
        },
    },
    "list_escalation_rules": {
        "description": "List all active escalation rules",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "escalation_rule", "in": "query"}},
    },
    "flag_overdue": {
        "description": "Get all overdue tasks",
        "method": "GET",
        "path": "/api/v1/tasks",
        "parameters": {
            "status": {"type": "string", "default": "TODO", "in": "query"},
        },
    },

    # ── Access Admin ───────────────────────────────
    "create_role": {
        "description": "Create a custom access role with specific permissions",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "access_role"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ name, base_role, module_access[], permissions[] }"},
        },
    },
    "list_roles": {
        "description": "List all roles (built-in and custom)",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "access_role", "in": "query"}},
    },
    "assign_permission": {
        "description": "Assign a specific permission to a role or user",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "permission"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ permission, target_type, target_id, reason, expires_at }"},
        },
    },
    "audit_access": {
        "description": "Retrieve access log entries for audit",
        "method": "GET",
        "path": "/api/v1/context",
        "parameters": {"category": {"type": "string", "default": "access_log", "in": "query"}},
    },
    "log_access_event": {
        "description": "Log an access event for compliance",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "access_log"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ event_type, user_id, target_user_id, resource, details }"},
        },
    },

    # ── Module Builder ─────────────────────────────
    "create_module_manifest": {
        "description": "Create a module manifest definition",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "module_manifest"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ module_type, name, description, category, agent_type, tier, tools[], icon, color }"},
        },
    },
    "list_modules": {
        "description": "List all modules installed for the organization",
        "method": "GET",
        "path": "/api/v1/modules/installed",
        "parameters": {},
    },
    "scaffold_agent_config": {
        "description": "Generate and store an agent configuration scaffold",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "agent_config"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ module_type, canonical_type, mc_type, system_prompt_summary, tools[] }"},
        },
    },
    "create_module_page_template": {
        "description": "Generate and store a Next.js page template for a new module",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "ENTITY", "category": "module_template"},
        "parameters": {
            "key": {"type": "string", "required": True},
            "value": {"type": "object", "required": True, "description": "{ module_type, module_name, tabs[], agent_type, description }"},
        },
    },

    # ══════════════════════════════════════════════════════
    # MODULE BUILDER TOOLS (local execution — not HTTP)
    # ══════════════════════════════════════════════════════

    "scaffold_module": {
        "description": "Scaffold a complete module package from a conversation — generates manifest, tools, system prompt, and pricing",
        "handler": "local",  # Routed to ModuleBuilderService, not HTTP
        "parameters": {
            "name": {"type": "string", "required": True, "description": "Human-readable module name"},
            "slug": {"type": "string", "required": True, "description": "URL-safe slug in kebab-case"},
            "module_type": {"type": "string", "required": True, "description": "Module type in UPPER_SNAKE_CASE"},
            "entity_name": {"type": "string", "required": True, "description": "Singular entity name"},
            "entity_name_plural": {"type": "string", "required": True, "description": "Plural entity name"},
            "fields": {"type": "array", "required": True, "description": "List of { name, type, required, description }"},
            "description": {"type": "string", "description": "Full description"},
            "category": {"type": "string", "description": "Category: Operations, Sales, HR, Finance, Marketing, Legal"},
            "pricing_type": {"type": "string", "description": "free, paid, or subscription"},
            "price_cents": {"type": "number", "description": "Price in cents for paid modules"},
            "monthly_price_cents": {"type": "number", "description": "Monthly price in cents for subscription"},
        },
    },
    "validate_module": {
        "description": "Validate a module package for security and completeness — returns blockers and warnings",
        "handler": "local",
        "parameters": {
            "module_package": {"type": "object", "required": True, "description": "The module package to validate"},
        },
    },
    "test_module": {
        "description": "Test module tools in a sandboxed environment — executes each tool with sample data",
        "handler": "local",
        "parameters": {
            "module_package": {"type": "object", "required": True, "description": "The module package to test"},
        },
    },
    "publish_module": {
        "description": "Publish a validated module to the SpokeStack Marketplace",
        "method": "POST",
        "path": "/api/v1/marketplace/publish",
        "parameters": {
            "module_package": {"type": "object", "required": True, "description": "The validated module package"},
        },
    },
    "list_my_modules": {
        "description": "List all modules published by the current organization",
        "method": "GET",
        "path": "/api/v1/marketplace/my-modules",
        "parameters": {},
    },
    "get_module_analytics": {
        "description": "Get analytics for a published module: install count, revenue, rating, churn",
        "method": "GET",
        "path": "/api/v1/marketplace/analytics/{moduleId}",
        "parameters": {
            "moduleId": {"type": "string", "required": True, "in": "path"},
        },
    },

    # ══════════════════════════════════════════════════════
    # MODULE REVIEWER TOOLS
    # ══════════════════════════════════════════════════════

    "analyze_tools": {
        "description": "Static analysis of module tool definitions for security issues",
        "handler": "local",
        "parameters": {
            "tools": {"type": "array", "required": True, "description": "Tool definitions to analyze"},
            "module_id": {"type": "string", "required": True, "description": "Module ID being reviewed"},
        },
    },
    "analyze_prompt": {
        "description": "Check system prompt for injection patterns, impersonation, and quality issues",
        "handler": "local",
        "parameters": {
            "system_prompt": {"type": "string", "required": True, "description": "System prompt to analyze"},
            "module_id": {"type": "string", "required": True, "description": "Module ID being reviewed"},
        },
    },
    "check_duplicates": {
        "description": "Search the marketplace for modules similar to the submitted one",
        "method": "GET",
        "path": "/api/v1/marketplace/browse",
        "parameters": {
            "q": {"type": "string", "required": True, "in": "query", "description": "Module name to search for"},
            "category": {"type": "string", "in": "query"},
        },
    },
    "generate_review": {
        "description": "Produce the final structured review report for a module",
        "method": "POST",
        "path": "/api/v1/context",
        "fixed_body_merge": {"entryType": "INSIGHT", "category": "module_review"},
        "parameters": {
            "key": {"type": "string", "required": True, "description": "Review key e.g. review_{module_id}"},
            "value": {"type": "object", "required": True, "description": "{ module_id, security_score, quality_score, issues_found[], recommendations[], overall_assessment }"},
        },
    },
    "approve_module": {
        "description": "Mark a module as approved and publish it to the marketplace",
        "method": "POST",
        "path": "/api/v1/marketplace/review/{moduleId}",
        "parameters": {
            "moduleId": {"type": "string", "required": True, "in": "path"},
            "decision": {"type": "string", "default": "approved"},
            "securityNotes": {"type": "string"},
        },
    },
    "reject_module": {
        "description": "Reject a module submission with detailed feedback",
        "method": "POST",
        "path": "/api/v1/marketplace/review/{moduleId}",
        "parameters": {
            "moduleId": {"type": "string", "required": True, "in": "path"},
            "decision": {"type": "string", "default": "rejected"},
            "feedback": {"type": "string", "required": True},
            "securityNotes": {"type": "string"},
        },
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
