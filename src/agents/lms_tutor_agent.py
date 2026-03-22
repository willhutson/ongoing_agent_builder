"""
LMS Tutor Agent - DeepTutor-Inspired Intelligent Tutoring

Implements:
- RAG-powered Q&A with citations from course materials
- Socratic teaching methodology (Assess → Retrieve → Explain → Reinforce → Visualize)
- Adaptive explanations based on learner knowledge state
- Interactive visualization generation
- Progressive knowledge extraction with dynamic topic queuing
- Web search supplementation for questions beyond indexed content
"""

from typing import Any
import json
import httpx
from .base import BaseAgent


class LmsTutorAgent(BaseAgent):
    """AI tutor agent providing personalized, citation-backed learning support."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "lms_tutor_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert AI tutor within an enterprise Learning Management System.
You help learners understand course materials through Socratic dialogue, clear explanations,
and adaptive teaching.

Your teaching methodology follows a dual-loop approach inspired by DeepTutor:

**Analysis Loop (Assess + Retrieve):**
1. ASSESS the learner's current understanding level using their knowledge state
2. RETRIEVE relevant content from course materials via RAG search and knowledge base

**Solve Loop (Explain + Reinforce + Visualize):**
3. EXPLAIN concepts with clear, scaffolded explanations and precise citations
4. REINFORCE learning by suggesting follow-up exercises or related topics
5. VISUALIZE complex concepts using diagrams, flowcharts, or concept maps when beneficial

Citation format: Always cite sources as [Module: X, Lesson: Y] or [Section: Z].

Teaching principles:
- Adapt explanation complexity to the learner's demonstrated knowledge level
- Use the Socratic method — ask guiding questions rather than giving direct answers
  when the learner would benefit from reasoning through the problem
- Break complex topics into digestible steps with progressive disclosure
- Connect new concepts to previously learned material
- When course content is insufficient, supplement with web search results (clearly marked)
- Track interactions to improve future recommendations"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "search_course_content",
                "description": "RAG search over indexed course materials. Returns relevant content chunks with source citations for answering learner questions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query based on the learner's question"},
                        "course_id": {"type": "string", "description": "Course to search within"},
                        "top_k": {"type": "integer", "description": "Number of results to return", "default": 5},
                        "include_citations": {"type": "boolean", "description": "Include source references", "default": True},
                    },
                    "required": ["query", "course_id"],
                },
            },
            {
                "name": "get_lesson_content",
                "description": "Retrieve full content of a specific lesson for detailed reference.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "module_id": {"type": "string"},
                        "lesson_id": {"type": "string"},
                    },
                    "required": ["course_id", "module_id", "lesson_id"],
                },
            },
            {
                "name": "get_learner_knowledge_state",
                "description": "Get the learner's current knowledge level, completed topics, and identified gaps for a course or topic. Enables adaptive tutoring.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "learner_id": {"type": "string"},
                        "course_id": {"type": "string", "description": "Optional course scope"},
                        "topic": {"type": "string", "description": "Optional specific topic"},
                    },
                    "required": ["learner_id"],
                },
            },
            {
                "name": "web_search_supplement",
                "description": "Search the web for supplementary information when course materials don't fully cover the learner's question. Results should be clearly marked as external sources.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Number of results", "default": 3},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "create_explanation",
                "description": "Create a structured explanation artifact with examples and citations for complex topics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "explanation": {"type": "string", "description": "The full explanation text"},
                        "examples": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Illustrative examples",
                        },
                        "difficulty_level": {
                            "type": "string",
                            "enum": ["beginner", "intermediate", "advanced"],
                        },
                        "citations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Source references from course materials",
                        },
                    },
                    "required": ["topic", "explanation"],
                },
            },
            {
                "name": "create_visualization",
                "description": "Create a visual learning aid — concept map, flowchart, timeline, or comparison table — to help explain complex concepts.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "concept": {"type": "string", "description": "The concept to visualize"},
                        "visualization_type": {
                            "type": "string",
                            "enum": ["concept_map", "flowchart", "timeline", "comparison_table"],
                        },
                        "elements": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string"},
                                    "connections": {"type": "array", "items": {"type": "string"}},
                                    "description": {"type": "string"},
                                },
                            },
                            "description": "Nodes/items in the visualization",
                        },
                        "title": {"type": "string"},
                    },
                    "required": ["concept", "visualization_type", "elements"],
                },
            },
            {
                "name": "suggest_next_topics",
                "description": "Based on the current conversation and learner state, suggest what to study next. Implements a dynamic topic queue for progressive learning.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "learner_id": {"type": "string"},
                        "current_topic": {"type": "string"},
                        "course_id": {"type": "string"},
                    },
                    "required": ["learner_id", "current_topic", "course_id"],
                },
            },
            {
                "name": "record_interaction",
                "description": "Log the tutoring interaction for analytics and adaptive learning improvements.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "learner_id": {"type": "string"},
                        "course_id": {"type": "string"},
                        "question": {"type": "string"},
                        "topics_covered": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "understanding_level": {
                            "type": "string",
                            "enum": ["struggling", "developing", "proficient", "mastery"],
                        },
                    },
                    "required": ["learner_id", "course_id", "question"],
                },
            },
            {
                "name": "run_code_example",
                "description": "Execute a code snippet to demonstrate a concept in technical courses. Returns the execution output.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "language": {
                            "type": "string",
                            "enum": ["python", "javascript", "typescript", "sql"],
                        },
                        "code": {"type": "string", "description": "Code to execute"},
                        "explanation": {"type": "string", "description": "What this code demonstrates"},
                    },
                    "required": ["language", "code"],
                },
            },
            {
                "name": "search_knowledge_base",
                "description": "Search the organizational knowledge base for supplementary resources. Reuses the KnowledgeAgent's search infrastructure.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "categories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by knowledge categories",
                        },
                    },
                    "required": ["query"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "search_course_content":
                response = await self.http_client.post(
                    "/api/v1/lms/content/search",
                    json={
                        "query": tool_input["query"],
                        "course_id": tool_input["course_id"],
                        "top_k": tool_input.get("top_k", 5),
                        "include_citations": tool_input.get("include_citations", True),
                    },
                )
                if response.status_code == 200:
                    return response.json()
                return {"results": [], "message": "No matching content found"}

            elif tool_name == "get_lesson_content":
                course_id = tool_input["course_id"]
                module_id = tool_input["module_id"]
                lesson_id = tool_input["lesson_id"]
                response = await self.http_client.get(
                    f"/api/v1/lms/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}"
                )
                if response.status_code == 200:
                    return response.json()
                return {"error": "Lesson not found", "lesson_id": lesson_id}

            elif tool_name == "get_learner_knowledge_state":
                params = {"learner_id": tool_input["learner_id"]}
                if "course_id" in tool_input:
                    params["course_id"] = tool_input["course_id"]
                if "topic" in tool_input:
                    params["topic"] = tool_input["topic"]
                response = await self.http_client.get(
                    f"/api/v1/lms/learners/{tool_input['learner_id']}/knowledge-state",
                    params=params,
                )
                if response.status_code == 200:
                    return response.json()
                return {
                    "level": "unknown",
                    "completed_topics": [],
                    "gaps": [],
                    "message": "Knowledge state not available — treat learner as intermediate",
                }

            elif tool_name == "web_search_supplement":
                response = await self.http_client.post(
                    "/api/v1/lms/search/web",
                    json={
                        "query": tool_input["query"],
                        "num_results": tool_input.get("num_results", 3),
                    },
                )
                if response.status_code == 200:
                    return response.json()
                return {"results": [], "message": "Web search unavailable"}

            elif tool_name == "create_explanation":
                return {
                    "artifact_type": "document",
                    "topic": tool_input["topic"],
                    "explanation": tool_input["explanation"],
                    "examples": tool_input.get("examples", []),
                    "difficulty_level": tool_input.get("difficulty_level", "intermediate"),
                    "citations": tool_input.get("citations", []),
                    "status": "created",
                }

            elif tool_name == "create_visualization":
                return {
                    "artifact_type": "chart",
                    "concept": tool_input["concept"],
                    "visualization_type": tool_input["visualization_type"],
                    "elements": tool_input["elements"],
                    "title": tool_input.get("title", tool_input["concept"]),
                    "status": "created",
                }

            elif tool_name == "suggest_next_topics":
                response = await self.http_client.get(
                    f"/api/v1/lms/learners/{tool_input['learner_id']}/recommended-topics",
                    params={
                        "current_topic": tool_input["current_topic"],
                        "course_id": tool_input["course_id"],
                    },
                )
                if response.status_code == 200:
                    return response.json()
                return {"topics": [], "message": "Recommendations not available"}

            elif tool_name == "record_interaction":
                response = await self.http_client.post(
                    "/api/v1/lms/interactions",
                    json={
                        "learner_id": tool_input["learner_id"],
                        "course_id": tool_input["course_id"],
                        "question": tool_input["question"],
                        "topics_covered": tool_input.get("topics_covered", []),
                        "understanding_level": tool_input.get("understanding_level", "developing"),
                    },
                )
                if response.status_code in (200, 201):
                    return response.json()
                return {"status": "recorded_locally"}

            elif tool_name == "run_code_example":
                response = await self.http_client.post(
                    "/api/v1/lms/code/execute",
                    json={
                        "language": tool_input["language"],
                        "code": tool_input["code"],
                    },
                )
                if response.status_code == 200:
                    result = response.json()
                    result["explanation"] = tool_input.get("explanation", "")
                    return result
                return {
                    "output": "Code execution unavailable",
                    "explanation": tool_input.get("explanation", ""),
                }

            elif tool_name == "search_knowledge_base":
                params = {"query": tool_input["query"]}
                if "categories" in tool_input:
                    params["categories"] = json.dumps(tool_input["categories"])
                response = await self.http_client.get(
                    "/api/v1/knowledge/search",
                    params=params,
                )
                if response.status_code == 200:
                    return response.json()
                return {"results": []}

            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
