"""
Core Toolkit — HTTP bridge to spokestack-core's REST API.

All operations call spokestack-core's endpoints over HTTP using
X-Agent-Secret + X-Org-Id headers for service-to-service auth.

Env vars:
  SPOKESTACK_CORE_URL (default: https://spokestack-core.vercel.app)
  AGENT_RUNTIME_SECRET
"""

import json
import logging
import os
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

CORE_API_URL = os.environ.get("SPOKESTACK_CORE_URL", "https://spokestack-core.vercel.app")
AGENT_SECRET = os.environ.get("AGENT_RUNTIME_SECRET", "")


class CoreToolkit:
    """
    Toolkit for spokestack-core operations via REST API.
    All operations are scoped by organizationId.
    """

    def __init__(self, org_id: str, user_id: str = "system"):
        self.org_id = org_id
        self.user_id = user_id
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=CORE_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "X-Agent-Secret": AGENT_SECRET,
                    "X-Org-Id": self.org_id,
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an HTTP request to spokestack-core."""
        client = self._get_client()
        try:
            response = await client.request(method, path, **kwargs)
            if response.status_code >= 400:
                text = response.text[:200]
                logger.error(f"CoreToolkit {method} {path}: {response.status_code} {text}")
                return {"error": f"API error ({response.status_code}): {text}"}
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"CoreToolkit {method} {path} network error: {e}")
            return {"error": f"Network error: {str(e)}"}

    # ══════════════════════════════════════════════════════
    # TASKS
    # ══════════════════════════════════════════════════════

    async def create_task(self, data: dict) -> dict:
        return await self._request("POST", "/api/v1/tasks", json={
            "title": data["title"],
            "description": data.get("description", ""),
            "status": data.get("status", "TODO"),
            "priority": data.get("priority", "MEDIUM"),
            "assigneeId": data.get("assignee_id"),
            "dueDate": data.get("due_date"),
        })

    async def update_task(self, task_id: str, data: dict) -> dict:
        body: dict[str, Any] = {}
        for snake, camel in [("title", "title"), ("description", "description"),
                              ("status", "status"), ("priority", "priority"),
                              ("assignee_id", "assigneeId"), ("due_date", "dueDate")]:
            if snake in data:
                body[camel] = data[snake]
        return await self._request("PATCH", f"/api/v1/tasks/{task_id}", json=body)

    async def complete_task(self, task_id: str) -> dict:
        return await self.update_task(task_id, {"status": "DONE"})

    async def list_tasks(self, filters: dict = None) -> dict:
        params: dict[str, str] = {}
        if filters:
            if filters.get("status"):
                params["status"] = filters["status"]
            if filters.get("assignee_id"):
                params["assigneeId"] = filters["assignee_id"]
            if filters.get("priority"):
                params["priority"] = filters["priority"]
            if filters.get("limit"):
                params["limit"] = str(filters["limit"])
        return await self._request("GET", "/api/v1/tasks", params=params)

    async def assign_task(self, task_id: str, assignee_id: str) -> dict:
        return await self.update_task(task_id, {"assignee_id": assignee_id})

    async def search_tasks(self, query: str, limit: int = 20) -> dict:
        return await self._request("GET", "/api/v1/tasks", params={
            "search": query, "limit": str(limit),
        })

    # ══════════════════════════════════════════════════════
    # PROJECTS
    # ══════════════════════════════════════════════════════

    async def create_project(self, data: dict) -> dict:
        return await self._request("POST", "/api/v1/projects", json={
            "name": data["name"],
            "description": data.get("description", ""),
            "status": data.get("status", "PLANNING"),
            "startDate": data.get("start_date"),
            "endDate": data.get("end_date"),
        })

    async def add_phase(self, project_id: str, data: dict) -> dict:
        return await self._request("POST", f"/api/v1/projects/{project_id}/phases", json={
            "name": data["name"],
            "position": data.get("order", data.get("position", 0)),
            "status": data.get("status", "PENDING"),
        })

    async def add_milestone(self, project_id: str, data: dict) -> dict:
        return await self._request("POST", f"/api/v1/projects/{project_id}/milestones", json={
            "name": data["name"],
            "dueDate": data.get("due_date"),
            "description": data.get("description", ""),
        })

    async def create_canvas(self, project_id: str, nodes: list[dict]) -> dict:
        return await self._request("POST", f"/api/v1/projects/{project_id}/canvas", json={
            "nodes": nodes,
        })

    async def get_project_status(self, project_id: str) -> dict:
        return await self._request("GET", f"/api/v1/projects/{project_id}")

    # ══════════════════════════════════════════════════════
    # BRIEFS
    # ══════════════════════════════════════════════════════

    async def create_brief(self, data: dict) -> dict:
        return await self._request("POST", "/api/v1/briefs", json={
            "title": data["title"],
            "description": data.get("description", ""),
            "status": data.get("status", "DRAFT"),
            "clientName": data.get("client_name", ""),
        })

    async def add_brief_phase(self, brief_id: str, data: dict) -> dict:
        return await self._request("POST", f"/api/v1/briefs/{brief_id}/phases", json={
            "name": data["name"],
            "position": data.get("order", data.get("position", 0)),
            "status": data.get("status", "PENDING"),
        })

    async def generate_artifact(self, brief_id: str, data: dict) -> dict:
        return await self._request("POST", f"/api/v1/briefs/{brief_id}/artifacts", json={
            "type": data["type"],
            "title": data.get("title", ""),
            "content": data.get("content", ""),
        })

    async def submit_for_review(self, artifact_id: str) -> dict:
        logger.warning(f"submit_for_review({artifact_id}): no dedicated endpoint, returning stub")
        return {"id": artifact_id, "status": "IN_REVIEW", "note": "Stub — no review endpoint yet"}

    async def record_review(self, artifact_id: str, data: dict) -> dict:
        logger.warning(f"record_review({artifact_id}): no dedicated endpoint, returning stub")
        return {"id": artifact_id, "decision": data.get("decision", "PENDING"), "note": "Stub — no review endpoint yet"}

    # ══════════════════════════════════════════════════════
    # ORDERS
    # ══════════════════════════════════════════════════════

    async def create_customer(self, data: dict) -> dict:
        return await self._request("POST", "/api/v1/customers", json={
            "name": data["name"],
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "company": data.get("company", ""),
        })

    async def create_order(self, data: dict) -> dict:
        return await self._request("POST", "/api/v1/orders", json={
            "customerId": data.get("customer_id"),
            "status": data.get("status", "PENDING"),
            "totalCents": data.get("total", 0),
            "currency": data.get("currency", "USD"),
            "notes": data.get("notes", ""),
        })

    async def update_order(self, order_id: str, data: dict) -> dict:
        body: dict[str, Any] = {}
        for key in ["status", "totalCents", "currency", "notes"]:
            if key in data:
                body[key] = data[key]
        return await self._request("PATCH", f"/api/v1/orders/{order_id}", json=body)

    async def generate_invoice(self, order_id: str) -> dict:
        return await self._request("POST", f"/api/v1/orders/{order_id}/invoice")

    async def record_payment(self, invoice_id: str, data: dict) -> dict:
        return await self._request("PATCH", f"/api/v1/invoices/{invoice_id}", json={
            "status": "PAID",
            "paidAt": data.get("paid_at"),
        })

    # ══════════════════════════════════════════════════════
    # CONTEXT GRAPH
    # ══════════════════════════════════════════════════════

    async def read_context(
        self,
        categories: list[str] = None,
        types: list[str] = None,
        limit: int = 50,
    ) -> dict:
        params: dict[str, str] = {"limit": str(limit)}
        if categories:
            params["category"] = ",".join(categories)
        if types:
            params["entryType"] = ",".join(types)
        return await self._request("GET", "/api/v1/context", params=params)

    async def write_context(
        self,
        entry_type: str,
        category: str,
        key: str,
        value: Any,
        confidence: float = 1.0,
        source_agent_type: str = None,
    ) -> dict:
        return await self._request("POST", "/api/v1/context", json={
            "entryType": entry_type,
            "category": category,
            "key": key,
            "value": value if isinstance(value, (str, dict, list)) else str(value),
            "confidence": confidence,
            "sourceAgentType": source_agent_type,
        })
