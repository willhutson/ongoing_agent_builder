"""
SpokeStack Agent UI Components

Provides contextual agent UI components for the ERP frontend.
These definitions can be used to generate React/TypeScript components
or serve as API responses for frontend rendering.
"""

from .components import (
    AgentCapabilityCard,
    AgentContextualSuggestion,
    AgentQuickAction,
    WorkflowProgressCard,
    get_contextual_agents_for_module,
    get_quick_actions_for_context,
)

__all__ = [
    "AgentCapabilityCard",
    "AgentContextualSuggestion",
    "AgentQuickAction",
    "WorkflowProgressCard",
    "get_contextual_agents_for_module",
    "get_quick_actions_for_context",
]
