# Browser-Enabled SpokeStack Capabilities

Beyond basic web scraping and debugging, browser automation unlocks several powerful capabilities for the multi-tenant SpokeStack platform.

---

## 1. Proof-of-Work Generation

**The Problem**: Clients want documented proof that work was done - screenshots of live ads, campaign setups, platform configurations.

**Browser Solution**:
```python
# Every agent can capture timestamped proof
await browser.capture_proof(
    url="https://business.facebook.com/ads/manager/campaign/123",
    output_dir="/proofs/client_acme",
    prefix="campaign_launch"
)
# Generates: campaign_launch_20260115_143022.png
```

**Multi-Tenant Value**:
- Each instance stores proofs in tenant-isolated storage
- Automatic audit trail for every action
- Client-facing reports include screenshot evidence
- Compliance documentation generated automatically

---

## 2. Platform Orchestration (Beyond APIs)

**The Problem**: Not all ad platform features are API-accessible. Some require browser-based admin actions.

**Browser Solution**:
```python
# Media Buying Agent can execute platform-specific workflows
await browser.open("https://ads.tiktok.com/i18n/promote/create")
await browser.snapshot()
await browser.fill("@e3", campaign_name)
await browser.select("@e7", "Traffic")
await browser.click("@e12")  # Next step
```

**Use Cases**:
- **Pixel Installation Verification**: Navigate to sites, check pixel fires
- **Audience Setup**: Create custom audiences not available via API
- **Creative Preview**: View how ads render in-platform
- **Permission Management**: Configure business manager access
- **Billing Updates**: Handle payment method changes

---

## 3. Cross-Platform Intelligence Hub

**The Problem**: Competitive intelligence requires data from multiple sources that don't integrate.

**Browser Solution**: Run parallel agents, each in isolated sessions:

```python
async def gather_competitive_intel(competitor: str):
    """Multi-source competitive intelligence gathering."""

    # Parallel execution across sources
    tasks = [
        scrape_meta_ad_library(competitor),      # Session: meta-ads
        scrape_similarweb(competitor),           # Session: traffic-data
        scrape_linkedin_company(competitor),     # Session: company-data
        scrape_glassdoor(competitor),            # Session: culture-data
        scrape_g2_reviews(competitor),           # Session: product-reviews
    ]

    results = await asyncio.gather(*tasks)
    return compile_competitive_report(results)
```

**Multi-Tenant Value**:
- Each instance can configure which sources to monitor
- Competitor lists are tenant-specific
- Intelligence feeds into Campaign, Strategy, and Client Success agents
- Automated alerts when competitors change tactics

---

## 4. Client Portal Automation

**The Problem**: Instances need to onboard into various client systems (ERPs, PMSs, custom portals).

**Browser Solution**:
```python
class InstanceOnboardingAgent:
    async def connect_client_portal(self, portal_url: str, credentials: dict):
        """Automate client portal setup and verification."""

        await self.browser.open(portal_url)
        await self.browser.snapshot()

        # Fill login form
        await self.browser.fill("@e2", credentials["username"])
        await self.browser.fill("@e3", credentials["password"])
        await self.browser.click("@e4")  # Login

        # Verify access
        await self.browser.wait_for_text("Dashboard")
        await self.browser.capture_proof(
            portal_url, "/proofs/onboarding", "portal_access"
        )

        return {"connected": True, "proof": proof_path}
```

**Use Cases**:
- Connect to client ERP systems
- Verify OAuth grants work
- Configure webhook endpoints
- Set up SSO connections
- Validate API credentials via browser fallback

---

## 5. Visual QA and Regression Testing

**The Problem**: Campaign landing pages, creative assets, and web properties need visual verification.

**Browser Solution**:
```python
class QAAgent:
    async def visual_regression_suite(self, client_id: str, urls: list):
        """Capture visual state for regression comparison."""

        baseline_dir = f"/qa/{client_id}/baseline"
        current_dir = f"/qa/{client_id}/current"

        for url in urls:
            await self.browser.open(url)
            await self.browser.wait(2000)

            # Capture current state
            filename = f"page_{hash(url)}.png"
            await self.browser.screenshot(f"{current_dir}/{filename}")

            # Compare to baseline (if exists)
            if exists(f"{baseline_dir}/{filename}"):
                diff = compare_images(
                    f"{baseline_dir}/{filename}",
                    f"{current_dir}/{filename}"
                )
                if diff > 0.05:  # 5% threshold
                    alert_visual_change(url, diff)
```

**Multi-Tenant Value**:
- Each instance maintains its own visual baselines
- Automated landing page monitoring
- Creative verification before launch
- Detect when client sites change unexpectedly

---

## 6. Compliance and Legal Documentation

**The Problem**: Agencies need to document compliance with platform ToS, capture regulatory disclosures, maintain audit trails.

**Browser Solution**:
```python
class LegalAgent:
    async def capture_compliance_docs(self, platforms: list):
        """Capture current T&C and policy pages for records."""

        policy_urls = {
            "meta": "https://www.facebook.com/policies/ads/",
            "google": "https://support.google.com/adspolicy/answer/6008942",
            "tiktok": "https://ads.tiktok.com/help/article/tiktok-advertising-policies",
        }

        for platform in platforms:
            url = policy_urls[platform]
            await self.browser.open(url)

            # Save as PDF for legal records
            await self.browser.pdf(
                f"/compliance/{platform}_policy_{date.today()}.pdf"
            )

            # Also screenshot
            await self.browser.screenshot(
                f"/compliance/{platform}_policy_{date.today()}.png"
            )
```

**Use Cases**:
- Monthly policy capture for audit trail
- FTC/regulatory compliance documentation
- Client contract compliance verification
- Privacy policy monitoring
- Terms of service change detection

---

## 7. Multi-Tenant Session Isolation

**Critical for SpokeStack**: Each tenant's agents run in isolated browser sessions.

```python
# Instance A's agents
social_a = AgentBrowserSkill(session_name="instance_a_social")
competitor_a = AgentBrowserSkill(session_name="instance_a_competitor")

# Instance B's agents (completely isolated)
social_b = AgentBrowserSkill(session_name="instance_b_social")
competitor_b = AgentBrowserSkill(session_name="instance_b_competitor")

# Can run all four simultaneously without conflict
await asyncio.gather(
    social_a.open("https://instagram.com/explore"),
    competitor_a.open("https://similarweb.com"),
    social_b.open("https://tiktok.com/discover"),
    competitor_b.open("https://semrush.com"),
)
```

**Why This Matters**:
- No cross-tenant data leakage
- Each tenant can have different authenticated sessions
- Parallel execution scales with instances
- Session cleanup prevents cookie/state pollution

---

## 8. Automated Reporting Enrichment

**The Problem**: Some data only exists in browser-rendered dashboards.

**Browser Solution**:
```python
class ReportAgent:
    async def capture_dashboard_exports(self, client_id: str):
        """Capture platform dashboards that don't have export APIs."""

        dashboards = [
            "https://analytics.google.com/analytics/web/#/report/...",
            "https://business.facebook.com/insights/...",
            "https://ads.tiktok.com/i18n/dashboard/...",
        ]

        for url in dashboards:
            await self.browser.open(url)
            await self.browser.wait(5000)  # Let charts render

            # Capture the visual dashboard
            await self.browser.screenshot(
                f"/reports/{client_id}/dashboard_{hash(url)}.png"
            )

        # Embed screenshots in client report
        return compile_visual_report(client_id)
```

---

## 9. Lead Enrichment and CRM Automation

**The Problem**: Contact data scattered across LinkedIn, company sites, databases.

**Browser Solution**:
```python
class CRMAgent:
    async def enrich_contact(self, contact: dict):
        """Enrich contact data from web sources."""

        enriched = contact.copy()

        # LinkedIn profile scraping (if public)
        if contact.get("linkedin_url"):
            await self.browser.open(contact["linkedin_url"])
            snapshot = await self.browser.snapshot(interactive_only=False)
            enriched["linkedin_data"] = parse_linkedin_snapshot(snapshot)

        # Company website
        if contact.get("company_domain"):
            await self.browser.open(f"https://{contact['company_domain']}/about")
            snapshot = await self.browser.snapshot(interactive_only=False)
            enriched["company_data"] = parse_about_page(snapshot)

        return enriched
```

---

## 10. Architecture Integration

### Browser Skill in the Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SPOKESTACK PLATFORM                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 CORE AGENTS (Global)                        │ │
│  │  • AgentBrowserSkill available to all 46 agents            │ │
│  │  • Browser commands defined in knowledge/skills/           │ │
│  └─────────────────────┬──────────────────────────────────────┘ │
│                        │                                         │
│  ┌─────────────────────┼──────────────────────────────────────┐ │
│  │         INSTANCE CONFIG (Per-Tenant)                        │ │
│  │  • Session naming: instance_{id}_{agent_type}              │ │
│  │  • Competitor lists, target platforms                       │ │
│  │  • OAuth credentials per tenant                             │ │
│  └─────────────────────┼──────────────────────────────────────┘ │
│                        │                                         │
│  ┌─────────────────────┼──────────────────────────────────────┐ │
│  │         SKILL EXTENSIONS (Per-Instance)                     │ │
│  │  • Custom scraping targets                                  │ │
│  │  • Client-specific portal automations                       │ │
│  │  • Visual baseline configurations                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Database Schema Additions

```sql
-- Track browser automation tasks per instance
CREATE TABLE browser_tasks (
    id UUID PRIMARY KEY,
    instance_id UUID REFERENCES instances(id),
    agent_type VARCHAR(50),
    session_name VARCHAR(100),
    task_type VARCHAR(50),  -- 'scrape', 'proof', 'form', 'qa'
    target_url TEXT,
    status VARCHAR(20),
    screenshot_path TEXT,
    result_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Store proof-of-work screenshots
CREATE TABLE proof_screenshots (
    id UUID PRIMARY KEY,
    instance_id UUID REFERENCES instances(id),
    client_id UUID REFERENCES clients(id),
    task_id UUID REFERENCES browser_tasks(id),
    file_path TEXT NOT NULL,
    url TEXT,
    captured_at TIMESTAMP DEFAULT NOW()
);
```

---

## Summary: Beyond Web Scraping

| Capability | Value for SpokeStack |
|------------|---------------------|
| Proof-of-Work | Client deliverables, audit trails |
| Platform Orchestration | Actions not possible via API |
| Competitive Intelligence | Multi-source parallel gathering |
| Portal Automation | Client system integration |
| Visual QA | Landing page monitoring |
| Compliance Docs | Legal/regulatory audit trail |
| Session Isolation | Multi-tenant security |
| Dashboard Capture | Reports with visual data |
| Lead Enrichment | CRM automation |

The browser skill transforms SpokeStack from an API-integration platform into a **full web automation platform** capable of handling any task that a human could do in a browser - at scale across all tenants.
