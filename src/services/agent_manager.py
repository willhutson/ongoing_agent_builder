"""
AgentManager - Central orchestration and monitoring for the 46-agent ecosystem.

Provides:
1. Agent lifecycle management (create, execute, monitor)
2. Multi-agent workflow orchestration
3. Cost tracking and optimization
4. Performance monitoring and analytics
5. Agent recommendations based on task analysis
"""

from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
import asyncio
from collections import defaultdict

from .agent_factory import AgentFactory, AGENT_REGISTRY
from .model_registry import (
    AGENT_MODEL_RECOMMENDATIONS,
    get_model_for_agent,
    get_agent_tier,
    ClaudeModelTier,
)
from .external_llm_registry import (
    AGENT_EXTERNAL_LLMS,
    EXTERNAL_LLM_CONFIGS,
    ExternalLLMProvider,
    get_external_llms_for_agent,
    get_configured_providers,
)


class ExecutionStatus(str, Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTier(str, Enum):
    """User-facing agent tiers aligned with erp_staging_lmtd."""
    ECONOMY = "economy"    # Maps to HAIKU - fast, cheap, high-volume
    STANDARD = "standard"  # Maps to SONNET - balanced
    PREMIUM = "premium"    # Maps to OPUS - complex reasoning


# Tier mappings
INTERNAL_TO_EXTERNAL_TIER = {
    ClaudeModelTier.HAIKU: AgentTier.ECONOMY,
    ClaudeModelTier.SONNET: AgentTier.STANDARD,
    ClaudeModelTier.OPUS: AgentTier.PREMIUM,
}

EXTERNAL_TO_INTERNAL_TIER = {
    AgentTier.ECONOMY: ClaudeModelTier.HAIKU,
    AgentTier.STANDARD: ClaudeModelTier.SONNET,
    AgentTier.PREMIUM: ClaudeModelTier.OPUS,
}


@dataclass
class AgentExecution:
    """Tracks a single agent execution."""
    id: UUID
    agent_type: str
    instance_id: UUID
    client_id: Optional[UUID]
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    input_tokens: int = 0
    output_tokens: int = 0
    external_llm_calls: list[dict] = field(default_factory=list)
    result: Optional[Any] = None
    error: Optional[str] = None
    cost_estimate: float = 0.0


@dataclass
class WorkflowStep:
    """A step in a multi-agent workflow."""
    agent_type: str
    input_mapping: dict[str, str]  # Maps workflow input to agent input
    output_key: str  # Key to store output in workflow context
    condition: Optional[str] = None  # Optional condition for execution
    parallel: bool = False  # Can run in parallel with other steps


@dataclass
class AgentWorkflow:
    """Multi-agent workflow definition."""
    id: UUID
    name: str
    description: str
    steps: list[WorkflowStep]
    created_at: datetime


class AgentManager:
    """
    Central manager for the agent ecosystem.

    Provides unified interface for:
    - Agent discovery and recommendations
    - Execution orchestration
    - Multi-agent workflows
    - Cost tracking
    - Performance monitoring
    """

    def __init__(self, factory: AgentFactory):
        self.factory = factory
        self._executions: dict[UUID, AgentExecution] = {}
        self._workflows: dict[UUID, AgentWorkflow] = {}
        self._execution_history: list[AgentExecution] = []
        self._cost_by_agent: dict[str, float] = defaultdict(float)
        self._cost_by_provider: dict[str, float] = defaultdict(float)

    # =========================================================================
    # AGENT DISCOVERY
    # =========================================================================

    def list_agents(self, module: Optional[str] = None) -> list[dict]:
        """List all available agents with metadata."""
        agents = []

        module_mapping = {
            "foundation": ["rfp", "brief", "content", "commercial"],
            "studio": ["presentation", "copy", "image"],
            "video": ["video_script", "video_storyboard", "video_production"],
            "social": ["social_listening", "community", "social_analytics"],
            "analytics": ["campaign_analytics", "brand_performance", "competitor"],
            "finance": ["invoice", "forecast", "budget"],
            "quality": ["qa", "legal"],
            "distribution": ["report", "approve", "brief_update", "ops_reporting"],
            "operations": ["resource", "workflow"],
            "client": ["crm", "scope", "onboarding", "instance_onboarding",
                      "instance_analytics", "instance_success"],
            "brand": ["brand_voice", "brand_visual", "brand_guidelines"],
            "gateways": ["gateway_whatsapp", "gateway_email", "gateway_slack", "gateway_sms"],
            "specialized": ["influencer", "pr", "events", "localization",
                          "accessibility", "knowledge", "training", "media_buying", "campaign"],
        }

        for agent_key in AGENT_REGISTRY.keys():
            agent_name = f"{agent_key}_agent" if not agent_key.startswith("gateway") else agent_key

            # Determine module
            agent_module = None
            for mod, agents_list in module_mapping.items():
                if agent_key in agents_list:
                    agent_module = mod
                    break

            if module and agent_module != module:
                continue

            # Get tier
            internal_tier = get_agent_tier(agent_name)
            external_tier = INTERNAL_TO_EXTERNAL_TIER.get(internal_tier, AgentTier.STANDARD)

            # Get external LLMs
            external_llms = get_external_llms_for_agent(agent_key)

            agents.append({
                "key": agent_key,
                "name": agent_name,
                "module": agent_module,
                "tier": external_tier.value,
                "internal_tier": internal_tier.value,
                "external_llms": [
                    {"provider": llm.provider.value, "name": llm.name}
                    for llm in external_llms
                ],
                "has_external_llms": len(external_llms) > 0,
            })

        return agents

    def get_agent_info(self, agent_type: str) -> dict:
        """Get detailed information about an agent."""
        if agent_type not in AGENT_REGISTRY:
            raise ValueError(f"Unknown agent type: {agent_type}")

        agent_class = AGENT_REGISTRY[agent_type]
        agent_name = f"{agent_type}_agent"
        internal_tier = get_agent_tier(agent_name)
        external_tier = INTERNAL_TO_EXTERNAL_TIER.get(internal_tier, AgentTier.STANDARD)
        external_llms = get_external_llms_for_agent(agent_type)
        configured_providers = get_configured_providers()

        return {
            "key": agent_type,
            "name": agent_name,
            "class": agent_class.__name__,
            "docstring": agent_class.__doc__,
            "tier": {
                "external": external_tier.value,
                "internal": internal_tier.value,
                "description": self._get_tier_description(external_tier),
            },
            "external_llms": [
                {
                    "provider": llm.provider.value,
                    "name": llm.name,
                    "description": llm.description,
                    "capabilities": llm.capabilities,
                    "configured": configured_providers.get(llm.provider, False),
                }
                for llm in external_llms
            ],
            "model_id": get_model_for_agent(agent_name),
        }

    def recommend_agents(self, task_description: str, max_results: int = 5) -> list[dict]:
        """Recommend agents based on task description."""
        task_lower = task_description.lower()
        scored_agents = []

        # Keywords for different agent types
        agent_keywords = {
            "rfp": ["rfp", "proposal", "bid", "tender"],
            "brief": ["brief", "requirement", "intake"],
            "content": ["content", "blog", "article", "editorial"],
            "commercial": ["pricing", "margin", "commercial", "quote"],
            "presentation": ["presentation", "deck", "slides", "powerpoint"],
            "copy": ["copy", "headline", "ad", "tagline"],
            "image": ["image", "photo", "visual", "graphic", "picture"],
            "video_script": ["script", "dialogue", "screenplay"],
            "video_storyboard": ["storyboard", "shot", "scene"],
            "video_production": ["video", "film", "motion"],
            "social_listening": ["social", "monitor", "listen", "sentiment"],
            "competitor": ["competitor", "competition", "market"],
            "campaign_analytics": ["campaign", "performance", "analytics", "metrics"],
            "forecast": ["forecast", "predict", "revenue", "projection"],
            "legal": ["legal", "contract", "compliance", "terms"],
            "invoice": ["invoice", "bill", "payment"],
            "qa": ["qa", "quality", "review", "check"],
            "report": ["report", "summary", "dashboard"],
            "pr": ["pr", "press", "media", "news"],
            "influencer": ["influencer", "creator", "ambassador"],
            "events": ["event", "conference", "webinar"],
            "localization": ["localize", "translate", "language"],
        }

        for agent_key, keywords in agent_keywords.items():
            score = sum(3 if kw in task_lower else 0 for kw in keywords)
            if score > 0:
                info = self.get_agent_info(agent_key)
                scored_agents.append({
                    **info,
                    "relevance_score": score,
                })

        scored_agents.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_agents[:max_results]

    # =========================================================================
    # EXECUTION MANAGEMENT
    # =========================================================================

    async def execute_agent(
        self,
        agent_type: str,
        task: str,
        instance_id: UUID,
        client_id: Optional[UUID] = None,
        tier_override: Optional[AgentTier] = None,
        **kwargs,
    ) -> AgentExecution:
        """Execute a single agent."""
        execution = AgentExecution(
            id=uuid4(),
            agent_type=agent_type,
            instance_id=instance_id,
            client_id=client_id,
            status=ExecutionStatus.PENDING,
            started_at=datetime.utcnow(),
        )
        self._executions[execution.id] = execution

        try:
            execution.status = ExecutionStatus.RUNNING

            # Apply tier override if specified
            model_override = None
            if tier_override:
                model_override = EXTERNAL_TO_INTERNAL_TIER.get(tier_override)

            # Create and execute agent
            agent = await self.factory.create_agent(
                agent_type=agent_type,
                instance_id=instance_id,
                client_id=client_id,
                **kwargs,
            )

            # Execute with the task
            result = await agent.execute(task)

            execution.status = ExecutionStatus.COMPLETED
            execution.result = result
            execution.completed_at = datetime.utcnow()

            # Track costs (simplified - real implementation would track actual usage)
            self._cost_by_agent[agent_type] += execution.cost_estimate

        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()

        self._execution_history.append(execution)
        return execution

    def get_execution(self, execution_id: UUID) -> Optional[AgentExecution]:
        """Get execution by ID."""
        return self._executions.get(execution_id)

    def list_executions(
        self,
        instance_id: Optional[UUID] = None,
        agent_type: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        limit: int = 100,
    ) -> list[AgentExecution]:
        """List executions with filters."""
        executions = self._execution_history[-limit:]

        if instance_id:
            executions = [e for e in executions if e.instance_id == instance_id]
        if agent_type:
            executions = [e for e in executions if e.agent_type == agent_type]
        if status:
            executions = [e for e in executions if e.status == status]

        return executions

    # =========================================================================
    # WORKFLOW ORCHESTRATION
    # =========================================================================

    def create_workflow(
        self,
        name: str,
        description: str,
        steps: list[dict],
    ) -> AgentWorkflow:
        """Create a multi-agent workflow."""
        workflow_steps = [
            WorkflowStep(
                agent_type=s["agent_type"],
                input_mapping=s.get("input_mapping", {}),
                output_key=s.get("output_key", f"step_{i}"),
                condition=s.get("condition"),
                parallel=s.get("parallel", False),
            )
            for i, s in enumerate(steps)
        ]

        workflow = AgentWorkflow(
            id=uuid4(),
            name=name,
            description=description,
            steps=workflow_steps,
            created_at=datetime.utcnow(),
        )

        self._workflows[workflow.id] = workflow
        return workflow

    async def execute_workflow(
        self,
        workflow_id: UUID,
        initial_context: dict,
        instance_id: UUID,
        client_id: Optional[UUID] = None,
    ) -> dict:
        """Execute a multi-agent workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        context = initial_context.copy()
        results = {}

        # Group steps by parallelism
        step_groups = []
        current_group = []

        for step in workflow.steps:
            if step.parallel and current_group:
                current_group.append(step)
            else:
                if current_group:
                    step_groups.append(current_group)
                current_group = [step]

        if current_group:
            step_groups.append(current_group)

        # Execute step groups
        for group in step_groups:
            if len(group) == 1:
                # Sequential execution
                step = group[0]
                result = await self._execute_workflow_step(
                    step, context, instance_id, client_id
                )
                context[step.output_key] = result
                results[step.output_key] = result
            else:
                # Parallel execution
                tasks = [
                    self._execute_workflow_step(step, context, instance_id, client_id)
                    for step in group
                ]
                step_results = await asyncio.gather(*tasks, return_exceptions=True)

                for step, result in zip(group, step_results):
                    if isinstance(result, Exception):
                        results[step.output_key] = {"error": str(result)}
                    else:
                        context[step.output_key] = result
                        results[step.output_key] = result

        return {
            "workflow_id": str(workflow_id),
            "workflow_name": workflow.name,
            "results": results,
        }

    async def _execute_workflow_step(
        self,
        step: WorkflowStep,
        context: dict,
        instance_id: UUID,
        client_id: Optional[UUID],
    ) -> Any:
        """Execute a single workflow step."""
        # Build input from mapping
        task_parts = []
        for ctx_key, desc in step.input_mapping.items():
            if ctx_key in context:
                task_parts.append(f"{desc}: {context[ctx_key]}")

        task = "\n".join(task_parts) if task_parts else str(context)

        execution = await self.execute_agent(
            agent_type=step.agent_type,
            task=task,
            instance_id=instance_id,
            client_id=client_id,
        )

        return execution.result

    # =========================================================================
    # ANALYTICS & MONITORING
    # =========================================================================

    def get_usage_stats(
        self,
        instance_id: Optional[UUID] = None,
        period_days: int = 30,
    ) -> dict:
        """Get usage statistics."""
        cutoff = datetime.utcnow()

        executions = [
            e for e in self._execution_history
            if (not instance_id or e.instance_id == instance_id)
        ]

        # Aggregate by agent
        by_agent = defaultdict(lambda: {"count": 0, "success": 0, "failed": 0})
        for e in executions:
            by_agent[e.agent_type]["count"] += 1
            if e.status == ExecutionStatus.COMPLETED:
                by_agent[e.agent_type]["success"] += 1
            elif e.status == ExecutionStatus.FAILED:
                by_agent[e.agent_type]["failed"] += 1

        # Aggregate by tier
        by_tier = defaultdict(lambda: {"count": 0, "cost": 0.0})
        for e in executions:
            agent_name = f"{e.agent_type}_agent"
            internal_tier = get_agent_tier(agent_name)
            external_tier = INTERNAL_TO_EXTERNAL_TIER.get(internal_tier, AgentTier.STANDARD)
            by_tier[external_tier.value]["count"] += 1
            by_tier[external_tier.value]["cost"] += e.cost_estimate

        return {
            "total_executions": len(executions),
            "by_agent": dict(by_agent),
            "by_tier": dict(by_tier),
            "total_cost": sum(e.cost_estimate for e in executions),
        }

    def get_provider_status(self) -> list[dict]:
        """Get status of all external LLM providers."""
        configured = get_configured_providers()
        result = []

        for provider, config in EXTERNAL_LLM_CONFIGS.items():
            # Find agents using this provider
            using_agents = [
                agent_name for agent_name, providers in AGENT_EXTERNAL_LLMS.items()
                if provider in providers
            ]

            result.append({
                "provider": provider.value,
                "name": config.name,
                "description": config.description,
                "capabilities": config.capabilities,
                "configured": configured.get(provider, False),
                "agents_using": using_agents,
                "agent_count": len(using_agents),
            })

        return result

    def get_tier_summary(self) -> dict:
        """Get summary of agents by tier."""
        summary = {
            "economy": {"agents": [], "description": "Fast, cost-effective for simple tasks"},
            "standard": {"agents": [], "description": "Balanced capability and cost"},
            "premium": {"agents": [], "description": "Complex reasoning, strategic decisions"},
        }

        for agent_key in AGENT_REGISTRY.keys():
            agent_name = f"{agent_key}_agent"
            internal_tier = get_agent_tier(agent_name)
            external_tier = INTERNAL_TO_EXTERNAL_TIER.get(internal_tier, AgentTier.STANDARD)
            summary[external_tier.value]["agents"].append(agent_key)

        for tier in summary:
            summary[tier]["count"] = len(summary[tier]["agents"])

        return summary

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_tier_description(self, tier: AgentTier) -> str:
        """Get description for a tier."""
        descriptions = {
            AgentTier.ECONOMY: "Fast, cost-effective for simple, high-volume tasks",
            AgentTier.STANDARD: "Balanced capability and cost - recommended for most tasks",
            AgentTier.PREMIUM: "Highest capability for complex analysis and strategic decisions",
        }
        return descriptions.get(tier, "")


# Singleton instance
_agent_manager: Optional[AgentManager] = None


def get_agent_manager(factory: AgentFactory) -> AgentManager:
    """Get or create the singleton AgentManager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager(factory)
    return _agent_manager
