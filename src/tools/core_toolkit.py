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

from src.services.action_reporter import report_action

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

    async def _report(self, action: str, entity_type: str, result: dict, agent_type: str = "core_tasks") -> None:
        """Report a successful mutation to Mission Control. Non-blocking."""
        # Extract entity_id from flat or nested response shapes
        entity_id = result.get("id") or ""
        if not entity_id:
            for nested_key in ("task", "project", "brief", "order", "client"):
                nested = result.get(nested_key)
                if isinstance(nested, dict) and nested.get("id"):
                    entity_id = nested["id"]
                    break

        # Extract entity_title from flat or nested response shapes
        entity_title = result.get("title") or result.get("name") or ""
        if not entity_title:
            for nested_key, field in [("task", "title"), ("project", "name"), ("brief", "title"), ("order", "name"), ("client", "name")]:
                nested = result.get(nested_key)
                if isinstance(nested, dict) and nested.get(field):
                    entity_title = nested[field]
                    break
        if entity_id and "error" not in result:
            try:
                await report_action(
                    org_id=self.org_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_title=entity_title,
                    agent_type=agent_type,
                )
            except Exception:
                pass  # Never block

    # ══════════════════════════════════════════════════════
    # TASKS
    # ══════════════════════════════════════════════════════

    async def create_task(self, data: dict) -> dict:
        result = await self._request("POST", "/api/v1/tasks", json={
            "title": data["title"],
            "description": data.get("description", ""),
            "status": data.get("status", "TODO"),
            "priority": data.get("priority", "MEDIUM"),
            "assigneeId": data.get("assignee_id"),
            "dueDate": data.get("due_date"),
        })
        await self._report("task.created", "TASK", result, "core_tasks")
        return result

    async def update_task(self, task_id: str, data: dict) -> dict:
        body: dict[str, Any] = {}
        for snake, camel in [("title", "title"), ("description", "description"),
                              ("status", "status"), ("priority", "priority"),
                              ("assignee_id", "assigneeId"), ("due_date", "dueDate")]:
            if snake in data:
                body[camel] = data[snake]
        result = await self._request("PATCH", f"/api/v1/tasks/{task_id}", json=body)
        await self._report("task.updated", "TASK", result, "core_tasks")
        return result

    async def complete_task(self, task_id: str) -> dict:
        result = await self.update_task(task_id, {"status": "DONE"})
        # update_task already reports "task.updated" — override with "task.completed"
        await self._report("task.completed", "TASK", result, "core_tasks")
        return result

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
        result = await self.update_task(task_id, {"assignee_id": assignee_id})
        # update_task already reports "task.updated" — override with "task.assigned"
        await self._report("task.assigned", "TASK", result, "core_tasks")
        return result

    async def search_tasks(self, query: str, limit: int = 20) -> dict:
        return await self._request("GET", "/api/v1/tasks", params={
            "search": query, "limit": str(limit),
        })

    # ══════════════════════════════════════════════════════
    # PROJECTS
    # ══════════════════════════════════════════════════════

    async def create_project(self, data: dict) -> dict:
        result = await self._request("POST", "/api/v1/projects", json={
            "name": data["name"],
            "description": data.get("description", ""),
            "status": data.get("status", "PLANNING"),
            "startDate": data.get("start_date"),
            "endDate": data.get("end_date"),
        })
        await self._report("project.created", "PROJECT", result, "core_projects")
        return result

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
        result = await self._request("POST", "/api/v1/briefs", json={
            "title": data["title"],
            "description": data.get("description", ""),
            "status": data.get("status", "DRAFT"),
            "clientName": data.get("client_name", ""),
        })
        await self._report("brief.created", "BRIEF", result, "core_briefs")
        return result

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

    # ══════════════════════════════════════════════════════
    # CLIENTS (formerly Customers)
    # ══════════════════════════════════════════════════════

    async def create_client(self, data: dict) -> dict:
        result = await self._request("POST", "/api/v1/clients", json={
            "name": data["name"],
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "company": data.get("company", ""),
        })
        await self._report("client.created", "CLIENT", result, "core_crm")
        return result

    # Backwards compat alias
    async def create_customer(self, data: dict) -> dict:
        return await self.create_client(data)

    async def create_order(self, data: dict) -> dict:
        result = await self._request("POST", "/api/v1/orders", json={
            "clientId": data.get("client_id") or data.get("customer_id"),
            "status": data.get("status", "PENDING"),
            "totalCents": data.get("total", 0),
            "currency": data.get("currency", "USD"),
            "notes": data.get("notes", ""),
        })
        await self._report("order.created", "ORDER", result, "core_orders")
        return result

    async def update_order(self, order_id: str, data: dict) -> dict:
        body: dict[str, Any] = {}
        for key in ["status", "totalCents", "currency", "notes"]:
            if key in data:
                body[key] = data[key]
        result = await self._request("PATCH", f"/api/v1/orders/{order_id}", json=body)
        await self._report("order.updated", "ORDER", result, "core_orders")
        return result

    async def generate_invoice(self, order_id: str) -> dict:
        return await self._request("POST", f"/api/v1/orders/{order_id}/invoice")

    async def record_payment(self, invoice_id: str, data: dict) -> dict:
        return await self._request("PATCH", f"/api/v1/invoices/{invoice_id}", json={
            "status": "PAID",
            "paidAt": data.get("paid_at"),
        })

    # ══════════════════════════════════════════════════════
    # EVENTS
    # ══════════════════════════════════════════════════════

    async def list_recent_events(self, entity_type: str = None, action: str = None,
                                  limit: int = 20, since: str = None) -> dict:
        """List recent events for this org."""
        params: dict[str, str] = {"limit": str(limit)}
        if entity_type:
            params["entityType"] = entity_type
        if action:
            params["action"] = action
        if since:
            params["since"] = since
        return await self._request("GET", "/api/v1/events", params=params)

    async def subscribe_to_event(self, entity_type: str, action: str,
                                  agent_id: str = "", conditions: dict = None,
                                  description: str = "") -> dict:
        """Create an event subscription."""
        return await self._request("POST", "/api/v1/events/subscriptions", json={
            "entityType": entity_type,
            "action": action,
            "handler": f"agent:{agent_id}" if agent_id else "agent:system",
            "config": {
                "conditions": conditions,
                "description": description or "Agent-created subscription",
            },
            "enabled": True,
        })

    # ══════════════════════════════════════════════════════
    # DIGITAL ASSET MANAGEMENT
    # ══════════════════════════════════════════════════════

    async def manage_assets(self, action: str, **kwargs) -> dict:
        """Interact with DAM — search, list libraries, get asset, browse folders."""
        if action == "listLibraries":
            return await self._request("GET", "/api/v1/assets/libraries")
        elif action == "searchAssets":
            params: dict[str, str] = {"limit": str(kwargs.get("limit", 20))}
            if kwargs.get("query"):
                params["q"] = kwargs["query"]
            if kwargs.get("asset_type"):
                params["assetType"] = kwargs["asset_type"]
            if kwargs.get("library_id"):
                params["libraryId"] = kwargs["library_id"]
            return await self._request("GET", "/api/v1/assets", params=params)
        elif action == "getAsset":
            return await self._request("GET", f"/api/v1/assets/{kwargs['asset_id']}")
        elif action == "listFolder":
            folder_id = kwargs.get("folder_id")
            if folder_id:
                return await self._request("GET", f"/api/v1/assets/folders/{folder_id}")
            library_id = kwargs.get("library_id")
            if library_id:
                return await self._request("GET", f"/api/v1/assets/libraries/{library_id}")
            return {"error": "Either folder_id or library_id is required for listFolder"}
        else:
            return {"error": f"Unknown asset action: {action}"}

    # ══════════════════════════════════════════════════════
    # INTEGRATIONS
    # ══════════════════════════════════════════════════════

    async def list_integrations(self) -> dict:
        """List all connected integrations for this org."""
        return await self._request("GET", "/api/v1/integrations")

    async def proxy_integration(self, provider: str, endpoint: str,
                                method: str = "GET", body: dict = None) -> dict:
        """Proxy a request to an external service through Nango."""
        payload = {
            "provider": provider,
            "endpoint": endpoint,
            "method": method,
        }
        if body:
            payload["body"] = body
        return await self._request("POST", "/api/v1/integrations/proxy", json=payload)

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
        result = await self._request("POST", "/api/v1/context", json={
            "entryType": entry_type,
            "category": category,
            "key": key,
            "value": value if isinstance(value, (str, dict, list)) else str(value),
            "confidence": confidence,
            "sourceAgentType": source_agent_type,
        })
        await self._report("context.written", "CONTEXT", result, source_agent_type or "core_context")
        return result
