"""Tests for Platform Skills (Layer 2) and Instance Skills/Knowledge (Layer 3/4)."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.skills.platform_skills import (
    PLATFORM_SKILLS,
    PlatformSkill,
    SkillCategory,
    get_platform_skill_tools,
    get_platform_skill,
    list_platform_skills,
)
from src.skills.instance_skills import (
    InstanceSkill,
    InstanceSkillStatus,
    get_instance_skills,
    get_instance_skill,
    save_instance_skill,
    delete_instance_skill,
    get_instance_skill_tools,
)
from src.knowledge.instance_knowledge import (
    KnowledgeDocument,
    KnowledgeCategory,
    get_knowledge_documents,
    get_knowledge_document,
    save_knowledge_document,
    delete_knowledge_document,
    build_knowledge_context,
)


# =============================================================================
# PLATFORM SKILLS (LAYER 2)
# =============================================================================

class TestPlatformSkills:

    EXPECTED_SKILLS = [
        "brief_quality_scorer",
        "smart_assigner",
        "scope_creep_detector",
        "timeline_estimator",
    ]

    def test_all_skills_present(self):
        for name in self.EXPECTED_SKILLS:
            assert name in PLATFORM_SKILLS, f"Missing skill: {name}"

    def test_skill_count(self):
        assert len(PLATFORM_SKILLS) == 4

    def test_skill_structure(self):
        for name, skill in PLATFORM_SKILLS.items():
            assert isinstance(skill, PlatformSkill)
            assert skill.name == name
            assert skill.display_name
            assert skill.description
            assert isinstance(skill.category, SkillCategory)
            assert skill.tool_definition

    def test_tool_definitions_valid(self):
        tools = get_platform_skill_tools()
        assert len(tools) == 4
        for tool in tools:
            assert tool["type"] == "function"
            func = tool["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func
            assert func["parameters"]["type"] == "object"

    def test_get_platform_skill(self):
        skill = get_platform_skill("brief_quality_scorer")
        assert skill is not None
        assert skill.category == SkillCategory.QUALITY

    def test_get_platform_skill_not_found(self):
        assert get_platform_skill("nonexistent") is None

    def test_list_platform_skills(self):
        skills = list_platform_skills()
        assert len(skills) == 4
        assert all("name" in s for s in skills)
        assert all("category" in s for s in skills)

    def test_brief_quality_scorer_params(self):
        skill = PLATFORM_SKILLS["brief_quality_scorer"]
        params = skill.tool_definition["function"]["parameters"]
        assert "brief_text" in params["properties"]
        assert "brief_text" in params["required"]

    def test_scope_creep_detector_params(self):
        skill = PLATFORM_SKILLS["scope_creep_detector"]
        params = skill.tool_definition["function"]["parameters"]
        assert "original_scope" in params["properties"]
        assert "current_work" in params["properties"]


# =============================================================================
# INSTANCE SKILLS (LAYER 3)
# =============================================================================

class TestInstanceSkills:

    @pytest.fixture(autouse=True)
    def clear_store(self):
        """Clear the in-memory store between tests."""
        from src.skills.instance_skills import _instance_skills
        _instance_skills.clear()
        yield
        _instance_skills.clear()

    @pytest.fixture
    def sample_skill(self):
        return InstanceSkill(
            id="skill_001",
            organization_id="org_test",
            name="teamlmtd_brief_template",
            display_name="TeamLMTD Brief Template",
            description="Enforces TeamLMTD's specific brief format",
            system_prompt="You enforce the TeamLMTD brief template...",
            tool_definition={
                "type": "function",
                "function": {
                    "name": "teamlmtd_brief_template",
                    "description": "Apply TeamLMTD brief template",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            status=InstanceSkillStatus.ACTIVE,
            allowed_agents=["brief", "content"],
        )

    @pytest.mark.asyncio
    async def test_save_and_get_skill(self, sample_skill):
        await save_instance_skill(sample_skill)
        result = await get_instance_skill("org_test", "skill_001")
        assert result is not None
        assert result.name == "teamlmtd_brief_template"

    @pytest.mark.asyncio
    async def test_get_skills_filters_active(self, sample_skill):
        # Save active skill
        await save_instance_skill(sample_skill)

        # Save draft skill
        draft = InstanceSkill(
            id="skill_002",
            organization_id="org_test",
            name="draft_skill",
            display_name="Draft",
            description="Not active",
            status=InstanceSkillStatus.DRAFT,
        )
        await save_instance_skill(draft)

        active = await get_instance_skills("org_test")
        assert len(active) == 1
        assert active[0].id == "skill_001"

    @pytest.mark.asyncio
    async def test_delete_skill(self, sample_skill):
        await save_instance_skill(sample_skill)
        deleted = await delete_instance_skill("org_test", "skill_001")
        assert deleted is True

        result = await get_instance_skill("org_test", "skill_001")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_instance_skill_tools(self, sample_skill):
        await save_instance_skill(sample_skill)
        tools = get_instance_skill_tools("org_test")
        assert len(tools) == 1
        assert tools[0]["function"]["name"] == "teamlmtd_brief_template"

    @pytest.mark.asyncio
    async def test_get_skills_empty_org(self):
        skills = await get_instance_skills("nonexistent_org")
        assert skills == []


# =============================================================================
# INSTANCE KNOWLEDGE (LAYER 4)
# =============================================================================

class TestInstanceKnowledge:

    @pytest.fixture(autouse=True)
    def clear_store(self):
        from src.knowledge.instance_knowledge import _knowledge_store
        _knowledge_store.clear()
        yield
        _knowledge_store.clear()

    @pytest.fixture
    def sample_doc(self):
        return KnowledgeDocument(
            id="doc_001",
            organization_id="org_test",
            title="TeamLMTD Brand Voice Guide",
            content="TeamLMTD's voice is professional yet approachable...",
            category=KnowledgeCategory.BRAND,
            tags=["brand", "voice", "tone"],
            allowed_agents=["copy", "content"],
            allowed_modules=["studio"],
        )

    @pytest.mark.asyncio
    async def test_save_and_get_doc(self, sample_doc):
        await save_knowledge_document(sample_doc)
        result = await get_knowledge_document("org_test", "doc_001")
        assert result is not None
        assert result.title == "TeamLMTD Brand Voice Guide"

    @pytest.mark.asyncio
    async def test_filter_by_category(self, sample_doc):
        await save_knowledge_document(sample_doc)

        # Save a process doc
        process_doc = KnowledgeDocument(
            id="doc_002",
            organization_id="org_test",
            title="Approval Process",
            content="All briefs must go through...",
            category=KnowledgeCategory.PROCESS,
        )
        await save_knowledge_document(process_doc)

        brand_docs = await get_knowledge_documents("org_test", category=KnowledgeCategory.BRAND)
        assert len(brand_docs) == 1
        assert brand_docs[0].id == "doc_001"

    @pytest.mark.asyncio
    async def test_filter_by_agent(self, sample_doc):
        await save_knowledge_document(sample_doc)

        # copy agent should see it
        docs = await get_knowledge_documents("org_test", agent_type="copy")
        assert len(docs) == 1

        # invoice agent should not (restricted to copy/content)
        docs = await get_knowledge_documents("org_test", agent_type="invoice")
        assert len(docs) == 0

    @pytest.mark.asyncio
    async def test_filter_by_module(self, sample_doc):
        await save_knowledge_document(sample_doc)

        # studio module should see it
        docs = await get_knowledge_documents("org_test", module_subdomain="studio")
        assert len(docs) == 1

        # finance module should not
        docs = await get_knowledge_documents("org_test", module_subdomain="finance")
        assert len(docs) == 0

    @pytest.mark.asyncio
    async def test_unrestricted_doc_visible_everywhere(self):
        doc = KnowledgeDocument(
            id="doc_003",
            organization_id="org_test",
            title="Company Overview",
            content="We are a creative agency...",
            category=KnowledgeCategory.REFERENCE,
            # No allowed_agents or allowed_modules = visible to all
        )
        await save_knowledge_document(doc)

        docs = await get_knowledge_documents("org_test", agent_type="invoice")
        assert len(docs) == 1

        docs = await get_knowledge_documents("org_test", module_subdomain="finance")
        assert len(docs) == 1

    @pytest.mark.asyncio
    async def test_soft_delete(self, sample_doc):
        await save_knowledge_document(sample_doc)
        deleted = await delete_knowledge_document("org_test", "doc_001")
        assert deleted is True

        # Should not appear in listings
        docs = await get_knowledge_documents("org_test")
        assert len(docs) == 0

        # But raw get still returns it (soft deleted)
        doc = await get_knowledge_document("org_test", "doc_001")
        assert doc is not None
        assert doc.is_active is False

    @pytest.mark.asyncio
    async def test_build_knowledge_context(self, sample_doc):
        await save_knowledge_document(sample_doc)
        ctx = await build_knowledge_context("org_test", agent_type="copy")
        assert "Organization Knowledge" in ctx
        assert "TeamLMTD Brand Voice Guide" in ctx

    @pytest.mark.asyncio
    async def test_build_knowledge_context_empty(self):
        ctx = await build_knowledge_context("nonexistent_org")
        assert ctx == ""
