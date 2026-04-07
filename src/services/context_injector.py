"""
Context Injector — Formats ContextEntry records into system prompt blocks.

Accepts entries directly from spokestack-core (passed in request body).
Filters by type, confidence, and expiry. Prioritizes PREFERENCE > INSIGHT > ENTITY.
Respects MAX_CONTEXT_CHARS to avoid bloating the prompt.
"""

from datetime import datetime, timezone
from typing import Optional


# Maximum characters to inject (~2000 tokens = ~8000 chars, but keep it tight)
MAX_CONTEXT_CHARS = 6000

ENTRY_TYPE_PRIORITY = {
    "PREFERENCE": 0,   # Always first — user preferences must be respected
    "INSIGHT": 1,      # Recent synthesis insights
    "ENTITY": 2,       # Active entities
    "MILESTONE": 3,
    "PATTERN": 4,
}


def format_context_entries(entries: list[dict]) -> str:
    """
    Takes a list of ContextEntry dicts (from spokestack-core API response)
    and formats them into a system prompt injection block.

    Returns empty string if no entries.
    """
    if not entries:
        return ""

    now = datetime.now(timezone.utc)

    # Filter and score entries
    filtered = []
    for entry in entries:
        entry_type = entry.get("entryType", "ENTITY")
        confidence = entry.get("confidence") or 0.0
        expires_at_raw = entry.get("expiresAt")

        # Skip expired entries
        if expires_at_raw:
            try:
                expires_at = datetime.fromisoformat(expires_at_raw.replace("Z", "+00:00"))
                if expires_at < now:
                    continue
            except (ValueError, AttributeError):
                pass

        # PREFERENCE: always include
        if entry_type == "PREFERENCE":
            filtered.append(entry)
            continue

        # INSIGHT: include if from last 30 days
        if entry_type == "INSIGHT":
            created_raw = entry.get("createdAt", "")
            try:
                created_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                age_days = (now - created_at).days
                if age_days <= 30:
                    filtered.append(entry)
            except (ValueError, AttributeError):
                filtered.append(entry)  # include if we can't parse date
            continue

        # ENTITY: include if confidence > 0.5
        if entry_type == "ENTITY" and confidence > 0.5:
            filtered.append(entry)
            continue

    if not filtered:
        return ""

    # Sort by priority, then by confidence descending
    filtered.sort(key=lambda e: (
        ENTRY_TYPE_PRIORITY.get(e.get("entryType", "ENTITY"), 5),
        -(e.get("confidence") or 0.0)
    ))

    lines = []
    total_chars = 0

    for entry in filtered:
        entry_type = entry.get("entryType", "ENTITY")
        key = entry.get("key", "")
        value = entry.get("value")

        # Format value for display
        if isinstance(value, dict):
            if "body" in value:
                value_str = value["body"]
            elif "corrected" in value:
                value_str = f"Prefer '{value['corrected']}' over '{value.get('original', '?')}'"
            else:
                parts = [f"{k}={v}" for k, v in value.items()
                         if k not in ("generatedAt", "sourceEntryCount") and v is not None]
                value_str = ", ".join(parts[:5])
        elif isinstance(value, str):
            value_str = value
        else:
            value_str = str(value) if value is not None else ""

        line = f"[{entry_type}] {key}: {value_str}"

        if total_chars + len(line) > MAX_CONTEXT_CHARS:
            break

        lines.append(line)
        total_chars += len(line)

    if not lines:
        return ""

    return (
        "\n--- ORGANIZATIONAL CONTEXT ---\n"
        + "\n".join(lines)
        + "\n---\n"
    )


def _format_single_integration(provider: str, seeded: dict) -> str:
    """Format a single integration line from provider key + seeded metadata."""
    if provider in ("google_drive", "google"):
        folder_count = int(seeded.get("folderCount", 0) or 0)
        if folder_count > 0:
            return (
                f"Google Drive: {folder_count} folder{'s' if folder_count != 1 else ''} scanned "
                f"(potential clients/projects detected)"
            )
        return "Google Drive: connected (no folders found yet)"

    elif provider == "slack":
        channel_count = int(seeded.get("channelCount", 0) or 0)
        client_ch = int(seeded.get("clientChannels", 0) or 0)
        project_ch = int(seeded.get("projectChannels", 0) or 0)
        team_ch = int(seeded.get("teamChannels", 0) or 0)
        if channel_count > 0:
            detail_parts = []
            if client_ch:
                detail_parts.append(f"{client_ch} client")
            if project_ch:
                detail_parts.append(f"{project_ch} project")
            if team_ch:
                detail_parts.append(f"{team_ch} team")
            detail = ", ".join(detail_parts)
            suffix = f" ({detail} channels)" if detail else ""
            return f"Slack: {channel_count} channels{suffix}"
        return "Slack: connected (channel scan pending)"

    elif provider == "hubspot":
        contact_count = int(seeded.get("contactCount", 0) or 0)
        company_count = int(seeded.get("companyCount", 0) or 0)
        if contact_count > 0 or company_count > 0:
            parts = []
            if contact_count:
                parts.append(f"{contact_count} contact{'s' if contact_count != 1 else ''}")
            if company_count:
                parts.append(f"{company_count} {'companies' if company_count != 1 else 'company'}")
            return f"HubSpot: {', '.join(parts)} imported"
        return "HubSpot: connected (sync pending)"

    elif provider == "gmail":
        return "Gmail: connected (email correspondence available)"

    elif provider == "figma":
        project_count = int(seeded.get("projectCount", 0) or 0)
        if project_count > 0:
            return f"Figma: {project_count} project{'s' if project_count != 1 else ''} detected"
        return "Figma: connected"

    elif provider == "github":
        repo_count = int(seeded.get("repoCount", 0) or 0)
        if repo_count > 0:
            return f"GitHub: {repo_count} {'repositories' if repo_count != 1 else 'repository'} connected"
        return "GitHub: connected"

    elif provider == "quickbooks":
        customer_count = int(seeded.get("customerCount", 0) or 0)
        if customer_count > 0:
            return f"QuickBooks: {customer_count} customer{'s' if customer_count != 1 else ''} imported"
        return "QuickBooks: connected"

    else:
        return f"{provider}: connected"


def format_integrations(integrations: list[dict]) -> str:
    """
    Format connected integrations into a system prompt section.
    Reads seededData metadata from Phase 18A context seeders for rich descriptions.
    Falls back to generic "connected" when seeding data is absent.
    """
    active = [i for i in (integrations or []) if i.get("status", "ACTIVE") == "ACTIVE" or i.get("seededData")]
    if not active:
        return ""

    lines = ["\n## Connected Integrations",
             "This organization has the following external tools connected:"]
    for conn in active:
        provider = conn.get("provider", "unknown")
        seeded = conn.get("seededData") or {}
        line = _format_single_integration(provider, seeded)
        lines.append(f"- {line}")

    lines.append("")
    lines.append(
        "You can use the `list_integrations` tool to check connection details, "
        "and `proxy_integration` tool to read or write data from these services."
    )
    return "\n".join(lines) + "\n"


def format_events(events: list[dict]) -> str:
    """
    Format recent org events into a system prompt section.
    Returns empty string if no events.
    """
    if not events:
        return ""

    lines = ["\n## Recent Activity",
             "The following events happened recently in this organization:"]
    for e in events[:10]:  # Cap at 10 events
        entity_type = e.get("entityType", "")
        action = e.get("action", "")
        entity_id = e.get("entityId", "")
        line = f"- {entity_type}.{action}: {entity_id}"

        metadata = e.get("metadata") or {}
        if "fromStatus" in metadata and "toStatus" in metadata:
            line += f" ({metadata['fromStatus']} → {metadata['toStatus']})"
        elif "title" in metadata:
            line += f" ({metadata['title']})"

        lines.append(line)

    lines.append("")
    lines.append(
        "You can use `list_recent_events` for more detail, or "
        "`subscribe_to_event` to set up automatic notifications for specific event types."
    )
    return "\n".join(lines) + "\n"


def inject_context_into_prompt(
    system_prompt: str,
    context_entries: list[dict],
    integrations: list[dict] = None,
    events: list[dict] = None,
) -> str:
    """
    Appends the formatted context block and integrations to the system prompt.
    Idempotent — if the context block is already present, returns unchanged.
    """
    if "--- ORGANIZATIONAL CONTEXT ---" in system_prompt:
        return system_prompt

    additions = []

    context_block = format_context_entries(context_entries)
    if context_block:
        additions.append(context_block)

    integrations_block = format_integrations(integrations)
    if integrations_block:
        additions.append(integrations_block)

    events_block = format_events(events)
    if events_block:
        additions.append(events_block)

    if not additions:
        return system_prompt

    return system_prompt.rstrip() + "\n\n" + "\n".join(additions)
