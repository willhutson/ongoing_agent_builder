"""
SpokeStack Skills Module

Layer 2 (Platform Skills), Layer 3 (Instance Skills), and specialized capabilities.
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

from .instance_skills import (
    InstanceSkill,
    InstanceSkillStatus,
    get_instance_skills,
    get_instance_skill,
    save_instance_skill,
    delete_instance_skill,
    get_instance_skill_tools,
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
    "InstanceSkill",
    "InstanceSkillStatus",
    "get_instance_skills",
    "get_instance_skill",
    "save_instance_skill",
    "delete_instance_skill",
    "get_instance_skill_tools",
]
