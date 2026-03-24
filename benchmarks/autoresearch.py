"""
AutoResearch-style Agent Improvement Loop.

Adapts Karpathy's autoresearch pattern to systematically improve agent
system prompts through autonomous experimentation:

1. Read current system prompt + baseline score
2. Use Claude to propose a prompt improvement
3. Apply the change to the agent file
4. Run benchmark suite → get new score
5. If improved: git commit the change
6. If regressed: git revert the change
7. Log experiment and repeat

Only modifies system_prompt text — never touches tools or code logic.
"""

import asyncio
import json
import os
import re
import subprocess
import textwrap
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.services.openrouter import OpenRouterClient
from src.config import get_settings
from benchmarks.harness import (
    load_agent_spec, run_benchmark, save_results,
    CASES_DIR, BenchmarkResult,
)
from benchmarks.scorer import score_all, compute_agent_score, CaseScore


PROGRAM_MD = Path(__file__).parent / "program.md"
RESULTS_DIR = Path(__file__).parent / "results"


@dataclass
class Experiment:
    """Record of a single autoresearch experiment."""
    experiment_id: str
    agent_type: str
    iteration: int
    timestamp: str
    baseline_score: float
    new_score: float
    delta: float
    kept: bool
    change_description: str
    prompt_before_len: int
    prompt_after_len: int
    token_cost_estimate: float = 0.0


def _read_program() -> str:
    """Read the human guidance file."""
    if PROGRAM_MD.exists():
        return PROGRAM_MD.read_text()
    return "Improve the agent's system prompt to increase benchmark scores."


def _find_agent_file(agent_type: str) -> Path:
    """Find the agent's Python source file."""
    agent_file = Path(f"src/agents/{agent_type}.py")
    if agent_file.exists():
        return agent_file
    raise FileNotFoundError(f"Agent file not found: {agent_file}")


def _extract_system_prompt(agent_file: Path) -> str:
    """Extract the system_prompt property return value from an agent file."""
    content = agent_file.read_text()

    # Match the system_prompt property — handles both direct return strings
    # and variable-based patterns
    pattern = r'def system_prompt\(self\)[^:]*:\s*\n(.*?)(?=\n    (?:def |@))'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)

    # Fallback: find the return statement with triple-quoted string
    pattern2 = r'def system_prompt\(self\).*?return\s+("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"]*")'
    match2 = re.search(pattern2, content)
    if match2:
        return match2.group(1)

    raise ValueError(f"Could not extract system_prompt from {agent_file}")


def _apply_prompt_change(agent_file: Path, old_prompt_body: str, new_prompt_body: str) -> bool:
    """Replace the system prompt body in the agent file."""
    content = agent_file.read_text()
    if old_prompt_body not in content:
        return False
    new_content = content.replace(old_prompt_body, new_prompt_body, 1)
    agent_file.write_text(new_content)
    return True


def _git_commit(message: str) -> bool:
    """Stage and commit changes."""
    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", message],
            check=True, capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _git_revert_file(file_path: Path) -> bool:
    """Revert a single file to its last committed state."""
    try:
        subprocess.run(
            ["git", "checkout", "HEAD", "--", str(file_path)],
            check=True, capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


async def _propose_improvement(
    client: OpenRouterClient,
    agent_type: str,
    current_prompt_body: str,
    baseline_score: float,
    past_experiments: list[Experiment],
    program: str,
) -> tuple[str, str]:
    """
    Use Claude to propose a system prompt improvement.

    Returns:
        (new_prompt_body, change_description)
    """
    # Build context from past experiments
    past_context = ""
    if past_experiments:
        past_lines = []
        for exp in past_experiments[-5:]:  # Last 5 experiments
            status = "KEPT" if exp.kept else "REVERTED"
            past_lines.append(
                f"  - [{status}] {exp.change_description} "
                f"(score: {exp.baseline_score} → {exp.new_score}, delta: {exp.delta:+.1f})"
            )
        past_context = "\nPast experiments (most recent):\n" + "\n".join(past_lines)

    messages = [{"role": "user", "content": f"""You are optimizing an AI agent's system prompt to improve its benchmark score.

Agent type: {agent_type}
Current benchmark score: {baseline_score}/100
{past_context}

## Improvement program
{program}

## Current system_prompt property body (the code inside the property):
```python
{current_prompt_body}
```

Propose ONE focused improvement to the system prompt. Return your response in this exact format:

CHANGE_DESCRIPTION: <one-line description of what you changed>
NEW_PROMPT_BODY:
```python
<the complete new property body, including the return statement>
```

Rules:
- Return the COMPLETE property body (everything after `def system_prompt(self) -> str:`)
- Make ONE focused change, not multiple
- Keep the same return structure (string, f-string, or variable + return)
- Do not add tool definitions in the prompt
- Keep under 2000 tokens
- Must be valid Python that returns a string"""}]

    response = await client.chat(
        model="claude-sonnet-4-20250514",
        messages=messages,
        max_tokens=4000,
    )

    content = response["choices"][0]["message"]["content"]

    # Parse the response
    desc_match = re.search(r'CHANGE_DESCRIPTION:\s*(.+)', content)
    change_desc = desc_match.group(1).strip() if desc_match else "Prompt improvement"

    # Extract the new prompt body from the code block
    code_match = re.search(r'NEW_PROMPT_BODY:\s*```python\s*\n(.*?)```', content, re.DOTALL)
    if code_match:
        new_body = code_match.group(1).rstrip()
    else:
        raise ValueError("Could not parse proposed prompt from LLM response")

    return new_body, change_desc


async def run_autoresearch(
    agent_type: str,
    iterations: int = 10,
    model_override: Optional[str] = None,
) -> list[Experiment]:
    """
    Run the autoresearch improvement loop for a specific agent.

    Args:
        agent_type: The agent type to improve (e.g. "brief_agent")
        iterations: Number of improvement iterations to run
        model_override: Override the model used for benchmarking

    Returns:
        List of Experiment records
    """
    settings = get_settings()
    client = OpenRouterClient(api_key=settings.openrouter_api_key)
    program = _read_program()
    agent_file = _find_agent_file(agent_type)

    # Load the agent spec for scoring
    yaml_path = CASES_DIR / f"{agent_type}.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(f"No benchmark cases for {agent_type}: {yaml_path}")
    spec = load_agent_spec(yaml_path)

    experiments: list[Experiment] = []

    # Load past experiments if they exist
    exp_log_path = RESULTS_DIR / agent_type
    exp_log_path.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"AutoResearch: {agent_type}")
    print(f"Iterations: {iterations}")
    print(f"Agent file: {agent_file}")
    print(f"{'='*60}")

    for i in range(iterations):
        print(f"\n--- Iteration {i+1}/{iterations} ---")

        # Step 1: Get current prompt body
        current_prompt_body = _extract_system_prompt(agent_file)
        print(f"  Current prompt: {len(current_prompt_body)} chars")

        # Step 2: Run baseline benchmark
        print("  Running baseline benchmark...")
        baseline_results = await run_benchmark(
            agent_type=agent_type,
            model_override=model_override,
        )
        baseline_scores = await score_all(
            spec.cases, baseline_results, client,
            skip_judge=False,
        )
        baseline_agg = compute_agent_score(baseline_scores)
        baseline_score = baseline_agg["composite"]
        print(f"  Baseline score: {baseline_score}/100")

        # Step 3: Propose improvement
        print("  Proposing improvement...")
        try:
            new_prompt_body, change_desc = await _propose_improvement(
                client, agent_type, current_prompt_body,
                baseline_score, experiments, program,
            )
            print(f"  Proposed: {change_desc}")
        except Exception as e:
            print(f"  Failed to propose: {e}")
            continue

        # Step 4: Apply the change
        if not _apply_prompt_change(agent_file, current_prompt_body, new_prompt_body):
            print("  Failed to apply prompt change (text not found)")
            continue

        # Step 5: Run benchmark with new prompt
        print("  Running benchmark with new prompt...")
        try:
            new_results = await run_benchmark(
                agent_type=agent_type,
                model_override=model_override,
            )
            new_scores = await score_all(
                spec.cases, new_results, client,
                skip_judge=False,
            )
            new_agg = compute_agent_score(new_scores)
            new_score = new_agg["composite"]
        except Exception as e:
            print(f"  Benchmark failed: {e}")
            _git_revert_file(agent_file)
            continue

        delta = new_score - baseline_score
        print(f"  New score: {new_score}/100 (delta: {delta:+.1f})")

        # Step 6: Keep or revert
        experiment = Experiment(
            experiment_id=f"{agent_type}-exp-{len(experiments)+1:03d}",
            agent_type=agent_type,
            iteration=i + 1,
            timestamp=datetime.now(timezone.utc).isoformat(),
            baseline_score=baseline_score,
            new_score=new_score,
            delta=round(delta, 1),
            kept=delta > 0,
            change_description=change_desc,
            prompt_before_len=len(current_prompt_body),
            prompt_after_len=len(new_prompt_body),
        )

        if delta > 0:
            # Improvement — commit!
            commit_msg = (
                f"autoresearch({agent_type}): {change_desc}\n\n"
                f"Score: {baseline_score} → {new_score} (+{delta:.1f})\n"
                f"Experiment: {experiment.experiment_id}"
            )
            if _git_commit(commit_msg):
                print(f"  KEPT - committed ({delta:+.1f})")
            else:
                print(f"  KEPT - commit failed, changes staged")
        else:
            # Regression or no change — revert
            _git_revert_file(agent_file)
            print(f"  REVERTED ({delta:+.1f})")

        experiments.append(experiment)

        # Save experiment log after each iteration
        log_file = exp_log_path / f"experiments.json"
        with open(log_file, "w") as f:
            json.dump([asdict(e) for e in experiments], f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print(f"AutoResearch Complete: {agent_type}")
    print(f"{'='*60}")
    kept = [e for e in experiments if e.kept]
    reverted = [e for e in experiments if not e.kept]
    print(f"  Iterations: {len(experiments)}")
    print(f"  Kept: {len(kept)}")
    print(f"  Reverted: {len(reverted)}")
    if experiments:
        first_score = experiments[0].baseline_score
        last_score = experiments[-1].new_score if experiments[-1].kept else experiments[-1].baseline_score
        print(f"  Score journey: {first_score} → {last_score} ({last_score - first_score:+.1f})")
    print(f"  Log: {exp_log_path / 'experiments.json'}")

    await client.http.aclose()
    return experiments
