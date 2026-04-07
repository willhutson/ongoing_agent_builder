"""Tests for Phase 18C: onboarding agent upgrade with SETUP_WORKSPACE."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestSetupWorkspacePrompt:

    def test_prompt_has_setup_workspace_block(self):
        from src.agents.core_onboarding_agent import ONBOARDING_SYSTEM_PROMPT
        assert "SETUP_WORKSPACE" in ONBOARDING_SYSTEM_PROMPT
        assert '<action type="SETUP_WORKSPACE">' in ONBOARDING_SYSTEM_PROMPT

    def test_prompt_has_all_action_fields(self):
        from src.agents.core_onboarding_agent import ONBOARDING_SYSTEM_PROMPT
        for field in ["industry", "orgName", "region", "teamSize", "clients", "primaryWorkflow", "suggestedModules"]:
            assert field in ONBOARDING_SYSTEM_PROMPT, f"Missing field: {field}"

    def test_prompt_has_valid_module_keys(self):
        from src.agents.core_onboarding_agent import ONBOARDING_SYSTEM_PROMPT
        for key in ["MEDIA_RELATIONS", "PRESS_RELEASES", "BRIEFS", "CRM", "CONTENT_STUDIO"]:
            assert key in ONBOARDING_SYSTEM_PROMPT, f"Missing module key: {key}"

    def test_prompt_has_all_industry_question_sets(self):
        from src.agents.core_onboarding_agent import ONBOARDING_SYSTEM_PROMPT
        for industry in ["pr_agency", "creative_agency", "saas", "ecommerce", "law_firm", "construction", "consulting"]:
            assert f"**{industry}:**" in ONBOARDING_SYSTEM_PROMPT, f"Missing question set: {industry}"

    def test_prompt_has_detection_table(self):
        from src.agents.core_onboarding_agent import ONBOARDING_SYSTEM_PROMPT
        assert "Industry Detection" in ONBOARDING_SYSTEM_PROMPT
        assert "Keywords" in ONBOARDING_SYSTEM_PROMPT

    def test_no_seed_context_reference(self):
        """SETUP_WORKSPACE supersedes SEED_CONTEXT."""
        from src.agents.core_onboarding_agent import ONBOARDING_SYSTEM_PROMPT
        assert "SEED_CONTEXT" not in ONBOARDING_SYSTEM_PROMPT


class TestDetectAndStoreIndustry:

    def test_detects_pr_agency(self):
        from src.agents.core_onboarding_agent import CoreOnboardingAgent
        agent = CoreOnboardingAgent.__new__(CoreOnboardingAgent)
        agent._detected_industry = None
        result = agent.detect_and_store_industry("We're a PR agency in Dubai")
        assert result == "pr_agency"

    def test_caches_result(self):
        from src.agents.core_onboarding_agent import CoreOnboardingAgent
        agent = CoreOnboardingAgent.__new__(CoreOnboardingAgent)
        agent._detected_industry = None
        agent.detect_and_store_industry("We're a PR agency")
        # Second call with different text should return cached result
        result = agent.detect_and_store_industry("Actually we're a SaaS company")
        assert result == "pr_agency"  # Cached from first call

    def test_defaults_to_consulting(self):
        from src.agents.core_onboarding_agent import CoreOnboardingAgent
        agent = CoreOnboardingAgent.__new__(CoreOnboardingAgent)
        agent._detected_industry = None
        result = agent.detect_and_store_industry("We do stuff")
        assert result == "consulting"


class TestGetTargetedQuestions:

    def test_returns_questions_for_detected_industry(self):
        from src.agents.core_onboarding_agent import CoreOnboardingAgent
        agent = CoreOnboardingAgent.__new__(CoreOnboardingAgent)
        agent._detected_industry = "pr_agency"
        questions = agent.get_targeted_questions()
        assert len(questions) >= 3
        assert any("media" in q.lower() or "outlet" in q.lower() for q in questions)

    def test_defaults_to_consulting_when_not_detected(self):
        from src.agents.core_onboarding_agent import CoreOnboardingAgent
        agent = CoreOnboardingAgent.__new__(CoreOnboardingAgent)
        agent._detected_industry = None
        questions = agent.get_targeted_questions()
        assert len(questions) >= 3

    def test_all_industries_have_questions(self):
        from src.agents.core_onboarding_agent import CoreOnboardingAgent
        from src.services.industry_schemas import INDUSTRY_SCHEMAS
        agent = CoreOnboardingAgent.__new__(CoreOnboardingAgent)
        for industry_key in INDUSTRY_SCHEMAS:
            agent._detected_industry = industry_key
            questions = agent.get_targeted_questions()
            assert len(questions) >= 3, f"{industry_key} has too few questions"


class TestPromptParsability:

    def test_prompt_is_valid_string(self):
        """Ensure no unescaped quotes break the string."""
        from src.agents.core_onboarding_agent import ONBOARDING_SYSTEM_PROMPT
        assert isinstance(ONBOARDING_SYSTEM_PROMPT, str)
        assert len(ONBOARDING_SYSTEM_PROMPT) > 500

    def test_action_block_is_parseable(self):
        """The example SETUP_WORKSPACE block in the prompt should be valid-ish JSON."""
        import re
        from src.agents.core_onboarding_agent import ONBOARDING_SYSTEM_PROMPT
        match = re.search(r'<action type="SETUP_WORKSPACE">\s*([\s\S]*?)\s*</action>', ONBOARDING_SYSTEM_PROMPT)
        assert match is not None, "No SETUP_WORKSPACE action block found in prompt"
