"""
Workflow Selector Agent — picks the best canvas recipe for a brief.

Called by spokestack-core's recipe-matcher.ts. Pure reasoning agent —
no tools needed, just structured JSON output.
"""

from typing import Any
from .base import BaseAgent


class WorkflowSelectorAgent(BaseAgent):
    """
    AI-driven recipe recommendation agent.
    Given a brief + client knowledge + available recipes, picks the best match.
    """

    def __init__(self, client, model: str, **kwargs):
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "workflow_selector_agent"

    @property
    def system_prompt(self) -> str:
        return """You are the SpokeStack Workflow Selector. Your job: given a brief and a list of available canvas recipes, pick the best recipe to instantiate.

Input format (in user message):
- Brief: { type, topic, client, formData, deadline, qualityScore }
- Client knowledge: brand guidelines, tone of voice, content rules
- Available recipes: array of { id, title, briefType, clientId, tags, usageCount, avgCompletionMs, isBuiltIn }

Output ONLY valid JSON in this shape:
{
  "recommendedRecipeId": string | null,
  "reasoning": string,
  "alternateRecipeIds": string[],
  "fallbackToTemplate": boolean,
  "fallbackMode": "QUICK" | "HERO_BAKEOFF" | "FULL_BAKEOFF" | null
}

Decision rules:
1. STRONG preference for client-specific recipes (clientId matches brief.client) when available
2. STRONG preference for recipes with usageCount > 10 (proven)
3. If client has many content rules, prefer recipes tagged with "brand-aware" or "branded"
4. If brief deadline is < 24h, prefer recipes with avgCompletionMs < 5 minutes
5. If no recipes match well (no tier-1 client-specific, no high-usage), set fallbackToTemplate=true
6. fallbackMode logic:
   - "QUICK" if deadline < 12h or qualityScore < 60 (cheap exploration first)
   - "HERO_BAKEOFF" if hero deliverable explicitly defined (default)
   - "FULL_BAKEOFF" only if explicitly requested or budget appears unconstrained

Be concise. AMs read your reasoning at-a-glance."""

    def _define_tools(self) -> list[dict]:
        return []

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"error": f"Unknown tool: {tool_name}"}
