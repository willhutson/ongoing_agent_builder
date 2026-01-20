"""
Marketing Knowledge Library

Frameworks, skills, and domain expertise for marketing-focused agents.
"""

from .positioning import (
    get_all_frameworks,
    MarketStage,
    PositioningAngle,
    MARKET_STAGE_STRATEGIES,
    POSITIONING_ANGLES,
    VALUE_PROP_FORMULAS,
    HEADLINE_FORMULAS,
    POSITIONING_CHECKLIST,
    suggest_angles_for_context,
    validate_positioning,
)

from .skills import (
    get_skill,
    get_skills_by_category,
    get_skills_for_agent,
    list_all_skills,
    SkillCategory,
    SkillComplexity,
    ALL_SKILLS,
)

__all__ = [
    # Positioning
    "get_all_frameworks",
    "MarketStage",
    "PositioningAngle",
    "MARKET_STAGE_STRATEGIES",
    "POSITIONING_ANGLES",
    "VALUE_PROP_FORMULAS",
    "HEADLINE_FORMULAS",
    "POSITIONING_CHECKLIST",
    "suggest_angles_for_context",
    "validate_positioning",
    # Skills
    "get_skill",
    "get_skills_by_category",
    "get_skills_for_agent",
    "list_all_skills",
    "SkillCategory",
    "SkillComplexity",
    "ALL_SKILLS",
]
