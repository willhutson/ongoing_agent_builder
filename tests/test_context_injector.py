"""Tests for context injection into agent system prompts."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.context_injector import format_context_entries, inject_context_into_prompt


def test_empty_entries_returns_empty():
    assert format_context_entries([]) == ""


def test_none_entries_returns_empty():
    assert format_context_entries(None) == ""


def test_preference_entries_always_included():
    entries = [{"entryType": "PREFERENCE", "key": "tone", "value": "concise", "confidence": 0.9}]
    result = format_context_entries(entries)
    assert "[PREFERENCE]" in result
    assert "tone" in result


def test_preference_with_zero_confidence_still_included():
    entries = [{"entryType": "PREFERENCE", "key": "format", "value": "bullet points", "confidence": 0.0}]
    result = format_context_entries(entries)
    assert "[PREFERENCE]" in result


def test_entity_below_confidence_threshold_excluded():
    entries = [{"entryType": "ENTITY", "key": "project.x", "value": {"name": "X"}, "confidence": 0.3}]
    result = format_context_entries(entries)
    assert result == ""


def test_entity_above_threshold_included():
    entries = [{"entryType": "ENTITY", "key": "project.x", "value": {"name": "X"}, "confidence": 0.8}]
    result = format_context_entries(entries)
    assert "[ENTITY]" in result


def test_entity_at_threshold_excluded():
    """confidence must be > 0.5, not >= 0.5"""
    entries = [{"entryType": "ENTITY", "key": "project.x", "value": {"name": "X"}, "confidence": 0.5}]
    result = format_context_entries(entries)
    assert result == ""


def test_insight_recent_included():
    from datetime import datetime, timezone, timedelta
    recent = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
    entries = [{"entryType": "INSIGHT", "key": "weekly_summary", "value": "All projects on track", "createdAt": recent}]
    result = format_context_entries(entries)
    assert "[INSIGHT]" in result


def test_insight_old_excluded():
    from datetime import datetime, timezone, timedelta
    old = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    entries = [{"entryType": "INSIGHT", "key": "old_summary", "value": "Stale data", "createdAt": old}]
    result = format_context_entries(entries)
    assert result == ""


def test_expired_entry_excluded():
    from datetime import datetime, timezone, timedelta
    expired = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    entries = [{"entryType": "PREFERENCE", "key": "temp", "value": "test", "expiresAt": expired}]
    result = format_context_entries(entries)
    assert result == ""


def test_preference_sorted_before_entity():
    entries = [
        {"entryType": "ENTITY", "key": "project.a", "value": {"name": "A"}, "confidence": 0.9},
        {"entryType": "PREFERENCE", "key": "tone", "value": "formal", "confidence": 0.8},
    ]
    result = format_context_entries(entries)
    lines = result.strip().split("\n")
    # Find the content lines (skip header/footer)
    content_lines = [l for l in lines if l.startswith("[")]
    assert content_lines[0].startswith("[PREFERENCE]")
    assert content_lines[1].startswith("[ENTITY]")


def test_dict_value_with_body_field():
    entries = [{"entryType": "PREFERENCE", "key": "style", "value": {"body": "Be concise and direct"}}]
    result = format_context_entries(entries)
    assert "Be concise and direct" in result


def test_dict_value_with_corrected_field():
    entries = [{"entryType": "PREFERENCE", "key": "term", "value": {"corrected": "clients", "original": "customers"}}]
    result = format_context_entries(entries)
    assert "Prefer 'clients' over 'customers'" in result


def test_inject_is_idempotent():
    prompt = "You are an assistant.\n\n--- ORGANIZATIONAL CONTEXT ---\n[PREFERENCE] foo: bar\n---\n"
    entries = [{"entryType": "PREFERENCE", "key": "foo", "value": "bar", "confidence": 0.9}]
    result = inject_context_into_prompt(prompt, entries)
    assert result.count("--- ORGANIZATIONAL CONTEXT ---") == 1


def test_inject_appends_to_prompt():
    prompt = "You are a helpful assistant."
    entries = [{"entryType": "PREFERENCE", "key": "tone", "value": "concise", "confidence": 0.9}]
    result = inject_context_into_prompt(prompt, entries)
    assert result.startswith("You are a helpful assistant.")
    assert "--- ORGANIZATIONAL CONTEXT ---" in result
    assert "[PREFERENCE] tone: concise" in result


def test_inject_with_no_entries_returns_unchanged():
    prompt = "You are a helpful assistant."
    result = inject_context_into_prompt(prompt, [])
    assert result == prompt


def test_max_chars_respected():
    large_entries = [
        {"entryType": "PREFERENCE", "key": f"key_{i}", "value": "x" * 500, "confidence": 0.9}
        for i in range(20)
    ]
    result = format_context_entries(large_entries)
    assert len(result) <= 6200  # MAX_CONTEXT_CHARS + header/footer overhead
