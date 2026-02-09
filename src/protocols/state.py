"""
Agent State Protocol (Integration Spec Section 1)

Defines the agent state machine and state payloads for
communication between Agent Builder and SpokeStack Mission Control.

State Machine:
    IDLE -> THINKING -> WORKING -> COMPLETE
                    -> WAITING (pending user input)
                    -> ERROR
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AgentState(str, Enum):
    """Agent states per the integration spec state machine."""
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETE = "complete"
    ERROR = "error"


class ActionType(str, Enum):
    """Types of post-completion actions."""
    SHARE_CLIENT = "share_client"
    SHARE_INTERNAL = "share_internal"
    ASSIGN_TEAM = "assign_team"
    HANDOFF_AGENT = "handoff_agent"
    ADD_TO_MODULE = "add_to_module"
    EXPORT = "export"
    APPROVE = "approve"
    SCHEDULE = "schedule"
    CUSTOM = "custom"


class StateProgress(BaseModel):
    """Progress tracking for WORKING state."""
    current: int
    total: int
    label: str
    percentage: float


class WaitingFor(BaseModel):
    """Describes what the agent is waiting for in WAITING state."""
    type: str  # user_input, approval, selection, confirmation
    prompt: str
    options: Optional[list[str]] = None
    required: bool = True
    timeout_minutes: Optional[int] = None


class SuggestedAction(BaseModel):
    """A suggested next action after agent completion."""
    id: str
    type: ActionType
    label: str
    description: Optional[str] = None
    icon: Optional[str] = None
    config: dict = Field(default_factory=dict)
    priority: int = 1
    conditions: Optional[dict] = None


class StateCompletion(BaseModel):
    """Completion details for COMPLETE state."""
    summary: str
    artifact_ids: list[str] = Field(default_factory=list)
    suggested_actions: list[SuggestedAction] = Field(default_factory=list)
    metrics: Optional[dict] = None


class StateError(BaseModel):
    """Error details for ERROR state."""
    code: str
    message: str
    recoverable: bool = False
    retry_after_seconds: Optional[int] = None
    user_action_required: Optional[str] = None


class AgentStateUpdate(BaseModel):
    """
    Full state update payload emitted by agents.
    Maps to the AgentStateUpdate interface in the spec.
    """
    chat_id: str
    agent_id: str
    agent_type: str
    timestamp: str  # ISO 8601
    state: AgentState

    # WORKING state
    progress: Optional[StateProgress] = None

    # WAITING state
    waiting_for: Optional[WaitingFor] = None

    # COMPLETE state
    completion: Optional[StateCompletion] = None

    # ERROR state
    error: Optional[StateError] = None

    def to_sse(self) -> str:
        """Serialize as SSE event."""
        import json
        data = self.model_dump(exclude_none=True)
        return f"event: state_update\ndata: {json.dumps(data)}\n\n"
