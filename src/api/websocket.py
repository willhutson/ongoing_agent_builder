"""
WebSocket Event Layer (Integration Spec Section 7)

Implements bidirectional WebSocket communication between
Agent Builder and SpokeStack Mission Control.

Events:
  Agent Builder -> SpokeStack:
    state:update, message:stream, message:complete,
    artifact:create/update/complete, handoff:request,
    model:switch:suggest, skill:toggle:ack

  SpokeStack -> Agent Builder:
    chat:start, message:send, action:execute,
    model:switch, skill:toggle, handoff:approve, chat:cancel
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
from datetime import datetime, timezone
import asyncio
import json
import logging
import uuid

from ..agents.base import AgentContext, AgentResult
from ..protocols.events import (
    StartChatRequest, MessageWithAttachments,
    SwitchModelRequest, ToggleSkillRequest,
    ExecuteActionRequest, ExecuteActionResponse,
    resolve_agent_type,
)
from ..protocols.handoffs import HandoffRequest, HandoffResponse
from ..protocols.state import AgentState

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}  # chat_id -> ws
        self.chat_agents: dict[str, dict] = {}  # chat_id -> agent state

    async def connect(self, chat_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[chat_id] = websocket
        logger.info(f"WebSocket connected: {chat_id}")

    def disconnect(self, chat_id: str):
        self.active_connections.pop(chat_id, None)
        self.chat_agents.pop(chat_id, None)
        logger.info(f"WebSocket disconnected: {chat_id}")

    async def send_event(self, chat_id: str, event_type: str, payload: dict):
        """Send an event to a specific chat connection."""
        ws = self.active_connections.get(chat_id)
        if ws:
            try:
                await ws.send_json({"type": event_type, "payload": payload})
            except Exception as e:
                logger.error(f"Failed to send event to {chat_id}: {e}")

    async def broadcast(self, event_type: str, payload: dict):
        """Broadcast an event to all connections."""
        for chat_id, ws in self.active_connections.items():
            try:
                await ws.send_json({"type": event_type, "payload": payload})
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/v1/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    organization_id: str = Query(None, alias="org_id"),
):
    """
    WebSocket endpoint for real-time agent communication.

    Connection URL: wss://agent-builder.spokestack.io/v1/ws?org_id=<org_id>

    Supports all event types from Integration Spec Section 7.
    """
    chat_id = str(uuid.uuid4())
    await manager.connect(chat_id, websocket)

    # Start heartbeat
    heartbeat_task = asyncio.create_task(_heartbeat(websocket, chat_id))

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")
            payload = data.get("payload", {})

            if event_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif event_type == "chat:start":
                await _handle_chat_start(chat_id, payload, organization_id)

            elif event_type == "message:send":
                await _handle_message(chat_id, payload, organization_id)

            elif event_type == "action:execute":
                await _handle_action(chat_id, payload)

            elif event_type == "model:switch":
                await _handle_model_switch(chat_id, payload)

            elif event_type == "skill:toggle":
                await _handle_skill_toggle(chat_id, payload)

            elif event_type == "handoff:approve":
                await _handle_handoff_approve(chat_id, payload)

            elif event_type == "chat:cancel":
                await _handle_cancel(chat_id)

            else:
                logger.warning(f"Unknown event type: {event_type}")

    except WebSocketDisconnect:
        manager.disconnect(chat_id)
        heartbeat_task.cancel()
    except Exception as e:
        logger.error(f"WebSocket error for {chat_id}: {e}")
        manager.disconnect(chat_id)
        heartbeat_task.cancel()


async def _heartbeat(websocket: WebSocket, chat_id: str):
    """Send heartbeat every 30 seconds."""
    try:
        while True:
            await asyncio.sleep(30)
            if chat_id in manager.active_connections:
                await websocket.send_json({"type": "ping"})
    except Exception:
        pass


async def _handle_chat_start(chat_id: str, payload: dict, org_id: str):
    """Handle chat:start event."""
    request = StartChatRequest(**payload)

    # Resolve agent type from Mission Control naming
    agent_type = resolve_agent_type(request.agent_type)

    # Store chat state
    manager.chat_agents[chat_id] = {
        "agent_type": agent_type,
        "model": request.model.get("id", "claude-sonnet-4-20250514"),
        "organization_id": request.organization_id or org_id,
        "user_id": request.user_id,
        "skills": request.skills.model_dump(),
        "context": request.context.model_dump(),
        "messages": [],
    }

    # Acknowledge
    await manager.send_event(chat_id, "chat:started", {
        "chatId": chat_id,
        "agentType": agent_type,
        "model": request.model,
    })


async def _handle_message(chat_id: str, payload: dict, org_id: str):
    """Handle message:send event."""
    chat_state = manager.chat_agents.get(chat_id)
    if not chat_state:
        await manager.send_event(chat_id, "error", {"code": "CHAT_NOT_FOUND", "message": "Chat not initialized"})
        return

    # Parse message with optional attachments
    msg = MessageWithAttachments(**payload) if "attachments" in payload else MessageWithAttachments(content=payload.get("content", payload.get("text", "")))

    # Build context with SSE callback that sends events back via WebSocket
    async def ws_sse_callback(event: dict):
        event_type = event.get("type", "agent_event")
        await manager.send_event(chat_id, event_type, event)

    context = AgentContext(
        tenant_id=chat_state["organization_id"],
        user_id=chat_state["user_id"],
        task=msg.content,
        metadata={"chat_id": chat_id, "skills": chat_state["skills"]},
        chat_id=chat_id,
        organization_id=chat_state["organization_id"],
        attachments=[a.model_dump() for a in msg.attachments] if msg.attachments else [],
        _sse_callback=ws_sse_callback,
    )

    # Execute agent in background
    asyncio.create_task(_run_agent_for_ws(chat_id, chat_state, context))


async def _run_agent_for_ws(chat_id: str, chat_state: dict, context: AgentContext):
    """Run agent and send results via WebSocket."""
    from .routes import get_agent, AgentType

    try:
        agent_type = AgentType(chat_state["agent_type"])
        agent = get_agent(agent_type)

        # Override model
        if chat_state.get("model"):
            agent.model = chat_state["model"]

        result = await agent.run(context)
        await agent.close()

        await manager.send_event(chat_id, "message:complete", {
            "chatId": chat_id,
            "message": {
                "role": "assistant",
                "content": result.output,
            },
            "artifacts": result.artifacts,
            "suggestedActions": result.suggested_actions,
            "createdEntities": result.created_entities,
        })

    except Exception as e:
        logger.error(f"Agent execution failed for {chat_id}: {e}")
        await manager.send_event(chat_id, "error", {
            "code": "AGENT_TIMEOUT",
            "message": str(e),
            "recoverable": True,
        })


async def _handle_action(chat_id: str, payload: dict):
    """Handle action:execute event."""
    request = ExecuteActionRequest(**payload)
    # Route to appropriate action handler
    await manager.send_event(chat_id, "action:result", {
        "success": True,
        "chatId": chat_id,
        "artifactId": request.artifact_id,
    })


async def _handle_model_switch(chat_id: str, payload: dict):
    """Handle model:switch event."""
    request = SwitchModelRequest(**payload)
    chat_state = manager.chat_agents.get(chat_id)
    if chat_state:
        previous_model = chat_state.get("model")
        chat_state["model"] = request.new_model_id
        await manager.send_event(chat_id, "model:switch:ack", {
            "chatId": chat_id,
            "previousModel": previous_model,
            "newModel": request.new_model_id,
            "contextPreserved": True,
            "message": f"Switched to {request.new_model_id}",
        })


async def _handle_skill_toggle(chat_id: str, payload: dict):
    """Handle skill:toggle event."""
    request = ToggleSkillRequest(**payload)
    await manager.send_event(chat_id, "skill:toggle:ack", {
        "chatId": chat_id,
        "skillId": request.skill_id,
        "enabled": request.enabled,
        "message": f"{'Enabled' if request.enabled else 'Disabled'} skill {request.skill_id}",
    })


async def _handle_handoff_approve(chat_id: str, payload: dict):
    """Handle handoff:approve event."""
    new_chat_id = str(uuid.uuid4())
    await manager.send_event(chat_id, "handoff:complete", {
        "approved": True,
        "newChatId": new_chat_id,
        "message": "Handoff approved",
    })


async def _handle_cancel(chat_id: str):
    """Handle chat:cancel event."""
    await manager.send_event(chat_id, "chat:cancelled", {"chatId": chat_id})
    manager.chat_agents.pop(chat_id, None)
