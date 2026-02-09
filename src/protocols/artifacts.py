"""
Artifact Protocol (Integration Spec Section 2)

Defines artifact types, creation events, and streaming updates
for real-time artifact building in Mission Control.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """All artifact types supported by SpokeStack."""
    # Content
    CALENDAR = "calendar"
    BRIEF = "brief"
    DOCUMENT = "document"
    DECK = "deck"
    MOODBOARD = "moodboard"
    # Video
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    SHOT_LIST = "shot_list"
    # Data
    REPORT = "report"
    TABLE = "table"
    CHART = "chart"
    # Operations
    CONTRACT = "contract"
    SURVEY = "survey"
    COURSE = "course"
    WORKFLOW = "workflow"


class ArtifactEventType(str, Enum):
    """Artifact lifecycle events."""
    CREATE = "artifact:create"
    UPDATE = "artifact:update"
    COMPLETE = "artifact:complete"


class ArtifactPreview(BaseModel):
    """Preview content for UI rendering."""
    type: str  # html, markdown, json
    content: str


class Artifact(BaseModel):
    """An artifact created or being built by an agent."""
    id: str
    type: ArtifactType
    module_type: Optional[str] = None
    title: str
    status: str = "building"  # building, draft, final
    version: int = 1
    data: dict = Field(default_factory=dict)
    preview: Optional[ArtifactPreview] = None
    client_id: Optional[str] = None
    project_id: Optional[str] = None


class ArtifactEvent(BaseModel):
    """Event emitted during artifact lifecycle."""
    event: ArtifactEventType
    chat_id: str
    agent_id: str
    artifact: Artifact

    def to_sse(self) -> str:
        """Serialize as SSE event."""
        import json
        data = self.model_dump(exclude_none=True)
        # Use the event type as the SSE event name
        event_name = self.event.value.replace(":", "_")
        return f"event: {event_name}\ndata: {json.dumps(data)}\n\n"


# Standard actions by artifact type (spec Section 3.2)
STANDARD_ACTIONS: dict[ArtifactType, list[str]] = {
    ArtifactType.CALENDAR: [
        "share_client", "handoff_agent", "add_to_module", "export",
    ],
    ArtifactType.BRIEF: [
        "assign_team", "share_client", "add_to_module", "handoff_agent",
    ],
    ArtifactType.DECK: [
        "share_client", "share_internal", "export", "add_to_module",
    ],
    ArtifactType.REPORT: [
        "share_client", "share_internal", "schedule", "export",
    ],
    ArtifactType.CONTRACT: [
        "share_internal", "handoff_agent", "add_to_module",
    ],
    ArtifactType.DOCUMENT: [
        "share_client", "share_internal", "export", "add_to_module",
    ],
    ArtifactType.SCRIPT: [
        "share_internal", "handoff_agent", "add_to_module",
    ],
    ArtifactType.STORYBOARD: [
        "share_internal", "handoff_agent", "add_to_module",
    ],
    ArtifactType.COURSE: [
        "share_internal", "add_to_module", "export",
    ],
}
