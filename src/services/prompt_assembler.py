"""
PromptAssembler: Three-Tier Prompt Merging for SpokeStack

Assembles final prompts by merging:
- Tier 1: Agent Builder (platform defaults, in code)
- Tier 2: Instance tuning (agency customization, in database)
- Tier 3: Client tuning (client preferences, in database)
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db.models import (
    Instance,
    Client,
    InstanceAgentConfig,
    InstanceTuningConfig,
    ClientTuningConfig,
)


# =============================================================================
# TIER 1: Agent Builder Defaults (Platform Level)
# =============================================================================

AGENT_BUILDER_DEFAULTS = {
    # Global defaults for all agents
    "_global": {
        "safety_preamble": """
You are an AI assistant operating within the SpokeStack platform.
Always maintain professional conduct and follow these guidelines:
- Never generate harmful, illegal, or unethical content
- Respect client confidentiality and data privacy
- Acknowledge uncertainty when you don't have enough information
- Ask clarifying questions when requirements are ambiguous
""",
        "output_format": """
Structure your responses clearly with:
- Clear headers for different sections
- Bullet points for lists
- Specific, actionable recommendations
""",
    },

    # Agent-specific defaults
    "copy": {
        "role": "You are a professional copywriter with expertise in marketing and brand communications.",
        "capabilities": """
Your capabilities include:
- Writing compelling headlines and taglines
- Creating engaging social media content
- Developing email marketing copy
- Crafting product descriptions
- Adapting tone and style for different audiences
""",
    },

    "media_buying": {
        "role": "You are a media buying specialist with expertise in digital advertising platforms.",
        "capabilities": """
Your capabilities include:
- Analyzing campaign performance metrics
- Recommending budget allocations
- Optimizing for ROAS and conversions
- Platform-specific strategy (Meta, Google, TikTok, etc.)
- Audience targeting recommendations
""",
    },

    "brand_voice": {
        "role": "You are a brand strategist specializing in voice and tone development.",
        "capabilities": """
Your capabilities include:
- Analyzing existing brand communications
- Developing voice and tone guidelines
- Creating brand voice documentation
- Ensuring consistency across channels
""",
    },

    # Add more agent-specific defaults as needed
}


class PromptAssembler:
    """
    Assembles prompts by merging three tiers of configuration.

    The assembly order is:
    1. Agent Builder defaults (code)
    2. Instance tuning (database)
    3. Client tuning (database)

    Later tiers can override or extend earlier tiers.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def assemble(
        self,
        agent_type: str,
        instance_id: UUID,
        client_id: Optional[UUID] = None,
    ) -> str:
        """
        Assemble the final prompt for an agent.

        Args:
            agent_type: Type of agent
            instance_id: Instance (tenant) ID
            client_id: Optional client ID for client-specific tuning

        Returns:
            Assembled prompt string
        """
        sections = []

        # =================================================================
        # TIER 1: Agent Builder Defaults
        # =================================================================
        tier1 = self._get_agent_builder_defaults(agent_type)
        if tier1:
            sections.append(("PLATFORM GUIDELINES", tier1))

        # =================================================================
        # TIER 2: Instance Tuning
        # =================================================================
        tier2 = await self._get_instance_tuning(instance_id, agent_type)
        if tier2:
            sections.append(("AGENCY CONTEXT", tier2))

        # =================================================================
        # TIER 3: Client Tuning
        # =================================================================
        if client_id:
            tier3 = await self._get_client_tuning(client_id)
            if tier3:
                sections.append(("CLIENT REQUIREMENTS", tier3))

        # Assemble final prompt
        return self._format_prompt(sections)

    def _get_agent_builder_defaults(self, agent_type: str) -> str:
        """Get Tier 1 defaults from code."""
        parts = []

        # Global defaults
        global_defaults = AGENT_BUILDER_DEFAULTS.get("_global", {})
        if global_defaults.get("safety_preamble"):
            parts.append(global_defaults["safety_preamble"].strip())

        # Agent-specific defaults
        agent_defaults = AGENT_BUILDER_DEFAULTS.get(agent_type, {})
        if agent_defaults.get("role"):
            parts.append(agent_defaults["role"].strip())
        if agent_defaults.get("capabilities"):
            parts.append(agent_defaults["capabilities"].strip())

        # Global output format
        if global_defaults.get("output_format"):
            parts.append(global_defaults["output_format"].strip())

        return "\n\n".join(parts) if parts else ""

    async def _get_instance_tuning(
        self, instance_id: UUID, agent_type: str
    ) -> str:
        """Get Tier 2 tuning from database."""
        parts = []

        # Get instance tuning config
        result = await self.db.execute(
            select(InstanceTuningConfig)
            .where(InstanceTuningConfig.instance_id == instance_id)
        )
        tuning = result.scalar_one_or_none()

        if tuning:
            # Agency brand voice
            if tuning.agency_brand_voice:
                parts.append(f"Agency Voice:\n{tuning.agency_brand_voice}")

            # Vertical knowledge
            if tuning.vertical_knowledge:
                parts.append(f"Industry Expertise:\n{tuning.vertical_knowledge}")

            # Regional context
            if tuning.regional_context:
                parts.append(f"Regional Context:\n{tuning.regional_context}")

            # Behavior params
            if tuning.behavior_params:
                behavior_text = self._format_behavior_params(tuning.behavior_params)
                if behavior_text:
                    parts.append(f"Behavior Guidelines:\n{behavior_text}")

            # Content policies
            if tuning.content_policies:
                policy_text = self._format_content_policies(tuning.content_policies)
                if policy_text:
                    parts.append(f"Content Policies:\n{policy_text}")

            # Custom instructions
            if tuning.custom_instructions:
                parts.append(f"Additional Instructions:\n{tuning.custom_instructions}")

        # Get agent-specific config
        result = await self.db.execute(
            select(InstanceAgentConfig)
            .where(
                InstanceAgentConfig.instance_id == instance_id,
                InstanceAgentConfig.agent_type == agent_type,
            )
        )
        agent_config = result.scalar_one_or_none()

        if agent_config and agent_config.prompt_extension:
            parts.append(f"Agent-Specific Instructions:\n{agent_config.prompt_extension}")

        return "\n\n".join(parts) if parts else ""

    async def _get_client_tuning(self, client_id: UUID) -> str:
        """Get Tier 3 tuning from database."""
        parts = []

        # Load client with tuning config
        result = await self.db.execute(
            select(Client)
            .where(Client.id == client_id)
            .options(selectinload(Client.tuning_config))
        )
        client = result.scalar_one_or_none()

        if not client:
            return ""

        # Add client context
        parts.append(f"Client: {client.name}")
        if client.industry:
            parts.append(f"Industry: {client.industry}")
        if client.vertical:
            parts.append(f"Vertical: {client.vertical}")

        tuning = client.tuning_config
        if tuning:
            # Brand voice
            if tuning.brand_voice:
                parts.append(f"\nBrand Voice:\n{tuning.brand_voice}")

            # Tone keywords
            if tuning.tone_keywords:
                keywords = ", ".join(tuning.tone_keywords)
                parts.append(f"\nTone: {keywords}")

            # Content rules
            if tuning.content_rules:
                rules_text = self._format_content_rules(tuning.content_rules)
                if rules_text:
                    parts.append(f"\nContent Rules:\n{rules_text}")

            # Writing style
            if tuning.writing_style:
                style_text = self._format_writing_style(tuning.writing_style)
                if style_text:
                    parts.append(f"\nWriting Style:\n{style_text}")

            # Learned preferences
            if tuning.learned_preferences:
                learned_text = self._format_learned_preferences(tuning.learned_preferences)
                if learned_text:
                    parts.append(f"\nLearned Preferences:\n{learned_text}")

        return "\n".join(parts) if parts else ""

    def _format_behavior_params(self, params: dict) -> str:
        """Format behavior parameters as readable text."""
        lines = []

        if params.get("creativity_level"):
            lines.append(f"- Creativity: {params['creativity_level']}")
        if params.get("formality"):
            lines.append(f"- Formality: {params['formality']}")
        if params.get("detail_level"):
            lines.append(f"- Detail level: {params['detail_level']}")

        return "\n".join(lines)

    def _format_content_policies(self, policies: dict) -> str:
        """Format content policies as readable text."""
        lines = []

        if policies.get("require_citations"):
            lines.append("- Always include citations for claims")
        if policies.get("max_content_length"):
            lines.append(f"- Maximum length: {policies['max_content_length']} characters")
        if policies.get("prohibited_topics"):
            topics = ", ".join(policies["prohibited_topics"])
            lines.append(f"- Avoid topics: {topics}")
        if policies.get("required_disclaimers"):
            for disclaimer in policies["required_disclaimers"]:
                lines.append(f"- Include disclaimer: {disclaimer}")

        return "\n".join(lines)

    def _format_content_rules(self, rules: dict) -> str:
        """Format content rules as readable text."""
        lines = []

        if rules.get("always"):
            lines.append("Always include:")
            for item in rules["always"]:
                lines.append(f"  - {item}")

        if rules.get("never"):
            lines.append("Never use:")
            for item in rules["never"]:
                lines.append(f"  - {item}")

        if rules.get("prefer"):
            lines.append("Prefer:")
            for item in rules["prefer"]:
                lines.append(f"  - {item}")

        if rules.get("avoid"):
            lines.append("Try to avoid:")
            for item in rules["avoid"]:
                lines.append(f"  - {item}")

        return "\n".join(lines)

    def _format_writing_style(self, style: dict) -> str:
        """Format writing style as readable text."""
        lines = []

        if style.get("sentence_length"):
            lines.append(f"- Sentence length: {style['sentence_length']}")
        if style.get("vocabulary"):
            lines.append(f"- Vocabulary level: {style['vocabulary']}")
        if style.get("emoji_usage"):
            lines.append(f"- Emoji usage: {style['emoji_usage']}")

        return "\n".join(lines)

    def _format_learned_preferences(self, preferences: dict) -> str:
        """Format learned preferences as readable text."""
        lines = []

        if preferences.get("positive_patterns"):
            lines.append("Patterns that work well:")
            for pattern in preferences["positive_patterns"][:5]:  # Limit to 5
                lines.append(f"  - {pattern}")

        if preferences.get("negative_patterns"):
            lines.append("Patterns to avoid:")
            for pattern in preferences["negative_patterns"][:5]:
                lines.append(f"  - {pattern}")

        return "\n".join(lines)

    def _format_prompt(self, sections: list[tuple[str, str]]) -> str:
        """Format sections into final prompt."""
        if not sections:
            return ""

        parts = []
        for header, content in sections:
            if content:
                parts.append(f"=== {header} ===\n{content}")

        return "\n\n".join(parts)
