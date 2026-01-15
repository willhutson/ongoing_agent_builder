"""
LMS Course Definitions

Agent-specific training courses that work across all tenants.
Courses are organized by agent capability, not industry vertical.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class CourseLevel(Enum):
    """Training course difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LessonType(Enum):
    """Types of lesson content."""
    VIDEO = "video"
    INTERACTIVE = "interactive"
    READING = "reading"
    HANDS_ON = "hands_on"
    QUIZ = "quiz"


@dataclass
class TrainingLesson:
    """A single lesson within a training module."""
    id: str
    title: str
    description: str
    lesson_type: LessonType
    duration_minutes: int
    content: dict  # Structured content for the lesson
    order: int = 0

    # Completion tracking
    requires_completion: bool = True
    passing_score: Optional[int] = None  # For quizzes

    # Resources
    resources: list[dict] = field(default_factory=list)


@dataclass
class TrainingModule:
    """A module containing related lessons."""
    id: str
    title: str
    description: str
    lessons: list[TrainingLesson]
    order: int = 0

    # Prerequisites
    prerequisites: list[str] = field(default_factory=list)  # Module IDs

    # Estimated time
    @property
    def total_duration_minutes(self) -> int:
        return sum(l.duration_minutes for l in self.lessons)


@dataclass
class TrainingCourse:
    """A complete training course for an agent."""
    id: str
    agent_id: str  # Links to the agent this course trains on
    title: str
    description: str
    level: CourseLevel
    modules: list[TrainingModule]

    # Metadata
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Course settings
    certificate_on_completion: bool = True
    required_for_agent_access: bool = False  # If true, must complete before using agent

    # Target audience (roles)
    target_roles: list[str] = field(default_factory=list)

    @property
    def total_duration_minutes(self) -> int:
        return sum(m.total_duration_minutes for m in self.modules)

    @property
    def total_lessons(self) -> int:
        return sum(len(m.lessons) for m in self.modules)


# =============================================================================
# Course Definitions - Agent-Specific Training
# =============================================================================

def _get_qa_agent_courses() -> list[TrainingCourse]:
    """QA Agent training courses."""
    return [
        TrainingCourse(
            id="qa_agent_fundamentals",
            agent_id="qa_agent",
            title="QA Agent Fundamentals",
            description="Learn the basics of using the QA Agent for quality assurance tasks.",
            level=CourseLevel.BEGINNER,
            target_roles=["qa_specialist", "project_manager", "account_manager"],
            modules=[
                TrainingModule(
                    id="qa_intro",
                    title="Introduction to QA Agent",
                    description="Overview of QA Agent capabilities and use cases.",
                    order=1,
                    lessons=[
                        TrainingLesson(
                            id="qa_overview",
                            title="What is the QA Agent?",
                            description="Understanding the QA Agent's role in your workflow.",
                            lesson_type=LessonType.VIDEO,
                            duration_minutes=8,
                            order=1,
                            content={
                                "video_url": "/training/videos/qa_overview.mp4",
                                "transcript": "The QA Agent automates quality assurance tasks...",
                                "key_points": [
                                    "Automated page verification",
                                    "Performance and accessibility audits",
                                    "Visual regression testing",
                                    "Screenshot capture for proof of work",
                                ],
                            },
                        ),
                        TrainingLesson(
                            id="qa_capabilities",
                            title="QA Agent Capabilities",
                            description="Deep dive into what the QA Agent can do.",
                            lesson_type=LessonType.INTERACTIVE,
                            duration_minutes=15,
                            order=2,
                            content={
                                "capability_explorer": True,
                                "categories": [
                                    {
                                        "name": "Performance Testing",
                                        "tools": ["run_performance_audit", "check_page_speed", "measure_ttfb"],
                                        "description": "Measure and optimize page load times",
                                    },
                                    {
                                        "name": "Accessibility Testing",
                                        "tools": ["run_accessibility_audit", "check_color_contrast", "verify_alt_text"],
                                        "description": "Ensure WCAG compliance",
                                    },
                                    {
                                        "name": "Mobile Testing",
                                        "tools": ["test_mobile_device", "capture_device_suite", "check_touch_targets"],
                                        "description": "Test across device viewports",
                                    },
                                    {
                                        "name": "SEO Verification",
                                        "tools": ["verify_meta_tags", "check_structured_data", "verify_canonical_url"],
                                        "description": "Verify SEO elements",
                                    },
                                    {
                                        "name": "Link Validation",
                                        "tools": ["check_broken_links", "verify_external_links", "check_link_attributes"],
                                        "description": "Find and fix broken links",
                                    },
                                ],
                            },
                        ),
                        TrainingLesson(
                            id="qa_first_task",
                            title="Your First QA Task",
                            description="Hands-on: Run your first QA check.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=20,
                            order=3,
                            content={
                                "exercise": {
                                    "title": "Verify a Landing Page",
                                    "steps": [
                                        "Navigate to a project in your ERP",
                                        "Open the QA Agent panel",
                                        "Enter a URL to verify",
                                        "Run the 'verify_landing_page' tool",
                                        "Review the results and screenshot",
                                    ],
                                    "success_criteria": "Successfully captured a landing page verification with screenshot",
                                },
                            },
                        ),
                    ],
                ),
                TrainingModule(
                    id="qa_performance",
                    title="Performance Testing",
                    description="Master performance auditing with the QA Agent.",
                    order=2,
                    prerequisites=["qa_intro"],
                    lessons=[
                        TrainingLesson(
                            id="performance_basics",
                            title="Understanding Performance Metrics",
                            description="Learn about Core Web Vitals and performance scoring.",
                            lesson_type=LessonType.READING,
                            duration_minutes=10,
                            order=1,
                            content={
                                "sections": [
                                    {
                                        "title": "Core Web Vitals",
                                        "content": "Core Web Vitals are Google's metrics for page experience...",
                                        "metrics": ["LCP", "FID", "CLS"],
                                    },
                                    {
                                        "title": "Performance Scores",
                                        "content": "The QA Agent calculates scores based on...",
                                    },
                                ],
                            },
                        ),
                        TrainingLesson(
                            id="performance_hands_on",
                            title="Running Performance Audits",
                            description="Hands-on: Run and interpret performance audits.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=25,
                            order=2,
                            content={
                                "exercise": {
                                    "title": "Complete Performance Audit",
                                    "tools_used": ["run_performance_audit", "check_page_speed", "measure_ttfb"],
                                    "steps": [
                                        "Run a full performance audit on a client page",
                                        "Identify the slowest loading elements",
                                        "Check the TTFB to diagnose server issues",
                                        "Document findings in the project",
                                    ],
                                },
                            },
                        ),
                        TrainingLesson(
                            id="performance_quiz",
                            title="Performance Testing Quiz",
                            description="Test your knowledge of performance testing.",
                            lesson_type=LessonType.QUIZ,
                            duration_minutes=10,
                            order=3,
                            passing_score=80,
                            content={
                                "questions": [
                                    {
                                        "question": "What does LCP stand for?",
                                        "options": ["Largest Contentful Paint", "Last Content Paint", "Lazy Content Processing"],
                                        "correct": 0,
                                    },
                                    {
                                        "question": "What is a good TTFB score?",
                                        "options": ["Under 200ms", "Under 1 second", "Under 5 seconds"],
                                        "correct": 0,
                                    },
                                    {
                                        "question": "Which tool measures Time to First Byte?",
                                        "options": ["measure_ttfb", "check_page_speed", "run_performance_audit"],
                                        "correct": 0,
                                    },
                                ],
                            },
                        ),
                    ],
                ),
            ],
        ),
        TrainingCourse(
            id="qa_agent_advanced",
            agent_id="qa_agent",
            title="Advanced QA Agent Techniques",
            description="Master advanced QA workflows including accessibility, cross-browser testing, and automation.",
            level=CourseLevel.ADVANCED,
            target_roles=["qa_specialist", "technical_lead"],
            modules=[
                TrainingModule(
                    id="qa_accessibility_deep",
                    title="Advanced Accessibility Testing",
                    description="Deep dive into WCAG compliance and accessibility auditing.",
                    order=1,
                    lessons=[
                        TrainingLesson(
                            id="wcag_levels",
                            title="WCAG Compliance Levels",
                            description="Understanding A, AA, and AAA compliance.",
                            lesson_type=LessonType.READING,
                            duration_minutes=15,
                            order=1,
                            content={
                                "wcag_breakdown": {
                                    "A": "Basic accessibility requirements",
                                    "AA": "Standard compliance (most common target)",
                                    "AAA": "Enhanced accessibility (not always achievable)",
                                },
                            },
                        ),
                        TrainingLesson(
                            id="a11y_hands_on",
                            title="Accessibility Audit Workflow",
                            description="Run comprehensive accessibility audits.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=30,
                            order=2,
                            content={
                                "exercise": {
                                    "tools_used": [
                                        "run_accessibility_audit",
                                        "check_color_contrast",
                                        "verify_alt_text",
                                        "check_keyboard_navigation",
                                        "check_form_accessibility",
                                    ],
                                },
                            },
                        ),
                    ],
                ),
                TrainingModule(
                    id="qa_cross_browser",
                    title="Cross-Browser & Device Testing",
                    description="Test across browsers and devices.",
                    order=2,
                    lessons=[
                        TrainingLesson(
                            id="device_testing",
                            title="Mobile Device Testing",
                            description="Test responsiveness across devices.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=25,
                            order=1,
                            content={
                                "exercise": {
                                    "tools_used": ["test_mobile_device", "capture_device_suite", "check_touch_targets"],
                                    "devices": ["iphone_se", "iphone_14_pro", "pixel_7", "ipad_mini"],
                                },
                            },
                        ),
                    ],
                ),
            ],
        ),
    ]


def _get_campaign_agent_courses() -> list[TrainingCourse]:
    """Campaign Agent training courses."""
    return [
        TrainingCourse(
            id="campaign_agent_fundamentals",
            agent_id="campaign_agent",
            title="Campaign Agent Fundamentals",
            description="Learn to use the Campaign Agent for campaign verification and asset management.",
            level=CourseLevel.BEGINNER,
            target_roles=["campaign_manager", "account_manager", "media_buyer"],
            modules=[
                TrainingModule(
                    id="campaign_intro",
                    title="Introduction to Campaign Agent",
                    description="Overview of Campaign Agent capabilities.",
                    order=1,
                    lessons=[
                        TrainingLesson(
                            id="campaign_overview",
                            title="Campaign Agent Overview",
                            description="What the Campaign Agent does and when to use it.",
                            lesson_type=LessonType.VIDEO,
                            duration_minutes=10,
                            order=1,
                            content={
                                "key_capabilities": [
                                    "Landing page verification",
                                    "A/B test variant capture",
                                    "UTM parameter validation",
                                    "Email preview testing",
                                    "Social asset verification",
                                    "Redirect chain analysis",
                                ],
                            },
                        ),
                        TrainingLesson(
                            id="campaign_verification",
                            title="Pre-Launch Verification",
                            description="Verify campaigns before they go live.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=20,
                            order=2,
                            content={
                                "exercise": {
                                    "title": "Pre-Launch Checklist",
                                    "tools_used": [
                                        "verify_landing_page",
                                        "validate_utm_parameters",
                                        "check_redirect_chain",
                                    ],
                                },
                            },
                        ),
                    ],
                ),
                TrainingModule(
                    id="campaign_ab_testing",
                    title="A/B Test Documentation",
                    description="Capture and compare A/B test variants.",
                    order=2,
                    lessons=[
                        TrainingLesson(
                            id="ab_capture",
                            title="Capturing A/B Variants",
                            description="Document test variants for analysis.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=15,
                            order=1,
                            content={
                                "exercise": {
                                    "tools_used": ["capture_ab_variants", "capture_multivariate"],
                                },
                            },
                        ),
                    ],
                ),
            ],
        ),
    ]


def _get_competitor_agent_courses() -> list[TrainingCourse]:
    """Competitor Agent training courses."""
    return [
        TrainingCourse(
            id="competitor_agent_fundamentals",
            agent_id="competitor_agent",
            title="Competitor Agent Fundamentals",
            description="Learn competitive intelligence gathering with the Competitor Agent.",
            level=CourseLevel.BEGINNER,
            target_roles=["strategist", "account_manager", "leadership"],
            modules=[
                TrainingModule(
                    id="competitor_intro",
                    title="Introduction to Competitor Agent",
                    description="Overview of competitive intelligence capabilities.",
                    order=1,
                    lessons=[
                        TrainingLesson(
                            id="competitor_overview",
                            title="Competitor Agent Overview",
                            description="Understanding competitive intelligence automation.",
                            lesson_type=LessonType.VIDEO,
                            duration_minutes=10,
                            order=1,
                            content={
                                "key_capabilities": [
                                    "Website analysis",
                                    "Ad library capture",
                                    "Change monitoring",
                                    "Technology detection",
                                ],
                            },
                        ),
                        TrainingLesson(
                            id="competitor_analysis",
                            title="Running Competitor Analysis",
                            description="Analyze a competitor website.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=25,
                            order=2,
                            content={
                                "exercise": {
                                    "tools_used": [
                                        "analyze_competitor",
                                        "capture_competitor_ads",
                                        "monitor_competitor_changes",
                                    ],
                                },
                            },
                        ),
                    ],
                ),
            ],
        ),
    ]


def _get_legal_agent_courses() -> list[TrainingCourse]:
    """Legal Agent training courses."""
    return [
        TrainingCourse(
            id="legal_agent_fundamentals",
            agent_id="legal_agent",
            title="Legal Agent Fundamentals",
            description="Learn compliance verification with the Legal Agent.",
            level=CourseLevel.BEGINNER,
            target_roles=["compliance_officer", "account_manager", "leadership"],
            modules=[
                TrainingModule(
                    id="legal_intro",
                    title="Introduction to Legal Agent",
                    description="Overview of compliance verification capabilities.",
                    order=1,
                    lessons=[
                        TrainingLesson(
                            id="legal_overview",
                            title="Legal Agent Overview",
                            description="Understanding compliance automation.",
                            lesson_type=LessonType.VIDEO,
                            duration_minutes=10,
                            order=1,
                            content={
                                "key_capabilities": [
                                    "GDPR compliance verification",
                                    "Cookie banner analysis",
                                    "FTC ad disclosure checks",
                                    "Privacy policy monitoring",
                                ],
                            },
                        ),
                        TrainingLesson(
                            id="gdpr_verification",
                            title="GDPR Compliance Checks",
                            description="Verify GDPR compliance elements.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=20,
                            order=2,
                            content={
                                "exercise": {
                                    "tools_used": [
                                        "verify_gdpr_compliance",
                                        "analyze_cookie_banner",
                                        "detect_policy_changes",
                                    ],
                                },
                            },
                        ),
                    ],
                ),
            ],
        ),
    ]


def _get_report_agent_courses() -> list[TrainingCourse]:
    """Report Agent training courses."""
    return [
        TrainingCourse(
            id="report_agent_fundamentals",
            agent_id="report_agent",
            title="Report Agent Fundamentals",
            description="Learn automated reporting with the Report Agent.",
            level=CourseLevel.BEGINNER,
            target_roles=["analyst", "account_manager", "leadership"],
            modules=[
                TrainingModule(
                    id="report_intro",
                    title="Introduction to Report Agent",
                    description="Overview of automated reporting capabilities.",
                    order=1,
                    lessons=[
                        TrainingLesson(
                            id="report_overview",
                            title="Report Agent Overview",
                            description="Understanding automated dashboard capture.",
                            lesson_type=LessonType.VIDEO,
                            duration_minutes=10,
                            order=1,
                            content={
                                "key_capabilities": [
                                    "GA4 dashboard capture",
                                    "Facebook Ads Manager capture",
                                    "PDF report generation",
                                    "Multi-dashboard comparison",
                                ],
                            },
                        ),
                        TrainingLesson(
                            id="dashboard_capture",
                            title="Capturing Analytics Dashboards",
                            description="Capture dashboards for client reports.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=25,
                            order=2,
                            content={
                                "exercise": {
                                    "tools_used": [
                                        "capture_ga4_dashboard",
                                        "capture_facebook_ads_manager",
                                        "generate_dashboard_pdf",
                                    ],
                                },
                            },
                        ),
                    ],
                ),
            ],
        ),
    ]


def _get_pr_agent_courses() -> list[TrainingCourse]:
    """PR Agent training courses."""
    return [
        TrainingCourse(
            id="pr_agent_fundamentals",
            agent_id="pr_agent",
            title="PR Agent Fundamentals",
            description="Learn media monitoring with the PR Agent.",
            level=CourseLevel.BEGINNER,
            target_roles=["pr_manager", "account_manager", "leadership"],
            modules=[
                TrainingModule(
                    id="pr_intro",
                    title="Introduction to PR Agent",
                    description="Overview of media monitoring capabilities.",
                    order=1,
                    lessons=[
                        TrainingLesson(
                            id="pr_overview",
                            title="PR Agent Overview",
                            description="Understanding media monitoring automation.",
                            lesson_type=LessonType.VIDEO,
                            duration_minutes=10,
                            order=1,
                            content={
                                "key_capabilities": [
                                    "Media mention monitoring",
                                    "Press coverage capture",
                                    "Brand sentiment tracking",
                                ],
                            },
                        ),
                    ],
                ),
            ],
        ),
    ]


def _get_orchestration_courses() -> list[TrainingCourse]:
    """Workflow orchestration training courses."""
    return [
        TrainingCourse(
            id="orchestration_fundamentals",
            agent_id="orchestration",  # Special ID for multi-agent training
            title="Multi-Agent Workflow Orchestration",
            description="Learn to combine agents into powerful automated workflows.",
            level=CourseLevel.INTERMEDIATE,
            target_roles=["project_manager", "technical_lead", "operations"],
            modules=[
                TrainingModule(
                    id="orchestration_intro",
                    title="Introduction to Workflows",
                    description="Understanding multi-agent orchestration.",
                    order=1,
                    lessons=[
                        TrainingLesson(
                            id="workflow_concepts",
                            title="Workflow Concepts",
                            description="Understanding how agents work together.",
                            lesson_type=LessonType.VIDEO,
                            duration_minutes=15,
                            order=1,
                            content={
                                "concepts": [
                                    "Sequential execution",
                                    "Parallel execution",
                                    "Conditional steps",
                                    "Human review checkpoints",
                                    "Context passing",
                                ],
                            },
                        ),
                        TrainingLesson(
                            id="workflow_templates",
                            title="Using Workflow Templates",
                            description="Pre-built workflows for common tasks.",
                            lesson_type=LessonType.INTERACTIVE,
                            duration_minutes=20,
                            order=2,
                            content={
                                "templates": [
                                    "campaign_launch_checklist",
                                    "competitive_analysis",
                                    "client_monthly_report",
                                    "content_approval",
                                    "gdpr_compliance_audit",
                                ],
                            },
                        ),
                        TrainingLesson(
                            id="run_workflow",
                            title="Running Your First Workflow",
                            description="Execute a multi-agent workflow.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=30,
                            order=3,
                            content={
                                "exercise": {
                                    "workflow": "campaign_launch_checklist",
                                    "steps": [
                                        "Select a campaign to verify",
                                        "Choose the campaign_launch_checklist workflow",
                                        "Review the workflow steps",
                                        "Execute the workflow",
                                        "Review results from each agent",
                                    ],
                                },
                            },
                        ),
                    ],
                ),
                TrainingModule(
                    id="orchestration_advanced",
                    title="Building Custom Workflows",
                    description="Create your own multi-agent workflows.",
                    order=2,
                    prerequisites=["orchestration_intro"],
                    lessons=[
                        TrainingLesson(
                            id="workflow_builder",
                            title="Using the Workflow Builder",
                            description="Build custom workflows programmatically.",
                            lesson_type=LessonType.HANDS_ON,
                            duration_minutes=40,
                            order=1,
                            content={
                                "exercise": {
                                    "title": "Build a Custom Workflow",
                                    "workflow_steps": [
                                        "Define workflow objectives",
                                        "Select agents and tools",
                                        "Configure input mappings",
                                        "Set up step connections",
                                        "Add human review points",
                                        "Test the workflow",
                                    ],
                                },
                            },
                        ),
                    ],
                ),
            ],
        ),
    ]


# =============================================================================
# Course Registry
# =============================================================================

_ALL_COURSES: list[TrainingCourse] = []


def _initialize_courses():
    """Initialize all courses."""
    global _ALL_COURSES
    _ALL_COURSES = [
        *_get_qa_agent_courses(),
        *_get_campaign_agent_courses(),
        *_get_competitor_agent_courses(),
        *_get_legal_agent_courses(),
        *_get_report_agent_courses(),
        *_get_pr_agent_courses(),
        *_get_orchestration_courses(),
    ]


def get_all_courses() -> list[TrainingCourse]:
    """Get all available training courses."""
    if not _ALL_COURSES:
        _initialize_courses()
    return _ALL_COURSES


def get_course_by_id(course_id: str) -> Optional[TrainingCourse]:
    """Get a specific course by ID."""
    for course in get_all_courses():
        if course.id == course_id:
            return course
    return None


def get_courses_for_agent(agent_id: str) -> list[TrainingCourse]:
    """Get all courses for a specific agent."""
    return [c for c in get_all_courses() if c.agent_id == agent_id]


def get_courses_for_role(role: str) -> list[TrainingCourse]:
    """Get courses recommended for a specific role."""
    return [c for c in get_all_courses() if role in c.target_roles]


def get_courses_by_level(level: CourseLevel) -> list[TrainingCourse]:
    """Get courses at a specific difficulty level."""
    return [c for c in get_all_courses() if c.level == level]
