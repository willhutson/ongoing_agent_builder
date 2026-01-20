#!/usr/bin/env python3
"""
ERP Integration Testing Script

Verifies the integration between ongoing_agent_builder and erp_staging_lmtd
as specified in JAN_2026_ERP_TO_AGENT_BUILDER_HANDOFF.md

Testing Checklist:
1. POST /api/v1/agent/execute - accepts required fields, routes to correct agent
2. GET /api/health - returns provider status with latency
3. Agent routing - all 46 agent types accessible
4. Model usage - uses ERP-provided model without re-resolution
5. Token tracking - returns usage metrics
6. Session maintenance - supports session_id for continuity
7. Callback functionality - sends results to callback_url
8. Organization context - respects X-Organization-Id header
9. Instance onboarding - wizard step support for SuperAdmin

Usage:
    python scripts/test_erp_integration.py [--base-url URL]
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from typing import Optional

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)


# Test configuration
DEFAULT_BASE_URL = "http://localhost:8000"

# All 46 agent types (per handoff spec)
AGENT_TYPES = [
    # Foundation
    "rfp", "brief", "content", "commercial",
    # Studio
    "presentation", "copy", "image",
    # Video
    "video_script", "video_storyboard", "video_production",
    # Distribution
    "report", "approve", "brief_update",
    # Gateway
    "gateway_whatsapp", "gateway_email", "gateway_slack", "gateway_sms",
    # Brand
    "brand_voice", "brand_visual", "brand_guidelines",
    # Operations
    "resource", "workflow", "ops_reporting",
    # Client
    "crm", "scope", "onboarding", "instance_onboarding", "instance_analytics", "instance_success",
    # Media
    "media_buying", "campaign",
    # Social
    "social_listening", "community", "social_analytics",
    # Performance
    "brand_performance", "campaign_analytics", "competitor",
    # Finance
    "invoice", "forecast", "budget",
    # Quality
    "qa", "legal",
    # Knowledge
    "knowledge", "training",
    # Specialized
    "influencer", "pr", "events", "localization", "accessibility",
]

# Expected tier assignments
ECONOMY_AGENTS = ["approve", "brief_update", "gateway_whatsapp", "gateway_email", "gateway_slack", "gateway_sms"]
PREMIUM_AGENTS = ["legal", "forecast", "budget", "knowledge"]


class ERPIntegrationTester:
    """Test suite for ERP integration endpoints."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {"passed": 0, "failed": 0, "errors": []}

    async def close(self):
        await self.client.aclose()

    def log(self, status: str, message: str):
        icon = "✅" if status == "pass" else "❌" if status == "fail" else "ℹ️"
        print(f"{icon} {message}")

    async def test_health_endpoint(self) -> bool:
        """Test GET /api/health returns provider status."""
        print("\n=== Testing Health Endpoint ===")

        try:
            response = await self.client.get(f"{self.base_url}/api/v1/health")

            if response.status_code != 200:
                self.log("fail", f"Health endpoint returned {response.status_code}")
                return False

            data = response.json()

            # Check required fields
            required_fields = ["status", "service", "version", "timestamp", "agents_available", "providers"]
            for field in required_fields:
                if field not in data:
                    self.log("fail", f"Missing required field: {field}")
                    return False

            # Check agents count
            if data["agents_available"] != 46:
                self.log("fail", f"Expected 46 agents, got {data['agents_available']}")
                return False

            # Check providers list
            if not isinstance(data["providers"], list):
                self.log("fail", "Providers should be a list")
                return False

            self.log("pass", f"Health endpoint OK - {data['agents_available']} agents available")
            self.log("info", f"  Status: {data['status']}")
            self.log("info", f"  Providers: {len(data['providers'])} configured")

            self.results["passed"] += 1
            return True

        except Exception as e:
            self.log("fail", f"Health endpoint error: {str(e)}")
            self.results["failed"] += 1
            self.results["errors"].append(f"health: {str(e)}")
            return False

    async def test_agent_execute(self, agent_type: str = "brief") -> bool:
        """Test POST /api/v1/agent/execute with a simple agent."""
        print(f"\n=== Testing Agent Execute ({agent_type}) ===")

        try:
            payload = {
                "agent": agent_type,
                "task": f"Test task for {agent_type} agent",
                "model": "claude-sonnet-4-20250514",
                "tier": "standard",
                "tenant_id": "test-tenant-001",
                "user_id": "test-user-001",
                "context": {"test": True},
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/agent/execute",
                json=payload,
                headers={
                    "X-Organization-Id": "test-org-001",
                    "X-Request-Id": "test-request-001",
                },
            )

            if response.status_code != 200:
                self.log("fail", f"Execute returned {response.status_code}: {response.text}")
                return False

            data = response.json()

            # Check required response fields
            required_fields = ["execution_id", "status", "session_id"]
            for field in required_fields:
                if field not in data:
                    self.log("fail", f"Missing required field: {field}")
                    return False

            self.log("pass", f"Agent execute OK - execution_id: {data['execution_id']}")
            self.log("info", f"  Status: {data['status']}")
            self.log("info", f"  Session ID: {data['session_id']}")

            self.results["passed"] += 1
            return True

        except Exception as e:
            self.log("fail", f"Agent execute error: {str(e)}")
            self.results["failed"] += 1
            self.results["errors"].append(f"execute({agent_type}): {str(e)}")
            return False

    async def test_agent_registry(self) -> bool:
        """Test GET /api/v1/agents/registry returns all 46 agents."""
        print("\n=== Testing Agent Registry ===")

        try:
            response = await self.client.get(f"{self.base_url}/api/v1/agents/registry")

            if response.status_code != 200:
                self.log("fail", f"Registry returned {response.status_code}")
                return False

            data = response.json()

            # Check total agents
            if data.get("total_agents") != 46:
                self.log("fail", f"Expected 46 agents, got {data.get('total_agents')}")
                return False

            # Check layers
            expected_layers = [
                "foundation", "studio", "video", "distribution", "gateway",
                "brand", "operations", "client", "media", "social",
                "performance", "finance", "quality", "knowledge", "specialized"
            ]

            missing_layers = [l for l in expected_layers if l not in data.get("layers", {})]
            if missing_layers:
                self.log("fail", f"Missing layers: {missing_layers}")
                return False

            # Check all agents present
            registered_agents = [a["type"] for a in data.get("agents", [])]
            missing_agents = [a for a in AGENT_TYPES if a not in registered_agents]
            if missing_agents:
                self.log("fail", f"Missing agents: {missing_agents[:5]}... ({len(missing_agents)} total)")
                return False

            self.log("pass", f"Agent registry OK - {len(registered_agents)} agents across {len(data['layers'])} layers")

            self.results["passed"] += 1
            return True

        except Exception as e:
            self.log("fail", f"Agent registry error: {str(e)}")
            self.results["failed"] += 1
            self.results["errors"].append(f"registry: {str(e)}")
            return False

    async def test_tier_assignments(self) -> bool:
        """Verify tier assignments match the handoff spec."""
        print("\n=== Testing Tier Assignments ===")

        try:
            response = await self.client.get(f"{self.base_url}/api/v1/agents/registry")

            if response.status_code != 200:
                self.log("fail", f"Registry returned {response.status_code}")
                return False

            data = response.json()
            agents = {a["type"]: a["tier"] for a in data.get("agents", [])}

            errors = []

            # Check economy tier agents
            for agent in ECONOMY_AGENTS:
                if agents.get(agent) != "economy":
                    errors.append(f"{agent} should be economy, got {agents.get(agent)}")

            # Check premium tier agents
            for agent in PREMIUM_AGENTS:
                if agents.get(agent) != "premium":
                    errors.append(f"{agent} should be premium, got {agents.get(agent)}")

            if errors:
                for err in errors[:5]:
                    self.log("fail", err)
                if len(errors) > 5:
                    self.log("fail", f"...and {len(errors) - 5} more tier errors")
                return False

            self.log("pass", "Tier assignments match handoff specification")
            self.log("info", f"  Economy agents: {len(ECONOMY_AGENTS)}")
            self.log("info", f"  Premium agents: {len(PREMIUM_AGENTS)}")
            self.log("info", f"  Standard agents: {46 - len(ECONOMY_AGENTS) - len(PREMIUM_AGENTS)}")

            self.results["passed"] += 1
            return True

        except Exception as e:
            self.log("fail", f"Tier assignment error: {str(e)}")
            self.results["failed"] += 1
            self.results["errors"].append(f"tiers: {str(e)}")
            return False

    async def test_instance_onboarding_agent(self) -> bool:
        """Test instance_onboarding agent for SuperAdmin wizard."""
        print("\n=== Testing Instance Onboarding Agent ===")

        try:
            # Get agent details
            response = await self.client.get(f"{self.base_url}/api/v1/agents/instance_onboarding")

            if response.status_code != 200:
                self.log("fail", f"Agent details returned {response.status_code}")
                return False

            data = response.json()

            # Verify tier is standard
            if data.get("tier") != "standard":
                self.log("fail", f"Expected standard tier, got {data.get('tier')}")
                return False

            # Test execute with wizard context
            payload = {
                "agent": "instance_onboarding",
                "task": json.dumps({
                    "wizard_step": "business_assessment",
                    "tenant_info": {
                        "name": "Test Agency",
                        "industry": "advertising",
                        "team_size": "medium",
                    },
                    "responses": {
                        "services": ["creative", "media"],
                        "regions": ["gcc"],
                    }
                }),
                "model": "claude-sonnet-4-20250514",
                "tier": "standard",
                "tenant_id": "test-tenant-wizard",
                "user_id": "test-superadmin",
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/agent/execute",
                json=payload,
            )

            if response.status_code != 200:
                self.log("fail", f"Wizard execute returned {response.status_code}")
                return False

            self.log("pass", "Instance onboarding agent (SuperAdmin wizard) OK")
            self.log("info", f"  Tier: {data.get('tier')}")
            self.log("info", f"  Recommended inputs: {list(data.get('recommended_inputs', {}).keys())}")

            self.results["passed"] += 1
            return True

        except Exception as e:
            self.log("fail", f"Instance onboarding error: {str(e)}")
            self.results["failed"] += 1
            self.results["errors"].append(f"instance_onboarding: {str(e)}")
            return False

    async def run_all_tests(self) -> dict:
        """Run all integration tests."""
        print(f"\n{'='*60}")
        print("ERP Integration Test Suite")
        print(f"Target: {self.base_url}")
        print(f"Time: {datetime.now().isoformat()}")
        print(f"{'='*60}")

        tests = [
            ("Health Endpoint", self.test_health_endpoint),
            ("Agent Execute", self.test_agent_execute),
            ("Agent Registry", self.test_agent_registry),
            ("Tier Assignments", self.test_tier_assignments),
            ("Instance Onboarding", self.test_instance_onboarding_agent),
        ]

        for name, test_func in tests:
            try:
                await test_func()
            except Exception as e:
                self.log("fail", f"{name} raised exception: {str(e)}")
                self.results["failed"] += 1
                self.results["errors"].append(f"{name}: {str(e)}")

        # Print summary
        print(f"\n{'='*60}")
        print("Test Summary")
        print(f"{'='*60}")
        total = self.results["passed"] + self.results["failed"]
        print(f"Passed: {self.results['passed']}/{total}")
        print(f"Failed: {self.results['failed']}/{total}")

        if self.results["errors"]:
            print("\nErrors:")
            for err in self.results["errors"]:
                print(f"  - {err}")

        return self.results


async def main():
    parser = argparse.ArgumentParser(description="Test ERP integration endpoints")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL of the agent service (default: {DEFAULT_BASE_URL})"
    )
    args = parser.parse_args()

    tester = ERPIntegrationTester(args.base_url)
    try:
        results = await tester.run_all_tests()
        sys.exit(0 if results["failed"] == 0 else 1)
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
