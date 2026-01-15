"""
SpokeStack Agent Orchestration System

Enables multi-agent workflows where agents collaborate on complex tasks,
passing context and results between each other in defined sequences.
"""

from .orchestrator import AgentOrchestrator
from .workflow import (
    Workflow,
    WorkflowStep,
    WorkflowTrigger,
    WorkflowCondition,
    StepType,
    TriggerType,
)
from .registry import AgentRegistry, AgentCapability
from .templates import WorkflowTemplates

__all__ = [
    "AgentOrchestrator",
    "Workflow",
    "WorkflowStep",
    "WorkflowTrigger",
    "WorkflowCondition",
    "StepType",
    "TriggerType",
    "AgentRegistry",
    "AgentCapability",
    "WorkflowTemplates",
]
