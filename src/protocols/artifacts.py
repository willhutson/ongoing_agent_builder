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


# Artifact data schemas - expected JSON structure for each artifact type's data field
ARTIFACT_DATA_SCHEMAS: dict[ArtifactType, dict] = {
    ArtifactType.BRIEF: {
        "type": "object",
        "required": ["client_name", "project_name", "objectives"],
        "properties": {
            "client_name": {"type": "string"},
            "project_name": {"type": "string"},
            "objectives": {"type": "array", "items": {"type": "string"}},
            "deliverables": {"type": "array", "items": {"type": "string"}},
            "timeline": {"type": "string"},
            "budget_indication": {"type": "string"},
            "complexity": {"type": "string", "enum": ["low", "medium", "high"]},
            "gaps": {"type": "array", "items": {"type": "string"}},
        },
    },
    ArtifactType.CALENDAR: {
        "type": "object",
        "required": ["entries"],
        "properties": {
            "entries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "assignee": {"type": "string"},
                    },
                },
            },
            "date_range": {"type": "object", "properties": {"start": {"type": "string"}, "end": {"type": "string"}}},
        },
    },
    ArtifactType.DECK: {
        "type": "object",
        "required": ["title", "slides"],
        "properties": {
            "title": {"type": "string"},
            "slides": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "notes": {"type": "string"},
                        "layout": {"type": "string"},
                    },
                },
            },
        },
    },
    ArtifactType.REPORT: {
        "type": "object",
        "required": ["title", "sections"],
        "properties": {
            "title": {"type": "string"},
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"},
                        "content": {"type": "string"},
                        "data": {"type": "object"},
                    },
                },
            },
            "executive_summary": {"type": "string"},
            "recommendations": {"type": "array", "items": {"type": "string"}},
        },
    },
    ArtifactType.DOCUMENT: {
        "type": "object",
        "required": ["title", "body"],
        "properties": {
            "title": {"type": "string"},
            "body": {"type": "string"},
            "metadata": {"type": "object"},
        },
    },
    ArtifactType.TABLE: {
        "type": "object",
        "required": ["columns", "rows"],
        "properties": {
            "columns": {
                "type": "array",
                "items": {"type": "object", "properties": {"name": {"type": "string"}, "type": {"type": "string"}}},
            },
            "rows": {"type": "array", "items": {"type": "array"}},
            "summary": {"type": "string"},
        },
    },
    ArtifactType.CHART: {
        "type": "object",
        "required": ["chart_type", "data"],
        "properties": {
            "chart_type": {"type": "string", "enum": ["bar", "line", "pie", "scatter", "area", "donut"]},
            "data": {
                "type": "object",
                "properties": {
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "datasets": {"type": "array"},
                },
            },
            "options": {"type": "object"},
        },
    },
    ArtifactType.CONTRACT: {
        "type": "object",
        "required": ["title", "parties", "clauses"],
        "properties": {
            "title": {"type": "string"},
            "parties": {"type": "array", "items": {"type": "string"}},
            "clauses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"title": {"type": "string"}, "content": {"type": "string"}},
                },
            },
            "effective_date": {"type": "string"},
            "terms": {"type": "string"},
        },
    },
    ArtifactType.SCRIPT: {
        "type": "object",
        "required": ["title", "scenes"],
        "properties": {
            "title": {"type": "string"},
            "scenes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "number": {"type": "integer"},
                        "heading": {"type": "string"},
                        "action": {"type": "string"},
                        "dialogue": {"type": "string"},
                    },
                },
            },
        },
    },
    ArtifactType.STORYBOARD: {
        "type": "object",
        "required": ["title", "frames"],
        "properties": {
            "title": {"type": "string"},
            "frames": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "number": {"type": "integer"},
                        "description": {"type": "string"},
                        "camera": {"type": "string"},
                        "audio": {"type": "string"},
                    },
                },
            },
        },
    },
    ArtifactType.SHOT_LIST: {
        "type": "object",
        "required": ["title", "shots"],
        "properties": {
            "title": {"type": "string"},
            "shots": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "number": {"type": "integer"},
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "equipment": {"type": "string"},
                    },
                },
            },
        },
    },
    ArtifactType.MOODBOARD: {
        "type": "object",
        "required": ["title", "elements"],
        "properties": {
            "title": {"type": "string"},
            "elements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["image", "color", "texture", "typography"]},
                        "description": {"type": "string"},
                    },
                },
            },
            "theme": {"type": "string"},
        },
    },
    ArtifactType.SURVEY: {
        "type": "object",
        "required": ["title", "questions"],
        "properties": {
            "title": {"type": "string"},
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["multiple_choice", "scale", "open"]},
                        "text": {"type": "string"},
                        "options": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        },
    },
    ArtifactType.COURSE: {
        "type": "object",
        "required": ["title", "modules"],
        "properties": {
            "title": {"type": "string"},
            "modules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "lessons": {"type": "array"},
                        "duration": {"type": "string"},
                    },
                },
            },
            "objectives": {"type": "array", "items": {"type": "string"}},
        },
    },
    ArtifactType.WORKFLOW: {
        "type": "object",
        "required": ["title", "steps"],
        "properties": {
            "title": {"type": "string"},
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "agent": {"type": "string"},
                        "description": {"type": "string"},
                        "dependencies": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        },
    },
}


def validate_artifact_data(artifact_type: ArtifactType, data: dict) -> tuple[bool, list[str]]:
    """Validate artifact data against its schema. Returns (is_valid, errors)."""
    schema = ARTIFACT_DATA_SCHEMAS.get(artifact_type)
    if not schema:
        return True, []  # No schema defined, accept anything

    errors = []
    required_fields = schema.get("required", [])
    for field_name in required_fields:
        if field_name not in data:
            errors.append(f"Missing required field: {field_name}")

    return len(errors) == 0, errors


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
