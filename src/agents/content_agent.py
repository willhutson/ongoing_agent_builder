from typing import Any
import httpx
from .base import BaseAgent


class ContentAgent(BaseAgent):
    """
    Agent for generating documents and content assets.

    Capabilities:
    - Generate proposals, SOWs, reports
    - Create presentation outlines and content
    - Draft creative briefs and copy
    - Build executive summaries
    - Generate meeting notes and action items
    - Create client-facing documents from templates
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
        return "content_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert content creator for a professional services agency.

Your role is to create high-quality documents and content assets by:
1. Understanding the purpose, audience, and context of each document
2. Following brand voice and style guidelines
3. Using templates where appropriate
4. Incorporating relevant data and case studies
5. Creating clear, compelling, professional content

Document types you can create:
- Proposals and pitch decks
- Statements of Work (SOWs)
- Project reports and status updates
- Executive summaries
- Creative briefs
- Presentation outlines
- Meeting notes and action items
- Client communications

Guidelines:
- Match tone to audience (formal for contracts, engaging for pitches)
- Be concise but thorough
- Use data and specifics where available
- Structure content for easy scanning
- Include clear next steps/CTAs where appropriate"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "get_template",
                "description": "Retrieve a document template from the system.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "template_type": {
                            "type": "string",
                            "enum": [
                                "proposal",
                                "sow",
                                "report",
                                "executive_summary",
                                "creative_brief",
                                "presentation",
                                "meeting_notes",
                            ],
                            "description": "Type of template to retrieve",
                        },
                        "client_id": {
                            "type": "string",
                            "description": "Client ID for client-specific templates",
                        },
                    },
                    "required": ["template_type"],
                },
            },
            {
                "name": "get_brand_guidelines",
                "description": "Get brand voice and style guidelines for content creation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {
                            "type": "string",
                            "description": "Client ID for client-specific guidelines",
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Type of document for context-specific guidelines",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_project_data",
                "description": "Get project information to incorporate into documents.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project ID to fetch data for",
                        },
                        "include_timeline": {"type": "boolean", "default": True},
                        "include_team": {"type": "boolean", "default": True},
                        "include_budget": {"type": "boolean", "default": False},
                        "include_deliverables": {"type": "boolean", "default": True},
                    },
                    "required": ["project_id"],
                },
            },
            {
                "name": "get_case_studies",
                "description": "Retrieve relevant case studies to reference in documents.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "industry": {"type": "string"},
                        "service_type": {"type": "string"},
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "limit": {"type": "integer", "default": 3},
                    },
                    "required": [],
                },
            },
            {
                "name": "save_document",
                "description": "Save a generated document to the DAM/content system.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "document_type": {
                            "type": "string",
                            "enum": [
                                "proposal",
                                "sow",
                                "report",
                                "executive_summary",
                                "creative_brief",
                                "presentation",
                                "meeting_notes",
                                "other",
                            ],
                        },
                        "content": {
                            "type": "string",
                            "description": "Document content (markdown or structured)",
                        },
                        "sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "heading": {"type": "string"},
                                    "content": {"type": "string"},
                                },
                            },
                            "description": "Document sections if structured",
                        },
                        "project_id": {"type": "string"},
                        "client_id": {"type": "string"},
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata (version, author, etc.)",
                        },
                    },
                    "required": ["title", "document_type", "content"],
                },
            },
            {
                "name": "get_meeting_transcript",
                "description": "Retrieve a meeting transcript to create notes from.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "meeting_id": {"type": "string"},
                        "date": {"type": "string", "description": "Meeting date if no ID"},
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by participants",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "generate_presentation_outline",
                "description": "Generate a structured presentation outline.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "audience": {"type": "string"},
                        "duration_minutes": {"type": "integer"},
                        "key_messages": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "include_data_slides": {"type": "boolean", "default": True},
                    },
                    "required": ["topic", "audience"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "get_template":
                return await self._get_template(tool_input)
            elif tool_name == "get_brand_guidelines":
                return await self._get_brand_guidelines(tool_input)
            elif tool_name == "get_project_data":
                return await self._get_project_data(tool_input)
            elif tool_name == "get_case_studies":
                return await self._get_case_studies(tool_input)
            elif tool_name == "save_document":
                return await self._save_document(tool_input)
            elif tool_name == "get_meeting_transcript":
                return await self._get_meeting_transcript(tool_input)
            elif tool_name == "generate_presentation_outline":
                return await self._generate_presentation_outline(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _get_template(self, params: dict) -> dict:
        """Get document template from ERP."""
        response = await self.http_client.get(
            "/api/v1/content/templates",
            params={
                "type": params["template_type"],
                "client_id": params.get("client_id"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "template": None,
            "note": f"No template found for {params['template_type']}",
        }

    async def _get_brand_guidelines(self, params: dict) -> dict:
        """Get brand guidelines."""
        response = await self.http_client.get(
            "/api/v1/content/brand-guidelines",
            params={
                "client_id": params.get("client_id"),
                "document_type": params.get("document_type"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "guidelines": {
                "tone": "professional, confident, clear",
                "style": "concise, data-driven, action-oriented",
            },
            "note": "Using default agency guidelines",
        }

    async def _get_project_data(self, params: dict) -> dict:
        """Get project data for document creation."""
        response = await self.http_client.get(
            f"/api/v1/projects/{params['project_id']}",
            params={
                "include_timeline": params.get("include_timeline", True),
                "include_team": params.get("include_team", True),
                "include_budget": params.get("include_budget", False),
                "include_deliverables": params.get("include_deliverables", True),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Project not found"}

    async def _get_case_studies(self, params: dict) -> dict:
        """Get relevant case studies."""
        response = await self.http_client.get(
            "/api/v1/content/case-studies",
            params={
                "industry": params.get("industry"),
                "service_type": params.get("service_type"),
                "keywords": ",".join(params.get("keywords", [])),
                "limit": params.get("limit", 3),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"case_studies": [], "note": "No matching case studies found"}

    async def _save_document(self, params: dict) -> dict:
        """Save document to DAM."""
        response = await self.http_client.post(
            "/api/v1/dam/documents",
            json={
                "title": params["title"],
                "document_type": params["document_type"],
                "content": params["content"],
                "sections": params.get("sections", []),
                "project_id": params.get("project_id"),
                "client_id": params.get("client_id"),
                "metadata": params.get("metadata", {}),
                "status": "draft",
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to save document", "status": response.status_code}

    async def _get_meeting_transcript(self, params: dict) -> dict:
        """Get meeting transcript."""
        response = await self.http_client.get(
            "/api/v1/meetings/transcripts",
            params={
                "meeting_id": params.get("meeting_id"),
                "date": params.get("date"),
                "participants": ",".join(params.get("participants", [])),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"transcript": None, "note": "Transcript not found"}

    async def _generate_presentation_outline(self, params: dict) -> dict:
        """Generate presentation outline - Claude will handle actual generation."""
        return {
            "topic": params["topic"],
            "audience": params["audience"],
            "duration_minutes": params.get("duration_minutes", 30),
            "key_messages": params.get("key_messages", []),
            "include_data_slides": params.get("include_data_slides", True),
            "instruction": "Generate a structured presentation outline with slide suggestions.",
        }

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
