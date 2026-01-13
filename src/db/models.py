"""
SpokeStack Multi-Tenant Database Models

Three-Layer Architecture:
- Layer 1: Core Agents (code, global)
- Layer 2: Instance Configuration (database, per-tenant)
- Layer 3: Skill Extensions (database, per-instance)

Plus: Version Control, Fine-Tuning, Feedback Loop
"""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    ForeignKey, DateTime, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid
import enum


Base = declarative_base()


# =============================================================================
# ENUMS
# =============================================================================

class UpdatePolicy(str, enum.Enum):
    AUTO = "auto"           # Immediate deployment
    STAGED = "staged"       # Sandbox first, then promote
    MANUAL = "manual"       # Explicit approval required


class FeedbackType(str, enum.Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    CORRECTED = "corrected"


class TuningTier(str, enum.Enum):
    AGENT_BUILDER = "agent_builder"  # Tier 1: Platform
    INSTANCE = "instance"            # Tier 2: Agency
    CLIENT = "client"                # Tier 3: Client


# =============================================================================
# LAYER 1: INSTANCES (Tenants)
# =============================================================================

class Instance(Base):
    """
    A SpokeStack instance (tenant).
    Each agency/organization gets their own instance.
    """
    __tablename__ = "instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)  # URL-safe identifier

    # Organization info
    organization_name = Column(String(255))
    contact_email = Column(String(255))

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Subscription tier affects available features
    tier = Column(String(50), default="standard")  # starter, standard, enterprise

    # Relationships
    agent_configs = relationship("InstanceAgentConfig", back_populates="instance", cascade="all, delete-orphan")
    skills = relationship("InstanceSkill", back_populates="instance", cascade="all, delete-orphan")
    version_config = relationship("InstanceVersionConfig", back_populates="instance", uselist=False, cascade="all, delete-orphan")
    tuning_config = relationship("InstanceTuningConfig", back_populates="instance", uselist=False, cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="instance", cascade="all, delete-orphan")


class Client(Base):
    """
    A client within an instance.
    Agencies (instances) serve multiple clients (brands).
    """
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)

    # Client info
    industry = Column(String(100))
    vertical = Column(String(100))  # beauty, fashion, tech, etc.
    region = Column(String(100))    # GCC, MENA, EU, etc.

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    instance = relationship("Instance", back_populates="clients")
    tuning_config = relationship("ClientTuningConfig", back_populates="client", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("AgentOutputFeedback", back_populates="client", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('instance_id', 'slug', name='uq_client_instance_slug'),
    )


# =============================================================================
# LAYER 2: INSTANCE AGENT CONFIGURATION
# =============================================================================

class InstanceAgentConfig(Base):
    """
    Per-instance configuration for each agent type.
    Enables/disables agents and customizes behavior per tenant.
    """
    __tablename__ = "instance_agent_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False)

    # Which agent this config applies to
    agent_type = Column(String(50), nullable=False)  # "copy", "media_buying", etc.

    # Enable/disable
    enabled = Column(Boolean, default=True)

    # Prompt customization (appended to base prompt)
    prompt_extension = Column(Text, default="")

    # Default specialization for this instance
    default_vertical = Column(String(100))
    default_region = Column(String(100))
    default_language = Column(String(10), default="en")

    # Tool restrictions
    disabled_tools = Column(ARRAY(String), default=[])

    # Behavior overrides
    max_tokens = Column(Integer)
    temperature = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    instance = relationship("Instance", back_populates="agent_configs")

    __table_args__ = (
        UniqueConstraint('instance_id', 'agent_type', name='uq_instance_agent_config'),
    )


# =============================================================================
# LAYER 3: SKILL EXTENSIONS (Custom Tools)
# =============================================================================

class InstanceSkill(Base):
    """
    Custom skills (tools) added at the instance level.
    Executed via webhook or internal script.
    """
    __tablename__ = "instance_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False)

    # Skill identity
    name = Column(String(100), nullable=False)  # Tool name (snake_case)
    display_name = Column(String(255))          # Human-readable name
    description = Column(Text, nullable=False)  # Shown to Claude

    # Input schema (JSON Schema format)
    input_schema = Column(JSONB, nullable=False)

    # Execution configuration
    execution_type = Column(String(20), default="webhook")  # webhook, internal, script
    webhook_url = Column(String(500))
    webhook_method = Column(String(10), default="POST")
    webhook_headers = Column(JSONB, default={})
    webhook_auth = Column(JSONB, default={})  # {type: "bearer", token: "..."} or {type: "api_key", header: "X-API-Key", value: "..."}

    # Which agents can use this skill
    agent_types = Column(ARRAY(String), default=[])  # Empty = all agents

    # Timeout and retry
    timeout_seconds = Column(Integer, default=30)
    retry_count = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    instance = relationship("Instance", back_populates="skills")

    __table_args__ = (
        UniqueConstraint('instance_id', 'name', name='uq_instance_skill_name'),
    )


# =============================================================================
# VERSION CONTROL
# =============================================================================

class AgentVersion(Base):
    """
    Global agent version registry.
    Tracks all released versions of each agent type.
    """
    __tablename__ = "agent_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    agent_type = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)  # semver: "2.4.0"

    # What's in this version
    release_notes = Column(Text)
    changes = Column(JSONB, default={})  # {tools_added: [], tools_removed: [], behavior_changes: []}

    # Optimization focus (for conflict detection)
    optimization_tags = Column(ARRAY(String), default=[])  # ["reach"], ["performance", "roas"], etc.

    # Compatibility
    min_platform_version = Column(String(20))
    breaking_changes = Column(Boolean, default=False)

    # Release info
    released_at = Column(DateTime(timezone=True), server_default=func.now())
    released_by = Column(String(255))

    # Status
    is_stable = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('agent_type', 'version', name='uq_agent_version'),
    )


class InstanceVersionConfig(Base):
    """
    Per-instance version preferences and pinning.
    Controls how updates are applied to each instance.
    """
    __tablename__ = "instance_version_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Global update policy for this instance
    update_policy = Column(SQLEnum(UpdatePolicy), default=UpdatePolicy.STAGED)

    # Instance's optimization preference (for conflict warnings)
    optimization_preference = Column(ARRAY(String), default=[])  # ["performance", "roas"]

    # Per-agent version pins (overrides global)
    # Format: {"copy": "2.3.1", "media_buying": "1.8.0"}
    pinned_versions = Column(JSONB, default={})

    # Per-agent update policy overrides
    # Format: {"media_buying": "manual"}
    agent_policies = Column(JSONB, default={})

    # Notification preferences
    notify_on_updates = Column(Boolean, default=True)
    notification_email = Column(String(255))
    notification_webhook = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    instance = relationship("Instance", back_populates="version_config")


# =============================================================================
# FINE-TUNING: TIER 2 (Instance/Agency Level)
# =============================================================================

class InstanceTuningConfig(Base):
    """
    Tier 2 tuning: Agency-level customization.
    Applied to all agents for this instance.
    """
    __tablename__ = "instance_tuning_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Agency brand voice (applied to all client work)
    agency_brand_voice = Column(Text, default="")

    # Vertical-specific knowledge
    vertical_knowledge = Column(Text, default="")  # Industry expertise

    # Regional/cultural context
    regional_context = Column(Text, default="")

    # Behavior parameters
    behavior_params = Column(JSONB, default={
        "default_temperature": 0.7,
        "creativity_level": "balanced",  # conservative, balanced, creative
        "formality": "professional",      # casual, professional, formal
        "detail_level": "comprehensive",  # concise, balanced, comprehensive
    })

    # Content guardrails
    content_policies = Column(JSONB, default={
        "require_citations": False,
        "max_content_length": None,
        "prohibited_topics": [],
        "required_disclaimers": [],
    })

    # Custom instructions (appended to all prompts)
    custom_instructions = Column(Text, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    instance = relationship("Instance", back_populates="tuning_config")


# =============================================================================
# FINE-TUNING: TIER 3 (Client Level)
# =============================================================================

class ClientTuningConfig(Base):
    """
    Tier 3 tuning: Client-level customization.
    Applied to all agents working on this client's work.
    """
    __tablename__ = "client_tuning_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Brand voice
    brand_voice = Column(Text, default="")
    tone_keywords = Column(ARRAY(String), default=[])  # ["bold", "playful", "luxurious"]

    # Content rules
    content_rules = Column(JSONB, default={
        "always": [],    # Always include these elements
        "never": [],     # Never use these words/phrases
        "prefer": [],    # Preferred terms/phrases
        "avoid": [],     # Try to avoid (soft rule)
    })

    # Writing style
    writing_style = Column(JSONB, default={
        "sentence_length": "varied",  # short, varied, long
        "vocabulary": "accessible",   # simple, accessible, sophisticated
        "emoji_usage": "none",        # none, minimal, moderate
        "hashtag_style": None,        # Format for hashtags
    })

    # Learned preferences (auto-populated from feedback)
    learned_preferences = Column(JSONB, default={
        "positive_patterns": [],  # Patterns from approved outputs
        "negative_patterns": [],  # Patterns from rejected outputs
        "corrections": [],        # Common corrections made
    })

    # Quick-tuning presets
    active_preset = Column(String(50))  # "formal", "casual", "campaign_mode", etc.
    custom_presets = Column(JSONB, default={})

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="tuning_config")


# =============================================================================
# FEEDBACK LOOP
# =============================================================================

class AgentOutputFeedback(Base):
    """
    Feedback on agent outputs.
    Powers the auto-learning system.
    """
    __tablename__ = "agent_output_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Context
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"))
    agent_type = Column(String(50), nullable=False)

    # The output being rated
    task_id = Column(String(100))  # Reference to original task
    original_output = Column(Text, nullable=False)

    # Feedback
    feedback_type = Column(SQLEnum(FeedbackType), nullable=False)
    corrected_output = Column(Text)  # If corrected
    correction_reason = Column(Text)  # Why it was corrected

    # Metadata
    feedback_by = Column(String(255))  # User who gave feedback
    feedback_at = Column(DateTime(timezone=True), server_default=func.now())

    # Analysis (populated by FeedbackAnalyzer)
    analyzed = Column(Boolean, default=False)
    analysis_result = Column(JSONB, default={})  # Extracted patterns
    applied_to_tuning = Column(Boolean, default=False)

    # Relationships
    client = relationship("Client", back_populates="feedback")


# =============================================================================
# AUDIT LOG
# =============================================================================

class TuningAuditLog(Base):
    """
    Audit trail for all tuning changes.
    Required for enterprise compliance.
    """
    __tablename__ = "tuning_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # What was changed
    tuning_tier = Column(SQLEnum(TuningTier), nullable=False)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="SET NULL"))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"))

    # Change details
    field_changed = Column(String(100), nullable=False)
    old_value = Column(JSONB)
    new_value = Column(JSONB)

    # Who and when
    changed_by = Column(String(255), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Context
    change_reason = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
