"""
Agent Training Content

Provides structured training content for each agent's capabilities.
This content is agent-specific and works across all tenant industries.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ToolGuide:
    """Guide for using a specific agent tool."""
    tool_name: str
    description: str
    when_to_use: list[str]
    input_parameters: dict
    example_usage: dict
    common_mistakes: list[str] = field(default_factory=list)
    tips: list[str] = field(default_factory=list)


@dataclass
class AgentGuide:
    """Complete guide for an agent's capabilities."""
    agent_id: str
    agent_name: str
    overview: str
    tool_guides: list[ToolGuide]
    best_practices: list[str]
    common_workflows: list[dict]


class AgentTrainingContent:
    """
    Provides training content for all agents.
    Content is agent-capability focused, not industry-specific.
    """

    def __init__(self):
        self._guides: dict[str, AgentGuide] = {}
        self._initialize_content()

    def _initialize_content(self):
        """Initialize all agent training content."""
        self._guides = {
            "qa_agent": self._get_qa_agent_guide(),
            "campaign_agent": self._get_campaign_agent_guide(),
            "competitor_agent": self._get_competitor_agent_guide(),
            "legal_agent": self._get_legal_agent_guide(),
            "report_agent": self._get_report_agent_guide(),
            "pr_agent": self._get_pr_agent_guide(),
        }

    def get_agent_guide(self, agent_id: str) -> Optional[AgentGuide]:
        """Get the training guide for an agent."""
        return self._guides.get(agent_id)

    def get_tool_guide(self, agent_id: str, tool_name: str) -> Optional[ToolGuide]:
        """Get the guide for a specific tool."""
        agent_guide = self._guides.get(agent_id)
        if agent_guide:
            for tool in agent_guide.tool_guides:
                if tool.tool_name == tool_name:
                    return tool
        return None

    def get_all_guides(self) -> list[AgentGuide]:
        """Get all agent guides."""
        return list(self._guides.values())

    # =========================================================================
    # QA Agent Content
    # =========================================================================

    def _get_qa_agent_guide(self) -> AgentGuide:
        return AgentGuide(
            agent_id="qa_agent",
            agent_name="QA Agent",
            overview="""The QA Agent automates quality assurance tasks for digital deliverables.
            It can verify pages are live and correct, run performance audits, check accessibility
            compliance, test across devices, verify SEO elements, and validate forms and links.

            Use the QA Agent whenever you need to verify that web pages meet quality standards
            before delivery or launch.""",
            best_practices=[
                "Always run a full performance audit before campaign launches",
                "Capture device suite screenshots for responsive verification",
                "Check accessibility compliance early in the project lifecycle",
                "Use the QA Agent to document proof of work for clients",
                "Set up regular broken link checks for client websites",
            ],
            common_workflows=[
                {
                    "name": "Pre-Launch Page Verification",
                    "steps": [
                        "verify_landing_page - Confirm page loads correctly",
                        "run_performance_audit - Check performance metrics",
                        "run_accessibility_audit - Verify WCAG compliance",
                        "capture_device_suite - Test responsive design",
                        "check_broken_links - Find any broken links",
                    ],
                },
                {
                    "name": "SEO Readiness Check",
                    "steps": [
                        "verify_meta_tags - Check title and descriptions",
                        "check_structured_data - Verify schema markup",
                        "verify_canonical_url - Confirm canonical tags",
                        "check_robots_meta - Check indexing settings",
                    ],
                },
            ],
            tool_guides=[
                ToolGuide(
                    tool_name="run_performance_audit",
                    description="Runs a comprehensive performance audit similar to Google Lighthouse.",
                    when_to_use=[
                        "Before launching a new page or campaign",
                        "When clients report slow page loads",
                        "For regular performance monitoring",
                        "When optimizing existing pages",
                    ],
                    input_parameters={
                        "url": "The page URL to audit",
                        "categories": "Which audits to run: performance, accessibility, seo, best-practices",
                    },
                    example_usage={
                        "scenario": "Verify a client landing page before campaign launch",
                        "input": {"url": "https://client.com/landing", "categories": ["performance", "accessibility"]},
                        "expected_output": "Performance scores, Core Web Vitals, optimization recommendations",
                    },
                    tips=[
                        "Run audits on production URLs for accurate results",
                        "Test at different times of day to catch caching issues",
                        "Compare scores before and after optimizations",
                    ],
                ),
                ToolGuide(
                    tool_name="run_accessibility_audit",
                    description="Checks page against WCAG accessibility guidelines.",
                    when_to_use=[
                        "For ADA/WCAG compliance verification",
                        "Before launching public-facing pages",
                        "When clients require accessibility certification",
                        "Regular accessibility monitoring",
                    ],
                    input_parameters={
                        "url": "The page URL to audit",
                        "wcag_level": "Target compliance level: A, AA, or AAA",
                    },
                    example_usage={
                        "scenario": "Verify WCAG AA compliance for a client website",
                        "input": {"url": "https://client.com", "wcag_level": "AA"},
                        "expected_output": "Compliance score, passed/failed checks, recommendations",
                    },
                    common_mistakes=[
                        "Only testing the homepage - test all key pages",
                        "Ignoring color contrast warnings",
                        "Not checking keyboard navigation",
                    ],
                ),
                ToolGuide(
                    tool_name="capture_device_suite",
                    description="Captures screenshots across multiple device viewports.",
                    when_to_use=[
                        "For responsive design verification",
                        "Client presentations and approvals",
                        "Before launching responsive updates",
                        "Visual regression testing",
                    ],
                    input_parameters={
                        "url": "The page URL to capture",
                        "devices": "List of devices: iphone_se, iphone_14_pro, pixel_7, ipad_mini, ipad_pro",
                    },
                    example_usage={
                        "scenario": "Verify responsive design before launch",
                        "input": {"url": "https://client.com", "devices": ["iphone_14_pro", "ipad_mini", "pixel_7"]},
                        "expected_output": "Screenshots from each device viewport",
                    },
                    tips=[
                        "Always include both phone and tablet viewports",
                        "Test both portrait and landscape when relevant",
                        "Save screenshots as proof of work",
                    ],
                ),
                ToolGuide(
                    tool_name="verify_meta_tags",
                    description="Checks SEO meta tags including title, description, and Open Graph tags.",
                    when_to_use=[
                        "SEO audits and verification",
                        "Before campaign launches",
                        "Social sharing optimization",
                        "Search ranking optimization",
                    ],
                    input_parameters={
                        "url": "The page URL to check",
                    },
                    example_usage={
                        "scenario": "Verify SEO setup for a new landing page",
                        "input": {"url": "https://client.com/new-page"},
                        "expected_output": "Title, description, OG tags, Twitter cards, and issues found",
                    },
                ),
                ToolGuide(
                    tool_name="check_broken_links",
                    description="Finds broken internal and external links on a page.",
                    when_to_use=[
                        "Pre-launch verification",
                        "Regular site maintenance",
                        "After content migrations",
                        "SEO health checks",
                    ],
                    input_parameters={
                        "url": "The page URL to check",
                        "include_external": "Whether to check external links too",
                    },
                    example_usage={
                        "scenario": "Find broken links before a site launch",
                        "input": {"url": "https://client.com", "include_external": True},
                        "expected_output": "List of broken links with status codes",
                    },
                ),
            ],
        )

    # =========================================================================
    # Campaign Agent Content
    # =========================================================================

    def _get_campaign_agent_guide(self) -> AgentGuide:
        return AgentGuide(
            agent_id="campaign_agent",
            agent_name="Campaign Agent",
            overview="""The Campaign Agent specializes in campaign verification and asset management.
            It can verify landing pages, capture A/B test variants, validate UTM parameters,
            test email templates, check social media assets, and analyze redirect chains.

            Use the Campaign Agent for pre-launch verification and campaign documentation.""",
            best_practices=[
                "Always verify landing pages before campaign launch",
                "Document A/B test variants with side-by-side captures",
                "Validate UTM parameters match tracking requirements",
                "Check redirect chains to minimize load time",
                "Capture email previews across multiple clients",
            ],
            common_workflows=[
                {
                    "name": "Campaign Pre-Launch",
                    "steps": [
                        "verify_landing_page - Confirm page is live",
                        "validate_utm_parameters - Check tracking setup",
                        "check_redirect_chain - Verify link path",
                        "verify_form_fields - Test form functionality",
                    ],
                },
                {
                    "name": "A/B Test Documentation",
                    "steps": [
                        "capture_ab_variants - Capture both variants",
                        "verify_landing_page - Verify each variant",
                        "validate_utm_parameters - Check tracking differs",
                    ],
                },
            ],
            tool_guides=[
                ToolGuide(
                    tool_name="verify_landing_page",
                    description="Verifies a campaign landing page is live and displays correctly.",
                    when_to_use=[
                        "Before launching paid campaigns",
                        "After page updates or changes",
                        "For client approval documentation",
                        "Regular campaign health checks",
                    ],
                    input_parameters={
                        "url": "The landing page URL",
                        "expected_content": "Content that should appear on the page",
                    },
                    example_usage={
                        "scenario": "Verify landing page before launching Google Ads",
                        "input": {"url": "https://client.com/promo", "expected_content": ["Shop Now", "Free Shipping"]},
                        "expected_output": "Page status, content verification, screenshot proof",
                    },
                ),
                ToolGuide(
                    tool_name="capture_ab_variants",
                    description="Captures A/B test variants side-by-side for comparison.",
                    when_to_use=[
                        "Documenting A/B tests for analysis",
                        "Client presentations of test variants",
                        "Before/after comparison documentation",
                    ],
                    input_parameters={
                        "variant_a_url": "URL for variant A",
                        "variant_b_url": "URL for variant B",
                        "test_name": "Name for the test",
                    },
                    example_usage={
                        "scenario": "Document an A/B test for client review",
                        "input": {
                            "variant_a_url": "https://client.com/landing?variant=a",
                            "variant_b_url": "https://client.com/landing?variant=b",
                            "test_name": "homepage_cta_test",
                        },
                        "expected_output": "Side-by-side screenshots of both variants",
                    },
                ),
                ToolGuide(
                    tool_name="validate_utm_parameters",
                    description="Validates UTM tracking parameters in a URL.",
                    when_to_use=[
                        "Before launching tracked campaigns",
                        "Verifying attribution setup",
                        "Auditing existing campaigns",
                    ],
                    input_parameters={
                        "url": "The full URL with UTM parameters",
                        "expected_utms": "Expected UTM values to verify",
                    },
                    example_usage={
                        "scenario": "Verify UTM parameters for a Facebook campaign",
                        "input": {
                            "url": "https://client.com/landing?utm_source=facebook&utm_medium=paid&utm_campaign=summer_sale",
                            "expected_utms": {"utm_source": "facebook", "utm_medium": "paid"},
                        },
                        "expected_output": "UTM validation results showing matches and mismatches",
                    },
                ),
                ToolGuide(
                    tool_name="check_redirect_chain",
                    description="Analyzes the redirect chain for a URL.",
                    when_to_use=[
                        "Verifying tracking links work correctly",
                        "Diagnosing slow page loads",
                        "Checking shortened URLs",
                        "Campaign link audits",
                    ],
                    input_parameters={
                        "url": "The starting URL to trace",
                    },
                    example_usage={
                        "scenario": "Check redirect chain for a tracking link",
                        "input": {"url": "https://track.example.com/abc123"},
                        "expected_output": "Each redirect hop with status codes and final destination",
                    },
                ),
            ],
        )

    # =========================================================================
    # Competitor Agent Content
    # =========================================================================

    def _get_competitor_agent_guide(self) -> AgentGuide:
        return AgentGuide(
            agent_id="competitor_agent",
            agent_name="Competitor Agent",
            overview="""The Competitor Agent gathers competitive intelligence by analyzing
            competitor websites, capturing their ads, and monitoring changes over time.

            Use the Competitor Agent for market research, strategy development, and
            competitive benchmarking.""",
            best_practices=[
                "Set up regular monitoring for key competitors",
                "Capture competitor ads monthly for trend analysis",
                "Document competitor website changes over time",
                "Use analysis for strategic recommendations",
            ],
            common_workflows=[
                {
                    "name": "Competitor Deep Dive",
                    "steps": [
                        "analyze_competitor - Full website analysis",
                        "capture_competitor_ads - Capture their ad creatives",
                        "monitor_competitor_changes - Set up change tracking",
                    ],
                },
            ],
            tool_guides=[
                ToolGuide(
                    tool_name="analyze_competitor",
                    description="Performs comprehensive analysis of a competitor website.",
                    when_to_use=[
                        "Strategic planning sessions",
                        "New client onboarding",
                        "Market research projects",
                        "Competitive positioning analysis",
                    ],
                    input_parameters={
                        "url": "The competitor's website URL",
                        "analysis_depth": "How deep to analyze: quick, standard, comprehensive",
                    },
                    example_usage={
                        "scenario": "Analyze a new competitor for a client",
                        "input": {"url": "https://competitor.com", "analysis_depth": "comprehensive"},
                        "expected_output": "Technology stack, content analysis, UX patterns, key findings",
                    },
                ),
                ToolGuide(
                    tool_name="capture_competitor_ads",
                    description="Captures competitor advertising from ad libraries.",
                    when_to_use=[
                        "Monthly competitive ad tracking",
                        "Creative inspiration research",
                        "Ad strategy planning",
                    ],
                    input_parameters={
                        "competitor_name": "The competitor to search for",
                        "platform": "Ad platform: facebook, google, linkedin",
                    },
                    example_usage={
                        "scenario": "Capture competitor Facebook ads",
                        "input": {"competitor_name": "Acme Corp", "platform": "facebook"},
                        "expected_output": "Screenshots of active competitor ads",
                    },
                ),
            ],
        )

    # =========================================================================
    # Legal Agent Content
    # =========================================================================

    def _get_legal_agent_guide(self) -> AgentGuide:
        return AgentGuide(
            agent_id="legal_agent",
            agent_name="Legal Agent",
            overview="""The Legal Agent verifies compliance with legal requirements including
            GDPR, cookie consent, FTC disclosure requirements, and privacy policies.

            Use the Legal Agent to ensure client deliverables meet regulatory requirements.""",
            best_practices=[
                "Run GDPR checks on all EU-targeted pages",
                "Verify cookie banners before launch",
                "Check FTC disclosure on influencer content",
                "Monitor policy pages for changes",
            ],
            common_workflows=[
                {
                    "name": "GDPR Compliance Audit",
                    "steps": [
                        "verify_gdpr_compliance - Check GDPR elements",
                        "analyze_cookie_banner - Verify consent mechanism",
                        "detect_policy_changes - Monitor privacy policy",
                    ],
                },
            ],
            tool_guides=[
                ToolGuide(
                    tool_name="verify_gdpr_compliance",
                    description="Verifies GDPR compliance elements on a page.",
                    when_to_use=[
                        "Launching pages targeting EU users",
                        "Compliance audits",
                        "Client due diligence",
                    ],
                    input_parameters={
                        "url": "The page URL to check",
                        "check_items": "Specific items to verify",
                    },
                    example_usage={
                        "scenario": "Verify GDPR compliance before EU campaign launch",
                        "input": {"url": "https://client.com/eu-landing", "check_items": ["cookie_consent", "privacy_link"]},
                        "expected_output": "GDPR compliance checklist results",
                    },
                ),
                ToolGuide(
                    tool_name="analyze_cookie_banner",
                    description="Analyzes cookie consent implementation.",
                    when_to_use=[
                        "Cookie compliance verification",
                        "Privacy audits",
                        "Before launching in regulated regions",
                    ],
                    input_parameters={
                        "url": "The page URL to analyze",
                    },
                    example_usage={
                        "scenario": "Verify cookie banner meets requirements",
                        "input": {"url": "https://client.com"},
                        "expected_output": "Cookie banner analysis including consent mechanism evaluation",
                    },
                ),
            ],
        )

    # =========================================================================
    # Report Agent Content
    # =========================================================================

    def _get_report_agent_guide(self) -> AgentGuide:
        return AgentGuide(
            agent_id="report_agent",
            agent_name="Report Agent",
            overview="""The Report Agent automates dashboard capture and report generation.
            It can capture analytics dashboards, ad platform reports, and generate PDFs.

            Use the Report Agent for client reporting and performance documentation.""",
            best_practices=[
                "Schedule regular dashboard captures for consistency",
                "Use date ranges that match client reporting periods",
                "Capture multiple dashboards for comprehensive reports",
                "Generate PDFs for client-ready deliverables",
            ],
            common_workflows=[
                {
                    "name": "Monthly Client Report",
                    "steps": [
                        "capture_ga4_dashboard - Get analytics data",
                        "capture_facebook_ads_manager - Get ad performance",
                        "capture_multi_dashboard - Compare platforms",
                        "generate_dashboard_pdf - Create deliverable",
                    ],
                },
            ],
            tool_guides=[
                ToolGuide(
                    tool_name="capture_ga4_dashboard",
                    description="Captures Google Analytics 4 dashboard screenshots.",
                    when_to_use=[
                        "Client performance reports",
                        "Monthly analytics review",
                        "Traffic analysis documentation",
                    ],
                    input_parameters={
                        "property_id": "GA4 property ID",
                        "report_type": "Type of report to capture",
                        "date_range": "Date range for the report",
                    },
                    example_usage={
                        "scenario": "Capture GA4 dashboard for monthly report",
                        "input": {"property_id": "123456789", "report_type": "overview", "date_range": "last_30_days"},
                        "expected_output": "GA4 dashboard screenshot",
                    },
                ),
                ToolGuide(
                    tool_name="generate_dashboard_pdf",
                    description="Generates a PDF from dashboard captures.",
                    when_to_use=[
                        "Creating client deliverables",
                        "Archiving report data",
                        "Sharing via email",
                    ],
                    input_parameters={
                        "url": "Dashboard URL to capture",
                        "report_name": "Name for the PDF",
                    },
                    example_usage={
                        "scenario": "Generate PDF report for client",
                        "input": {"url": "https://analytics.google.com/...", "report_name": "January_2024_Report"},
                        "expected_output": "PDF file path",
                    },
                ),
            ],
        )

    # =========================================================================
    # PR Agent Content
    # =========================================================================

    def _get_pr_agent_guide(self) -> AgentGuide:
        return AgentGuide(
            agent_id="pr_agent",
            agent_name="PR Agent",
            overview="""The PR Agent handles media monitoring and press coverage documentation.
            It can track media mentions and capture press coverage for client archives.

            Use the PR Agent for brand monitoring and PR measurement.""",
            best_practices=[
                "Set up regular media monitoring for client brands",
                "Capture press coverage immediately for archival",
                "Track sentiment trends over time",
            ],
            common_workflows=[
                {
                    "name": "Media Monitoring",
                    "steps": [
                        "monitor_media_mentions - Track brand mentions",
                        "capture_press_coverage - Document coverage",
                    ],
                },
            ],
            tool_guides=[
                ToolGuide(
                    tool_name="monitor_media_mentions",
                    description="Monitors media mentions for a brand.",
                    when_to_use=[
                        "Brand reputation monitoring",
                        "PR campaign tracking",
                        "Crisis monitoring",
                    ],
                    input_parameters={
                        "brand_name": "The brand to monitor",
                        "sources": "Media sources to check",
                    },
                    example_usage={
                        "scenario": "Monitor mentions for a client brand",
                        "input": {"brand_name": "Acme Corp", "sources": ["news", "social"]},
                        "expected_output": "List of recent mentions with sentiment",
                    },
                ),
                ToolGuide(
                    tool_name="capture_press_coverage",
                    description="Captures press coverage for documentation.",
                    when_to_use=[
                        "Documenting media wins",
                        "Building press archives",
                        "Client reporting",
                    ],
                    input_parameters={
                        "article_url": "URL of the press coverage",
                        "client_id": "Client this coverage is for",
                    },
                    example_usage={
                        "scenario": "Capture a press article for client",
                        "input": {"article_url": "https://news.example.com/article", "client_id": "client_123"},
                        "expected_output": "Archived screenshot and metadata",
                    },
                ),
            ],
        )
