"""
PromptHelper Agent - Meta-agent for crafting effective prompts and selecting optimal agents.

This agent helps users:
1. Create better prompts for any of the 46 agents
2. Choose the right agent(s) for their task
3. Select optimal LLM providers based on cost/quality needs
4. Understand model tier implications (Economy/Standard/Premium)
"""

from typing import Any
from .base import BaseAgent
from ..services.external_llm_registry import (
    EXTERNAL_LLM_CONFIGS,
    AGENT_EXTERNAL_LLMS,
    ExternalLLMProvider,
)


# Agent capabilities with prompting guidance
AGENT_CATALOG = {
    # ==========================================================================
    # FOUNDATION
    # ==========================================================================
    "rfp": {
        "name": "RFP Agent",
        "tier": "premium",
        "purpose": "RFP analysis, proposal strategy, competitive positioning",
        "external_llms": ["Perplexity"],
        "optimal_inputs": ["RFP document", "company capabilities", "win themes", "competitor intel"],
        "tips": ["Include full RFP or key sections", "Specify differentiation points", "Note any incumbents"],
    },
    "brief": {
        "name": "Brief Agent",
        "tier": "standard",
        "purpose": "Brief intake, parsing, structured requirement extraction",
        "external_llms": [],
        "optimal_inputs": ["Raw client communication", "email/call transcripts", "existing assets"],
        "tips": ["Include all context even if messy", "Note client history", "Flag urgency"],
    },
    "content": {
        "name": "Content Agent",
        "tier": "standard",
        "purpose": "Content strategy, ideation, editorial planning",
        "external_llms": ["DALL-E", "Imagen", "Perplexity"],
        "optimal_inputs": ["Brand guidelines", "target audience", "campaign goals", "SEO keywords"],
        "tips": ["Define content pillars", "Specify formats needed", "Include competitor examples"],
    },
    "commercial": {
        "name": "Commercial Agent",
        "tier": "premium",
        "purpose": "Pricing intelligence, margin analysis, commercial strategy",
        "external_llms": [],
        "optimal_inputs": ["Scope of work", "historical pricing", "cost inputs", "target margins"],
        "tips": ["Include detailed scope", "Provide cost breakdown", "Note fixed-price constraints"],
    },

    # ==========================================================================
    # STUDIO
    # ==========================================================================
    "presentation": {
        "name": "Presentation Agent",
        "tier": "standard",
        "purpose": "AI presentation creation (Beautiful.ai, Gamma, Presenton)",
        "external_llms": ["Presenton (90% margin)", "Gamma", "Beautiful.ai", "DALL-E"],
        "optimal_inputs": ["Content outline", "key messages", "slide count", "visual style"],
        "tips": ["Specify audience and goal", "Include brand colors", "Note mandatory slides"],
    },
    "copy": {
        "name": "Copy Agent",
        "tier": "standard",
        "purpose": "Copywriting for ads, campaigns, marketing",
        "external_llms": ["Google TTS (draft)", "ElevenLabs (final)", "OpenAI TTS"],
        "optimal_inputs": ["Brief", "tone of voice", "target audience", "CTA goals"],
        "tips": ["Include character limits", "Specify placement", "Provide brand voice guidelines"],
    },
    "image": {
        "name": "Image Agent",
        "tier": "standard",
        "purpose": "AI image generation across 5 providers",
        "external_llms": ["DALL-E (premium)", "Flux ($0.003)", "Stability", "Aurora", "Imagen (50% cheaper)"],
        "optimal_inputs": ["Visual concept", "style reference", "aspect ratio", "quality level"],
        "tips": ["Be specific about style", "Include lighting/composition", "Reference similar images"],
    },

    # ==========================================================================
    # VIDEO
    # ==========================================================================
    "video_script": {
        "name": "Video Script Agent",
        "tier": "standard",
        "purpose": "Scriptwriting with VO generation",
        "external_llms": ["ElevenLabs", "Google TTS"],
        "optimal_inputs": ["Video type", "key messages", "duration", "tone"],
        "tips": ["Specify length", "Include distribution channel", "Note talent requirements"],
    },
    "video_storyboard": {
        "name": "Video Storyboard Agent",
        "tier": "standard",
        "purpose": "Visual storyboarding for production",
        "external_llms": ["Higgsfield (12 models)"],
        "optimal_inputs": ["Script", "shot list", "visual references", "production constraints"],
        "tips": ["Provide approved script", "Include reference images", "Specify live vs animation"],
    },
    "video_production": {
        "name": "Video Production Agent",
        "tier": "standard",
        "purpose": "AI video generation (Sora 2, Veo 3, Kling, etc.)",
        "external_llms": ["Higgsfield (12 models: Sora 2, Veo 3, Kling, Minimax, etc.)", "Runway Gen-3"],
        "optimal_inputs": ["Storyboard", "assets", "music/audio", "output specs"],
        "tips": ["Include approved storyboard", "Specify resolution", "Note platform requirements"],
    },

    # ==========================================================================
    # SOCIAL & RESEARCH
    # ==========================================================================
    "social_listening": {
        "name": "Social Listening Agent",
        "tier": "standard",
        "purpose": "Real-time social monitoring and sentiment",
        "external_llms": ["Grok (real-time X/Twitter)", "Perplexity"],
        "optimal_inputs": ["Keywords/hashtags", "competitors", "date range", "platforms"],
        "tips": ["List specific keywords", "Include competitor handles", "Flag crisis terms"],
    },
    "competitor": {
        "name": "Competitor Agent",
        "tier": "premium",
        "purpose": "Competitive intelligence and market analysis",
        "external_llms": ["Grok", "Perplexity", "Gemini Vision (dashboard analysis)"],
        "optimal_inputs": ["Competitor list", "analysis focus", "data sources"],
        "tips": ["List specific competitors", "Specify aspects to analyze", "Include competitor URLs"],
    },
    "pr": {
        "name": "PR Agent",
        "tier": "standard",
        "purpose": "PR strategy, media relations, crisis management",
        "external_llms": ["Grok (breaking news)", "Perplexity"],
        "optimal_inputs": ["News/announcement", "target media", "key messages", "timeline"],
        "tips": ["Include embargo dates", "Specify target outlets", "Note any sensitivities"],
    },
    "influencer": {
        "name": "Influencer Agent",
        "tier": "standard",
        "purpose": "Influencer discovery, outreach, campaign management",
        "external_llms": ["Perplexity", "Gemini Vision", "Grok"],
        "optimal_inputs": ["Campaign goals", "target demographics", "budget", "platform focus"],
        "tips": ["Specify engagement requirements", "Include brand fit criteria", "Note exclusions"],
    },

    # ==========================================================================
    # ANALYTICS
    # ==========================================================================
    "campaign_analytics": {
        "name": "Campaign Analytics Agent",
        "tier": "standard",
        "purpose": "Campaign performance analysis",
        "external_llms": ["Gemini Vision (2M context, 4x cheaper)"],
        "optimal_inputs": ["Campaign data/screenshots", "KPIs", "benchmarks"],
        "tips": ["Include all metrics", "Specify success KPIs", "Provide benchmarks"],
    },
    "social_analytics": {
        "name": "Social Analytics Agent",
        "tier": "standard",
        "purpose": "Social media performance analysis",
        "external_llms": ["Gemini Vision"],
        "optimal_inputs": ["Platform data", "date range", "comparison periods"],
        "tips": ["Include historical data", "Specify platforms", "Note any anomalies"],
    },
    "brand_performance": {
        "name": "Brand Performance Agent",
        "tier": "standard",
        "purpose": "Brand health metrics and tracking",
        "external_llms": ["Gemini Vision"],
        "optimal_inputs": ["Brand metrics", "survey data", "competitor benchmarks"],
        "tips": ["Include sentiment data", "Provide historical trends", "Note measurement methodology"],
    },

    # ==========================================================================
    # FINANCE
    # ==========================================================================
    "invoice": {
        "name": "Invoice Agent",
        "tier": "standard",
        "purpose": "Invoice generation and billing automation",
        "external_llms": [],
        "optimal_inputs": ["Project details", "billing terms", "line items", "client info"],
        "tips": ["Include PO numbers", "Specify payment terms", "Note retainer amounts"],
    },
    "forecast": {
        "name": "Forecast Agent",
        "tier": "premium",
        "purpose": "Revenue forecasting and financial projections",
        "external_llms": [],
        "optimal_inputs": ["Pipeline data", "historical revenue", "assumptions"],
        "tips": ["Include probability scores", "Provide historical trends", "Specify forecast period"],
    },
    "budget": {
        "name": "Budget Agent",
        "tier": "standard",
        "purpose": "Budget planning and tracking",
        "external_llms": [],
        "optimal_inputs": ["Budget constraints", "cost categories", "historical spending"],
        "tips": ["Include all cost centers", "Specify approval thresholds", "Note any caps"],
    },

    # ==========================================================================
    # QUALITY & LEGAL
    # ==========================================================================
    "qa": {
        "name": "QA Agent",
        "tier": "standard",
        "purpose": "Quality assurance and review workflows",
        "external_llms": ["Gemini Vision (bulk screenshots)", "GPT-4 Vision"],
        "optimal_inputs": ["Deliverables/screenshots", "quality criteria", "brand guidelines"],
        "tips": ["Include QA criteria", "Attach brand guidelines", "Specify severity levels"],
    },
    "legal": {
        "name": "Legal Agent",
        "tier": "premium",
        "purpose": "Contract analysis and legal risk assessment",
        "external_llms": [],
        "optimal_inputs": ["Contract text", "company policies", "risk tolerance"],
        "tips": ["Include full contract", "Specify standard terms", "Flag specific clauses"],
    },

    # ==========================================================================
    # DISTRIBUTION
    # ==========================================================================
    "report": {
        "name": "Report Agent",
        "tier": "economy",
        "purpose": "Report distribution and presentation generation",
        "external_llms": ["Gamma", "Zhipu GLM (128K output)"],
        "optimal_inputs": ["Report data", "audience", "format", "key findings"],
        "tips": ["Specify report type", "Include executive summary needs", "Note distribution list"],
    },
    "ops_reporting": {
        "name": "Ops Reporting Agent",
        "tier": "economy",
        "purpose": "Operational KPI aggregation and alerts",
        "external_llms": ["Presenton (90% margin)", "Zhipu GLM"],
        "optimal_inputs": ["KPI data", "thresholds", "comparison periods"],
        "tips": ["Define alert thresholds", "Specify frequency", "Include trend requirements"],
    },

    # ==========================================================================
    # OPERATIONS
    # ==========================================================================
    "resource": {
        "name": "Resource Agent",
        "tier": "standard",
        "purpose": "Resource planning and allocation",
        "external_llms": [],
        "optimal_inputs": ["Project requirements", "team availability", "skills needed"],
        "tips": ["Include skill requirements", "Note timeline constraints", "Specify utilization targets"],
    },
    "workflow": {
        "name": "Workflow Agent",
        "tier": "standard",
        "purpose": "Workflow orchestration and automation",
        "external_llms": [],
        "optimal_inputs": ["Process steps", "dependencies", "stakeholders"],
        "tips": ["Map current process", "Identify bottlenecks", "Specify automation goals"],
    },

    # ==========================================================================
    # CLIENT
    # ==========================================================================
    "crm": {
        "name": "CRM Agent",
        "tier": "standard",
        "purpose": "Client relationship management",
        "external_llms": [],
        "optimal_inputs": ["Client history", "interaction logs", "account status"],
        "tips": ["Include relationship history", "Note key stakeholders", "Flag any issues"],
    },
    "scope": {
        "name": "Scope Agent",
        "tier": "standard",
        "purpose": "Scope definition and change management",
        "external_llms": [],
        "optimal_inputs": ["Project requirements", "constraints", "assumptions"],
        "tips": ["Be specific about deliverables", "Include exclusions", "Note dependencies"],
    },
    "onboarding": {
        "name": "Onboarding Agent",
        "tier": "standard",
        "purpose": "Client onboarding and setup",
        "external_llms": [],
        "optimal_inputs": ["Client info", "requirements", "timeline"],
        "tips": ["Include all stakeholders", "Specify integration needs", "Note training requirements"],
    },

    # ==========================================================================
    # BRAND
    # ==========================================================================
    "brand_voice": {
        "name": "Brand Voice Agent",
        "tier": "standard",
        "purpose": "Brand voice development and cloning",
        "external_llms": ["ElevenLabs (voice cloning)"],
        "optimal_inputs": ["Brand attributes", "sample content", "target audience"],
        "tips": ["Include existing samples", "Specify personality traits", "Note any taboos"],
    },
    "brand_visual": {
        "name": "Brand Visual Agent",
        "tier": "standard",
        "purpose": "Visual brand development",
        "external_llms": ["DALL-E", "Flux", "Stability", "Imagen"],
        "optimal_inputs": ["Brand guidelines", "visual references", "use cases"],
        "tips": ["Include color codes", "Provide mood boards", "Specify asset types needed"],
    },
    "brand_guidelines": {
        "name": "Brand Guidelines Agent",
        "tier": "standard",
        "purpose": "Brand guidelines creation and management",
        "external_llms": [],
        "optimal_inputs": ["Brand elements", "usage rules", "examples"],
        "tips": ["Include all brand elements", "Specify dos and don'ts", "Provide examples"],
    },

    # ==========================================================================
    # SPECIALIZED
    # ==========================================================================
    "events": {
        "name": "Events Agent",
        "tier": "standard",
        "purpose": "Event planning and management",
        "external_llms": ["DALL-E", "Beautiful.ai"],
        "optimal_inputs": ["Event brief", "audience", "budget", "venue"],
        "tips": ["Specify event type", "Include logistics", "Note catering needs"],
    },
    "localization": {
        "name": "Localization Agent",
        "tier": "standard",
        "purpose": "Content localization and translation",
        "external_llms": ["Google TTS", "ElevenLabs", "Whisper"],
        "optimal_inputs": ["Source content", "target languages", "cultural context"],
        "tips": ["Specify markets", "Include cultural notes", "Note any taboos"],
    },
    "accessibility": {
        "name": "Accessibility Agent",
        "tier": "standard",
        "purpose": "Accessibility compliance and enhancements",
        "external_llms": ["Google TTS", "ElevenLabs", "Whisper"],
        "optimal_inputs": ["Content to assess", "compliance standards", "audience needs"],
        "tips": ["Specify WCAG level", "Include alt text needs", "Note audio requirements"],
    },
    "knowledge": {
        "name": "Knowledge Agent",
        "tier": "standard",
        "purpose": "Knowledge base management",
        "external_llms": [],
        "optimal_inputs": ["Knowledge content", "taxonomy", "access rules"],
        "tips": ["Include metadata", "Specify categorization", "Note update frequency"],
    },
    "training": {
        "name": "Training Agent",
        "tier": "standard",
        "purpose": "Training program development",
        "external_llms": [],
        "optimal_inputs": ["Learning objectives", "audience level", "delivery format"],
        "tips": ["Specify prerequisites", "Include assessment needs", "Note certification requirements"],
    },
    "community": {
        "name": "Community Agent",
        "tier": "standard",
        "purpose": "Community management and engagement",
        "external_llms": ["DALL-E", "Imagen"],
        "optimal_inputs": ["Community guidelines", "engagement goals", "content calendar"],
        "tips": ["Include moderation rules", "Specify response times", "Note escalation paths"],
    },
    "media_buying": {
        "name": "Media Buying Agent",
        "tier": "standard",
        "purpose": "Media planning and buying",
        "external_llms": ["DALL-E", "Imagen"],
        "optimal_inputs": ["Budget", "target audience", "channels", "KPIs"],
        "tips": ["Include historical performance", "Specify bid strategies", "Note placement preferences"],
    },
    "campaign": {
        "name": "Campaign Agent",
        "tier": "standard",
        "purpose": "Campaign planning and execution",
        "external_llms": ["Higgsfield", "DALL-E", "Imagen"],
        "optimal_inputs": ["Campaign brief", "objectives", "timeline", "budget"],
        "tips": ["Include all channels", "Specify creative needs", "Note measurement plan"],
    },
}

# Provider cost/quality matrix for recommendations
PROVIDER_MATRIX = {
    "image": {
        "economy": {"provider": "Flux Schnell", "cost": "$0.003/image", "quality": "Good for drafts"},
        "standard": {"provider": "Imagen 3", "cost": "$0.02/image", "quality": "50% cheaper than DALL-E"},
        "premium": {"provider": "DALL-E 3 HD", "cost": "$0.08/image", "quality": "Highest quality"},
    },
    "video": {
        "economy": {"provider": "Pika/Seedance", "cost": "$0.40/10s", "quality": "Quick drafts"},
        "standard": {"provider": "Kling 1.6", "cost": "$0.80/10s", "quality": "Good quality"},
        "premium": {"provider": "Sora 2/Veo 3", "cost": "$2.00/10s", "quality": "Best quality"},
    },
    "voice": {
        "economy": {"provider": "Google TTS", "cost": "$4/1M chars", "quality": "75x cheaper, good for drafts"},
        "standard": {"provider": "OpenAI TTS", "cost": "$15/1M chars", "quality": "Balanced"},
        "premium": {"provider": "ElevenLabs", "cost": "$300/1M chars", "quality": "Best, voice cloning"},
    },
    "presentation": {
        "economy": {"provider": "Presenton", "cost": "~$0.10/10 slides", "quality": "90% margin, internal use"},
        "standard": {"provider": "Gamma", "cost": "~$4/10 slides", "quality": "Client-facing"},
        "premium": {"provider": "Beautiful.ai", "cost": "~$6/10 slides", "quality": "Premium decks"},
    },
    "text": {
        "economy": {"provider": "Gemini Flash", "cost": "$0.10/1M tokens", "quality": "Routing/classification"},
        "standard": {"provider": "GLM-4.7", "cost": "$2.20/1M tokens", "quality": "5x cheaper, 128K output"},
        "premium": {"provider": "Claude Opus", "cost": "$75/1M tokens", "quality": "Best reasoning"},
    },
    "research": {
        "economy": {"provider": "Perplexity Sonar", "cost": "$1/1k queries", "quality": "Basic search"},
        "standard": {"provider": "Perplexity Pro", "cost": "$5/1k queries", "quality": "Deep research"},
        "premium": {"provider": "Grok + Perplexity", "cost": "~$8/1k queries", "quality": "Real-time + research"},
    },
}


class PromptHelperAgent(BaseAgent):
    """
    Meta-agent that helps users craft better prompts and select optimal agents.

    Capabilities:
    - Agent discovery and recommendation
    - Prompt analysis and optimization
    - Provider selection based on cost/quality
    - Tier-aware recommendations (Economy/Standard/Premium)
    """

    def __init__(self, client, model: str, erp_base_url: str = None, erp_api_key: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "prompt_helper_agent"

    @property
    def system_prompt(self) -> str:
        return """You are the Prompt Helper Agent - a meta-agent that helps users get the best results from the 46-agent ecosystem and 14 external LLM providers.

Your responsibilities:
1. AGENT SELECTION: Recommend the right agent(s) for any task
2. PROMPT OPTIMIZATION: Help users craft effective prompts
3. PROVIDER SELECTION: Recommend optimal LLM providers based on cost/quality needs
4. TIER GUIDANCE: Explain Economy/Standard/Premium implications

Key knowledge:
- 46 specialized agents across Foundation, Studio, Video, Social, Analytics, Finance, Quality, Distribution, Operations, Client, Brand, and Specialized modules
- 14 external LLM providers: Higgsfield (12 video models), Runway, DALL-E, Flux, Stability, Aurora, Imagen, ElevenLabs, OpenAI TTS/Whisper/Vision, Google TTS/Gemini/Vision, Beautiful.ai, Gamma, Presenton, Perplexity, Grok, Zhipu GLM
- Three pricing tiers: Economy (budget), Standard (balanced), Premium (best quality)

When helping users:
1. First understand their goal
2. Recommend the most appropriate agent(s)
3. Suggest the right provider tier based on their needs
4. Identify missing information in their prompt
5. Provide an optimized, structured prompt

Be concise but thorough. Your goal is to maximize efficiency and quality of every agent interaction."""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "find_agents_for_task",
                "description": "Find the best agent(s) for a specific task",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "What the user wants to accomplish",
                        },
                        "budget_tier": {
                            "type": "string",
                            "enum": ["economy", "standard", "premium"],
                            "description": "Budget preference for external LLM usage",
                        },
                    },
                    "required": ["task_description"],
                },
            },
            {
                "name": "get_agent_details",
                "description": "Get detailed information about a specific agent",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Agent name (e.g., 'image', 'video_production', 'rfp')",
                        },
                    },
                    "required": ["agent_name"],
                },
            },
            {
                "name": "analyze_and_improve_prompt",
                "description": "Analyze a prompt and suggest improvements",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target_agent": {
                            "type": "string",
                            "description": "The agent this prompt is for",
                        },
                        "current_prompt": {
                            "type": "string",
                            "description": "The user's current prompt",
                        },
                    },
                    "required": ["target_agent", "current_prompt"],
                },
            },
            {
                "name": "get_provider_recommendations",
                "description": "Get provider recommendations for a capability",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "capability": {
                            "type": "string",
                            "enum": ["image", "video", "voice", "presentation", "text", "research"],
                            "description": "The capability type",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["cost", "quality", "balanced"],
                            "description": "What to optimize for",
                        },
                    },
                    "required": ["capability"],
                },
            },
            {
                "name": "generate_structured_prompt",
                "description": "Generate a structured prompt template for an agent",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Target agent name",
                        },
                        "use_case": {
                            "type": "string",
                            "description": "Specific use case description",
                        },
                    },
                    "required": ["agent_name", "use_case"],
                },
            },
            {
                "name": "list_all_agents",
                "description": "List all available agents grouped by module",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string",
                            "enum": ["all", "foundation", "studio", "video", "social", "analytics",
                                    "finance", "quality", "distribution", "operations", "client",
                                    "brand", "specialized"],
                            "description": "Filter by module",
                        },
                    },
                },
            },
            {
                "name": "list_all_providers",
                "description": "List all external LLM providers with capabilities",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["all", "video", "image", "voice", "vision", "presentation",
                                    "research", "routing"],
                            "description": "Filter by capability category",
                        },
                    },
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "find_agents_for_task":
            return self._find_agents(
                tool_input["task_description"],
                tool_input.get("budget_tier", "standard"),
            )
        elif tool_name == "get_agent_details":
            return self._get_agent_details(tool_input["agent_name"])
        elif tool_name == "analyze_and_improve_prompt":
            return self._analyze_prompt(
                tool_input["target_agent"],
                tool_input["current_prompt"],
            )
        elif tool_name == "get_provider_recommendations":
            return self._get_provider_recommendations(
                tool_input["capability"],
                tool_input.get("priority", "balanced"),
            )
        elif tool_name == "generate_structured_prompt":
            return self._generate_prompt_template(
                tool_input["agent_name"],
                tool_input["use_case"],
            )
        elif tool_name == "list_all_agents":
            return self._list_agents(tool_input.get("module", "all"))
        elif tool_name == "list_all_providers":
            return self._list_providers(tool_input.get("category", "all"))
        return {"error": f"Unknown tool: {tool_name}"}

    def _find_agents(self, task_description: str, budget_tier: str) -> dict:
        """Find agents matching a task description."""
        task_lower = task_description.lower()
        matches = []

        for agent_key, info in AGENT_CATALOG.items():
            score = 0
            # Check purpose
            for word in task_lower.split():
                if len(word) > 3 and word in info["purpose"].lower():
                    score += 3
            # Check inputs
            for input_type in info["optimal_inputs"]:
                if any(w in input_type.lower() for w in task_lower.split() if len(w) > 3):
                    score += 1

            if score > 0:
                matches.append({
                    "agent": agent_key,
                    "name": info["name"],
                    "purpose": info["purpose"],
                    "tier": info["tier"],
                    "external_llms": info["external_llms"],
                    "relevance": score,
                })

        matches.sort(key=lambda x: x["relevance"], reverse=True)

        return {
            "task": task_description,
            "budget_tier": budget_tier,
            "recommended_agents": matches[:5],
            "tip": f"Using '{budget_tier}' tier providers where applicable",
        }

    def _get_agent_details(self, agent_name: str) -> dict:
        """Get detailed info about an agent."""
        key = agent_name.replace("_agent", "")
        if key in AGENT_CATALOG:
            info = AGENT_CATALOG[key].copy()
            info["agent_key"] = key
            return info
        return {
            "error": f"Unknown agent: {agent_name}",
            "available": list(AGENT_CATALOG.keys()),
        }

    def _analyze_prompt(self, target_agent: str, current_prompt: str) -> dict:
        """Analyze and improve a prompt."""
        key = target_agent.replace("_agent", "")
        if key not in AGENT_CATALOG:
            return {"error": f"Unknown agent: {target_agent}"}

        info = AGENT_CATALOG[key]
        prompt_lower = current_prompt.lower()
        issues = []
        missing = []

        # Check for optimal inputs
        for input_type in info["optimal_inputs"]:
            keywords = [w.lower() for w in input_type.split() if len(w) > 3]
            if not any(kw in prompt_lower for kw in keywords):
                missing.append(input_type)

        if missing:
            issues.append(f"Missing key inputs: {', '.join(missing[:3])}")

        # Check length
        word_count = len(current_prompt.split())
        if word_count < 15:
            issues.append("Prompt is brief - consider adding more context")
        elif word_count > 500:
            issues.append("Prompt is very long - consider focusing on essentials")

        # Applicable tips
        applicable_tips = [tip for tip in info["tips"] if not any(
            w.lower() in prompt_lower for w in tip.split()[:3] if len(w) > 4
        )]

        return {
            "agent": target_agent,
            "word_count": word_count,
            "issues": issues,
            "missing_inputs": missing,
            "tips": applicable_tips[:3],
            "external_llms": info["external_llms"],
            "tier": info["tier"],
        }

    def _get_provider_recommendations(self, capability: str, priority: str) -> dict:
        """Get provider recommendations."""
        if capability not in PROVIDER_MATRIX:
            return {"error": f"Unknown capability: {capability}"}

        matrix = PROVIDER_MATRIX[capability]

        if priority == "cost":
            recommended = matrix["economy"]
            alternatives = [matrix["standard"]]
        elif priority == "quality":
            recommended = matrix["premium"]
            alternatives = [matrix["standard"]]
        else:
            recommended = matrix["standard"]
            alternatives = [matrix["economy"], matrix["premium"]]

        return {
            "capability": capability,
            "priority": priority,
            "recommended": recommended,
            "alternatives": alternatives,
            "all_options": matrix,
        }

    def _generate_prompt_template(self, agent_name: str, use_case: str) -> dict:
        """Generate structured prompt template."""
        key = agent_name.replace("_agent", "")
        if key not in AGENT_CATALOG:
            return {"error": f"Unknown agent: {agent_name}"}

        info = AGENT_CATALOG[key]

        template_parts = [
            f"## Task: {use_case}",
            "",
            "## Required Information",
        ]

        for input_type in info["optimal_inputs"]:
            template_parts.append(f"**{input_type}:**\n[Provide here]")

        template_parts.extend([
            "",
            "## Additional Context",
            "[Any constraints, preferences, or background]",
            "",
            "## Expected Output",
            "[Describe desired format and deliverables]",
        ])

        return {
            "agent": agent_name,
            "use_case": use_case,
            "template": "\n".join(template_parts),
            "tips": info["tips"],
            "external_llms": info["external_llms"],
        }

    def _list_agents(self, module: str) -> dict:
        """List agents by module."""
        module_mapping = {
            "foundation": ["rfp", "brief", "content", "commercial"],
            "studio": ["presentation", "copy", "image"],
            "video": ["video_script", "video_storyboard", "video_production"],
            "social": ["social_listening", "community", "social_analytics"],
            "analytics": ["campaign_analytics", "brand_performance", "competitor"],
            "finance": ["invoice", "forecast", "budget"],
            "quality": ["qa", "legal"],
            "distribution": ["report", "ops_reporting"],
            "operations": ["resource", "workflow"],
            "client": ["crm", "scope", "onboarding"],
            "brand": ["brand_voice", "brand_visual", "brand_guidelines"],
            "specialized": ["events", "localization", "accessibility", "knowledge",
                          "training", "influencer", "pr", "media_buying", "campaign"],
        }

        if module == "all":
            result = {}
            for mod, agents in module_mapping.items():
                result[mod] = [
                    {"agent": a, "name": AGENT_CATALOG.get(a, {}).get("name", a)}
                    for a in agents if a in AGENT_CATALOG
                ]
            return {"modules": result, "total_agents": len(AGENT_CATALOG)}

        agents = module_mapping.get(module, [])
        return {
            "module": module,
            "agents": [
                {"agent": a, **AGENT_CATALOG.get(a, {})}
                for a in agents if a in AGENT_CATALOG
            ],
        }

    def _list_providers(self, category: str) -> dict:
        """List external LLM providers."""
        category_mapping = {
            "video": [ExternalLLMProvider.HIGGSFIELD, ExternalLLMProvider.RUNWAY],
            "image": [ExternalLLMProvider.OPENAI_DALLE, ExternalLLMProvider.REPLICATE_FLUX,
                     ExternalLLMProvider.STABILITY, ExternalLLMProvider.XAI_AURORA,
                     ExternalLLMProvider.GOOGLE_IMAGEN],
            "voice": [ExternalLLMProvider.ELEVENLABS, ExternalLLMProvider.OPENAI_TTS,
                     ExternalLLMProvider.GOOGLE_TTS, ExternalLLMProvider.OPENAI_WHISPER],
            "vision": [ExternalLLMProvider.OPENAI_VISION, ExternalLLMProvider.GOOGLE_GEMINI_VISION],
            "presentation": [ExternalLLMProvider.BEAUTIFUL_AI, ExternalLLMProvider.GAMMA,
                           ExternalLLMProvider.PRESENTON],
            "research": [ExternalLLMProvider.PERPLEXITY, ExternalLLMProvider.XAI_GROK],
            "routing": [ExternalLLMProvider.GOOGLE_GEMINI, ExternalLLMProvider.ZHIPU_GLM],
        }

        if category == "all":
            providers = list(EXTERNAL_LLM_CONFIGS.values())
        else:
            provider_list = category_mapping.get(category, [])
            providers = [EXTERNAL_LLM_CONFIGS[p] for p in provider_list]

        return {
            "category": category,
            "providers": [
                {
                    "id": p.provider.value,
                    "name": p.name,
                    "description": p.description,
                    "capabilities": p.capabilities,
                    "models": p.models or [],
                }
                for p in providers
            ],
            "total": len(providers),
        }
