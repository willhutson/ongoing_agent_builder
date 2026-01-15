"""
Pre-built Workflow Templates

Ready-to-use workflow templates for common marketing agency tasks.
These can be used directly or customized for specific client needs.
"""

from .workflow import (
    Workflow,
    WorkflowStep,
    WorkflowTrigger,
    WorkflowCondition,
    StepType,
    TriggerType,
)
from .orchestrator import WorkflowBuilder


class WorkflowTemplates:
    """
    Factory for pre-built workflow templates.

    Categories:
    - Campaign: Campaign launch, A/B testing, performance monitoring
    - Client: Onboarding, reporting, competitive analysis
    - QA: Pre-launch checklists, regression testing
    - Compliance: GDPR audits, ad disclosure checks
    - Content: Content approval, social media scheduling
    """

    @staticmethod
    def campaign_launch_checklist() -> Workflow:
        """
        Complete pre-launch checklist for campaigns.

        Workflow:
        1. Verify landing page is live
        2. Run performance audit (parallel)
        3. Run accessibility audit (parallel)
        4. Check SEO meta tags (parallel)
        5. Verify UTM parameters
        6. Check GDPR compliance
        7. Human review checkpoint
        8. Capture final proof screenshots
        """
        return (
            WorkflowBuilder("campaign_launch_checklist")
            .name("Campaign Launch Checklist")
            .description("Comprehensive pre-launch verification for campaigns")
            .category("campaign")
            .tags("launch", "qa", "compliance")
            .requires_input("landing_page_url", "campaign_id", "expected_utms")
            .allowed_roles("campaign_manager", "account_manager", "qa_specialist")

            # Step 1: Verify landing page
            .add_step(
                "verify_landing",
                "qa_agent",
                "verify_landing_page",
                {
                    "url": "$context.landing_page_url",
                    "campaign_id": "$context.campaign_id",
                    "expected_elements": "$context.expected_content",
                },
                description="Verify landing page is live and contains expected content"
            )

            # Steps 2-4: Parallel audits
            .add_step(
                "performance_audit",
                "qa_agent",
                "run_performance_audit",
                {
                    "url": "$context.landing_page_url",
                    "categories": ["performance", "seo", "best-practices"],
                },
                step_type=StepType.PARALLEL,
                description="Run Lighthouse performance audit"
            )
            .add_step(
                "accessibility_audit",
                "qa_agent",
                "run_accessibility_audit",
                {
                    "url": "$context.landing_page_url",
                    "wcag_level": "AA",
                },
                step_type=StepType.PARALLEL,
                description="Check WCAG AA accessibility compliance"
            )
            .add_step(
                "seo_check",
                "qa_agent",
                "verify_meta_tags",
                {
                    "url": "$context.landing_page_url",
                },
                step_type=StepType.PARALLEL,
                description="Verify SEO meta tags and Open Graph tags"
            )

            # Step 5: UTM validation
            .add_step(
                "utm_validation",
                "campaign_agent",
                "validate_utm_parameters",
                {
                    "url": "$context.landing_page_url",
                    "expected_utms": "$context.expected_utms",
                },
                description="Validate UTM tracking parameters"
            )

            # Step 6: GDPR compliance
            .add_step(
                "gdpr_check",
                "legal_agent",
                "verify_gdpr_compliance",
                {
                    "url": "$context.landing_page_url",
                    "check_items": ["cookie_banner", "privacy_link", "consent_mechanism"],
                },
                description="Verify GDPR compliance elements"
            )

            # Step 7: Human review
            .add_human_review(
                "manager_approval",
                description="Review all QA results before final capture"
            )

            # Step 8: Final proof capture
            .add_step(
                "capture_proof",
                "qa_agent",
                "capture_device_suite",
                {
                    "url": "$context.landing_page_url",
                    "devices": ["iphone_14_pro", "ipad_mini", "desktop"],
                },
                description="Capture final proof screenshots across devices"
            )

            # Define flow
            .connect("verify_landing", "performance_audit")
            .connect("verify_landing", "accessibility_audit")
            .connect("verify_landing", "seo_check")
            .connect("performance_audit", "utm_validation")
            .connect("accessibility_audit", "utm_validation")
            .connect("seo_check", "utm_validation")
            .connect("utm_validation", "gdpr_check")
            .connect("gdpr_check", "manager_approval")
            .connect("manager_approval", "capture_proof")

            .build()
        )

    @staticmethod
    def competitive_analysis() -> Workflow:
        """
        Comprehensive competitive analysis workflow.

        Workflow:
        1. Analyze primary competitor website
        2. Capture competitor ads (parallel)
        3. Check competitor social presence (parallel)
        4. Detect recent website changes
        5. Generate comparison report
        """
        return (
            WorkflowBuilder("competitive_analysis")
            .name("Competitive Analysis")
            .description("Deep-dive competitor research and intelligence gathering")
            .category("research")
            .tags("competitor", "research", "strategy")
            .requires_input("competitor_url", "competitor_name", "client_id")
            .allowed_roles("strategist", "account_manager", "leadership")

            .add_step(
                "analyze_website",
                "competitor_agent",
                "analyze_competitor",
                {
                    "url": "$context.competitor_url",
                    "analysis_depth": "comprehensive",
                },
                description="Comprehensive competitor website analysis"
            )

            .add_step(
                "capture_ads",
                "competitor_agent",
                "capture_competitor_ads",
                {
                    "competitor_name": "$context.competitor_name",
                    "platform": "meta",
                },
                step_type=StepType.PARALLEL,
                description="Capture competitor ads from Meta Ad Library"
            )

            .add_step(
                "social_analysis",
                "competitor_agent",
                "analyze_competitor",
                {
                    "url": "$context.competitor_social_url",
                    "analysis_depth": "social_focus",
                },
                step_type=StepType.PARALLEL,
                condition="context.competitor_social_url != None",
                description="Analyze competitor social media presence"
            )

            .add_step(
                "detect_changes",
                "competitor_agent",
                "monitor_competitor_changes",
                {
                    "url": "$context.competitor_url",
                },
                description="Detect recent changes to competitor website"
            )

            .connect("analyze_website", "capture_ads")
            .connect("analyze_website", "social_analysis")
            .connect("capture_ads", "detect_changes")
            .connect("social_analysis", "detect_changes")

            .build()
        )

    @staticmethod
    def client_monthly_report() -> Workflow:
        """
        Monthly client reporting workflow.

        Workflow:
        1. Capture GA4 dashboard
        2. Capture Facebook Ads dashboard (parallel)
        3. Capture Google Ads dashboard (parallel)
        4. Capture social media analytics (parallel)
        5. Generate combined PDF report
        6. Human review before delivery
        """
        return (
            WorkflowBuilder("client_monthly_report")
            .name("Monthly Client Report")
            .description("Automated monthly performance report generation")
            .category("reporting")
            .tags("reporting", "client", "analytics")
            .requires_input("client_id", "ga4_property_id", "date_range")
            .allowed_roles("analyst", "account_manager")

            .add_step(
                "capture_ga4",
                "report_agent",
                "capture_ga4_dashboard",
                {
                    "property_id": "$context.ga4_property_id",
                    "report_type": "overview",
                    "date_range": "$context.date_range",
                },
                description="Capture Google Analytics 4 dashboard"
            )

            .add_step(
                "capture_facebook",
                "report_agent",
                "capture_facebook_ads_manager",
                {
                    "account_id": "$context.facebook_ad_account",
                    "date_range": "$context.date_range",
                },
                step_type=StepType.PARALLEL,
                condition="context.facebook_ad_account != None",
                description="Capture Facebook Ads performance"
            )

            .add_step(
                "capture_google_ads",
                "report_agent",
                "capture_google_ads_dashboard",
                {
                    "account_id": "$context.google_ads_account",
                    "date_range": "$context.date_range",
                },
                step_type=StepType.PARALLEL,
                condition="context.google_ads_account != None",
                description="Capture Google Ads performance"
            )

            .add_step(
                "capture_social",
                "report_agent",
                "capture_instagram_insights",
                {
                    "account_id": "$context.instagram_account",
                },
                step_type=StepType.PARALLEL,
                condition="context.instagram_account != None",
                description="Capture social media analytics"
            )

            .add_step(
                "generate_pdf",
                "report_agent",
                "generate_dashboard_pdf",
                {
                    "report_name": "$context.report_name",
                },
                description="Generate combined PDF report"
            )

            .add_human_review(
                "review_report",
                description="Review report before sending to client"
            )

            .connect("capture_ga4", "capture_facebook")
            .connect("capture_ga4", "capture_google_ads")
            .connect("capture_ga4", "capture_social")
            .connect("capture_facebook", "generate_pdf")
            .connect("capture_google_ads", "generate_pdf")
            .connect("capture_social", "generate_pdf")
            .connect("generate_pdf", "review_report")

            .build()
        )

    @staticmethod
    def content_approval_workflow() -> Workflow:
        """
        Content review and approval workflow.

        Workflow:
        1. Verify content is live at URL
        2. Check brand guidelines compliance
        3. Check legal/compliance issues
        4. Capture for client approval
        5. Client approval checkpoint
        """
        return (
            WorkflowBuilder("content_approval")
            .name("Content Approval Workflow")
            .description("Review and approve content before client delivery")
            .category("content")
            .tags("content", "approval", "qa")
            .requires_input("content_url", "content_type", "client_id")
            .allowed_roles("content_manager", "account_manager", "creative_lead")

            .add_step(
                "verify_live",
                "qa_agent",
                "verify_landing_page",
                {
                    "url": "$context.content_url",
                },
                description="Verify content is live and accessible"
            )

            .add_step(
                "check_accessibility",
                "qa_agent",
                "run_accessibility_audit",
                {
                    "url": "$context.content_url",
                    "wcag_level": "AA",
                },
                description="Check accessibility compliance"
            )

            .add_step(
                "legal_review",
                "legal_agent",
                "check_ad_disclosure",
                {
                    "url": "$context.content_url",
                    "ad_type": "$context.content_type",
                },
                condition="context.content_type in ['sponsored', 'ad', 'influencer']",
                description="Check FTC disclosure requirements"
            )

            .add_step(
                "capture_proof",
                "qa_agent",
                "capture_device_suite",
                {
                    "url": "$context.content_url",
                    "devices": ["iphone_14_pro", "desktop"],
                },
                description="Capture screenshots for client approval"
            )

            .add_human_review(
                "client_approval",
                description="Send to client for final approval"
            )

            .connect("verify_live", "check_accessibility")
            .connect("check_accessibility", "legal_review")
            .connect("legal_review", "capture_proof")
            .connect("capture_proof", "client_approval")

            .build()
        )

    @staticmethod
    def ab_test_analysis() -> Workflow:
        """
        A/B test variant analysis workflow.

        Workflow:
        1. Capture both variants side by side
        2. Run performance audit on both (parallel)
        3. Check SEO on both (parallel)
        4. Generate comparison summary
        """
        return (
            WorkflowBuilder("ab_test_analysis")
            .name("A/B Test Analysis")
            .description("Capture and analyze A/B test variants")
            .category("campaign")
            .tags("ab-test", "analysis", "optimization")
            .requires_input("variant_a_url", "variant_b_url", "test_name")
            .allowed_roles("campaign_manager", "analyst", "optimizer")

            .add_step(
                "capture_variants",
                "campaign_agent",
                "capture_ab_variants",
                {
                    "variant_a_url": "$context.variant_a_url",
                    "variant_b_url": "$context.variant_b_url",
                    "test_name": "$context.test_name",
                },
                description="Capture both A/B variants side by side"
            )

            .add_step(
                "audit_variant_a",
                "qa_agent",
                "run_performance_audit",
                {
                    "url": "$context.variant_a_url",
                    "categories": ["performance", "accessibility"],
                },
                step_type=StepType.PARALLEL,
                description="Performance audit for Variant A"
            )

            .add_step(
                "audit_variant_b",
                "qa_agent",
                "run_performance_audit",
                {
                    "url": "$context.variant_b_url",
                    "categories": ["performance", "accessibility"],
                },
                step_type=StepType.PARALLEL,
                description="Performance audit for Variant B"
            )

            .add_step(
                "mobile_test_a",
                "qa_agent",
                "test_mobile_device",
                {
                    "url": "$context.variant_a_url",
                    "device": "iphone_14_pro",
                },
                step_type=StepType.PARALLEL,
                description="Mobile test for Variant A"
            )

            .add_step(
                "mobile_test_b",
                "qa_agent",
                "test_mobile_device",
                {
                    "url": "$context.variant_b_url",
                    "device": "iphone_14_pro",
                },
                step_type=StepType.PARALLEL,
                description="Mobile test for Variant B"
            )

            .connect("capture_variants", "audit_variant_a")
            .connect("capture_variants", "audit_variant_b")
            .connect("capture_variants", "mobile_test_a")
            .connect("capture_variants", "mobile_test_b")

            .build()
        )

    @staticmethod
    def new_client_onboarding() -> Workflow:
        """
        New client onboarding workflow.

        Workflow:
        1. Analyze client's current website
        2. Analyze top competitors (parallel)
        3. Check current SEO status
        4. Check accessibility baseline
        5. Capture baseline screenshots
        6. Generate onboarding report
        """
        return (
            WorkflowBuilder("new_client_onboarding")
            .name("New Client Onboarding")
            .description("Comprehensive analysis for new client setup")
            .category("client")
            .tags("onboarding", "analysis", "baseline")
            .requires_input("client_website", "competitor_urls", "client_id")
            .allowed_roles("account_manager", "strategist", "leadership")

            .add_step(
                "analyze_client_site",
                "competitor_agent",
                "analyze_competitor",
                {
                    "url": "$context.client_website",
                    "analysis_depth": "comprehensive",
                },
                description="Comprehensive analysis of client's current website"
            )

            .add_step(
                "analyze_competitor_1",
                "competitor_agent",
                "analyze_competitor",
                {
                    "url": "$context.competitor_urls[0]",
                    "analysis_depth": "standard",
                },
                step_type=StepType.PARALLEL,
                condition="len(context.competitor_urls) > 0",
                description="Analyze primary competitor"
            )

            .add_step(
                "analyze_competitor_2",
                "competitor_agent",
                "analyze_competitor",
                {
                    "url": "$context.competitor_urls[1]",
                    "analysis_depth": "standard",
                },
                step_type=StepType.PARALLEL,
                condition="len(context.competitor_urls) > 1",
                description="Analyze secondary competitor"
            )

            .add_step(
                "seo_baseline",
                "qa_agent",
                "verify_meta_tags",
                {
                    "url": "$context.client_website",
                },
                description="Establish SEO baseline"
            )

            .add_step(
                "accessibility_baseline",
                "qa_agent",
                "run_accessibility_audit",
                {
                    "url": "$context.client_website",
                    "wcag_level": "AA",
                },
                description="Establish accessibility baseline"
            )

            .add_step(
                "performance_baseline",
                "qa_agent",
                "run_performance_audit",
                {
                    "url": "$context.client_website",
                    "categories": ["performance", "seo", "accessibility", "best-practices"],
                },
                description="Establish performance baseline"
            )

            .add_step(
                "capture_baseline",
                "qa_agent",
                "capture_visual_baseline",
                {
                    "url": "$context.client_website",
                    "baseline_name": "onboarding_baseline",
                },
                description="Capture visual baseline for future regression testing"
            )

            .connect("analyze_client_site", "analyze_competitor_1")
            .connect("analyze_client_site", "analyze_competitor_2")
            .connect("analyze_client_site", "seo_baseline")
            .connect("seo_baseline", "accessibility_baseline")
            .connect("accessibility_baseline", "performance_baseline")
            .connect("performance_baseline", "capture_baseline")

            .build()
        )

    @staticmethod
    def gdpr_compliance_audit() -> Workflow:
        """
        Complete GDPR compliance audit workflow.

        Workflow:
        1. Check cookie banner implementation
        2. Verify privacy policy presence
        3. Check consent mechanisms
        4. Verify data request handling info
        5. Generate compliance report
        """
        return (
            WorkflowBuilder("gdpr_compliance_audit")
            .name("GDPR Compliance Audit")
            .description("Comprehensive GDPR compliance verification")
            .category("compliance")
            .tags("gdpr", "compliance", "privacy", "legal")
            .requires_input("website_url", "client_id")
            .allowed_roles("compliance_officer", "account_manager", "legal")

            .add_step(
                "cookie_banner",
                "legal_agent",
                "analyze_cookie_banner",
                {
                    "url": "$context.website_url",
                },
                description="Analyze cookie consent banner implementation"
            )

            .add_step(
                "gdpr_elements",
                "legal_agent",
                "verify_gdpr_compliance",
                {
                    "url": "$context.website_url",
                    "check_items": [
                        "cookie_banner",
                        "privacy_link",
                        "consent_mechanism",
                        "data_request_info",
                        "cookie_policy",
                    ],
                },
                description="Verify all GDPR required elements"
            )

            .add_step(
                "privacy_policy",
                "legal_agent",
                "detect_policy_changes",
                {
                    "url": "$context.website_url",
                    "policy_type": "privacy",
                },
                description="Capture and analyze privacy policy"
            )

            .add_step(
                "capture_evidence",
                "qa_agent",
                "capture_device_suite",
                {
                    "url": "$context.website_url",
                    "devices": ["desktop"],
                },
                description="Capture compliance evidence screenshots"
            )

            .connect("cookie_banner", "gdpr_elements")
            .connect("gdpr_elements", "privacy_policy")
            .connect("privacy_policy", "capture_evidence")

            .build()
        )

    @staticmethod
    def social_content_verification() -> Workflow:
        """
        Social media content verification before posting.

        Workflow:
        1. Verify link preview (OG tags)
        2. Check image/video assets
        3. Verify hashtags and mentions
        4. Legal disclosure check (if sponsored)
        5. Approval checkpoint
        """
        return (
            WorkflowBuilder("social_content_verification")
            .name("Social Content Verification")
            .description("Pre-post verification for social media content")
            .category("content")
            .tags("social", "content", "verification")
            .requires_input("content_url", "platform", "is_sponsored")
            .allowed_roles("social_manager", "content_manager", "account_manager")

            .add_step(
                "verify_og_tags",
                "qa_agent",
                "verify_meta_tags",
                {
                    "url": "$context.content_url",
                },
                description="Verify Open Graph tags for social preview"
            )

            .add_step(
                "capture_preview",
                "campaign_agent",
                "capture_social_preview",
                {
                    "page_url": "$context.content_url",
                    "platform": "$context.platform",
                },
                description="Capture how content will appear when shared"
            )

            .add_step(
                "disclosure_check",
                "legal_agent",
                "check_ad_disclosure",
                {
                    "url": "$context.content_url",
                    "ad_type": "sponsored",
                },
                condition="context.is_sponsored == True",
                description="Verify FTC disclosure for sponsored content"
            )

            .add_human_review(
                "content_approval",
                description="Final approval before posting"
            )

            .connect("verify_og_tags", "capture_preview")
            .connect("capture_preview", "disclosure_check")
            .connect("disclosure_check", "content_approval")

            .build()
        )

    @classmethod
    def get_all_templates(cls) -> dict[str, Workflow]:
        """Get all available workflow templates."""
        return {
            "campaign_launch_checklist": cls.campaign_launch_checklist(),
            "competitive_analysis": cls.competitive_analysis(),
            "client_monthly_report": cls.client_monthly_report(),
            "content_approval": cls.content_approval_workflow(),
            "ab_test_analysis": cls.ab_test_analysis(),
            "new_client_onboarding": cls.new_client_onboarding(),
            "gdpr_compliance_audit": cls.gdpr_compliance_audit(),
            "social_content_verification": cls.social_content_verification(),
        }

    @classmethod
    def get_templates_by_category(cls, category: str) -> list[Workflow]:
        """Get all templates in a category."""
        all_templates = cls.get_all_templates()
        return [w for w in all_templates.values() if w.category == category]

    @classmethod
    def get_template_summary(cls) -> list[dict]:
        """Get summary of all templates for UI display."""
        return [
            {
                "id": w.id,
                "name": w.name,
                "description": w.description,
                "category": w.category,
                "tags": w.tags,
                "step_count": len(w.steps),
                "required_inputs": w.required_inputs,
                "allowed_roles": w.allowed_roles,
            }
            for w in cls.get_all_templates().values()
        ]
