"""
WebSocket/SSE Event Types (Integration Spec Section 7)

Defines all event types for communication between
Agent Builder and SpokeStack Mission Control.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# ============================================
# Inbound Events (SpokeStack -> Agent Builder)
# ============================================

class ChatSkillStack(BaseModel):
    """Skill configuration for a chat session."""
    platform_skills: list[str] = Field(default_factory=list)
    instance_skills: list[str] = Field(default_factory=list)
    client_skills: list[str] = Field(default_factory=list)
    disabled_skills: list[str] = Field(default_factory=list)


class ChatContext(BaseModel):
    """Context for starting a chat."""
    client_id: Optional[str] = None
    project_id: Optional[str] = None
    related_artifacts: list[str] = Field(default_factory=list)


class StartChatRequest(BaseModel):
    """Request to start a new chat session (spec Section 4.2)."""
    agent_type: str
    organization_id: str
    user_id: str
    model: dict = Field(default_factory=lambda: {"id": "claude-sonnet-4-20250514", "allow_auto_switch": False})
    skills: ChatSkillStack = Field(default_factory=ChatSkillStack)
    context: ChatContext = Field(default_factory=ChatContext)


class Attachment(BaseModel):
    """File attachment for vision/image support (spec Section 11.8)."""
    type: str  # image/jpeg, image/png, etc.
    name: str
    size: int
    data: str  # Base64-encoded
    media_type: str  # Same as type, for Claude API compatibility


class MessageWithAttachments(BaseModel):
    """User message with optional attachments (spec Section 11.8)."""
    content: str
    attachments: list[Attachment] = Field(default_factory=list)

    def to_claude_message(self) -> dict:
        """Convert to Claude API message format with vision support."""
        content_blocks = []

        # Text content
        if self.content:
            content_blocks.append({"type": "text", "text": self.content})

        # Image attachments for vision
        for attachment in self.attachments:
            if attachment.type.startswith("image/"):
                content_blocks.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": attachment.media_type,
                        "data": attachment.data,
                    },
                })

        return {"role": "user", "content": content_blocks}


class SwitchModelRequest(BaseModel):
    """Request to switch model mid-conversation (spec Section 4.3)."""
    chat_id: str
    new_model_id: str
    reason: Optional[str] = None


class ToggleSkillRequest(BaseModel):
    """Request to toggle a skill during conversation (spec Section 5.2)."""
    chat_id: str
    skill_id: str
    enabled: bool
    reason: Optional[str] = None


class ExecuteActionRequest(BaseModel):
    """Request to execute a post-completion action (spec Section 3.3)."""
    chat_id: str
    artifact_id: str
    action: dict  # {type, config}
    context: dict  # {userId, organizationId, clientId?}


class ExecuteActionResponse(BaseModel):
    """Response from executing an action."""
    success: bool
    new_chat_id: Optional[str] = None
    new_agent_type: Optional[str] = None
    external_url: Optional[str] = None
    module_url: Optional[str] = None
    share_result: Optional[dict] = None
    error: Optional[str] = None


# ============================================
# Event Wrappers
# ============================================

class AgentEvent(BaseModel):
    """Event from Agent Builder to SpokeStack."""
    type: str
    payload: dict


class PlatformEvent(BaseModel):
    """Event from SpokeStack to Agent Builder."""
    type: str
    payload: dict


# ============================================
# Agent Type Mapping (spec Section 11.7)
# ============================================

# Mission Control -> Agent Builder mapping
MC_TO_AGENT_BUILDER_MAP = {
    "assistant": "workflow",
    "content_strategist": "content",
    "brief_writer": "brief",
    "deck_designer": "presentation",
    "video_director": "video_script",
    "document_writer": "copy",
    "analyst": "campaign_analytics",
    "media_buyer": "media_buying",
    "course_designer": "training",
    "contract_analyzer": "legal",
    "resource_planner": "resource",
}

# Reverse mapping
AGENT_BUILDER_TO_MC_MAP = {v: k for k, v in MC_TO_AGENT_BUILDER_MAP.items()}


def resolve_agent_type(mc_type: str) -> str:
    """Resolve Mission Control agent type to Agent Builder type."""
    return MC_TO_AGENT_BUILDER_MAP.get(mc_type, mc_type)
