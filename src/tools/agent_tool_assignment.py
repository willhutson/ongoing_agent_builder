"""
Agent Tool Assignment — which CRUD tools each agent type can use.

Agents only see the tools assigned to them. This prevents a brief_writer
from deleting tasks or a CRM manager from approving briefs.
"""

from src.tools.spokestack_crud_tools import TOOLS, get_openai_tools


# Maps canonical agent types to their allowed tool names
AGENT_TOOLS: dict[str, list[str]] = {
    "assistant": [
        "list_tasks", "list_projects", "list_briefs", "list_orders", "list_clients",
        "create_task", "update_task", "complete_task",
        "read_context", "get_recent_activity", "list_team_members", "search_workspace",
    ],
    "brief_writer": [
        "create_brief", "update_brief", "approve_brief", "request_revisions", "list_briefs",
        "list_clients", "read_context",
    ],
    "project_manager": [
        "create_project", "update_project", "complete_project", "list_projects",
        "create_task", "update_task", "complete_task", "list_tasks",
        "list_clients", "read_context",
    ],
    "order_manager": [
        "create_order", "update_order_status", "generate_invoice", "list_orders",
        "list_invoices", "list_clients", "read_context",
    ],
    "crm_manager": [
        "create_client", "update_client", "list_clients",
        "list_orders", "list_briefs", "read_context", "write_context",
    ],
    "analyst": [
        "list_tasks", "list_projects", "list_briefs", "list_orders", "list_clients",
        "list_invoices", "read_context", "get_recent_activity", "list_team_members",
        "search_workspace",
    ],
    "content_creator": [
        "create_brief", "list_briefs", "list_clients", "read_context",
    ],
    "core_onboarding": [
        "create_task", "create_project", "create_brief", "create_client",
        "install_module", "list_installed_modules", "write_context", "read_context",
    ],
    # Core agents from Phases 1-7
    "core_tasks": [
        "create_task", "update_task", "complete_task", "delete_task", "list_tasks",
        "read_context", "write_context", "search_workspace",
    ],
    "core_projects": [
        "create_project", "update_project", "complete_project", "list_projects",
        "create_task", "list_tasks", "read_context", "write_context",
    ],
    "core_briefs": [
        "create_brief", "update_brief", "approve_brief", "request_revisions", "list_briefs",
        "list_clients", "read_context", "write_context",
    ],
    "core_orders": [
        "create_order", "update_order_status", "generate_invoice", "list_orders",
        "list_invoices", "create_client", "list_clients", "read_context", "write_context",
    ],
}

# Default fallback — if agent type not in AGENT_TOOLS, use assistant's tools
DEFAULT_AGENT_TYPE = "assistant"


def get_tools_for_agent(agent_type: str) -> list[str]:
    """Get the list of tool names available to an agent type."""
    return AGENT_TOOLS.get(agent_type, AGENT_TOOLS[DEFAULT_AGENT_TYPE])


def get_openai_tools_for_agent(agent_type: str) -> list[dict]:
    """Get OpenAI function-calling format tools for an agent type."""
    tool_names = get_tools_for_agent(agent_type)
    return get_openai_tools(tool_names)
