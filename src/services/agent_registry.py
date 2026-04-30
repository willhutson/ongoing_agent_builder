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
    # Canonical routing types (used by MC_TO_CANONICAL_MAP targets)
    "assistant": {"name": "General Assistant", "description": "General-purpose assistant for tasks, questions, and workspace management", "category": "core"},
    "project_manager": {"name": "Project Manager", "description": "Plans and manages projects, timelines, and milestones", "category": "core"},
    "brief_writer": {"name": "Brief Writer", "description": "Creates and manages creative briefs, campaign briefs, and strategic documents", "category": "core"},
    "content_creator": {"name": "Content Creator", "description": "Writes copy, designs presentations, scripts video content", "category": "content"},
    "analyst": {"name": "Analyst", "description": "Analyzes data, generates reports, tracks metrics and KPIs", "category": "analytics"},
    "crm_manager": {"name": "CRM Manager", "description": "Manages client relationships, deals, and contact data", "category": "client"},
    "order_manager": {"name": "Order Manager", "description": "Manages orders, invoices, and financial operations", "category": "operations"},
    # Core agents
    "core_onboarding": {"name": "Onboarding Specialist", "description": "Workspace setup and business discovery", "category": "core"},
    "core_tasks": {"name": "Tasks Agent", "description": "Task management and tracking", "category": "core"},
    "core_projects": {"name": "Projects Agent", "description": "Project planning and management", "category": "core"},
    "core_briefs": {"name": "Briefs Agent", "description": "Brief lifecycle management", "category": "core"},
    "core_orders": {"name": "Orders Agent", "description": "Order, invoicing, and payment management", "category": "core"},
    # PR / Communications
    "media_relations_manager": {"name": "Media Relations Manager", "description": "Journalist contacts, media lists, pitch tracking, coverage monitoring", "category": "pr_comms"},
    "press_release_writer": {"name": "Press Release Writer", "description": "Press release drafting, editing, approval, and distribution", "category": "pr_comms"},
    "crisis_manager": {"name": "Crisis Manager", "description": "Rapid-response crisis communications and stakeholder management", "category": "pr_comms"},
    "client_reporter": {"name": "Client Reporter", "description": "Monthly retainer reports with coverage metrics and AVE", "category": "pr_comms"},
    "influencer_manager": {"name": "Influencer Manager", "description": "Influencer relationships, campaigns, and ROI tracking", "category": "pr_comms"},
    "event_planner": {"name": "Event Planner", "description": "Event planning, guest lists, run of show, vendor management", "category": "pr_comms"},
    # Marketplace modules
    "board_manager": {"name": "Board Manager", "description": "Kanban/sprint board management", "category": "marketplace"},
    "workflow_designer": {"name": "Workflow Designer", "description": "Automated trigger → condition → action workflows", "category": "marketplace"},
    "social_listener": {"name": "Social Listener", "description": "Brand mention monitoring and sentiment analysis", "category": "marketplace"},
    "nps_analyst": {"name": "NPS Analyst", "description": "NPS surveys, scoring, and detractor follow-up", "category": "marketplace"},
    "chat_operator": {"name": "Chat Operator", "description": "Live chat management, routing, canned responses", "category": "marketplace"},
    "portal_manager": {"name": "Portal Manager", "description": "Client portal deliverables and approvals", "category": "marketplace"},
    "delegation_coordinator": {"name": "Delegation Coordinator", "description": "Task delegation, workload balancing, escalation", "category": "marketplace"},
    "access_admin": {"name": "Access Admin", "description": "Role/permission management, audit, compliance", "category": "marketplace"},
    "module_builder": {"name": "Module Builder", "description": "Build, validate, and publish custom modules to the Marketplace", "category": "marketplace"},
    "module_reviewer": {"name": "Module Reviewer", "description": "Automated security and quality review for marketplace submissions", "category": "internal"},
    "workflow_selector": {"name": "Workflow Selector", "description": "AI-driven recipe recommendation for canvas workflows", "category": "operations"},
}


# ══════════════════════════════════════════════════════════════
# MC Translation Map — maps every MC/module type spokestack-core
# might send to the canonical type this runtime understands
# ══════════════════════════════════════════════════════════════

MC_TO_CANONICAL_MAP: dict[str, str] = {
    # MC specialist types → tool-assignment canonical types
    "mc-general": "assistant",
    "mc-expert": "assistant",
    "mc-planner": "project_manager",
    "mc-advisor": "assistant",
    "mc-reviewer": "brief_writer",
    "mc-scheduler": "assistant",
    "mc-analyst": "analyst",
    "mc-strategist": "content_creator",
    "mc-executor": "assistant",
    "mc-optimizer": "analyst",
    "mc-educator": "assistant",
    "mc-communicator": "assistant",

    # Module assistant types
    "module-crm-assistant": "crm_manager",
    "module-briefs-assistant": "brief_writer",
    "module-tasks-assistant": "assistant",
    "module-projects-assistant": "project_manager",
    "module-orders-assistant": "order_manager",
    "module-analytics-assistant": "analyst",
    "module-content-studio-assistant": "content_creator",
    "module-social-publishing-assistant": "assistant",
    "module-finance-assistant": "order_manager",
    "module-time-leave-assistant": "assistant",
    "module-email-assistant": "assistant",
    "module-calendar-assistant": "assistant",
    "module-surveys-assistant": "assistant",
    "module-lms-assistant": "assistant",
    "module-media-buying-assistant": "analyst",

    # Onboarding
    "onboarding": "core_onboarding",
    "onboarding-publisher-setup": "core_onboarding",
    "onboarding-reply-setup": "core_onboarding",
    "onboarding-channel-setup": "core_onboarding",
    "onboarding-vertical-config": "core_onboarding",

    # Legacy MC names (from original MC_TO_AGENT_BUILDER_MAP)
    "assistant": "assistant",
    "content_strategist": "content_creator",
    "brief_writer": "brief_writer",
    "deck_designer": "content_creator",
    "video_director": "content_creator",
    "document_writer": "content_creator",
    "analyst": "analyst",
    "media_buyer": "analyst",
    "course_designer": "assistant",
    "contract_analyzer": "analyst",
    "resource_planner": "project_manager",

    # PR / Communications module assistants
    "module-media-relations-assistant": "media_relations_manager",
    "module-press-releases-assistant": "press_release_writer",
    "module-crisis-comms-assistant": "crisis_manager",
    "module-client-reporting-assistant": "client_reporter",
    "module-influencer-mgmt-assistant": "influencer_manager",
    "module-events-assistant": "event_planner",
    # Marketplace module agents (dedicated types — replaces PR #55 stubs)
    "module-boards-assistant": "board_manager",
    "module-workflows-assistant": "workflow_designer",
    "module-listening-assistant": "social_listener",
    "module-nps-assistant": "nps_analyst",
    "module-spokechat-assistant": "chat_operator",
    "module-client-portal-assistant": "portal_manager",
    "module-delegation-assistant": "delegation_coordinator",
    "module-access-control-assistant": "access_admin",
    "module-builder-assistant": "module_builder",

    # Pass-through canonical types (already in AGENT_TOOLS)
    "project_manager": "project_manager",
    "order_manager": "order_manager",
    "crm_manager": "crm_manager",
    "content_creator": "content_creator",
    "core_onboarding": "core_onboarding",
    "core_tasks": "core_tasks",
    "core_projects": "core_projects",
    "core_briefs": "core_briefs",
    "core_orders": "core_orders",
    "media_relations_manager": "media_relations_manager",
    "press_release_writer": "press_release_writer",
    "crisis_manager": "crisis_manager",
    "client_reporter": "client_reporter",
    "influencer_manager": "influencer_manager",
    "event_planner": "event_planner",
    "board_manager": "board_manager",
    "workflow_designer": "workflow_designer",
    "social_listener": "social_listener",
    "nps_analyst": "nps_analyst",
    "chat_operator": "chat_operator",
    "portal_manager": "portal_manager",
    "delegation_coordinator": "delegation_coordinator",
    "access_admin": "access_admin",
    "module_builder": "module_builder",
    "module_reviewer": "module_reviewer",
    "workflow_selector": "workflow_selector",
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
    from src.tools.agent_tool_assignment import AGENT_TOOLS
    from src.tools.spokestack_crud_tools import TOOLS

    # Build the spec's canonical agent list (tool-assignment types)
    canonical_agents = []
    for agent_type, tool_names in AGENT_TOOLS.items():
        meta = AGENT_METADATA.get(agent_type, {})
        canonical_agents.append({
            "type": agent_type,
            "name": meta.get("name", agent_type.replace("_", " ").title()),
            "description": meta.get("description", ""),
            "category": meta.get("category", "general"),
            "tools": tool_names,
            "defaultModel": get_default_model(agent_type),
        })

    # Full tool registry — every tool with its HTTP definition
    tool_registry = {}
    for name, definition in TOOLS.items():
        entry = {"name": name}
        for key in ("description", "method", "path", "parameters", "fixed_body", "fixed_body_merge", "handler"):
            if key in definition:
                # Normalize key names for JSON consumers
                json_key = "fixedBody" if key == "fixed_body" else (
                    "fixedBodyMerge" if key == "fixed_body_merge" else key
                )
                entry[json_key] = definition[key]
        tool_registry[name] = entry

    # Agent → tool name mapping
    agent_tools = {
        agent_type: list(tool_names)
        for agent_type, tool_names in AGENT_TOOLS.items()
    }

    return {
        "agents": canonical_agents,
        "total": len(canonical_agents),
        "mcTranslationMap": MC_TO_CANONICAL_MAP,
        "toolRegistry": tool_registry,
        "agentTools": agent_tools,
    }
