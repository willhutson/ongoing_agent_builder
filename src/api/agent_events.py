"""
Agent Event Handler — receives events routed by spokestack-core's event processor.

When a subscription has handler: "agent:{agentId}", core posts the event here.
The agent is triggered with the event as context.
"""

import json
import logging
import os
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/agent-events", tags=["agent-events"])


class EventPayload(BaseModel):
    entityType: str
    entityId: str
    action: str
    metadata: dict = Field(default_factory=dict)
    organizationId: str


class AgentEventRequest(BaseModel):
    agentId: str
    event: EventPayload
    organizationId: str


class AgentEventResponse(BaseModel):
    ok: bool
    agentId: str
    message: str = ""


def _validate_agent_secret(x_agent_secret: Optional[str]):
    expected = os.environ.get("AGENT_RUNTIME_SECRET", "")
    if not expected:
        return
    if not x_agent_secret or x_agent_secret != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Agent-Secret")


def format_event_for_agent(event: EventPayload) -> str:
    """Build a human-readable message from an event."""
    msg = f"Event: {event.entityType} was {event.action} (ID: {event.entityId})"
    metadata = event.metadata
    if "fromStatus" in metadata and "toStatus" in metadata:
        msg += f" — status changed from {metadata['fromStatus']} to {metadata['toStatus']}"
    if "changedFields" in metadata:
        fields = metadata["changedFields"]
        if isinstance(fields, list):
            msg += f" — fields changed: {', '.join(fields)}"
    if "title" in metadata:
        msg += f" — \"{metadata['title']}\""
    return msg


@router.post("", response_model=AgentEventResponse)
async def handle_agent_event(
    request: AgentEventRequest,
    x_agent_secret: Optional[str] = Header(default=None, alias="X-Agent-Secret"),
):
    """
    Receive an event routed by spokestack-core's event processor.

    When a subscription has handler: "agent:{agentId}", core posts here.
    The agent is triggered with the event formatted as a context message.
    """
    _validate_agent_secret(x_agent_secret)

    event_message = format_event_for_agent(request.event)

    logger.info(
        f"[agent-event] agent={request.agentId} org={request.organizationId} "
        f"event={request.event.entityType}.{request.event.action} "
        f"entity={request.event.entityId}"
    )

    # For now, log the event trigger. Full agent session triggering
    # requires async execution (background task or queue), which will
    # be wired when the agent session infrastructure supports it.
    # The event data is captured and available for when we add
    # trigger_agent_session().

    return AgentEventResponse(
        ok=True,
        agentId=request.agentId,
        message=f"Event received: {event_message}",
    )
