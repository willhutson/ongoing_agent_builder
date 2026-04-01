"""
Event & Asset Management Tools — listRecentEvents, subscribeToEvent, manageAssets.

Agents use these to query org events, subscribe to future events,
and interact with the Digital Asset Management (DAM) system.
All calls proxy through spokestack-core's REST API.
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# Tool Definitions
# ══════════════════════════════════════════════════════════════

LIST_RECENT_EVENTS_TOOL = {
    "type": "function",
    "function": {
        "name": "list_recent_events",
        "description": (
            "Get recent events for this organization. Shows what's been happening — "
            "new tasks, status changes, completed projects, sync completions, etc. "
            "Useful for understanding current activity and providing proactive updates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "entity_type": {
                    "type": "string",
                    "description": "Filter by entity type: Client, Task, Project, Brief, Order, Integration, Asset",
                },
                "action": {
                    "type": "string",
                    "description": "Filter by action: created, updated, deleted, status_changed, sync_completed",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 20, max 100)",
                    "default": 20,
                },
                "since": {
                    "type": "string",
                    "description": "ISO datetime — only events after this time. Default: last 24 hours",
                },
            },
            "required": [],
        },
    },
}

SUBSCRIBE_TO_EVENT_TOOL = {
    "type": "function",
    "function": {
        "name": "subscribe_to_event",
        "description": (
            "Subscribe to be notified when specific events happen in this organization. "
            "Creates an event subscription that triggers an action when the specified event "
            "occurs. Example: watch for when any project status changes to COMPLETED."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "entity_type": {
                    "type": "string",
                    "description": "Entity to watch: Client, Task, Project, Brief, Order, Integration, Asset, or * for all",
                    "enum": ["Client", "Task", "Project", "Brief", "Order", "Integration", "Asset", "*"],
                },
                "action": {
                    "type": "string",
                    "description": "Action to watch: created, updated, deleted, status_changed, or * for all",
                    "enum": ["created", "updated", "deleted", "status_changed", "*"],
                },
                "conditions": {
                    "type": "object",
                    "description": "Optional conditions for filtering. Example: { 'toStatus': 'COMPLETED' }",
                },
                "description": {
                    "type": "string",
                    "description": "Human-readable description of why this subscription exists",
                },
            },
            "required": ["entity_type", "action"],
        },
    },
}

MANAGE_ASSETS_TOOL = {
    "type": "function",
    "function": {
        "name": "manage_assets",
        "description": (
            "Interact with the organization's Digital Asset Management system. "
            "Search for assets (logos, brand files, project deliverables), "
            "list libraries, get asset details, or browse folders."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "What to do",
                    "enum": ["searchAssets", "listLibraries", "getAsset", "listFolder"],
                },
                "query": {
                    "type": "string",
                    "description": "Search query (for searchAssets) — searches name and tags",
                },
                "asset_type": {
                    "type": "string",
                    "description": "Filter by type (for searchAssets)",
                    "enum": ["IMAGE", "VIDEO", "AUDIO", "DOCUMENT", "FONT", "TEMPLATE", "THREE_D", "OTHER"],
                },
                "library_id": {
                    "type": "string",
                    "description": "Library ID (for listFolder or filtering searchAssets)",
                },
                "folder_id": {
                    "type": "string",
                    "description": "Folder ID (for listFolder)",
                },
                "asset_id": {
                    "type": "string",
                    "description": "Asset ID (for getAsset)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 20)",
                    "default": 20,
                },
            },
            "required": ["action"],
        },
    },
}

# Grouped for registration
EVENT_TOOLS = [LIST_RECENT_EVENTS_TOOL, SUBSCRIBE_TO_EVENT_TOOL]
ASSET_TOOLS = [MANAGE_ASSETS_TOOL]
EVENT_AND_ASSET_TOOLS = EVENT_TOOLS + ASSET_TOOLS

EVENT_TOOL_NAMES = {t["function"]["name"] for t in EVENT_AND_ASSET_TOOLS}
