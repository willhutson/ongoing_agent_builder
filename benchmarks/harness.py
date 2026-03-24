"""
Benchmark Harness — Runs agents against test cases and captures results.

Instantiates agents with MockERPToolkit, executes benchmark tasks,
and collects structured outputs for scoring.
"""

import asyncio
import importlib
import json
import time
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.services.openrouter import OpenRouterClient
from src.config import get_settings
from benchmarks.mock_erp import MockERPToolkit


CASES_DIR = Path(__file__).parent / "cases"


@dataclass
class BenchmarkCase:
    """A single test case loaded from YAML."""
    id: str
    name: str
    task: str
    expected: dict = field(default_factory=dict)
    rubric: str = ""


@dataclass
class AgentSpec:
    """Agent configuration loaded from YAML."""
    agent_type: str
    agent_class: str
    agent_module: str
    constructor_kwargs: dict = field(default_factory=dict)
    cases: list[BenchmarkCase] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    """Result from running a single benchmark case."""
    case_id: str
    case_name: str
    agent_type: str
    output: str
    artifacts: list[dict] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    timestamp: str = ""
    success: bool = True
    error: str = ""


def load_agent_spec(yaml_path: Path) -> AgentSpec:
    """Load agent spec and test cases from a YAML file."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    cases = [
        BenchmarkCase(
            id=c["id"],
            name=c["name"],
            task=c["task"],
            expected=c.get("expected", {}),
            rubric=c.get("rubric", ""),
        )
        for c in data.get("cases", [])
    ]

    return AgentSpec(
        agent_type=data["agent_type"],
        agent_class=data["agent_class"],
        agent_module=data["agent_module"],
        constructor_kwargs=data.get("constructor_kwargs", {}),
        cases=cases,
    )


def load_all_specs() -> list[AgentSpec]:
    """Load all agent specs from the cases directory."""
    specs = []
    for yaml_file in sorted(CASES_DIR.glob("*.yaml")):
        specs.append(load_agent_spec(yaml_file))
    return specs


def _instantiate_agent(
    spec: AgentSpec,
    client: OpenRouterClient,
    model: str,
    mock_erp: MockERPToolkit,
) -> BaseAgent:
    """Dynamically instantiate an agent from its spec."""
    module = importlib.import_module(spec.agent_module)
    agent_cls = getattr(module, spec.agent_class)

    kwargs = {
        "client": client,
        "model": model,
        **spec.constructor_kwargs,
    }

    agent = agent_cls(**kwargs)
    # Inject mock ERP toolkit so ERP tool calls return fixture data
    agent.erp_toolkit = mock_erp
    return agent


async def run_case(
    agent: BaseAgent,
    case: BenchmarkCase,
    agent_type: str,
) -> BenchmarkResult:
    """Run a single benchmark case against an agent."""
    context = AgentContext(
        tenant_id="benchmark",
        user_id="benchmark-harness",
        task=case.task,
        metadata={"benchmark_case_id": case.id},
    )

    # Reset token counters
    agent._input_tokens = 0
    agent._output_tokens = 0
    agent._artifacts = []
    agent._created_entities = []

    start = time.monotonic()
    try:
        result: AgentResult = await agent.run(context)
        elapsed_ms = (time.monotonic() - start) * 1000

        return BenchmarkResult(
            case_id=case.id,
            case_name=case.name,
            agent_type=agent_type,
            output=result.output,
            artifacts=result.artifacts,
            tool_calls=_extract_tool_calls(result),
            input_tokens=result.metadata.get("input_tokens", 0),
            output_tokens=result.metadata.get("output_tokens", 0),
            latency_ms=round(elapsed_ms, 1),
            timestamp=datetime.now(timezone.utc).isoformat(),
            success=result.success,
        )
    except Exception as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return BenchmarkResult(
            case_id=case.id,
            case_name=case.name,
            agent_type=agent_type,
            output="",
            latency_ms=round(elapsed_ms, 1),
            timestamp=datetime.now(timezone.utc).isoformat(),
            success=False,
            error=str(e),
        )


def _extract_tool_calls(result: AgentResult) -> list[str]:
    """Extract tool call names from agent result metadata."""
    # AgentResult tracks created entities which imply tool use
    tool_names = []
    for entity in result.created_entities:
        if isinstance(entity, dict) and "type" in entity:
            tool_names.append(f"create_{entity['type']}")
    # Also check artifacts
    for artifact in result.artifacts:
        if isinstance(artifact, dict):
            tool_names.append("emit_artifact")
    return tool_names


async def run_benchmark(
    agent_type: Optional[str] = None,
    model_override: Optional[str] = None,
) -> list[BenchmarkResult]:
    """
    Run the full benchmark suite (or a single agent's cases).

    Args:
        agent_type: If set, only run cases for this agent type (e.g. "brief_agent")
        model_override: Override the model used for benchmarking

    Returns:
        List of BenchmarkResult for all cases run
    """
    settings = get_settings()
    model = model_override or settings.claude_model
    client = OpenRouterClient(api_key=settings.openrouter_api_key)

    specs = load_all_specs()
    if agent_type:
        specs = [s for s in specs if s.agent_type == agent_type]
        if not specs:
            raise ValueError(f"No benchmark cases found for agent type: {agent_type}")

    all_results: list[BenchmarkResult] = []

    for spec in specs:
        mock_erp = MockERPToolkit()
        agent = _instantiate_agent(spec, client, model, mock_erp)

        print(f"\n{'='*60}")
        print(f"Benchmarking: {spec.agent_type} ({len(spec.cases)} cases)")
        print(f"{'='*60}")

        for case in spec.cases:
            print(f"  Running: {case.id} - {case.name}...", end=" ", flush=True)
            result = await run_case(agent, case, spec.agent_type)
            status = "PASS" if result.success else "FAIL"
            print(f"{status} ({result.latency_ms:.0f}ms, {result.input_tokens + result.output_tokens} tokens)")
            all_results.append(result)

        await agent.close()

    await client.http.aclose()
    return all_results


def save_results(results: list[BenchmarkResult], tag: str = "baseline") -> Path:
    """Save benchmark results to a JSON file."""
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{tag}_{timestamp}.json"
    filepath = results_dir / filename

    data = {
        "tag": tag,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": [asdict(r) for r in results],
        "summary": {
            "total_cases": len(results),
            "passed": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "total_tokens": sum(r.input_tokens + r.output_tokens for r in results),
            "avg_latency_ms": round(
                sum(r.latency_ms for r in results) / len(results), 1
            ) if results else 0,
        },
    }

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nResults saved to: {filepath}")
    return filepath
