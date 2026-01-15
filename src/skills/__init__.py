"""
SpokeStack Skills Module

Browser automation and other specialized capabilities for agents.
"""

from .agent_browser import (
    AgentBrowserSkill,
    BrowserResult,
    SnapshotResult,
    quick_scrape
)

__all__ = [
    "AgentBrowserSkill",
    "BrowserResult",
    "SnapshotResult",
    "quick_scrape"
]
