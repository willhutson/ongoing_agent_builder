"""
AgentFactory: Runtime Agent Assembly for Multi-Tenant SpokeStack

Assembles agents at runtime by:
1. Loading core agent class (Layer 1)
2. Applying instance configuration (Layer 2)
3. Injecting custom skills (Layer 3)
4. Merging tuning from all three tiers
"""

from typing import Optional, Type, Any
from uuid import UUID
import anthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..config import get_settings
from ..db.models import (
    Instance,
    InstanceAgentConfig,
    InstanceSkill,
    InstanceVersionConfig,
    AgentVersion,
)
from ..agents import (
    # Foundation
    RFPAgent, BriefAgent, ContentAgent, CommercialAgent,
    # Studio
    PresentationAgent, CopyAgent, ImageAgent,
    # Video
    VideoScriptAgent, VideoStoryboardAgent, VideoProductionAgent,
    # Distribution
    ReportAgent, ApproveAgent, BriefUpdateAgent,
    # Gateways
    WhatsAppGateway, EmailGateway, SlackGateway, SMSGateway,
    # Brand
    BrandVoiceAgent, BrandVisualAgent, BrandGuidelinesAgent,
    # Operations
    ResourceAgent, WorkflowAgent, OpsReportingAgent,
    # Client
    CRMAgent, ScopeAgent, OnboardingAgent, InstanceOnboardingAgent,
    InstanceAnalyticsAgent, InstanceSuccessAgent,
    # Media
    MediaBuyingAgent, CampaignAgent,
    # Social
    SocialListeningAgent, CommunityAgent, SocialAnalyticsAgent,
    # Performance
    BrandPerformanceAgent, CampaignAnalyticsAgent, CompetitorAgent,
    # Finance
    InvoiceAgent, ForecastAgent, BudgetAgent,
    # Quality
    QAAgent, LegalAgent,
    # Knowledge
    KnowledgeAgent, TrainingAgent,
    # Specialized
    InfluencerAgent, PRAgent, EventsAgent, LocalizationAgent, AccessibilityAgent,
    # Meta
    PromptHelperAgent,
)
from .prompt_assembler import PromptAssembler
from .skill_executor import SkillExecutor


# Agent type to class mapping
AGENT_REGISTRY: dict[str, Type] = {
    # Foundation
    "rfp": RFPAgent,
    "brief": BriefAgent,
    "content": ContentAgent,
    "commercial": CommercialAgent,
    # Studio
    "presentation": PresentationAgent,
    "copy": CopyAgent,
    "image": ImageAgent,
    # Video
    "video_script": VideoScriptAgent,
    "video_storyboard": VideoStoryboardAgent,
    "video_production": VideoProductionAgent,
    # Distribution
    "report": ReportAgent,
    "approve": ApproveAgent,
    "brief_update": BriefUpdateAgent,
    # Gateways
    "gateway_whatsapp": WhatsAppGateway,
    "gateway_email": EmailGateway,
    "gateway_slack": SlackGateway,
    "gateway_sms": SMSGateway,
    # Brand
    "brand_voice": BrandVoiceAgent,
    "brand_visual": BrandVisualAgent,
    "brand_guidelines": BrandGuidelinesAgent,
    # Operations
    "resource": ResourceAgent,
    "workflow": WorkflowAgent,
    "ops_reporting": OpsReportingAgent,
    # Client
    "crm": CRMAgent,
    "scope": ScopeAgent,
    "onboarding": OnboardingAgent,
    "instance_onboarding": InstanceOnboardingAgent,
    "instance_analytics": InstanceAnalyticsAgent,
    "instance_success": InstanceSuccessAgent,
    # Media
    "media_buying": MediaBuyingAgent,
    "campaign": CampaignAgent,
    # Social
    "social_listening": SocialListeningAgent,
    "community": CommunityAgent,
    "social_analytics": SocialAnalyticsAgent,
    # Performance
    "brand_performance": BrandPerformanceAgent,
    "campaign_analytics": CampaignAnalyticsAgent,
    "competitor": CompetitorAgent,
    # Finance
    "invoice": InvoiceAgent,
    "forecast": ForecastAgent,
    "budget": BudgetAgent,
    # Quality
    "qa": QAAgent,
    "legal": LegalAgent,
    # Knowledge
    "knowledge": KnowledgeAgent,
    "training": TrainingAgent,
    # Specialized
    "influencer": InfluencerAgent,
    "pr": PRAgent,
    "events": EventsAgent,
    "localization": LocalizationAgent,
    "accessibility": AccessibilityAgent,
    # Meta
    "prompt_helper": PromptHelperAgent,
}


class AgentFactory:
    """
    Factory for creating runtime-configured agents.

    Handles the three-layer architecture:
    - Layer 1: Core agent code (from AGENT_REGISTRY)
    - Layer 2: Instance configuration (from database)
    - Layer 3: Custom skills (from database, executed via webhook)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.prompt_assembler = PromptAssembler(db)
        self.skill_executor = SkillExecutor(db)

    async def create_agent(
        self,
        agent_type: str,
        instance_id: UUID,
        client_id: Optional[UUID] = None,
        # Override defaults
        language: Optional[str] = None,
        vertical: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Any:
        """
        Create a fully-configured agent for an instance.

        Args:
            agent_type: Type of agent to create (e.g., "copy", "media_buying")
            instance_id: Instance (tenant) ID
            client_id: Optional client ID for client-specific tuning
            language: Override default language
            vertical: Override default vertical
            region: Override default region

        Returns:
            Configured agent instance ready to execute
        """
        # Validate agent type
        if agent_type not in AGENT_REGISTRY:
            raise ValueError(f"Unknown agent type: {agent_type}")

        # Load instance and configuration
        instance = await self._load_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance not found: {instance_id}")

        if not instance.is_active:
            raise ValueError(f"Instance is inactive: {instance_id}")

        # Get agent-specific config for this instance
        agent_config = await self._get_agent_config(instance_id, agent_type)

        # Check if agent is enabled for this instance
        if agent_config and not agent_config.enabled:
            raise ValueError(f"Agent {agent_type} is disabled for instance {instance_id}")

        # Determine version to use
        version = await self._get_agent_version(instance_id, agent_type)

        # Assemble the prompt (merges all three tiers)
        assembled_prompt = await self.prompt_assembler.assemble(
            agent_type=agent_type,
            instance_id=instance_id,
            client_id=client_id,
        )

        # Get custom skills for this instance
        skills = await self._get_instance_skills(instance_id, agent_type)

        # Create the agent
        agent_class = AGENT_REGISTRY[agent_type]
        client = anthropic.AsyncAnthropic(api_key=self.settings.anthropic_api_key)

        # Build kwargs with overrides
        agent_kwargs = {
            "client": client,
            "model": self.settings.claude_model,
            "erp_base_url": self.settings.erp_api_base_url,
            "erp_api_key": self.settings.erp_api_key,
        }

        # Apply instance defaults (can be overridden by explicit params)
        if agent_config:
            if not language and agent_config.default_language:
                language = agent_config.default_language
            if not vertical and agent_config.default_vertical:
                vertical = agent_config.default_vertical
            if not region and agent_config.default_region:
                region = agent_config.default_region

            # Apply behavior overrides
            if agent_config.max_tokens:
                agent_kwargs["max_tokens"] = agent_config.max_tokens
            if agent_config.temperature is not None:
                agent_kwargs["temperature"] = agent_config.temperature

        # Add specialization params if supported by agent
        if language:
            agent_kwargs["language"] = language
        if vertical:
            agent_kwargs["vertical"] = vertical
        if region:
            agent_kwargs["region"] = region
        if client_id:
            agent_kwargs["client_id"] = str(client_id)

        # Create base agent
        agent = agent_class(**agent_kwargs)

        # Inject assembled prompt
        agent._assembled_prompt = assembled_prompt

        # Inject custom skills as tools
        if skills:
            agent._custom_skills = skills
            agent._skill_executor = self.skill_executor

        # Inject disabled tools list
        if agent_config and agent_config.disabled_tools:
            agent._disabled_tools = agent_config.disabled_tools

        # Store context for tracking
        agent._instance_id = instance_id
        agent._client_id = client_id
        agent._agent_version = version

        return agent

    async def _load_instance(self, instance_id: UUID) -> Optional[Instance]:
        """Load instance with related configs."""
        result = await self.db.execute(
            select(Instance)
            .where(Instance.id == instance_id)
            .options(
                selectinload(Instance.agent_configs),
                selectinload(Instance.version_config),
                selectinload(Instance.tuning_config),
            )
        )
        return result.scalar_one_or_none()

    async def _get_agent_config(
        self, instance_id: UUID, agent_type: str
    ) -> Optional[InstanceAgentConfig]:
        """Get instance-specific config for an agent type."""
        result = await self.db.execute(
            select(InstanceAgentConfig)
            .where(
                InstanceAgentConfig.instance_id == instance_id,
                InstanceAgentConfig.agent_type == agent_type,
            )
        )
        return result.scalar_one_or_none()

    async def _get_agent_version(
        self, instance_id: UUID, agent_type: str
    ) -> Optional[str]:
        """
        Determine which version of an agent to use.
        Respects version pinning if configured.
        """
        # Check for pinned version
        result = await self.db.execute(
            select(InstanceVersionConfig)
            .where(InstanceVersionConfig.instance_id == instance_id)
        )
        version_config = result.scalar_one_or_none()

        if version_config and version_config.pinned_versions:
            pinned = version_config.pinned_versions.get(agent_type)
            if pinned:
                return pinned

        # Get latest stable version
        result = await self.db.execute(
            select(AgentVersion)
            .where(
                AgentVersion.agent_type == agent_type,
                AgentVersion.is_stable == True,
                AgentVersion.is_deprecated == False,
            )
            .order_by(AgentVersion.released_at.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        return latest.version if latest else "1.0.0"

    async def _get_instance_skills(
        self, instance_id: UUID, agent_type: str
    ) -> list[InstanceSkill]:
        """Get custom skills available for this agent in this instance."""
        result = await self.db.execute(
            select(InstanceSkill)
            .where(
                InstanceSkill.instance_id == instance_id,
                InstanceSkill.is_active == True,
            )
        )
        skills = result.scalars().all()

        # Filter to skills that apply to this agent type
        return [
            skill for skill in skills
            if not skill.agent_types or agent_type in skill.agent_types
        ]

    @staticmethod
    def list_agent_types() -> list[str]:
        """List all available agent types."""
        return list(AGENT_REGISTRY.keys())

    @staticmethod
    def get_agent_info(agent_type: str) -> dict:
        """Get information about an agent type."""
        if agent_type not in AGENT_REGISTRY:
            raise ValueError(f"Unknown agent type: {agent_type}")

        agent_class = AGENT_REGISTRY[agent_type]
        return {
            "type": agent_type,
            "class": agent_class.__name__,
            "docstring": agent_class.__doc__,
        }
