"""
SpokeStack Tool Registry (Integration Spec Section 11.6)

Maps agent types to their required SpokeStack tools.
Provides tool definitions and tool executor factory.
"""

from .spokestack_base import SpokeStackClient
from .spokestack_briefs import BriefTools
from .spokestack_calendar import CalendarTools
from .spokestack_projects import ProjectTools
from .spokestack_clients import ClientTools
from .spokestack_team import TeamTools
from .spokestack_common import CommonTools


# Required tools per agent type (spec Section 11.6)
AGENT_REQUIRED_TOOLS: dict[str, list[str]] = {
    "workflow": ["get_clients", "get_team_members", "navigate_to", "get_form_schema"],
    "content": ["create_calendar_entries", "get_client_context", "get_clients"],
    "brief": ["create_brief", "get_clients", "get_team_members", "get_client_context"],
    "presentation": ["get_client_context"],
    "video_script": ["create_brief", "get_client_context"],
    "copy": ["create_brief", "get_client_context"],
    "campaign_analytics": ["get_client_context"],
    "media_buying": ["get_client_context"],
    "training": ["get_client_context"],
    "legal": ["get_client_context"],
    "resource": ["get_team_members"],
}


def get_tool_definitions_for_agent(agent_type: str) -> list[dict]:
    """
    Get all tool definitions an agent needs based on its type.
    Always includes common tools, plus agent-specific tools.
    """
    required_tools = AGENT_REQUIRED_TOOLS.get(agent_type, [])
    definitions = []

    # Always include common tools
    definitions.extend(CommonTools.tool_definitions())

    # Add module-specific tools based on requirements
    tool_name_to_source = {
        "create_brief": BriefTools,
        "get_briefs": BriefTools,
        "create_calendar_entries": CalendarTools,
        "get_calendar_entries": CalendarTools,
        "create_project": ProjectTools,
        "add_project_milestone": ProjectTools,
        "get_clients": ClientTools,
        "get_client_context": ClientTools,
        "get_team_members": TeamTools,
        "assign_to_user": TeamTools,
    }

    added_sources = set()
    for tool_name in required_tools:
        source = tool_name_to_source.get(tool_name)
        if source and source not in added_sources:
            definitions.extend(source.tool_definitions())
            added_sources.add(source)

    return definitions


def create_tool_executor(erp_base_url: str, erp_api_key: str) -> dict:
    """
    Create tool executor instances for all SpokeStack modules.

    Returns a dict of tool_name -> (tool_instance, method_name)
    for routing tool calls to the right implementation.
    """
    client = SpokeStackClient(erp_base_url, erp_api_key)

    brief_tools = BriefTools(client)
    calendar_tools = CalendarTools(client)
    project_tools = ProjectTools(client)
    client_tools = ClientTools(client)
    team_tools = TeamTools(client)
    common_tools = CommonTools(client)

    return {
        # Common tools
        "navigate_to": (common_tools, "navigate_to"),
        "get_form_schema": (common_tools, "get_form_schema"),
        "fill_form_field": (common_tools, "fill_form_field"),
        "submit_form": (common_tools, "submit_form"),
        # Brief tools
        "create_brief": (brief_tools, "create_brief"),
        "get_briefs": (brief_tools, "get_briefs"),
        # Calendar tools
        "create_calendar_entries": (calendar_tools, "create_calendar_entries"),
        "get_calendar_entries": (calendar_tools, "get_calendar_entries"),
        # Project tools
        "create_project": (project_tools, "create_project"),
        "add_project_milestone": (project_tools, "add_milestone"),
        # Client tools
        "get_clients": (client_tools, "get_clients"),
        "get_client_context": (client_tools, "get_client_context"),
        # Team tools
        "get_team_members": (team_tools, "get_team_members"),
        "assign_to_user": (team_tools, "assign_to_user"),
    }
