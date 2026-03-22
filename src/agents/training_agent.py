"""
Training Agent - LMS Orchestrator

Enhanced from basic CRUD to serve as the central LMS orchestrator that:
- Handles direct training operations (create, assign, track, quiz, certifications)
- Delegates intelligent tutoring to LmsTutorAgent
- Delegates content processing to LmsContentAgent
- Delegates adaptive assessment to LmsAssessmentAgent
- Manages learner profiles, learning paths, and analytics

Uses the HandoffContext/HandoffRequest protocol for sub-agent delegation.
Maps to DeepTutor's dual-loop pattern: analysis loop determines intent,
then dispatches to the appropriate specialized agent.
"""

from typing import Any
import json
import httpx
from .base import BaseAgent
from ..protocols.handoffs import HandoffContext, HandoffRequest


class TrainingAgent(BaseAgent):
    """LMS orchestrator agent — triages requests and delegates to specialized LMS sub-agents."""

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
        return "training_agent"

    @property
    def system_prompt(self) -> str:
        return """You are the LMS orchestrator for an enterprise Learning Management System.
You manage the full lifecycle of training and learning, from course creation to learner certification.

You have two modes of operation:

**Direct Operations** — handle these yourself:
- Creating and managing training modules
- Assigning training to users
- Tracking learner progress
- Managing certifications
- Searching courses
- Viewing learner profiles and analytics
- Creating learning paths

**Delegated Intelligence** — hand off to specialized agents:
- When a learner asks a question about course content → hand off to the LMS Tutor Agent
  (provides RAG-powered answers with citations, Socratic dialogue, visualizations)
- When documents need to be processed or indexed → hand off to the LMS Content Agent
  (handles ingestion, chunking, embedding, concept extraction, course structure generation)
- When assessments need to be generated or evaluated → hand off to the LMS Assessment Agent
  (creates adaptive quizzes, evaluates responses, generates practice exercises, analyzes gaps)

Routing guidelines:
- "Help me understand X" / "Explain X" / "What does X mean?" → Tutor Agent
- "Upload this document" / "Index this content" / "Create a course from these materials" → Content Agent
- "Quiz me on X" / "Generate an assessment" / "How am I doing?" → Assessment Agent
- "Create a training module" / "Assign this course" / "Show my certifications" → Handle directly

Always provide context when handing off: include the learner's ID, course ID, and any relevant
conversation history so the sub-agent can continue seamlessly."""

    def _define_tools(self) -> list[dict]:
        return [
            # === Direct Operations (existing) ===
            {
                "name": "create_training",
                "description": "Create a training module in the LMS.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "object"},
                        "type": {"type": "string"},
                    },
                    "required": ["title"],
                },
            },
            {
                "name": "assign_training",
                "description": "Assign training to one or more users.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "training_id": {"type": "string"},
                        "user_ids": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["training_id", "user_ids"],
                },
            },
            {
                "name": "track_progress",
                "description": "Track training progress for a user or course.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "training_id": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "create_quiz",
                "description": "Create a basic training quiz. For adaptive/intelligent assessment generation, use handoff_to_assessment instead.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "training_id": {"type": "string"},
                        "questions": {"type": "array", "items": {"type": "object"}},
                    },
                    "required": ["training_id", "questions"],
                },
            },
            {
                "name": "get_certifications",
                "description": "Get certifications earned by a user.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                    },
                    "required": ["user_id"],
                },
            },
            # === New Direct Operations ===
            {
                "name": "get_learner_profile",
                "description": "Fetch a learner's complete profile including progress across courses, knowledge gaps, and recommended next steps.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                    },
                    "required": ["user_id"],
                },
            },
            {
                "name": "create_learning_path",
                "description": "Create a personalized learning path based on learner goals and current level. Sequences courses and modules for optimal progression.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "learner_id": {"type": "string"},
                        "goal": {"type": "string", "description": "What the learner wants to achieve"},
                        "current_level": {
                            "type": "string",
                            "enum": ["beginner", "intermediate", "advanced"],
                        },
                        "course_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific courses to include",
                        },
                        "duration_weeks": {"type": "integer", "description": "Target duration in weeks"},
                    },
                    "required": ["learner_id", "goal"],
                },
            },
            {
                "name": "get_learning_analytics",
                "description": "Retrieve analytics for a course, module, or learner — enrollment rates, completion rates, average scores, time spent.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "scope": {
                            "type": "string",
                            "enum": ["course", "module", "learner", "organization"],
                        },
                        "scope_id": {"type": "string", "description": "ID of the course, module, learner, or org"},
                        "time_range": {
                            "type": "string",
                            "enum": ["7d", "30d", "90d", "all"],
                            "default": "30d",
                        },
                    },
                    "required": ["scope", "scope_id"],
                },
            },
            {
                "name": "search_courses",
                "description": "Search available courses with filtering by status, category, skill level.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "status": {
                            "type": "string",
                            "enum": ["published", "draft", "archived"],
                        },
                        "category": {"type": "string"},
                        "skill_level": {
                            "type": "string",
                            "enum": ["beginner", "intermediate", "advanced"],
                        },
                    },
                    "required": [],
                },
            },
            # === Handoff Operations ===
            {
                "name": "handoff_to_tutor",
                "description": "Route a tutoring or Q&A request to the LMS Tutor Agent. Use when a learner asks a question about course content, needs an explanation, or wants guided learning.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "The learner's question or request"},
                        "course_id": {"type": "string"},
                        "learner_id": {"type": "string"},
                        "learner_context": {
                            "type": "object",
                            "description": "Additional context about the learner's current state",
                        },
                    },
                    "required": ["question"],
                },
            },
            {
                "name": "handoff_to_content_processor",
                "description": "Route a content processing request to the LMS Content Agent. Use for document ingestion, RAG indexing, concept extraction, or course structure generation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["ingest", "search", "analyze", "structure", "reindex"],
                            "description": "What content operation to perform",
                        },
                        "document_url": {"type": "string"},
                        "document_type": {"type": "string"},
                        "course_id": {"type": "string"},
                        "query": {"type": "string", "description": "For search actions"},
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "handoff_to_assessment",
                "description": "Route an assessment request to the LMS Assessment Agent. Use for quiz generation, response evaluation, knowledge gap analysis, or practice exercises.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "learner_id": {"type": "string"},
                        "assessment_type": {
                            "type": "string",
                            "enum": ["diagnostic", "formative", "summative", "practice"],
                            "description": "Type of assessment to generate",
                        },
                        "topic": {"type": "string", "description": "Specific topic to assess"},
                        "request": {"type": "string", "description": "Detailed description of the assessment need"},
                    },
                    "required": ["course_id", "learner_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            # === Direct Operations (existing) ===
            if tool_name == "create_training":
                response = await self.http_client.post("/api/v1/training/modules", json=tool_input)
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create training"}

            elif tool_name == "assign_training":
                response = await self.http_client.post(
                    f"/api/v1/training/modules/{tool_input['training_id']}/assign",
                    json=tool_input,
                )
                return response.json() if response.status_code == 200 else {"error": "Failed to assign training"}

            elif tool_name == "track_progress":
                response = await self.http_client.get("/api/v1/training/progress", params=tool_input)
                return response.json() if response.status_code == 200 else {"progress": None}

            elif tool_name == "create_quiz":
                response = await self.http_client.post(
                    f"/api/v1/training/modules/{tool_input['training_id']}/quiz",
                    json=tool_input,
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create quiz"}

            elif tool_name == "get_certifications":
                response = await self.http_client.get(
                    f"/api/v1/training/users/{tool_input['user_id']}/certifications"
                )
                return response.json() if response.status_code == 200 else {"certifications": []}

            # === New Direct Operations ===
            elif tool_name == "get_learner_profile":
                response = await self.http_client.get(
                    f"/api/v1/lms/learners/{tool_input['user_id']}/profile"
                )
                if response.status_code == 200:
                    return response.json()
                return {"user_id": tool_input["user_id"], "profile": None, "message": "Profile not found"}

            elif tool_name == "create_learning_path":
                response = await self.http_client.post(
                    "/api/v1/lms/learning-paths",
                    json={
                        "learner_id": tool_input["learner_id"],
                        "goal": tool_input["goal"],
                        "current_level": tool_input.get("current_level"),
                        "course_ids": tool_input.get("course_ids", []),
                        "duration_weeks": tool_input.get("duration_weeks"),
                    },
                )
                if response.status_code in (200, 201):
                    data = response.json()
                    data["artifact_type"] = "course"
                    return data
                return {"error": "Failed to create learning path"}

            elif tool_name == "get_learning_analytics":
                response = await self.http_client.get(
                    "/api/v1/lms/analytics",
                    params={
                        "scope": tool_input["scope"],
                        "scope_id": tool_input["scope_id"],
                        "time_range": tool_input.get("time_range", "30d"),
                    },
                )
                if response.status_code == 200:
                    return response.json()
                return {"analytics": None, "message": "Analytics not available"}

            elif tool_name == "search_courses":
                params = {}
                if "query" in tool_input:
                    params["query"] = tool_input["query"]
                if "status" in tool_input:
                    params["status"] = tool_input["status"]
                if "category" in tool_input:
                    params["category"] = tool_input["category"]
                if "skill_level" in tool_input:
                    params["skill_level"] = tool_input["skill_level"]
                response = await self.http_client.get("/api/v1/lms/courses", params=params)
                if response.status_code == 200:
                    return response.json()
                return {"courses": []}

            # === Handoff Operations ===
            elif tool_name == "handoff_to_tutor":
                context = HandoffContext(
                    parent_chat_id=getattr(self, "_current_chat_id", "unknown"),
                    parent_agent_type="training_agent",
                    parent_summary="Training agent routing learner question to tutor",
                    task=tool_input["question"],
                    artifacts=[],
                    constraints=None,
                )
                handoff = HandoffRequest(
                    from_chat_id=context.parent_chat_id,
                    from_agent_type="training_agent",
                    to_agent_type="lms_tutor",
                    context=context,
                    requires_user_approval=False,
                    auto_start=True,
                )
                return {
                    "handoff": "lms_tutor",
                    "request": handoff.model_dump(),
                    "message": f"Routing to LMS Tutor Agent: {tool_input['question']}",
                    "course_id": tool_input.get("course_id"),
                    "learner_id": tool_input.get("learner_id"),
                }

            elif tool_name == "handoff_to_content_processor":
                task_description = f"Content action: {tool_input['action']}"
                if "query" in tool_input:
                    task_description += f" — {tool_input['query']}"
                if "document_url" in tool_input:
                    task_description += f" — {tool_input['document_url']}"

                context = HandoffContext(
                    parent_chat_id=getattr(self, "_current_chat_id", "unknown"),
                    parent_agent_type="training_agent",
                    parent_summary="Training agent routing content processing request",
                    task=task_description,
                    artifacts=[],
                )
                handoff = HandoffRequest(
                    from_chat_id=context.parent_chat_id,
                    from_agent_type="training_agent",
                    to_agent_type="lms_content",
                    context=context,
                    requires_user_approval=False,
                    auto_start=True,
                )
                return {
                    "handoff": "lms_content",
                    "request": handoff.model_dump(),
                    "message": f"Routing to LMS Content Agent: {task_description}",
                    "action": tool_input["action"],
                    "course_id": tool_input.get("course_id"),
                }

            elif tool_name == "handoff_to_assessment":
                task_description = f"Assessment: {tool_input.get('assessment_type', 'formative')}"
                if "topic" in tool_input:
                    task_description += f" on {tool_input['topic']}"
                if "request" in tool_input:
                    task_description += f" — {tool_input['request']}"

                context = HandoffContext(
                    parent_chat_id=getattr(self, "_current_chat_id", "unknown"),
                    parent_agent_type="training_agent",
                    parent_summary="Training agent routing assessment request",
                    task=task_description,
                    artifacts=[],
                )
                handoff = HandoffRequest(
                    from_chat_id=context.parent_chat_id,
                    from_agent_type="training_agent",
                    to_agent_type="lms_assessment",
                    context=context,
                    requires_user_approval=False,
                    auto_start=True,
                )
                return {
                    "handoff": "lms_assessment",
                    "request": handoff.model_dump(),
                    "message": f"Routing to LMS Assessment Agent: {task_description}",
                    "course_id": tool_input.get("course_id"),
                    "learner_id": tool_input.get("learner_id"),
                }

            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
