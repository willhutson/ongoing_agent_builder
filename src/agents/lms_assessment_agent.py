"""
LMS Assessment Agent - Adaptive Assessment & Knowledge Reinforcement

Implements:
- Adaptive quiz generation using Bloom's taxonomy levels
- LLM-powered response evaluation with detailed feedback
- Knowledge gap analysis from assessment patterns
- Practice exercise generation targeting weak areas
- Spaced-repetition flashcard creation
- Assessment persistence and result tracking

Maps to DeepTutor's "Knowledge Reinforcement" capability.
"""

from typing import Any
import json
import httpx
from .base import BaseAgent


class LmsAssessmentAgent(BaseAgent):
    """Agent for generating and managing adaptive assessments."""

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
        return "lms_assessment_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an assessment design expert within an enterprise Learning Management System.
You create adaptive quizzes, exercises, and evaluations that accurately measure and reinforce learning.

Your methodology:
1. ANALYZE the learner's current knowledge state and the course learning objectives
2. SELECT appropriate question types and difficulty levels using Bloom's Taxonomy:
   - Remember: recall facts and basic concepts
   - Understand: explain ideas and concepts
   - Apply: use information in new situations
   - Analyze: draw connections among ideas
   - Evaluate: justify a stand or decision
   - Create: produce new or original work
3. GENERATE questions that test understanding, not just recall
4. EVALUATE responses with detailed, constructive feedback referencing course materials
5. ADAPT difficulty dynamically based on learner responses
6. MAP each question to specific learning objectives for gap analysis

Question quality guidelines:
- Avoid trivial recall-only questions — prioritize application and analysis levels
- Write clear, unambiguous question stems
- Ensure distractors (wrong answers) are plausible but distinguishably incorrect
- Always include explanations referencing specific course material for each answer
- Vary question types to test different cognitive skills
- For adaptive assessments, start at the learner's estimated level and adjust"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_quiz",
                "description": "Generate an adaptive quiz based on course content and learner level. Uses LLM to create contextually relevant questions at appropriate difficulty.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "module_id": {"type": "string", "description": "Optional — scope to a module"},
                        "learner_id": {"type": "string", "description": "For adaptive difficulty"},
                        "num_questions": {"type": "integer", "default": 10},
                        "difficulty": {
                            "type": "string",
                            "enum": ["auto", "beginner", "intermediate", "advanced"],
                            "default": "auto",
                            "description": "'auto' adapts to learner level",
                        },
                        "question_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["multiple_choice", "true_false", "short_answer", "code", "matching"],
                            },
                            "description": "Types of questions to include",
                        },
                        "bloom_levels": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["remember", "understand", "apply", "analyze", "evaluate", "create"],
                            },
                            "description": "Target Bloom's taxonomy levels",
                        },
                    },
                    "required": ["course_id", "learner_id"],
                },
            },
            {
                "name": "evaluate_response",
                "description": "Evaluate a learner's response to an assessment question. Provides scoring, detailed feedback, and citations to course materials.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "question_id": {"type": "string"},
                        "question_text": {"type": "string"},
                        "learner_response": {"type": "string"},
                        "correct_answer": {"type": "string"},
                        "rubric": {
                            "type": "object",
                            "description": "Scoring rubric with criteria and point values",
                        },
                        "course_id": {"type": "string", "description": "For citation lookup"},
                    },
                    "required": ["question_id", "question_text", "learner_response", "correct_answer"],
                },
            },
            {
                "name": "get_learner_performance",
                "description": "Retrieve assessment history and performance metrics for a learner across courses or a specific course.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "learner_id": {"type": "string"},
                        "course_id": {"type": "string"},
                        "time_range": {
                            "type": "string",
                            "enum": ["7d", "30d", "90d", "all"],
                            "default": "all",
                        },
                    },
                    "required": ["learner_id"],
                },
            },
            {
                "name": "generate_practice_exercises",
                "description": "Create targeted practice exercises that address specific knowledge gaps identified from assessment results.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "learner_id": {"type": "string"},
                        "topic": {"type": "string"},
                        "gap_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific areas where the learner needs practice",
                        },
                        "exercise_count": {"type": "integer", "default": 5},
                        "course_id": {"type": "string"},
                    },
                    "required": ["learner_id", "topic", "gap_areas"],
                },
            },
            {
                "name": "create_flashcards",
                "description": "Generate spaced-repetition flashcards from course content for effective memorization and review.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "module_id": {"type": "string"},
                        "num_cards": {"type": "integer", "default": 20},
                        "topics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific topics to create flashcards for",
                        },
                    },
                    "required": ["course_id"],
                },
            },
            {
                "name": "analyze_knowledge_gaps",
                "description": "Analyze assessment results to identify knowledge gaps and recommend remediation paths.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "learner_id": {"type": "string"},
                        "course_id": {"type": "string"},
                    },
                    "required": ["learner_id", "course_id"],
                },
            },
            {
                "name": "save_assessment",
                "description": "Persist a generated assessment to the ERP for assignment to learners.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "assessment": {
                            "type": "object",
                            "description": "The full assessment object with questions, answers, and metadata",
                        },
                        "course_id": {"type": "string"},
                        "assessment_type": {
                            "type": "string",
                            "enum": ["diagnostic", "formative", "summative", "practice"],
                        },
                        "title": {"type": "string"},
                    },
                    "required": ["assessment", "course_id", "assessment_type", "title"],
                },
            },
            {
                "name": "submit_assessment_results",
                "description": "Record a learner's completed assessment results for tracking and analytics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "assessment_id": {"type": "string"},
                        "learner_id": {"type": "string"},
                        "responses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question_id": {"type": "string"},
                                    "response": {"type": "string"},
                                    "is_correct": {"type": "boolean"},
                                    "score": {"type": "number"},
                                },
                            },
                        },
                        "time_spent_seconds": {"type": "integer"},
                    },
                    "required": ["assessment_id", "learner_id", "responses"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "generate_quiz":
                payload = {
                    "course_id": tool_input["course_id"],
                    "learner_id": tool_input["learner_id"],
                    "num_questions": tool_input.get("num_questions", 10),
                    "difficulty": tool_input.get("difficulty", "auto"),
                }
                if "module_id" in tool_input:
                    payload["module_id"] = tool_input["module_id"]
                if "question_types" in tool_input:
                    payload["question_types"] = tool_input["question_types"]
                if "bloom_levels" in tool_input:
                    payload["bloom_levels"] = tool_input["bloom_levels"]
                response = await self.http_client.post(
                    "/api/v1/lms/assessments/generate", json=payload
                )
                if response.status_code in (200, 201):
                    data = response.json()
                    data["artifact_type"] = "survey"
                    return data
                return {"error": "Quiz generation failed", "status_code": response.status_code}

            elif tool_name == "evaluate_response":
                payload = {
                    "question_id": tool_input["question_id"],
                    "question_text": tool_input["question_text"],
                    "learner_response": tool_input["learner_response"],
                    "correct_answer": tool_input["correct_answer"],
                }
                if "rubric" in tool_input:
                    payload["rubric"] = tool_input["rubric"]
                if "course_id" in tool_input:
                    payload["course_id"] = tool_input["course_id"]
                response = await self.http_client.post(
                    "/api/v1/lms/assessments/evaluate", json=payload
                )
                if response.status_code == 200:
                    return response.json()
                return {
                    "score": 0,
                    "feedback": "Evaluation unavailable",
                    "is_correct": False,
                }

            elif tool_name == "get_learner_performance":
                params = {"learner_id": tool_input["learner_id"]}
                if "course_id" in tool_input:
                    params["course_id"] = tool_input["course_id"]
                if "time_range" in tool_input:
                    params["time_range"] = tool_input["time_range"]
                response = await self.http_client.get(
                    f"/api/v1/lms/assessments/performance/{tool_input['learner_id']}",
                    params=params,
                )
                if response.status_code == 200:
                    return response.json()
                return {"assessments": [], "overall_score": None}

            elif tool_name == "generate_practice_exercises":
                response = await self.http_client.post(
                    "/api/v1/lms/assessments/practice",
                    json={
                        "learner_id": tool_input["learner_id"],
                        "topic": tool_input["topic"],
                        "gap_areas": tool_input["gap_areas"],
                        "exercise_count": tool_input.get("exercise_count", 5),
                        "course_id": tool_input.get("course_id"),
                    },
                )
                if response.status_code in (200, 201):
                    data = response.json()
                    data["artifact_type"] = "document"
                    return data
                return {"exercises": [], "message": "Exercise generation unavailable"}

            elif tool_name == "create_flashcards":
                payload = {
                    "course_id": tool_input["course_id"],
                    "num_cards": tool_input.get("num_cards", 20),
                }
                if "module_id" in tool_input:
                    payload["module_id"] = tool_input["module_id"]
                if "topics" in tool_input:
                    payload["topics"] = tool_input["topics"]
                response = await self.http_client.post(
                    "/api/v1/lms/assessments/flashcards", json=payload
                )
                if response.status_code in (200, 201):
                    data = response.json()
                    data["artifact_type"] = "table"
                    return data
                return {"cards": [], "artifact_type": "table"}

            elif tool_name == "analyze_knowledge_gaps":
                response = await self.http_client.get(
                    f"/api/v1/lms/assessments/gaps/{tool_input['learner_id']}",
                    params={"course_id": tool_input["course_id"]},
                )
                if response.status_code == 200:
                    return response.json()
                return {"gaps": [], "recommendations": []}

            elif tool_name == "save_assessment":
                response = await self.http_client.post(
                    "/api/v1/lms/assessments",
                    json={
                        "assessment": tool_input["assessment"],
                        "course_id": tool_input["course_id"],
                        "type": tool_input["assessment_type"],
                        "title": tool_input["title"],
                    },
                )
                if response.status_code in (200, 201):
                    return response.json()
                return {"error": "Failed to save assessment"}

            elif tool_name == "submit_assessment_results":
                response = await self.http_client.post(
                    f"/api/v1/lms/assessments/{tool_input['assessment_id']}/results",
                    json={
                        "learner_id": tool_input["learner_id"],
                        "responses": tool_input["responses"],
                        "time_spent_seconds": tool_input.get("time_spent_seconds", 0),
                    },
                )
                if response.status_code in (200, 201):
                    return response.json()
                return {"error": "Failed to submit results"}

            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
