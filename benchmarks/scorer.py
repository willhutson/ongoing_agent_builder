"""
Benchmark Scorer — Multi-dimensional agent output evaluation.

Combines fast structural checks (free) with LLM-as-judge scoring
to produce a 0-100 composite score per benchmark case.

Score breakdown:
  - Structural checks:  0-40 points
  - LLM judge score:    0-50 points
  - Efficiency bonus:   0-10 points
  Total:                0-100 points
"""

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

from src.services.openrouter import OpenRouterClient
from benchmarks.harness import BenchmarkCase, BenchmarkResult


@dataclass
class StructuralScore:
    """Score from automated structural checks."""
    artifact_score: float = 0.0  # 0-10: correct artifact types
    tool_usage_score: float = 0.0  # 0-10: expected tools used
    contains_score: float = 0.0  # 0-10: must-contain keywords present
    no_contains_score: float = 0.0  # 0-10: must-not-contain absent
    total: float = 0.0  # 0-40
    details: list[str] = field(default_factory=list)


@dataclass
class JudgeScore:
    """Score from LLM-as-judge evaluation."""
    completeness: int = 0  # 1-5
    structure: int = 0  # 1-5
    actionability: int = 0  # 1-5
    quality: int = 0  # 1-5
    total: float = 0.0  # 0-50 (mapped from 4-20 scale)
    reasoning: str = ""


@dataclass
class EfficiencyScore:
    """Bonus points for token efficiency."""
    total_tokens: int = 0
    output_length: int = 0
    score: float = 0.0  # 0-10


@dataclass
class CaseScore:
    """Complete score for a single benchmark case."""
    case_id: str
    agent_type: str
    structural: StructuralScore
    judge: JudgeScore
    efficiency: EfficiencyScore
    composite: float = 0.0  # 0-100


def score_structural(case: BenchmarkCase, result: BenchmarkResult) -> StructuralScore:
    """Run automated structural checks (free, instant)."""
    score = StructuralScore()
    expected = case.expected
    output_lower = result.output.lower()

    # Artifact type check (0-10)
    expected_artifacts = expected.get("artifacts", None)
    if expected_artifacts is not None:
        if len(expected_artifacts) == 0:
            # Should NOT produce artifacts
            if len(result.artifacts) == 0:
                score.artifact_score = 10.0
                score.details.append("Correctly produced no artifacts")
            else:
                score.artifact_score = 2.0
                score.details.append(f"Produced {len(result.artifacts)} unexpected artifacts")
        else:
            # Should produce specific artifact types
            produced_types = {a.get("type", "") for a in result.artifacts}
            expected_set = set(expected_artifacts)
            matched = produced_types & expected_set
            if expected_set:
                score.artifact_score = (len(matched) / len(expected_set)) * 10
                score.details.append(f"Artifacts: {len(matched)}/{len(expected_set)} expected types")
    else:
        # No artifact expectation — give full marks
        score.artifact_score = 10.0

    # Tool usage check (0-10)
    expected_tools = expected.get("tool_calls", None)
    if expected_tools is not None:
        # Check tool calls in result
        used_tools = set(result.tool_calls)
        expected_tool_set = set(expected_tools)
        if expected_tool_set:
            matched = used_tools & expected_tool_set
            score.tool_usage_score = (len(matched) / len(expected_tool_set)) * 10
            score.details.append(f"Tools: {len(matched)}/{len(expected_tool_set)} expected")
        else:
            score.tool_usage_score = 10.0
    else:
        score.tool_usage_score = 10.0

    # Must-contain check (0-10)
    must_contain = expected.get("must_contain", [])
    if must_contain:
        found = sum(1 for kw in must_contain if kw.lower() in output_lower)
        score.contains_score = (found / len(must_contain)) * 10
        missing = [kw for kw in must_contain if kw.lower() not in output_lower]
        if missing:
            score.details.append(f"Missing keywords: {missing}")
        else:
            score.details.append(f"All {len(must_contain)} required keywords present")
    else:
        score.contains_score = 10.0

    # Must-not-contain check (0-10)
    must_not_contain = expected.get("must_not_contain", [])
    if must_not_contain:
        violations = [kw for kw in must_not_contain if kw.lower() in output_lower]
        if violations:
            score.no_contains_score = max(0, 10 - len(violations) * 5)
            score.details.append(f"Contains forbidden: {violations}")
        else:
            score.no_contains_score = 10.0
            score.details.append("No forbidden keywords found")
    else:
        score.no_contains_score = 10.0

    score.total = score.artifact_score + score.tool_usage_score + score.contains_score + score.no_contains_score
    return score


async def score_judge(
    case: BenchmarkCase,
    result: BenchmarkResult,
    client: OpenRouterClient,
    judge_model: str = "claude-sonnet-4-20250514",
) -> JudgeScore:
    """Use LLM-as-judge to evaluate output quality."""
    if not result.success or not result.output:
        return JudgeScore(reasoning="Agent failed or produced no output")

    prompt = f"""You are evaluating an AI agent's output for quality. Score each dimension from 1-5.

TASK GIVEN TO AGENT:
{case.task}

AGENT OUTPUT:
{result.output}

EVALUATION RUBRIC:
{case.rubric if case.rubric else "Score on: completeness, structure, actionability, and overall quality."}

Respond in this exact JSON format (no other text):
{{
  "completeness": <1-5>,
  "structure": <1-5>,
  "actionability": <1-5>,
  "quality": <1-5>,
  "reasoning": "<2-3 sentence explanation>"
}}"""

    try:
        response = await client.chat(
            model=judge_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )

        content = response["choices"][0]["message"]["content"]
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
        if json_match:
            scores = json.loads(json_match.group())
        else:
            scores = json.loads(content)

        judge = JudgeScore(
            completeness=min(5, max(1, int(scores.get("completeness", 3)))),
            structure=min(5, max(1, int(scores.get("structure", 3)))),
            actionability=min(5, max(1, int(scores.get("actionability", 3)))),
            quality=min(5, max(1, int(scores.get("quality", 3)))),
            reasoning=scores.get("reasoning", ""),
        )
        # Map 4-20 raw score to 0-50
        raw = judge.completeness + judge.structure + judge.actionability + judge.quality
        judge.total = ((raw - 4) / 16) * 50
        return judge

    except Exception as e:
        return JudgeScore(reasoning=f"Judge evaluation failed: {e}")


def score_efficiency(result: BenchmarkResult) -> EfficiencyScore:
    """Score token efficiency — reward concise, high-quality responses."""
    total_tokens = result.input_tokens + result.output_tokens
    output_len = len(result.output)

    # Efficiency heuristic: penalize extremely high token usage
    # Baseline: ~2000 tokens is efficient, ~8000+ is wasteful
    if total_tokens == 0:
        score = 5.0  # No data
    elif total_tokens < 1500:
        score = 10.0
    elif total_tokens < 3000:
        score = 8.0
    elif total_tokens < 5000:
        score = 6.0
    elif total_tokens < 8000:
        score = 4.0
    else:
        score = 2.0

    return EfficiencyScore(
        total_tokens=total_tokens,
        output_length=output_len,
        score=score,
    )


async def score_case(
    case: BenchmarkCase,
    result: BenchmarkResult,
    client: Optional[OpenRouterClient] = None,
    judge_model: str = "claude-sonnet-4-20250514",
    skip_judge: bool = False,
) -> CaseScore:
    """
    Compute the full composite score for a benchmark case.

    Args:
        case: The benchmark case definition
        result: The agent's output for this case
        client: OpenRouter client (required for LLM judge)
        judge_model: Model to use for LLM-as-judge
        skip_judge: If True, skip LLM judge (faster, cheaper)
    """
    structural = score_structural(case, result)

    if skip_judge or client is None:
        judge = JudgeScore(reasoning="Judge skipped")
    else:
        judge = await score_judge(case, result, client, judge_model)

    efficiency = score_efficiency(result)

    composite = structural.total + judge.total + efficiency.score

    return CaseScore(
        case_id=case.id,
        agent_type=result.agent_type,
        structural=structural,
        judge=judge,
        efficiency=efficiency,
        composite=round(composite, 1),
    )


async def score_all(
    cases: list[BenchmarkCase],
    results: list[BenchmarkResult],
    client: Optional[OpenRouterClient] = None,
    judge_model: str = "claude-sonnet-4-20250514",
    skip_judge: bool = False,
) -> list[CaseScore]:
    """Score all benchmark results."""
    # Match cases to results by case_id
    case_map = {c.id: c for c in cases}
    scores = []

    for result in results:
        case = case_map.get(result.case_id)
        if case:
            score = await score_case(case, result, client, judge_model, skip_judge)
            scores.append(score)

    return scores


def compute_agent_score(scores: list[CaseScore]) -> dict:
    """Compute aggregate score for an agent across all its cases."""
    if not scores:
        return {"agent_type": "unknown", "composite": 0, "cases": 0}

    agent_type = scores[0].agent_type
    composites = [s.composite for s in scores]

    return {
        "agent_type": agent_type,
        "composite": round(sum(composites) / len(composites), 1),
        "min": round(min(composites), 1),
        "max": round(max(composites), 1),
        "cases": len(scores),
        "structural_avg": round(sum(s.structural.total for s in scores) / len(scores), 1),
        "judge_avg": round(sum(s.judge.total for s in scores) / len(scores), 1),
        "efficiency_avg": round(sum(s.efficiency.score for s in scores) / len(scores), 1),
    }


def print_scorecard(scores: list[CaseScore]) -> None:
    """Print a formatted scorecard to stdout."""
    # Group by agent
    agents: dict[str, list[CaseScore]] = {}
    for s in scores:
        agents.setdefault(s.agent_type, []).append(s)

    print(f"\n{'='*70}")
    print(f"{'BENCHMARK SCORECARD':^70}")
    print(f"{'='*70}")

    for agent_type, agent_scores in sorted(agents.items()):
        agg = compute_agent_score(agent_scores)
        print(f"\n  {agent_type}: {agg['composite']}/100")
        print(f"    Structural: {agg['structural_avg']}/40  |  Judge: {agg['judge_avg']}/50  |  Efficiency: {agg['efficiency_avg']}/10")
        print(f"    Cases: {agg['cases']}  |  Range: {agg['min']}-{agg['max']}")

        for s in agent_scores:
            status = "PASS" if s.composite >= 50 else "WARN" if s.composite >= 30 else "FAIL"
            print(f"      [{status}] {s.case_id}: {s.composite}/100")
            if s.structural.details:
                for d in s.structural.details[:3]:
                    print(f"            {d}")

    print(f"\n{'='*70}")
    all_composites = [s.composite for s in scores]
    if all_composites:
        overall = round(sum(all_composites) / len(all_composites), 1)
        print(f"  OVERALL: {overall}/100 across {len(scores)} cases")
    print(f"{'='*70}\n")
