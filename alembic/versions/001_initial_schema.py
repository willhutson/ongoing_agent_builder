"""Initial schema for SpokeStack multi-tenant platform

Revision ID: 001
Revises:
Create Date: 2025-01-13

Creates all tables for:
- Multi-tenancy (instances, clients)
- Instance agent configuration
- Skill extensions (custom tools)
- Version control
- Fine-tuning (3-tier)
- Feedback loop
- Audit logging
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # ENUMS
    # ==========================================================================
    update_policy_enum = postgresql.ENUM('auto', 'staged', 'manual', name='updatepolicy', create_type=False)
    update_policy_enum.create(op.get_bind(), checkfirst=True)

    feedback_type_enum = postgresql.ENUM('approved', 'rejected', 'corrected', name='feedbacktype', create_type=False)
    feedback_type_enum.create(op.get_bind(), checkfirst=True)

    tuning_tier_enum = postgresql.ENUM('agent_builder', 'instance', 'client', name='tuningtier', create_type=False)
    tuning_tier_enum.create(op.get_bind(), checkfirst=True)

    # ==========================================================================
    # INSTANCES (Tenants)
    # ==========================================================================
    op.create_table(
        'instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('organization_name', sa.String(255)),
        sa.Column('contact_email', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('tier', sa.String(50), default='standard'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_instances_slug', 'instances', ['slug'])
    op.create_index('ix_instances_is_active', 'instances', ['is_active'])

    # ==========================================================================
    # CLIENTS
    # ==========================================================================
    op.create_table(
        'clients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('instances.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('industry', sa.String(100)),
        sa.Column('vertical', sa.String(100)),
        sa.Column('region', sa.String(100)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.UniqueConstraint('instance_id', 'slug', name='uq_client_instance_slug'),
    )
    op.create_index('ix_clients_instance_id', 'clients', ['instance_id'])

    # ==========================================================================
    # INSTANCE AGENT CONFIGS
    # ==========================================================================
    op.create_table(
        'instance_agent_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('instances.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('prompt_extension', sa.Text(), default=''),
        sa.Column('default_vertical', sa.String(100)),
        sa.Column('default_region', sa.String(100)),
        sa.Column('default_language', sa.String(10), default='en'),
        sa.Column('disabled_tools', postgresql.ARRAY(sa.String()), default=[]),
        sa.Column('max_tokens', sa.Integer()),
        sa.Column('temperature', sa.Float()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.UniqueConstraint('instance_id', 'agent_type', name='uq_instance_agent_config'),
    )
    op.create_index('ix_instance_agent_configs_instance_id', 'instance_agent_configs', ['instance_id'])

    # ==========================================================================
    # INSTANCE SKILLS (Custom Tools)
    # ==========================================================================
    op.create_table(
        'instance_skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('instances.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(255)),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('input_schema', postgresql.JSONB(), nullable=False),
        sa.Column('execution_type', sa.String(20), default='webhook'),
        sa.Column('webhook_url', sa.String(500)),
        sa.Column('webhook_method', sa.String(10), default='POST'),
        sa.Column('webhook_headers', postgresql.JSONB(), default={}),
        sa.Column('webhook_auth', postgresql.JSONB(), default={}),
        sa.Column('agent_types', postgresql.ARRAY(sa.String()), default=[]),
        sa.Column('timeout_seconds', sa.Integer(), default=30),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.UniqueConstraint('instance_id', 'name', name='uq_instance_skill_name'),
    )
    op.create_index('ix_instance_skills_instance_id', 'instance_skills', ['instance_id'])

    # ==========================================================================
    # AGENT VERSIONS
    # ==========================================================================
    op.create_table(
        'agent_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('release_notes', sa.Text()),
        sa.Column('changes', postgresql.JSONB(), default={}),
        sa.Column('optimization_tags', postgresql.ARRAY(sa.String()), default=[]),
        sa.Column('min_platform_version', sa.String(20)),
        sa.Column('breaking_changes', sa.Boolean(), default=False),
        sa.Column('released_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('released_by', sa.String(255)),
        sa.Column('is_stable', sa.Boolean(), default=True),
        sa.Column('is_deprecated', sa.Boolean(), default=False),
        sa.UniqueConstraint('agent_type', 'version', name='uq_agent_version'),
    )
    op.create_index('ix_agent_versions_agent_type', 'agent_versions', ['agent_type'])

    # ==========================================================================
    # INSTANCE VERSION CONFIGS
    # ==========================================================================
    op.create_table(
        'instance_version_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('instances.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('update_policy', update_policy_enum, default='staged'),
        sa.Column('optimization_preference', postgresql.ARRAY(sa.String()), default=[]),
        sa.Column('pinned_versions', postgresql.JSONB(), default={}),
        sa.Column('agent_policies', postgresql.JSONB(), default={}),
        sa.Column('notify_on_updates', sa.Boolean(), default=True),
        sa.Column('notification_email', sa.String(255)),
        sa.Column('notification_webhook', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # ==========================================================================
    # INSTANCE TUNING CONFIGS (Tier 2)
    # ==========================================================================
    op.create_table(
        'instance_tuning_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('instances.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('agency_brand_voice', sa.Text(), default=''),
        sa.Column('vertical_knowledge', sa.Text(), default=''),
        sa.Column('regional_context', sa.Text(), default=''),
        sa.Column('behavior_params', postgresql.JSONB(), default={}),
        sa.Column('content_policies', postgresql.JSONB(), default={}),
        sa.Column('custom_instructions', sa.Text(), default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # ==========================================================================
    # CLIENT TUNING CONFIGS (Tier 3)
    # ==========================================================================
    op.create_table(
        'client_tuning_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('brand_voice', sa.Text(), default=''),
        sa.Column('tone_keywords', postgresql.ARRAY(sa.String()), default=[]),
        sa.Column('content_rules', postgresql.JSONB(), default={}),
        sa.Column('writing_style', postgresql.JSONB(), default={}),
        sa.Column('learned_preferences', postgresql.JSONB(), default={}),
        sa.Column('active_preset', sa.String(50)),
        sa.Column('custom_presets', postgresql.JSONB(), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # ==========================================================================
    # AGENT OUTPUT FEEDBACK
    # ==========================================================================
    op.create_table(
        'agent_output_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('instances.id', ondelete='CASCADE'), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clients.id', ondelete='SET NULL')),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('task_id', sa.String(100)),
        sa.Column('original_output', sa.Text(), nullable=False),
        sa.Column('feedback_type', feedback_type_enum, nullable=False),
        sa.Column('corrected_output', sa.Text()),
        sa.Column('correction_reason', sa.Text()),
        sa.Column('feedback_by', sa.String(255)),
        sa.Column('feedback_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('analyzed', sa.Boolean(), default=False),
        sa.Column('analysis_result', postgresql.JSONB(), default={}),
        sa.Column('applied_to_tuning', sa.Boolean(), default=False),
    )
    op.create_index('ix_agent_output_feedback_instance_id', 'agent_output_feedback', ['instance_id'])
    op.create_index('ix_agent_output_feedback_client_id', 'agent_output_feedback', ['client_id'])
    op.create_index('ix_agent_output_feedback_analyzed', 'agent_output_feedback', ['analyzed'])

    # ==========================================================================
    # TUNING AUDIT LOGS
    # ==========================================================================
    op.create_table(
        'tuning_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tuning_tier', tuning_tier_enum, nullable=False),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('instances.id', ondelete='SET NULL')),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clients.id', ondelete='SET NULL')),
        sa.Column('field_changed', sa.String(100), nullable=False),
        sa.Column('old_value', postgresql.JSONB()),
        sa.Column('new_value', postgresql.JSONB()),
        sa.Column('changed_by', sa.String(255), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('change_reason', sa.Text()),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
    )
    op.create_index('ix_tuning_audit_logs_instance_id', 'tuning_audit_logs', ['instance_id'])
    op.create_index('ix_tuning_audit_logs_changed_at', 'tuning_audit_logs', ['changed_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('tuning_audit_logs')
    op.drop_table('agent_output_feedback')
    op.drop_table('client_tuning_configs')
    op.drop_table('instance_tuning_configs')
    op.drop_table('instance_version_configs')
    op.drop_table('agent_versions')
    op.drop_table('instance_skills')
    op.drop_table('instance_agent_configs')
    op.drop_table('clients')
    op.drop_table('instances')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS tuningtier')
    op.execute('DROP TYPE IF EXISTS feedbacktype')
    op.execute('DROP TYPE IF EXISTS updatepolicy')
