# SpokeStack Agent Training Program Technical Specification

> Complete guide for training teams on the 49+ agent ecosystem, including agent capabilities, training methodologies, ERP integration, engagement suite, extended modules, and ongoing maintenance.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Training Program Structure](#2-training-program-structure)
3. [Agent Ecosystem Deep Dive](#3-agent-ecosystem-deep-dive)
4. [ERP Integration & Onboarding](#4-erp-integration--onboarding)
5. [Agent Training & Customization](#5-agent-training--customization)
6. [Updating & Maintaining Agents](#6-updating--maintaining-agents)
7. [Certification Tracks](#7-certification-tracks)
8. [Hands-On Labs](#8-hands-on-labs)
9. [Assessment & Evaluation](#9-assessment--evaluation)
10. [Resources & Reference Materials](#10-resources--reference-materials)

---

## 1. Overview

### 1.1 Purpose

This training program ensures all stakeholders understand:
- **What** each of the 49+ agents does (including 3 new Engagement Suite agents)
- **How** to configure, train, and customize agents for specific needs
- **How** to onboard agents to new ERP instances
- **How** to configure engagement and extended modules per industry vertical
- **How** to maintain, update, and troubleshoot agents in production

### 1.2 Target Audiences

| Audience | Focus Areas | Certification Track |
|----------|-------------|---------------------|
| **Platform Administrators** | Instance setup, agent configuration, monitoring | Admin Certified |
| **Account Managers** | Agent capabilities, client workflows, reporting | Practitioner Certified |
| **Creative Teams** | Studio agents, content workflows, moodboards | Creative Certified |
| **Media Teams** | Media agents, campaign analytics, platform integrations | Media Certified |
| **Engagement Teams** | Publisher, Reply, Channel agents, omnichannel orchestration | Engagement Certified |
| **Developers** | Agent customization, API integration, tool development | Developer Certified |
| **Customer Success** | Instance lifecycle agents, health monitoring, expansion | Success Certified |

### 1.3 Core Paradigm: Think → Act → Create

Every agent follows this paradigm:

```
┌─────────────────────────────────────────────────────────────────┐
│                    THINK → ACT → CREATE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  THINK                                                          │
│  ├── Analyze the context (brief, client, project)               │
│  ├── Understand requirements and constraints                    │
│  ├── Plan the approach (which tools, what order)                │
│  └── Consider specializations (vertical, region, language)      │
│                                                                 │
│  ACT                                                            │
│  ├── Execute tools (API calls, data queries, validations)       │
│  ├── Iterate based on feedback                                  │
│  ├── Handle errors gracefully                                   │
│  └── Gather all necessary information                           │
│                                                                 │
│  CREATE                                                         │
│  ├── Synthesize thinking + action into deliverables             │
│  ├── Generate documents, assets, recommendations                │
│  ├── Format output appropriately                                │
│  └── Provide actionable next steps                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Training Program Structure

### 2.1 Learning Paths

```
                              ┌─────────────────┐
                              │   FOUNDATION    │
                              │   (Required)    │
                              │    8 hours      │
                              └────────┬────────┘
                                       │
     ┌───────────────┬─────────────────┼─────────────────┬───────────────┐
     │               │                 │                 │               │
     ▼               ▼                 ▼                 ▼               ▼
┌──────────┐  ┌──────────┐      ┌──────────┐      ┌──────────┐  ┌──────────┐
│ CREATIVE │  │  MEDIA   │      │OPERATIONS│      │ENGAGEMENT│  │VERTICALS │
│  TRACK   │  │  TRACK   │      │  TRACK   │      │  TRACK   │  │  TRACK   │
│ 12 hours │  │ 12 hours │      │ 12 hours │      │ 12 hours │  │ 8 hours  │
└──────────┘  └──────────┘      └──────────┘      └──────────┘  └──────────┘
     │               │                 │                 │               │
     └───────────────┴─────────────────┼─────────────────┴───────────────┘
                                       │
                              ┌────────▼────────┐
                              │   ADVANCED      │
                              │ SPECIALIZATION  │
                              │   16 hours      │
                              └─────────────────┘
```

### 2.2 Module Breakdown

#### Foundation (Required - 8 hours)

| Module | Duration | Topics |
|--------|----------|--------|
| F1: Platform Overview | 2 hrs | Architecture, multi-tenancy, agent service |
| F2: Agent Fundamentals | 2 hrs | Think→Act→Create, tool execution, specialization |
| F3: ERP Integration | 2 hrs | Modules, data flow, API structure |
| F4: Basic Operations | 2 hrs | Invoking agents, monitoring, troubleshooting |

#### Creative Track (12 hours)

| Module | Duration | Agents Covered |
|--------|----------|----------------|
| C1: Studio Agents | 3 hrs | Presentation, Copy, Image |
| C2: Video Pipeline | 3 hrs | Video Script, Storyboard, Production |
| C3: Brand Agents | 3 hrs | Voice, Visual, Guidelines |
| C4: Moodboard Integration | 3 hrs | Creative input flows, style extraction |

#### Media Track (12 hours)

| Module | Duration | Agents Covered |
|--------|----------|----------------|
| M1: Media Operations | 3 hrs | Media Buying, Campaign |
| M2: Social Suite | 3 hrs | Listening, Community, Social Analytics |
| M3: Performance Analytics | 3 hrs | Brand Performance, Campaign Analytics, Competitor |
| M4: Platform Integrations | 3 hrs | Google Ads, Meta, TikTok, LinkedIn connections |

#### Operations Track (12 hours)

| Module | Duration | Agents Covered |
|--------|----------|----------------|
| O1: Foundation Agents | 3 hrs | RFP, Brief, Content, Commercial |
| O2: Distribution & Gateways | 3 hrs | Report, Approve, WhatsApp, Email, Slack, SMS |
| O3: Resource Management | 3 hrs | Resource, Workflow, Ops Reporting |
| O4: Client Management | 3 hrs | CRM, Scope, Onboarding |

#### Engagement Track (12 hours) - NEW

| Module | Duration | Agents Covered |
|--------|----------|----------------|
| E1: Publisher Agent | 3 hrs | Publisher, Content Calendar integration, multi-platform preview |
| E2: Reply Agent | 3 hrs | Reply, unified inbox, crisis escalation, auto-responder |
| E3: Channel Agent | 3 hrs | Channel, omnichannel orchestration, flow design, real-time sync |
| E4: Integration Workflows | 3 hrs | Studio→Publisher Queue, Reply escalation, Channel automation |

#### Verticals Track (8 hours) - NEW

| Module | Duration | Topics |
|--------|----------|--------|
| V1: Module Tier Architecture | 2 hrs | Tier 1-5 hierarchy, configurable primitives |
| V2: Engagement Module Assignment | 3 hrs | Per-vertical engagement configurations (15 verticals) |
| V3: Extended Module Configuration | 3 hrs | Entities, Scheduler, Deadlines, Inventory, Contracts, Tickets, Vault |

#### Advanced Specialization (16 hours)

| Module | Duration | Topics |
|--------|----------|--------|
| A1: Instance Lifecycle | 4 hrs | Instance Onboarding, Analytics, Success agents |
| A2: Agent Customization | 4 hrs | System prompts, tools, specializations |
| A3: Integration Development | 4 hrs | Custom tools, API extensions, webhooks |
| A4: Scaling & Performance | 4 hrs | Multi-tenant optimization, monitoring, alerting |

---

## 3. Agent Ecosystem Deep Dive

### 3.1 Agent Categories

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        49+ AGENTS BY CATEGORY                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  BUSINESS OPERATIONS (15)                                               │
│  ├── Foundation: RFP, Brief, Content, Commercial                        │
│  ├── Client: CRM, Scope, Onboarding                                     │
│  ├── Finance: Invoice, Forecast, Budget                                 │
│  └── Operations: Resource, Workflow, Ops Reporting, Quality (QA, Legal) │
│                                                                         │
│  CREATIVE & PRODUCTION (10)                                             │
│  ├── Studio: Presentation, Copy, Image                                  │
│  ├── Video: Script, Storyboard, Production                              │
│  └── Brand: Voice, Visual, Guidelines                                   │
│                                                                         │
│  MARKETING & MEDIA (8)                                                  │
│  ├── Media: Media Buying, Campaign                                      │
│  ├── Social: Listening, Community, Social Analytics                     │
│  └── Performance: Brand Performance, Campaign Analytics, Competitor     │
│                                                                         │
│  DISTRIBUTION & ENGAGEMENT (10) - EXPANDED                              │
│  ├── Core: Report, Approve, Brief Update                                │
│  ├── Gateways: WhatsApp, Email, Slack, SMS                              │
│  └── Engagement Suite (NEW): Publisher, Reply, Channel                  │
│                                                                         │
│  PLATFORM & LIFECYCLE (6)                                               │
│  ├── Instance: Onboarding, Analytics, Success                           │
│  └── Knowledge: Knowledge, Training                                     │
│                                                                         │
│  SPECIALIZED (5)                                                        │
│  └── Influencer, PR, Events, Localization, Accessibility                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.1.1 Module Tier Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MODULE TIER ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TIER 1: FOUNDATION (Always Present)                                    │
│  └── Hub, Team, Clients, Admin, Superadmin                              │
│                                                                         │
│  TIER 2: CORE OPERATIONS                                                │
│  ├── Briefs, Projects, Boards, Workflows                                │
│  ├── Time, Resources, Leave                                             │
│  └── Finance, CRM, RFP, Chat                                            │
│                                                                         │
│  TIER 3: SPECIALIZED SUITES                                             │
│  ├── SpokeStudio (Docs, Video, Decks, Moodboards, Calendar, AI Skills)  │
│  ├── Marketing (Analytics, Listening, Media Buying)                     │
│  ├── Learning (LMS, Course Builder, Knowledge Base)                     │
│  └── Feedback (Surveys, Quizzes & Polls, NPS)                           │
│                                                                         │
│  TIER 4: EXTENDED MODULES (Configurable per Vertical)                   │
│  └── Entities, Scheduler, Deadlines, Inventory, Contracts, Tickets, Vault│
│                                                                         │
│  TIER 5: ENGAGEMENT SUITE (NEW)                                         │
│  └── Publisher, Reply, Channel                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.1.2 Extended Modules Reference

| Module | Purpose | Key Verticals |
|--------|---------|---------------|
| **Entities** | Universal party management (candidates, vendors, guests) | Recruitment, Events, Training |
| **Scheduler** | Appointment and resource booking | Consulting, Legal, Training |
| **Deadlines** | Compliance and deadline tracking | Legal, Accounting, Architecture |
| **Inventory** | Asset and item management | Events, IT, Architecture |
| **Contracts** | Agreement lifecycle management | All |
| **Tickets** | Service request handling | IT Consulting |
| **Vault** | Secure document management | Legal, Accounting |

### 3.1.3 Industry Vertical Configurations (15 Verticals)

| Vertical | Engagement Modules | Extended Modules |
|----------|-------------------|------------------|
| Marketing Agency | publisher, reply, channel | - |
| PR & Communications | publisher, reply, channel | - |
| Creative Studio | publisher, channel | - |
| Event Management | publisher, reply, channel | entities, scheduler, inventory, contracts, vault |
| Consulting Firm | channel | - |
| Recruitment Agency | channel, reply | entities, scheduler, contracts |
| IT Consulting | reply, channel | tickets, contracts, deadlines, inventory |
| Legal Services | channel | deadlines, contracts, vault, scheduler |
| Accounting Firm | channel | - |
| HR Consulting | channel, reply | - |
| Architecture & Design | channel, publisher | - |
| Engineering Consultancy | channel | - |
| Project Management | channel | - |
| Training & Development | channel, publisher | - |
| Translation Services | channel | - |

### 3.2 Agent Reference Cards

Each agent has a reference card with:

#### Example: RFP Agent

```
┌─────────────────────────────────────────────────────────────┐
│ RFP AGENT                                           [FOUND] │
├─────────────────────────────────────────────────────────────┤
│ PURPOSE: Analyze RFPs, extract requirements, draft proposals│
├─────────────────────────────────────────────────────────────┤
│ TOOLS (5):                                                  │
│ ├── analyze_rfp: Parse RFP documents                        │
│ ├── extract_requirements: Pull key requirements             │
│ ├── find_case_studies: Match relevant past work             │
│ ├── draft_proposal: Generate proposal sections              │
│ └── estimate_effort: Calculate resource needs               │
├─────────────────────────────────────────────────────────────┤
│ SPECIALIZATIONS:                                            │
│ ├── Vertical: Tech, Finance, Healthcare, Retail, etc.       │
│ ├── Region: GCC, MENA, EU, US, APAC                         │
│ └── Language: EN, AR, FR, etc.                              │
├─────────────────────────────────────────────────────────────┤
│ ERP MODULES: rfp, briefs, crm                               │
├─────────────────────────────────────────────────────────────┤
│ TYPICAL WORKFLOW:                                           │
│ 1. Receive RFP document                                     │
│ 2. Analyze and extract requirements                         │
│ 3. Find matching case studies from DAM                      │
│ 4. Draft proposal sections                                  │
│ 5. Estimate effort and resources                            │
│ 6. Route to Commercial Agent for pricing                    │
└─────────────────────────────────────────────────────────────┘
```

#### Publisher Agent (NEW - Engagement Suite)

```
┌─────────────────────────────────────────────────────────────┐
│ PUBLISHER AGENT                                    [ENGAGE] │
├─────────────────────────────────────────────────────────────┤
│ PURPOSE: Content distribution, multi-platform preview,      │
│          scheduling, and publishing queue management        │
├─────────────────────────────────────────────────────────────┤
│ TOOLS (8):                                                  │
│ ├── preview_content: Multi-platform preview rendering       │
│ ├── schedule_post: Add content to publishing queue          │
│ ├── manage_queue: View/edit/reorder publishing queue        │
│ ├── publish_now: Immediate multi-platform publishing        │
│ ├── get_optimal_times: AI-suggested posting times           │
│ ├── format_for_platform: Adapt content per platform specs   │
│ ├── sync_calendar: Integrate with SpokeStudio Calendar      │
│ └── validate_content: Pre-publish compliance checks         │
├─────────────────────────────────────────────────────────────┤
│ PREVIEW MODES:                                              │
│ ├── Website, Instagram, X/Twitter, Facebook                 │
│ ├── LinkedIn, TikTok, Email                                 │
│ └── WYSIWYG publishing hub with multi-platform view         │
├─────────────────────────────────────────────────────────────┤
│ ROUTES:                                                     │
│ └── /publisher, /publisher/create, /publisher/drafts,       │
│     /publisher/scheduled, /publisher/preview                │
├─────────────────────────────────────────────────────────────┤
│ ERP MODULES: publisher, studio, content-calendar            │
├─────────────────────────────────────────────────────────────┤
│ TYPICAL WORKFLOW:                                           │
│ 1. Receive content from SpokeStudio                         │
│ 2. Preview across target platforms                          │
│ 3. Format and optimize per platform requirements            │
│ 4. Add to publishing queue with optimal timing              │
│ 5. Execute scheduled publishing                             │
│ 6. Route to Reply Agent for engagement monitoring           │
└─────────────────────────────────────────────────────────────┘
```

#### Reply Agent (NEW - Engagement Suite)

```
┌─────────────────────────────────────────────────────────────┐
│ REPLY AGENT                                        [ENGAGE] │
├─────────────────────────────────────────────────────────────┤
│ PURPOSE: Unified inbox management, customer service, crisis │
│          escalation, FAQ management, auto-response          │
├─────────────────────────────────────────────────────────────┤
│ TOOLS (10):                                                 │
│ ├── unify_inbox: Consolidate messages across channels       │
│ ├── analyze_sentiment: Real-time sentiment analysis         │
│ ├── suggest_response: AI-powered response suggestions       │
│ ├── manage_faq: Create/update FAQ knowledge base            │
│ ├── configure_autoresponder: Set auto-response triggers     │
│ ├── escalate_crisis: Initiate crisis protocol               │
│ ├── route_to_team: Assign to appropriate team member        │
│ ├── trigger_delight: Activate surprise & delight actions    │
│ ├── log_interaction: Record customer touchpoints            │
│ └── generate_csat: Request customer satisfaction feedback   │
├─────────────────────────────────────────────────────────────┤
│ INBOX SOURCES:                                              │
│ └── Social, Email, Website, Messaging, Reviews              │
├─────────────────────────────────────────────────────────────┤
│ AUTO-RESPONDER TRIGGERS:                                    │
│ ├── Time-based (off-hours, holidays)                        │
│ ├── Keyword-based (FAQ matching)                            │
│ ├── Sentiment-based (negative/positive detection)           │
│ └── Customer type (VIP, new, at-risk)                       │
├─────────────────────────────────────────────────────────────┤
│ CRISIS ESCALATION (4 Severity Levels):                      │
│ ├── Level 1: Auto-respond, log, monitor                     │
│ ├── Level 2: Escalate to team lead                          │
│ ├── Level 3: Alert management + PR team                     │
│ └── Level 4: Executive notification + crisis protocol       │
├─────────────────────────────────────────────────────────────┤
│ ROUTES:                                                     │
│ └── /reply, /reply/inbox, /reply/assigned, /reply/faq,      │
│     /reply/auto, /reply/escalation                          │
├─────────────────────────────────────────────────────────────┤
│ ERP MODULES: reply, crm, notifications, chat                │
├─────────────────────────────────────────────────────────────┤
│ TYPICAL WORKFLOW:                                           │
│ 1. Receive message from unified inbox                       │
│ 2. Analyze sentiment and context                            │
│ 3. Check FAQ for matching response                          │
│ 4. If crisis detected, initiate escalation protocol         │
│ 5. Generate response suggestion                             │
│ 6. Route to Channel Agent for delivery                      │
└─────────────────────────────────────────────────────────────┘
```

#### Channel Agent (NEW - Engagement Suite)

```
┌─────────────────────────────────────────────────────────────┐
│ CHANNEL AGENT                                      [ENGAGE] │
├─────────────────────────────────────────────────────────────┤
│ PURPOSE: Omnichannel orchestration, visual flow design,     │
│          natural language automation, real-time sync        │
├─────────────────────────────────────────────────────────────┤
│ TOOLS (12):                                                 │
│ ├── design_flow: Visual drag-and-drop flow creation         │
│ ├── parse_nl_flow: Natural language flow interpretation     │
│ ├── connect_platform: OAuth platform connections            │
│ ├── sync_channels: Real-time cross-platform sync            │
│ ├── route_message: Intelligent message routing              │
│ ├── configure_webhook: Inbound/outbound webhooks            │
│ ├── manage_queue: Channel-specific queue management         │
│ ├── reply_anywhere: Slack/Email/WhatsApp/SMS response       │
│ ├── track_conversation: Cross-channel thread tracking       │
│ ├── analyze_channel: Per-channel performance metrics        │
│ ├── set_triggers: Automation trigger configuration          │
│ └── handoff_human: Seamless bot-to-human handoff            │
├─────────────────────────────────────────────────────────────┤
│ NATURAL LANGUAGE FLOW EXAMPLES:                             │
│ ├── "After client approves, send to publish for CM"         │
│ ├── "When sentiment negative, escalate to team lead"        │
│ └── "If VIP customer, priority route to account manager"    │
├─────────────────────────────────────────────────────────────┤
│ CONNECTED PLATFORMS:                                        │
│ ├── Messaging: WhatsApp, SMS, Slack, Teams                  │
│ ├── Social: Instagram, X/Twitter, Facebook, LinkedIn        │
│ ├── Email: Gmail, Outlook, custom SMTP                      │
│ └── Website: Live chat, contact forms, chatbots             │
├─────────────────────────────────────────────────────────────┤
│ ROUTES:                                                     │
│ └── /channel, /channel/inbox, /channel/connections,         │
│     /channel/flows                                          │
├─────────────────────────────────────────────────────────────┤
│ ERP MODULES: channel, integrations, workflows, chat         │
├─────────────────────────────────────────────────────────────┤
│ TYPICAL WORKFLOW:                                           │
│ 1. Receive natural language flow description                │
│ 2. Parse and create visual flow diagram                     │
│ 3. Configure triggers and conditions                        │
│ 4. Connect required platforms via OAuth                     │
│ 5. Activate automation with real-time sync                  │
│ 6. Monitor and optimize based on analytics                  │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Agent Interaction Patterns

```
                    CLIENT REQUEST
                          │
                          ▼
                   ┌──────────────┐
                   │ Brief Agent  │
                   └──────┬───────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │ Copy Agent │  │Image Agent │  │Video Agent │
   └──────┬─────┘  └─────┬──────┘  └─────┬──────┘
          │              │               │
          └──────────────┼───────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ QA Agent    │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │Approve Agent│
                  └──────┬──────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
   ┌───────────┐  ┌───────────┐  ┌───────────┐
   │  Email    │  │ WhatsApp  │  │  Slack    │
   │  Gateway  │  │  Gateway  │  │  Gateway  │
   └───────────┘  └───────────┘  └───────────┘
                         │
                         ▼
                   CLIENT DELIVERY
```

### 3.4 Engagement Suite Interaction Patterns (NEW)

#### Content Calendar → Publisher Queue → Publish Flow

```
                    SPOKESTUDIO
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │    Docs    │  │   Video    │  │   Decks    │
   └──────┬─────┘  └─────┬──────┘  └─────┬──────┘
          │              │               │
          └──────────────┼───────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  Content    │
                  │  Calendar   │
                  └──────┬──────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │  Drafts   │  │ Scheduled │  │  Queue    │
    └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
          │              │              │
          └──────────────┼──────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  PUBLISHER  │
                  │    AGENT    │
                  └──────┬──────┘
                         │
     ┌───────────────────┼───────────────────┐
     │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Website │ │  IG    │ │X/Twitter│ │LinkedIn│ │TikTok │
│Preview │ │Preview │ │ Preview │ │Preview │ │Preview│
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
                         │
                         ▼
               MULTI-PLATFORM PUBLISH
```

#### Reply Escalation Flow

```
                    INCOMING MESSAGE
                          │
                          ▼
                   ┌──────────────┐
                   │ Unified Inbox │
                   │ (All Sources) │
                   └───────┬──────┘
                           │
                           ▼
                   ┌──────────────┐
                   │    REPLY     │
                   │    AGENT     │
                   └───────┬──────┘
                           │
                           ▼
                   ┌──────────────┐
                   │  Sentiment   │
                   │  Analysis    │
                   └───────┬──────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
  [POSITIVE]          [NEUTRAL]          [NEGATIVE]
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Surprise & │    │  Standard   │    │   Crisis    │
│   Delight   │    │  Response   │    │  Protocol   │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        │                    │                    │
                        ▼                    ▼                    ▼
                  ┌──────────┐        ┌──────────┐        ┌──────────┐
                  │ Level 1  │        │ Level 2  │        │ Level 3-4│
                  │ Auto-Log │        │Team Lead │        │ Exec +   │
                  │ Monitor  │        │ Escalate │        │ PR Team  │
                  └──────────┘        └──────────┘        └──────────┘
                                             │
                                             ▼
                                   ┌─────────────────┐
                                   │  LEADERSHIP     │
                                   │    ALERT        │
                                   └─────────────────┘
```

#### Channel Flow: Natural Language → Automation

```
              NATURAL LANGUAGE INPUT
                      │
    "After client approves, send to publish
     for community manager review"
                      │
                      ▼
              ┌──────────────┐
              │   CHANNEL    │
              │    AGENT     │
              └───────┬──────┘
                      │
                      ▼
              ┌──────────────┐
              │  NL Parser   │
              │  (parse_nl_  │
              │    flow)     │
              └───────┬──────┘
                      │
                      ▼
       ┌──────────────────────────┐
       │    VISUAL FLOW CANVAS    │
       │                          │
       │  ┌──────┐    ┌──────┐   │
       │  │Client│───►│Approve│   │
       │  │Action│    │Trigger│   │
       │  └──────┘    └───┬───┘   │
       │                  │       │
       │            ┌─────▼─────┐ │
       │            │Publisher  │ │
       │            │  Queue    │ │
       │            └─────┬─────┘ │
       │                  │       │
       │            ┌─────▼─────┐ │
       │            │   CM      │ │
       │            │  Review   │ │
       │            └───────────┘ │
       └──────────────────────────┘
                      │
                      ▼
              ┌──────────────┐
              │  Automation  │
              │   Trigger    │
              └───────┬──────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
  ┌─────────┐   ┌─────────┐   ┌─────────┐
  │  Slack  │   │  Email  │   │WhatsApp │
  │ Notify  │   │ Notify  │   │ Notify  │
  └─────────┘   └─────────┘   └─────────┘
```

---

## 4. ERP Integration & Onboarding

### 4.1 Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ERP INTEGRATION LAYERS                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        ERP APPLICATION                           │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │ Studio  │ │   CRM   │ │  DAM    │ │ Briefs  │ │Reporting│   │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │   │
│  └───────┼──────────┼──────────┼──────────┼──────────┼────────────┘   │
│          │          │          │          │          │                 │
│          └──────────┴──────────┴──────────┴──────────┘                 │
│                                  │                                      │
│                           ┌──────▼──────┐                              │
│                           │  ERP API    │                              │
│                           │ (REST/GQL)  │                              │
│                           └──────┬──────┘                              │
│                                  │                                      │
│  ════════════════════════════════╪══════════════════════════════════   │
│                                  │                                      │
│                           ┌──────▼──────┐                              │
│                           │ Agent API   │                              │
│                           │  Gateway    │                              │
│                           └──────┬──────┘                              │
│                                  │                                      │
│          ┌──────────┬────────────┼────────────┬──────────┐             │
│          │          │            │            │          │             │
│    ┌─────▼────┐ ┌───▼───┐ ┌─────▼────┐ ┌────▼────┐ ┌───▼────┐        │
│    │Foundation│ │Studio │ │  Media   │ │ Client  │ │Instance│        │
│    │  Agents  │ │Agents │ │  Agents  │ │ Agents  │ │ Agents │        │
│    └──────────┘ └───────┘ └──────────┘ └─────────┘ └────────┘        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Instance Onboarding Process

The Instance Onboarding Agent manages new tenant setup:

#### Phase 1: Assessment (Tools: assess_business, recommend_modules)

```
INPUT:
├── Business type (agency, studio, in-house, freelancer)
├── Business size (solo, small, medium, large, enterprise)
├── Services offered (creative, media, social, PR, events)
├── Operating regions (GCC, MENA, EU, Americas, APAC)
└── Client types (B2B, B2C, D2C, government, nonprofit)

OUTPUT:
├── Recommended modules (from 28 available)
├── Complexity tier (starter, professional, enterprise)
└── Feature recommendations
```

#### Phase 2: Infrastructure (Tools: provision_database, provision_storage, provision_cache, provision_search)

```
PROVISIONS:
├── Database instance (tenant-isolated, region-optimized)
├── Storage buckets (DAM, exports, uploads, backups)
├── Cache layer (Redis for sessions/caching)
└── Search indices (content, projects, clients, assets)
```

#### Phase 3: Platform Credentials (Tools: initiate_oauth_flow, complete_oauth_flow, link_ad_accounts)

```
PLATFORMS SUPPORTED:
├── Ads: Google Ads, Meta Ads, TikTok, Snapchat, LinkedIn, Twitter, Pinterest, DV360
├── Analytics: Google Analytics, Search Console, Brandwatch
├── Creative: Adobe CC, Figma, Canva
├── Operations: Slack, Google Workspace, Microsoft 365
└── Finance: Xero, QuickBooks, HubSpot, Salesforce
```

#### Phase 4: Configuration (Tools: configure_branding, setup_admin_user, create_roles, configure_sso)

```
CONFIGURES:
├── Branding (colors, logo, theme, fonts)
├── User structure (admin, departments, roles)
├── SSO (Google, Azure AD, Okta, Auth0, SAML)
└── Permissions (role-based access control)
```

#### Phase 5: Sample Data (Tools: generate_sample_instance, generate_sample_clients, populate_dashboards)

```
GENERATES (for demos):
├── Fictional company matching profile
├── Sample clients with realistic data
├── Sample projects in various stages
├── Sample team with utilization data
└── Populated dashboards with trends
```

### 4.3 ERP Module to Agent Mapping

| ERP Module | Primary Agent(s) | Supporting Agents |
|------------|------------------|-------------------|
| `ai` | All agents | - |
| `briefs` | Brief Agent | Content, RFP |
| `builder` | Content Agent | Presentation |
| `chat` | Gateway Agents | - |
| `complaints` | CRM Agent | QA |
| `content-engine` | Content Agent | Copy, Image |
| `content` | Content Agent | Brand Voice |
| `crm` | CRM Agent | Onboarding |
| `dam` | Image Agent | Video Production |
| `dashboard` | Ops Reporting | Instance Analytics |
| `delegation` | Workflow Agent | Resource |
| `files` | All agents | - |
| `forms` | Brief Agent | Events |
| `integrations` | Instance Onboarding | All gateways |
| `leave` | Resource Agent | Workflow |
| `notifications` | Gateway Agents | - |
| `nps` | CRM Agent | Instance Success |
| `onboarding` | Onboarding Agent | Instance Onboarding |
| `reporting` | Ops Reporting | Instance Analytics |
| `resources` | Resource Agent | Workflow |
| `retainer` | Scope Agent | Invoice |
| `rfp` | RFP Agent | Commercial |
| `scope-changes` | Scope Agent | Commercial |
| `settings` | Instance Onboarding | - |
| `studio` | All Studio Agents | Brand agents |
| `time-tracking` | Resource Agent | Invoice |
| `whatsapp` | WhatsApp Gateway | Distribution agents |
| `workflows` | Workflow Agent | All agents |

#### Engagement Suite Modules (NEW)

| ERP Module | Primary Agent(s) | Supporting Agents |
|------------|------------------|-------------------|
| `publisher` | Publisher Agent | Content, Calendar |
| `content-calendar` | Publisher Agent | Studio agents |
| `reply` | Reply Agent | CRM, Channel |
| `channel` | Channel Agent | All gateways, Publisher |
| `unified-inbox` | Reply Agent | Channel |
| `auto-responder` | Reply Agent | Knowledge |
| `crisis-escalation` | Reply Agent | Workflow |

#### Extended Modules (NEW - Tier 4)

| ERP Module | Primary Agent(s) | Key Verticals |
|------------|------------------|---------------|
| `entities` | Entities Manager | Recruitment, Events, Training |
| `scheduler` | Scheduler Agent | Consulting, Legal, Training |
| `deadlines` | Deadline Tracker | Legal, Accounting, Architecture |
| `inventory` | Inventory Manager | Events, IT, Architecture |
| `contracts` | Contract Agent | All verticals |
| `tickets` | Ticket Handler | IT Consulting |
| `vault` | Vault Agent | Legal, Accounting |

---

## 5. Agent Training & Customization

### 5.1 Understanding Agent Components

Every agent has four key components:

```python
class ExampleAgent(BaseAgent):

    # 1. IDENTITY - Name and purpose
    @property
    def name(self) -> str:
        return "example_agent"

    # 2. SYSTEM PROMPT - Personality, knowledge, behavior
    @property
    def system_prompt(self) -> str:
        return """You are an expert in [domain].

        Your role is to [primary purpose].

        ## Capabilities
        - [Capability 1]
        - [Capability 2]

        ## Approach
        [How the agent should think and behave]
        """

    # 3. TOOLS - Actions the agent can take
    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "tool_name",
                "description": "What this tool does",
                "input_schema": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
        ]

    # 4. TOOL EXECUTION - How tools work
    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "tool_name":
            return await self._do_something(tool_input)
```

### 5.2 Customizing System Prompts

System prompts define agent behavior. Key sections:

```
STRUCTURE OF A SYSTEM PROMPT
============================

1. ROLE DEFINITION
   "You are an expert [role] specializing in [domain]."

2. PRIMARY PURPOSE
   "Your role is to [main objective]."

3. CAPABILITIES LIST
   ## Capabilities
   - Capability 1: Description
   - Capability 2: Description

4. KNOWLEDGE AREAS
   ## Domain Knowledge
   - Area 1
   - Area 2

5. BEHAVIORAL GUIDELINES
   ## Approach
   - Be [adjective]
   - Always [action]
   - Never [action]

6. OUTPUT EXPECTATIONS
   ## Output Format
   - Format specifications
   - Quality standards

7. SPECIALIZATION HOOKS
   ## Vertical-Specific Notes
   [Content varies by vertical/region/language]
```

### 5.3 Adding Specializations

Agents support specialization through constructor parameters:

```python
# Vertical specialization
InfluencerAgent(
    vertical="beauty",      # Applies beauty industry knowledge
    region="uae",           # UAE-specific influencers and regulations
    language="ar",          # Arabic language support
    client_id="client_123"  # Client-specific rules
)

# The agent's system prompt adapts based on these parameters
```

#### Specialization Matrix

| Parameter | Affects | Example Values |
|-----------|---------|----------------|
| `vertical` | Domain knowledge, examples, terminology | beauty, fashion, food, tech, finance, healthcare |
| `region` | Local regulations, platforms, influencers | uae, ksa, us, uk, eu, apac |
| `language` | Output language, cultural context | en, ar, fr, de, es, zh |
| `client_id` | Brand voice, past work, preferences | client-specific ID |

### 5.4 Creating Custom Tools

Tools are the actions agents can take:

```python
# Tool definition
{
    "name": "analyze_sentiment",
    "description": "Analyze sentiment of social media mentions",
    "input_schema": {
        "type": "object",
        "properties": {
            "mentions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of mentions to analyze"
            },
            "include_emotions": {
                "type": "boolean",
                "default": False,
                "description": "Include emotion breakdown"
            }
        },
        "required": ["mentions"]
    }
}

# Tool execution
async def _analyze_sentiment(self, params: dict) -> dict:
    mentions = params["mentions"]
    include_emotions = params.get("include_emotions", False)

    # Call ERP API or external service
    response = await self.http_client.post(
        "/api/v1/sentiment/analyze",
        json={"mentions": mentions, "emotions": include_emotions}
    )

    return response.json()
```

### 5.5 Training with Examples

Agents can be improved by adding examples to system prompts:

```
## Examples

### Example 1: Simple Request
USER: "Analyze this brief for a social media campaign"
APPROACH:
1. Parse the brief document
2. Extract campaign objectives
3. Identify target audience
4. Note key messages
5. List deliverables required

### Example 2: Complex Request
USER: "Compare this RFP to our past wins in the finance vertical"
APPROACH:
1. Analyze RFP requirements
2. Search case studies filtered by vertical=finance
3. Match capabilities to requirements
4. Identify gaps
5. Generate comparison report
```

---

## 6. Updating & Maintaining Agents

### 6.1 Update Categories

| Category | Description | Frequency | Risk Level |
|----------|-------------|-----------|------------|
| **Prompt Tuning** | Adjusting system prompts for better outputs | Weekly | Low |
| **Tool Enhancement** | Adding parameters or improving tool logic | Bi-weekly | Medium |
| **New Tools** | Adding new capabilities | Monthly | Medium |
| **New Agents** | Creating entirely new agents | Quarterly | High |
| **Architecture Changes** | Modifying base agent behavior | Rare | Critical |

### 6.2 Update Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AGENT UPDATE WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. IDENTIFY NEED                                                       │
│     ├── User feedback                                                   │
│     ├── Performance metrics                                             │
│     ├── New requirements                                                │
│     └── Bug reports                                                     │
│                                                                         │
│  2. DESIGN CHANGE                                                       │
│     ├── Document proposed change                                        │
│     ├── Assess impact on other agents                                   │
│     ├── Review with stakeholders                                        │
│     └── Get approval                                                    │
│                                                                         │
│  3. DEVELOP                                                             │
│     ├── Implement in development branch                                 │
│     ├── Write/update tests                                              │
│     ├── Update documentation                                            │
│     └── Peer review                                                     │
│                                                                         │
│  4. TEST                                                                │
│     ├── Unit tests                                                      │
│     ├── Integration tests                                               │
│     ├── Regression tests                                                │
│     └── User acceptance testing                                         │
│                                                                         │
│  5. DEPLOY                                                              │
│     ├── Staged rollout (% of traffic)                                   │
│     ├── Monitor metrics                                                 │
│     ├── Rollback if issues                                              │
│     └── Full deployment                                                 │
│                                                                         │
│  6. MONITOR                                                             │
│     ├── Track performance                                               │
│     ├── Gather feedback                                                 │
│     ├── Document learnings                                              │
│     └── Plan next iteration                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Monitoring Agent Performance

Key metrics to track:

| Metric | Description | Target |
|--------|-------------|--------|
| **Success Rate** | % of tasks completed successfully | >95% |
| **Latency** | Time from request to response | <30s |
| **Tool Error Rate** | % of tool executions that fail | <2% |
| **User Satisfaction** | Rating from users | >4.0/5.0 |
| **Hallucination Rate** | Incorrect/fabricated information | <1% |
| **Token Efficiency** | Tokens used per task | Varies by agent |

### 6.4 Troubleshooting Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Timeout** | Agent doesn't respond | Increase timeout, optimize tools |
| **Wrong Tool** | Agent uses incorrect tool | Improve tool descriptions |
| **Hallucination** | Agent invents data | Add validation, ground in data |
| **Loop** | Agent repeats actions | Add loop detection, max iterations |
| **Context Loss** | Agent forgets earlier info | Improve context management |
| **Format Error** | Output in wrong format | Add output examples to prompt |

---

## 7. Certification Tracks

### 7.1 Certification Levels

```
                         ┌─────────────────────┐
                         │      EXPERT         │
                         │   (All tracks +     │
                         │    contribution)    │
                         └──────────┬──────────┘
                                    │
    ┌───────────────┬───────────────┼───────────────┬───────────────┐
    │               │               │               │               │
    ▼               ▼               ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│SPECIALIST│   │SPECIALIST│   │SPECIALIST│   │SPECIALIST│   │SPECIALIST│
│Creative │   │  Media   │   │Operations│   │Engagement│   │Verticals │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
    │               │               │               │               │
    └───────────────┴───────────────┼───────────────┴───────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │    PRACTITIONER     │
                         │  (Foundation + 1    │
                         │      track)         │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │     FOUNDATION      │
                         │    (Required)       │
                         └─────────────────────┘
```

### 7.2 Certification Requirements

#### Foundation Certified

- Complete Foundation modules (8 hours)
- Pass Foundation exam (70% minimum)
- Complete 3 hands-on labs

#### Practitioner Certified

- Foundation Certified
- Complete one specialized track (12 hours)
- Pass track-specific exam (75% minimum)
- Complete 5 hands-on labs
- Submit 1 case study

#### Specialist Certified

- Practitioner Certified
- Complete Advanced Specialization (16 hours)
- Pass advanced exam (80% minimum)
- Complete 10 hands-on labs (including track-specific labs)
- Submit 2 case studies
- Contribute 1 improvement (documentation, tool, or prompt)

##### Engagement Specialist Requirements (NEW)

- Complete Engagement Track (12 hours)
- Pass Engagement exam (80% minimum)
- Complete E-LAB-01 through E-LAB-09
- Demonstrate proficiency in:
  - Publisher multi-platform preview configuration
  - Reply crisis escalation protocol setup
  - Channel natural language flow design
  - Full engagement pipeline integration

##### Verticals Specialist Requirements (NEW)

- Complete Verticals Track (8 hours)
- Pass Verticals exam (80% minimum)
- Complete V-LAB-01 through V-LAB-03
- Configure at least 3 different industry verticals
- Demonstrate extended module configuration

#### Expert Certified

- All five Specialist certifications (Creative, Media, Operations, Engagement, Verticals)
- Contribute significant improvement (new agent, major feature)
- Mentor 2 practitioners
- Present at internal training session

---

## 8. Hands-On Labs

### 8.1 Lab Environment

Each participant gets:
- Sandbox ERP instance
- Agent API access
- Test data set
- Monitoring dashboard

### 8.2 Lab Catalog

#### Foundation Labs

| Lab | Duration | Objective |
|-----|----------|-----------|
| F-LAB-01: First Agent Call | 30 min | Execute your first agent request |
| F-LAB-02: Agent Chaining | 45 min | Chain multiple agents together |
| F-LAB-03: Error Handling | 30 min | Handle and recover from errors |

#### Creative Labs

| Lab | Duration | Objective |
|-----|----------|-----------|
| C-LAB-01: Brief to Copy | 1 hr | Generate copy from a brief |
| C-LAB-02: Moodboard Flow | 1 hr | Use moodboard to influence creative |
| C-LAB-03: Video Pipeline | 1.5 hr | Script → Storyboard → Production |
| C-LAB-04: Brand Consistency | 1 hr | Ensure brand voice across assets |

#### Media Labs

| Lab | Duration | Objective |
|-----|----------|-----------|
| M-LAB-01: Campaign Setup | 1 hr | Create campaign with Media Buying agent |
| M-LAB-02: Social Listening | 1 hr | Monitor and respond to mentions |
| M-LAB-03: Performance Report | 1 hr | Generate analytics report |
| M-LAB-04: Platform Integration | 1.5 hr | Connect Google Ads and Meta |

#### Operations Labs

| Lab | Duration | Objective |
|-----|----------|-----------|
| O-LAB-01: RFP Analysis | 1 hr | Analyze RFP and draft proposal |
| O-LAB-02: Client Onboarding | 1 hr | Onboard new client with checklist |
| O-LAB-03: Resource Planning | 1 hr | Allocate resources to project |
| O-LAB-04: Approval Workflow | 1 hr | Route content through approvals |

#### Engagement Labs (NEW)

| Lab | Duration | Objective |
|-----|----------|-----------|
| E-LAB-01: Publisher Preview Modes | 1 hr | Configure multi-platform preview modes (Website, IG, X, LinkedIn, TikTok, Email) |
| E-LAB-02: Content Queue Workflow | 1.5 hr | Build Studio → Content Calendar → Publisher Queue workflow |
| E-LAB-03: Reply Unified Inbox | 1 hr | Set up unified inbox consolidating Social, Email, Website, Messaging |
| E-LAB-04: Crisis Escalation Setup | 1.5 hr | Configure 4-level crisis escalation protocols with leadership alerts |
| E-LAB-05: Auto-Responder Config | 1 hr | Create auto-responders with time, keyword, sentiment, and customer triggers |
| E-LAB-06: Channel Visual Flows | 1.5 hr | Build automation flows using drag-and-drop canvas |
| E-LAB-07: Natural Language Flows | 1 hr | Design flows using natural language descriptions |
| E-LAB-08: Reply-from-Anywhere | 1 hr | Configure Slack, Email, WhatsApp, SMS response integration |
| E-LAB-09: Full Engagement Pipeline | 2 hr | End-to-end: Content → Publish → Reply → Channel orchestration |

#### Verticals Labs (NEW)

| Lab | Duration | Objective |
|-----|----------|-----------|
| V-LAB-01: Vertical Config | 1 hr | Configure engagement modules for specific vertical |
| V-LAB-02: Extended Modules | 1.5 hr | Set up Entities, Scheduler, Contracts for Recruitment vertical |
| V-LAB-03: Event Management Setup | 2 hr | Full event vertical with entities, scheduler, inventory, vault |

#### Advanced Labs

| Lab | Duration | Objective |
|-----|----------|-----------|
| A-LAB-01: Instance Setup | 2 hr | Full instance onboarding |
| A-LAB-02: Custom Agent | 2 hr | Create a custom specialized agent |
| A-LAB-03: Tool Development | 2 hr | Add new tool to existing agent |
| A-LAB-04: Analytics Deep Dive | 2 hr | Use Instance Analytics for insights |
| A-LAB-05: Engagement Suite Integration | 2 hr | Full Publisher + Reply + Channel integration |
| A-LAB-06: Vertical Customization | 2 hr | Customize extended modules for new industry vertical |

---

## 9. Assessment & Evaluation

### 9.1 Assessment Types

| Type | Format | Weight |
|------|--------|--------|
| **Knowledge Check** | Multiple choice, 30 questions | 30% |
| **Practical Exam** | Hands-on scenarios, 5 tasks | 40% |
| **Case Study** | Written analysis and solution | 20% |
| **Peer Review** | Evaluation by certified peer | 10% |

### 9.2 Practical Exam Scenarios

#### Foundation Practical

1. Execute agent request with proper parameters
2. Handle an agent error gracefully
3. Chain two agents together
4. Interpret agent response and extract key data
5. Configure agent specialization

#### Creative Practical

1. Generate multi-format content from brief
2. Apply moodboard styling to output
3. Ensure brand voice consistency
4. Complete video pipeline workflow
5. QA creative output

#### Media Practical

1. Set up campaign with platform integration
2. Generate performance report
3. Respond to social crisis scenario
4. Optimize underperforming campaign
5. Benchmark against competitors

#### Operations Practical

1. Process RFP and generate proposal
2. Detect and handle scope creep
3. Generate resource utilization report
4. Complete client onboarding workflow
5. Troubleshoot workflow automation

#### Engagement Practical (NEW)

1. Configure Publisher with multi-platform preview modes
2. Set up Reply unified inbox with FAQ integration
3. Create auto-responder with sentiment-based triggers
4. Design Channel flow using natural language
5. Complete crisis escalation scenario (Level 3)

#### Verticals Practical (NEW)

1. Configure engagement modules for Event Management vertical
2. Set up extended modules (Entities, Scheduler, Inventory)
3. Build vertical-specific workflow with contracts and vault
4. Migrate configuration between verticals
5. Generate vertical compliance report

---

## 10. Resources & Reference Materials

### 10.1 Documentation

| Resource | Location | Description |
|----------|----------|-------------|
| Agent Directory | `docs/AGENTS.md` | All 49+ agents with tools |
| API Reference | `/docs` endpoint | OpenAPI specification |
| Architecture | `README.md` | System architecture |
| Context Recovery | `CONTEXT.md` | Session continuity |
| Training Spec | `docs/TRAINING_SPEC.md` | This document |

### 10.2 Quick Reference

#### API Endpoints

```
POST /api/v1/agent/execute     - Execute agent task
GET  /api/v1/agent/status/:id  - Get task status
GET  /api/v1/agents            - List all agents
GET  /api/v1/health            - Health check
```

#### Execute Request Format

```json
{
  "agent_type": "rfp",
  "task": "Analyze this RFP and extract requirements",
  "tenant_id": "tenant-123",
  "user_id": "user-456",
  "metadata": {
    "project_id": "project-789",
    "document_url": "https://..."
  },
  "stream": false,
  "language": "en",
  "client_id": "client-abc",
  "vertical": "technology",
  "region": "uae"
}
```

### 10.3 Support Channels

| Channel | Use Case | Response Time |
|---------|----------|---------------|
| Slack #agent-help | Quick questions | <1 hour |
| GitHub Issues | Bug reports | <24 hours |
| Training Sessions | Learning | Scheduled |
| Office Hours | Complex problems | Weekly |

### 10.4 Glossary

| Term | Definition |
|------|------------|
| **Agent** | AI-powered specialist that performs specific tasks |
| **Tool** | Action an agent can take (API call, data query, etc.) |
| **Specialization** | Configuration that adapts agent for vertical/region/language |
| **System Prompt** | Instructions that define agent behavior |
| **Instance** | A tenant's ERP deployment |
| **Moodboard** | Human-curated visual inspiration for creative agents |
| **Gateway** | Agent that handles message delivery (WhatsApp, Email, etc.) |
| **Handoff** | Transfer of context from one agent to another |
| **Engagement Suite** | Tier 5 modules: Publisher, Reply, Channel for content distribution and customer engagement |
| **Extended Module** | Tier 4 configurable primitives (Entities, Scheduler, Deadlines, Inventory, Contracts, Tickets, Vault) |
| **Publisher** | WYSIWYG publishing hub with multi-platform preview and scheduling |
| **Reply** | Unified inbox with AI-suggested responses and crisis escalation |
| **Channel** | Omnichannel orchestration layer with visual flow design |
| **Unified Inbox** | Consolidated view of messages from Social, Email, Website, Messaging, Reviews |
| **Crisis Escalation** | 4-level protocol for handling negative sentiment and emergencies |
| **Natural Language Flow** | Describing automation workflows in plain English |
| **Vertical** | Industry-specific configuration (e.g., Marketing Agency, Legal Services) |
| **Module Tier** | Hierarchical organization of platform modules (Tiers 1-5) |

---

## Appendix A: Agent Tool Counts

| Agent | Tools | Category |
|-------|-------|----------|
| Instance Onboarding | 32 | Platform & Lifecycle |
| Instance Success | 33 | Platform & Lifecycle |
| Instance Analytics | 25 | Platform & Lifecycle |
| Channel Agent | 12 | Engagement Suite (NEW) |
| Reply Agent | 10 | Engagement Suite (NEW) |
| Publisher Agent | 8 | Engagement Suite (NEW) |
| Commercial Agent | 8 | Business Operations |
| Content Agent | 7 | Business Operations |
| Brief Agent | 6 | Business Operations |
| RFP Agent | 5 | Business Operations |
| All other agents | 4-6 | Various |

### Engagement Suite Tool Summary

| Agent | Tool Count | Primary Capabilities |
|-------|------------|---------------------|
| **Publisher** | 8 | preview_content, schedule_post, manage_queue, publish_now, get_optimal_times, format_for_platform, sync_calendar, validate_content |
| **Reply** | 10 | unify_inbox, analyze_sentiment, suggest_response, manage_faq, configure_autoresponder, escalate_crisis, route_to_team, trigger_delight, log_interaction, generate_csat |
| **Channel** | 12 | design_flow, parse_nl_flow, connect_platform, sync_channels, route_message, configure_webhook, manage_queue, reply_anywhere, track_conversation, analyze_channel, set_triggers, handoff_human |

---

## Appendix B: Training Schedule Template

```
WEEK 1: Foundation
├── Day 1-2: Platform Overview & Agent Fundamentals
├── Day 3-4: ERP Integration + Module Tier Architecture
└── Day 5: Basic Operations + Labs

WEEK 2: Specialized Track (Choose One: Creative/Media/Operations/Engagement)
├── Day 1-2: Track-specific Module 1 & 2
├── Day 3-4: Track-specific Module 3 & 4
└── Day 5: Labs + Assessment Prep

WEEK 2.5: Verticals Track (Optional but Recommended)
├── Day 1: Module Tier Architecture (Tiers 1-5)
├── Day 2-3: Engagement Module Assignment (15 verticals)
└── Day 4: Extended Module Configuration + Labs

WEEK 3: Advanced (For Specialists)
├── Day 1: Instance Lifecycle
├── Day 2: Agent Customization + Engagement Suite
├── Day 3: Integration Development
├── Day 4: Scaling & Performance
└── Day 5: Final Assessment + Certification

ENGAGEMENT TRACK SCHEDULE (12 hours)
├── Day 1 (3 hrs): Publisher Agent - Multi-platform preview, queue management
├── Day 2 (3 hrs): Reply Agent - Unified inbox, crisis escalation
├── Day 3 (3 hrs): Channel Agent - Omnichannel orchestration, flow design
└── Day 4 (3 hrs): Integration Labs - Full engagement pipeline
```

---

## Appendix C: Type Definitions (NEW)

### Engagement Module Types

```typescript
// Engagement module types (Tier 5)
export type EngagementModule = "publisher" | "reply" | "channel";

// Extended module types (Tier 4)
export type ExtendedModule =
  | "entities"
  | "scheduler"
  | "deadlines"
  | "inventory"
  | "contracts"
  | "tickets"
  | "vault";

// Platform module types
export type PlatformModule =
  | "hub" | "team" | "clients" | "admin" | "superadmin"  // Tier 1
  | "briefs" | "projects" | "boards" | "workflows"       // Tier 2
  | "time" | "resources" | "leave"                       // Tier 2
  | "finance" | "crm" | "rfp" | "chat"                   // Tier 2
  | "studio" | "marketing" | "learning" | "feedback";    // Tier 3

// Vertical configuration now includes engagement and extended modules
export interface VerticalConfiguration {
  vertical: IndustryVertical;
  modules: {
    core: PlatformModule[];           // Required modules
    recommended: PlatformModule[];    // Suggested modules
    optional: PlatformModule[];       // Available add-ons
    engagement?: EngagementModule[];  // NEW: Tier 5 engagement modules
    extended?: ExtendedModule[];      // NEW: Tier 4 extended modules
  };
  features: VerticalFeatures;
  branding: VerticalBranding;
}

// 15 Industry Verticals
export type IndustryVertical =
  | "marketing_agency"
  | "pr_communications"
  | "creative_studio"
  | "event_management"
  | "consulting_firm"
  | "recruitment_agency"
  | "it_consulting"
  | "legal_services"
  | "accounting_firm"
  | "hr_consulting"
  | "architecture_design"
  | "engineering_consultancy"
  | "project_management"
  | "training_development"
  | "translation_services";

// Publisher preview modes
export type PublisherPreviewMode =
  | "website"
  | "instagram"
  | "twitter"
  | "facebook"
  | "linkedin"
  | "tiktok"
  | "email";

// Reply auto-responder trigger types
export type AutoResponderTrigger =
  | "time"        // Off-hours, holidays
  | "keyword"     // FAQ matching
  | "sentiment"   // Negative/positive detection
  | "customer";   // VIP, new, at-risk

// Crisis escalation levels
export type CrisisLevel = 1 | 2 | 3 | 4;

export interface CrisisProtocol {
  level: CrisisLevel;
  actions: string[];
  notify: string[];     // Team members to alert
  sla: number;          // Response time in minutes
}
```

### Publisher Routes

```typescript
export const PUBLISHER_ROUTES = {
  base: "/publisher",
  create: "/publisher/create",
  drafts: "/publisher/drafts",
  scheduled: "/publisher/scheduled",
  preview: "/publisher/preview",
} as const;
```

### Reply Routes

```typescript
export const REPLY_ROUTES = {
  base: "/reply",
  inbox: "/reply/inbox",
  assigned: "/reply/assigned",
  faq: "/reply/faq",
  auto: "/reply/auto",
  escalation: "/reply/escalation",
} as const;
```

### Channel Routes

```typescript
export const CHANNEL_ROUTES = {
  base: "/channel",
  inbox: "/channel/inbox",
  connections: "/channel/connections",
  flows: "/channel/flows",
} as const;
```

---

**Document Version**: 2.0
**Last Updated**: 2026-01-13
**Maintained By**: SpokeStack Platform Team
**Review Cycle**: Quarterly
**Change Summary**: Added Engagement Suite (Tier 5), Extended Modules (Tier 4), 15 Industry Verticals, 3 new agents (Publisher, Reply, Channel)
