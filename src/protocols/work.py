"""
Agent Work Protocol (Integration Spec Section 11)

Defines the "screen share" paradigm where agents operate SpokeStack
on behalf of users. The Agent Work pane shows this operation in real-time.

Key concepts:
- AgentWorkState: Tracks what the agent is doing in SpokeStack
- AgentAction: Individual actions (navigate, fill_field, create, etc.)
- CreatedEntity: Entities created in SpokeStack during work
- SSE events: work_start, action, entity_created, work_complete, work_error
"""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class AgentWorkModule(str, Enum):
    """SpokeStack modules the agent can operate in."""
    BRIEFS = "briefs"
    STUDIO_CALENDAR = "studio/calendar"
    STUDIO_DECKS = "studio/decks"
    PROJECTS = "projects"
    CLIENTS = "clients"
    DEALS = "deals"
    RFP = "rfp"
    TIME = "time"
    RESOURCES = "resources"
    LMS_COURSES = "lms/courses"
    TEAM = "team"


class AgentActionType(str, Enum):
    """Types of actions an agent can take in SpokeStack."""
    NAVIGATE = "navigate"
    OPEN_FORM = "open_form"
    FILL_FIELD = "fill_field"
    SELECT_OPTION = "select_option"
    CREATE = "create"
    UPDATE = "update"
    ASSIGN = "assign"
    SUBMIT = "submit"
    COMPLETE = "complete"
    ERROR = "error"


class AgentAction(BaseModel):
    """A single action taken by the agent in SpokeStack."""
    id: str
    type: AgentActionType
    timestamp: str  # ISO 8601
    module: Optional[AgentWorkModule] = None
    route: Optional[str] = None

    # For fill_field actions
    field: Optional[str] = None
    field_label: Optional[str] = None
    value: Optional[Any] = None
    display_value: Optional[str] = None

    # Status
    status: str = "pending"  # pending, filling, filled, success, error
    message: Optional[str] = None


class CreatedEntity(BaseModel):
    """An entity created in SpokeStack by the agent."""
    id: str
    type: str  # brief, calendar_entry, project, etc.
    title: str
    module: AgentWorkModule
    url: str  # Deep link to entity in SpokeStack


class AgentWorkState(BaseModel):
    """
    Full work state for the Agent Work pane.
    Tracks what the agent is doing in SpokeStack in real-time.
    """
    chat_id: str
    is_working: bool = False

    # Current location in SpokeStack
    current_module: Optional[AgentWorkModule] = None
    current_route: Optional[str] = None
    current_entity: Optional[str] = None

    # Action tracking
    actions: list[AgentAction] = Field(default_factory=list)

    # Form field tracking
    pending_fields: list[str] = Field(default_factory=list)
    completed_fields: list[str] = Field(default_factory=list)

    # Created entities
    created_entities: list[CreatedEntity] = Field(default_factory=list)

    # Error state
    error: Optional[str] = None


# ============================================
# SSE Event Models
# ============================================

class WorkStartEvent(BaseModel):
    """SSE event: work_start - Agent begins operating SpokeStack."""
    type: str = "work_start"
    module: AgentWorkModule
    route: str
    pending_fields: list[str] = Field(default_factory=list)

    def to_sse(self) -> str:
        import json
        return f"event: work_start\ndata: {json.dumps(self.model_dump())}\n\n"


class WorkActionEvent(BaseModel):
    """SSE event: action - Agent takes an action in SpokeStack."""
    type: str = "action"
    action: AgentAction

    def to_sse(self) -> str:
        import json
        return f"event: action\ndata: {json.dumps(self.model_dump())}\n\n"


class EntityCreatedEvent(BaseModel):
    """SSE event: entity_created - Agent created an entity in SpokeStack."""
    type: str = "entity_created"
    entity: CreatedEntity

    def to_sse(self) -> str:
        import json
        return f"event: entity_created\ndata: {json.dumps(self.model_dump())}\n\n"


class WorkCompleteEvent(BaseModel):
    """SSE event: work_complete - Agent finished operating SpokeStack."""
    type: str = "work_complete"
    state: dict  # AgentWorkState snapshot

    def to_sse(self) -> str:
        import json
        return f"event: work_complete\ndata: {json.dumps(self.model_dump())}\n\n"


class WorkErrorEvent(BaseModel):
    """SSE event: work_error - Error during SpokeStack operation."""
    type: str = "work_error"
    error: str

    def to_sse(self) -> str:
        import json
        return f"event: work_error\ndata: {json.dumps(self.model_dump())}\n\n"
