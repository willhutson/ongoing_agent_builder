#!/usr/bin/env python3
"""
CLI entry point for agent benchmarking and autoresearch.

Usage:
    # Run benchmarks for all starter agents
    python scripts/run_benchmarks.py --benchmark

    # Run benchmarks for specific agent
    python scripts/run_benchmarks.py --benchmark --agent brief_agent

    # Run with structural scoring only (no LLM judge — free)
    python scripts/run_benchmarks.py --benchmark --skip-judge

    # Run autoresearch improvement loop
    python scripts/run_benchmarks.py --autoresearch --agent brief_agent --iterations 10

    # Show past results
    python scripts/run_benchmarks.py --results

    # Show past results for specific agent
    python scripts/run_benchmarks.py --results --agent brief_agent
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.harness import run_benchmark, save_results, load_all_specs
from benchmarks.scorer import score_all, print_scorecard, compute_agent_score
from benchmarks.autoresearch import run_autoresearch
from src.services.openrouter import OpenRouterClient
from src.config import get_settings


async def cmd_benchmark(args):
    """Run benchmark suite and score results."""
    print("Starting benchmark run...")

    # Run agents
    results = await run_benchmark(
        agent_type=args.agent,
        model_override=args.model,
    )

    if not results:
        print("No results — check that benchmark cases exist.")
        return

    # Save raw results
    tag = args.agent or "all"
    results_path = save_results(results, tag=f"benchmark_{tag}")

    # Score results
    settings = get_settings()
    client = None
    if not args.skip_judge:
        client = OpenRouterClient(api_key=settings.openrouter_api_key)

    # Load cases for scoring
    specs = load_all_specs()
    all_cases = []
    for spec in specs:
        if args.agent and spec.agent_type != args.agent:
            continue
        all_cases.extend(spec.cases)

    scores = await score_all(
        all_cases, results,
        client=client,
        skip_judge=args.skip_judge,
    )

    print_scorecard(scores)

    # Save scores
    scores_path = results_path.with_suffix(".scores.json")
    with open(scores_path, "w") as f:
        from dataclasses import asdict
        json.dump({
            "scores": [asdict(s) for s in scores],
            "agents": {
                agent_type: compute_agent_score(agent_scores)
                for agent_type in set(s.agent_type for s in scores)
                for agent_scores in [[s for s in scores if s.agent_type == agent_type]]
            },
        }, f, indent=2)
    print(f"Scores saved to: {scores_path}")

    if client:
        await client.http.aclose()


async def cmd_autoresearch(args):
    """Run the autoresearch improvement loop."""
    if not args.agent:
        print("Error: --agent is required for autoresearch")
        print("Example: python scripts/run_benchmarks.py --autoresearch --agent brief_agent")
        sys.exit(1)

    experiments = await run_autoresearch(
        agent_type=args.agent,
        iterations=args.iterations,
        model_override=args.model,
    )

    if experiments:
        kept = sum(1 for e in experiments if e.kept)
        print(f"\nDone! {kept}/{len(experiments)} improvements kept.")


def cmd_results(args):
    """Show past benchmark results."""
    results_dir = Path(__file__).parent.parent / "benchmarks" / "results"

    if args.agent:
        # Show experiment log for specific agent
        exp_log = results_dir / args.agent / "experiments.json"
        if exp_log.exists():
            with open(exp_log) as f:
                experiments = json.load(f)
            print(f"\nAutoResearch experiments for {args.agent}:")
            print(f"{'='*60}")
            for exp in experiments:
                status = "KEPT" if exp["kept"] else "REVERTED"
                print(f"  [{status}] {exp['experiment_id']}: "
                      f"{exp['baseline_score']} → {exp['new_score']} "
                      f"({exp['delta']:+.1f})")
                print(f"    {exp['change_description']}")
            print(f"{'='*60}")
        else:
            print(f"No experiment log found for {args.agent}")

    # Show score files
    score_files = sorted(results_dir.glob("*.scores.json"), reverse=True)
    if score_files:
        print(f"\nRecent benchmark scores:")
        for sf in score_files[:5]:
            with open(sf) as f:
                data = json.load(f)
            agents = data.get("agents", {})
            agents_summary = ", ".join(
                f"{k}: {v['composite']}/100"
                for k, v in agents.items()
            )
            print(f"  {sf.name}: {agents_summary}")
    else:
        print("\nNo benchmark results yet. Run: python scripts/run_benchmarks.py --benchmark")


def main():
    parser = argparse.ArgumentParser(
        description="Agent Benchmarking & AutoResearch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--benchmark", action="store_true", help="Run benchmark suite")
    mode.add_argument("--autoresearch", action="store_true", help="Run autoresearch improvement loop")
    mode.add_argument("--results", action="store_true", help="Show past results")

    parser.add_argument("--agent", type=str, help="Agent type (e.g. brief_agent)")
    parser.add_argument("--iterations", type=int, default=10, help="AutoResearch iterations (default: 10)")
    parser.add_argument("--model", type=str, help="Override model for benchmarking")
    parser.add_argument("--skip-judge", action="store_true", help="Skip LLM-as-judge (structural scoring only)")

    args = parser.parse_args()

    if args.benchmark:
        asyncio.run(cmd_benchmark(args))
    elif args.autoresearch:
        asyncio.run(cmd_autoresearch(args))
    elif args.results:
        cmd_results(args)


if __name__ == "__main__":
    main()
