from typing import Any, Optional, List
import httpx
import os
from datetime import datetime
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class QAAgent(BaseAgent):
    """
    Agent for quality assurance.

    Capabilities:
    - Create and manage QA checklists (API)
    - Run QA reviews (API)
    - Log and track issues (API)
    - Visual regression testing (Browser)
    - Landing page verification (Browser)
    - Screenshot capture for proof (Browser)
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        instance_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.instance_id = instance_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        # Browser for visual QA
        session_name = f"qa_{instance_id}" if instance_id else "qa"
        self.browser = AgentBrowserSkill(session_name=session_name)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "qa_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a quality assurance expert.

Your role is to ensure quality of all deliverables:
1. Review content against checklists
2. Verify landing pages are live and correct
3. Capture visual proof for client sign-off
4. Track and manage QA issues
5. Perform visual regression testing

You have browser automation for visual QA:
- Verify landing pages load correctly before campaigns launch
- Capture screenshots as proof of work
- Compare page states for visual regression

Always document findings with screenshots."""

    def _define_tools(self) -> list[dict]:
        return [
            # ===== API-Based Tools =====
            {
                "name": "create_qa_checklist",
                "description": "Create QA checklist for a deliverable type.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deliverable_type": {"type": "string"},
                        "items": {"type": "array", "items": {"type": "object"}},
                    },
                    "required": ["deliverable_type"],
                },
            },
            {
                "name": "run_qa_review",
                "description": "Run QA review on deliverable.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deliverable_id": {"type": "string"},
                        "checklist_id": {"type": "string"},
                    },
                    "required": ["deliverable_id"],
                },
            },
            {
                "name": "log_issue",
                "description": "Log QA issue found during review.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deliverable_id": {"type": "string"},
                        "issue": {"type": "object"},
                    },
                    "required": ["deliverable_id", "issue"],
                },
            },
            {
                "name": "get_qa_status",
                "description": "Get QA status for a project.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                    },
                    "required": ["project_id"],
                },
            },
            {
                "name": "approve_qa",
                "description": "Approve QA review.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "review_id": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["review_id"],
                },
            },
            # ===== Browser-Based Tools =====
            {
                "name": "verify_landing_page",
                "description": "Verify a landing page is live and capture screenshot proof.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Landing page URL to verify"},
                        "campaign_id": {"type": "string", "description": "Associated campaign ID"},
                        "expected_elements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Text/elements expected to be present",
                        },
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "capture_visual_baseline",
                "description": "Capture screenshot baseline for future visual regression.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "baseline_name": {"type": "string", "description": "Name for this baseline"},
                    },
                    "required": ["url", "baseline_name"],
                },
            },
            {
                "name": "check_visual_regression",
                "description": "Compare current page state against baseline for changes.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "baseline_name": {"type": "string"},
                    },
                    "required": ["url", "baseline_name"],
                },
            },
            {
                "name": "verify_multiple_pages",
                "description": "Verify multiple landing pages in batch.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "urls": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of URLs to verify",
                        },
                        "campaign_id": {"type": "string"},
                    },
                    "required": ["urls"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            # ===== API-Based Tools =====
            if tool_name == "create_qa_checklist":
                response = await self.http_client.post(
                    "/api/v1/qa/checklists",
                    json=tool_input
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}

            elif tool_name == "run_qa_review":
                return {"status": "ready", "instruction": "Review deliverable against quality checklist."}

            elif tool_name == "log_issue":
                response = await self.http_client.post(
                    f"/api/v1/qa/deliverables/{tool_input['deliverable_id']}/issues",
                    json=tool_input["issue"]
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}

            elif tool_name == "get_qa_status":
                response = await self.http_client.get(
                    f"/api/v1/qa/projects/{tool_input['project_id']}/status"
                )
                return response.json() if response.status_code == 200 else {"status": None}

            elif tool_name == "approve_qa":
                response = await self.http_client.post(
                    f"/api/v1/qa/reviews/{tool_input['review_id']}/approve",
                    json=tool_input
                )
                return response.json() if response.status_code == 200 else {"error": "Failed"}

            # ===== Browser-Based Tools =====
            elif tool_name == "verify_landing_page":
                return await self._verify_landing_page(
                    url=tool_input["url"],
                    campaign_id=tool_input.get("campaign_id"),
                    expected=tool_input.get("expected_elements", []),
                )

            elif tool_name == "capture_visual_baseline":
                return await self._capture_baseline(
                    url=tool_input["url"],
                    name=tool_input["baseline_name"],
                )

            elif tool_name == "check_visual_regression":
                return await self._check_regression(
                    url=tool_input["url"],
                    name=tool_input["baseline_name"],
                )

            elif tool_name == "verify_multiple_pages":
                return await self._verify_multiple(
                    urls=tool_input["urls"],
                    campaign_id=tool_input.get("campaign_id"),
                )

            return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # Browser-Based Implementations
    # =========================================================================

    async def _verify_landing_page(
        self,
        url: str,
        campaign_id: Optional[str] = None,
        expected: List[str] = None
    ) -> dict:
        """Verify landing page is live and capture proof."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            # Get page snapshot
            snapshot = await self.browser.snapshot(interactive_only=False)

            # Check for expected elements
            found_elements = []
            missing_elements = []
            if expected:
                for element in expected:
                    if element.lower() in snapshot.raw.lower():
                        found_elements.append(element)
                    else:
                        missing_elements.append(element)

            # Capture proof screenshot
            output_dir = "/tmp/qa_proofs"
            os.makedirs(output_dir, exist_ok=True)
            prefix = f"landing_{campaign_id}" if campaign_id else "landing"
            screenshot_path = await self.browser.capture_proof(
                url=url,
                output_dir=output_dir,
                prefix=prefix
            )

            return {
                "url": url,
                "campaign_id": campaign_id,
                "status": "verified" if not missing_elements else "issues_found",
                "found_elements": found_elements,
                "missing_elements": missing_elements,
                "screenshot": screenshot_path,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"url": url, "status": "error", "error": str(e)}

    async def _capture_baseline(self, url: str, name: str) -> dict:
        """Capture visual baseline for regression testing."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            # Create baseline directory
            baseline_dir = f"/tmp/qa_baselines/{self.instance_id or 'default'}"
            os.makedirs(baseline_dir, exist_ok=True)

            # Capture baseline screenshot
            filename = f"{name}_{datetime.now().strftime('%Y%m%d')}.png"
            filepath = os.path.join(baseline_dir, filename)
            await self.browser.screenshot(filepath)

            return {
                "url": url,
                "baseline_name": name,
                "baseline_path": filepath,
                "captured_at": datetime.now().isoformat(),
                "status": "baseline_captured",
            }

        except Exception as e:
            return {"error": f"Baseline capture failed: {str(e)}"}

    async def _check_regression(self, url: str, name: str) -> dict:
        """Check for visual regression against baseline."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            # Capture current state
            current_dir = f"/tmp/qa_current/{self.instance_id or 'default'}"
            os.makedirs(current_dir, exist_ok=True)
            current_path = os.path.join(current_dir, f"{name}_current.png")
            await self.browser.screenshot(current_path)

            # Find baseline
            baseline_dir = f"/tmp/qa_baselines/{self.instance_id or 'default'}"
            baseline_files = [f for f in os.listdir(baseline_dir) if f.startswith(name)] if os.path.exists(baseline_dir) else []

            if not baseline_files:
                return {
                    "url": url,
                    "baseline_name": name,
                    "status": "no_baseline",
                    "current_screenshot": current_path,
                    "message": "No baseline found. Capture baseline first.",
                }

            # Latest baseline
            baseline_path = os.path.join(baseline_dir, sorted(baseline_files)[-1])

            # Note: Actual image comparison would require PIL/opencv
            # For now, return paths for manual comparison or external tool
            return {
                "url": url,
                "baseline_name": name,
                "baseline_path": baseline_path,
                "current_path": current_path,
                "status": "ready_for_comparison",
                "message": "Screenshots captured. Compare visually or use image diff tool.",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": f"Regression check failed: {str(e)}"}

    async def _verify_multiple(
        self,
        urls: List[str],
        campaign_id: Optional[str] = None
    ) -> dict:
        """Verify multiple landing pages."""
        results = []
        for url in urls:
            result = await self._verify_landing_page(
                url=url,
                campaign_id=campaign_id,
            )
            results.append(result)

        # Summary
        verified = sum(1 for r in results if r.get("status") == "verified")
        issues = sum(1 for r in results if r.get("status") == "issues_found")
        errors = sum(1 for r in results if r.get("status") == "error")

        return {
            "campaign_id": campaign_id,
            "total": len(urls),
            "verified": verified,
            "issues_found": issues,
            "errors": errors,
            "results": results,
        }

    async def close(self):
        """Cleanup resources."""
        await self.http_client.aclose()
        await self.browser.close()
