"""
Workflow Definition Classes

Defines the structure of multi-agent workflows including steps,
triggers, conditions, and execution patterns.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from datetime import datetime


class StepType(Enum):
    """Type of workflow step execution."""
    SEQUENTIAL = "sequential"      # Wait for previous step to complete
    PARALLEL = "parallel"          # Run alongside other parallel steps
    CONDITIONAL = "conditional"    # Only run if condition is met
    LOOP = "loop"                  # Repeat until condition is met
    HUMAN_REVIEW = "human_review"  # Pause for human approval


class TriggerType(Enum):
    """What initiates a workflow."""
    MANUAL = "manual"              # User-initiated
    SCHEDULE = "schedule"          # Cron-based schedule
    EVENT = "event"                # ERP event (e.g., project created)
    WEBHOOK = "webhook"            # External webhook
    AGENT_REQUEST = "agent_request"  # Another agent requests this workflow


class WorkflowStatus(Enum):
    """Current status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"              # Waiting for human review
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowCondition:
    """
    Condition that determines if a step should execute.

    Examples:
    - "previous_step.status == 'success'"
    - "context.client_tier == 'premium'"
    - "results.competitor_count > 5"
    """
    expression: str
    description: str = ""

    def evaluate(self, context: dict) -> bool:
        """Evaluate condition against workflow context."""
        try:
            # Safe evaluation with limited scope
            safe_dict = {
                "context": context.get("context", {}),
                "results": context.get("results", {}),
                "previous_step": context.get("previous_step", {}),
                "True": True,
                "False": False,
                "None": None,
            }
            return eval(self.expression, {"__builtins__": {}}, safe_dict)
        except Exception:
            return False


@dataclass
class WorkflowTrigger:
    """Defines what initiates a workflow."""
    type: TriggerType
    config: dict = field(default_factory=dict)

    # For scheduled triggers
    cron_expression: Optional[str] = None

    # For event triggers
    event_type: Optional[str] = None
    event_filter: Optional[dict] = None

    # For webhook triggers
    webhook_path: Optional[str] = None


@dataclass
class WorkflowStep:
    """
    A single step in a workflow that invokes an agent tool.

    Attributes:
        id: Unique identifier for this step
        name: Human-readable name
        agent: Which agent to use (e.g., "qa_agent", "competitor_agent")
        tool: Which tool to invoke (e.g., "run_performance_audit")
        input_mapping: How to map workflow context to tool inputs
        output_key: Where to store results in workflow context
        step_type: How this step executes relative to others
        condition: Optional condition for execution
        timeout_seconds: Max time for this step
        retry_count: Number of retries on failure
        on_failure: What to do on failure ("continue", "stop", "skip_to")
        next_steps: IDs of steps that follow this one
    """
    id: str
    name: str
    agent: str
    tool: str
    input_mapping: dict = field(default_factory=dict)
    output_key: str = ""
    step_type: StepType = StepType.SEQUENTIAL
    condition: Optional[WorkflowCondition] = None
    timeout_seconds: int = 300
    retry_count: int = 1
    on_failure: str = "stop"
    skip_to_step: Optional[str] = None
    next_steps: list[str] = field(default_factory=list)
    description: str = ""

    def __post_init__(self):
        if not self.output_key:
            self.output_key = f"{self.agent}_{self.tool}_result"


@dataclass
class Workflow:
    """
    Complete workflow definition for multi-agent orchestration.

    A workflow connects multiple agents in a defined sequence,
    passing context and results between them.
    """
    id: str
    name: str
    description: str
    steps: list[WorkflowStep]
    trigger: WorkflowTrigger

    # Workflow metadata
    version: str = "1.0"
    category: str = "general"
    tags: list[str] = field(default_factory=list)

    # Execution settings
    timeout_seconds: int = 3600  # 1 hour default
    max_parallel_steps: int = 5

    # Initial context that's always available
    default_context: dict = field(default_factory=dict)

    # Required inputs from the trigger
    required_inputs: list[str] = field(default_factory=list)

    # Who can run this workflow
    allowed_roles: list[str] = field(default_factory=lambda: ["admin"])

    # Notification settings
    notify_on_complete: bool = True
    notify_on_failure: bool = True
    notification_channels: list[str] = field(default_factory=lambda: ["email"])

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_entry_steps(self) -> list[WorkflowStep]:
        """Get steps that have no predecessors (entry points)."""
        # Find all steps that are referenced as next_steps
        referenced = set()
        for step in self.steps:
            referenced.update(step.next_steps)

        # Entry steps are those not referenced by any other step
        entry_steps = [s for s in self.steps if s.id not in referenced]

        # If no clear entry point, use first step
        return entry_steps if entry_steps else [self.steps[0]] if self.steps else []

    def validate(self) -> tuple[bool, list[str]]:
        """Validate workflow configuration."""
        errors = []

        if not self.steps:
            errors.append("Workflow must have at least one step")

        step_ids = {s.id for s in self.steps}

        for step in self.steps:
            # Check next_steps reference valid steps
            for next_id in step.next_steps:
                if next_id not in step_ids:
                    errors.append(f"Step '{step.id}' references unknown step '{next_id}'")

            # Check skip_to_step is valid
            if step.skip_to_step and step.skip_to_step not in step_ids:
                errors.append(f"Step '{step.id}' skip_to_step references unknown step")

        # Check for cycles (simple check)
        # A more thorough check would use topological sort

        return len(errors) == 0, errors


@dataclass
class WorkflowExecution:
    """
    Tracks the execution state of a workflow instance.
    """
    id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING

    # Execution context - shared data between steps
    context: dict = field(default_factory=dict)

    # Results from each step
    step_results: dict = field(default_factory=dict)

    # Current step(s) being executed
    current_steps: list[str] = field(default_factory=list)

    # Completed steps
    completed_steps: list[str] = field(default_factory=list)

    # Failed steps with error info
    failed_steps: dict = field(default_factory=dict)

    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Human review state
    pending_review: Optional[str] = None  # Step ID awaiting review
    review_notes: str = ""

    # Who initiated this execution
    initiated_by: str = ""
    organization_id: str = ""

    def get_step_result(self, step_id: str) -> Optional[dict]:
        """Get the result of a specific step."""
        return self.step_results.get(step_id)

    def set_step_result(self, step_id: str, result: dict):
        """Store the result of a step."""
        self.step_results[step_id] = result
        self.completed_steps.append(step_id)
        if step_id in self.current_steps:
            self.current_steps.remove(step_id)

    def mark_step_failed(self, step_id: str, error: str):
        """Mark a step as failed."""
        self.failed_steps[step_id] = {
            "error": error,
            "failed_at": datetime.now().isoformat(),
        }
        if step_id in self.current_steps:
            self.current_steps.remove(step_id)
