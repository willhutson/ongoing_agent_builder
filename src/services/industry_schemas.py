"""
Industry schema registry for SpokeStack onboarding and context routing.

Each schema defines:
  display_name          — human-readable name shown in the UI
  context_categories    — ContextEntry categories this industry uses
  onboarding_questions  — targeted questions the onboarding agent should ask
  agent_instructions    — short paragraph injected into system prompts for this industry
"""

from __future__ import annotations
from typing import TypedDict


class IndustrySchema(TypedDict):
    display_name: str
    context_categories: list[str]
    onboarding_questions: list[str]
    agent_instructions: str


INDUSTRY_SCHEMAS: dict[str, IndustrySchema] = {

    "pr_agency": {
        "display_name": "PR & Communications Agency",
        "context_categories": [
            "journalist", "media_list", "coverage", "client", "pitch",
            "press_release", "crisis_playbook",
        ],
        "onboarding_questions": [
            "What regions do you primarily work in?",
            "Do you have a specialty — tech, luxury, government, consumer, financial?",
            "How many active clients do you typically manage?",
            "Which media outlets matter most to your work?",
            "Do you handle crisis communications, or is it purely proactive PR?",
        ],
        "agent_instructions": (
            "You work for a PR and communications agency. "
            "Journalists, media relationships, and press coverage are central to every workflow. "
            "When drafting pitches, always reference the journalist's beat and recent coverage. "
            "When handling crisis situations, prioritise speed, accuracy, and client approval before sending."
        ),
    },

    "creative_agency": {
        "display_name": "Creative & Digital Agency",
        "context_categories": [
            "client", "campaign", "brief", "brand_guide", "content_calendar",
        ],
        "onboarding_questions": [
            "What services do you lead with — branding, paid media, content, web, all of the above?",
            "How many active client accounts do you run at once?",
            "Do you work with brand guidelines provided by clients, or do you create them?",
            "What's your typical project cycle — retainer, project-based, or mixed?",
        ],
        "agent_instructions": (
            "You work for a creative and digital marketing agency. "
            "Campaign briefs, brand consistency, and client deliverables drive every conversation. "
            "Lead with creative rationale before execution details."
        ),
    },

    "saas": {
        "display_name": "SaaS / Software Company",
        "context_categories": [
            "product", "feature", "user_segment", "competitor", "press_release",
        ],
        "onboarding_questions": [
            "What is your product and who is your primary buyer?",
            "Are you B2B, B2C, or both?",
            "What's your current growth stage — early, growth, or scale?",
            "Who are your main competitors?",
            "Which channels matter most — PLG, sales-led, or community?",
        ],
        "agent_instructions": (
            "You work for a software company. "
            "Product launches, developer relations, and growth marketing are core workflows. "
            "Adapt tone to audience — technical for developers, benefit-led for buyers."
        ),
    },

    "ecommerce": {
        "display_name": "E-Commerce / Retail",
        "context_categories": [
            "product", "promotion", "influencer", "campaign", "customer_segment",
        ],
        "onboarding_questions": [
            "What categories do you sell in?",
            "Do you sell DTC, through marketplaces, or both?",
            "What's your typical promotion cadence — seasonal, always-on, or event-driven?",
            "Do you work with influencers or affiliate partners?",
        ],
        "agent_instructions": (
            "You work for an e-commerce or retail business. "
            "Product listings, promotions, influencer campaigns, and customer communications drive the workflow."
        ),
    },

    "consulting": {
        "display_name": "Management / Strategy Consulting",
        "context_categories": [
            "client", "deliverable", "proposal", "stakeholder",
        ],
        "onboarding_questions": [
            "What industries do your clients come from?",
            "What's your typical engagement size and duration?",
            "Do you produce slide decks, written reports, or both as primary deliverables?",
            "How many active engagements does your team manage at once?",
        ],
        "agent_instructions": (
            "You work for a consulting firm. "
            "Client deliverables, proposals, and stakeholder communications are the core output. "
            "Structure all output with the answer first, supporting evidence second."
        ),
    },

    "law_firm": {
        "display_name": "Law Firm / Legal Services",
        "context_categories": [
            "client", "matter", "document", "stakeholder", "deadline",
        ],
        "onboarding_questions": [
            "What practice areas does your firm cover?",
            "Do you work primarily with corporate clients, individuals, or both?",
            "What types of documents do you draft most often — contracts, briefs, correspondence?",
            "How many active matters does a typical fee earner manage?",
        ],
        "agent_instructions": (
            "You work for a law firm. "
            "Precision and formality are non-negotiable. "
            "Never make definitive legal conclusions — frame outputs as analysis for attorney review. "
            "Flag ambiguity rather than resolve it independently."
        ),
    },

    "construction": {
        "display_name": "Construction / Real Estate Development",
        "context_categories": [
            "project", "vendor", "stakeholder", "timeline", "compliance",
        ],
        "onboarding_questions": [
            "Do you build residential, commercial, or mixed-use projects?",
            "How many active projects does your team run simultaneously?",
            "Who are your primary stakeholders — clients, investors, local authorities?",
            "What's your biggest communication challenge — subcontractor coordination, client reporting, or both?",
        ],
        "agent_instructions": (
            "You work in construction or real estate development. "
            "Project timelines, vendor coordination, and stakeholder reporting are the main workflows."
        ),
    },

}


def get_schema_for_industry(industry: str) -> IndustrySchema:
    """Returns the schema for the given industry key, defaulting to consulting."""
    return INDUSTRY_SCHEMAS.get(industry, INDUSTRY_SCHEMAS["consulting"])


def detect_industry(description: str) -> str:
    """
    Keyword-based industry detection from a free-text description.
    Returns an industry key from INDUSTRY_SCHEMAS.
    """
    desc = description.lower()

    if any(w in desc for w in ["law", "legal", "solicitor", "barrister", "attorney", "counsel"]):
        return "law_firm"
    if any(w in desc for w in ["construction", "building", "real estate", "property", "infrastructure"]):
        return "construction"
    if any(w in desc for w in ["pr agency", "public relations", "media relations", "press release", "communications agency", "comms agency", "journalist", "publicist"]):
        return "pr_agency"
    if any(w in desc for w in ["creative", "digital agency", "advertising", "design agency"]):
        return "creative_agency"
    if any(w in desc for w in ["saas", "software", "product", "app ", " app", "platform", "tech startup"]):
        return "saas"
    if any(w in desc for w in ["ecommerce", "e-commerce", "retail", "shop", "store", "marketplace", "dtc"]):
        return "ecommerce"
    if any(w in desc for w in ["consulting", "strategy", "advisory", "management consultant"]):
        return "consulting"

    return "consulting"  # safe default


def get_all_industry_options() -> list[dict]:
    """Returns a list suitable for presenting industry choices to the user."""
    return [
        {"key": key, "display_name": schema["display_name"]}
        for key, schema in INDUSTRY_SCHEMAS.items()
    ]
