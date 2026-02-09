"""
SpokeStack Integration Protocols

Implements the Agent Builder Integration Specification v2.0
from erp_staging_lmtd. Covers:
- Agent state machine and status reporting
- Artifact creation and streaming
- Post-completion action routing
- Agent Work Protocol (live SpokeStack operation)
- Agent-to-agent handoffs
- WebSocket/SSE event types
- Error handling
"""

from .state import (
    AgentState,
    AgentStateUpdate,
    StateProgress,
    WaitingFor,
    StateCompletion,
    StateError,
    SuggestedAction,
    ActionType,
)
from .artifacts import (
    ArtifactType,
    ArtifactEvent,
    ArtifactEventType,
    Artifact,
    ArtifactPreview,
)
from .work import (
    AgentWorkState,
    AgentWorkModule,
    AgentAction,
    AgentActionType,
    CreatedEntity,
    WorkStartEvent,
    WorkActionEvent,
    EntityCreatedEvent,
    WorkCompleteEvent,
    WorkErrorEvent,
)
from .handoffs import (
    HandoffRequest,
    HandoffResponse,
    HandoffContext,
)
from .events import (
    AgentEvent,
    PlatformEvent,
    StartChatRequest,
    ChatSkillStack,
    MessageWithAttachments,
    Attachment,
)
from .errors import (
    AgentError,
    ERROR_CODES,
)

__all__ = [
    # State
    "AgentState", "AgentStateUpdate", "StateProgress", "WaitingFor",
    "StateCompletion", "StateError", "SuggestedAction", "ActionType",
    # Artifacts
    "ArtifactType", "ArtifactEvent", "ArtifactEventType", "Artifact", "ArtifactPreview",
    # Work
    "AgentWorkState", "AgentWorkModule", "AgentAction", "AgentActionType",
    "CreatedEntity", "WorkStartEvent", "WorkActionEvent",
    "EntityCreatedEvent", "WorkCompleteEvent", "WorkErrorEvent",
    # Handoffs
    "HandoffRequest", "HandoffResponse", "HandoffContext",
    # Events
    "AgentEvent", "PlatformEvent", "StartChatRequest",
    "ChatSkillStack", "MessageWithAttachments", "Attachment",
    # Errors
    "AgentError", "ERROR_CODES",
]
