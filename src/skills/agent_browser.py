"""
Agent Browser Skill
Browser automation capability for all agents using Vercel's agent-browser CLI.

Usage:
    from src.skills.agent_browser import AgentBrowserSkill

    browser = AgentBrowserSkill(session_name="social-listener")
    await browser.open("https://instagram.com/explore")
    elements = await browser.snapshot(interactive_only=True)
    await browser.click("@e2")
    text = await browser.get_text("@e3")
    await browser.screenshot("proof.png")
    await browser.close()
"""

import asyncio
import json
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SnapshotResult:
    """Result from a browser snapshot."""
    raw: str
    refs: Dict[str, Dict[str, Any]]
    timestamp: datetime


@dataclass
class BrowserResult:
    """Generic result from browser operations."""
    success: bool
    data: Any
    error: Optional[str] = None


class AgentBrowserSkill:
    """
    Browser automation skill for agents.

    Wraps Vercel's agent-browser CLI with async Python interface.
    Each instance can use an isolated session for parallel agent execution.
    """

    def __init__(
        self,
        session_name: Optional[str] = None,
        headed: bool = False,
        timeout: int = 30000
    ):
        """
        Initialize browser skill.

        Args:
            session_name: Isolated session name for parallel agents.
                         If None, uses default session.
            headed: Run with visible browser window (for debugging).
            timeout: Default timeout in milliseconds.
        """
        self.session_name = session_name
        self.headed = headed
        self.timeout = timeout
        self._initialized = False

    async def _run_command(
        self,
        *args: str,
        parse_json: bool = False
    ) -> BrowserResult:
        """Execute agent-browser command."""
        cmd = ["agent-browser"]

        # Add session if specified
        if self.session_name and self._initialized:
            cmd.extend(["--session", self.session_name])

        # Add headed flag if needed
        if self.headed:
            cmd.append("--headed")

        cmd.extend(args)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return BrowserResult(
                    success=False,
                    data=None,
                    error=stderr.decode().strip()
                )

            output = stdout.decode().strip()

            if parse_json:
                try:
                    data = json.loads(output)
                    return BrowserResult(success=True, data=data)
                except json.JSONDecodeError:
                    return BrowserResult(success=True, data=output)

            return BrowserResult(success=True, data=output)

        except FileNotFoundError:
            return BrowserResult(
                success=False,
                data=None,
                error="agent-browser not installed. Run: npm install -g @anthropic-ai/agent-browser"
            )
        except Exception as e:
            return BrowserResult(
                success=False,
                data=None,
                error=str(e)
            )

    # =========================================================================
    # Session Management
    # =========================================================================

    async def init_session(self) -> BrowserResult:
        """Initialize isolated session for this agent."""
        if self.session_name:
            result = await self._run_command("session", "new", self.session_name)
            if result.success:
                self._initialized = True
            return result
        self._initialized = True
        return BrowserResult(success=True, data="Using default session")

    async def close_session(self) -> BrowserResult:
        """Close this agent's session."""
        if self.session_name:
            return await self._run_command("session", "close", self.session_name)
        return BrowserResult(success=True, data="Default session remains open")

    # =========================================================================
    # Navigation
    # =========================================================================

    async def open(self, url: str) -> BrowserResult:
        """Navigate to URL."""
        if not self._initialized:
            await self.init_session()
        return await self._run_command("open", url)

    async def back(self) -> BrowserResult:
        """Go back in history."""
        return await self._run_command("back")

    async def forward(self) -> BrowserResult:
        """Go forward in history."""
        return await self._run_command("forward")

    async def reload(self) -> BrowserResult:
        """Reload current page."""
        return await self._run_command("reload")

    async def close(self) -> BrowserResult:
        """Close browser and session."""
        result = await self._run_command("close")
        await self.close_session()
        return result

    # =========================================================================
    # Snapshots (Critical for AI efficiency)
    # =========================================================================

    async def snapshot(
        self,
        interactive_only: bool = True,
        compact: bool = True,
        as_json: bool = False
    ) -> SnapshotResult:
        """
        Get page snapshot with element refs.

        Args:
            interactive_only: Only return interactive elements (buttons, inputs, links).
                            Highly recommended - reduces context by 93%.
            compact: Compact output format.
            as_json: Return raw JSON for parsing.

        Returns:
            SnapshotResult with refs like @e1, @e2, etc.
        """
        args = ["snapshot"]
        if interactive_only:
            args.append("-i")
        if compact:
            args.append("-c")
        if as_json:
            args.append("--json")

        result = await self._run_command(*args, parse_json=as_json)

        refs = {}
        if as_json and result.success and isinstance(result.data, dict):
            refs = result.data.get("refs", {})

        return SnapshotResult(
            raw=result.data if isinstance(result.data, str) else json.dumps(result.data),
            refs=refs,
            timestamp=datetime.now()
        )

    # =========================================================================
    # Interactions
    # =========================================================================

    async def click(self, ref: str) -> BrowserResult:
        """Click element by ref (e.g., @e1)."""
        return await self._run_command("click", ref)

    async def fill(self, ref: str, text: str) -> BrowserResult:
        """Fill input field by ref."""
        return await self._run_command("fill", ref, text)

    async def select(self, ref: str, option: str) -> BrowserResult:
        """Select dropdown option by ref."""
        return await self._run_command("select", ref, option)

    async def check(self, ref: str) -> BrowserResult:
        """Check checkbox by ref."""
        return await self._run_command("check", ref)

    async def uncheck(self, ref: str) -> BrowserResult:
        """Uncheck checkbox by ref."""
        return await self._run_command("uncheck", ref)

    async def hover(self, ref: str) -> BrowserResult:
        """Hover over element by ref."""
        return await self._run_command("hover", ref)

    async def focus(self, ref: str) -> BrowserResult:
        """Focus element by ref."""
        return await self._run_command("focus", ref)

    # =========================================================================
    # Semantic Locators (When refs aren't enough)
    # =========================================================================

    async def find_and_click(
        self,
        locator_type: str,
        locator_value: str,
        **kwargs
    ) -> BrowserResult:
        """
        Find element and click using semantic locator.

        Args:
            locator_type: One of: role, text, label, placeholder, testid
            locator_value: Value to match
            **kwargs: Additional args like --name for role locator
        """
        args = ["find", locator_type, locator_value, "click"]
        for key, value in kwargs.items():
            args.extend([f"--{key}", value])
        return await self._run_command(*args)

    async def find_and_fill(
        self,
        locator_type: str,
        locator_value: str,
        text: str,
        **kwargs
    ) -> BrowserResult:
        """Find element and fill using semantic locator."""
        args = ["find", locator_type, locator_value, "fill", text]
        for key, value in kwargs.items():
            args.extend([f"--{key}", value])
        return await self._run_command(*args)

    # =========================================================================
    # Data Extraction
    # =========================================================================

    async def get_text(self, ref: str) -> BrowserResult:
        """Get text content of element."""
        return await self._run_command("get", "text", ref)

    async def get_value(self, ref: str) -> BrowserResult:
        """Get input value of element."""
        return await self._run_command("get", "value", ref)

    async def get_html(self, ref: str) -> BrowserResult:
        """Get HTML of element."""
        return await self._run_command("get", "html", ref)

    async def get_attribute(self, ref: str, attribute: str) -> BrowserResult:
        """Get specific attribute of element."""
        return await self._run_command("get", "attribute", ref, attribute)

    async def screenshot(self, filepath: str) -> BrowserResult:
        """Take screenshot and save to file."""
        return await self._run_command("screenshot", filepath)

    async def pdf(self, filepath: str) -> BrowserResult:
        """Save page as PDF."""
        return await self._run_command("pdf", filepath)

    # =========================================================================
    # Waiting
    # =========================================================================

    async def wait(self, milliseconds: int) -> BrowserResult:
        """Wait for specified milliseconds."""
        return await self._run_command("wait", str(milliseconds))

    async def wait_for_element(self, ref: str) -> BrowserResult:
        """Wait for element to be visible."""
        return await self._run_command("wait", ref)

    async def wait_for_text(self, text: str) -> BrowserResult:
        """Wait for text to appear on page."""
        return await self._run_command("wait", "--text", text)

    async def wait_for_hidden(self, ref: str) -> BrowserResult:
        """Wait for element to be hidden."""
        return await self._run_command("wait", "--hidden", ref)

    # =========================================================================
    # High-Level Patterns
    # =========================================================================

    async def scrape_page(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Scrape multiple elements from a page.

        Args:
            url: Page to scrape
            selectors: Dict mapping field names to refs (e.g., {"title": "@e3"})

        Returns:
            Dict with field names mapped to extracted text
        """
        await self.open(url)
        await self.snapshot(interactive_only=False)  # Need full tree for content

        results = {}
        for field, ref in selectors.items():
            result = await self.get_text(ref)
            results[field] = result.data if result.success else None

        return results

    async def fill_form(
        self,
        url: str,
        fields: Dict[str, str],
        submit_ref: Optional[str] = None
    ) -> BrowserResult:
        """
        Fill out a form and optionally submit.

        Args:
            url: Form page URL
            fields: Dict mapping refs to values (e.g., {"@e2": "John"})
            submit_ref: Ref of submit button (optional)

        Returns:
            Result of form submission
        """
        await self.open(url)
        await self.snapshot()

        for ref, value in fields.items():
            await self.fill(ref, value)

        if submit_ref:
            return await self.click(submit_ref)

        return BrowserResult(success=True, data="Form filled")

    async def capture_proof(
        self,
        url: str,
        output_dir: str,
        prefix: str = "proof"
    ) -> str:
        """
        Navigate to URL and capture screenshot as proof-of-work.

        Args:
            url: Page to capture
            output_dir: Directory to save screenshot
            prefix: Filename prefix

        Returns:
            Path to saved screenshot
        """
        await self.open(url)
        await self.wait(1000)  # Let page settle

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(output_dir, f"{prefix}_{timestamp}.png")

        await self.screenshot(filepath)
        return filepath


# =============================================================================
# Convenience function for one-off operations
# =============================================================================

async def quick_scrape(url: str, instruction: str) -> Dict[str, Any]:
    """
    Quick scrape with automatic element discovery.

    This is a high-level function that:
    1. Opens the URL
    2. Takes a snapshot
    3. Returns the snapshot for agent interpretation

    The agent should then decide which refs to extract from.
    """
    browser = AgentBrowserSkill()
    await browser.open(url)
    snapshot = await browser.snapshot(interactive_only=False, as_json=True)
    await browser.close()

    return {
        "url": url,
        "snapshot": snapshot.raw,
        "refs": snapshot.refs,
        "instruction": instruction
    }
