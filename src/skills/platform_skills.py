"""
Platform Skills (Layer 2) — Universal skills available to all agents.

From AGENT_ARCHITECTURE.md, these encode 15+ years of agency expertise
as reusable tools that any agent can invoke during execution.

Phase 2 implementation: Skills are registered as tools that agents can call.
Each skill takes structured input and returns structured output.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class SkillCategory(str, Enum):
    """Categories of platform skills."""
    QUALITY = "quality"
    PLANNING = "planning"
    DETECTION = "detection"
    ESTIMATION = "estimation"


@dataclass
class PlatformSkill:
    """Definition of a platform skill."""
    name: str
    display_name: str
    category: SkillCategory
    description: str
    tool_definition: dict = field(default_factory=dict)


# =============================================================================
# PLATFORM SKILLS REGISTRY
# =============================================================================

PLATFORM_SKILLS: dict[str, PlatformSkill] = {
    "brief_quality_scorer": PlatformSkill(
        name="brief_quality_scorer",
        display_name="Brief Quality Scorer",
        category=SkillCategory.QUALITY,
        description="Scores brief completeness and quality on a 0-100 scale. Checks for missing fields, ambiguous requirements, and scope clarity.",
        tool_definition={
            "type": "function",
            "function": {
                "name": "brief_quality_scorer",
                "description": "Score a brief for completeness and quality. Returns a score (0-100) with specific feedback on missing or weak areas.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brief_text": {
                            "type": "string",
                            "description": "The full brief text to score",
                        },
                        "brief_type": {
                            "type": "string",
                            "enum": ["campaign", "creative", "media", "pr", "event", "retainer", "project"],
                            "description": "Type of brief for context-appropriate scoring",
                        },
                        "check_fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific fields to check (e.g., ['objectives', 'budget', 'timeline', 'target_audience'])",
                        },
                    },
                    "required": ["brief_text"],
                },
            },
        },
    ),
    "smart_assigner": PlatformSkill(
        name="smart_assigner",
        display_name="Smart Assigner",
        category=SkillCategory.PLANNING,
        description="Recommends optimal team member assignment based on skills, availability, workload, and past performance.",
        tool_definition={
            "type": "function",
            "function": {
                "name": "smart_assigner",
                "description": "Recommend the best team member(s) for a task based on skills, availability, and workload balance.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Description of the task to assign",
                        },
                        "required_skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Skills required for the task",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Task priority level",
                        },
                        "estimated_hours": {
                            "type": "number",
                            "description": "Estimated hours to complete",
                        },
                        "deadline": {
                            "type": "string",
                            "description": "ISO 8601 deadline",
                        },
                    },
                    "required": ["task_description"],
                },
            },
        },
    ),
    "scope_creep_detector": PlatformSkill(
        name="scope_creep_detector",
        display_name="Scope Creep Detector",
        category=SkillCategory.DETECTION,
        description="Analyzes task changes against the original brief/SOW to detect scope creep. Returns risk level and specific deviations.",
        tool_definition={
            "type": "function",
            "function": {
                "name": "scope_creep_detector",
                "description": "Compare current work against original scope to detect creep. Returns risk assessment and specific deviations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "original_scope": {
                            "type": "string",
                            "description": "Original brief, SOW, or scope document",
                        },
                        "current_work": {
                            "type": "string",
                            "description": "Current task or deliverable description",
                        },
                        "change_requests": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of change requests or additions since original scope",
                        },
                    },
                    "required": ["original_scope", "current_work"],
                },
            },
        },
    ),
    "timeline_estimator": PlatformSkill(
        name="timeline_estimator",
        display_name="Timeline Estimator",
        category=SkillCategory.ESTIMATION,
        description="Estimates project timelines based on scope, team size, complexity, and historical data patterns.",
        tool_definition={
            "type": "function",
            "function": {
                "name": "timeline_estimator",
                "description": "Estimate project timeline with confidence intervals. Uses scope complexity and team capacity.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_description": {
                            "type": "string",
                            "description": "Description of the project or deliverable",
                        },
                        "deliverables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of specific deliverables",
                        },
                        "team_size": {
                            "type": "integer",
                            "description": "Number of team members assigned",
                        },
                        "complexity": {
                            "type": "string",
                            "enum": ["simple", "moderate", "complex", "highly_complex"],
                            "description": "Overall project complexity",
                        },
                        "dependencies": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "External dependencies or blockers",
                        },
                    },
                    "required": ["project_description"],
                },
            },
        },
    ),
}


def get_platform_skill_tools() -> list[dict]:
    """Get all platform skills as tool definitions for agent registration."""
    return [skill.tool_definition for skill in PLATFORM_SKILLS.values()]


def get_platform_skill(name: str) -> Optional[PlatformSkill]:
    """Get a specific platform skill by name."""
    return PLATFORM_SKILLS.get(name)


def list_platform_skills() -> list[dict]:
    """List all platform skills with metadata."""
    return [
        {
            "name": skill.name,
            "display_name": skill.display_name,
            "category": skill.category.value,
            "description": skill.description,
        }
        for skill in PLATFORM_SKILLS.values()
    ]
