# Agent Ecosystem Directory

> **Built on Claude Agent SDK** - All agents follow the Think → Act → Create paradigm with maximum flexibility for specialization by vertical, region, and language.

## Architecture Principles

### Flexibility First
Every agent can be specialized:
- **By Vertical**: Beauty, Fashion, Food, Tech, Finance, Healthcare, etc.
- **By Region**: UAE, KSA, US, UK, APAC, etc.
- **By Language**: English, Arabic, French, etc.
- **By Client**: Client-specific rules, voice, preferences

### Agent Composition
```python
# Example: Creating a specialized agent
InfluencerAgent(
    vertical="beauty",
    region="uae",
    language="ar",
    client_id="client_123"  # Optional client-specific rules
)
```

### Shared Context
All agents can access:
- Moodboards (inspiration/style reference)
- Brand guidelines (voice, visual, rules)
- Client context (history, preferences)
- Project data (briefs, deliverables, timelines)

---

## Agent Ecosystem Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AGENT ECOSYSTEM                                │
│                     Built on Claude Agent SDK                           │
│                     Think → Act → Create                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FOUNDATION (4)           BRAND (3)              STUDIO (7)             │
│  ├── RFP ✅               ├── Voice              ├── Presentation       │
│  ├── Brief ✅             ├── Visual             ├── Copy (multi-lang)  │
│  ├── Content ✅           └── Guidelines         ├── Image              │
│  └── Commercial ✅                               ├── Video Script       │
│                                                  ├── Video Storyboard   │
│  DISTRIBUTION (4)         OPERATIONS (3)         └── Video Production   │
│  ├── Report               ├── Resource                                  │
│  ├── Approve              ├── Workflow           CLIENT (3)             │
│  ├── Brief Update         └── Reporting          ├── CRM                │
│  └── WhatsApp Gateway                            ├── Scope              │
│                                                  └── Onboarding         │
│  MEDIA (2)                SOCIAL (3)             PERFORMANCE (3)        │
│  ├── Media Buying         ├── Listening          ├── Brand Performance  │
│  └── Campaign             ├── Community          ├── Campaign Analytics │
│                           └── Social Analytics   └── Competitor         │
│                                                                          │
│  FINANCE (3)              QUALITY (2)            KNOWLEDGE (2)          │
│  ├── Invoice              ├── QA                 ├── Knowledge          │
│  ├── Forecast             └── Legal              └── Training           │
│  └── Budget                                                             │
│                                                                          │
│  INFLUENCER (1+)          PR (1)                 EVENTS (1)             │
│  ├── Discovery            ├── Press Release      ├── Planning           │
│  ├── Outreach             ├── Media Outreach     ├── Logistics          │
│  └── Tracking             └── Coverage           └── Attendee           │
│  (specializable by                                                       │
│   vertical/region)        LOCALIZATION (1+)      ACCESSIBILITY (1)      │
│                           └── Multi-market       └── Compliance         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

Total: 43+ agents (expandable by specialization)
```

---

## Layer Details

### Foundation Layer (Built ✅)

Core business operations agents.

| Agent | Status | Tools | Purpose |
|-------|--------|-------|---------|
| **RFP Agent** | ✅ Built | 5 | Analyze RFPs, extract requirements, find case studies, draft proposals |
| **Brief Agent** | ✅ Built | 6 | Parse briefs, find similar work, generate clarifying questions, estimate complexity |
| **Content Agent** | ✅ Built | 7 | Generate documents, proposals, reports from templates with brand guidelines |
| **Commercial Agent** | ✅ Built | 8 | Pricing intelligence, learn from past RFP outcomes, win/loss analysis |

---

### Brand Layer

Manage brand DNA across all creative work.

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Brand Voice Agent** | `get_voice_guidelines`, `analyze_tone`, `suggest_messaging`, `validate_copy` | Tone, messaging, language patterns |
| **Brand Visual Agent** | `get_visual_guidelines`, `analyze_moodboard`, `extract_palette`, `validate_visuals` | Colors, typography, imagery style |
| **Brand Guidelines Agent** | `get_guidelines`, `validate_asset`, `flag_violations`, `suggest_fix` | Master brand rules, do's/don'ts |

---

### Studio Layer (Creative Production)

All agents can consume moodboards as inspiration input.

#### Copy Agents (Multi-Language)
| Agent | Specialization | Tools |
|-------|----------------|-------|
| **Copy Agent (EN)** | English markets | `generate_headline`, `generate_body`, `generate_social`, `generate_email`, `generate_website`, `generate_script`, `apply_brand_voice`, `revision_workflow` |
| **Copy Agent (AR)** | Arabic markets | Same + `ensure_rtl`, `cultural_adaptation`, `arabic_typography` |
| **Copy Agent (FR)** | French markets | Same + `french_localization` |
| *Additional languages as needed* | | |

#### Visual Agents
| Agent | Tools | Purpose |
|-------|-------|---------|
| **Presentation Agent** | `generate_deck`, `generate_slide`, `get_brand_template`, `insert_erp_data`, `apply_moodboard_style` | Decks from briefs, ERP data integration |
| **Image Agent** | `generate_from_prompt`, `generate_from_moodboard`, `upscale`, `style_transfer`, `save_to_dam` | AI image generation |

#### Video Agents (Pipeline)
| Agent | Tools | Purpose |
|-------|-------|---------|
| **Video Script Agent** | `generate_script`, `format_for_animation`, `format_for_live_action`, `apply_brand_voice` | Scripts from briefs |
| **Video Storyboard Agent** | `generate_storyboard`, `generate_shot_list`, `visualize_frame`, `annotate_direction` | Visual frames, shot planning |
| **Video Production Agent** | `generate_video`, `apply_style`, `render`, `add_music`, `track_production` | Final production, animations |

---

### Distribution Layer (WhatsApp Integration)

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Report Agent** | `format_report`, `send_to_am`, `send_to_client`, `schedule_delivery`, `track_opens` | Send dashboards/reports |
| **Approve Agent** | `request_approval`, `parse_response`, `update_status`, `escalate_timeout`, `track_sla` | Request & collect sign-offs |
| **Brief Update Agent** | `notify_team`, `summarize_changes`, `confirm_receipt`, `track_acknowledgment` | Distribute brief updates |
| **WhatsApp Gateway** | `send_message`, `receive_reply`, `manage_session`, `template_compliance`, `rate_limit` | Low-level messaging |

---

### Operations Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Resource Agent** | `get_availability`, `suggest_allocation`, `balance_workload`, `flag_overload`, `forecast_capacity` | Smart allocation |
| **Workflow Agent** | `create_trigger`, `execute_workflow`, `update_status`, `notify_stakeholders` | Automations, triggers |
| **Reporting Agent** | `generate_report`, `analyze_trends`, `alert_anomaly`, `schedule_report` | KPIs, operational insights |

---

### Client Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **CRM Agent** | `get_client_health`, `predict_churn`, `suggest_touchpoint`, `track_satisfaction` | Client health, relationships |
| **Scope Agent** | `detect_scope_creep`, `track_utilization`, `alert_overrun`, `suggest_change_order` | Scope creep, retainers |
| **Onboarding Agent** | `create_checklist`, `track_progress`, `send_reminders`, `assign_tasks` | New client/project setup |

---

### Media & Advertising Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Media Buying Agent** | `create_media_plan`, `optimize_spend`, `track_performance`, `suggest_reallocation`, `budget_pacing` | Plan, buy, optimize media |
| **Campaign Agent** | `create_campaign`, `track_metrics`, `alert_underperform`, `a_b_test`, `generate_report` | Campaign setup & tracking |

---

### Social Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Social Listening Agent** | `monitor_brand`, `analyze_sentiment`, `detect_crisis`, `track_competitors`, `identify_trends` | Monitor mentions, sentiment |
| **Community Agent** | `draft_reply`, `prioritize_mentions`, `escalate_issue`, `track_response_time`, `moderate` | Replies, engagement |
| **Social Analytics Agent** | `generate_social_report`, `benchmark_performance`, `identify_top_content`, `recommend_posting_time` | Performance reporting |

---

### Performance & Analytics Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Brand Performance Agent** | `track_brand_metrics`, `analyze_awareness`, `measure_sentiment_trend`, `benchmark_category` | Brand health tracking |
| **Campaign Analytics Agent** | `aggregate_metrics`, `attribution_analysis`, `roi_calculation`, `cross_channel_report` | Cross-channel performance |
| **Competitor Agent** | `track_competitor`, `analyze_share_of_voice`, `alert_competitor_move`, `benchmark_creative` | Competitive intelligence |

---

### Finance Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Invoice Agent** | `generate_invoice`, `track_payment`, `send_reminder`, `flag_overdue`, `reconcile` | Billing, AR |
| **Forecast Agent** | `forecast_revenue`, `analyze_pipeline`, `model_scenarios`, `track_accuracy` | Revenue/pipeline forecasting |
| **Budget Agent** | `track_spend`, `alert_overrun`, `reallocate_budget`, `variance_analysis` | Project/client budgets |

---

### Quality & Compliance Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **QA Agent** | `review_asset`, `check_brand_compliance`, `flag_issues`, `suggest_fixes`, `track_revisions` | Review workflows, quality |
| **Legal Agent** | `draft_contract`, `check_terms`, `flag_risk`, `track_expiry`, `ensure_compliance` | Contracts, NDAs, compliance |

---

### Knowledge Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Knowledge Agent** | `search_knowledge`, `suggest_reference`, `update_playbook`, `surface_best_practice` | Internal wiki, best practices |
| **Training Agent** | `assign_training`, `track_completion`, `suggest_learning`, `certify_skill` | Onboarding, skill development |

---

### Influencer Layer (Specializable)

**Base Agent + Vertical Specializations**

| Agent | Specialization | Tools |
|-------|----------------|-------|
| **Influencer Agent (Base)** | General | `discover_influencers`, `analyze_audience`, `outreach`, `track_campaign`, `measure_roi` |
| **Influencer Agent (Beauty)** | Beauty vertical | Base + `beauty_category_match`, `ingredient_expertise`, `beauty_trend_analysis` |
| **Influencer Agent (Fashion)** | Fashion vertical | Base + `style_match`, `fashion_week_tracking`, `trend_forecasting` |
| **Influencer Agent (Food)** | Food & Beverage | Base + `cuisine_expertise`, `restaurant_partnerships`, `recipe_content` |
| **Influencer Agent (Tech)** | Technology | Base + `tech_expertise_match`, `product_review_history`, `tech_audience_analysis` |
| **Influencer Agent (Lifestyle)** | Lifestyle | Base + `lifestyle_category_match`, `family_friendly_check`, `values_alignment` |

**Regional Specializations:**
- UAE, KSA, Kuwait, Qatar, Bahrain, Oman (GCC)
- US, UK, EU markets
- APAC markets

---

### PR Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **PR Agent** | `draft_press_release`, `media_outreach`, `track_coverage`, `analyze_sentiment`, `crisis_response`, `media_list_management` | Press releases, media relations, coverage tracking |

---

### Events Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Events Agent** | `create_event_plan`, `manage_logistics`, `track_registrations`, `send_invites`, `manage_vendors`, `post_event_report` | Event planning, logistics, attendee management |

---

### Localization Layer (Multi-Market)

| Agent | Specialization | Tools |
|-------|----------------|-------|
| **Localization Agent** | Multi-market adaptation | `adapt_content`, `cultural_check`, `legal_compliance_check`, `local_regulations`, `currency_conversion`, `date_format` |

**Market Specializations:**
- GCC (UAE, KSA, etc.)
- Levant (Lebanon, Jordan, etc.)
- North Africa
- Western markets
- Asian markets

---

### Accessibility Layer

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Accessibility Agent** | `wcag_audit`, `generate_alt_text`, `caption_video`, `color_contrast_check`, `screen_reader_test`, `accessibility_report` | WCAG compliance, inclusive design |

---

## Shared Tools (Cross-Agent)

These tools are available to multiple agents:

| Tool | Available To | Purpose |
|------|--------------|---------|
| `get_moodboard` | All Studio agents | Fetch moodboard as inspiration |
| `analyze_moodboard` | All Studio agents | Extract style from moodboard |
| `get_brand_guidelines` | All agents | Fetch brand rules |
| `get_brand_voice` | Copy, Content, PR agents | Fetch voice/tone guidelines |
| `save_to_dam` | All producing agents | Store assets |
| `get_from_dam` | All agents | Retrieve assets |
| `get_client_context` | Many agents | Client history/preferences |
| `get_project_data` | Many agents | Project details from ERP |
| `send_notification` | All agents | Trigger notifications |
| `log_activity` | All agents | Audit trail |

---

## Agent Summary

| Layer | Agents | Status |
|-------|--------|--------|
| Foundation | 4 | ✅ Built |
| Brand | 3 | Planned |
| Studio | 7+ | Planned |
| Distribution | 4 | Planned |
| Operations | 3 | Planned |
| Client | 3 | Planned |
| Media | 2 | Planned |
| Social | 3 | Planned |
| Performance | 3 | Planned |
| Finance | 3 | Planned |
| Quality | 2 | Planned |
| Knowledge | 2 | Planned |
| Influencer | 1+ (specializable) | Planned |
| PR | 1 | Planned |
| Events | 1 | Planned |
| Localization | 1+ (specializable) | Planned |
| Accessibility | 1 | Planned |
| **TOTAL** | **43+ base** | 4 built |

*Note: With vertical, regional, and language specializations, the total can expand to 100+ specialized agent configurations.*

---

## Implementation Priority

### Phase 1: Foundation ✅
- RFP, Brief, Content, Commercial

### Phase 2: Studio Core
- Presentation, Copy (EN/AR), Image

### Phase 3: Distribution
- Report, Approve, Brief Update, WhatsApp Gateway

### Phase 4: Video Pipeline
- Video Script, Storyboard, Production

### Phase 5: Social & Media
- Listening, Community, Media Buying, Campaign

### Phase 6: Operations & Client
- Resource, Workflow, CRM, Scope

### Phase 7: Performance & Finance
- Brand Performance, Analytics, Invoice, Budget

### Phase 8: Specialized
- Influencer (by vertical), PR, Events, Localization, Accessibility

---

## Claude Agent SDK Integration

All agents are built on the Claude Agent SDK following this pattern:

```python
from anthropic import AsyncAnthropic
from src.agents.base import BaseAgent, AgentContext

class SpecializedAgent(BaseAgent):
    """
    Specialized agent with vertical/region/language support.
    """

    def __init__(
        self,
        client: AsyncAnthropic,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        # Specialization options
        vertical: str = None,      # e.g., "beauty", "fashion", "food"
        region: str = None,        # e.g., "uae", "ksa", "us"
        language: str = "en",      # e.g., "en", "ar", "fr"
        client_id: str = None,     # For client-specific rules
    ):
        self.vertical = vertical
        self.region = region
        self.language = language
        self.client_specific_id = client_id
        super().__init__(client, model)

    @property
    def system_prompt(self) -> str:
        base_prompt = "You are an expert..."

        # Add specialization context
        if self.vertical:
            base_prompt += f"\n\nVertical expertise: {self.vertical}"
        if self.region:
            base_prompt += f"\n\nRegional focus: {self.region}"
        if self.language != "en":
            base_prompt += f"\n\nPrimary language: {self.language}"

        return base_prompt
```

---

## ERP Module Mapping

| ERP Module | Primary Agents |
|------------|----------------|
| `rfp` | RFP, Commercial |
| `briefs` | Brief |
| `content` | Content, Copy |
| `studio` | Presentation, Video, Image |
| `dam` | All producing agents |
| `crm` | CRM, RFP, Brief, Commercial |
| `resources` | Resource |
| `reporting` | Reporting, Analytics |
| `workflows` | Workflow |
| `whatsapp` | Distribution agents |
| `integrations` | Media, Social agents |
| `settings` | Brand, Commercial |
| `nps` | CRM, Brand Performance |
| `complaints` | CRM, Community |
| `scope-changes` | Scope |
| `retainer` | Scope, Commercial |
| `time-tracking` | Resource |
| `delegation` | Resource, Workflow |
| `dashboard` | Reporting |
| `notifications` | All agents |
| `forms` | Onboarding |
| `onboarding` | Onboarding |
| `leave` | Resource |
| `files` | DAM tools |
| `chat` | Community |
| `content-engine` | Studio agents |
| `ai` | All agents (meta) |
| `builder` | Studio agents |
