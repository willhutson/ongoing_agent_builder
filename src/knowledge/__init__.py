"""
Knowledge Library

Centralized knowledge bases that agents can inject into their context.
Provides frameworks, skills, and domain expertise for enhanced agent capabilities.
"""

from .marketing.positioning import (
    get_all_frameworks as get_positioning_frameworks,
    MarketStage,
    PositioningAngle,
    suggest_angles_for_context,
    validate_positioning,
)
from .marketing.skills import (
    get_skill,
    get_skills_by_category,
    get_skills_for_agent,
    list_all_skills,
    SkillCategory,
    ALL_SKILLS,
)


def get_knowledge_for_agent(agent_name: str) -> dict:
    """
    Get relevant knowledge for an agent to inject into its context.

    Returns frameworks, skills, and domain knowledge relevant to the agent.
    """
    knowledge = {
        "skills": [],
        "frameworks": {},
    }

    # Get skills mapped to this agent
    agent_skills = get_skills_for_agent(agent_name)
    knowledge["skills"] = [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "best_practices": s.best_practices,
            "common_mistakes": s.common_mistakes,
            "key_questions": s.key_questions,
        }
        for s in agent_skills
    ]

    # Add positioning frameworks for content/copy agents
    if agent_name in ["copy_agent", "content_agent", "campaign_agent", "brief_agent"]:
        knowledge["frameworks"]["positioning"] = get_positioning_frameworks()

    return knowledge


def get_brainstorm_context(
    task_type: str,
    market_stage: str = None,
    audience: str = None,
) -> dict:
    """
    Get context for brainstorming sessions.

    Provides relevant frameworks, angles, and formulas based on the task.
    """
    context = {
        "positioning": get_positioning_frameworks(),
        "suggested_angles": [],
        "relevant_skills": [],
    }

    # Suggest positioning angles based on market stage
    if market_stage:
        try:
            stage = MarketStage(market_stage)
            context["suggested_angles"] = [
                a.value for a in suggest_angles_for_context(market_stage=stage)
            ]
        except ValueError:
            pass

    # Get skills relevant to the task type
    task_skill_mapping = {
        "landing_page": ["page_cro", "copywriting", "form_cro"],
        "email": ["email_sequence", "copywriting"],
        "ads": ["paid_ads", "copywriting"],
        "pricing": ["pricing_strategy", "paywall_upgrade_cro"],
        "launch": ["launch_strategy", "social_content"],
        "seo": ["seo_audit", "programmatic_seo", "schema_markup"],
        "conversion": ["page_cro", "form_cro", "signup_flow_cro", "onboarding_cro"],
    }

    skill_ids = task_skill_mapping.get(task_type, [])
    context["relevant_skills"] = [
        {
            "id": s.id,
            "name": s.name,
            "best_practices": s.best_practices,
            "key_questions": s.key_questions,
        }
        for skill_id in skill_ids
        if (s := get_skill(skill_id))
    ]

    return context


__all__ = [
    # Positioning
    "get_positioning_frameworks",
    "MarketStage",
    "PositioningAngle",
    "suggest_angles_for_context",
    "validate_positioning",
    # Skills
    "get_skill",
    "get_skills_by_category",
    "get_skills_for_agent",
    "list_all_skills",
    "SkillCategory",
    "ALL_SKILLS",
    # Agent integration
    "get_knowledge_for_agent",
    "get_brainstorm_context",
]
