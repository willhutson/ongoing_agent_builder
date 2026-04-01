"""
Action Reporter — Fire-and-forget reporting of agent actions to spokestack-core.

Every meaningful CoreToolkit mutation (create, update, complete, assign) fires
a POST to spokestack-core's context API so Mission Control can display live
agent activity. This must NEVER block or throw.
"""

import httpx
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

CORE_API_URL = os.environ.get("SPOKESTACK_CORE_URL", "https://spokestack-core.vercel.app")
AGENT_SECRET = os.environ.get("AGENT_RUNTIME_SECRET", "")


async def report_action(
    org_id: str,
    action: str,          # e.g. "task.created", "task.completed", "project.created"
    entity_type: str,     # e.g. "TASK", "PROJECT", "BRIEF", "ORDER"
    entity_id: str,       # the created/updated entity's ID
    entity_title: str,    # human-readable title
    agent_type: str,      # e.g. "core_tasks", "core_projects"
    metadata: dict = None,
) -> None:
    """Fire-and-forget action report to spokestack-core's context API."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{CORE_API_URL}/api/v1/context",
                headers={
                    "Content-Type": "application/json",
                    "X-Agent-Secret": AGENT_SECRET,
                    "X-Org-Id": org_id,
                },
                json={
                    "entryType": "PATTERN",
                    "category": "agent.action",
                    "key": f"{action}:{entity_id}",
                    "value": {
                        "action": action,
                        "entityType": entity_type,
                        "entityId": entity_id,
                        "entityTitle": entity_title,
                        "agentType": agent_type,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        **(metadata or {}),
                    },
                    "confidence": 1.0,
                    "sourceAgentType": agent_type,
                },
            )
    except Exception as e:
        # Fire-and-forget — never block agent execution
        logger.debug(f"Action report failed (non-blocking): {e}")
