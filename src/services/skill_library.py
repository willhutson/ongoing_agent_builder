"""
Skill Library Service

Makes skills invokable by users and agents. Skills can be:
1. Directly invoked by users (routes to appropriate agent with skill context)
2. Injected into agent context during execution
3. Called as tools by agents during conversations
"""

from typing import Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..knowledge import (
    get_skill,
    get_brainstorm_context,
    get_positioning_frameworks,
    list_all_skills,
    ALL_SKILLS,
    SkillCategory,
)
from ..knowledge.marketing.positioning import (
    POSITIONING_ANGLES,
    VALUE_PROP_FORMULAS,
    HEADLINE_FORMULAS,
    MarketStage,
    PositioningAngle,
)


class SkillInvocationType(str, Enum):
    """How a skill can be invoked."""
    USER_DIRECT = "user_direct"      # User invokes directly
    AGENT_CONTEXT = "agent_context"  # Injected into agent
    AGENT_TOOL = "agent_tool"        # Called by agent as tool


@dataclass
class SkillInvocation:
    """Result of invoking a skill."""
    skill_id: str
    skill_name: str
    agent_to_use: str
    context_to_inject: dict
    suggested_prompt: str
    key_questions: list[str]


class SkillLibrary:
    """
    Central service for skill management and invocation.

    Users can browse and invoke skills directly. When invoked,
    the skill routes to the appropriate agent with relevant
    frameworks and context pre-loaded.
    """

    def __init__(self):
        self._skills = ALL_SKILLS
        self._custom_skills: dict[str, dict] = {}  # Instance-specific skills

    # =========================================================================
    # SKILL DISCOVERY
    # =========================================================================

    def list_skills(
        self,
        category: Optional[SkillCategory] = None,
        search: Optional[str] = None,
    ) -> list[dict]:
        """List available skills with optional filtering."""
        skills = []

        for skill_id, skill in self._skills.items():
            if category and skill.category != category:
                continue
            if search and search.lower() not in skill.name.lower():
                continue

            skills.append({
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "category": skill.category.value,
                "complexity": skill.complexity.value,
                "agent": skill.agent_mapping,
                "invokable": True,
            })

        return skills

    def get_skill_details(self, skill_id: str) -> Optional[dict]:
        """Get full details for a skill."""
        skill = get_skill(skill_id)
        if not skill:
            return None

        return {
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "category": skill.category.value,
            "complexity": skill.complexity.value,
            "use_cases": skill.use_cases,
            "key_questions": skill.key_questions,
            "deliverables": skill.deliverables,
            "best_practices": skill.best_practices,
            "common_mistakes": skill.common_mistakes,
            "tools_used": skill.tools_used,
            "agent": skill.agent_mapping,
        }

    # =========================================================================
    # SKILL INVOCATION
    # =========================================================================

    def invoke_skill(
        self,
        skill_id: str,
        user_input: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> SkillInvocation:
        """
        Invoke a skill - prepares context for the appropriate agent.

        Returns the agent to use and the context to inject.
        """
        skill = get_skill(skill_id)
        if not skill:
            raise ValueError(f"Unknown skill: {skill_id}")

        # Build context to inject into agent
        inject_context = {
            "skill": {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
            },
            "guidance": {
                "best_practices": skill.best_practices,
                "common_mistakes": skill.common_mistakes,
                "deliverables": skill.deliverables,
            },
        }

        # Add frameworks based on skill type
        if skill.category == SkillCategory.CONTENT:
            inject_context["frameworks"] = {
                "positioning": get_positioning_frameworks(),
            }
        elif skill.category == SkillCategory.STRATEGY:
            inject_context["frameworks"] = {
                "positioning": get_positioning_frameworks(),
                "value_props": VALUE_PROP_FORMULAS,
            }
        elif skill.category == SkillCategory.CONVERSION:
            inject_context["frameworks"] = {
                "headlines": HEADLINE_FORMULAS,
            }

        # Add user context if provided
        if context:
            inject_context["user_context"] = context

        # Build suggested prompt
        prompt_parts = [f"Using the {skill.name} skill:"]
        if user_input:
            prompt_parts.append(f"\n{user_input}")
        else:
            prompt_parts.append("\nPlease help me with the following:")
            for q in skill.key_questions[:3]:
                prompt_parts.append(f"- {q}")

        return SkillInvocation(
            skill_id=skill.id,
            skill_name=skill.name,
            agent_to_use=skill.agent_mapping or "content_agent",
            context_to_inject=inject_context,
            suggested_prompt="\n".join(prompt_parts),
            key_questions=skill.key_questions,
        )

    # =========================================================================
    # BRAINSTORM MODE
    # =========================================================================

    def start_brainstorm(
        self,
        task_type: str,
        market_stage: Optional[str] = None,
        audience: Optional[str] = None,
        product: Optional[str] = None,
    ) -> dict:
        """
        Start a brainstorming session with relevant frameworks loaded.

        Returns context for creative ideation including:
        - Positioning angles and templates
        - Value proposition formulas
        - Headline formulas
        - Relevant skills
        """
        context = get_brainstorm_context(task_type, market_stage, audience)

        # Add product-specific suggestions
        if product:
            context["product"] = product

        # Add angle recommendations
        if market_stage:
            try:
                stage = MarketStage(market_stage)
                stage_info = {
                    MarketStage.NEW: {
                        "approach": "Simple promise",
                        "recommended_angles": ["transformation", "speed"],
                        "example": "Now you can [X]",
                    },
                    MarketStage.GROWING: {
                        "approach": "Bigger claim",
                        "recommended_angles": ["speed", "transformation"],
                        "example": "[X] in [specific time]",
                    },
                    MarketStage.CROWDED: {
                        "approach": "Show mechanism",
                        "recommended_angles": ["contrarian", "specificity"],
                        "example": "The [method] that works",
                    },
                    MarketStage.JADED: {
                        "approach": "Prove it",
                        "recommended_angles": ["contrarian", "enemy"],
                        "example": "[Data/proof] that shows",
                    },
                    MarketStage.MATURE: {
                        "approach": "Sell identity",
                        "recommended_angles": ["specificity", "transformation"],
                        "example": "For [people who are X]",
                    },
                }
                context["stage_strategy"] = stage_info.get(stage, {})
            except ValueError:
                pass

        # Add value prop formulas
        context["value_prop_formulas"] = VALUE_PROP_FORMULAS
        context["headline_formulas"] = HEADLINE_FORMULAS

        return {
            "mode": "brainstorm",
            "task_type": task_type,
            "context": context,
            "instructions": self._get_brainstorm_instructions(task_type),
        }

    def _get_brainstorm_instructions(self, task_type: str) -> str:
        """Get instructions for brainstorm mode."""
        instructions = {
            "landing_page": """
Brainstorm Mode: Landing Page

1. Start with positioning - what angle resonates with your market stage?
2. Write 5-10 headline variations using the formulas provided
3. Identify the core transformation (before → after)
4. List objections to address
5. Define social proof needed
            """,
            "email": """
Brainstorm Mode: Email Sequence

1. Define the goal of the sequence
2. Map the value journey (what does each email deliver?)
3. Write subject line variations for each email
4. Identify key CTAs and their timing
5. Plan segmentation triggers
            """,
            "pricing": """
Brainstorm Mode: Pricing Strategy

1. Identify value metrics (what do customers pay for?)
2. Analyze competitor positioning
3. Design 2-3 tier structure
4. Create anchoring strategy
5. Plan upgrade triggers
            """,
            "launch": """
Brainstorm Mode: Launch Strategy

1. Define launch goals and success metrics
2. Identify announcement channels
3. Create messaging hierarchy
4. Plan pre-launch, launch, post-launch
5. List assets needed
            """,
        }
        return instructions.get(task_type, "Brainstorm mode active. Use the frameworks provided to generate ideas.")

    # =========================================================================
    # FRAMEWORK ACCESS
    # =========================================================================

    def get_positioning_angles(self) -> list[dict]:
        """Get all positioning angles with examples."""
        return [
            {
                "angle": angle.value,
                "description": framework.description,
                "template": framework.template,
                "examples": framework.examples,
                "best_for": framework.best_for,
            }
            for angle, framework in POSITIONING_ANGLES.items()
        ]

    def get_headline_formulas(self) -> dict:
        """Get headline formulas."""
        return HEADLINE_FORMULAS

    def get_value_prop_formulas(self) -> dict:
        """Get value proposition formulas."""
        return VALUE_PROP_FORMULAS


# Singleton instance
_skill_library: Optional[SkillLibrary] = None


def get_skill_library() -> SkillLibrary:
    """Get the singleton SkillLibrary instance."""
    global _skill_library
    if _skill_library is None:
        _skill_library = SkillLibrary()
    return _skill_library
