"""
LMS Content Agent - Course Material Processing & RAG Pipeline

Implements:
- Document ingestion and processing (PDF, DOCX, video transcripts, HTML, Markdown)
- Text chunking and vector embedding for semantic search
- Concept extraction and relationship mapping
- Multi-level content summarization
- Course structure generation from raw materials
- Search index management

Maps to DeepTutor's "Knowledge Foundation" layer.
"""

from typing import Any
import json
import httpx
from .base import BaseAgent


class LmsContentAgent(BaseAgent):
    """Agent for processing course materials into searchable, structured knowledge."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=120.0,  # Longer timeout for document processing
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "lms_content_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a course content processing expert within an enterprise Learning Management System.
You ingest, analyze, and index educational materials to power the RAG-based tutoring system.

Your responsibilities:
1. INGEST uploaded documents (PDFs, DOCX, video transcripts, articles) into the content pipeline
2. EXTRACT key concepts, learning objectives, and topic hierarchies from course materials
3. SUMMARIZE content at multiple granularity levels (brief, standard, detailed) for different use cases
4. MAP concept relationships to build navigable knowledge graphs
5. STRUCTURE raw materials into well-organized course outlines with modules and lessons
6. INDEX content for fast, accurate semantic search by the tutoring agent

Processing principles:
- Preserve source attribution — every chunk must trace back to its origin document, page, and section
- Extract both explicit content and implicit relationships between topics
- Generate embeddings that capture semantic meaning, not just keyword matches
- Identify prerequisite chains so the tutoring agent can recommend proper learning sequences
- Flag content quality issues (gaps, contradictions, outdated information) proactively"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "ingest_document",
                "description": "Process an uploaded document into the RAG pipeline. Extracts text, splits into chunks, and prepares for embedding.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document_url": {"type": "string", "description": "URL or path to the document"},
                        "document_type": {
                            "type": "string",
                            "enum": ["pdf", "docx", "video_transcript", "html", "markdown"],
                        },
                        "course_id": {"type": "string", "description": "Course this document belongs to"},
                        "module_id": {"type": "string", "description": "Optional module scope"},
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata (author, version, etc.)",
                        },
                    },
                    "required": ["document_url", "document_type", "course_id"],
                },
            },
            {
                "name": "extract_concepts",
                "description": "Extract key concepts and their relationships from course content using LLM analysis. Identifies topics, subtopics, definitions, and prerequisite chains.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Text content to analyze"},
                        "course_id": {"type": "string"},
                        "extraction_depth": {
                            "type": "string",
                            "enum": ["surface", "standard", "deep"],
                            "description": "How deeply to analyze the content",
                            "default": "standard",
                        },
                    },
                    "required": ["content", "course_id"],
                },
            },
            {
                "name": "generate_content_summary",
                "description": "Create summaries of course content at multiple granularity levels.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_id": {"type": "string", "description": "ID of the content to summarize"},
                        "levels": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["brief", "standard", "detailed"],
                            },
                            "description": "Summary levels to generate",
                        },
                    },
                    "required": ["content_id", "levels"],
                },
            },
            {
                "name": "build_concept_map",
                "description": "Build a concept relationship graph for a course or module. Shows how topics connect and identifies learning pathways.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "module_id": {"type": "string", "description": "Optional — scope to a single module"},
                    },
                    "required": ["course_id"],
                },
            },
            {
                "name": "chunk_and_embed",
                "description": "Split content into overlapping chunks and generate vector embeddings for semantic search.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_id": {"type": "string", "description": "ID of the ingested content"},
                        "chunk_size": {"type": "integer", "description": "Characters per chunk", "default": 1000},
                        "overlap": {"type": "integer", "description": "Overlap between chunks", "default": 200},
                    },
                    "required": ["content_id"],
                },
            },
            {
                "name": "create_course_structure",
                "description": "Analyze uploaded materials and generate a proposed course structure with modules, lessons, and learning objectives. Emits a COURSE artifact.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "materials": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of content IDs to analyze",
                        },
                        "target_audience": {"type": "string"},
                        "learning_objectives": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "estimated_duration_hours": {"type": "number"},
                    },
                    "required": ["materials", "target_audience", "learning_objectives"],
                },
            },
            {
                "name": "get_content_status",
                "description": "Check the processing status of previously ingested content.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_id": {"type": "string"},
                    },
                    "required": ["content_id"],
                },
            },
            {
                "name": "update_content_index",
                "description": "Refresh the search index for a course after content additions or changes.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                    },
                    "required": ["course_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "ingest_document":
                payload = {
                    "document_url": tool_input["document_url"],
                    "document_type": tool_input["document_type"],
                    "course_id": tool_input["course_id"],
                }
                if "module_id" in tool_input:
                    payload["module_id"] = tool_input["module_id"]
                if "metadata" in tool_input:
                    payload["metadata"] = tool_input["metadata"]
                response = await self.http_client.post(
                    "/api/v1/lms/content/ingest", json=payload
                )
                if response.status_code in (200, 201, 202):
                    return response.json()
                return {"error": "Ingestion failed", "status_code": response.status_code}

            elif tool_name == "extract_concepts":
                # LLM-powered concept extraction — send content to ERP which
                # runs extraction via the agent builder's own LLM pipeline
                response = await self.http_client.post(
                    "/api/v1/lms/content/extract-concepts",
                    json={
                        "content": tool_input["content"],
                        "course_id": tool_input["course_id"],
                        "extraction_depth": tool_input.get("extraction_depth", "standard"),
                    },
                )
                if response.status_code == 200:
                    return response.json()
                return {"concepts": [], "relationships": [], "message": "Extraction unavailable"}

            elif tool_name == "generate_content_summary":
                response = await self.http_client.post(
                    f"/api/v1/lms/content/{tool_input['content_id']}/summarize",
                    json={"levels": tool_input["levels"]},
                )
                if response.status_code == 200:
                    return response.json()
                return {"summaries": {}, "message": "Summarization unavailable"}

            elif tool_name == "build_concept_map":
                params = {"course_id": tool_input["course_id"]}
                if "module_id" in tool_input:
                    params["module_id"] = tool_input["module_id"]
                response = await self.http_client.get(
                    f"/api/v1/lms/courses/{tool_input['course_id']}/concept-map",
                    params=params,
                )
                if response.status_code == 200:
                    data = response.json()
                    data["artifact_type"] = "chart"
                    return data
                return {"nodes": [], "edges": [], "artifact_type": "chart"}

            elif tool_name == "chunk_and_embed":
                response = await self.http_client.post(
                    "/api/v1/lms/content/embed",
                    json={
                        "content_id": tool_input["content_id"],
                        "chunk_size": tool_input.get("chunk_size", 1000),
                        "overlap": tool_input.get("overlap", 200),
                    },
                )
                if response.status_code in (200, 202):
                    return response.json()
                return {"error": "Embedding failed", "status_code": response.status_code}

            elif tool_name == "create_course_structure":
                response = await self.http_client.post(
                    "/api/v1/lms/content/generate-structure",
                    json={
                        "materials": tool_input["materials"],
                        "target_audience": tool_input["target_audience"],
                        "learning_objectives": tool_input["learning_objectives"],
                        "estimated_duration_hours": tool_input.get("estimated_duration_hours"),
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    data["artifact_type"] = "course"
                    return data
                return {"error": "Structure generation failed"}

            elif tool_name == "get_content_status":
                response = await self.http_client.get(
                    f"/api/v1/lms/content/{tool_input['content_id']}/status"
                )
                if response.status_code == 200:
                    return response.json()
                return {"status": "unknown", "content_id": tool_input["content_id"]}

            elif tool_name == "update_content_index":
                response = await self.http_client.post(
                    "/api/v1/lms/content/reindex",
                    json={"course_id": tool_input["course_id"]},
                )
                if response.status_code in (200, 202):
                    return response.json()
                return {"status": "reindex_requested", "course_id": tool_input["course_id"]}

            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
