"""
Agent-to-Agent Handoff Protocol (Integration Spec Section 6)

Defines how agents spawn other agents with context passing,
user approval flows, and cross-agent artifact references.
"""

from typing import Optional
from pydantic import BaseModel, Field


class HandoffContext(BaseModel):
    """Context passed from parent agent to child agent."""
    parent_chat_id: str
    parent_agent_type: str
    parent_summary: str
    artifacts: list[dict] = Field(default_factory=list)
    relevant_messages: list[dict] = Field(default_factory=list)
    task: str
    constraints: Optional[list[str]] = None
    artifact_format: Optional[str] = None  # Format passthrough for Mission Control routing
    organization_id: Optional[str] = None  # Tenant for billing and scoping
    user_id: Optional[str] = None  # User initiating the handoff
    module_subdomain: Optional[str] = None  # Module scope for agent validation


class HandoffRequest(BaseModel):
    """Request from an agent to hand off to another agent."""
    from_chat_id: str
    from_agent_type: str
    to_agent_type: str
    context: HandoffContext
    requires_user_approval: bool = True
    auto_start: bool = False
    organization_id: Optional[str] = None  # Top-level org override


class HandoffResponse(BaseModel):
    """Response to a handoff request."""
    approved: bool
    new_chat_id: Optional[str] = None
    new_agent_type: Optional[str] = None
    message: str = ""
