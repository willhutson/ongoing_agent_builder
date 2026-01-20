"""
Extended Skills Library

Additional skills based on agent capabilities and user stories.
Covers: Video, Brand, Analytics, Finance, Client, Legal, Events, Influencer
"""

from dataclasses import dataclass, field
from .skills import Skill, SkillCategory, SkillComplexity, ModuleMapping


# =============================================================================
# VIDEO SKILLS
# =============================================================================

VIDEO_SKILLS = {
    "video_scripting": Skill(
        id="video_scripting",
        name="Video Script Writing",
        description="Write compelling video scripts with proper structure",
        category=SkillCategory.CONTENT,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Product demo videos",
            "Explainer videos",
            "Testimonial videos",
            "Social video content",
            "Ads and commercials",
        ],
        key_questions=[
            "What is the video's goal?",
            "Who is the target audience?",
            "What is the video length?",
            "What platform is it for?",
            "Is there on-camera talent?",
        ],
        deliverables=[
            "Full script with VO/dialogue",
            "Scene descriptions",
            "B-roll suggestions",
            "Music/audio notes",
        ],
        best_practices=[
            "Hook in first 3 seconds",
            "One key message per video",
            "Show, don't tell",
            "End with clear CTA",
            "Write for the ear, not eye",
        ],
        common_mistakes=[
            "Too much information",
            "Weak or missing hook",
            "No clear CTA",
            "Script too long for format",
        ],
        tools_used=["ElevenLabs", "Google TTS"],
        agent_mapping="video_script_agent",
        module_mapping=ModuleMapping.VIDEO,
    ),
    "storyboarding": Skill(
        id="storyboarding",
        name="Video Storyboarding",
        description="Create visual storyboards for video production",
        category=SkillCategory.CONTENT,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Commercial storyboards",
            "Explainer video planning",
            "Social content planning",
            "Animation pre-production",
        ],
        key_questions=[
            "What is the approved script?",
            "What is the visual style?",
            "Live action or animation?",
            "What assets are available?",
            "Production constraints?",
        ],
        deliverables=[
            "Shot-by-shot breakdown",
            "Frame descriptions",
            "Camera angles/movements",
            "Transition notes",
        ],
        best_practices=[
            "Match script beats to visuals",
            "Plan for key product moments",
            "Note camera movements",
            "Include timing estimates",
            "Reference similar videos",
        ],
        common_mistakes=[
            "Too many shots for budget",
            "Unclear visual descriptions",
            "Missing transitions",
            "Not matching script",
        ],
        tools_used=["Higgsfield"],
        agent_mapping="video_storyboard_agent",
        module_mapping=ModuleMapping.VIDEO,
    ),
    "video_production_brief": Skill(
        id="video_production_brief",
        name="Video Production Brief",
        description="Create comprehensive production briefs for video",
        category=SkillCategory.CONTENT,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "Agency video briefs",
            "Internal production briefs",
            "AI video generation specs",
        ],
        key_questions=[
            "What is the video objective?",
            "Budget range?",
            "Timeline?",
            "Distribution channels?",
            "Required deliverable formats?",
        ],
        deliverables=[
            "Production brief document",
            "Technical specifications",
            "Asset requirements",
            "Approval milestones",
        ],
        best_practices=[
            "Include all technical specs upfront",
            "Define approval process",
            "List all stakeholders",
            "Specify deliverable formats",
        ],
        common_mistakes=[
            "Vague requirements",
            "Missing technical specs",
            "No approval process defined",
        ],
        tools_used=["Higgsfield", "Runway"],
        agent_mapping="video_production_agent",
        module_mapping=ModuleMapping.VIDEO,
    ),
}


# =============================================================================
# BRAND SKILLS
# =============================================================================

BRAND_SKILLS = {
    "brand_voice_development": Skill(
        id="brand_voice_development",
        name="Brand Voice Development",
        description="Define and document brand voice and tone",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "New brand voice creation",
            "Brand voice refresh",
            "Voice guidelines documentation",
            "Tone variations by channel",
        ],
        key_questions=[
            "What are the brand values?",
            "Who is the target audience?",
            "What personality traits?",
            "How formal/informal?",
            "What should we never say?",
        ],
        deliverables=[
            "Voice attributes (3-5 traits)",
            "Tone spectrum",
            "Do's and don'ts",
            "Example copy in voice",
            "Channel-specific variations",
        ],
        best_practices=[
            "Base on audience language",
            "Define 3-5 key attributes",
            "Include what NOT to say",
            "Provide clear examples",
            "Create tone variations",
        ],
        common_mistakes=[
            "Too many attributes",
            "Vague descriptions",
            "No examples",
            "Ignoring audience",
        ],
        tools_used=["ElevenLabs"],
        agent_mapping="brand_voice_agent",
        module_mapping=ModuleMapping.BRAND,
    ),
    "visual_identity": Skill(
        id="visual_identity",
        name="Visual Identity Development",
        description="Develop visual brand elements and guidelines",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "Brand visual refresh",
            "Visual guidelines creation",
            "Asset style definition",
            "Template systems",
        ],
        key_questions=[
            "What is the brand personality?",
            "Target audience preferences?",
            "Existing brand elements?",
            "Primary use cases?",
            "Competitor visual landscape?",
        ],
        deliverables=[
            "Color palette with rationale",
            "Typography recommendations",
            "Image style guidelines",
            "Layout principles",
            "Example applications",
        ],
        best_practices=[
            "Start with brand strategy",
            "Create flexible system",
            "Include accessibility",
            "Show real applications",
            "Define clear hierarchy",
        ],
        common_mistakes=[
            "Too many colors",
            "Inconsistent application",
            "Ignoring accessibility",
            "No rationale provided",
        ],
        tools_used=["DALL-E", "Flux", "Stability", "Imagen"],
        agent_mapping="brand_visual_agent",
        module_mapping=ModuleMapping.BRAND,
    ),
    "brand_guidelines_creation": Skill(
        id="brand_guidelines_creation",
        name="Brand Guidelines Creation",
        description="Create comprehensive brand guidelines document",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "New brand guidelines",
            "Guidelines update",
            "Quick reference guides",
            "Partner/vendor guidelines",
        ],
        key_questions=[
            "What elements to include?",
            "Who will use the guidelines?",
            "What format is needed?",
            "How detailed?",
            "Enforcement process?",
        ],
        deliverables=[
            "Brand guidelines document",
            "Quick reference sheet",
            "Asset library structure",
            "Usage examples",
        ],
        best_practices=[
            "Make it usable, not just pretty",
            "Include clear examples",
            "Show incorrect usage",
            "Keep it updated",
            "Make it accessible",
        ],
        common_mistakes=[
            "Too long/complex",
            "No examples",
            "Hard to find info",
            "Never updated",
        ],
        agent_mapping="brand_guidelines_agent",
        module_mapping=ModuleMapping.BRAND,
    ),
}


# =============================================================================
# ANALYTICS SKILLS
# =============================================================================

ANALYTICS_SKILLS = {
    "campaign_performance_analysis": Skill(
        id="campaign_performance_analysis",
        name="Campaign Performance Analysis",
        description="Analyze marketing campaign performance and provide insights",
        category=SkillCategory.ANALYTICS,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Campaign post-mortems",
            "Weekly/monthly reporting",
            "A/B test analysis",
            "Channel comparison",
        ],
        key_questions=[
            "What were the campaign goals?",
            "What data is available?",
            "Comparison period?",
            "Success metrics?",
            "Budget spent?",
        ],
        deliverables=[
            "Performance summary",
            "Key insights",
            "Recommendations",
            "Visualization of trends",
        ],
        best_practices=[
            "Compare to benchmarks",
            "Segment by audience",
            "Look for patterns",
            "Actionable recommendations",
            "Context for numbers",
        ],
        common_mistakes=[
            "Data without insights",
            "No benchmarks",
            "Ignoring context",
            "Too many metrics",
        ],
        tools_used=["Gemini Vision"],
        agent_mapping="campaign_analytics_agent",
        module_mapping=ModuleMapping.ANALYTICS,
    ),
    "competitor_analysis": Skill(
        id="competitor_analysis",
        name="Competitor Analysis",
        description="Analyze competitor marketing strategies and positioning",
        category=SkillCategory.ANALYTICS,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Competitive landscape review",
            "New market entry",
            "Campaign planning",
            "Positioning strategy",
        ],
        key_questions=[
            "Who are the main competitors?",
            "What aspects to analyze?",
            "Time period?",
            "Available data sources?",
        ],
        deliverables=[
            "Competitor matrix",
            "Messaging analysis",
            "Channel breakdown",
            "Opportunity gaps",
        ],
        best_practices=[
            "Use multiple data sources",
            "Look for patterns",
            "Focus on actionable insights",
            "Update regularly",
        ],
        common_mistakes=[
            "Surface-level analysis",
            "Outdated information",
            "Too many competitors",
            "No actionable insights",
        ],
        tools_used=["Perplexity", "Grok", "Gemini Vision"],
        agent_mapping="competitor_agent",
        module_mapping=ModuleMapping.ANALYTICS,
    ),
    "social_performance_analysis": Skill(
        id="social_performance_analysis",
        name="Social Media Performance Analysis",
        description="Analyze social media performance and engagement",
        category=SkillCategory.ANALYTICS,
        complexity=SkillComplexity.BASIC,
        use_cases=[
            "Monthly social reports",
            "Content performance review",
            "Audience analysis",
            "Engagement optimization",
        ],
        key_questions=[
            "Which platforms?",
            "Time period?",
            "Comparison baseline?",
            "Key metrics?",
        ],
        deliverables=[
            "Performance dashboard",
            "Top performing content",
            "Audience insights",
            "Recommendations",
        ],
        best_practices=[
            "Focus on engagement rate",
            "Analyze by content type",
            "Compare to benchmarks",
            "Track over time",
        ],
        common_mistakes=[
            "Vanity metrics focus",
            "No context",
            "Missing engagement",
        ],
        tools_used=["Gemini Vision", "Grok"],
        agent_mapping="social_analytics_agent",
        module_mapping=ModuleMapping.SOCIAL,
    ),
}


# =============================================================================
# FINANCE SKILLS
# =============================================================================

FINANCE_SKILLS = {
    "project_scoping": Skill(
        id="project_scoping",
        name="Project Scoping & Estimation",
        description="Define project scope and create estimates",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "New project scoping",
            "Change requests",
            "Retainer planning",
            "Resource estimation",
        ],
        key_questions=[
            "What are the deliverables?",
            "What is the timeline?",
            "What resources needed?",
            "What are the assumptions?",
            "What are the risks?",
        ],
        deliverables=[
            "Scope document",
            "Hour estimates",
            "Resource plan",
            "Assumptions list",
            "Risk assessment",
        ],
        best_practices=[
            "Document all assumptions",
            "Include buffer (15-20%)",
            "Get stakeholder sign-off",
            "Define out-of-scope clearly",
        ],
        common_mistakes=[
            "Underestimating complexity",
            "Missing dependencies",
            "No change process",
            "Vague deliverables",
        ],
        agent_mapping="scope_agent",
        module_mapping=ModuleMapping.CLIENT,
    ),
    "budget_planning": Skill(
        id="budget_planning",
        name="Marketing Budget Planning",
        description="Plan and allocate marketing budgets",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Annual budget planning",
            "Campaign budgeting",
            "Channel allocation",
            "Budget reallocation",
        ],
        key_questions=[
            "Total budget available?",
            "Business goals?",
            "Historical performance?",
            "Required channels?",
            "Fixed vs variable costs?",
        ],
        deliverables=[
            "Budget allocation",
            "Channel breakdown",
            "Monthly phasing",
            "ROI projections",
        ],
        best_practices=[
            "Align to business goals",
            "Use historical data",
            "Build in contingency",
            "Track against plan",
        ],
        common_mistakes=[
            "No contingency",
            "Ignoring seasonality",
            "Set and forget",
            "No measurement plan",
        ],
        agent_mapping="budget_agent",
        module_mapping=ModuleMapping.FINANCE,
    ),
    "revenue_forecasting": Skill(
        id="revenue_forecasting",
        name="Revenue Forecasting",
        description="Create revenue forecasts and projections",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "Quarterly forecasting",
            "Pipeline analysis",
            "Scenario planning",
            "Board reporting",
        ],
        key_questions=[
            "Current pipeline?",
            "Historical close rates?",
            "Seasonality factors?",
            "Market conditions?",
            "What scenarios to model?",
        ],
        deliverables=[
            "Revenue forecast",
            "Scenario analysis",
            "Key assumptions",
            "Risk factors",
        ],
        best_practices=[
            "Use probability weights",
            "Model multiple scenarios",
            "Document assumptions",
            "Update regularly",
        ],
        common_mistakes=[
            "Over-optimistic",
            "Single scenario",
            "Stale data",
            "No assumptions documented",
        ],
        agent_mapping="forecast_agent",
        module_mapping=ModuleMapping.FINANCE,
    ),
}


# =============================================================================
# CLIENT MANAGEMENT SKILLS
# =============================================================================

CLIENT_SKILLS = {
    "client_brief_intake": Skill(
        id="client_brief_intake",
        name="Client Brief Intake",
        description="Structure and clarify client briefs",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.BASIC,
        use_cases=[
            "New project intake",
            "Campaign briefs",
            "Creative briefs",
            "Strategy briefs",
        ],
        key_questions=[
            "What is the objective?",
            "Who is the audience?",
            "What is the timeline?",
            "What is the budget?",
            "What does success look like?",
        ],
        deliverables=[
            "Structured brief document",
            "Clarifying questions",
            "Success metrics",
            "Key dates",
        ],
        best_practices=[
            "Get specific on goals",
            "Clarify audience",
            "Confirm constraints",
            "Document everything",
        ],
        common_mistakes=[
            "Assuming understanding",
            "Missing constraints",
            "Vague success metrics",
        ],
        agent_mapping="brief_agent",
        module_mapping=ModuleMapping.CLIENT,
    ),
    "client_onboarding": Skill(
        id="client_onboarding",
        name="Client Onboarding",
        description="Structure and execute client onboarding",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "New client setup",
            "Project kickoff",
            "Team introductions",
            "Systems access",
        ],
        key_questions=[
            "What info do we need?",
            "What access is required?",
            "Who are the stakeholders?",
            "What is the timeline?",
            "Communication preferences?",
        ],
        deliverables=[
            "Onboarding checklist",
            "Kickoff agenda",
            "Information request",
            "Communication plan",
        ],
        best_practices=[
            "Structured checklist",
            "Clear ownership",
            "Regular check-ins",
            "Document preferences",
        ],
        common_mistakes=[
            "Missing key info",
            "No clear timeline",
            "Assuming preferences",
        ],
        agent_mapping="onboarding_agent",
        module_mapping=ModuleMapping.CLIENT,
    ),
    "stakeholder_management": Skill(
        id="stakeholder_management",
        name="Stakeholder Management",
        description="Manage client stakeholders effectively",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Multi-stakeholder projects",
            "Approval processes",
            "Status communication",
            "Escalation handling",
        ],
        key_questions=[
            "Who are the stakeholders?",
            "Decision-making authority?",
            "Communication preferences?",
            "Approval workflow?",
        ],
        deliverables=[
            "Stakeholder map",
            "Communication plan",
            "Approval workflow",
            "Escalation path",
        ],
        best_practices=[
            "Map all stakeholders early",
            "Understand motivations",
            "Tailor communication",
            "Document decisions",
        ],
        common_mistakes=[
            "Missing key stakeholders",
            "One-size communication",
            "No escalation plan",
        ],
        agent_mapping="crm_agent",
        module_mapping=ModuleMapping.CLIENT,
    ),
}


# =============================================================================
# LEGAL & COMPLIANCE SKILLS
# =============================================================================

LEGAL_SKILLS = {
    "contract_review": Skill(
        id="contract_review",
        name="Contract Review",
        description="Review contracts for risks and issues",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "Vendor contracts",
            "Client agreements",
            "Partnership agreements",
            "NDA review",
        ],
        key_questions=[
            "What type of contract?",
            "Key terms to check?",
            "Risk tolerance?",
            "Standard terms available?",
            "Negotiation points?",
        ],
        deliverables=[
            "Risk summary",
            "Key terms analysis",
            "Recommended changes",
            "Negotiation priorities",
        ],
        best_practices=[
            "Check against standards",
            "Flag high-risk clauses",
            "Prioritize issues",
            "Document reasoning",
        ],
        common_mistakes=[
            "Missing key clauses",
            "No risk ranking",
            "Over-flagging",
        ],
        agent_mapping="legal_agent",
        module_mapping=ModuleMapping.OPERATIONS,
    ),
    "compliance_check": Skill(
        id="compliance_check",
        name="Marketing Compliance Check",
        description="Check marketing materials for compliance",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Ad compliance review",
            "Email compliance",
            "Privacy compliance",
            "Industry regulations",
        ],
        key_questions=[
            "What type of content?",
            "Target markets?",
            "Industry regulations?",
            "Claims being made?",
        ],
        deliverables=[
            "Compliance checklist",
            "Issues flagged",
            "Required disclosures",
            "Recommended changes",
        ],
        best_practices=[
            "Know regulations",
            "Document evidence",
            "Use checklists",
            "Get legal sign-off",
        ],
        common_mistakes=[
            "Assuming compliance",
            "Missing disclosures",
            "Outdated knowledge",
        ],
        agent_mapping="legal_agent",
        module_mapping=ModuleMapping.OPERATIONS,
    ),
}


# =============================================================================
# EVENTS & INFLUENCER SKILLS
# =============================================================================

EVENTS_INFLUENCER_SKILLS = {
    "event_planning": Skill(
        id="event_planning",
        name="Event Planning",
        description="Plan and coordinate marketing events",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "Conference planning",
            "Webinars",
            "Product launches",
            "Customer events",
        ],
        key_questions=[
            "Event objective?",
            "Target audience?",
            "Budget?",
            "Timeline?",
            "Virtual or in-person?",
        ],
        deliverables=[
            "Event brief",
            "Timeline/checklist",
            "Budget breakdown",
            "Promotion plan",
        ],
        best_practices=[
            "Start with clear goals",
            "Build in buffer time",
            "Have backup plans",
            "Post-event follow-up",
        ],
        common_mistakes=[
            "Unrealistic timeline",
            "No promotion plan",
            "Missing follow-up",
        ],
        tools_used=["DALL-E", "Beautiful.ai"],
        agent_mapping="events_agent",
        module_mapping=ModuleMapping.OPERATIONS,
    ),
    "influencer_campaign": Skill(
        id="influencer_campaign",
        name="Influencer Campaign Planning",
        description="Plan and execute influencer marketing campaigns",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Product launches",
            "Brand awareness",
            "Content partnerships",
            "Affiliate programs",
        ],
        key_questions=[
            "Campaign goals?",
            "Target audience?",
            "Budget?",
            "Influencer criteria?",
            "Content requirements?",
        ],
        deliverables=[
            "Campaign brief",
            "Influencer criteria",
            "Outreach templates",
            "Contract terms",
            "Success metrics",
        ],
        best_practices=[
            "Define clear criteria",
            "Check authenticity",
            "Clear content guidelines",
            "Track attribution",
        ],
        common_mistakes=[
            "Follower count focus",
            "Vague guidelines",
            "No tracking",
        ],
        tools_used=["Perplexity", "Gemini Vision", "Grok"],
        agent_mapping="influencer_agent",
        module_mapping=ModuleMapping.SOCIAL,
    ),
    "pr_campaign": Skill(
        id="pr_campaign",
        name="PR Campaign Planning",
        description="Plan and execute PR campaigns",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Product launches",
            "Company announcements",
            "Thought leadership",
            "Crisis communication",
        ],
        key_questions=[
            "What is the news?",
            "Target publications?",
            "Timeline?",
            "Spokesperson available?",
            "Assets needed?",
        ],
        deliverables=[
            "PR brief",
            "Media list",
            "Press release",
            "Pitch templates",
            "Q&A document",
        ],
        best_practices=[
            "Lead with news value",
            "Personalize pitches",
            "Have assets ready",
            "Follow up appropriately",
        ],
        common_mistakes=[
            "No news angle",
            "Generic pitches",
            "Missing assets",
            "Bad timing",
        ],
        tools_used=["Grok", "Perplexity"],
        agent_mapping="pr_agent",
        module_mapping=ModuleMapping.SOCIAL,
    ),
}


# =============================================================================
# COMBINE ALL EXTENDED SKILLS
# =============================================================================

EXTENDED_SKILLS = {
    **VIDEO_SKILLS,
    **BRAND_SKILLS,
    **ANALYTICS_SKILLS,
    **FINANCE_SKILLS,
    **CLIENT_SKILLS,
    **LEGAL_SKILLS,
    **EVENTS_INFLUENCER_SKILLS,
}
