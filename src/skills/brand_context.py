"""
Shared brand knowledge formatter for all agents.

Formats a client's brand knowledge into a system-prompt-friendly block
that any agent can read. Used by brief, copy, image, video_script,
and video_storyboard agents.
"""


def format_brand_knowledge(client: dict) -> str:
    """
    Format a client's brand knowledge into a system-prompt-friendly block.

    Input shape:
    {
      "name": "Visit Dubai",
      "code": "DET-VD",
      "industry": "Tourism / Government",
      "brand_guidelines": "Premium, warm, UAE-specific...",
      "tone_of_voice": "Conversational but elevated...",
      "visual_references": ["url1", "url2"],
      "content_rules": [
        {"rule": "Never mention competitors"},
        {"rule": "Always use #VisitDubai"}
      ]
    }

    Returns a markdown block injectable into any agent prompt.
    Returns empty string when nothing is populated.
    """
    if not client:
        return ""

    name = client.get("name", "")
    code = client.get("code", "")
    industry = client.get("industry", "")
    brand_guidelines = client.get("brand_guidelines", "")
    tone_of_voice = client.get("tone_of_voice", "")
    visual_references = client.get("visual_references", [])
    content_rules = client.get("content_rules", [])

    # Check if there's anything to show
    has_content = any([brand_guidelines, tone_of_voice, visual_references, content_rules])
    if not has_content:
        return ""

    sections = []

    # Header
    header_parts = [name]
    if code:
        header_parts.append(f"({code})")
    if industry:
        header_parts.append(f"— {industry}")
    sections.append(f"=== CLIENT BRAND CONTEXT ===\nClient: {' '.join(header_parts)}")

    # Brand guidelines
    if brand_guidelines:
        sections.append(f"Brand Guidelines:\n{brand_guidelines}")

    # Tone of voice
    if tone_of_voice:
        sections.append(f"Tone of Voice:\n{tone_of_voice}")

    # Visual references
    if visual_references:
        refs = "\n".join(f"- {ref}" for ref in visual_references)
        sections.append(f"Visual References:\n{refs}")

    # Content rules
    if content_rules:
        rules = "\n".join(
            f"{i+1}. {r['rule'] if isinstance(r, dict) else r}"
            for i, r in enumerate(content_rules)
        )
        sections.append(f"Content Rules (DO NOT VIOLATE):\n{rules}")

    sections.append("=== END BRAND CONTEXT ===")

    return "\n\n".join(sections)
