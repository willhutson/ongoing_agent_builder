"""
ERP Tool Definitions — OpenAI-compatible function definitions
that agents can call to read and write ERP module data.

Read tools are injected into ALL agents.
Write tools are selectively injected based on AGENT_WRITE_TOOL_MAP.
"""


# ══════════════════════════════════════════════════════════════
# READ TOOLS — Injected into every agent via BaseAgent
# ══════════════════════════════════════════════════════════════

ERP_READ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_client_context",
            "description": (
                "Get full client profile including brand pack, recent briefs, "
                "projects, and contacts. Use this when you need brand context "
                "or client history."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string", "description": "The client ID"},
                },
                "required": ["client_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_briefs",
            "description": (
                "List briefs for a client, optionally filtered by status. "
                "Use for questions about what briefs exist, their status, or brief history."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["DRAFT", "ACTIVE", "IN_REVIEW", "COMPLETED", "ARCHIVED"],
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_content_posts",
            "description": (
                "List content posts / calendar entries for a client within a date range."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "date_from": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                    "date_to": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "List projects for a client with their tasks and milestones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_analytics",
            "description": (
                "Get performance metrics and KPIs for a client. Use for questions "
                "about how a campaign or client is performing."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "period": {
                        "type": "string",
                        "enum": ["7d", "30d", "90d", "ytd"],
                        "default": "7d",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pending_reviews",
            "description": (
                "Get all items awaiting review for a specific user across all modules. "
                "Use for 'what's on my plate?' or 'what needs my approval?' questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_workload",
            "description": (
                "Get team workload and utilization data. "
                "Use for resource planning and capacity questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Optional team filter",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_modules",
            "description": (
                "Search across all ERP modules for a query. "
                "Use when you need to find specific records, people, or content."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "modules": {
                        "type": "string",
                        "description": "Comma-separated module filter: briefs,studio,crm,projects",
                    },
                    "client_id": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
]


# ══════════════════════════════════════════════════════════════
# WRITE TOOLS — Selectively injected per agent type
# ══════════════════════════════════════════════════════════════

ERP_WRITE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_brief",
            "description": (
                "Create a new brief in the Briefs module from your artifact data. "
                "Call this AFTER you've generated a brief artifact to persist it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "title": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["CAMPAIGN", "CONTENT", "DESIGN", "VIDEO", "SOCIAL", "STRATEGY", "OTHER"],
                    },
                    "content": {
                        "type": "object",
                        "description": "The full brief content object",
                    },
                },
                "required": ["client_id", "title", "type", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_content_posts",
            "description": (
                "Create content posts in Studio from a calendar artifact. "
                "Pass the entries array from your calendar artifact."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "posts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "body": {"type": "string"},
                                "scheduledFor": {"type": "string"},
                                "contentType": {"type": "string"},
                                "platforms": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                    },
                },
                "required": ["client_id", "posts"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_project",
            "description": "Create a project with tasks and milestones in the Projects module.",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "tasks": {"type": "array", "items": {"type": "object"}},
                    "milestones": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["client_id", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_media_plan",
            "description": "Create a media buying plan in the Media module.",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "name": {"type": "string"},
                    "budget": {"type": "number"},
                    "channels": {"type": "array", "items": {"type": "object"}},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                },
                "required": ["client_id", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_post",
            "description": "Update an existing content post in Studio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {"type": "string"},
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                    "scheduledFor": {"type": "string"},
                    "status": {"type": "string"},
                },
                "required": ["post_id"],
            },
        },
    },
]


# ══════════════════════════════════════════════════════════════
# AGENT → WRITE TOOL MAPPING
# ══════════════════════════════════════════════════════════════

AGENT_WRITE_TOOL_MAP: dict[str, list[str]] = {
    "brief": ["create_brief"],
    "content": ["create_content_posts", "update_post"],
    "copy": ["update_post"],
    "resource": ["create_project"],
    "media_buying": ["create_media_plan"],
    "publisher": ["create_content_posts"],
    "campaign": ["create_media_plan"],
    "campaign_analytics": ["create_content_posts"],
    "social_listening": ["create_content_posts"],
}

# Set of all ERP read tool names for fast lookup in BaseAgent
ERP_READ_TOOL_NAMES = {t["function"]["name"] for t in ERP_READ_TOOLS}

# Set of all ERP write tool names for fast lookup
ERP_WRITE_TOOL_NAMES = {t["function"]["name"] for t in ERP_WRITE_TOOLS}

# Combined set
ERP_TOOL_NAMES = ERP_READ_TOOL_NAMES | ERP_WRITE_TOOL_NAMES
