"""
Agent Orchestrator

The core engine that executes multi-agent workflows, managing:
- Step sequencing and parallel execution
- Context passing between agents
- Error handling and recovery
- Human review pauses
- Progress tracking and notifications
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable, Optional
from dataclasses import dataclass, field

from .workflow import (
    Workflow,
    WorkflowStep,
    WorkflowExecution,
    WorkflowStatus,
    StepType,
)
from .registry import AgentRegistry, get_registry


@dataclass
class StepExecutionResult:
    """Result of executing a single step."""
    step_id: str
    success: bool
    result: dict = field(default_factory=dict)
    error: Optional[str] = None
    duration_seconds: float = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AgentOrchestrator:
    """
    Orchestrates multi-agent workflows for SpokeStack.

    The orchestrator:
    1. Receives a workflow definition and input context
    2. Executes steps in the correct order (sequential, parallel, conditional)
    3. Passes results between agents via shared context
    4. Handles failures with retry and skip logic
    5. Pauses for human review when needed
    6. Tracks progress and sends notifications

    Usage:
        orchestrator = AgentOrchestrator(agents, http_client)
        execution = await orchestrator.run_workflow(workflow, initial_context)
    """

    def __init__(
        self,
        agent_factory: Callable[[str], Any],  # Function to get agent by ID
        registry: Optional[AgentRegistry] = None,
        notification_callback: Optional[Callable] = None,
        storage_callback: Optional[Callable] = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            agent_factory: Function that returns an agent instance given agent_id
            registry: Agent registry for capability discovery
            notification_callback: Async function to send notifications
            storage_callback: Async function to persist execution state
        """
        self.agent_factory = agent_factory
        self.registry = registry or get_registry()
        self.notification_callback = notification_callback
        self.storage_callback = storage_callback

        # Active executions
        self._executions: dict[str, WorkflowExecution] = {}

        # Execution locks for thread safety
        self._locks: dict[str, asyncio.Lock] = {}

    async def run_workflow(
        self,
        workflow: Workflow,
        context: dict,
        initiated_by: str = "system",
        organization_id: str = "",
    ) -> WorkflowExecution:
        """
        Execute a complete workflow.

        Args:
            workflow: The workflow definition to execute
            context: Initial context (inputs) for the workflow
            initiated_by: User/system that started the workflow
            organization_id: Tenant ID for multi-tenant isolation

        Returns:
            WorkflowExecution with results from all steps
        """
        # Validate workflow
        is_valid, errors = workflow.validate()
        if not is_valid:
            raise ValueError(f"Invalid workflow: {errors}")

        # Validate required inputs
        for required in workflow.required_inputs:
            if required not in context:
                raise ValueError(f"Missing required input: {required}")

        # Create execution instance
        execution = WorkflowExecution(
            id=str(uuid.uuid4()),
            workflow_id=workflow.id,
            status=WorkflowStatus.RUNNING,
            context={**workflow.default_context, **context},
            initiated_by=initiated_by,
            organization_id=organization_id,
            started_at=datetime.now(),
        )

        # Store and track execution
        self._executions[execution.id] = execution
        self._locks[execution.id] = asyncio.Lock()

        try:
            # Get entry steps
            entry_steps = workflow.get_entry_steps()

            # Execute workflow
            await self._execute_steps(workflow, execution, entry_steps)

            # Mark complete if no failures stopped us
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()

            # Send completion notification
            if workflow.notify_on_complete and self.notification_callback:
                await self.notification_callback({
                    "type": "workflow_complete",
                    "workflow_id": workflow.id,
                    "execution_id": execution.id,
                    "status": execution.status.value,
                    "initiated_by": initiated_by,
                })

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.now()

            # Send failure notification
            if workflow.notify_on_failure and self.notification_callback:
                await self.notification_callback({
                    "type": "workflow_failed",
                    "workflow_id": workflow.id,
                    "execution_id": execution.id,
                    "error": str(e),
                    "initiated_by": initiated_by,
                })

            raise

        finally:
            # Persist final state
            if self.storage_callback:
                await self.storage_callback(execution)

        return execution

    async def _execute_steps(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        steps: list[WorkflowStep],
    ):
        """Execute a set of steps, handling parallel and sequential logic."""

        # Group steps by type
        parallel_steps = [s for s in steps if s.step_type == StepType.PARALLEL]
        sequential_steps = [s for s in steps if s.step_type != StepType.PARALLEL]

        # Execute parallel steps concurrently
        if parallel_steps:
            parallel_tasks = [
                self._execute_single_step(workflow, execution, step)
                for step in parallel_steps[:workflow.max_parallel_steps]
            ]
            await asyncio.gather(*parallel_tasks, return_exceptions=True)

        # Execute sequential steps one at a time
        for step in sequential_steps:
            # Check if workflow was paused or failed
            if execution.status not in [WorkflowStatus.RUNNING]:
                break

            await self._execute_single_step(workflow, execution, step)

    async def _execute_single_step(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        step: WorkflowStep,
    ) -> StepExecutionResult:
        """Execute a single workflow step."""

        result = StepExecutionResult(
            step_id=step.id,
            success=False,
            started_at=datetime.now(),
        )

        try:
            # Check condition
            if step.condition:
                condition_context = {
                    "context": execution.context,
                    "results": execution.step_results,
                    "previous_step": execution.step_results.get(
                        execution.completed_steps[-1] if execution.completed_steps else None, {}
                    ),
                }
                if not step.condition.evaluate(condition_context):
                    result.success = True
                    result.result = {"skipped": True, "reason": "Condition not met"}
                    result.completed_at = datetime.now()
                    return result

            # Handle human review step
            if step.step_type == StepType.HUMAN_REVIEW:
                execution.status = WorkflowStatus.PAUSED
                execution.pending_review = step.id
                if self.notification_callback:
                    await self.notification_callback({
                        "type": "human_review_required",
                        "workflow_id": workflow.id,
                        "execution_id": execution.id,
                        "step_id": step.id,
                        "step_name": step.name,
                    })
                result.success = True
                result.result = {"awaiting_review": True}
                return result

            # Mark step as current
            async with self._locks[execution.id]:
                execution.current_steps.append(step.id)

            # Get the agent
            agent = self.agent_factory(step.agent)
            if not agent:
                raise ValueError(f"Agent not found: {step.agent}")

            # Build tool input from mapping
            tool_input = self._build_tool_input(step.input_mapping, execution.context)

            # Execute with retry logic
            last_error = None
            for attempt in range(step.retry_count):
                try:
                    # Execute the agent tool
                    tool_result = await asyncio.wait_for(
                        agent._execute_tool(step.tool, tool_input),
                        timeout=step.timeout_seconds,
                    )

                    # Check for error in result
                    if isinstance(tool_result, dict) and "error" in tool_result:
                        raise Exception(tool_result["error"])

                    # Success!
                    result.success = True
                    result.result = tool_result
                    break

                except asyncio.TimeoutError:
                    last_error = f"Step timed out after {step.timeout_seconds}s"
                except Exception as e:
                    last_error = str(e)

                # Wait before retry
                if attempt < step.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

            if not result.success:
                result.error = last_error

        except Exception as e:
            result.error = str(e)

        finally:
            result.completed_at = datetime.now()
            result.duration_seconds = (
                result.completed_at - result.started_at
            ).total_seconds() if result.started_at else 0

            # Update execution state
            async with self._locks[execution.id]:
                if result.success:
                    execution.set_step_result(step.id, result.result)
                    # Store result in context under output_key
                    execution.context[step.output_key] = result.result
                else:
                    execution.mark_step_failed(step.id, result.error or "Unknown error")

                    # Handle failure
                    if step.on_failure == "stop":
                        execution.status = WorkflowStatus.FAILED
                    elif step.on_failure == "skip_to" and step.skip_to_step:
                        # Jump to specified step
                        skip_step = workflow.get_step(step.skip_to_step)
                        if skip_step:
                            await self._execute_single_step(workflow, execution, skip_step)

            # Execute next steps if successful
            if result.success and step.next_steps and execution.status == WorkflowStatus.RUNNING:
                next_step_objs = [
                    workflow.get_step(sid) for sid in step.next_steps
                ]
                next_step_objs = [s for s in next_step_objs if s is not None]
                if next_step_objs:
                    await self._execute_steps(workflow, execution, next_step_objs)

        return result

    def _build_tool_input(self, mapping: dict, context: dict) -> dict:
        """
        Build tool input from mapping and context.

        Mapping can contain:
        - Static values: {"url": "https://example.com"}
        - Context references: {"url": "$context.landing_page_url"}
        - Result references: {"baseline": "$results.qa_baseline"}
        """
        tool_input = {}

        for key, value in mapping.items():
            if isinstance(value, str) and value.startswith("$"):
                # Parse reference
                ref_path = value[1:].split(".")
                ref_value = context
                for part in ref_path:
                    if isinstance(ref_value, dict):
                        ref_value = ref_value.get(part, {})
                    else:
                        ref_value = None
                        break
                tool_input[key] = ref_value
            else:
                tool_input[key] = value

        return tool_input

    async def resume_workflow(
        self,
        execution_id: str,
        approval: bool = True,
        review_notes: str = "",
    ) -> WorkflowExecution:
        """
        Resume a paused workflow after human review.

        Args:
            execution_id: ID of the paused execution
            approval: Whether the review was approved
            review_notes: Notes from the reviewer

        Returns:
            Updated WorkflowExecution
        """
        execution = self._executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")

        if execution.status != WorkflowStatus.PAUSED:
            raise ValueError(f"Execution is not paused: {execution.status}")

        execution.review_notes = review_notes

        if approval:
            execution.status = WorkflowStatus.RUNNING
            # Continue from next steps after the review step
            # This would need the workflow definition to be stored/retrieved
        else:
            execution.status = WorkflowStatus.CANCELLED

        return execution

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get an execution by ID."""
        return self._executions.get(execution_id)

    def get_active_executions(self, organization_id: str = None) -> list[WorkflowExecution]:
        """Get all active (running or paused) executions."""
        active = [
            e for e in self._executions.values()
            if e.status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]
        ]
        if organization_id:
            active = [e for e in active if e.organization_id == organization_id]
        return active


class WorkflowBuilder:
    """
    Fluent builder for creating workflows programmatically.

    Usage:
        workflow = (
            WorkflowBuilder("campaign_launch")
            .name("Campaign Launch Checklist")
            .add_step("qa_landing", "qa_agent", "verify_landing_page", {...})
            .add_step("qa_performance", "qa_agent", "run_performance_audit", {...})
            .add_step("legal_check", "legal_agent", "verify_gdpr_compliance", {...})
            .connect("qa_landing", "qa_performance")
            .connect("qa_landing", "legal_check")  # Parallel after qa_landing
            .build()
        )
    """

    def __init__(self, workflow_id: str):
        self._id = workflow_id
        self._name = workflow_id
        self._description = ""
        self._steps: list[WorkflowStep] = []
        self._category = "general"
        self._tags: list[str] = []
        self._required_inputs: list[str] = []
        self._allowed_roles: list[str] = ["admin"]
        self._trigger_type = "manual"

    def name(self, name: str) -> "WorkflowBuilder":
        self._name = name
        return self

    def description(self, desc: str) -> "WorkflowBuilder":
        self._description = desc
        return self

    def category(self, cat: str) -> "WorkflowBuilder":
        self._category = cat
        return self

    def tags(self, *tags: str) -> "WorkflowBuilder":
        self._tags.extend(tags)
        return self

    def requires_input(self, *inputs: str) -> "WorkflowBuilder":
        self._required_inputs.extend(inputs)
        return self

    def allowed_roles(self, *roles: str) -> "WorkflowBuilder":
        self._allowed_roles = list(roles)
        return self

    def add_step(
        self,
        step_id: str,
        agent: str,
        tool: str,
        input_mapping: dict = None,
        step_type: StepType = StepType.SEQUENTIAL,
        condition: str = None,
        description: str = "",
    ) -> "WorkflowBuilder":
        """Add a step to the workflow."""
        step = WorkflowStep(
            id=step_id,
            name=step_id.replace("_", " ").title(),
            agent=agent,
            tool=tool,
            input_mapping=input_mapping or {},
            step_type=step_type,
            description=description,
        )
        if condition:
            from .workflow import WorkflowCondition
            step.condition = WorkflowCondition(expression=condition)
        self._steps.append(step)
        return self

    def add_human_review(
        self,
        step_id: str,
        description: str = "Review and approve before continuing",
    ) -> "WorkflowBuilder":
        """Add a human review checkpoint."""
        step = WorkflowStep(
            id=step_id,
            name=step_id.replace("_", " ").title(),
            agent="",
            tool="",
            step_type=StepType.HUMAN_REVIEW,
            description=description,
        )
        self._steps.append(step)
        return self

    def connect(self, from_step: str, to_step: str) -> "WorkflowBuilder":
        """Connect two steps (from_step -> to_step)."""
        for step in self._steps:
            if step.id == from_step:
                if to_step not in step.next_steps:
                    step.next_steps.append(to_step)
                break
        return self

    def build(self) -> Workflow:
        """Build the workflow."""
        from .workflow import WorkflowTrigger, TriggerType

        return Workflow(
            id=self._id,
            name=self._name,
            description=self._description,
            steps=self._steps,
            trigger=WorkflowTrigger(type=TriggerType.MANUAL),
            category=self._category,
            tags=self._tags,
            required_inputs=self._required_inputs,
            allowed_roles=self._allowed_roles,
        )
