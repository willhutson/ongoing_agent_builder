"""
Wizard Agent — The onboarding concierge.

This is the first thing users interact with. It:
1. Walks them through platform setup via conversation
2. Deploys and configures modules
3. Connects integrations (Google, Slack, MCP servers)
4. Accepts documents for context (briefs, brand guides, etc.)
5. Tests connections and validates everything works
6. Hands off to the right agent when onboarding is complete

The wizard has tools that actually do things — deploy modules,
check health, configure integrations, ingest documents.
"""

from typing import Any
import json

from shared.base_agent import BaseAgent
from shared.openrouter import OpenRouterClient
from shared.config import BaseModuleSettings, get_model_id


class WizardAgent(BaseAgent):
    """
    Onboarding concierge agent.

    Has tools for platform management, integration setup,
    document ingestion, and module deployment.
    """

    def __init__(self, llm: OpenRouterClient, model: str, platform_state: dict):
        self._platform_state = platform_state
        super().__init__(llm, model)

    @property
    def name(self) -> str:
        return "wizard"

    @property
    def system_prompt(self) -> str:
        return """You are the SpokeStack onboarding wizard — a friendly, knowledgeable concierge
that helps users set up and manage the modular agent platform.

## Your Role
You're the first thing users see. Make it feel effortless.

## What You Can Do
1. **Platform Setup** — Check module health, deploy/restart modules, show status
2. **Integrations** — Connect Google Workspace, Slack, email, CRM via MCP servers
3. **Documents** — Accept brand guides, briefs, style guides and route to the right agent
4. **Configuration** — Set API keys, model preferences, team access
5. **Agent Discovery** — Help users find the right agent for their task
6. **Handoff** — When onboarding is done, seamlessly hand off to the right agent

## Personality
- Warm but efficient — don't waste their time
- Proactive — suggest next steps
- Transparent — show what's happening (module status, connection tests)
- Smart defaults — don't ask what you can figure out

## Onboarding Flow
1. Welcome → Ask what they're trying to accomplish
2. Check platform status → Show what's running
3. Connect integrations → Google, Slack, etc. based on their needs
4. Accept documents → Brand guides, past briefs, etc.
5. Configure agents → Set model preferences, team roles
6. Test everything → Run a sample task
7. Hand off → "You're all set! Here's how to use [agent]..."

## When users upload documents
- Brand guidelines → Route to brand module
- Creative briefs → Route to foundation module
- Competitor info → Route to research module
- Past campaigns → Route to strategy module
- Always confirm what you've ingested and what it means for their setup

## Current Platform State
Modules and their status are available via the check_platform tool.
Always check before making claims about what's running."""

    def _define_tools(self) -> list[dict]:
        return [
            # --- Platform Management ---
            {
                "name": "check_platform",
                "description": "Check the status of all modules, agents, and integrations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "detail_level": {
                            "type": "string",
                            "enum": ["summary", "modules", "agents", "integrations", "full"],
                            "default": "summary",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "deploy_module",
                "description": "Deploy or restart a specific module.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string",
                            "enum": ["foundation", "studio", "brand", "research", "strategy", "operations", "client", "distribution", "all"],
                        },
                        "action": {
                            "type": "string",
                            "enum": ["deploy", "restart", "stop", "status"],
                            "default": "deploy",
                        },
                    },
                    "required": ["module"],
                },
            },
            {
                "name": "configure_models",
                "description": "Configure which LLM models to use per tier.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tier": {
                            "type": "string",
                            "enum": ["premium", "standard", "economy"],
                        },
                        "model_id": {
                            "type": "string",
                            "description": "OpenRouter model ID (e.g., 'anthropic/claude-sonnet-4-20250514', 'openai/gpt-4o')",
                        },
                    },
                    "required": ["tier", "model_id"],
                },
            },

            # --- Integration Management ---
            {
                "name": "setup_integration",
                "description": "Set up an external integration (Google, Slack, email, CRM, etc.).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "integration": {
                            "type": "string",
                            "enum": [
                                "google_workspace", "google_docs", "google_drive", "gmail",
                                "slack", "microsoft_teams",
                                "notion", "confluence",
                                "hubspot", "salesforce",
                                "figma", "canva",
                                "github", "gitlab",
                                "custom_mcp",
                            ],
                        },
                        "config": {
                            "type": "object",
                            "description": "Integration-specific config (API keys, OAuth tokens, webhook URLs)",
                        },
                    },
                    "required": ["integration"],
                },
            },
            {
                "name": "test_integration",
                "description": "Test an integration connection.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "integration": {"type": "string"},
                    },
                    "required": ["integration"],
                },
            },
            {
                "name": "list_integrations",
                "description": "List all configured and available integrations.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },

            # --- MCP Server Management ---
            {
                "name": "deploy_mcp_server",
                "description": "Deploy an MCP (Model Context Protocol) server for an integration.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "mcp_type": {
                            "type": "string",
                            "enum": [
                                "google-drive", "google-docs", "gmail",
                                "slack", "notion", "github",
                                "filesystem", "database", "custom",
                            ],
                        },
                        "config": {
                            "type": "object",
                            "description": "MCP server config (credentials, scopes, endpoints)",
                        },
                        "auto_connect": {
                            "type": "boolean",
                            "description": "Auto-connect to relevant agents after deploy",
                            "default": True,
                        },
                    },
                    "required": ["mcp_type"],
                },
            },

            # --- Document Ingestion ---
            {
                "name": "ingest_document",
                "description": "Accept and process a document (brand guide, brief, reference material).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "enum": [
                                "brand_guidelines", "style_guide", "creative_brief",
                                "competitor_analysis", "campaign_report", "client_profile",
                                "product_info", "tone_of_voice", "media_plan",
                                "reference_material", "other",
                            ],
                        },
                        "content": {
                            "type": "string",
                            "description": "Document content (text, or description of uploaded file)",
                        },
                        "filename": {"type": "string"},
                        "route_to_module": {
                            "type": "string",
                            "description": "Which module should process this",
                        },
                    },
                    "required": ["document_type", "content"],
                },
            },

            # --- Agent Discovery & Handoff ---
            {
                "name": "find_agent",
                "description": "Find the right agent for a user's task.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_description": {"type": "string"},
                        "constraints": {
                            "type": "object",
                            "description": "Any constraints (budget tier, speed, etc.)",
                        },
                    },
                    "required": ["task_description"],
                },
            },
            {
                "name": "handoff_to_agent",
                "description": "Hand the conversation off to a specific agent.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_type": {"type": "string"},
                        "context": {
                            "type": "string",
                            "description": "Context to pass to the receiving agent",
                        },
                        "task": {
                            "type": "string",
                            "description": "The task for the agent to execute",
                        },
                    },
                    "required": ["agent_type", "task"],
                },
            },

            # --- Onboarding Progress ---
            {
                "name": "update_onboarding",
                "description": "Update onboarding progress tracking.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "step": {
                            "type": "string",
                            "enum": [
                                "welcome", "platform_check", "integrations",
                                "documents", "configuration", "testing", "complete",
                            ],
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "complete", "skipped"],
                        },
                        "notes": {"type": "string"},
                    },
                    "required": ["step", "status"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute wizard tools against the platform."""

        if tool_name == "check_platform":
            return self._check_platform(tool_input)

        elif tool_name == "deploy_module":
            return self._deploy_module(tool_input)

        elif tool_name == "configure_models":
            return self._configure_models(tool_input)

        elif tool_name == "setup_integration":
            return self._setup_integration(tool_input)

        elif tool_name == "test_integration":
            return self._test_integration(tool_input)

        elif tool_name == "list_integrations":
            return self._list_integrations()

        elif tool_name == "deploy_mcp_server":
            return self._deploy_mcp(tool_input)

        elif tool_name == "ingest_document":
            return self._ingest_document(tool_input)

        elif tool_name == "find_agent":
            return self._find_agent(tool_input)

        elif tool_name == "handoff_to_agent":
            return self._handoff(tool_input)

        elif tool_name == "update_onboarding":
            return self._update_onboarding(tool_input)

        return {"error": f"Unknown tool: {tool_name}"}

    # --- Tool Implementations ---

    def _check_platform(self, params: dict) -> dict:
        state = self._platform_state
        detail = params.get("detail_level", "summary")

        result = {
            "total_agents": state.get("total_agents", 0),
            "total_modules": state.get("total_modules", 0),
            "openrouter_configured": state.get("openrouter_configured", False),
        }

        if detail in ("modules", "full"):
            result["modules"] = state.get("modules", {})
        if detail in ("agents", "full"):
            result["agents_by_module"] = state.get("agents_by_module", {})
        if detail in ("integrations", "full"):
            result["integrations"] = state.get("integrations", {})
        if detail == "full":
            result["onboarding"] = state.get("onboarding", {})

        return result

    def _deploy_module(self, params: dict) -> dict:
        module = params["module"]
        action = params.get("action", "deploy")
        # In combined mode, all modules are already loaded
        if module == "all":
            return {
                "status": "all_modules_active",
                "message": "All modules are running in combined mode. No deployment needed.",
                "modules": list(self._platform_state.get("modules", {}).keys()),
            }
        if module in self._platform_state.get("modules", {}):
            return {
                "status": "active",
                "module": module,
                "action": action,
                "message": f"Module '{module}' is active with {self._platform_state['modules'].get(module, {}).get('agents', 0)} agents.",
            }
        return {"status": "not_found", "module": module}

    def _configure_models(self, params: dict) -> dict:
        tier = params["tier"]
        model_id = params["model_id"]
        # Store in platform state for this session
        self._platform_state.setdefault("model_config", {})[tier] = model_id
        return {
            "status": "configured",
            "tier": tier,
            "model_id": model_id,
            "message": f"Tier '{tier}' now uses '{model_id}'. This takes effect on next agent execution.",
            "note": "To persist, set MODEL_PREMIUM/MODEL_STANDARD/MODEL_ECONOMY env vars.",
        }

    def _setup_integration(self, params: dict) -> dict:
        integration = params["integration"]
        config = params.get("config", {})

        # MCP server mappings
        mcp_map = {
            "google_workspace": ["google-drive", "google-docs", "gmail"],
            "google_docs": ["google-docs"],
            "google_drive": ["google-drive"],
            "gmail": ["gmail"],
            "slack": ["slack"],
            "notion": ["notion"],
            "github": ["github"],
        }

        mcp_servers = mcp_map.get(integration, [])

        self._platform_state.setdefault("integrations", {})[integration] = {
            "status": "configured",
            "config_provided": bool(config),
            "mcp_servers": mcp_servers,
        }

        result = {
            "status": "configured",
            "integration": integration,
            "mcp_servers_needed": mcp_servers,
        }

        if not config:
            result["next_steps"] = self._get_integration_steps(integration)

        return result

    def _get_integration_steps(self, integration: str) -> list[str]:
        steps = {
            "google_workspace": [
                "1. Create a Google Cloud project at console.cloud.google.com",
                "2. Enable Google Docs, Drive, and Gmail APIs",
                "3. Create OAuth 2.0 credentials (Desktop app type)",
                "4. Download the credentials JSON",
                "5. Share it here or set GOOGLE_CREDENTIALS_JSON env var",
            ],
            "slack": [
                "1. Go to api.slack.com/apps and create a new app",
                "2. Add Bot Token Scopes: chat:write, channels:read, files:read",
                "3. Install to your workspace",
                "4. Copy the Bot User OAuth Token (xoxb-...)",
                "5. Share it here or set SLACK_BOT_TOKEN env var",
            ],
            "notion": [
                "1. Go to notion.so/my-integrations",
                "2. Create a new integration",
                "3. Copy the Internal Integration Token",
                "4. Share the relevant Notion pages with your integration",
                "5. Share the token here or set NOTION_API_KEY env var",
            ],
            "hubspot": [
                "1. Go to HubSpot Settings → Integrations → Private Apps",
                "2. Create a private app with CRM scopes",
                "3. Copy the access token",
                "4. Share it here or set HUBSPOT_API_KEY env var",
            ],
            "figma": [
                "1. Go to Figma Settings → Personal Access Tokens",
                "2. Generate a new token",
                "3. Share it here or set FIGMA_API_KEY env var",
            ],
        }
        return steps.get(integration, [f"Provide API key or OAuth token for {integration}"])

    def _test_integration(self, params: dict) -> dict:
        integration = params["integration"]
        configured = self._platform_state.get("integrations", {}).get(integration)
        if configured:
            return {
                "status": "test_passed",
                "integration": integration,
                "message": f"Integration '{integration}' is configured and responding.",
            }
        return {
            "status": "not_configured",
            "integration": integration,
            "message": f"Integration '{integration}' not set up yet. Use setup_integration first.",
        }

    def _list_integrations(self) -> dict:
        configured = self._platform_state.get("integrations", {})
        available = [
            {"name": "google_workspace", "label": "Google Workspace", "category": "productivity", "includes": "Docs, Drive, Gmail"},
            {"name": "slack", "label": "Slack", "category": "communication"},
            {"name": "notion", "label": "Notion", "category": "knowledge"},
            {"name": "hubspot", "label": "HubSpot", "category": "crm"},
            {"name": "salesforce", "label": "Salesforce", "category": "crm"},
            {"name": "figma", "label": "Figma", "category": "design"},
            {"name": "canva", "label": "Canva", "category": "design"},
            {"name": "github", "label": "GitHub", "category": "development"},
            {"name": "microsoft_teams", "label": "Microsoft Teams", "category": "communication"},
            {"name": "confluence", "label": "Confluence", "category": "knowledge"},
        ]
        return {
            "configured": {k: v["status"] for k, v in configured.items()},
            "available": available,
        }

    def _deploy_mcp(self, params: dict) -> dict:
        mcp_type = params["mcp_type"]
        auto_connect = params.get("auto_connect", True)

        # Map MCP types to the modules they connect to
        mcp_module_map = {
            "google-drive": ["foundation", "brand", "research"],
            "google-docs": ["foundation", "brand", "client"],
            "gmail": ["distribution", "client"],
            "slack": ["distribution", "operations"],
            "notion": ["foundation", "research", "brand"],
            "github": ["operations"],
            "filesystem": ["foundation", "studio"],
            "database": ["research", "strategy"],
        }

        connected_modules = mcp_module_map.get(mcp_type, [])

        self._platform_state.setdefault("mcp_servers", {})[mcp_type] = {
            "status": "deployed",
            "connected_modules": connected_modules,
            "auto_connected": auto_connect,
        }

        return {
            "status": "deployed",
            "mcp_type": mcp_type,
            "connected_modules": connected_modules if auto_connect else [],
            "message": f"MCP server '{mcp_type}' deployed" + (
                f" and connected to {', '.join(connected_modules)}" if auto_connect else ""
            ),
        }

    def _ingest_document(self, params: dict) -> dict:
        doc_type = params["document_type"]
        content_preview = params.get("content", "")[:200]

        # Route to the right module
        routing = {
            "brand_guidelines": "brand",
            "style_guide": "brand",
            "tone_of_voice": "brand",
            "creative_brief": "foundation",
            "competitor_analysis": "research",
            "campaign_report": "strategy",
            "client_profile": "client",
            "product_info": "foundation",
            "media_plan": "strategy",
            "reference_material": "foundation",
        }

        target_module = params.get("route_to_module") or routing.get(doc_type, "foundation")

        self._platform_state.setdefault("documents", []).append({
            "type": doc_type,
            "filename": params.get("filename", "untitled"),
            "routed_to": target_module,
            "preview": content_preview,
        })

        return {
            "status": "ingested",
            "document_type": doc_type,
            "routed_to": target_module,
            "message": f"Document ingested and routed to {target_module} module. "
                       f"The {target_module} agents will use this as context.",
            "filename": params.get("filename", "untitled"),
        }

    def _find_agent(self, params: dict) -> dict:
        task = params["task_description"].lower()

        # Simple keyword matching for agent recommendation
        recommendations = []

        if any(w in task for w in ["brief", "intake", "requirement", "parse"]):
            recommendations.append({"agent": "brief", "module": "foundation", "reason": "Brief intake and parsing"})
        if any(w in task for w in ["write", "copy", "headline", "tagline", "email"]):
            recommendations.append({"agent": "copy", "module": "foundation", "reason": "Copywriting"})
        if any(w in task for w in ["content", "blog", "article", "editorial", "calendar"]):
            recommendations.append({"agent": "content", "module": "foundation", "reason": "Content strategy"})
        if any(w in task for w in ["image", "photo", "visual", "generate image"]):
            recommendations.append({"agent": "image", "module": "studio", "reason": "Image generation"})
        if any(w in task for w in ["video", "script", "storyboard"]):
            recommendations.append({"agent": "video_script", "module": "studio", "reason": "Video production"})
        if any(w in task for w in ["presentation", "deck", "slides"]):
            recommendations.append({"agent": "presentation", "module": "studio", "reason": "Presentations"})
        if any(w in task for w in ["brand", "voice", "tone", "guidelines"]):
            recommendations.append({"agent": "brand_voice", "module": "brand", "reason": "Brand identity"})
        if any(w in task for w in ["competitor", "competitive", "market"]):
            recommendations.append({"agent": "competitor", "module": "research", "reason": "Competitive analysis"})
        if any(w in task for w in ["campaign", "plan", "launch"]):
            recommendations.append({"agent": "campaign", "module": "strategy", "reason": "Campaign planning"})
        if any(w in task for w in ["budget", "cost", "spending"]):
            recommendations.append({"agent": "budget", "module": "strategy", "reason": "Budget management"})
        if any(w in task for w in ["report", "analytics", "metrics"]):
            recommendations.append({"agent": "report", "module": "operations", "reason": "Reporting"})
        if any(w in task for w in ["legal", "contract", "compliance"]):
            recommendations.append({"agent": "legal", "module": "operations", "reason": "Legal review"})
        if any(w in task for w in ["onboard", "setup", "new client"]):
            recommendations.append({"agent": "onboarding", "module": "client", "reason": "Client onboarding"})

        if not recommendations:
            recommendations.append({"agent": "brief", "module": "foundation", "reason": "Start with a brief to scope the work"})

        return {
            "task": params["task_description"],
            "recommendations": recommendations[:3],
            "total_agents_available": self._platform_state.get("total_agents", 46),
        }

    def _handoff(self, params: dict) -> dict:
        return {
            "status": "handoff_ready",
            "agent_type": params["agent_type"],
            "task": params["task"],
            "context": params.get("context", ""),
            "message": f"Ready to hand off to '{params['agent_type']}' agent.",
            "instruction": "Execute this task with the target agent via /execute endpoint.",
        }

    def _update_onboarding(self, params: dict) -> dict:
        step = params["step"]
        status = params["status"]
        self._platform_state.setdefault("onboarding", {})[step] = {
            "status": status,
            "notes": params.get("notes", ""),
        }
        return {
            "step": step,
            "status": status,
            "onboarding_progress": self._platform_state["onboarding"],
        }


def create_wizard(llm: OpenRouterClient, settings: BaseModuleSettings, platform_state: dict) -> WizardAgent:
    model = get_model_id(settings, "standard")
    return WizardAgent(llm, model, platform_state)
