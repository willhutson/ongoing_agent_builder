from typing import Any
import httpx
from .base import BaseAgent


class BriefAgent(BaseAgent):
    """
    Agent for AI-assisted brief intake and management.

    Capabilities:
    - Parse incoming brief requests (email, forms, documents)
    - Extract structured requirements from unstructured input
    - Identify missing information and generate clarifying questions
    - Match briefs to relevant past projects for scoping
    - Create draft briefs in ERP with proper categorization
    - Estimate initial scope/complexity
    """

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=30.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "brief_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert brief intake specialist for a professional services agency.

Your role is to transform raw client requests into structured, actionable briefs by:
1. Extracting key information from any input format (emails, calls, documents)
2. Identifying the core objectives and deliverables
3. Spotting gaps and generating smart clarifying questions
4. Categorizing work type (campaign, brand, digital, content, etc.)
5. Estimating complexity and flagging risks early

When processing a brief:
- Extract: Client name, project name, objectives, deliverables, timeline, budget hints
- Categorize: Service type, industry, complexity level
- Identify gaps: What's missing that we need to ask?
- Find similar: Past projects that can inform scoping
- Draft: Create a structured brief ready for review

Always be thorough but concise. Flag assumptions clearly.
Ask clarifying questions when critical information is missing."""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "parse_brief_input",
                "description": "Parse raw input (email, transcript, document) and extract structured brief information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "raw_input": {
                            "type": "string",
                            "description": "The raw text input to parse",
                        },
                        "input_type": {
                            "type": "string",
                            "enum": ["email", "call_transcript", "document", "form", "chat"],
                            "description": "Type of input being parsed",
                        },
                    },
                    "required": ["raw_input"],
                },
            },
            {
                "name": "search_similar_briefs",
                "description": "Search ERP for similar past briefs to inform scoping and estimation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "service_type": {
                            "type": "string",
                            "description": "Type of service (branding, digital, campaign, etc.)",
                        },
                        "industry": {
                            "type": "string",
                            "description": "Client industry",
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Keywords to match",
                        },
                        "complexity": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Estimated complexity level",
                        },
                        "limit": {
                            "type": "integer",
                            "default": 5,
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_client_context",
                "description": "Get context about a client - past work, preferences, contacts.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_name": {
                            "type": "string",
                            "description": "Client name to look up",
                        },
                        "include_briefs": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include past briefs",
                        },
                        "include_contacts": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include contact information",
                        },
                    },
                    "required": ["client_name"],
                },
            },
            {
                "name": "create_draft_brief",
                "description": "Create a draft brief in the ERP system.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string"},
                        "project_name": {"type": "string"},
                        "objectives": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of project objectives",
                        },
                        "deliverables": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "quantity": {"type": "integer"},
                                },
                            },
                            "description": "List of deliverables",
                        },
                        "service_type": {"type": "string"},
                        "timeline": {
                            "type": "object",
                            "properties": {
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"},
                                "milestones": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                        "budget_indication": {"type": "string"},
                        "complexity": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                        },
                        "gaps": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Information gaps / clarifying questions needed",
                        },
                        "notes": {"type": "string"},
                    },
                    "required": ["client_name", "project_name", "objectives"],
                },
            },
            {
                "name": "generate_clarifying_questions",
                "description": "Generate smart clarifying questions based on identified gaps.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_context": {
                            "type": "string",
                            "description": "Context about the brief so far",
                        },
                        "gaps": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Identified information gaps",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "important", "nice_to_have"],
                            "description": "Filter questions by priority",
                        },
                    },
                    "required": ["brief_context", "gaps"],
                },
            },
            {
                "name": "estimate_complexity",
                "description": "Estimate project complexity based on brief details and similar past projects.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deliverables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of deliverables",
                        },
                        "timeline_days": {
                            "type": "integer",
                            "description": "Number of days for project",
                        },
                        "service_type": {"type": "string"},
                        "client_type": {
                            "type": "string",
                            "enum": ["new", "existing", "retainer"],
                        },
                    },
                    "required": ["deliverables"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "parse_brief_input":
                return await self._parse_brief_input(tool_input)
            elif tool_name == "search_similar_briefs":
                return await self._search_similar_briefs(tool_input)
            elif tool_name == "get_client_context":
                return await self._get_client_context(tool_input)
            elif tool_name == "create_draft_brief":
                return await self._create_draft_brief(tool_input)
            elif tool_name == "generate_clarifying_questions":
                return await self._generate_clarifying_questions(tool_input)
            elif tool_name == "estimate_complexity":
                return await self._estimate_complexity(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _parse_brief_input(self, params: dict) -> dict:
        """Parse raw input - this could call an NLP service or do local processing."""
        # For now, return structure for Claude to fill
        return {
            "status": "ready_for_extraction",
            "input_type": params.get("input_type", "unknown"),
            "input_length": len(params.get("raw_input", "")),
            "instruction": "Extract structured brief information from the raw input provided.",
        }

    async def _search_similar_briefs(self, params: dict) -> dict:
        """Search ERP for similar briefs."""
        response = await self.http_client.get(
            "/api/v1/briefs/search",
            params={
                "service_type": params.get("service_type"),
                "industry": params.get("industry"),
                "keywords": ",".join(params.get("keywords", [])),
                "complexity": params.get("complexity"),
                "limit": params.get("limit", 5),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"briefs": [], "note": "No similar briefs found"}

    async def _get_client_context(self, params: dict) -> dict:
        """Get client context from CRM."""
        response = await self.http_client.get(
            "/api/v1/crm/clients/search",
            params={
                "name": params["client_name"],
                "include_briefs": params.get("include_briefs", True),
                "include_contacts": params.get("include_contacts", True),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"client": None, "note": "Client not found - may be new"}

    async def _create_draft_brief(self, params: dict) -> dict:
        """Create draft brief in ERP."""
        response = await self.http_client.post(
            "/api/v1/briefs",
            json={
                **params,
                "status": "draft",
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to create brief", "status": response.status_code}

    async def _generate_clarifying_questions(self, params: dict) -> dict:
        """Generate clarifying questions - Claude will handle the actual generation."""
        return {
            "context": params["brief_context"],
            "gaps": params["gaps"],
            "priority_filter": params.get("priority", "all"),
            "instruction": "Generate specific, actionable clarifying questions for each gap.",
        }

    async def _estimate_complexity(self, params: dict) -> dict:
        """Estimate complexity based on deliverables and similar projects."""
        # Query for similar projects to inform estimate
        response = await self.http_client.get(
            "/api/v1/briefs/complexity-benchmark",
            params={
                "deliverables": ",".join(params.get("deliverables", [])),
                "service_type": params.get("service_type"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "estimated_complexity": "medium",
            "confidence": "low",
            "note": "No benchmark data available - estimate based on deliverables only",
        }

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
