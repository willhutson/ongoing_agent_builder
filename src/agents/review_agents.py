"""
Review Agents — automated first-pass review for marketplace module submissions.
"""

from typing import Any
from .base import BaseAgent


class ModuleReviewerAgent(BaseAgent):
    """
    Module Reviewer — automated security and quality review.
    Triggered by spokestack-core when a module is submitted.
    Internal only — not exposed to end users.
    """

    def __init__(self, client, model: str, **kwargs):
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "module_reviewer_agent"

    @property
    def system_prompt(self) -> str:
        return """You are the SpokeStack Module Reviewer. You analyze submitted modules for security issues, quality, and marketplace readiness.

When you receive a review task, follow this exact sequence:
1. Call analyze_tools with the module's tool definitions
2. Call analyze_prompt with the module's system prompt
3. Call check_duplicates with the module's name and description
4. Call generate_review to produce the structured report
5. If security_score >= 9 AND quality_score >= 7: call approve_module
6. If security_score < 5 (blockers found): call reject_module with detailed feedback
7. Otherwise (scores 5-8): do nothing — enters human review queue

## Security scoring (1-10)

- All tools call /api/v1/* only → required for any score above 0
- No admin, auth, or marketplace routes → each is -3 points
- No external URLs → -3 points
- No injection patterns in prompt → each found is -2 points

## Quality scoring (1-10)

- Clear purpose and description → +2
- All tools have descriptions → +1
- System prompt is substantive (200+ chars) → +1
- No marketplace duplicate → +2
- Well-formed slug → +1
- Reasonable pricing → +1

Be precise. Cite specific tool names when flagging issues."""

    def _define_tools(self) -> list[dict]:
        return []

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        from src.services.module_builder_service import analyze_tools, analyze_prompt

        if tool_name == "analyze_tools":
            return analyze_tools(tool_input.get("tools", []), tool_input.get("module_id", ""))
        elif tool_name == "analyze_prompt":
            return analyze_prompt(tool_input.get("system_prompt", ""), tool_input.get("module_id", ""))
        return {"error": f"Unknown tool: {tool_name}"}
