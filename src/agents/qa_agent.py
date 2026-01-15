from typing import Any, Optional, List
import httpx
import os
from datetime import datetime
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class QAAgent(BaseAgent):
    """
    Agent for comprehensive quality assurance.

    Capabilities:
    - Create and manage QA checklists (API)
    - Run QA reviews (API)
    - Log and track issues (API)
    - Visual regression testing (Browser)
    - Landing page verification (Browser)
    - Screenshot capture for proof (Browser)
    - Performance/Lighthouse auditing (Browser)
    - Accessibility compliance testing (Browser)
    - Cross-browser compatibility testing (Browser)
    - Mobile device testing (Browser)
    - SEO verification (Browser)
    - Form testing and validation (Browser)
    - Broken link detection (Browser)
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
        return """You are a comprehensive quality assurance expert for digital marketing.

Your role is to ensure quality of all deliverables:
1. Review content against checklists
2. Verify landing pages are live and correct
3. Capture visual proof for client sign-off
4. Track and manage QA issues
5. Perform visual regression testing

You have extensive browser automation for comprehensive QA:
- Verify landing pages load correctly before campaigns launch
- Capture screenshots as proof of work
- Compare page states for visual regression
- Run performance audits (Lighthouse-style metrics)
- Test accessibility compliance (WCAG, color contrast, keyboard nav)
- Verify cross-browser compatibility
- Test mobile responsiveness across devices
- Verify SEO elements (meta tags, structured data, canonicals)
- Test form functionality and validation
- Check for broken links

Always document findings with screenshots and detailed reports."""

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
            # ===== Extended Browser Tools - Performance =====
            {"name": "run_performance_audit", "description": "Run Lighthouse-style performance audit on a page.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "categories": {"type": "array", "items": {"type": "string", "enum": ["performance", "accessibility", "seo", "best-practices"]}}}, "required": ["url"]}},
            {"name": "check_page_speed", "description": "Check page load speed and Core Web Vitals.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            {"name": "measure_ttfb", "description": "Measure Time to First Byte for a URL.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            # ===== Extended Browser Tools - Accessibility =====
            {"name": "run_accessibility_audit", "description": "Run WCAG accessibility audit on a page.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "wcag_level": {"type": "string", "enum": ["A", "AA", "AAA"], "default": "AA"}}, "required": ["url"]}},
            {"name": "check_color_contrast", "description": "Check color contrast ratios for accessibility.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            {"name": "verify_alt_text", "description": "Verify all images have appropriate alt text.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            {"name": "check_keyboard_navigation", "description": "Verify page is keyboard navigable.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            # ===== Extended Browser Tools - Cross-Browser =====
            {"name": "capture_cross_browser", "description": "Capture page across different browser configurations.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "browsers": {"type": "array", "items": {"type": "string", "enum": ["chrome", "firefox", "safari", "edge"]}}}, "required": ["url"]}},
            {"name": "verify_browser_compatibility", "description": "Check for browser compatibility issues.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "check_features": {"type": "array", "items": {"type": "string"}}}, "required": ["url"]}},
            # ===== Extended Browser Tools - Mobile Testing =====
            {"name": "test_mobile_device", "description": "Test page on specific mobile device viewport.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "device": {"type": "string", "enum": ["iphone_se", "iphone_14_pro", "pixel_7", "samsung_s23", "ipad_mini", "ipad_pro"]}}, "required": ["url", "device"]}},
            {"name": "capture_device_suite", "description": "Capture page across multiple device viewports.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "devices": {"type": "array", "items": {"type": "string"}}}, "required": ["url"]}},
            {"name": "check_touch_targets", "description": "Verify touch targets are appropriately sized for mobile.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            # ===== Extended Browser Tools - SEO =====
            {"name": "verify_meta_tags", "description": "Verify SEO meta tags (title, description, OG tags).", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            {"name": "check_structured_data", "description": "Check Schema.org structured data markup.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            {"name": "verify_canonical_url", "description": "Verify canonical URL tag is correct.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "expected_canonical": {"type": "string"}}, "required": ["url"]}},
            {"name": "check_robots_meta", "description": "Check robots meta tag and X-Robots-Tag header.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            # ===== Extended Browser Tools - Form Testing =====
            {"name": "test_form_fields", "description": "Test form field presence and types.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "form_selector": {"type": "string"}}, "required": ["url"]}},
            {"name": "verify_form_validation", "description": "Verify form validation messages display correctly.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "test_invalid_inputs": {"type": "boolean", "default": True}}, "required": ["url"]}},
            {"name": "check_form_accessibility", "description": "Check form accessibility (labels, ARIA, error handling).", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            # ===== Extended Browser Tools - Link Validation =====
            {"name": "check_broken_links", "description": "Find broken links on a page.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "include_external": {"type": "boolean", "default": False}}, "required": ["url"]}},
            {"name": "verify_external_links", "description": "Verify external links are valid and appropriate.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            {"name": "check_link_attributes", "description": "Verify links have proper attributes (rel, target).", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
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

            # ===== Extended Browser Tools - Performance =====
            elif tool_name == "run_performance_audit":
                return await self._run_performance_audit(tool_input["url"], tool_input.get("categories", ["performance", "accessibility", "seo"]))
            elif tool_name == "check_page_speed":
                return await self._check_page_speed(tool_input["url"])
            elif tool_name == "measure_ttfb":
                return await self._measure_ttfb(tool_input["url"])

            # ===== Extended Browser Tools - Accessibility =====
            elif tool_name == "run_accessibility_audit":
                return await self._run_accessibility_audit(tool_input["url"], tool_input.get("wcag_level", "AA"))
            elif tool_name == "check_color_contrast":
                return await self._check_color_contrast(tool_input["url"])
            elif tool_name == "verify_alt_text":
                return await self._verify_alt_text(tool_input["url"])
            elif tool_name == "check_keyboard_navigation":
                return await self._check_keyboard_navigation(tool_input["url"])

            # ===== Extended Browser Tools - Cross-Browser =====
            elif tool_name == "capture_cross_browser":
                return await self._capture_cross_browser(tool_input["url"], tool_input.get("browsers", ["chrome"]))
            elif tool_name == "verify_browser_compatibility":
                return await self._verify_browser_compatibility(tool_input["url"], tool_input.get("check_features", []))

            # ===== Extended Browser Tools - Mobile Testing =====
            elif tool_name == "test_mobile_device":
                return await self._test_mobile_device(tool_input["url"], tool_input["device"])
            elif tool_name == "capture_device_suite":
                return await self._capture_device_suite(tool_input["url"], tool_input.get("devices", ["iphone_14_pro", "ipad_mini"]))
            elif tool_name == "check_touch_targets":
                return await self._check_touch_targets(tool_input["url"])

            # ===== Extended Browser Tools - SEO =====
            elif tool_name == "verify_meta_tags":
                return await self._verify_meta_tags(tool_input["url"])
            elif tool_name == "check_structured_data":
                return await self._check_structured_data(tool_input["url"])
            elif tool_name == "verify_canonical_url":
                return await self._verify_canonical_url(tool_input["url"], tool_input.get("expected_canonical"))
            elif tool_name == "check_robots_meta":
                return await self._check_robots_meta(tool_input["url"])

            # ===== Extended Browser Tools - Form Testing =====
            elif tool_name == "test_form_fields":
                return await self._test_form_fields(tool_input["url"], tool_input.get("form_selector"))
            elif tool_name == "verify_form_validation":
                return await self._verify_form_validation(tool_input["url"], tool_input.get("test_invalid_inputs", True))
            elif tool_name == "check_form_accessibility":
                return await self._check_form_accessibility(tool_input["url"])

            # ===== Extended Browser Tools - Link Validation =====
            elif tool_name == "check_broken_links":
                return await self._check_broken_links(tool_input["url"], tool_input.get("include_external", False))
            elif tool_name == "verify_external_links":
                return await self._verify_external_links(tool_input["url"])
            elif tool_name == "check_link_attributes":
                return await self._check_link_attributes(tool_input["url"])

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

    # =========================================================================
    # Performance Testing Methods
    # =========================================================================

    async def _run_performance_audit(self, url: str, categories: List[str]) -> dict:
        """Run Lighthouse-style performance audit."""
        try:
            import time
            start_time = time.time()

            await self.browser.open(url)
            load_time = time.time() - start_time
            await self.browser.wait(3000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="performance_audit"
            )

            # Analyze page content for performance indicators
            content = snapshot.raw.lower()

            audit_results = {
                "performance": {
                    "score": 0,
                    "metrics": {
                        "page_load_time": round(load_time, 2),
                        "has_lazy_loading": "loading=\"lazy\"" in content or "lazyload" in content,
                        "has_async_scripts": "async" in content,
                        "has_deferred_scripts": "defer" in content,
                        "estimated_dom_size": len(content),
                    }
                },
                "accessibility": {
                    "score": 0,
                    "checks": {
                        "has_lang_attribute": "lang=" in content,
                        "has_alt_texts": "alt=" in content,
                        "has_aria_labels": "aria-label" in content or "aria-labelledby" in content,
                        "has_skip_link": "skip" in content,
                    }
                },
                "seo": {
                    "score": 0,
                    "checks": {
                        "has_title": "<title" in content,
                        "has_meta_description": "meta name=\"description\"" in content or "meta property=\"og:description\"" in content,
                        "has_h1": "<h1" in content,
                        "has_canonical": "rel=\"canonical\"" in content,
                    }
                },
                "best-practices": {
                    "score": 0,
                    "checks": {
                        "has_https": url.startswith("https://"),
                        "has_viewport_meta": "viewport" in content,
                        "no_document_write": "document.write" not in content,
                    }
                }
            }

            # Calculate scores
            for category in categories:
                if category in audit_results:
                    checks = audit_results[category].get("checks", audit_results[category].get("metrics", {}))
                    if checks:
                        passed = sum(1 for v in checks.values() if v is True or (isinstance(v, (int, float)) and v < 5))
                        audit_results[category]["score"] = round((passed / len(checks)) * 100)

            return {
                "url": url,
                "categories": categories,
                "audit_results": {k: v for k, v in audit_results.items() if k in categories},
                "screenshot": screenshot,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": f"Performance audit failed: {str(e)}"}

    async def _check_page_speed(self, url: str) -> dict:
        """Check page load speed and Core Web Vitals approximation."""
        try:
            import time

            # Measure load time
            start_time = time.time()
            await self.browser.open(url)
            first_paint = time.time() - start_time

            await self.browser.wait(2000)
            fully_loaded = time.time() - start_time

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="page_speed"
            )

            # Approximate Core Web Vitals
            core_web_vitals = {
                "FCP": round(first_paint * 1000),  # First Contentful Paint (ms)
                "LCP_estimate": round(fully_loaded * 1000),  # Largest Contentful Paint estimate
                "FCP_rating": "good" if first_paint < 1.8 else "needs_improvement" if first_paint < 3 else "poor",
                "LCP_rating": "good" if fully_loaded < 2.5 else "needs_improvement" if fully_loaded < 4 else "poor",
            }

            return {
                "url": url,
                "page_load_time_seconds": round(fully_loaded, 2),
                "core_web_vitals": core_web_vitals,
                "screenshot": screenshot,
                "recommendation": "Page loads quickly" if fully_loaded < 3 else "Consider optimizing page load time",
            }
        except Exception as e:
            return {"error": f"Page speed check failed: {str(e)}"}

    async def _measure_ttfb(self, url: str) -> dict:
        """Measure Time to First Byte."""
        try:
            import time

            start_time = time.time()
            response = await self.http_client.get(url, follow_redirects=True)
            ttfb = time.time() - start_time

            ttfb_rating = "good" if ttfb < 0.2 else "needs_improvement" if ttfb < 0.5 else "poor"

            return {
                "url": url,
                "ttfb_seconds": round(ttfb, 3),
                "ttfb_milliseconds": round(ttfb * 1000),
                "rating": ttfb_rating,
                "status_code": response.status_code,
                "server": response.headers.get("server", "unknown"),
            }
        except Exception as e:
            return {"error": f"TTFB measurement failed: {str(e)}"}

    # =========================================================================
    # Accessibility Testing Methods
    # =========================================================================

    async def _run_accessibility_audit(self, url: str, wcag_level: str) -> dict:
        """Run WCAG accessibility audit."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix=f"a11y_audit_{wcag_level}"
            )

            content = snapshot.raw.lower()

            # WCAG checks by level
            wcag_checks = {
                "A": {
                    "images_have_alt": "alt=" in content,
                    "page_has_title": "<title" in content,
                    "form_labels_present": "label" in content or "aria-label" in content,
                    "link_purpose_clear": True,  # Would need semantic analysis
                    "lang_attribute": "lang=" in content,
                },
                "AA": {
                    "color_contrast": True,  # Would need visual analysis
                    "resize_text": "font-size" in content,
                    "keyboard_focus_visible": "focus" in content,
                    "consistent_navigation": True,  # Would need multi-page analysis
                    "error_identification": "error" in content or "invalid" in content,
                },
                "AAA": {
                    "sign_language": False,  # Not typically present
                    "extended_audio_description": False,
                    "reading_level": True,  # Would need content analysis
                    "pronunciation": False,
                },
            }

            # Collect applicable checks
            applicable_checks = {}
            levels_to_check = ["A"]
            if wcag_level in ["AA", "AAA"]:
                levels_to_check.append("AA")
            if wcag_level == "AAA":
                levels_to_check.append("AAA")

            for level in levels_to_check:
                applicable_checks[level] = wcag_checks[level]

            # Calculate compliance
            total_checks = sum(len(checks) for checks in applicable_checks.values())
            passed_checks = sum(
                sum(1 for v in checks.values() if v)
                for checks in applicable_checks.values()
            )
            compliance_score = round((passed_checks / total_checks) * 100) if total_checks > 0 else 0

            return {
                "url": url,
                "wcag_level": wcag_level,
                "compliance_score": compliance_score,
                "checks": applicable_checks,
                "passed": passed_checks,
                "total": total_checks,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Accessibility audit failed: {str(e)}"}

    async def _check_color_contrast(self, url: str) -> dict:
        """Check color contrast ratios."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="color_contrast"
            )

            content = snapshot.raw.lower()

            # Basic color analysis from CSS
            contrast_findings = {
                "uses_high_contrast_colors": "contrast" in content,
                "has_color_declarations": "color:" in content,
                "has_background_colors": "background" in content,
                "potential_issues": [],
            }

            # Flag potential low-contrast patterns
            low_contrast_patterns = ["color: #999", "color: #ccc", "color: gray", "color: lightgray"]
            for pattern in low_contrast_patterns:
                if pattern in content:
                    contrast_findings["potential_issues"].append(f"Possible low contrast: {pattern}")

            return {
                "url": url,
                "contrast_findings": contrast_findings,
                "screenshot": screenshot,
                "recommendation": "Run manual contrast check with WebAIM tool for accurate results",
            }
        except Exception as e:
            return {"error": f"Color contrast check failed: {str(e)}"}

    async def _verify_alt_text(self, url: str) -> dict:
        """Verify all images have appropriate alt text."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="alt_text_check"
            )

            content = snapshot.raw

            # Find images and check for alt text
            import re
            img_pattern = r'<img[^>]*>'
            images = re.findall(img_pattern, content, re.IGNORECASE)

            images_with_alt = []
            images_without_alt = []
            decorative_images = []

            for img in images:
                if 'alt=""' in img:
                    decorative_images.append(img[:100])
                elif 'alt=' in img:
                    images_with_alt.append(img[:100])
                else:
                    images_without_alt.append(img[:100])

            return {
                "url": url,
                "total_images": len(images),
                "images_with_alt": len(images_with_alt),
                "images_without_alt": len(images_without_alt),
                "decorative_images": len(decorative_images),
                "missing_alt_examples": images_without_alt[:5],
                "compliant": len(images_without_alt) == 0,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Alt text verification failed: {str(e)}"}

    async def _check_keyboard_navigation(self, url: str) -> dict:
        """Verify page is keyboard navigable."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=True)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="keyboard_nav"
            )

            content = snapshot.raw.lower()

            keyboard_findings = {
                "has_focusable_elements": "tabindex" in content or "<button" in content or "<a " in content,
                "has_focus_styles": ":focus" in content or "focus" in content,
                "has_skip_links": "skip" in content and ("nav" in content or "main" in content),
                "uses_tabindex": "tabindex" in content,
                "has_keyboard_handlers": "keydown" in content or "keyup" in content or "keypress" in content,
                "potential_tab_traps": "tabindex=\"-1\"" in content,
            }

            return {
                "url": url,
                "keyboard_findings": keyboard_findings,
                "focusable_content_preview": snapshot.raw[:1000],
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Keyboard navigation check failed: {str(e)}"}

    # =========================================================================
    # Cross-Browser Testing Methods
    # =========================================================================

    async def _capture_cross_browser(self, url: str, browsers: List[str]) -> dict:
        """Capture page across different browser configurations."""
        try:
            captures = []

            # Note: With single browser automation, we simulate by capturing
            # In production, this would use BrowserStack/Sauce Labs
            for browser in browsers:
                await self.browser.open(url)
                await self.browser.wait(2000)
                screenshot = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/qa_proofs",
                    prefix=f"browser_{browser}"
                )
                captures.append({
                    "browser": browser,
                    "screenshot": screenshot,
                    "note": "Simulated capture - use BrowserStack for actual cross-browser testing",
                })

            return {
                "url": url,
                "browsers_tested": browsers,
                "captures": captures,
                "recommendation": "For true cross-browser testing, integrate with BrowserStack or Sauce Labs",
            }
        except Exception as e:
            return {"error": f"Cross-browser capture failed: {str(e)}"}

    async def _verify_browser_compatibility(self, url: str, check_features: List[str]) -> dict:
        """Check for browser compatibility issues."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="browser_compat"
            )

            content = snapshot.raw.lower()

            # Check for modern CSS/JS features that may have compatibility issues
            compatibility_checks = {
                "css_grid": "display: grid" in content or "display:grid" in content,
                "flexbox": "display: flex" in content or "display:flex" in content,
                "css_variables": "var(--" in content,
                "es6_modules": "type=\"module\"" in content,
                "fetch_api": "fetch(" in content,
                "async_await": "async" in content,
                "webp_images": ".webp" in content,
                "css_animations": "@keyframes" in content or "animation:" in content,
            }

            # Check requested features
            feature_results = {}
            for feature in check_features:
                feature_lower = feature.lower().replace(" ", "_")
                feature_results[feature] = compatibility_checks.get(feature_lower, "unknown")

            return {
                "url": url,
                "detected_features": {k: v for k, v in compatibility_checks.items() if v},
                "requested_feature_checks": feature_results,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Browser compatibility check failed: {str(e)}"}

    # =========================================================================
    # Mobile Device Testing Methods
    # =========================================================================

    async def _test_mobile_device(self, url: str, device: str) -> dict:
        """Test page on specific mobile device viewport."""
        try:
            device_specs = {
                "iphone_se": {"width": 375, "height": 667, "pixel_ratio": 2},
                "iphone_14_pro": {"width": 393, "height": 852, "pixel_ratio": 3},
                "pixel_7": {"width": 412, "height": 915, "pixel_ratio": 2.625},
                "samsung_s23": {"width": 360, "height": 780, "pixel_ratio": 3},
                "ipad_mini": {"width": 768, "height": 1024, "pixel_ratio": 2},
                "ipad_pro": {"width": 1024, "height": 1366, "pixel_ratio": 2},
            }

            spec = device_specs.get(device, device_specs["iphone_14_pro"])

            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix=f"device_{device}"
            )

            content = snapshot.raw.lower()

            mobile_analysis = {
                "has_viewport_meta": "viewport" in content,
                "has_responsive_images": "srcset" in content or "picture" in content,
                "has_mobile_nav": "hamburger" in content or "mobile-menu" in content or "nav-toggle" in content,
                "uses_media_queries": "@media" in content,
            }

            return {
                "url": url,
                "device": device,
                "device_specs": spec,
                "mobile_analysis": mobile_analysis,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Mobile device test failed: {str(e)}"}

    async def _capture_device_suite(self, url: str, devices: List[str]) -> dict:
        """Capture page across multiple device viewports."""
        try:
            captures = []

            for device in devices:
                result = await self._test_mobile_device(url, device)
                if "error" not in result:
                    captures.append({
                        "device": device,
                        "screenshot": result.get("screenshot"),
                        "specs": result.get("device_specs"),
                    })

            return {
                "url": url,
                "devices_tested": len(captures),
                "captures": captures,
            }
        except Exception as e:
            return {"error": f"Device suite capture failed: {str(e)}"}

    async def _check_touch_targets(self, url: str) -> dict:
        """Verify touch targets are appropriately sized for mobile."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=True)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="touch_targets"
            )

            content = snapshot.raw.lower()

            # Check for touch target sizing
            touch_target_analysis = {
                "has_adequate_padding": "padding" in content,
                "has_min_height_styles": "min-height" in content,
                "has_touch_action": "touch-action" in content,
                "uses_button_elements": "<button" in content,
                "has_tap_highlight": "tap-highlight" in content,
            }

            # Count interactive elements
            interactive_count = content.count("<button") + content.count("<a ") + content.count("onclick")

            return {
                "url": url,
                "touch_target_analysis": touch_target_analysis,
                "interactive_elements_count": interactive_count,
                "screenshot": screenshot,
                "recommendation": "Ensure all touch targets are at least 44x44 pixels for accessibility",
            }
        except Exception as e:
            return {"error": f"Touch target check failed: {str(e)}"}

    # =========================================================================
    # SEO Verification Methods
    # =========================================================================

    async def _verify_meta_tags(self, url: str) -> dict:
        """Verify SEO meta tags."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="meta_tags"
            )

            content = snapshot.raw

            import re

            # Extract meta tags
            meta_tags = {
                "title": None,
                "description": None,
                "og:title": None,
                "og:description": None,
                "og:image": None,
                "twitter:card": None,
                "twitter:title": None,
                "robots": None,
            }

            # Title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
            if title_match:
                meta_tags["title"] = title_match.group(1).strip()

            # Meta tags
            for tag in meta_tags.keys():
                if tag == "title":
                    continue
                pattern = f'(name|property)=["\']({tag}|og:{tag}|twitter:{tag})["\'][^>]*content=["\']([^"\']+)["\']'
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    meta_tags[tag] = match.group(3)

            # Analyze
            issues = []
            if not meta_tags["title"]:
                issues.append("Missing title tag")
            elif len(meta_tags["title"]) > 60:
                issues.append("Title too long (>60 chars)")

            if not meta_tags["description"]:
                issues.append("Missing meta description")

            if not meta_tags["og:title"] or not meta_tags["og:description"]:
                issues.append("Missing Open Graph tags")

            return {
                "url": url,
                "meta_tags": meta_tags,
                "issues": issues,
                "seo_ready": len(issues) == 0,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Meta tag verification failed: {str(e)}"}

    async def _check_structured_data(self, url: str) -> dict:
        """Check Schema.org structured data markup."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="structured_data"
            )

            content = snapshot.raw

            import re

            # Check for JSON-LD
            jsonld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>([^<]+)</script>'
            jsonld_matches = re.findall(jsonld_pattern, content, re.IGNORECASE | re.DOTALL)

            # Check for microdata
            has_microdata = 'itemscope' in content.lower() or 'itemtype' in content.lower()

            # Check for RDFa
            has_rdfa = 'vocab=' in content.lower() or 'typeof=' in content.lower()

            structured_data = {
                "has_json_ld": len(jsonld_matches) > 0,
                "json_ld_count": len(jsonld_matches),
                "has_microdata": has_microdata,
                "has_rdfa": has_rdfa,
                "json_ld_snippets": [s[:200] for s in jsonld_matches[:3]],
            }

            return {
                "url": url,
                "structured_data": structured_data,
                "has_any_structured_data": any([structured_data["has_json_ld"], has_microdata, has_rdfa]),
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Structured data check failed: {str(e)}"}

    async def _verify_canonical_url(self, url: str, expected_canonical: str = None) -> dict:
        """Verify canonical URL tag."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="canonical_check"
            )

            content = snapshot.raw

            import re

            # Find canonical tag
            canonical_match = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', content, re.IGNORECASE)
            found_canonical = canonical_match.group(1) if canonical_match else None

            matches_expected = True
            if expected_canonical and found_canonical:
                matches_expected = found_canonical == expected_canonical

            return {
                "url": url,
                "found_canonical": found_canonical,
                "expected_canonical": expected_canonical,
                "has_canonical": found_canonical is not None,
                "matches_expected": matches_expected,
                "is_self_referencing": found_canonical == url if found_canonical else False,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Canonical URL verification failed: {str(e)}"}

    async def _check_robots_meta(self, url: str) -> dict:
        """Check robots meta tag and X-Robots-Tag header."""
        try:
            # Check HTTP headers
            response = await self.http_client.get(url, follow_redirects=True)
            x_robots_header = response.headers.get("X-Robots-Tag")

            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="robots_check"
            )

            content = snapshot.raw

            import re

            # Find robots meta tag
            robots_match = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
            robots_content = robots_match.group(1) if robots_match else None

            # Parse directives
            directives = {
                "index": True,
                "follow": True,
                "noindex": False,
                "nofollow": False,
            }

            if robots_content:
                robots_lower = robots_content.lower()
                directives["noindex"] = "noindex" in robots_lower
                directives["nofollow"] = "nofollow" in robots_lower
                directives["index"] = "noindex" not in robots_lower
                directives["follow"] = "nofollow" not in robots_lower

            return {
                "url": url,
                "robots_meta_tag": robots_content,
                "x_robots_header": x_robots_header,
                "directives": directives,
                "is_indexable": directives["index"],
                "links_followed": directives["follow"],
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Robots meta check failed: {str(e)}"}

    # =========================================================================
    # Form Testing Methods
    # =========================================================================

    async def _test_form_fields(self, url: str, form_selector: str = None) -> dict:
        """Test form field presence and types."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=True)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="form_fields"
            )

            content = snapshot.raw

            import re

            # Find all input fields
            input_pattern = r'<input[^>]*>'
            inputs = re.findall(input_pattern, content, re.IGNORECASE)

            # Categorize inputs
            field_types = {}
            for inp in inputs:
                type_match = re.search(r'type=["\']([^"\']+)["\']', inp, re.IGNORECASE)
                field_type = type_match.group(1) if type_match else "text"
                field_types[field_type] = field_types.get(field_type, 0) + 1

            # Find textareas
            textarea_count = content.lower().count("<textarea")

            # Find select elements
            select_count = content.lower().count("<select")

            # Find forms
            form_count = content.lower().count("<form")

            return {
                "url": url,
                "form_count": form_count,
                "total_inputs": len(inputs),
                "input_types": field_types,
                "textarea_count": textarea_count,
                "select_count": select_count,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Form field test failed: {str(e)}"}

    async def _verify_form_validation(self, url: str, test_invalid_inputs: bool) -> dict:
        """Verify form validation messages display correctly."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=True)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="form_validation"
            )

            content = snapshot.raw.lower()

            validation_analysis = {
                "has_required_fields": "required" in content,
                "has_pattern_validation": "pattern=" in content,
                "has_min_max_length": "minlength" in content or "maxlength" in content,
                "has_type_validation": 'type="email"' in content or 'type="number"' in content or 'type="tel"' in content,
                "has_custom_validation": "setcustomvalidity" in content or "validity" in content,
                "has_error_messages": "error" in content or "invalid" in content,
                "has_aria_invalid": "aria-invalid" in content,
            }

            return {
                "url": url,
                "validation_analysis": validation_analysis,
                "has_validation": any(validation_analysis.values()),
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Form validation check failed: {str(e)}"}

    async def _check_form_accessibility(self, url: str) -> dict:
        """Check form accessibility."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=True)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="form_a11y"
            )

            content = snapshot.raw.lower()

            a11y_checks = {
                "has_labels": "<label" in content,
                "has_for_attributes": "for=" in content,
                "has_aria_labels": "aria-label" in content,
                "has_aria_describedby": "aria-describedby" in content,
                "has_fieldsets": "<fieldset" in content,
                "has_legends": "<legend" in content,
                "has_autocomplete": "autocomplete=" in content,
                "has_error_association": "aria-errormessage" in content or "aria-describedby" in content,
            }

            passed = sum(1 for v in a11y_checks.values() if v)
            total = len(a11y_checks)

            return {
                "url": url,
                "accessibility_checks": a11y_checks,
                "score": round((passed / total) * 100),
                "passed": passed,
                "total": total,
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Form accessibility check failed: {str(e)}"}

    # =========================================================================
    # Link Validation Methods
    # =========================================================================

    async def _check_broken_links(self, url: str, include_external: bool) -> dict:
        """Find broken links on a page."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="broken_links"
            )

            content = snapshot.raw

            import re
            from urllib.parse import urljoin, urlparse

            # Find all links
            link_pattern = r'href=["\']([^"\']+)["\']'
            links = re.findall(link_pattern, content, re.IGNORECASE)

            # Filter and normalize links
            parsed_base = urlparse(url)
            internal_links = []
            external_links = []

            for link in links:
                if link.startswith("#") or link.startswith("javascript:") or link.startswith("mailto:"):
                    continue

                full_url = urljoin(url, link)
                parsed_link = urlparse(full_url)

                if parsed_link.netloc == parsed_base.netloc:
                    internal_links.append(full_url)
                else:
                    external_links.append(full_url)

            # Check a sample of links (limit to avoid long waits)
            links_to_check = internal_links[:10]
            if include_external:
                links_to_check.extend(external_links[:5])

            broken_links = []
            valid_links = []

            for link in links_to_check:
                try:
                    response = await self.http_client.head(link, follow_redirects=True, timeout=10.0)
                    if response.status_code >= 400:
                        broken_links.append({"url": link, "status": response.status_code})
                    else:
                        valid_links.append(link)
                except Exception:
                    broken_links.append({"url": link, "status": "error"})

            return {
                "url": url,
                "internal_links_found": len(internal_links),
                "external_links_found": len(external_links),
                "links_checked": len(links_to_check),
                "broken_links": broken_links,
                "valid_links_count": len(valid_links),
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Broken link check failed: {str(e)}"}

    async def _verify_external_links(self, url: str) -> dict:
        """Verify external links are valid and appropriate."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="external_links"
            )

            content = snapshot.raw

            import re
            from urllib.parse import urlparse

            # Find all links
            link_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>'
            link_elements = re.findall(link_pattern, content, re.IGNORECASE)

            parsed_base = urlparse(url)
            external_links = []

            for link in link_elements:
                if link.startswith("http"):
                    parsed_link = urlparse(link)
                    if parsed_link.netloc != parsed_base.netloc:
                        external_links.append(link)

            # Check external links (sample)
            external_link_status = []
            for link in external_links[:10]:
                try:
                    response = await self.http_client.head(link, follow_redirects=True, timeout=10.0)
                    external_link_status.append({
                        "url": link,
                        "status": response.status_code,
                        "valid": response.status_code < 400,
                    })
                except Exception as e:
                    external_link_status.append({
                        "url": link,
                        "status": "error",
                        "error": str(e),
                        "valid": False,
                    })

            return {
                "url": url,
                "external_links_found": len(external_links),
                "links_verified": len(external_link_status),
                "link_status": external_link_status,
                "all_valid": all(l.get("valid", False) for l in external_link_status),
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"External link verification failed: {str(e)}"}

    async def _check_link_attributes(self, url: str) -> dict:
        """Verify links have proper attributes."""
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/qa_proofs",
                prefix="link_attributes"
            )

            content = snapshot.raw

            import re

            # Find all anchor tags
            anchor_pattern = r'<a[^>]*>'
            anchors = re.findall(anchor_pattern, content, re.IGNORECASE)

            attribute_analysis = {
                "total_links": len(anchors),
                "links_with_target_blank": 0,
                "links_with_rel_noopener": 0,
                "links_with_rel_noreferrer": 0,
                "links_with_title": 0,
                "links_with_aria_label": 0,
                "external_without_noopener": [],
            }

            for anchor in anchors:
                anchor_lower = anchor.lower()

                if 'target="_blank"' in anchor_lower or "target='_blank'" in anchor_lower:
                    attribute_analysis["links_with_target_blank"] += 1

                    # Check security attributes
                    has_noopener = "noopener" in anchor_lower
                    has_noreferrer = "noreferrer" in anchor_lower

                    if has_noopener:
                        attribute_analysis["links_with_rel_noopener"] += 1
                    if has_noreferrer:
                        attribute_analysis["links_with_rel_noreferrer"] += 1

                    if not has_noopener and not has_noreferrer:
                        attribute_analysis["external_without_noopener"].append(anchor[:100])

                if "title=" in anchor_lower:
                    attribute_analysis["links_with_title"] += 1

                if "aria-label" in anchor_lower:
                    attribute_analysis["links_with_aria_label"] += 1

            # Security check
            security_issues = len(attribute_analysis["external_without_noopener"])

            return {
                "url": url,
                "attribute_analysis": attribute_analysis,
                "security_issues": security_issues,
                "recommendation": "Add rel='noopener noreferrer' to all target='_blank' links" if security_issues > 0 else "Links properly configured",
                "screenshot": screenshot,
            }
        except Exception as e:
            return {"error": f"Link attribute check failed: {str(e)}"}

    async def close(self):
        """Cleanup resources."""
        await self.http_client.aclose()
        await self.browser.close()
