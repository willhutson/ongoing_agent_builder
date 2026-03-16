"""
Instance Skills (Layer 3) — Per-organization custom skills.

From AGENT_ARCHITECTURE.md:
- Layer 3 skills are custom per organization (premium feature, Phase 2+)
- Organizations can define their own skills that encode org-specific processes
- Skills are stored per organizationId and loaded at agent runtime
- Example: "TeamLMTD Brief Template" skill that enforces their specific brief format

Phase 2+ implementation: This module defines the interfaces and storage.
Actual skill execution reuses the same LLM-based pattern as platform skills.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class InstanceSkillStatus(str, Enum):
    """Lifecycle status of an instance skill."""
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"
    ARCHIVED = "archived"


@dataclass
class InstanceSkill:
    """A custom skill defined by a specific organization."""
    id: str
    organization_id: str
    name: str
    display_name: str
    description: str
    status: InstanceSkillStatus = InstanceSkillStatus.DRAFT

    # The skill's system prompt — what expertise it encodes
    system_prompt: str = ""

    # Tool definition (same format as platform skills)
    tool_definition: dict = field(default_factory=dict)

    # Optional: restrict to specific agent types
    allowed_agents: list[str] = field(default_factory=list)

    # Metadata
    created_by: Optional[str] = None
    version: int = 1


# =============================================================================
# INSTANCE SKILL STORE (Phase 2 — will be backed by DB)
# =============================================================================

# In-memory store for now; Phase 2 will use Prisma/PostgreSQL
_instance_skills: dict[str, dict[str, InstanceSkill]] = {}
# Structure: { organization_id: { skill_id: InstanceSkill } }


async def get_instance_skills(organization_id: str) -> list[InstanceSkill]:
    """Get all active instance skills for an organization."""
    org_skills = _instance_skills.get(organization_id, {})
    return [s for s in org_skills.values() if s.status == InstanceSkillStatus.ACTIVE]


async def get_instance_skill(organization_id: str, skill_id: str) -> Optional[InstanceSkill]:
    """Get a specific instance skill."""
    org_skills = _instance_skills.get(organization_id, {})
    return org_skills.get(skill_id)


async def save_instance_skill(skill: InstanceSkill) -> InstanceSkill:
    """Save or update an instance skill."""
    if skill.organization_id not in _instance_skills:
        _instance_skills[skill.organization_id] = {}
    _instance_skills[skill.organization_id][skill.id] = skill
    return skill


async def delete_instance_skill(organization_id: str, skill_id: str) -> bool:
    """Delete an instance skill."""
    org_skills = _instance_skills.get(organization_id, {})
    if skill_id in org_skills:
        del org_skills[skill_id]
        return True
    return False


def get_instance_skill_tools(organization_id: str) -> list[dict]:
    """Get tool definitions for all active instance skills for an org.

    Called during agent initialization to merge org-specific skills
    into the agent's tool list alongside platform skills.
    """
    org_skills = _instance_skills.get(organization_id, {})
    return [
        s.tool_definition
        for s in org_skills.values()
        if s.status == InstanceSkillStatus.ACTIVE and s.tool_definition
    ]
