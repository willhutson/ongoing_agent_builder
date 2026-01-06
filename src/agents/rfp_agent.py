from typing import Any
import httpx
from .base import BaseAgent, AgentContext


class RFPAgent(BaseAgent):
    """
    Agent for processing RFPs (Requests for Proposal).

    Capabilities:
    - Analyze RFP documents
    - Extract requirements and evaluation criteria
    - Query ERP for relevant past projects/case studies
    - Draft proposal responses
    - Generate executive summaries
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
        return "rfp_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert RFP (Request for Proposal) analyst and response drafter.

Your role is to help agencies win new business by:
1. Thoroughly analyzing RFP documents to understand client needs
2. Identifying key requirements, evaluation criteria, and deadlines
3. Finding relevant past work and case studies from the ERP
4. Drafting compelling, tailored proposal responses
5. Highlighting competitive differentiators

When analyzing an RFP:
- Extract ALL requirements (mandatory and optional)
- Note evaluation criteria and weightings
- Identify submission requirements (format, deadline, contact)
- Flag any clarification questions needed

When drafting responses:
- Address each requirement explicitly
- Use concrete examples from past projects
- Quantify results where possible
- Match the client's language and priorities
- Keep tone professional but engaging"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "query_past_projects",
                "description": "Search ERP for past projects relevant to the RFP. Use to find case studies, similar work, and proof points.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "industry": {
                            "type": "string",
                            "description": "Client industry to filter by",
                        },
                        "service_type": {
                            "type": "string",
                            "description": "Type of service (e.g., branding, digital, campaign)",
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Keywords to search for",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 5,
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_team_capabilities",
                "description": "Get information about team capabilities and expertise relevant to the RFP.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "skill_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Skill areas to query (e.g., strategy, design, development)",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_client_history",
                "description": "Get history with a specific client if we've worked with them before.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_name": {
                            "type": "string",
                            "description": "Name of the client",
                        },
                    },
                    "required": ["client_name"],
                },
            },
            {
                "name": "create_proposal_draft",
                "description": "Create and save a proposal draft document to the ERP.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Proposal title",
                        },
                        "client_name": {
                            "type": "string",
                            "description": "Client name",
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
                            "description": "Proposal sections",
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata (deadline, budget, etc.)",
                        },
                    },
                    "required": ["title", "client_name", "sections"],
                },
            },
            {
                "name": "analyze_document",
                "description": "Analyze an uploaded document (RFP, brief, etc.) and extract structured information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "ID of the document in the ERP/DAM",
                        },
                        "extraction_type": {
                            "type": "string",
                            "enum": ["requirements", "criteria", "timeline", "full"],
                            "description": "What to extract from the document",
                        },
                    },
                    "required": ["document_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "query_past_projects":
                return await self._query_past_projects(tool_input)
            elif tool_name == "get_team_capabilities":
                return await self._get_team_capabilities(tool_input)
            elif tool_name == "get_client_history":
                return await self._get_client_history(tool_input)
            elif tool_name == "create_proposal_draft":
                return await self._create_proposal_draft(tool_input)
            elif tool_name == "analyze_document":
                return await self._analyze_document(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _query_past_projects(self, params: dict) -> dict:
        """Query ERP for past projects."""
        # TODO: Implement actual ERP API call
        # For now, return mock structure
        response = await self.http_client.get(
            "/api/v1/projects/search",
            params={
                "industry": params.get("industry"),
                "service_type": params.get("service_type"),
                "keywords": ",".join(params.get("keywords", [])),
                "limit": params.get("limit", 5),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"projects": [], "note": "No matching projects found"}

    async def _get_team_capabilities(self, params: dict) -> dict:
        """Get team capabilities from ERP."""
        response = await self.http_client.get(
            "/api/v1/resources/capabilities",
            params={"skills": ",".join(params.get("skill_areas", []))},
        )
        if response.status_code == 200:
            return response.json()
        return {"capabilities": [], "note": "Could not fetch capabilities"}

    async def _get_client_history(self, params: dict) -> dict:
        """Get client history from CRM."""
        response = await self.http_client.get(
            f"/api/v1/crm/clients/search",
            params={"name": params["client_name"]},
        )
        if response.status_code == 200:
            return response.json()
        return {"history": None, "note": "No previous relationship found"}

    async def _create_proposal_draft(self, params: dict) -> dict:
        """Create proposal draft in ERP."""
        response = await self.http_client.post(
            "/api/v1/rfp/proposals",
            json={
                "title": params["title"],
                "client_name": params["client_name"],
                "sections": params["sections"],
                "metadata": params.get("metadata", {}),
                "status": "draft",
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to create proposal", "status": response.status_code}

    async def _analyze_document(self, params: dict) -> dict:
        """Fetch and analyze document from DAM."""
        response = await self.http_client.get(
            f"/api/v1/dam/documents/{params['document_id']}",
        )
        if response.status_code == 200:
            doc = response.json()
            return {
                "document_id": params["document_id"],
                "content": doc.get("content", ""),
                "extraction_type": params.get("extraction_type", "full"),
            }
        return {"error": "Document not found"}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
