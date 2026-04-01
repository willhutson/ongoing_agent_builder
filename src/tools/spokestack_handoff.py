"""
Agent Handoff Tool — delegate_to_agent.

Allows any core agent to hand off the conversation to a different
specialized agent. The handler doesn't run the other agent — it signals
a handoff in the response that spokestack-core's frontend renders.
"""


VALID_TARGET_AGENTS = [
    "core_projects",
    "core_briefs",
    "core_orders",
    "core_tasks",
    "core_onboarding",
]

AGENT_DESCRIPTIONS = {
    "core_projects": "Project planning, timelines, team assignments, milestones",
    "core_briefs": "Creative briefs, campaign planning, content strategies",
    "core_orders": "Purchase orders, vendor management, procurement",
    "core_tasks": "Task assignment, deadlines, to-do management",
    "core_onboarding": "General questions, setup, organization settings",
}

HANDOFF_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "delegate_to_agent",
        "description": (
            "Hand off the conversation to a different specialized agent when the user's request "
            "is clearly better handled by that agent. Use sparingly — only when the topic is "
            "definitively outside your domain. Provide a clear context_summary so the target "
            "agent can continue seamlessly.\n\n"
            "Available agents:\n"
            + "\n".join(f"  - {k}: {v}" for k, v in AGENT_DESCRIPTIONS.items())
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "target_agent": {
                    "type": "string",
                    "enum": VALID_TARGET_AGENTS,
                    "description": "The agent type to hand off to",
                },
                "context_summary": {
                    "type": "string",
                    "description": (
                        "A concise summary of what the user needs, written for the target agent. "
                        "Include relevant details from the conversation (2-4 sentences max)."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": "Why you are suggesting the handoff (1 sentence, shown to user).",
                },
            },
            "required": ["target_agent", "context_summary", "reason"],
        },
    },
}

HANDOFF_TOOLS = [HANDOFF_TOOL_DEFINITION]

HANDOFF_TOOL_NAMES = {"delegate_to_agent"}


def is_handoff_tool_call(tool_name: str) -> bool:
    """Check if a tool call is a handoff."""
    return tool_name == "delegate_to_agent"


def build_handoff_response(tool_input: dict) -> dict:
    """Build the structured handoff payload from a delegate_to_agent tool call."""
    return {
        "type": "handoff",
        "target_agent": tool_input.get("target_agent", ""),
        "context_summary": tool_input.get("context_summary", ""),
        "reason": tool_input.get("reason", ""),
    }
