# Browser Automation Capability Map

## Overview

This document maps which agents gain browser automation capabilities and their specific use cases.

## Priority Tiers

### Tier 1: High Impact (Enable First)

| Agent | Session Name | Primary Use Cases |
|-------|-------------|-------------------|
| **Social Listening** | `social-listener` | Scrape trending content, competitor posts, sentiment from comments |
| **Competitor** | `competitor-intel` | Navigate SimilarWeb, SpyFu, Meta Ad Library for competitive intel |
| **Media Buying** | `media-buyer` | Verify campaign setup, screenshot live ads, audit placements |
| **Instance Onboarding** | `instance-onboard` | Auto-configure platform credentials via OAuth flows |
| **QA** | `qa-agent` | Visual regression testing, screenshot campaign landing pages |
| **Influencer** | `influencer-agent` | Enrich creator profiles, scrape bios/media kits/engagement |
| **CRM** | `crm-agent` | Auto-lookup contact data from LinkedIn, company sites |

### Tier 2: Medium Impact

| Agent | Session Name | Primary Use Cases |
|-------|-------------|-------------------|
| **Campaign** | `campaign-agent` | Capture live creative screenshots, verify ad copy in-platform |
| **Report** | `report-agent` | Export dashboards that only render client-side |
| **Legal** | `legal-agent` | Navigate T&C pages, capture compliance documentation |
| **Training** | `training-agent` | Pull certification status from vendor portals |
| **PR** | `pr-agent` | Monitor news sites, capture coverage screenshots |
| **Social Analytics** | `social-analytics` | Scrape platform-native insights not in APIs |

### Tier 3: Lower Priority (API-first is fine)

| Agent | Reason |
|-------|--------|
| Invoice, Budget, Forecast | Financial data lives in structured systems |
| Workflow, Resource | Internal ERP operations |
| Voice, Visual, Guidelines | Brand assets are internal |
| Knowledge, Training | Content from internal sources |

---

## Implementation Examples

### Social Listening Agent

```python
from skills.agent_browser import AgentBrowserSkill

class SocialListeningAgent:
    def __init__(self):
        self.browser = AgentBrowserSkill(session_name="social-listener")
    
    async def gather_trending_content(self, platform: str, topic: str):
        """Scrape trending content that APIs don't expose."""
        
        # Navigate to explore/trending page
        if platform == "instagram":
            await self.browser.open("https://instagram.com/explore")
        elif platform == "tiktok":
            await self.browser.open("https://tiktok.com/discover")
        
        # Get interactive elements
        snapshot = await self.browser.snapshot(interactive_only=True)
        
        # Extract trending posts (agent interprets refs from snapshot)
        # ... agent logic to identify relevant refs ...
        
        # Capture proof
        await self.browser.screenshot(f"trending_{platform}_{topic}.png")
        
        await self.browser.close()
        return results
```

### Competitor Intelligence Agent

```python
from skills.agent_browser import AgentBrowserSkill

class CompetitorAgent:
    def __init__(self):
        self.browser = AgentBrowserSkill(session_name="competitor-intel")
    
    async def analyze_competitor_ads(self, competitor: str):
        """Scrape Meta Ad Library for competitor creative."""
        
        # Navigate to Ad Library
        await self.browser.open(
            f"https://www.facebook.com/ads/library/?q={competitor}"
        )
        await self.browser.wait(2000)  # Let results load
        
        # Snapshot the ad listings
        snapshot = await self.browser.snapshot(interactive_only=False)
        
        # Screenshot for proof/analysis
        await self.browser.screenshot(f"competitor_{competitor}_ads.png")
        
        await self.browser.close()
        return snapshot
    
    async def get_traffic_estimates(self, domain: str):
        """Scrape SimilarWeb for traffic data."""
        
        await self.browser.open(f"https://similarweb.com/website/{domain}")
        await self.browser.wait(3000)
        
        snapshot = await self.browser.snapshot()
        
        # Extract key metrics
        # ... agent interprets refs ...
        
        await self.browser.close()
```

### Instance Onboarding Agent

```python
from skills.agent_browser import AgentBrowserSkill

class InstanceOnboardingAgent:
    def __init__(self):
        self.browser = AgentBrowserSkill(
            session_name="instance-onboard",
            headed=True  # Visible for OAuth flows
        )
    
    async def verify_platform_access(self, platform: str, account_id: str):
        """Verify OAuth credentials work via browser."""
        
        platform_urls = {
            "meta": "https://business.facebook.com/settings",
            "google": "https://ads.google.com/aw/overview",
            "tiktok": "https://ads.tiktok.com/i18n/dashboard",
        }
        
        await self.browser.open(platform_urls[platform])
        await self.browser.wait(3000)
        
        # Check if we're authenticated
        snapshot = await self.browser.snapshot()
        
        # Screenshot verification
        filepath = await self.browser.capture_proof(
            platform_urls[platform],
            "/tmp/verifications",
            f"verify_{platform}_{account_id}"
        )
        
        await self.browser.close()
        return {"verified": True, "proof": filepath}
```

### QA Agent

```python
from skills.agent_browser import AgentBrowserSkill

class QAAgent:
    def __init__(self):
        self.browser = AgentBrowserSkill(session_name="qa-agent")
    
    async def visual_regression_check(self, urls: list):
        """Capture screenshots for visual regression testing."""
        
        screenshots = []
        for url in urls:
            await self.browser.open(url)
            await self.browser.wait(2000)
            
            filepath = f"/tmp/qa/screenshot_{hash(url)}.png"
            await self.browser.screenshot(filepath)
            screenshots.append(filepath)
        
        await self.browser.close()
        return screenshots
    
    async def verify_campaign_landing(self, campaign_id: str, landing_url: str):
        """Verify campaign landing page is live and correct."""
        
        await self.browser.open(landing_url)
        await self.browser.wait(3000)
        
        # Get page content
        snapshot = await self.browser.snapshot(interactive_only=False)
        
        # Screenshot proof
        await self.browser.screenshot(f"/tmp/qa/campaign_{campaign_id}.png")
        
        await self.browser.close()
        return snapshot
```

---

## Session Management for Parallel Execution

Multiple agents can run simultaneously using isolated sessions:

```python
import asyncio
from skills.agent_browser import AgentBrowserSkill

async def run_parallel_intel():
    """Run multiple browser agents in parallel."""
    
    # Each agent gets its own isolated browser session
    social = AgentBrowserSkill(session_name="social-parallel")
    competitor = AgentBrowserSkill(session_name="competitor-parallel")
    qa = AgentBrowserSkill(session_name="qa-parallel")
    
    # Run all three simultaneously
    results = await asyncio.gather(
        social.open("https://instagram.com/explore"),
        competitor.open("https://similarweb.com"),
        qa.open("https://client-landing-page.com"),
    )
    
    # Each works independently
    await asyncio.gather(
        social.snapshot(),
        competitor.snapshot(),
        qa.screenshot("/tmp/qa_check.png"),
    )
    
    # Cleanup
    await asyncio.gather(
        social.close(),
        competitor.close(),
        qa.close(),
    )
```

---

## Environment Configuration

Add to `.env`:

```bash
# Optional: Custom Chrome path
AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/google-chrome

# Optional: Default to headed mode for debugging
AGENT_BROWSER_HEADLESS=false
```

---

## Rollout Checklist

### Phase 1: Infrastructure (Day 1)
- [ ] Add `agent-browser` to requirements/dependencies
- [ ] Create `src/skills/agent_browser.py`
- [ ] Add skill documentation to `docs/skills/`
- [ ] Test basic commands work in agent environment

### Phase 2: Tier 1 Agents (Week 1)
- [ ] Social Listening Agent - trending content scraping
- [ ] Competitor Agent - Meta Ad Library, SimilarWeb integration
- [ ] Instance Onboarding Agent - OAuth verification flows
- [ ] QA Agent - visual regression capture

### Phase 3: Tier 2 Agents (Week 2)
- [ ] Campaign Agent - live ad screenshots
- [ ] Report Agent - dashboard exports
- [ ] CRM Agent - contact enrichment
- [ ] Influencer Agent - creator profile scraping

### Phase 4: Documentation & Training (Week 3)
- [ ] Update AGENTS.md with browser capability flags
- [ ] Add browser automation examples to Training Agent content
- [ ] Create troubleshooting guide for common issues
