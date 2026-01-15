#!/bin/bash
# Setup script for agent-browser integration
# Run from the ongoing_agent_builder repo root

set -e

echo "🚀 Setting up agent-browser integration..."

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js first."
    exit 1
fi

# Install agent-browser globally
echo "📦 Installing agent-browser CLI..."
npm install -g @anthropic-ai/agent-browser

# Verify installation
if ! command -v agent-browser &> /dev/null; then
    echo "❌ agent-browser installation failed"
    exit 1
fi
echo "✅ agent-browser installed"

# Install browser dependencies
echo "🌐 Installing browser dependencies..."
agent-browser install --with-deps

# Create skill directories if they don't exist
echo "📁 Creating skill directories..."
mkdir -p knowledge/agents/skills/agent-browser
mkdir -p src/skills

# Copy skill files (assuming this script is run from integration package)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/skills/agent-browser/SKILL.md" ]; then
    echo "📄 Copying skill documentation..."
    cp "$SCRIPT_DIR/skills/agent-browser/SKILL.md" knowledge/agents/skills/agent-browser/
fi

if [ -f "$SCRIPT_DIR/src/skills/agent_browser.py" ]; then
    echo "🐍 Copying Python skill wrapper..."
    cp "$SCRIPT_DIR/src/skills/agent_browser.py" src/skills/
fi

if [ -f "$SCRIPT_DIR/src/skills/__init__.py" ]; then
    cp "$SCRIPT_DIR/src/skills/__init__.py" src/skills/
fi

if [ -f "$SCRIPT_DIR/docs/BROWSER_CAPABILITY_MAP.md" ]; then
    echo "📋 Copying capability map..."
    mkdir -p docs
    cp "$SCRIPT_DIR/docs/BROWSER_CAPABILITY_MAP.md" docs/
fi

# Test the installation
echo "🧪 Testing agent-browser..."
agent-browser --version

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Review docs/BROWSER_CAPABILITY_MAP.md for agent integration guide"
echo "  2. Import in your agents: from skills.agent_browser import AgentBrowserSkill"
echo "  3. Test: agent-browser open example.com && agent-browser snapshot -i && agent-browser close"
echo ""
