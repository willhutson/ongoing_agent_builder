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
    # ── PR / Communications agents ──
    "media_relations_manager": [
        "add_journalist", "search_journalists", "create_media_list",
        "create_pitch", "log_coverage", "get_coverage_report",
        "list_pitches", "create_followup_task",
        "list_clients", "read_context",
    ],
    "press_release_writer": [
        "draft_press_release", "update_press_release", "submit_for_approval",
        "approve_release", "list_press_releases", "schedule_distribution",
        "list_clients", "read_context",
    ],
    "crisis_manager": [
        "activate_crisis", "draft_holding_statement", "map_stakeholder",
        "create_crisis_task", "update_crisis_status", "get_stakeholders",
        "list_clients", "read_context", "write_context",
    ],
    "client_reporter": [
        "generate_report", "get_coverage_data", "get_activity_data",
        "get_client_briefs", "save_report_metrics",
        "list_clients", "read_context",
    ],
    "influencer_manager": [
        "add_influencer", "search_influencers", "create_influencer_campaign",
        "create_deliverable", "create_influencer_contract", "list_campaigns",
        "list_clients", "read_context",
    ],
    "event_planner": [
        "create_event", "add_guest", "get_guest_list",
        "create_run_of_show_item", "add_vendor", "update_event_status",
        "list_events", "list_clients", "read_context",
    ],
    # ── Marketplace module agents ──
    "board_manager": [
        "create_board", "add_card", "move_card", "list_boards",
        "list_board_cards", "create_column", "read_context", "list_clients",
    ],
    "workflow_designer": [
        "create_workflow_def", "create_workflow", "list_workflows", "create_trigger",
        "create_action", "activate_workflow", "read_context", "write_context",
    ],
    "social_listener": [
        "log_mention", "search_mentions", "create_alert",
        "generate_listening_report", "get_sentiment_summary",
        "create_followup_task", "read_context", "list_clients",
    ],
    "nps_analyst": [
        "create_survey", "log_response", "calculate_nps",
        "list_surveys", "create_followup", "generate_nps_report", "read_context",
    ],
    "chat_operator": [
        "create_canned_response", "list_canned_responses", "create_routing_rule",
        "list_conversations", "create_escalation", "log_conversation", "read_context",
    ],
    "portal_manager": [
        "create_deliverable_entry", "list_deliverables", "submit_deliverable_for_review",
        "update_approval_status", "create_client_update", "list_clients", "read_context",
    ],
    "delegation_coordinator": [
        "delegate_task", "reassign_task", "check_workload",
        "create_escalation_rule", "list_escalation_rules", "flag_overdue", "read_context",
    ],
    "access_admin": [
        "create_role", "list_roles", "assign_permission",
        "audit_access", "log_access_event", "list_team_members", "read_context",
    ],
    "module_builder": [
        "scaffold_module", "validate_module", "test_module", "publish_module",
        "list_my_modules", "get_module_analytics", "read_context",
        "create_module_manifest", "create_module_page_template",
        "scaffold_agent_config", "list_modules",
    ],
    "module_reviewer": [
        "analyze_tools", "analyze_prompt", "check_duplicates",
        "generate_review", "approve_module", "reject_module",
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
