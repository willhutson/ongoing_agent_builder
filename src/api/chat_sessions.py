"""
Chat Sessions API (Integration Spec Section 8)

REST API endpoints for chat session management, action execution,
and artifact retrieval. Supplements the WebSocket real-time layer.

Endpoints:
  POST /chats           - Start new chat (returns WebSocket URL)
  GET  /chats/:chatId   - Get chat state
  POST /chats/:chatId/actions - Execute action on artifact
  GET  /chats/:chatId/artifacts - Get artifacts for chat
  POST /chats/:chatId/messages  - Send message (SSE streaming)
  POST /chats/:chatId/handoff   - Request agent handoff
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid
import json
import asyncio
import logging

from ..protocols.events import (
    StartChatRequest, MessageWithAttachments,
    ExecuteActionRequest, ExecuteActionResponse,
    resolve_agent_type,
)
from ..protocols.handoffs import HandoffRequest, HandoffResponse
from ..protocols.state import AgentState
from ..protocols.errors import AgentError, ERROR_CODES
from ..agents.base import AgentContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat-sessions"])

# In-memory chat sessions (Redis in production)
_chat_sessions: dict[str, dict] = {}


class StartChatResponse(BaseModel):
    """Response from starting a new chat."""
    chat_id: str
    ws_url: str
    agent_type: str
    model: str


class ChatMessageRequest(BaseModel):
    """Request to send a message in a chat."""
    content: str
    attachments: list[dict] = Field(default_factory=list)


class ChatState(BaseModel):
    """Current state of a chat session."""
    chat_id: str
    agent_type: str
    model: str
    state: str
    messages: list[dict] = Field(default_factory=list)
    artifacts: list[dict] = Field(default_factory=list)
    created_entities: list[dict] = Field(default_factory=list)


@router.post("/chats", response_model=StartChatResponse)
async def start_chat(request: StartChatRequest):
    """
    Start a new chat session with an agent.

    Returns a chat_id and WebSocket URL for real-time communication.
    Also supports REST-based messaging via POST /chats/{chatId}/messages.
    """
    chat_id = str(uuid.uuid4())
    agent_type = resolve_agent_type(request.agent_type)
    model_id = request.model.get("id", "claude-sonnet-4-20250514")

    _chat_sessions[chat_id] = {
        "chat_id": chat_id,
        "agent_type": agent_type,
        "model": model_id,
        "organization_id": request.organization_id,
        "user_id": request.user_id,
        "skills": request.skills.model_dump(),
        "context": request.context.model_dump(),
        "state": AgentState.IDLE.value,
        "messages": [],
        "artifacts": [],
        "created_entities": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return StartChatResponse(
        chat_id=chat_id,
        ws_url=f"/v1/ws?chat_id={chat_id}",
        agent_type=agent_type,
        model=model_id,
    )


@router.get("/chats/{chat_id}", response_model=ChatState)
async def get_chat_state(chat_id: str):
    """Get current state of a chat session."""
    session = _chat_sessions.get(chat_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")

    return ChatState(
        chat_id=session["chat_id"],
        agent_type=session["agent_type"],
        model=session["model"],
        state=session["state"],
        messages=session["messages"],
        artifacts=session["artifacts"],
        created_entities=session["created_entities"],
    )


@router.post("/chats/{chat_id}/messages")
async def send_chat_message(chat_id: str, request: ChatMessageRequest):
    """
    Send a message in a chat session with SSE streaming response.

    Supports vision/attachments per spec Section 11.8.
    Returns SSE stream with state updates, work events, and message chunks.
    """
    session = _chat_sessions.get(chat_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Store user message
    session["messages"].append({"role": "user", "content": request.content})
    session["state"] = AgentState.THINKING.value

    # SSE event queue for streaming
    event_queue: asyncio.Queue = asyncio.Queue()

    async def sse_callback(event: dict):
        await event_queue.put(event)

    context = AgentContext(
        tenant_id=session["organization_id"],
        user_id=session["user_id"],
        task=request.content,
        metadata={"chat_id": chat_id},
        chat_id=chat_id,
        organization_id=session["organization_id"],
        attachments=request.attachments,
        _sse_callback=sse_callback,
    )

    async def generate():
        from .routes import get_agent, AgentType

        try:
            agent_type = AgentType(session["agent_type"])
            agent = get_agent(agent_type)
            if session.get("model"):
                agent.model = session["model"]

            # Run agent with streaming
            async for chunk in agent.stream(context):
                yield chunk

            await agent.close()

            # Drain any remaining SSE events
            while not event_queue.empty():
                event = event_queue.get_nowait()
                yield f"data: {json.dumps(event)}\n\n"

            yield "data: [DONE]\n\n"
            session["state"] = AgentState.COMPLETE.value

        except Exception as e:
            logger.error(f"Agent error in chat {chat_id}: {e}")
            error = AgentError.from_code("AGENT_TIMEOUT", details={"error": str(e)}, recoverable=True)
            yield error.to_sse()
            session["state"] = AgentState.ERROR.value

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/chats/{chat_id}/actions", response_model=ExecuteActionResponse)
async def execute_action(chat_id: str, request: ExecuteActionRequest):
    """
    Execute a post-completion action on an artifact.
    Handles: share_client, handoff_agent, add_to_module, export, etc.
    """
    session = _chat_sessions.get(chat_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")

    action_type = request.action.get("type")

    if action_type == "handoff_agent":
        target_agent = request.action.get("config", {}).get("agent_type")
        if target_agent:
            new_chat_id = str(uuid.uuid4())
            return ExecuteActionResponse(
                success=True,
                new_chat_id=new_chat_id,
                new_agent_type=target_agent,
            )

    if action_type == "add_to_module":
        module = request.action.get("config", {}).get("module")
        return ExecuteActionResponse(
            success=True,
            module_url=f"/{module}/{request.artifact_id}" if module else None,
        )

    return ExecuteActionResponse(success=True)


@router.get("/chats/{chat_id}/artifacts")
async def get_chat_artifacts(chat_id: str):
    """Get all artifacts created during a chat session."""
    session = _chat_sessions.get(chat_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")

    return {"chat_id": chat_id, "artifacts": session.get("artifacts", [])}


@router.post("/chats/{chat_id}/handoff", response_model=HandoffResponse)
async def request_handoff(chat_id: str, request: HandoffRequest):
    """
    Request an agent-to-agent handoff.
    Creates a new chat session with the target agent and passes context.
    """
    session = _chat_sessions.get(chat_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")

    new_chat_id = str(uuid.uuid4())
    _chat_sessions[new_chat_id] = {
        "chat_id": new_chat_id,
        "agent_type": request.to_agent_type,
        "model": session["model"],
        "organization_id": session["organization_id"],
        "user_id": session["user_id"],
        "skills": session.get("skills", {}),
        "context": {
            "parent_chat_id": chat_id,
            "parent_agent_type": request.from_agent_type,
            "handoff_context": request.context.model_dump(),
        },
        "state": AgentState.IDLE.value,
        "messages": [],
        "artifacts": [],
        "created_entities": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return HandoffResponse(
        approved=True,
        new_chat_id=new_chat_id,
        new_agent_type=request.to_agent_type,
        message=f"Handoff to {request.to_agent_type} approved",
    )
