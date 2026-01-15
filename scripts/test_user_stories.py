#!/usr/bin/env python3
"""
User Story Testing for SpokeStack Browser-Enabled Agents

Real-world agency scenarios to test agent capabilities with Claude API.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import anthropic
from src.config import get_settings
from src.agents.base import AgentContext

# =============================================================================
# USER STORIES - Real agency scenarios for each browser-enabled agent
# =============================================================================

USER_STORIES = {
    "competitor": {
        "agent_class": "CompetitorAgent",
        "module": "src.agents.competitor_agent",
        "stories": [
            {
                "id": "COMP-001",
                "title": "Quarterly Competitor Report",
                "persona": "Strategy Director at a B2B SaaS agency",
                "scenario": """I need to prepare a quarterly competitive landscape report for our client Acme Corp,
who competes with Salesforce and HubSpot in the CRM space. Can you help me gather current data on:
1. How these brands compare in Google Trends over the past year
2. Their Trustpilot ratings and recent customer sentiment
3. Any recent funding or company news from Crunchbase

Focus on actionable insights we can present to the client.""",
            },
            {
                "id": "COMP-002",
                "title": "New Business Pitch Research",
                "persona": "Business Development Manager",
                "scenario": """We're pitching a mid-size fintech startup called 'PayFlow' next week.
I need competitive intelligence on their main competitors: Stripe and Square.

Please scrape:
- G2 reviews to understand market perception
- LinkedIn company pages for employee count/growth signals
- Google Trends to show relative market interest

This will help us craft a differentiated positioning strategy in the pitch.""",
            },
        ],
    },
    "social_listening": {
        "agent_class": "SocialListeningAgent",
        "module": "src.agents.social_listening_agent",
        "stories": [
            {
                "id": "SOC-001",
                "title": "Brand Crisis Monitoring",
                "persona": "Account Director at PR agency",
                "scenario": """Our client 'TechGiant Inc' just had a product recall and we need to monitor
the social conversation. Please help me scan:

1. Reddit discussions about TechGiant in tech subreddits over the past week
2. Twitter/X sentiment around the recall announcement
3. Any HackerNews threads discussing this

I need to understand the narrative so we can advise on response strategy.""",
            },
            {
                "id": "SOC-002",
                "title": "Product Launch Buzz Tracking",
                "persona": "Campaign Manager",
                "scenario": """We just launched a new AI writing tool called 'WriteBot' for our client.
Help me capture the initial buzz by checking:

1. Product Hunt - did we get featured? What's the discussion?
2. Reddit mentions in r/artificial and r/productivity
3. Any YouTube videos or reviews popping up?

I need screenshots as proof points for the client report.""",
            },
        ],
    },
    "influencer": {
        "agent_class": "InfluencerAgent",
        "module": "src.agents.influencer_agent",
        "stories": [
            {
                "id": "INF-001",
                "title": "Influencer Vetting for Campaign",
                "persona": "Influencer Marketing Manager",
                "scenario": """We're planning a $50K influencer campaign for a fitness brand.
A macro-influencer @FitLifeJake (Instagram) has pitched to us.

Before we commit, please help me vet:
1. SocialBlade analytics - are their growth patterns organic?
2. HypeAuditor audience quality metrics
3. Check for fake followers using available tools

I need confidence this isn't a bot farm before I recommend to the client.""",
            },
            {
                "id": "INF-002",
                "title": "Influencer Discovery Research",
                "persona": "Talent Scout",
                "scenario": """Our client is a sustainable fashion brand targeting Gen-Z.
We need to find micro-influencers in the sustainable fashion space.

Please search Modash for:
- Sustainable fashion influencers on Instagram
- Check SocialBlade for a few promising profiles

Give me a shortlist approach we can present to the client.""",
            },
        ],
    },
    "media_buying": {
        "agent_class": "MediaBuyingAgent",
        "module": "src.agents.media_buying_agent",
        "stories": [
            {
                "id": "MED-001",
                "title": "Competitive Ad Intelligence",
                "persona": "Paid Media Director",
                "scenario": """We're taking over paid media for a new e-commerce client in the outdoor gear space.
Before we build our strategy, I need to understand the competitive landscape.

Please research:
1. Facebook Ad Library - what are REI and Patagonia running?
2. SpyFu data on backcountry.com - what keywords are they buying?
3. Capture current SERP ads for 'hiking backpack'

This will inform our differentiation strategy and budget allocation.""",
            },
            {
                "id": "MED-002",
                "title": "Campaign Proof for Client",
                "persona": "Account Manager",
                "scenario": """Client is asking for proof that their Google Ads are showing.
They want to see their ads in the wild for the keyword 'enterprise CRM software'.

Please capture:
1. SERP ads screenshot for that keyword
2. Any competitor ads showing alongside

I need this for our weekly client call as proof of delivery.""",
            },
        ],
    },
    "pr": {
        "agent_class": "PRAgent",
        "module": "src.agents.pr_agent",
        "stories": [
            {
                "id": "PR-001",
                "title": "Coverage Report for Client",
                "persona": "PR Account Executive",
                "scenario": """Our client Anthropic just announced their new Claude model.
I need to compile a media coverage report for the exec team.

Please gather:
1. Google News coverage from the past week
2. TechCrunch and other tech publication mentions
3. PR Newswire/Business Wire for the official release

Screenshot all coverage for the report deck.""",
            },
            {
                "id": "PR-002",
                "title": "Competitor Press Monitoring",
                "persona": "Communications Strategist",
                "scenario": """Our client is in the AI space and wants to track what competitors are announcing.

Please monitor recent press for:
1. OpenAI announcements in the past month
2. Google DeepMind press coverage
3. Any emerging AI startups getting press attention

I need to brief the client on competitive messaging trends.""",
            },
        ],
    },
    "crm": {
        "agent_class": "CRMAgent",
        "module": "src.agents.crm_agent",
        "stories": [
            {
                "id": "CRM-001",
                "title": "Lead Enrichment for Outreach",
                "persona": "Business Development Rep",
                "scenario": """We're preparing outreach to a list of target companies in the fintech space.
I need to enrich our lead data for 'Plaid' (plaid.com) before our sales call.

Please gather:
1. LinkedIn company page - employee count, recent posts, open roles
2. Clearbit company data
3. Hunter.io for email patterns

This will help personalize our outreach.""",
            },
            {
                "id": "CRM-002",
                "title": "Client 360 Research",
                "persona": "Customer Success Manager",
                "scenario": """I have a QBR with our client Notion tomorrow and need a full picture of their current state.

Please pull:
1. Their LinkedIn company page for recent announcements
2. Social media presence overview (Twitter, LinkedIn)
3. Any recent press coverage

I want to come prepared to discuss their business context.""",
            },
        ],
    },
}


def get_agent_instance(agent_name: str, client: anthropic.AsyncAnthropic, settings):
    """Instantiate an agent."""
    info = USER_STORIES[agent_name]
    module = __import__(info["module"], fromlist=[info["agent_class"]])
    agent_class = getattr(module, info["agent_class"])

    kwargs = {
        "client": client,
        "model": settings.claude_model,
        "erp_base_url": settings.erp_api_base_url or "http://localhost:8080",
        "erp_api_key": settings.erp_api_key or "test-key",
        "client_id": "test-client",
        "instance_id": "test-instance",
    }

    if agent_name == "influencer":
        kwargs["vertical"] = "technology"
        kwargs["region"] = "US"

    return agent_class(**kwargs)


async def run_story(agent_name: str, story: dict, stream: bool = True):
    """Run a single user story."""
    settings = get_settings()

    if not settings.anthropic_api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Add to .env file.")
        sys.exit(1)

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    agent = get_agent_instance(agent_name, client, settings)

    print("\n" + "=" * 80)
    print(f"USER STORY: {story['id']} - {story['title']}")
    print("=" * 80)
    print(f"Persona: {story['persona']}")
    print(f"Agent: {agent_name}")
    print("-" * 80)
    print(f"Scenario:\n{story['scenario']}")
    print("-" * 80)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    print("\n--- AGENT RESPONSE ---\n")

    context = AgentContext(
        tenant_id="agency-test",
        user_id=story["persona"].lower().replace(" ", "-"),
        task=story["scenario"],
        metadata={"story_id": story["id"], "test_mode": True},
    )

    try:
        if stream:
            async for chunk in agent.stream(context):
                print(chunk, end="", flush=True)
            print("\n")
        else:
            result = await agent.run(context)
            print(result.output)
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        await agent.close()

    print("\n" + "=" * 80)
    print(f"Completed: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)


def show_menu():
    """Show interactive menu."""
    print("\n" + "=" * 80)
    print("SPOKESTACK USER STORY TESTER")
    print("=" * 80)

    # List agents with stories
    print("\nSelect an agent to test:\n")
    agents = list(USER_STORIES.keys())
    for i, agent in enumerate(agents, 1):
        stories = USER_STORIES[agent]["stories"]
        print(f"  {i}. {agent.upper()} ({len(stories)} stories)")

    print(f"\n  0. Run ALL stories (full test suite)")
    print(f"  q. Quit")

    return agents


async def interactive_test():
    """Interactive testing session."""
    agents = show_menu()

    choice = input("\nSelect agent (number): ").strip().lower()

    if choice == "q":
        return

    if choice == "0":
        # Run all stories
        print("\nRunning full test suite...")
        for agent_name in agents:
            for story in USER_STORIES[agent_name]["stories"]:
                await run_story(agent_name, story)
                input("\nPress Enter to continue to next story...")
        return

    try:
        agent_idx = int(choice) - 1
        agent_name = agents[agent_idx]
    except (ValueError, IndexError):
        print("Invalid selection")
        return

    # Show stories for selected agent
    stories = USER_STORIES[agent_name]["stories"]
    print(f"\n{agent_name.upper()} Stories:\n")
    for i, story in enumerate(stories, 1):
        print(f"  {i}. [{story['id']}] {story['title']}")
        print(f"     Persona: {story['persona']}")

    story_choice = input("\nSelect story (number): ").strip()

    try:
        story_idx = int(story_choice) - 1
        story = stories[story_idx]
    except (ValueError, IndexError):
        print("Invalid selection")
        return

    # Run the story
    await run_story(agent_name, story)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test agents with user stories")
    parser.add_argument("--agent", "-a", help="Agent name")
    parser.add_argument("--story", "-s", help="Story ID (e.g., COMP-001)")
    parser.add_argument("--list", "-l", action="store_true", help="List all stories")
    parser.add_argument("--all", action="store_true", help="Run all stories")

    args = parser.parse_args()

    if args.list:
        print("\n" + "=" * 80)
        print("ALL USER STORIES")
        print("=" * 80)
        for agent_name, info in USER_STORIES.items():
            print(f"\n{agent_name.upper()}")
            print("-" * 40)
            for story in info["stories"]:
                print(f"  [{story['id']}] {story['title']}")
                print(f"    Persona: {story['persona']}")
        return

    if args.agent and args.story:
        # Find specific story
        if args.agent in USER_STORIES:
            for story in USER_STORIES[args.agent]["stories"]:
                if story["id"] == args.story:
                    await run_story(args.agent, story)
                    return
        print(f"Story {args.story} not found")
        return

    if args.all:
        # Run all stories
        for agent_name in USER_STORIES:
            for story in USER_STORIES[agent_name]["stories"]:
                await run_story(agent_name, story)
                print("\n" + "-" * 40)
                input("Press Enter for next story...")
        return

    # Interactive mode
    while True:
        await interactive_test()
        again = input("\nRun another test? (y/n): ").strip().lower()
        if again != "y":
            break


if __name__ == "__main__":
    asyncio.run(main())
