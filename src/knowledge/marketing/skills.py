"""
Marketing Skills Library

A comprehensive library of marketing skills, tactics, and frameworks
that agents can leverage for various marketing tasks.

Based on analysis of proven marketing patterns and frameworks.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SkillCategory(str, Enum):
    """Marketing skill categories."""
    CONVERSION = "conversion"       # CRO, forms, flows
    CONTENT = "content"             # Copy, editing, social
    SEO = "seo"                     # Search optimization
    PAID = "paid"                   # Advertising
    ANALYTICS = "analytics"         # Tracking, testing
    GROWTH = "growth"               # Referral, launch
    STRATEGY = "strategy"           # Pricing, psychology
    EMAIL = "email"                 # Sequences, automation


class ModuleMapping(str, Enum):
    """ERP module mappings for skill invocation."""
    STUDIO = "studio"               # Creative production
    VIDEO = "video"                 # Video pipeline
    ANALYTICS = "analytics"         # Reporting & analytics
    PAID_MEDIA = "paid_media"       # Media buying & ads
    CONTENT = "content"             # Content & copy
    BRAND = "brand"                 # Brand management
    CLIENT = "client"               # Client management
    FINANCE = "finance"             # Finance & billing
    OPERATIONS = "operations"       # Operations
    SOCIAL = "social"               # Social media
    DISTRIBUTION = "distribution"   # Reports & distribution


class SkillComplexity(str, Enum):
    """Skill complexity levels."""
    BASIC = "basic"         # Can be done quickly with minimal context
    INTERMEDIATE = "intermediate"  # Needs some expertise
    ADVANCED = "advanced"   # Requires deep domain knowledge


@dataclass
class Skill:
    """A marketing skill with guidance."""
    id: str
    name: str
    description: str
    category: SkillCategory
    complexity: SkillComplexity
    use_cases: list[str]
    key_questions: list[str]  # Questions to ask before executing
    deliverables: list[str]   # What this skill produces
    best_practices: list[str]
    common_mistakes: list[str]
    tools_used: list[str] = field(default_factory=list)
    agent_mapping: Optional[str] = None  # Which agent handles this
    module_mapping: Optional[ModuleMapping] = None  # Which ERP module this belongs to
    invokable: bool = True  # Can users invoke this directly?


# =============================================================================
# CONVERSION OPTIMIZATION SKILLS
# =============================================================================

CONVERSION_SKILLS = {
    "page_cro": Skill(
        id="page_cro",
        name="Landing Page CRO",
        description="Optimize landing pages for higher conversion rates",
        category=SkillCategory.CONVERSION,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Homepage optimization",
            "Product page conversion",
            "Campaign landing pages",
            "Lead magnet pages",
        ],
        key_questions=[
            "What is the current conversion rate?",
            "What is the primary CTA?",
            "Who is the target audience?",
            "What is the traffic source?",
            "What objections need to be addressed?",
        ],
        deliverables=[
            "Page audit with specific issues",
            "Prioritized improvement recommendations",
            "Copy/messaging suggestions",
            "A/B test hypotheses",
        ],
        best_practices=[
            "One clear CTA per page",
            "Headline matches ad/source",
            "Social proof above the fold",
            "Remove navigation on landing pages",
            "Mobile-first design",
        ],
        common_mistakes=[
            "Too many CTAs competing for attention",
            "Feature-focused instead of benefit-focused",
            "Missing trust signals",
            "Slow page load times",
            "Generic stock photos",
        ],
        tools_used=["Gemini Vision", "Screenshot analysis"],
        agent_mapping="qa_agent",
    ),
    "form_cro": Skill(
        id="form_cro",
        name="Form Optimization",
        description="Optimize lead capture and contact forms",
        category=SkillCategory.CONVERSION,
        complexity=SkillComplexity.BASIC,
        use_cases=[
            "Lead generation forms",
            "Contact forms",
            "Demo request forms",
            "Signup forms",
        ],
        key_questions=[
            "What is form abandonment rate?",
            "How many fields currently?",
            "What info is actually needed?",
            "Where does form appear in funnel?",
        ],
        deliverables=[
            "Field reduction recommendations",
            "Multi-step form structure",
            "Micro-copy improvements",
            "Validation UX suggestions",
        ],
        best_practices=[
            "Ask only essential fields",
            "Use multi-step for 5+ fields",
            "Show progress indicators",
            "Inline validation",
            "Clear error messages",
            "Mobile-optimized inputs",
        ],
        common_mistakes=[
            "Asking for phone on first contact",
            "Required fields that aren't needed",
            "No autofill support",
            "Submit button says 'Submit'",
        ],
        agent_mapping="qa_agent",
    ),
    "signup_flow_cro": Skill(
        id="signup_flow_cro",
        name="Signup Flow Optimization",
        description="Optimize registration and signup flows",
        category=SkillCategory.CONVERSION,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "SaaS free trial signups",
            "Freemium conversions",
            "Account creation",
            "SSO vs email signup",
        ],
        key_questions=[
            "What is signup completion rate?",
            "Where do users drop off?",
            "What value do they see before signup?",
            "What is activation metric?",
        ],
        deliverables=[
            "Signup flow analysis",
            "Step reduction recommendations",
            "Social login strategy",
            "Progress indicator design",
        ],
        best_practices=[
            "Show value before asking for signup",
            "Offer Google/social login",
            "Email-only for first step",
            "Defer profile completion",
            "Celebrate completion",
        ],
        common_mistakes=[
            "Requiring credit card for trial",
            "Long forms before value",
            "No guest checkout option",
            "Verification friction",
        ],
        agent_mapping="onboarding_agent",
    ),
    "onboarding_cro": Skill(
        id="onboarding_cro",
        name="User Activation & Onboarding",
        description="Optimize post-signup user activation",
        category=SkillCategory.CONVERSION,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "SaaS onboarding flows",
            "Product activation",
            "Time-to-value optimization",
            "Aha moment discovery",
        ],
        key_questions=[
            "What is the aha moment?",
            "What % reach activation?",
            "How long to activation?",
            "What are common drop-off points?",
        ],
        deliverables=[
            "Onboarding flow map",
            "Activation metric definition",
            "Checklist/progress design",
            "Email sequence triggers",
        ],
        best_practices=[
            "Define clear activation metric",
            "Progressive disclosure",
            "Celebrate small wins",
            "Contextual help tooltips",
            "Example data/templates",
        ],
        common_mistakes=[
            "Feature tour on first login",
            "No clear next step",
            "Overwhelming with options",
            "No follow-up for stalled users",
        ],
        agent_mapping="onboarding_agent",
    ),
    "popup_cro": Skill(
        id="popup_cro",
        name="Popup & Modal Optimization",
        description="Create and optimize popups and modals",
        category=SkillCategory.CONVERSION,
        complexity=SkillComplexity.BASIC,
        use_cases=[
            "Exit intent popups",
            "Email capture modals",
            "Announcement bars",
            "Product recommendations",
        ],
        key_questions=[
            "What is popup conversion rate?",
            "What triggers the popup?",
            "What is the offer?",
            "Mobile vs desktop behavior?",
        ],
        deliverables=[
            "Popup strategy",
            "Trigger timing recommendations",
            "Copy and CTA optimization",
            "Design suggestions",
        ],
        best_practices=[
            "Delay popup 5-10 seconds minimum",
            "Easy close button",
            "Mobile-friendly sizing",
            "Clear value proposition",
            "Segment by behavior",
        ],
        common_mistakes=[
            "Immediate popup on page load",
            "Tiny close button",
            "Full-screen on mobile",
            "Same popup for everyone",
        ],
        agent_mapping="content_agent",
    ),
    "paywall_upgrade_cro": Skill(
        id="paywall_upgrade_cro",
        name="Paywall & Upgrade Optimization",
        description="Optimize in-app upgrade flows and paywalls",
        category=SkillCategory.CONVERSION,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "Freemium upgrade prompts",
            "Trial expiration flows",
            "Feature gating",
            "Usage limit prompts",
        ],
        key_questions=[
            "What is free-to-paid rate?",
            "What features are gated?",
            "When do upgrade prompts appear?",
            "What is pricing structure?",
        ],
        deliverables=[
            "Paywall audit",
            "Upgrade prompt timing",
            "Copy optimization",
            "Pricing presentation",
        ],
        best_practices=[
            "Show value of upgrade in context",
            "Anchor to higher plan",
            "Highlight popular/recommended plan",
            "Offer annual savings",
            "Money-back guarantee",
        ],
        common_mistakes=[
            "Blocking before value shown",
            "No try before buy",
            "Complex pricing",
            "No urgency/scarcity",
        ],
        agent_mapping="commercial_agent",
    ),
}


# =============================================================================
# CONTENT & COPY SKILLS
# =============================================================================

CONTENT_SKILLS = {
    "copywriting": Skill(
        id="copywriting",
        name="Marketing Copywriting",
        description="Write compelling marketing copy",
        category=SkillCategory.CONTENT,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Headlines and taglines",
            "Landing page copy",
            "Ad copy",
            "Email copy",
            "Product descriptions",
        ],
        key_questions=[
            "Who is the target audience?",
            "What is the primary benefit?",
            "What action should they take?",
            "What is the tone of voice?",
            "What objections need addressing?",
        ],
        deliverables=[
            "Multiple headline variations",
            "Body copy",
            "CTA options",
            "Microcopy suggestions",
        ],
        best_practices=[
            "Lead with benefits, not features",
            "Use customer language",
            "Write at 8th grade level",
            "One idea per paragraph",
            "End with clear CTA",
        ],
        common_mistakes=[
            "Feature-focused copy",
            "Jargon and buzzwords",
            "Weak or missing CTA",
            "Too clever, not clear",
        ],
        agent_mapping="copy_agent",
    ),
    "copy_editing": Skill(
        id="copy_editing",
        name="Copy Editing & Polish",
        description="Edit and improve existing copy",
        category=SkillCategory.CONTENT,
        complexity=SkillComplexity.BASIC,
        use_cases=[
            "Website copy review",
            "Email cleanup",
            "Ad copy optimization",
            "Consistency check",
        ],
        key_questions=[
            "What is the current copy?",
            "What is the brand voice?",
            "What is underperforming?",
            "Any specific constraints?",
        ],
        deliverables=[
            "Edited copy with track changes",
            "Style consistency fixes",
            "Clarity improvements",
            "Grammar/punctuation fixes",
        ],
        best_practices=[
            "Read aloud for flow",
            "Cut unnecessary words",
            "Active voice over passive",
            "Consistent terminology",
        ],
        common_mistakes=[
            "Over-editing voice out",
            "Inconsistent changes",
            "Missing context",
        ],
        agent_mapping="qa_agent",
    ),
    "social_content": Skill(
        id="social_content",
        name="Social Media Content",
        description="Create content for social platforms",
        category=SkillCategory.CONTENT,
        complexity=SkillComplexity.BASIC,
        use_cases=[
            "LinkedIn posts",
            "Twitter/X threads",
            "Instagram captions",
            "Content calendars",
        ],
        key_questions=[
            "Which platforms?",
            "What is the content goal?",
            "Brand voice guidelines?",
            "Posting frequency?",
        ],
        deliverables=[
            "Post copy variations",
            "Hashtag recommendations",
            "Posting schedule",
            "Content themes",
        ],
        best_practices=[
            "Platform-native formatting",
            "Hook in first line",
            "Consistent posting schedule",
            "Engage in comments",
            "Use native features (polls, etc.)",
        ],
        common_mistakes=[
            "Same content all platforms",
            "Over-promotional",
            "Inconsistent posting",
            "Ignoring engagement",
        ],
        agent_mapping="community_agent",
    ),
}


# =============================================================================
# SEO SKILLS
# =============================================================================

SEO_SKILLS = {
    "seo_audit": Skill(
        id="seo_audit",
        name="SEO Audit",
        description="Audit technical and on-page SEO",
        category=SkillCategory.SEO,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Site-wide SEO health check",
            "Page-level optimization",
            "Technical SEO issues",
            "Content gap analysis",
        ],
        key_questions=[
            "What is current organic traffic?",
            "Target keywords?",
            "Any known issues?",
            "Competitor sites?",
        ],
        deliverables=[
            "Technical SEO checklist",
            "On-page recommendations",
            "Priority action items",
            "Content opportunities",
        ],
        best_practices=[
            "Check Core Web Vitals",
            "Audit title tags and metas",
            "Review internal linking",
            "Check mobile usability",
            "Analyze competitor rankings",
        ],
        common_mistakes=[
            "Ignoring technical issues",
            "Keyword stuffing",
            "Duplicate content",
            "Missing alt text",
        ],
        tools_used=["Perplexity", "Web research"],
        agent_mapping="content_agent",
    ),
    "programmatic_seo": Skill(
        id="programmatic_seo",
        name="Programmatic SEO",
        description="Build SEO pages at scale",
        category=SkillCategory.SEO,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "Location pages",
            "Integration pages",
            "Comparison pages",
            "Directory/listing pages",
        ],
        key_questions=[
            "What data sources available?",
            "Target keyword patterns?",
            "Unique value per page?",
            "How many pages?",
        ],
        deliverables=[
            "Page template structure",
            "Data requirements",
            "Internal linking strategy",
            "Quality guidelines",
        ],
        best_practices=[
            "Unique value on each page",
            "Proper canonicalization",
            "Strategic internal linking",
            "Quality over quantity",
            "User intent match",
        ],
        common_mistakes=[
            "Thin/duplicate content",
            "No unique value",
            "Ignoring user intent",
            "Over-automation",
        ],
        tools_used=["Zhipu GLM"],
        agent_mapping="content_agent",
    ),
    "schema_markup": Skill(
        id="schema_markup",
        name="Schema Markup",
        description="Add structured data for rich snippets",
        category=SkillCategory.SEO,
        complexity=SkillComplexity.BASIC,
        use_cases=[
            "Product schema",
            "FAQ schema",
            "Article schema",
            "Organization schema",
        ],
        key_questions=[
            "What content types?",
            "Current schema status?",
            "Target rich snippets?",
        ],
        deliverables=[
            "Schema JSON-LD templates",
            "Implementation guide",
            "Testing recommendations",
        ],
        best_practices=[
            "Use JSON-LD format",
            "Validate with Google tool",
            "Match visible content",
            "Keep updated",
        ],
        common_mistakes=[
            "Schema doesn't match content",
            "Using deprecated schemas",
            "Not testing after changes",
        ],
        agent_mapping="content_agent",
    ),
}


# =============================================================================
# PAID ADVERTISING SKILLS
# =============================================================================

PAID_SKILLS = {
    "paid_ads": Skill(
        id="paid_ads",
        name="Paid Ad Campaigns",
        description="Create and optimize paid advertising",
        category=SkillCategory.PAID,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Google Ads campaigns",
            "Meta/Facebook ads",
            "LinkedIn ads",
            "Retargeting campaigns",
        ],
        key_questions=[
            "Campaign objective?",
            "Target audience?",
            "Budget?",
            "Current performance?",
            "Landing page ready?",
        ],
        deliverables=[
            "Campaign structure",
            "Ad copy variations",
            "Audience targeting",
            "Budget allocation",
        ],
        best_practices=[
            "Clear campaign objective",
            "Tight audience targeting",
            "A/B test ad creative",
            "Match ad to landing page",
            "Track conversions",
        ],
        common_mistakes=[
            "Broad targeting",
            "One ad per ad group",
            "No conversion tracking",
            "Sending to homepage",
        ],
        tools_used=["DALL-E", "Imagen"],
        agent_mapping="media_buying_agent",
    ),
}


# =============================================================================
# ANALYTICS & TESTING SKILLS
# =============================================================================

ANALYTICS_SKILLS = {
    "ab_test_setup": Skill(
        id="ab_test_setup",
        name="A/B Test Design",
        description="Plan and design statistically valid A/B tests",
        category=SkillCategory.ANALYTICS,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Landing page tests",
            "Email subject tests",
            "Pricing tests",
            "CTA tests",
        ],
        key_questions=[
            "What is the hypothesis?",
            "Primary metric?",
            "Sample size needed?",
            "Test duration?",
        ],
        deliverables=[
            "Test hypothesis document",
            "Variant specifications",
            "Success metrics",
            "Sample size calculation",
        ],
        best_practices=[
            "One variable per test",
            "Statistical significance (95%+)",
            "Sufficient sample size",
            "Document everything",
            "Don't peek at results early",
        ],
        common_mistakes=[
            "Testing too many things",
            "Ending tests early",
            "Insufficient traffic",
            "No clear hypothesis",
        ],
        agent_mapping="campaign_analytics_agent",
    ),
    "analytics_tracking": Skill(
        id="analytics_tracking",
        name="Analytics & Tracking Setup",
        description="Set up tracking and measurement",
        category=SkillCategory.ANALYTICS,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "GA4 setup",
            "GTM implementation",
            "Event tracking",
            "Conversion tracking",
        ],
        key_questions=[
            "What needs to be tracked?",
            "Current tracking status?",
            "Key conversion events?",
            "Reporting needs?",
        ],
        deliverables=[
            "Tracking plan document",
            "Event taxonomy",
            "GTM container setup",
            "Dashboard requirements",
        ],
        best_practices=[
            "Document all events",
            "Consistent naming conventions",
            "Test before deploying",
            "Regular audits",
        ],
        common_mistakes=[
            "Inconsistent event names",
            "Missing conversion events",
            "No testing",
            "Over-tracking",
        ],
        agent_mapping="campaign_analytics_agent",
    ),
}


# =============================================================================
# GROWTH SKILLS
# =============================================================================

GROWTH_SKILLS = {
    "launch_strategy": Skill(
        id="launch_strategy",
        name="Launch Strategy",
        description="Plan product and feature launches",
        category=SkillCategory.GROWTH,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "Product launches",
            "Feature announcements",
            "Version releases",
            "Market expansion",
        ],
        key_questions=[
            "What is being launched?",
            "Target audience?",
            "Launch timeline?",
            "Success metrics?",
            "Available channels?",
        ],
        deliverables=[
            "Launch timeline",
            "Channel strategy",
            "Messaging framework",
            "Asset checklist",
            "Success metrics",
        ],
        best_practices=[
            "Build anticipation pre-launch",
            "Coordinate all channels",
            "Have assets ready early",
            "Plan for problems",
            "Follow up post-launch",
        ],
        common_mistakes=[
            "Launching without promotion",
            "No follow-up plan",
            "Unclear positioning",
            "Unrealistic timeline",
        ],
        tools_used=["Perplexity"],
        agent_mapping="pr_agent",
    ),
    "referral_program": Skill(
        id="referral_program",
        name="Referral Program Design",
        description="Design referral and affiliate programs",
        category=SkillCategory.GROWTH,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Customer referral programs",
            "Affiliate programs",
            "Partner programs",
            "Ambassador programs",
        ],
        key_questions=[
            "Current customer LTV?",
            "Acquisition cost?",
            "What motivates customers?",
            "Technical capabilities?",
        ],
        deliverables=[
            "Program structure",
            "Incentive recommendations",
            "Terms and conditions",
            "Promotion plan",
        ],
        best_practices=[
            "Reward both parties",
            "Make sharing frictionless",
            "Clear, simple rewards",
            "Track and attribute",
            "Promote at right moments",
        ],
        common_mistakes=[
            "Complex reward structures",
            "Hard to share",
            "Weak incentives",
            "No promotion",
        ],
        agent_mapping="campaign_agent",
    ),
    "free_tool_strategy": Skill(
        id="free_tool_strategy",
        name="Free Tool Strategy",
        description="Plan engineering-as-marketing tools",
        category=SkillCategory.GROWTH,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "Calculators",
            "Generators",
            "Analyzers",
            "Templates",
        ],
        key_questions=[
            "Target audience pain points?",
            "Existing tools in market?",
            "SEO opportunity?",
            "Lead capture strategy?",
        ],
        deliverables=[
            "Tool concept",
            "Feature requirements",
            "Lead capture flow",
            "Promotion plan",
        ],
        best_practices=[
            "Solve real pain point",
            "Make it genuinely useful",
            "Capture leads naturally",
            "Optimize for SEO",
            "Make it shareable",
        ],
        common_mistakes=[
            "Gating too much value",
            "Not useful standalone",
            "No promotion plan",
            "Poor UX",
        ],
        agent_mapping="content_agent",
    ),
}


# =============================================================================
# STRATEGY SKILLS
# =============================================================================

STRATEGY_SKILLS = {
    "pricing_strategy": Skill(
        id="pricing_strategy",
        name="Pricing Strategy",
        description="Design pricing, packaging, and monetization",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.ADVANCED,
        use_cases=[
            "New product pricing",
            "Pricing page optimization",
            "Plan restructuring",
            "Discount strategy",
        ],
        key_questions=[
            "Current pricing model?",
            "Target customer segments?",
            "Competitor pricing?",
            "Value metrics?",
            "Current conversion rates?",
        ],
        deliverables=[
            "Pricing recommendations",
            "Package structure",
            "Pricing page copy",
            "Discount guidelines",
        ],
        best_practices=[
            "Price to value, not cost",
            "3 tiers maximum",
            "Clear differentiation",
            "Anchor to highest plan",
            "Annual discount 15-20%",
        ],
        common_mistakes=[
            "Racing to bottom",
            "Too many tiers",
            "Unclear value difference",
            "No anchor pricing",
        ],
        agent_mapping="commercial_agent",
    ),
    "marketing_psychology": Skill(
        id="marketing_psychology",
        name="Marketing Psychology",
        description="Apply behavioral science to marketing",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Persuasive copy",
            "Pricing psychology",
            "Social proof",
            "Urgency/scarcity",
        ],
        key_questions=[
            "Target audience?",
            "Desired behavior?",
            "Current approach?",
            "Ethical constraints?",
        ],
        deliverables=[
            "Psychology principles to apply",
            "Implementation recommendations",
            "Copy/design suggestions",
        ],
        best_practices=[
            "Use ethically",
            "Test effectiveness",
            "Don't manipulate",
            "Match to audience",
        ],
        common_mistakes=[
            "Fake urgency",
            "Misleading claims",
            "Over-using tactics",
            "Ignoring trust",
        ],
        agent_mapping="copy_agent",
    ),
    "competitor_alternatives": Skill(
        id="competitor_alternatives",
        name="Competitor Alternatives Pages",
        description="Create comparison and alternative pages",
        category=SkillCategory.STRATEGY,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "X vs Y pages",
            "Alternative to X pages",
            "Comparison guides",
            "Migration guides",
        ],
        key_questions=[
            "Main competitors?",
            "Key differentiators?",
            "Target search terms?",
            "Competitor weaknesses?",
        ],
        deliverables=[
            "Comparison page structure",
            "Feature comparison table",
            "Positioning copy",
            "SEO optimization",
        ],
        best_practices=[
            "Be factual and fair",
            "Highlight real differences",
            "Update regularly",
            "Include migration help",
        ],
        common_mistakes=[
            "Misleading comparisons",
            "Outdated info",
            "Too aggressive tone",
            "Ignoring competitor strengths",
        ],
        tools_used=["Perplexity", "Grok"],
        agent_mapping="competitor_agent",
    ),
}


# =============================================================================
# EMAIL SKILLS
# =============================================================================

EMAIL_SKILLS = {
    "email_sequence": Skill(
        id="email_sequence",
        name="Email Sequence Design",
        description="Build email sequences and drip campaigns",
        category=SkillCategory.EMAIL,
        complexity=SkillComplexity.INTERMEDIATE,
        use_cases=[
            "Welcome sequences",
            "Nurture campaigns",
            "Onboarding emails",
            "Re-engagement campaigns",
        ],
        key_questions=[
            "Sequence goal?",
            "Audience segment?",
            "Trigger event?",
            "Sequence length?",
            "Current email performance?",
        ],
        deliverables=[
            "Sequence flow diagram",
            "Email copy for each step",
            "Subject line variations",
            "Timing recommendations",
        ],
        best_practices=[
            "Clear goal per email",
            "Progressive value",
            "Personalization",
            "Test subject lines",
            "Monitor engagement",
        ],
        common_mistakes=[
            "Too frequent",
            "No clear goal",
            "Generic content",
            "No testing",
        ],
        agent_mapping="copy_agent",
    ),
}


# =============================================================================
# SKILL REGISTRY
# =============================================================================

ALL_SKILLS = {
    **CONVERSION_SKILLS,
    **CONTENT_SKILLS,
    **SEO_SKILLS,
    **PAID_SKILLS,
    **ANALYTICS_SKILLS,
    **GROWTH_SKILLS,
    **STRATEGY_SKILLS,
    **EMAIL_SKILLS,
}


def get_skill(skill_id: str) -> Optional[Skill]:
    """Get a skill by ID."""
    return ALL_SKILLS.get(skill_id)


def get_skills_by_category(category: SkillCategory) -> list[Skill]:
    """Get all skills in a category."""
    return [s for s in ALL_SKILLS.values() if s.category == category]


def get_skills_for_agent(agent_name: str) -> list[Skill]:
    """Get skills that map to a specific agent."""
    return [s for s in ALL_SKILLS.values() if s.agent_mapping == agent_name]


def get_all_skills() -> dict:
    """Get all skills including extended skills."""
    from .extended_skills import EXTENDED_SKILLS
    return {**ALL_SKILLS, **EXTENDED_SKILLS}


def list_all_skills() -> dict[str, list[dict]]:
    """List all skills grouped by category."""
    result = {}
    for category in SkillCategory:
        skills = get_skills_by_category(category)
        result[category.value] = [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "complexity": s.complexity.value,
                "agent": s.agent_mapping,
                "module": s.module_mapping.value if s.module_mapping else None,
                "invokable": s.invokable,
            }
            for s in skills
        ]
    return result


def get_skills_by_module(module: ModuleMapping) -> list[Skill]:
    """Get all skills available in a specific module."""
    return [s for s in ALL_SKILLS.values() if s.module_mapping == module and s.invokable]


def list_skills_by_module() -> dict[str, list[dict]]:
    """List all invokable skills grouped by ERP module."""
    result = {}
    for module in ModuleMapping:
        skills = get_skills_by_module(module)
        if skills:
            result[module.value] = [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "complexity": s.complexity.value,
                    "agent": s.agent_mapping,
                }
                for s in skills
            ]
    return result


# Module to skill mapping for quick lookup
MODULE_SKILL_REGISTRY = {
    ModuleMapping.STUDIO: [
        "copywriting", "copy_editing", "page_cro",
    ],
    ModuleMapping.VIDEO: [
        "video_scripting", "storyboarding", "video_production_brief",
    ],
    ModuleMapping.ANALYTICS: [
        "ab_test_setup", "analytics_tracking", "campaign_performance_analysis",
        "social_performance_analysis",
    ],
    ModuleMapping.PAID_MEDIA: [
        "paid_ads",
    ],
    ModuleMapping.CONTENT: [
        "copywriting", "copy_editing", "social_content", "email_sequence",
    ],
    ModuleMapping.BRAND: [
        "brand_voice_development", "visual_identity", "brand_guidelines_creation",
    ],
    ModuleMapping.CLIENT: [
        "client_brief_intake", "client_onboarding", "stakeholder_management",
        "project_scoping",
    ],
    ModuleMapping.FINANCE: [
        "budget_planning", "revenue_forecasting", "pricing_strategy",
    ],
    ModuleMapping.SOCIAL: [
        "social_content", "social_performance_analysis",
    ],
    ModuleMapping.DISTRIBUTION: [
        "campaign_performance_analysis",
    ],
}
