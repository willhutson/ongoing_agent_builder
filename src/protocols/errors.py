"""
Error Handling Protocol (Integration Spec Section 9)

Defines error codes and error response format for
consistent error handling across Agent Builder and SpokeStack.
"""

from typing import Optional
from pydantic import BaseModel


# Error code definitions (spec Section 9.1)
ERROR_CODES = {
    # Agent errors
    "AGENT_NOT_FOUND": "Agent type not available",
    "AGENT_BUSY": "Agent is processing another request",
    "AGENT_TIMEOUT": "Agent took too long to respond",
    # Model errors
    "MODEL_NOT_AVAILABLE": "Selected model not available",
    "MODEL_RATE_LIMITED": "Model API rate limited",
    "MODEL_CONTEXT_EXCEEDED": "Conversation too long for model",
    # Skill errors
    "SKILL_NOT_FOUND": "Skill not found",
    "SKILL_EXECUTION_FAILED": "Skill failed to execute",
    # Action errors
    "ACTION_NOT_SUPPORTED": "Action not supported for this artifact",
    "ACTION_FAILED": "Action execution failed",
    # Auth errors
    "UNAUTHORIZED": "Invalid or expired token",
    "FORBIDDEN": "Insufficient permissions",
    "ORG_NOT_FOUND": "Organization not found",
    # Work errors
    "WORK_API_ERROR": "SpokeStack API call failed",
    "WORK_FORM_VALIDATION": "Form validation failed",
    "WORK_ENTITY_NOT_FOUND": "Entity not found in SpokeStack",
}


class AgentError(BaseModel):
    """Standardized error response format (spec Section 9.2)."""
    code: str
    message: str
    details: Optional[dict] = None
    recoverable: bool = False
    retry_after: Optional[int] = None  # Seconds
    user_action_required: Optional[str] = None

    @classmethod
    def from_code(cls, code: str, details: Optional[dict] = None, **kwargs) -> "AgentError":
        """Create an error from a predefined code."""
        message = ERROR_CODES.get(code, "Unknown error")
        return cls(code=code, message=message, details=details, **kwargs)

    def to_sse(self) -> str:
        """Serialize as SSE event."""
        import json
        data = self.model_dump(exclude_none=True)
        return f"event: error\ndata: {json.dumps(data)}\n\n"
