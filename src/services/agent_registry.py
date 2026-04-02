"""
Canonical Agent Type Registry — exports the full agent type list with metadata
and the MC translation map for spokestack-core alignment.

spokestack-core fetches GET /api/v1/agents/registry at startup to:
1. Know every agent type this runtime supports
2. Translate mc-* and module-*-assistant names to canonical types
"""

from src.api.routes import AgentType
from src.services.model_registry import (
    AGENT_MODEL_RECOMMENDATIONS, INTERNAL_TO_EXTERNAL,
    ClaudeModelTier, CLAUDE_MODELS,
)


# ══════════════════════════════════════════════════════════════
# Agent Metadata
# ══════════════════════════════════════════════════════════════

AGENT_METADATA: dict[str, dict] = {
    # Foundation
    "rfp": {"name": "RFP Writer", "description": "Creates RFP responses and proposals", "category": "content"},
    "brief": {"name": "Brief Writer", "description": "Creates creative and strategic briefs", "category": "content"},
    "content": {"name": "Content Strategist", "description": "Content strategy and document generation", "category": "content"},
    "commercial": {"name": "Commercial Analyst", "description": "Commercial analysis and sales collateral", "category": "content"},
    # Studio
    "presentation": {"name": "Deck Designer", "description": "Presentation and slide deck creation", "category": "studio"},
    "copy": {"name": "Copywriter", "description": "Ad copy, email copy, social copy, scripts", "category": "studio"},
    "image": {"name": "Image Director", "description": "AI image generation and visual direction", "category": "studio"},
    # Video
    "video_script": {"name": "Video Director", "description": "Video script writing", "category": "video"},
    "video_storyboard": {"name": "Storyboard Artist", "description": "Video storyboard creation", "category": "video"},
    "video_production": {"name": "Production Manager", "description": "Video production guidance", "category": "video"},
    "video_editor": {"name": "Video Editor", "description": "Video editing and composition", "category": "video"},
    # Distribution
    "report": {"name": "Report Generator", "description": "Report creation and formatting", "category": "distribution"},
    "approve": {"name": "Approval Router", "description": "Content review and approval routing", "category": "distribution"},
    "brief_update": {"name": "Brief Updater", "description": "Brief version updates", "category": "distribution"},
    # Gateways
    "gateway_whatsapp": {"name": "WhatsApp Gateway", "description": "WhatsApp message handling", "category": "gateway"},
    "gateway_email": {"name": "Email Gateway", "description": "Email message handling", "category": "gateway"},
    "gateway_slack": {"name": "Slack Gateway", "description": "Slack message handling", "category": "gateway"},
    "gateway_sms": {"name": "SMS Gateway", "description": "SMS message handling", "category": "gateway"},
    # Brand
    "brand_voice": {"name": "Brand Voice", "description": "Brand voice and tone development", "category": "brand"},
    "brand_visual": {"name": "Brand Visual", "description": "Visual identity guidelines", "category": "brand"},
    "brand_guidelines": {"name": "Brand Guidelines", "description": "Brand standards management", "category": "brand"},
    # Operations
    "resource": {"name": "Resource Planner", "description": "Resource allocation and capacity planning", "category": "operations"},
    "workflow": {"name": "Workflow Manager", "description": "Workflow orchestration", "category": "operations"},
    "ops_reporting": {"name": "Ops Reporter", "description": "Operations reporting", "category": "operations"},
    # Client
    "crm": {"name": "CRM Assistant", "description": "Client relationship management", "category": "client"},
    "scope": {"name": "Scope Manager", "description": "Scope definition and management", "category": "client"},
    "onboarding": {"name": "Onboarding Agent", "description": "Client onboarding", "category": "client"},
    "instance_onboarding": {"name": "Instance Setup", "description": "Instance/workspace setup", "category": "client"},
    "instance_analytics": {"name": "Instance Analytics", "description": "Instance analytics tracking", "category": "client"},
    "instance_success": {"name": "Success Manager", "description": "Customer success management", "category": "client"},
    # Media
    "media_buying": {"name": "Media Buyer", "description": "Media buying and ad planning", "category": "media"},
    "campaign": {"name": "Campaign Manager", "description": "Campaign management", "category": "media"},
    # Social
    "social_listening": {"name": "Social Listener", "description": "Social media monitoring", "category": "social"},
    "community": {"name": "Community Manager", "description": "Community management", "category": "social"},
    "social_analytics": {"name": "Social Analyst", "description": "Social analytics", "category": "social"},
    "publisher": {"name": "Publisher", "description": "Content publishing across platforms", "category": "social"},
    # Performance
    "brand_performance": {"name": "Brand Performance", "description": "Brand performance analysis", "category": "performance"},
    "campaign_analytics": {"name": "Campaign Analyst", "description": "Campaign analytics", "category": "performance"},
    "competitor": {"name": "Competitor Analyst", "description": "Competitive intelligence", "category": "performance"},
    # Finance
    "invoice": {"name": "Invoice Manager", "description": "Invoice generation and management", "category": "finance"},
    "forecast": {"name": "Forecaster", "description": "Revenue forecasting", "category": "finance"},
    "budget": {"name": "Budget Manager", "description": "Budget management", "category": "finance"},
    # Quality
    "qa": {"name": "QA Agent", "description": "Quality assurance and testing", "category": "quality"},
    "legal": {"name": "Legal Analyst", "description": "Contract analysis and legal review", "category": "quality"},
    # Knowledge
    "knowledge": {"name": "Knowledge Manager", "description": "Knowledge base management", "category": "knowledge"},
    "training": {"name": "Training Designer", "description": "Training content creation", "category": "knowledge"},
    # Specialized
    "influencer": {"name": "Influencer Manager", "description": "Influencer outreach and analytics", "category": "specialized"},
    "pr": {"name": "PR Agent", "description": "Public relations management", "category": "specialized"},
    "events": {"name": "Events Planner", "description": "Event planning and management", "category": "specialized"},
    "localization": {"name": "Localization Agent", "description": "Content localization", "category": "specialized"},
    "accessibility": {"name": "Accessibility Agent", "description": "Accessibility compliance", "category": "specialized"},
    # Meta
    "prompt_helper": {"name": "Prompt Helper", "description": "Helps craft better prompts", "category": "meta"},
    # Core (spokestack-core agents)
    "core_onboarding": {"name": "Onboarding Specialist", "description": "Workspace setup and business discovery", "category": "core"},
    "core_tasks": {"name": "Tasks Agent", "description": "Task management and tracking", "category": "core"},
    "core_projects": {"name": "Projects Agent", "description": "Project planning and management", "category": "core"},
    "core_briefs": {"name": "Briefs Agent", "description": "Brief lifecycle management", "category": "core"},
    "core_orders": {"name": "Orders Agent", "description": "Order, invoicing, and payment management", "category": "core"},
}


# ══════════════════════════════════════════════════════════════
# MC Translation Map — maps every MC/module type spokestack-core
# might send to the canonical type this runtime understands
# ══════════════════════════════════════════════════════════════

MC_TO_CANONICAL_MAP: dict[str, str] = {
    # MC specialist types (from erp_staging_lmtd)
    "mc-general": "workflow",
    "mc-expert": "knowledge",
    "mc-planner": "brief",
    "mc-advisor": "content",
    "mc-reviewer": "qa",
    "mc-scheduler": "resource",
    "mc-analyst": "campaign_analytics",
    "mc-strategist": "content",
    "mc-executor": "workflow",
    "mc-optimizer": "campaign_analytics",
    "mc-educator": "training",
    "mc-communicator": "copy",

    # Module assistant types
    "module-crm-assistant": "crm",
    "module-briefs-assistant": "brief",
    "module-tasks-assistant": "core_tasks",
    "module-projects-assistant": "core_projects",
    "module-orders-assistant": "core_orders",
    "module-analytics-assistant": "campaign_analytics",
    "module-content-studio-assistant": "content",
    "module-social-publishing-assistant": "campaign",
    "module-finance-assistant": "invoice",
    "module-time-leave-assistant": "resource",
    "module-email-assistant": "gateway_email",
    "module-calendar-assistant": "workflow",
    "module-surveys-assistant": "community",
    "module-lms-assistant": "training",
    "module-media-buying-assistant": "media_buying",

    # Onboarding types
    "onboarding-publisher-setup": "onboarding",
    "onboarding-reply-setup": "onboarding",
    "onboarding-channel-setup": "onboarding",
    "onboarding-vertical-config": "onboarding",

    # Legacy MC names (from existing MC_TO_AGENT_BUILDER_MAP)
    "assistant": "workflow",
    "content_strategist": "content",
    "brief_writer": "brief",
    "deck_designer": "presentation",
    "video_director": "video_script",
    "document_writer": "copy",
    "analyst": "campaign_analytics",
    "media_buyer": "media_buying",
    "course_designer": "training",
    "contract_analyzer": "legal",
    "resource_planner": "resource",
}


def resolve_agent_type(requested_type: str) -> str:
    """
    Translate any agent type string to its canonical form.
    Handles mc-*, module-*-assistant, legacy MC names, and pass-through canonical names.
    """
    return MC_TO_CANONICAL_MAP.get(requested_type, requested_type)


def get_default_model(agent_type: str) -> str:
    """Get the default model ID for an agent type."""
    agent_name = f"{agent_type}_agent"
    tier = AGENT_MODEL_RECOMMENDATIONS.get(agent_name, ClaudeModelTier.SONNET)
    return CLAUDE_MODELS[tier]


def build_registry_response() -> dict:
    """Build the full registry response for GET /api/v1/agents/registry."""
    agents = []
    for agent_type in AgentType:
        canonical = agent_type.value
        meta = AGENT_METADATA.get(canonical, {})
        agents.append({
            "type": canonical,
            "name": meta.get("name", canonical.replace("_", " ").title()),
            "description": meta.get("description", ""),
            "category": meta.get("category", "general"),
            "defaultModel": get_default_model(canonical),
        })

    # Add core agents (not in AgentType enum but registered)
    for core_type in ["core_onboarding", "core_tasks", "core_projects", "core_briefs", "core_orders"]:
        meta = AGENT_METADATA.get(core_type, {})
        agents.append({
            "type": core_type,
            "name": meta.get("name", core_type.replace("_", " ").title()),
            "description": meta.get("description", ""),
            "category": "core",
            "defaultModel": get_default_model(core_type),
        })

    return {
        "agents": agents,
        "total": len(agents),
        "mcTranslationMap": MC_TO_CANONICAL_MAP,
    }
