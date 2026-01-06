from typing import Any
import httpx
from .base import BaseAgent


class ApproveAgent(BaseAgent):
    """
    Agent for managing approvals and feedback collection.

    Capabilities:
    - Request approvals via multiple channels
    - Collect and organize feedback
    - Track approval status
    - Route approvals based on workflow
    - Handle escalations
    - Summarize feedback for action
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        language: str = "en",
        client_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.language = language
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "approve_agent"

    @property
    def system_prompt(self) -> str:
        base_prompt = """You are an expert approval workflow coordinator.

Your role is to manage the approval process efficiently:
1. Request approvals from the right stakeholders
2. Present deliverables clearly for review
3. Collect and organize feedback
4. Track approval status and deadlines
5. Escalate when needed
6. Summarize actionable feedback

Approval types you handle:
- Creative approvals (copy, design, video)
- Client approvals (deliverables, budgets)
- Internal approvals (scope changes, resource allocation)
- Legal/compliance approvals
- Financial approvals

Communication best practices:
- Clear subject/context
- Direct link to review material
- Specific questions if needed
- Deadline stated clearly
- Easy approve/reject mechanism
- Follow-up reminders

Feedback organization:
- Categorize by type (must-fix, nice-to-have, question)
- Tag by reviewer
- Link to specific elements
- Prioritize for action"""

        if self.language != "en":
            base_prompt += f"\n\nPrimary language: {self.language}"
        if self.client_specific_id:
            base_prompt += f"\n\nApply client-specific approval workflow for client: {self.client_specific_id}"

        return base_prompt

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "request_approval",
                "description": "Send an approval request to stakeholders.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "approval_type": {
                            "type": "string",
                            "enum": ["creative", "client", "internal", "legal", "financial"],
                            "description": "Type of approval",
                        },
                        "deliverable_id": {
                            "type": "string",
                            "description": "ID of item to approve",
                        },
                        "deliverable_type": {
                            "type": "string",
                            "enum": ["copy", "design", "video", "presentation", "document", "budget", "scope"],
                            "description": "Type of deliverable",
                        },
                        "approvers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Approver user IDs or emails",
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["whatsapp", "email", "slack", "sms", "in_app"],
                            "description": "Notification channel",
                        },
                        "deadline": {
                            "type": "string",
                            "description": "Approval deadline (ISO date)",
                        },
                        "message": {
                            "type": "string",
                            "description": "Custom message to approvers",
                        },
                        "questions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific questions for reviewers",
                        },
                    },
                    "required": ["approval_type", "deliverable_id", "approvers"],
                },
            },
            {
                "name": "collect_feedback",
                "description": "Retrieve and organize feedback from approvers.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "approval_id": {
                            "type": "string",
                            "description": "Approval request ID",
                        },
                        "deliverable_id": {
                            "type": "string",
                            "description": "Deliverable to get feedback for",
                        },
                        "categorize": {
                            "type": "boolean",
                            "description": "Auto-categorize feedback",
                            "default": True,
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_approval_status",
                "description": "Check status of approval requests.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "approval_id": {
                            "type": "string",
                            "description": "Specific approval ID",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Get all approvals for project",
                        },
                        "status_filter": {
                            "type": "string",
                            "enum": ["pending", "approved", "rejected", "expired", "all"],
                            "description": "Filter by status",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "send_reminder",
                "description": "Send approval reminder.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "approval_id": {
                            "type": "string",
                            "description": "Approval to remind about",
                        },
                        "approvers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific approvers to remind (or all if empty)",
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["whatsapp", "email", "slack", "sms"],
                            "description": "Reminder channel",
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["normal", "urgent", "final"],
                            "description": "Reminder urgency level",
                        },
                    },
                    "required": ["approval_id"],
                },
            },
            {
                "name": "escalate_approval",
                "description": "Escalate approval to higher authority.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "approval_id": {
                            "type": "string",
                            "description": "Approval to escalate",
                        },
                        "escalate_to": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "User IDs to escalate to",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Escalation reason",
                        },
                    },
                    "required": ["approval_id", "escalate_to", "reason"],
                },
            },
            {
                "name": "summarize_feedback",
                "description": "Generate actionable summary of all feedback.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "approval_id": {
                            "type": "string",
                            "description": "Approval request ID",
                        },
                        "deliverable_id": {
                            "type": "string",
                            "description": "Deliverable ID",
                        },
                        "group_by": {
                            "type": "string",
                            "enum": ["priority", "reviewer", "element", "type"],
                            "description": "How to group feedback",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "record_decision",
                "description": "Record an approval decision.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "approval_id": {
                            "type": "string",
                            "description": "Approval request ID",
                        },
                        "approver_id": {
                            "type": "string",
                            "description": "Who is deciding",
                        },
                        "decision": {
                            "type": "string",
                            "enum": ["approved", "rejected", "approved_with_changes"],
                            "description": "The decision",
                        },
                        "feedback": {
                            "type": "string",
                            "description": "Feedback/comments",
                        },
                        "conditions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Conditions for approval",
                        },
                    },
                    "required": ["approval_id", "approver_id", "decision"],
                },
            },
            {
                "name": "get_deliverable",
                "description": "Fetch deliverable details for approval.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deliverable_id": {
                            "type": "string",
                            "description": "Deliverable ID",
                        },
                        "deliverable_type": {
                            "type": "string",
                            "description": "Type of deliverable",
                        },
                    },
                    "required": ["deliverable_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "request_approval":
                return await self._request_approval(tool_input)
            elif tool_name == "collect_feedback":
                return await self._collect_feedback(tool_input)
            elif tool_name == "get_approval_status":
                return await self._get_approval_status(tool_input)
            elif tool_name == "send_reminder":
                return await self._send_reminder(tool_input)
            elif tool_name == "escalate_approval":
                return await self._escalate_approval(tool_input)
            elif tool_name == "summarize_feedback":
                return await self._summarize_feedback(tool_input)
            elif tool_name == "record_decision":
                return await self._record_decision(tool_input)
            elif tool_name == "get_deliverable":
                return await self._get_deliverable(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _request_approval(self, params: dict) -> dict:
        """Create and send approval request."""
        response = await self.http_client.post(
            "/api/v1/approvals",
            json={
                "approval_type": params["approval_type"],
                "deliverable_id": params["deliverable_id"],
                "deliverable_type": params.get("deliverable_type"),
                "approvers": params["approvers"],
                "channel": params.get("channel", "email"),
                "deadline": params.get("deadline"),
                "message": params.get("message"),
                "questions": params.get("questions", []),
                "client_id": self.client_specific_id,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to create approval request"}

    async def _collect_feedback(self, params: dict) -> dict:
        """Collect feedback from approvers."""
        approval_id = params.get("approval_id")
        deliverable_id = params.get("deliverable_id")

        if approval_id:
            response = await self.http_client.get(
                f"/api/v1/approvals/{approval_id}/feedback"
            )
        elif deliverable_id:
            response = await self.http_client.get(
                f"/api/v1/deliverables/{deliverable_id}/feedback"
            )
        else:
            return {"error": "Provide approval_id or deliverable_id"}

        if response.status_code == 200:
            feedback = response.json()
            if params.get("categorize", True):
                return {
                    "feedback": feedback,
                    "instruction": "Categorize feedback by priority and type for actionable summary.",
                }
            return feedback
        return {"feedback": [], "note": "No feedback found"}

    async def _get_approval_status(self, params: dict) -> dict:
        """Get approval status."""
        if params.get("approval_id"):
            response = await self.http_client.get(
                f"/api/v1/approvals/{params['approval_id']}"
            )
        elif params.get("project_id"):
            response = await self.http_client.get(
                "/api/v1/approvals",
                params={
                    "project_id": params["project_id"],
                    "status": params.get("status_filter", "all"),
                },
            )
        else:
            response = await self.http_client.get(
                "/api/v1/approvals",
                params={
                    "client_id": self.client_specific_id,
                    "status": params.get("status_filter", "pending"),
                },
            )

        if response.status_code == 200:
            return response.json()
        return {"approvals": [], "note": "No approvals found"}

    async def _send_reminder(self, params: dict) -> dict:
        """Send approval reminder."""
        response = await self.http_client.post(
            f"/api/v1/approvals/{params['approval_id']}/remind",
            json={
                "approvers": params.get("approvers"),
                "channel": params.get("channel", "email"),
                "urgency": params.get("urgency", "normal"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to send reminder"}

    async def _escalate_approval(self, params: dict) -> dict:
        """Escalate approval."""
        response = await self.http_client.post(
            f"/api/v1/approvals/{params['approval_id']}/escalate",
            json={
                "escalate_to": params["escalate_to"],
                "reason": params["reason"],
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to escalate approval"}

    async def _summarize_feedback(self, params: dict) -> dict:
        """Generate feedback summary."""
        # First collect feedback
        feedback_result = await self._collect_feedback(params)

        return {
            "status": "ready_to_summarize",
            "feedback": feedback_result.get("feedback", []),
            "group_by": params.get("group_by", "priority"),
            "instruction": "Generate actionable summary grouped by priority with clear next steps.",
        }

    async def _record_decision(self, params: dict) -> dict:
        """Record approval decision."""
        response = await self.http_client.post(
            f"/api/v1/approvals/{params['approval_id']}/decisions",
            json={
                "approver_id": params["approver_id"],
                "decision": params["decision"],
                "feedback": params.get("feedback"),
                "conditions": params.get("conditions", []),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to record decision"}

    async def _get_deliverable(self, params: dict) -> dict:
        """Get deliverable details."""
        deliverable_type = params.get("deliverable_type", "generic")
        response = await self.http_client.get(
            f"/api/v1/deliverables/{params['deliverable_id']}",
            params={"type": deliverable_type},
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Deliverable not found"}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
