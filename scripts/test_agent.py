#!/usr/bin/env python3
"""
Test script for SpokeStack agents with Claude API.

Usage:
    python scripts/test_agent.py                          # Interactive mode
    python scripts/test_agent.py --agent competitor       # Specific agent
    python scripts/test_agent.py --agent pr --task "..."  # Agent + task
    python scripts/test_agent.py --list                   # List all agents
"""
import asyncio
import argparse
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import anthropic
from src.config import get_settings
from src.agents.base import AgentContext

# Browser-enabled agents (the ones we just expanded)
BROWSER_AGENTS = {
    "competitor": {
        "class": "CompetitorAgent",
        "module": "src.agents.competitor_agent",
        "description": "Competitive intelligence (LinkedIn, Glassdoor, Crunchbase, G2, Trustpilot, Google Trends)",
        "sample_tasks": [
            "Scrape Google Trends comparing 'Slack' vs 'Microsoft Teams' vs 'Discord' over the past year",
            "Get Trustpilot reviews for amazon.com",
            "Scrape Crunchbase for openai funding information",
        ],
    },
    "social_listening": {
        "class": "SocialListeningAgent",
        "module": "src.agents.social_listening_agent",
        "description": "Social monitoring (Reddit, Twitter, Google News, YouTube, HackerNews, Product Hunt, Quora)",
        "sample_tasks": [
            "Search Reddit for discussions about 'Claude AI' in the past week",
            "Scrape HackerNews for mentions of 'AI agents'",
            "Search Google News for 'Anthropic' mentions from the past month",
        ],
    },
    "influencer": {
        "class": "InfluencerAgent",
        "module": "src.agents.influencer_agent",
        "description": "Influencer analytics (SocialBlade, HypeAuditor, fake follower check, Modash)",
        "sample_tasks": [
            "Check SocialBlade analytics for YouTube user 'mkbhd'",
            "Analyze HypeAuditor data for Instagram user 'therock'",
            "Search Modash for fitness influencers",
        ],
    },
    "media_buying": {
        "class": "MediaBuyingAgent",
        "module": "src.agents.media_buying_agent",
        "description": "Ad intelligence (Google Ads preview, SERP ads, FB Ad Library, SpyFu, SEMrush)",
        "sample_tasks": [
            "Capture SERP ads for keyword 'crm software'",
            "Scrape Facebook Ad Library for ads from 'Nike'",
            "Get SpyFu data for hubspot.com",
        ],
    },
    "pr": {
        "class": "PRAgent",
        "module": "src.agents.pr_agent",
        "description": "PR monitoring (Google News, PR Newswire, Business Wire, TechCrunch, industry publications)",
        "sample_tasks": [
            "Scrape Google News for 'Tesla' mentions in the past week",
            "Search PR Newswire for press releases about 'electric vehicles'",
            "Monitor competitor press coverage for 'Apple'",
        ],
    },
    "crm": {
        "class": "CRMAgent",
        "module": "src.agents.crm_agent",
        "description": "CRM enrichment (Apollo, ZoomInfo, Clearbit, LinkedIn company, Hunter.io)",
        "sample_tasks": [
            "Scrape LinkedIn company page for 'anthropic'",
            "Look up Clearbit data for stripe.com",
            "Search Hunter.io for emails at openai.com",
        ],
    },
}


def list_agents():
    """Print available agents and their capabilities."""
    print("\n" + "=" * 70)
    print("BROWSER-ENABLED AGENTS")
    print("=" * 70)

    for name, info in BROWSER_AGENTS.items():
        print(f"\n{name}")
        print("-" * len(name))
        print(f"  {info['description']}")
        print(f"\n  Sample tasks:")
        for task in info["sample_tasks"]:
            print(f"    - {task}")

    print("\n" + "=" * 70)


def get_agent_instance(agent_name: str, client: anthropic.AsyncAnthropic, settings):
    """Dynamically instantiate an agent."""
    if agent_name not in BROWSER_AGENTS:
        raise ValueError(f"Unknown agent: {agent_name}. Use --list to see available agents.")

    info = BROWSER_AGENTS[agent_name]
    module = __import__(info["module"], fromlist=[info["class"]])
    agent_class = getattr(module, info["class"])

    # Common kwargs for all browser agents
    kwargs = {
        "client": client,
        "model": settings.claude_model,
        "erp_base_url": settings.erp_api_base_url or "http://localhost:8080",
        "erp_api_key": settings.erp_api_key or "test-key",
        "client_id": "test-client",
        "instance_id": "test-instance",
    }

    # Some agents have extra params
    if agent_name == "influencer":
        kwargs["vertical"] = "technology"
        kwargs["region"] = "US"

    return agent_class(**kwargs)


async def run_agent(agent_name: str, task: str, stream: bool = False):
    """Run an agent with a task."""
    settings = get_settings()

    if not settings.anthropic_api_key:
        print("ERROR: ANTHROPIC_API_KEY not set in .env")
        print("Add it to your .env file:")
        print("  anthropic_api_key=sk-ant-...")
        sys.exit(1)

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    print(f"\n{'=' * 70}")
    print(f"Testing: {agent_name}")
    print(f"Model: {settings.claude_model}")
    print(f"Task: {task}")
    print(f"{'=' * 70}\n")

    agent = get_agent_instance(agent_name, client, settings)

    context = AgentContext(
        tenant_id="test-tenant",
        user_id="test-user",
        task=task,
        metadata={"test_mode": True},
    )

    try:
        if stream:
            print("--- Streaming Response ---\n")
            async for chunk in agent.stream(context):
                print(chunk, end="", flush=True)
            print("\n")
        else:
            print("--- Running Agent ---\n")
            result = await agent.run(context)
            print(f"Success: {result.success}")
            print(f"\n--- Output ---\n{result.output}")
            if result.artifacts:
                print(f"\n--- Artifacts ---\n{result.artifacts}")
    finally:
        await agent.close()

    print(f"\n{'=' * 70}")
    print("Test complete!")


def interactive_mode():
    """Interactive agent testing."""
    print("\n" + "=" * 70)
    print("SPOKESTACK AGENT TESTER - Interactive Mode")
    print("=" * 70)

    # List agents
    print("\nAvailable agents:")
    for i, (name, info) in enumerate(BROWSER_AGENTS.items(), 1):
        print(f"  {i}. {name} - {info['description'][:50]}...")

    # Select agent
    print("\nSelect an agent (enter number or name):")
    choice = input("> ").strip()

    if choice.isdigit():
        idx = int(choice) - 1
        agent_name = list(BROWSER_AGENTS.keys())[idx]
    else:
        agent_name = choice.lower()

    if agent_name not in BROWSER_AGENTS:
        print(f"Unknown agent: {agent_name}")
        sys.exit(1)

    # Show sample tasks
    info = BROWSER_AGENTS[agent_name]
    print(f"\nSelected: {agent_name}")
    print(f"Description: {info['description']}")
    print("\nSample tasks:")
    for i, task in enumerate(info["sample_tasks"], 1):
        print(f"  {i}. {task}")

    # Get task
    print("\nEnter task (or number for sample task):")
    task_input = input("> ").strip()

    if task_input.isdigit():
        idx = int(task_input) - 1
        task = info["sample_tasks"][idx]
    else:
        task = task_input

    # Run
    print("\nStream output? (y/n, default: n)")
    stream = input("> ").strip().lower() == "y"

    asyncio.run(run_agent(agent_name, task, stream))


def main():
    parser = argparse.ArgumentParser(description="Test SpokeStack agents")
    parser.add_argument("--list", action="store_true", help="List available agents")
    parser.add_argument("--agent", "-a", type=str, help="Agent to test")
    parser.add_argument("--task", "-t", type=str, help="Task for the agent")
    parser.add_argument("--stream", "-s", action="store_true", help="Stream output")

    args = parser.parse_args()

    if args.list:
        list_agents()
        return

    if args.agent and args.task:
        asyncio.run(run_agent(args.agent, args.task, args.stream))
    elif args.agent:
        # Show agent info and sample tasks
        if args.agent not in BROWSER_AGENTS:
            print(f"Unknown agent: {args.agent}")
            list_agents()
            sys.exit(1)
        info = BROWSER_AGENTS[args.agent]
        print(f"\n{args.agent}")
        print("-" * len(args.agent))
        print(f"  {info['description']}")
        print("\n  Sample tasks:")
        for task in info["sample_tasks"]:
            print(f"    - {task}")
        print(f"\n  Run with: python scripts/test_agent.py --agent {args.agent} --task \"<task>\"")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
