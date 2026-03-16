"""
SpokeStack Skills Module

Layer 2 (Platform Skills) and specialized capabilities for agents.
"""

from .agent_browser import (
    AgentBrowserSkill,
    BrowserResult,
    SnapshotResult,
    quick_scrape
)

from .platform_skills import (
    PLATFORM_SKILLS,
    PlatformSkill,
    SkillCategory,
    get_platform_skill_tools,
    get_platform_skill,
    list_platform_skills,
)

__all__ = [
    "AgentBrowserSkill",
    "BrowserResult",
    "SnapshotResult",
    "quick_scrape",
    "PLATFORM_SKILLS",
    "PlatformSkill",
    "SkillCategory",
    "get_platform_skill_tools",
    "get_platform_skill",
    "list_platform_skills",
]
