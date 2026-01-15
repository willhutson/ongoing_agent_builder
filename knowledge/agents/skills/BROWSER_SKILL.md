# Agent Browser Skill

Browser automation for AI agents using Vercel's `agent-browser` CLI.

## Overview

`agent-browser` provides 93% context reduction compared to raw Playwright by using a Snapshot + Refs workflow. Agents get only actionable element references instead of massive DOM trees.

## Installation

```bash
# Global install (recommended for agent service)
npm install -g @anthropic-ai/agent-browser

# Or run via npx
npx agent-browser --help
```

## Core Workflow

Every browser automation follows this pattern:

```bash
# 1. Open page
agent-browser open <url>

# 2. Get interactive elements with refs (@e1, @e2, etc.)
agent-browser snapshot -i

# 3. Interact using refs
agent-browser click @e1
agent-browser fill @e2 "text"

# 4. Re-snapshot after page changes
agent-browser snapshot -i

# 5. Close when done
agent-browser close
```

## Commands Reference

### Navigation
```bash
agent-browser open <url>              # Navigate to URL
agent-browser tab new <url>           # Open in new tab
agent-browser tab list                # List open tabs
agent-browser tab switch <id>         # Switch to tab
agent-browser back                    # Go back
agent-browser forward                 # Go forward
agent-browser reload                  # Reload page
```

### Snapshots (Critical for AI efficiency)
```bash
agent-browser snapshot                # Full accessibility tree
agent-browser snapshot -i             # Interactive elements only (buttons, inputs, links)
agent-browser snapshot -c             # Compact output
agent-browser snapshot -i -c          # Minimal tokens - use this most often
agent-browser snapshot --json         # JSON output for parsing
```

### Interactions (Use refs from snapshot)
```bash
agent-browser click @e1               # Click element
agent-browser fill @e2 "text"         # Fill input field
agent-browser select @e3 "option"     # Select dropdown option
agent-browser check @e4               # Check checkbox
agent-browser uncheck @e5             # Uncheck checkbox
agent-browser hover @e6               # Hover over element
agent-browser focus @e7               # Focus element
```

### Semantic Locators (When refs aren't enough)
```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "test@example.com"
agent-browser find placeholder "Search..." fill "query"
agent-browser find testid "login-btn" click
```

### Data Extraction
```bash
agent-browser get text @e1            # Get element text
agent-browser get value @e2           # Get input value
agent-browser get html @e3            # Get element HTML
agent-browser get attribute @e4 href  # Get specific attribute
agent-browser screenshot page.png     # Take screenshot
agent-browser pdf output.pdf          # Save as PDF
```

### Waiting
```bash
agent-browser wait 2000               # Wait milliseconds
agent-browser wait @e1                # Wait for element visible
agent-browser wait --text "Success"   # Wait for text to appear
agent-browser wait --hidden @e2       # Wait for element to hide
```

### Sessions (For multi-agent isolation)
```bash
agent-browser session new myagent     # Create isolated session
agent-browser session list            # List sessions
agent-browser session use myagent     # Switch to session
agent-browser session close myagent   # Close session
```

## Best Practices for Agents

### 1. Always use `-i` flag for snapshots
```bash
# Good - minimal context
agent-browser snapshot -i

# Avoid - massive DOM tree
agent-browser snapshot
```

### 2. Use sessions for parallel agents
```bash
# Social Listening Agent
agent-browser session new social-listener
agent-browser session use social-listener
agent-browser open instagram.com/explore
# ... work ...
agent-browser session close social-listener

# Competitor Agent (runs simultaneously)
agent-browser session new competitor-intel
agent-browser session use competitor-intel
agent-browser open similarweb.com
# ... work ...
agent-browser session close competitor-intel
```

### 3. Re-snapshot after any page change
```bash
agent-browser click @e2
agent-browser snapshot -i    # Refs change after interactions!
agent-browser click @e5      # Use new refs
```

### 4. Use --json for programmatic parsing
```bash
agent-browser snapshot -i --json | jq '.refs'
agent-browser get text @e1 --json
```

### 5. Screenshot for proof-of-work
```bash
# Capture verification screenshots
agent-browser screenshot verification_$(date +%s).png
```

## Common Agent Patterns

### Scrape and Extract
```bash
agent-browser open https://example.com/products
agent-browser snapshot -i
agent-browser get text @e3   # Product name
agent-browser get text @e5   # Price
agent-browser screenshot products.png
agent-browser close
```

### Form Submission
```bash
agent-browser open https://example.com/signup
agent-browser snapshot -i
agent-browser fill @e2 "John Doe"
agent-browser fill @e3 "john@example.com"
agent-browser click @e7      # Submit button
agent-browser wait --text "Success"
agent-browser screenshot confirmation.png
agent-browser close
```

### Multi-Page Navigation
```bash
agent-browser open https://example.com
agent-browser snapshot -i
agent-browser click @e4      # Navigate to page 2
agent-browser snapshot -i    # New refs!
agent-browser click @e2      # Action on page 2
agent-browser back
agent-browser snapshot -i    # Back to original refs
agent-browser close
```

### Authentication Flow
```bash
agent-browser open https://example.com/login
agent-browser snapshot -i
agent-browser fill @e2 "$USERNAME"
agent-browser fill @e3 "$PASSWORD"
agent-browser click @e5
agent-browser wait --text "Dashboard"
agent-browser screenshot logged_in.png
# Continue with authenticated session...
```

## Debugging

```bash
# Run with visible browser
agent-browser open example.com --headed

# Verbose logging
agent-browser --verbose open example.com

# Check daemon status
agent-browser status
```

## Environment Variables

```bash
AGENT_BROWSER_EXECUTABLE_PATH=/path/to/chrome  # Custom Chrome path
AGENT_BROWSER_HEADLESS=false                   # Default to headed mode
```
