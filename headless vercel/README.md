# Agent Browser Integration

Browser automation capability for the agent army using Vercel's `agent-browser` CLI.

## Quick Start

### 1. Install agent-browser

```bash
# Global install (recommended)
npm install -g @anthropic-ai/agent-browser

# Verify installation
agent-browser --help
```

### 2. Add skill to your agent service

Copy these files to your repo:

```bash
# Skill documentation (for agent reference)
cp skills/agent-browser/SKILL.md /path/to/ongoing_agent_builder/knowledge/agents/skills/

# Python wrapper
cp src/skills/agent_browser.py /path/to/ongoing_agent_builder/src/skills/
```

### 3. Update requirements.txt

No Python dependencies needed - we shell out to the CLI. The Node.js package is installed globally.

### 4. Use in your agents

```python
from skills.agent_browser import AgentBrowserSkill

class MyAgent:
    async def do_browser_task(self):
        browser = AgentBrowserSkill(session_name="my-agent")
        
        await browser.open("https://example.com")
        snapshot = await browser.snapshot(interactive_only=True)
        await browser.click("@e2")
        text = await browser.get_text("@e3")
        await browser.screenshot("proof.png")
        await browser.close()
        
        return text
```

## Files Included

```
agent-browser-integration/
├── README.md                           # This file
├── skills/
│   └── agent-browser/
│       └── SKILL.md                    # Agent-readable skill documentation
├── src/
│   └── skills/
│       └── agent_browser.py            # Python async wrapper
└── docs/
    └── BROWSER_CAPABILITY_MAP.md       # Which agents use browser automation
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT SERVICE                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              46 Specialized Agents                      │ │
│  │  (Social Listening, Competitor, QA, CRM, etc.)         │ │
│  └─────────────────────┬──────────────────────────────────┘ │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           AgentBrowserSkill (Python)                    │ │
│  │  • Async wrapper for CLI commands                      │ │
│  │  • Session management for parallel agents              │ │
│  │  • High-level patterns (scrape, fill_form, etc.)       │ │
│  └─────────────────────┬──────────────────────────────────┘ │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           agent-browser CLI (Rust + Node.js)            │ │
│  │  • 93% context reduction via Snapshot + Refs           │ │
│  │  • Session isolation for parallel execution            │ │
│  │  • Playwright under the hood                           │ │
│  └─────────────────────┬──────────────────────────────────┘ │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Chromium (Local Browser)                   │ │
│  │  • Headless by default                                 │ │
│  │  • Headed mode for debugging                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key Concepts

### Snapshot + Refs Workflow

The core innovation of `agent-browser` is the Snapshot + Refs pattern:

1. **Snapshot** returns element refs like `@e1`, `@e2`, `@e3`
2. **Refs** are deterministic selectors that don't change until the page changes
3. **Context is minimal** - only refs and accessible names, not full DOM

```bash
# Get minimal, actionable data
agent-browser snapshot -i -c

# Output like:
# @e1 button "Sign In"
# @e2 textbox "Email"
# @e3 textbox "Password"
# @e4 button "Submit"
```

### Session Isolation

Each agent can run in its own isolated browser session:

```python
# Social agent in one session
social = AgentBrowserSkill(session_name="social-listener")

# Competitor agent in another session (runs in parallel)
competitor = AgentBrowserSkill(session_name="competitor-intel")
```

### Proof of Work

Capture screenshots as verification:

```python
await browser.screenshot(f"proof_{task_id}_{timestamp}.png")
```

## Common Patterns

### Scrape and Extract

```python
await browser.open(url)
snapshot = await browser.snapshot()
text = await browser.get_text("@e3")
await browser.close()
```

### Fill and Submit Form

```python
await browser.open(form_url)
await browser.snapshot()
await browser.fill("@e2", "john@example.com")
await browser.fill("@e3", "password123")
await browser.click("@e5")  # Submit button
await browser.wait_for_text("Success")
await browser.screenshot("confirmation.png")
await browser.close()
```

### Multi-Page Navigation

```python
await browser.open(start_url)
await browser.snapshot()
await browser.click("@e4")  # Navigate to page 2
await browser.snapshot()    # New refs after navigation!
await browser.click("@e2")  # Use new refs
await browser.close()
```

## Debugging

```python
# Run with visible browser
browser = AgentBrowserSkill(session_name="debug", headed=True)
```

Or via CLI:

```bash
agent-browser open example.com --headed
```

## Environment Variables

```bash
# Custom Chrome path (optional)
AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/google-chrome

# Default to headed mode (optional, for debugging)
AGENT_BROWSER_HEADLESS=false
```

## Troubleshooting

### "agent-browser not found"

```bash
npm install -g @anthropic-ai/agent-browser
```

### "Browser failed to launch"

```bash
# Install browser dependencies
agent-browser install --with-deps
```

### "Session already exists"

```bash
# List and clean up sessions
agent-browser session list
agent-browser session close <name>
```

## See Also

- [SKILL.md](skills/agent-browser/SKILL.md) - Full command reference
- [BROWSER_CAPABILITY_MAP.md](docs/BROWSER_CAPABILITY_MAP.md) - Which agents use browser automation
- [agent-browser GitHub](https://github.com/vercel-labs/agent-browser) - Official repo
