# Agent Registry

Total: 71+ agent classes across 63 files.

## Routing Methods

| Method | Count | Entry Point | Description |
|--------|-------|-------------|-------------|
| Core Router | 22 | `/api/v1/core/execute` | Directly callable via `CORE_AGENT_CLASSES` |
| ERP Integration | 47 | `/api/v1/agent/execute` | LMTD ERP agents via `AgentType` enum |
| Module Registration | Dynamic | `/api/v1/core/modules/register` | Marketplace modules registered at runtime |
| Dynamic Registry | Dynamic | In-memory | Runtime-registered via `DynamicModuleRegistry` |

## Core Router Agents (22)

Registered in `src/api/core_router.py` → `CORE_AGENT_CLASSES`:

| Type | Class | File |
|------|-------|------|
| core_onboarding | CoreOnboardingAgent | core_onboarding_agent.py |
| core_tasks | CoreTasksAgent | core_tasks_agent.py |
| core_projects | CoreProjectsAgent | core_projects_agent.py |
| core_briefs | CoreBriefsAgent | core_briefs_agent.py |
| core_orders | CoreOrdersAgent | core_orders_agent.py |
| media_relations_manager | MediaRelationsAgent | comms_pr_agents.py |
| press_release_writer | PressReleaseAgent | comms_pr_agents.py |
| crisis_manager | CrisisManagerAgent | comms_pr_agents.py |
| client_reporter | ClientReporterAgent | comms_pr_agents.py |
| influencer_manager | InfluencerManagerAgent | comms_pr_agents.py |
| event_planner | EventPlannerAgent | comms_pr_agents.py |
| board_manager | BoardManagerAgent | marketplace_agents.py |
| workflow_designer | WorkflowDesignerAgent | marketplace_agents.py |
| social_listener | SocialListenerAgent | marketplace_agents.py |
| nps_analyst | NpsAnalystAgent | marketplace_agents.py |
| chat_operator | ChatOperatorAgent | marketplace_agents.py |
| portal_manager | PortalManagerAgent | marketplace_agents.py |
| delegation_coordinator | DelegationCoordinatorAgent | marketplace_agents.py |
| access_admin | AccessAdminAgent | marketplace_agents.py |
| module_builder | ModuleBuilderAgent | marketplace_agents.py |
| module_reviewer | ModuleReviewerAgent | review_agents.py |

## ERP Integration Agents (47)

Registered in `src/api/routes.py` → `AgentType` enum. Served via `/api/v1/agent/execute`:

| Category | Agents |
|----------|--------|
| Foundation | rfp, brief, content, commercial |
| Studio | presentation, copy, image |
| Video | video_script, video_storyboard, video_production, video_editor |
| Distribution | report, approve, brief_update |
| Gateways | gateway_whatsapp, gateway_email, gateway_slack, gateway_sms |
| Brand | brand_voice, brand_visual, brand_guidelines |
| Operations | resource, workflow, ops_reporting |
| Client | crm, scope, onboarding, instance_onboarding, instance_analytics, instance_success |
| Media | media_buying, campaign |
| Social | social_listening, community, social_analytics, publisher |
| Performance | brand_performance, campaign_analytics, competitor |
| Finance | invoice, forecast, budget |
| Quality | qa, legal |
| Knowledge | knowledge, training |
| LMS | lms_tutor, lms_content, lms_assessment |
| Specialized | influencer, pr, events, localization, accessibility |
| Meta | prompt_helper |

## MC Translation

spokestack-core sends MC-style agent types (e.g., `mc-general`, `module-crm-assistant`).
These are translated to canonical types via `MC_TO_CANONICAL_MAP` in `src/services/agent_registry.py`.

## Model Tiers

| Tier | Model | Used By |
|------|-------|---------|
| Premium (OPUS) | claude-opus-4 | legal, forecast, budget, knowledge |
| Standard (SONNET) | claude-sonnet-4 | Most agents (default) |
| Economy (HAIKU) | claude-haiku-3.5 | Gateways, approve, brief_update |

Override via `model_tier` parameter in execute request or `FORCE_MODEL_TIER` env var.
