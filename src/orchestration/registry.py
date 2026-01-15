"""
Agent Registry

Provides capability discovery and agent metadata for the orchestration system.
Agents register their capabilities, allowing workflows to dynamically
select the right agent for each task.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


class CapabilityCategory(Enum):
    """Categories of agent capabilities."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CONTENT = "content"
    VERIFICATION = "verification"
    CAPTURE = "capture"
    COMPLIANCE = "compliance"
    REPORTING = "reporting"
    MONITORING = "monitoring"
    COMMUNICATION = "communication"


@dataclass
class AgentCapability:
    """
    Describes a single capability (tool) an agent provides.
    """
    tool_name: str
    description: str
    category: CapabilityCategory
    input_schema: dict
    output_schema: dict = field(default_factory=dict)

    # What this capability is best for
    use_cases: list[str] = field(default_factory=list)

    # Example prompts that would use this capability
    example_prompts: list[str] = field(default_factory=list)

    # Estimated execution time
    avg_duration_seconds: int = 30

    # Whether this requires browser automation
    requires_browser: bool = False

    # Whether this requires authentication
    requires_auth: bool = False

    # Cost tier (for budgeting)
    cost_tier: str = "standard"  # standard, premium, enterprise


@dataclass
class AgentInfo:
    """
    Complete information about an agent.
    """
    agent_id: str
    name: str
    description: str
    capabilities: list[AgentCapability]

    # Agent category
    category: str = "general"

    # What roles typically use this agent
    typical_users: list[str] = field(default_factory=list)

    # ERP modules this agent integrates with
    erp_modules: list[str] = field(default_factory=list)

    # Icon for UI
    icon: str = "bot"

    # Color theme for UI
    color: str = "blue"

    def get_capability(self, tool_name: str) -> Optional[AgentCapability]:
        """Get a specific capability by tool name."""
        for cap in self.capabilities:
            if cap.tool_name == tool_name:
                return cap
        return None

    def get_capabilities_by_category(self, category: CapabilityCategory) -> list[AgentCapability]:
        """Get all capabilities in a category."""
        return [c for c in self.capabilities if c.category == category]


class AgentRegistry:
    """
    Central registry of all available agents and their capabilities.

    Used by the orchestrator to:
    - Discover available agents
    - Find agents with specific capabilities
    - Get input/output schemas for workflow validation
    - Provide capability information to the UI
    """

    def __init__(self):
        self._agents: dict[str, AgentInfo] = {}
        self._capability_index: dict[str, list[str]] = {}  # capability -> agent_ids
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize the registry with all SpokeStack agents."""

        # =====================================================================
        # QA Agent
        # =====================================================================
        self.register_agent(AgentInfo(
            agent_id="qa_agent",
            name="QA Agent",
            description="Comprehensive quality assurance for digital marketing deliverables",
            category="verification",
            typical_users=["qa_specialist", "project_manager", "account_manager"],
            erp_modules=["projects", "deliverables", "campaigns"],
            icon="clipboard-check",
            color="green",
            capabilities=[
                AgentCapability(
                    tool_name="run_performance_audit",
                    description="Run Lighthouse-style performance audit on a page",
                    category=CapabilityCategory.ANALYSIS,
                    input_schema={"url": "string", "categories": "array"},
                    use_cases=["Pre-launch checks", "Performance optimization", "Client reporting"],
                    example_prompts=["Check the performance of our landing page", "Run a Lighthouse audit"],
                    requires_browser=True,
                    avg_duration_seconds=45,
                ),
                AgentCapability(
                    tool_name="run_accessibility_audit",
                    description="Run WCAG accessibility compliance audit",
                    category=CapabilityCategory.COMPLIANCE,
                    input_schema={"url": "string", "wcag_level": "string"},
                    use_cases=["ADA compliance", "Accessibility certification", "Inclusive design verification"],
                    example_prompts=["Check accessibility compliance", "Is this page WCAG AA compliant?"],
                    requires_browser=True,
                    avg_duration_seconds=30,
                ),
                AgentCapability(
                    tool_name="verify_meta_tags",
                    description="Verify SEO meta tags (title, description, OG tags)",
                    category=CapabilityCategory.VERIFICATION,
                    input_schema={"url": "string"},
                    use_cases=["SEO verification", "Social sharing preview", "Search optimization"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="check_broken_links",
                    description="Find broken links on a page",
                    category=CapabilityCategory.VERIFICATION,
                    input_schema={"url": "string", "include_external": "boolean"},
                    use_cases=["Pre-launch checks", "Site maintenance", "SEO health"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="capture_device_suite",
                    description="Capture page across multiple device viewports",
                    category=CapabilityCategory.CAPTURE,
                    input_schema={"url": "string", "devices": "array"},
                    use_cases=["Responsive testing", "Client presentations", "Design QA"],
                    requires_browser=True,
                    avg_duration_seconds=60,
                ),
            ],
        ))

        # =====================================================================
        # Campaign Agent
        # =====================================================================
        self.register_agent(AgentInfo(
            agent_id="campaign_agent",
            name="Campaign Agent",
            description="Campaign management and asset verification",
            category="management",
            typical_users=["campaign_manager", "account_manager", "media_buyer"],
            erp_modules=["campaigns", "projects", "assets"],
            icon="megaphone",
            color="purple",
            capabilities=[
                AgentCapability(
                    tool_name="capture_ab_variants",
                    description="Capture A/B test variants side-by-side",
                    category=CapabilityCategory.CAPTURE,
                    input_schema={"variant_a_url": "string", "variant_b_url": "string", "test_name": "string"},
                    use_cases=["A/B test documentation", "Variant comparison", "Test analysis"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="verify_landing_page",
                    description="Verify campaign landing page is live and correct",
                    category=CapabilityCategory.VERIFICATION,
                    input_schema={"url": "string", "expected_content": "array"},
                    use_cases=["Pre-launch verification", "Campaign QA", "Client approval"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="validate_utm_parameters",
                    description="Validate UTM parameters in landing page URL",
                    category=CapabilityCategory.VERIFICATION,
                    input_schema={"url": "string", "expected_utms": "object"},
                    use_cases=["Campaign tracking", "Attribution verification", "Analytics setup"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="check_redirect_chain",
                    description="Check redirect chain for a URL",
                    category=CapabilityCategory.VERIFICATION,
                    input_schema={"url": "string"},
                    use_cases=["Link validation", "Tracking verification", "Performance optimization"],
                    requires_browser=True,
                ),
            ],
        ))

        # =====================================================================
        # Competitor Agent
        # =====================================================================
        self.register_agent(AgentInfo(
            agent_id="competitor_agent",
            name="Competitor Agent",
            description="Competitive intelligence and market analysis",
            category="research",
            typical_users=["strategist", "account_manager", "leadership"],
            erp_modules=["clients", "strategy", "reports"],
            icon="search",
            color="orange",
            capabilities=[
                AgentCapability(
                    tool_name="analyze_competitor",
                    description="Comprehensive competitor website analysis",
                    category=CapabilityCategory.ANALYSIS,
                    input_schema={"url": "string", "analysis_depth": "string"},
                    use_cases=["Competitive analysis", "Market research", "Strategy development"],
                    requires_browser=True,
                    avg_duration_seconds=60,
                ),
                AgentCapability(
                    tool_name="capture_competitor_ads",
                    description="Capture competitor advertising on Meta Ad Library",
                    category=CapabilityCategory.CAPTURE,
                    input_schema={"competitor_name": "string", "platform": "string"},
                    use_cases=["Ad intelligence", "Creative inspiration", "Competitive benchmarking"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="monitor_competitor_changes",
                    description="Detect changes on competitor websites",
                    category=CapabilityCategory.MONITORING,
                    input_schema={"url": "string", "baseline_date": "string"},
                    use_cases=["Competitive monitoring", "Market tracking", "Strategy updates"],
                    requires_browser=True,
                ),
            ],
        ))

        # =====================================================================
        # Legal Agent
        # =====================================================================
        self.register_agent(AgentInfo(
            agent_id="legal_agent",
            name="Legal Agent",
            description="Legal compliance and policy verification",
            category="compliance",
            typical_users=["compliance_officer", "account_manager", "leadership"],
            erp_modules=["clients", "deliverables", "compliance"],
            icon="scale",
            color="red",
            capabilities=[
                AgentCapability(
                    tool_name="verify_gdpr_compliance",
                    description="Verify GDPR compliance elements on a page",
                    category=CapabilityCategory.COMPLIANCE,
                    input_schema={"url": "string", "check_items": "array"},
                    use_cases=["GDPR compliance", "Privacy verification", "Client protection"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="analyze_cookie_banner",
                    description="Analyze cookie consent implementation",
                    category=CapabilityCategory.COMPLIANCE,
                    input_schema={"url": "string"},
                    use_cases=["Cookie compliance", "Privacy audit", "Legal review"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="check_ad_disclosure",
                    description="Verify FTC ad disclosure requirements",
                    category=CapabilityCategory.COMPLIANCE,
                    input_schema={"url": "string", "ad_type": "string"},
                    use_cases=["FTC compliance", "Influencer verification", "Ad review"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="detect_policy_changes",
                    description="Detect changes to terms of service or privacy policy",
                    category=CapabilityCategory.MONITORING,
                    input_schema={"url": "string", "policy_type": "string"},
                    use_cases=["Policy monitoring", "Compliance tracking", "Risk management"],
                    requires_browser=True,
                ),
            ],
        ))

        # =====================================================================
        # Report Agent
        # =====================================================================
        self.register_agent(AgentInfo(
            agent_id="report_agent",
            name="Report Agent",
            description="Analytics dashboard capture and reporting",
            category="reporting",
            typical_users=["analyst", "account_manager", "leadership"],
            erp_modules=["reports", "clients", "dashboards"],
            icon="chart-bar",
            color="blue",
            capabilities=[
                AgentCapability(
                    tool_name="capture_ga4_dashboard",
                    description="Capture Google Analytics 4 dashboard",
                    category=CapabilityCategory.CAPTURE,
                    input_schema={"property_id": "string", "report_type": "string", "date_range": "string"},
                    use_cases=["Client reporting", "Performance tracking", "Analytics documentation"],
                    requires_browser=True,
                    requires_auth=True,
                    avg_duration_seconds=45,
                ),
                AgentCapability(
                    tool_name="capture_facebook_ads_manager",
                    description="Capture Facebook Ads Manager dashboard",
                    category=CapabilityCategory.CAPTURE,
                    input_schema={"account_id": "string", "date_range": "string"},
                    use_cases=["Ad performance reporting", "Client updates", "Campaign analysis"],
                    requires_browser=True,
                    requires_auth=True,
                ),
                AgentCapability(
                    tool_name="generate_dashboard_pdf",
                    description="Generate PDF from dashboard capture",
                    category=CapabilityCategory.REPORTING,
                    input_schema={"url": "string", "report_name": "string"},
                    use_cases=["Client deliverables", "Report generation", "Documentation"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="capture_multi_dashboard",
                    description="Capture multiple dashboards for comparison",
                    category=CapabilityCategory.CAPTURE,
                    input_schema={"dashboard_urls": "array", "comparison_name": "string"},
                    use_cases=["Multi-channel reporting", "Performance comparison", "Executive summaries"],
                    requires_browser=True,
                    avg_duration_seconds=120,
                ),
            ],
        ))

        # =====================================================================
        # PR Agent
        # =====================================================================
        self.register_agent(AgentInfo(
            agent_id="pr_agent",
            name="PR Agent",
            description="Public relations and media monitoring",
            category="communication",
            typical_users=["pr_manager", "account_manager", "leadership"],
            erp_modules=["clients", "media", "campaigns"],
            icon="newspaper",
            color="teal",
            capabilities=[
                AgentCapability(
                    tool_name="monitor_media_mentions",
                    description="Monitor media mentions for a brand",
                    category=CapabilityCategory.MONITORING,
                    input_schema={"brand_name": "string", "sources": "array"},
                    use_cases=["Media monitoring", "Brand tracking", "PR measurement"],
                    requires_browser=True,
                ),
                AgentCapability(
                    tool_name="capture_press_coverage",
                    description="Capture press coverage for documentation",
                    category=CapabilityCategory.CAPTURE,
                    input_schema={"article_url": "string", "client_id": "string"},
                    use_cases=["Coverage documentation", "Client reporting", "PR archive"],
                    requires_browser=True,
                ),
            ],
        ))

    def register_agent(self, agent: AgentInfo):
        """Register an agent and index its capabilities."""
        self._agents[agent.agent_id] = agent

        # Index capabilities for fast lookup
        for capability in agent.capabilities:
            if capability.tool_name not in self._capability_index:
                self._capability_index[capability.tool_name] = []
            self._capability_index[capability.tool_name].append(agent.agent_id)

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent info by ID."""
        return self._agents.get(agent_id)

    def get_all_agents(self) -> list[AgentInfo]:
        """Get all registered agents."""
        return list(self._agents.values())

    def find_agents_with_capability(self, tool_name: str) -> list[AgentInfo]:
        """Find all agents that have a specific capability."""
        agent_ids = self._capability_index.get(tool_name, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def find_agents_by_category(self, category: str) -> list[AgentInfo]:
        """Find all agents in a category."""
        return [a for a in self._agents.values() if a.category == category]

    def find_agents_for_module(self, module: str) -> list[AgentInfo]:
        """Find all agents that integrate with an ERP module."""
        return [a for a in self._agents.values() if module in a.erp_modules]

    def find_capabilities_by_category(self, category: CapabilityCategory) -> list[tuple[AgentInfo, AgentCapability]]:
        """Find all capabilities in a category across all agents."""
        results = []
        for agent in self._agents.values():
            for cap in agent.get_capabilities_by_category(category):
                results.append((agent, cap))
        return results

    def get_capability_schema(self, agent_id: str, tool_name: str) -> Optional[dict]:
        """Get the input schema for a specific capability."""
        agent = self.get_agent(agent_id)
        if agent:
            cap = agent.get_capability(tool_name)
            if cap:
                return cap.input_schema
        return None

    def search_capabilities(self, query: str) -> list[tuple[AgentInfo, AgentCapability]]:
        """Search capabilities by keyword."""
        query_lower = query.lower()
        results = []
        for agent in self._agents.values():
            for cap in agent.capabilities:
                if (query_lower in cap.tool_name.lower() or
                    query_lower in cap.description.lower() or
                    any(query_lower in uc.lower() for uc in cap.use_cases)):
                    results.append((agent, cap))
        return results

    def to_dict(self) -> dict:
        """Export registry as dictionary for API/UI consumption."""
        return {
            "agents": [
                {
                    "id": a.agent_id,
                    "name": a.name,
                    "description": a.description,
                    "category": a.category,
                    "icon": a.icon,
                    "color": a.color,
                    "erp_modules": a.erp_modules,
                    "typical_users": a.typical_users,
                    "capabilities": [
                        {
                            "tool_name": c.tool_name,
                            "description": c.description,
                            "category": c.category.value,
                            "use_cases": c.use_cases,
                            "requires_browser": c.requires_browser,
                            "avg_duration_seconds": c.avg_duration_seconds,
                        }
                        for c in a.capabilities
                    ],
                }
                for a in self._agents.values()
            ]
        }


# Singleton instance
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
