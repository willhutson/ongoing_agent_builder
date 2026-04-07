"""Tests for Phase 17B: context injection wiring + industry schemas + onboarding."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


# ══════════════════════════════════════════════════════════════
# W1: CoreExecuteRequest fields
# ══════════════════════════════════════════════════════════════

class TestCoreExecuteRequestFields:

    def test_context_entries_defaults_to_empty_list(self):
        from src.api.core_router import CoreExecuteRequest
        req = CoreExecuteRequest(task="hello", org_id="org_1")
        assert req.context_entries == []

    def test_integrations_defaults_to_empty_list(self):
        from src.api.core_router import CoreExecuteRequest
        req = CoreExecuteRequest(task="hello", org_id="org_1")
        assert req.integrations == []

    def test_recent_events_defaults_to_empty_list(self):
        from src.api.core_router import CoreExecuteRequest
        req = CoreExecuteRequest(task="hello", org_id="org_1")
        assert req.recent_events == []

    def test_accepts_populated_context(self):
        from src.api.core_router import CoreExecuteRequest
        req = CoreExecuteRequest(
            task="hello",
            org_id="org_1",
            context_entries=[{"entryType": "PREFERENCE", "key": "tone", "value": "concise"}],
            integrations=[{"provider": "asana", "status": "ACTIVE"}],
            recent_events=[{"entityType": "Task", "action": "created"}],
        )
        assert len(req.context_entries) == 1
        assert len(req.integrations) == 1
        assert len(req.recent_events) == 1

    def test_backwards_compat_no_new_fields(self):
        """Existing callers that don't send new fields should still work."""
        from src.api.core_router import CoreExecuteRequest
        req = CoreExecuteRequest(task="hello", tenant_id="org_1")
        assert req.context_entries == []
        assert req.integrations == []
        assert req.recent_events == []


# ══════════════════════════════════════════════════════════════
# W1: Injector is called (verified via inject_context_into_prompt behavior)
# ══════════════════════════════════════════════════════════════

class TestInjectorWiring:

    def test_empty_context_returns_original_prompt(self):
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are a helpful assistant."
        result = inject_context_into_prompt(prompt, [], integrations=[], events=[])
        assert result == prompt

    def test_populated_context_appends_block(self):
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are a helpful assistant."
        entries = [{"entryType": "PREFERENCE", "key": "tone", "value": "concise"}]
        result = inject_context_into_prompt(prompt, entries, integrations=[], events=[])
        assert "ORGANIZATIONAL CONTEXT" in result
        assert "tone" in result

    def test_integrations_from_request_body(self):
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are an assistant."
        integrations = [{"provider": "asana", "providerLabel": "Asana", "status": "ACTIVE"}]
        result = inject_context_into_prompt(prompt, [], integrations=integrations, events=[])
        assert "Asana" in result

    def test_events_from_request_body(self):
        from src.services.context_injector import inject_context_into_prompt
        prompt = "You are an assistant."
        events = [{"entityType": "Task", "action": "completed", "entityId": "t1"}]
        result = inject_context_into_prompt(prompt, [], integrations=[], events=events)
        assert "Task.completed" in result


# ══════════════════════════════════════════════════════════════
# W2: Industry Schemas
# ══════════════════════════════════════════════════════════════

class TestIndustrySchemas:

    def test_all_7_industries_defined(self):
        from src.services.industry_schemas import INDUSTRY_SCHEMAS
        expected = ["pr_agency", "creative_agency", "saas", "ecommerce", "consulting", "law_firm", "construction"]
        for key in expected:
            assert key in INDUSTRY_SCHEMAS, f"Missing industry: {key}"

    def test_each_schema_has_required_fields(self):
        from src.services.industry_schemas import INDUSTRY_SCHEMAS
        for key, schema in INDUSTRY_SCHEMAS.items():
            assert "display_name" in schema, f"{key} missing display_name"
            assert "context_categories" in schema, f"{key} missing context_categories"
            assert "onboarding_questions" in schema, f"{key} missing onboarding_questions"
            assert "agent_instructions" in schema, f"{key} missing agent_instructions"
            assert len(schema["onboarding_questions"]) >= 3, f"{key} has too few questions"

    def test_detect_industry_pr(self):
        from src.services.industry_schemas import detect_industry
        assert detect_industry("We're a PR agency in Dubai") == "pr_agency"
        assert detect_industry("public relations consultancy") == "pr_agency"
        assert detect_industry("media relations firm") == "pr_agency"

    def test_detect_industry_saas(self):
        from src.services.industry_schemas import detect_industry
        assert detect_industry("We build SaaS products") == "saas"
        assert detect_industry("software platform for HR") == "saas"

    def test_detect_industry_ecommerce(self):
        from src.services.industry_schemas import detect_industry
        assert detect_industry("online retail store") == "ecommerce"
        assert detect_industry("e-commerce marketplace") == "ecommerce"

    def test_detect_industry_law(self):
        from src.services.industry_schemas import detect_industry
        assert detect_industry("corporate law firm") == "law_firm"
        assert detect_industry("legal services provider") == "law_firm"

    def test_detect_industry_construction(self):
        from src.services.industry_schemas import detect_industry
        assert detect_industry("construction company") == "construction"
        assert detect_industry("real estate developer") == "construction"

    def test_detect_industry_default(self):
        from src.services.industry_schemas import detect_industry
        assert detect_industry("some random business") == "consulting"

    def test_get_schema_for_known_industry(self):
        from src.services.industry_schemas import get_schema_for_industry
        schema = get_schema_for_industry("pr_agency")
        assert schema["display_name"] == "PR & Communications Agency"

    def test_get_schema_for_unknown_defaults_to_consulting(self):
        from src.services.industry_schemas import get_schema_for_industry
        schema = get_schema_for_industry("unknown_industry")
        assert schema["display_name"] == "Management / Strategy Consulting"

    def test_get_all_industry_options(self):
        from src.services.industry_schemas import get_all_industry_options
        options = get_all_industry_options()
        assert len(options) == 7
        assert all("key" in o and "display_name" in o for o in options)


# ══════════════════════════════════════════════════════════════
# W3: Onboarding Agent
# ══════════════════════════════════════════════════════════════

class TestOnboardingAgent:

    def test_prompt_mentions_seed_context(self):
        from src.agents.core_onboarding_agent import CoreOnboardingAgent
        agent = CoreOnboardingAgent.__new__(CoreOnboardingAgent)
        assert "SEED_CONTEXT" in agent.system_prompt

    def test_prompt_mentions_industry_keys(self):
        from src.agents.core_onboarding_agent import CoreOnboardingAgent
        agent = CoreOnboardingAgent.__new__(CoreOnboardingAgent)
        assert "pr_agency" in agent.system_prompt
        assert "consulting" in agent.system_prompt

    def test_prompt_has_industry_adaptations(self):
        from src.agents.core_onboarding_agent import CoreOnboardingAgent
        agent = CoreOnboardingAgent.__new__(CoreOnboardingAgent)
        assert "PR & Communications" in agent.system_prompt
        assert "SaaS" in agent.system_prompt
        assert "Law Firm" in agent.system_prompt

    def test_get_onboarding_questions_for_industry(self):
        from src.agents.core_onboarding_agent import get_onboarding_questions_for_industry
        key, questions = get_onboarding_questions_for_industry("We're a PR agency")
        assert key == "pr_agency"
        assert len(questions) >= 3
        assert any("media" in q.lower() or "outlet" in q.lower() for q in questions)

    def test_get_onboarding_questions_default(self):
        from src.agents.core_onboarding_agent import get_onboarding_questions_for_industry
        key, questions = get_onboarding_questions_for_industry("random stuff")
        assert key == "consulting"
        assert len(questions) >= 3
