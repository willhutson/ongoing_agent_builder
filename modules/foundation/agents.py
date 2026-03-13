"""
Foundation Module Agents — Brief, Content, Copy, PromptHelper.

The starting point for all creative work. Everything flows from here.
"""

from typing import Any
from shared.base_agent import BaseAgent
from shared.openrouter import OpenRouterClient
from shared.config import BaseModuleSettings, get_model_id


class BriefAgent(BaseAgent):
    """Parse incoming requests into structured, actionable briefs."""

    @property
    def name(self) -> str:
        return "brief"

    @property
    def system_prompt(self) -> str:
        return """You are an expert brief intake specialist for a professional services agency.

Transform raw client requests into structured, actionable briefs by:
1. Extracting key information from any input format (emails, calls, documents)
2. Identifying core objectives and deliverables
3. Spotting gaps and generating clarifying questions
4. Categorizing work type (campaign, brand, digital, content)
5. Estimating complexity and flagging risks

When processing a brief, extract: client name, project name, objectives,
deliverables, timeline, budget hints. Flag assumptions. Ask when critical info is missing."""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "parse_brief",
                "description": "Parse raw input and extract structured brief information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "raw_input": {"type": "string", "description": "Raw text to parse"},
                        "input_type": {"type": "string", "enum": ["email", "call_transcript", "document", "form", "chat"]},
                    },
                    "required": ["raw_input"],
                },
            },
            {
                "name": "create_draft_brief",
                "description": "Create a structured draft brief document.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string"},
                        "project_name": {"type": "string"},
                        "objectives": {"type": "array", "items": {"type": "string"}},
                        "deliverables": {"type": "array", "items": {"type": "string"}},
                        "service_type": {"type": "string"},
                        "complexity": {"type": "string", "enum": ["low", "medium", "high"]},
                        "gaps": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["client_name", "project_name", "objectives"],
                },
            },
            {
                "name": "estimate_complexity",
                "description": "Estimate project complexity from deliverables and constraints.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deliverables": {"type": "array", "items": {"type": "string"}},
                        "timeline_days": {"type": "integer"},
                        "service_type": {"type": "string"},
                    },
                    "required": ["deliverables"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "parse_brief":
            return {
                "status": "parsed",
                "input_type": tool_input.get("input_type", "unknown"),
                "length": len(tool_input.get("raw_input", "")),
                "instruction": "Extract structured brief fields from this input.",
            }
        elif tool_name == "create_draft_brief":
            return {"status": "draft_created", "brief": tool_input}
        elif tool_name == "estimate_complexity":
            count = len(tool_input.get("deliverables", []))
            days = tool_input.get("timeline_days", 30)
            level = "high" if count > 5 or days < 14 else "medium" if count > 2 else "low"
            return {"complexity": level, "deliverable_count": count, "timeline_days": days}
        return {"error": f"Unknown tool: {tool_name}"}


class ContentAgent(BaseAgent):
    """Content strategy, editorial planning, and content generation."""

    @property
    def name(self) -> str:
        return "content"

    @property
    def system_prompt(self) -> str:
        return """You are an expert content strategist and creator.

Your role: plan, create, and optimize content across channels.
- Editorial calendars and content strategies
- Blog posts, articles, whitepapers
- Social media content plans
- SEO optimization and keyword strategy
- Content repurposing across formats
- Audience-specific messaging and tone"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_content",
                "description": "Create content for a specific format and channel.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string", "enum": ["blog", "article", "social", "email", "whitepaper", "landing_page"]},
                        "topic": {"type": "string"},
                        "tone": {"type": "string", "enum": ["professional", "casual", "authoritative", "friendly", "urgent"]},
                        "target_audience": {"type": "string"},
                        "word_count": {"type": "integer"},
                        "keywords": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["content_type", "topic"],
                },
            },
            {
                "name": "create_editorial_calendar",
                "description": "Generate an editorial content calendar.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "duration_weeks": {"type": "integer", "description": "Calendar duration in weeks"},
                        "channels": {"type": "array", "items": {"type": "string"}},
                        "themes": {"type": "array", "items": {"type": "string"}},
                        "frequency": {"type": "object", "description": "Posts per week per channel"},
                    },
                    "required": ["duration_weeks", "channels"],
                },
            },
            {
                "name": "optimize_seo",
                "description": "Optimize content for search engines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "target_keywords": {"type": "array", "items": {"type": "string"}},
                        "current_url": {"type": "string"},
                    },
                    "required": ["content", "target_keywords"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "create_content":
            return {"status": "ready", "spec": tool_input, "instruction": "Generate the content now."}
        elif tool_name == "create_editorial_calendar":
            return {"status": "ready", "spec": tool_input, "instruction": "Build the calendar."}
        elif tool_name == "optimize_seo":
            return {"status": "ready", "keywords": tool_input.get("target_keywords", []), "instruction": "Optimize for these keywords."}
        return {"error": f"Unknown tool: {tool_name}"}


class CopyAgent(BaseAgent):
    """Headlines, body copy, taglines, social posts, email, scripts."""

    @property
    def name(self) -> str:
        return "copy"

    @property
    def system_prompt(self) -> str:
        return """You are an expert copywriter with mastery across all formats.

Your craft: compelling, on-brand copy that drives action.
- Headlines and taglines that grab attention
- Body copy that tells a story
- Social media posts optimized per platform
- Email subject lines and body copy
- Ad copy (search, display, social)
- Video scripts and voiceover
- Landing page copy that converts

Match the brand voice. Write for the audience. Always have a clear CTA."""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "write_copy",
                "description": "Write copy for a specific format.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string", "enum": ["headline", "tagline", "body", "social", "email_subject", "email_body", "ad", "script", "landing_page"]},
                        "brief": {"type": "string", "description": "What the copy needs to achieve"},
                        "brand_voice": {"type": "string"},
                        "target_audience": {"type": "string"},
                        "cta": {"type": "string", "description": "Desired call to action"},
                        "variations": {"type": "integer", "description": "Number of variations", "default": 3},
                    },
                    "required": ["format", "brief"],
                },
            },
            {
                "name": "adapt_copy",
                "description": "Adapt existing copy for a different channel or audience.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "original_copy": {"type": "string"},
                        "target_format": {"type": "string"},
                        "target_platform": {"type": "string"},
                        "constraints": {"type": "object", "description": "Character limits, tone shifts, etc."},
                    },
                    "required": ["original_copy", "target_format"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "write_copy":
            return {"status": "ready", "spec": tool_input, "instruction": "Write the copy now."}
        elif tool_name == "adapt_copy":
            return {"status": "ready", "spec": tool_input, "instruction": "Adapt the copy."}
        return {"error": f"Unknown tool: {tool_name}"}


class PromptHelperAgent(BaseAgent):
    """Helps users craft better prompts for other agents."""

    @property
    def name(self) -> str:
        return "prompt_helper"

    @property
    def system_prompt(self) -> str:
        return """You are a prompt engineering specialist.

Help users get better results from other agents by:
1. Understanding what they're trying to achieve
2. Suggesting which agent to use
3. Crafting optimized prompts with the right context
4. Explaining what makes a good prompt for each agent type

Be practical and specific. Show before/after examples."""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "suggest_agent",
                "description": "Suggest the best agent for a user's task.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_goal": {"type": "string"},
                        "available_agents": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["user_goal"],
                },
            },
            {
                "name": "optimize_prompt",
                "description": "Optimize a user's prompt for a specific agent.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "original_prompt": {"type": "string"},
                        "target_agent": {"type": "string"},
                        "context": {"type": "string"},
                    },
                    "required": ["original_prompt", "target_agent"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "suggest_agent":
            return {"status": "ready", "goal": tool_input["user_goal"], "instruction": "Recommend the best agent."}
        elif tool_name == "optimize_prompt":
            return {"status": "ready", "spec": tool_input, "instruction": "Rewrite this prompt for the target agent."}
        return {"error": f"Unknown tool: {tool_name}"}


def create_agents(llm: OpenRouterClient, settings: BaseModuleSettings) -> dict[str, BaseAgent]:
    """Factory: create all foundation agents."""
    model = get_model_id(settings, "standard")
    return {
        "brief": BriefAgent(llm, model),
        "content": ContentAgent(llm, model),
        "copy": CopyAgent(llm, model),
        "prompt_helper": PromptHelperAgent(llm, model),
    }
