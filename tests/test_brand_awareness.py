"""Tests for brand-aware agents + workflow selector + brand formatter."""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════
# A1: Brand Knowledge Formatter
# ══════════════════════════════════════════════════════════════

class TestBrandFormatter:

    def test_full_context(self):
        from src.skills.brand_context import format_brand_knowledge
        client = load_fixture("visit_dubai_context.json")
        result = format_brand_knowledge(client)
        assert "=== CLIENT BRAND CONTEXT ===" in result
        assert "Visit Dubai" in result
        assert "DET-VD" in result
        assert "Tourism" in result
        assert "Premium, warm" in result
        assert "Conversational but elevated" in result
        assert "#VisitDubai" in result
        assert "=== END BRAND CONTEXT ===" in result

    def test_tone_only(self):
        from src.skills.brand_context import format_brand_knowledge
        client = {"name": "Minimal", "tone_of_voice": "Friendly and casual"}
        result = format_brand_knowledge(client)
        assert "=== CLIENT BRAND CONTEXT ===" in result
        assert "Friendly and casual" in result
        assert "Brand Guidelines:" not in result  # No guidelines set

    def test_empty_client(self):
        from src.skills.brand_context import format_brand_knowledge
        assert format_brand_knowledge({}) == ""
        assert format_brand_knowledge(None) == ""

    def test_no_content(self):
        from src.skills.brand_context import format_brand_knowledge
        client = {"name": "Empty Co", "code": "EC"}
        assert format_brand_knowledge(client) == ""

    def test_content_rules_formatting(self):
        from src.skills.brand_context import format_brand_knowledge
        client = load_fixture("twenty_five_degrees_context.json")
        result = format_brand_knowledge(client)
        assert "1. Never reference investment returns" in result
        assert "DO NOT VIOLATE" in result


# ══════════════════════════════════════════════════════════════
# A2: Brief Agent Brand Awareness
# ══════════════════════════════════════════════════════════════

class TestBriefAgentBrandAwareness:

    def _get_prompt(self):
        with open("src/agents/brief_agent.py") as f:
            content = f.read()
        # Extract system prompt from source
        return content

    def test_prompt_mentions_brand_context(self):
        content = self._get_prompt()
        assert "CLIENT BRAND CONTEXT" in content

    def test_prompt_mentions_critical_gaps(self):
        content = self._get_prompt()
        assert "criticalGaps" in content

    def test_prompt_mentions_brand_rules(self):
        content = self._get_prompt()
        assert "brand rules" in content.lower()


# ══════════════════════════════════════════════════════════════
# A3: Workflow Selector
# ══════════════════════════════════════════════════════════════

class TestWorkflowSelector:

    def test_prompt_mentions_json_output(self):
        with open("src/agents/workflow_selector_agent.py") as f:
            content = f.read()
        assert "recommendedRecipeId" in content
        assert "fallbackToTemplate" in content

    def test_prompt_has_decision_rules(self):
        with open("src/agents/workflow_selector_agent.py") as f:
            content = f.read()
        assert "client-specific" in content
        assert "usageCount" in content

    def test_in_agent_metadata(self):
        from src.services.agent_registry import AGENT_METADATA
        assert "workflow_selector" in AGENT_METADATA

    def test_mc_translation(self):
        from src.services.agent_registry import resolve_agent_type
        assert resolve_agent_type("workflow_selector") == "workflow_selector"


# ══════════════════════════════════════════════════════════════
# A4: Copy Agent Brand Awareness
# ══════════════════════════════════════════════════════════════

class TestCopyAgentBrandAwareness:

    def _read_source(self):
        with open("src/agents/copy_agent.py") as f:
            return f.read()

    def test_prompt_mentions_brand_context(self):
        assert "CLIENT BRAND CONTEXT" in self._read_source()

    def test_prompt_mentions_content_rules(self):
        assert "content rule" in self._read_source().lower()


# ══════════════════════════════════════════════════════════════
# A5: Visual Agents Brand Awareness
# ══════════════════════════════════════════════════════════════

class TestImageAgentBrandAwareness:

    def _read_source(self):
        with open("src/agents/image_agent.py") as f:
            return f.read()

    def test_prompt_mentions_brand_context(self):
        assert "CLIENT BRAND CONTEXT" in self._read_source()

    def test_prompt_mentions_visual_references(self):
        assert "visual references" in self._read_source().lower()


class TestVideoScriptBrandAwareness:

    def test_prompt_mentions_brand_context(self):
        with open("src/agents/video_script_agent.py") as f:
            assert "CLIENT BRAND CONTEXT" in f.read()


class TestStoryboardBrandAwareness:

    def _read_source(self):
        with open("src/agents/video_storyboard_agent.py") as f:
            return f.read()

    def test_prompt_mentions_brand_context(self):
        assert "CLIENT BRAND CONTEXT" in self._read_source()

    def test_prompt_mentions_visual_refs_as_shot_notes(self):
        assert "shot reference" in self._read_source().lower()
