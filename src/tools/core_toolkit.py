"""
Core Toolkit — Direct Prisma access to spokestack-core's PostgreSQL database.

Unlike ERPToolkit (which uses HTTP calls to LMTD ERP), CoreToolkit connects
directly to spokestack-core's Supabase PostgreSQL via Prisma. All operations
are scoped by organizationId.

Env var: SPOKESTACK_CORE_DATABASE_URL
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Lazy Prisma import — generated client may not exist in all environments
_prisma_client = None


def _get_prisma():
    """Lazy-initialize the Prisma client for spokestack-core."""
    global _prisma_client
    if _prisma_client is None:
        try:
            from prisma import Prisma
            _prisma_client = Prisma()
        except ImportError:
            raise RuntimeError(
                "Prisma client not installed. Run: prisma generate --schema=prisma/core.prisma"
            )
    return _prisma_client


async def _ensure_connected():
    """Ensure Prisma client is connected."""
    client = _get_prisma()
    if not client.is_connected():
        await client.connect()
    return client


class CoreToolkit:
    """
    Toolkit for spokestack-core operations via direct Prisma calls.
    All operations are scoped by organizationId passed in the constructor.
    """

    def __init__(self, org_id: str, user_id: str = "system"):
        self.org_id = org_id
        self.user_id = user_id

    async def close(self) -> None:
        """Disconnect Prisma client."""
        global _prisma_client
        if _prisma_client and _prisma_client.is_connected():
            await _prisma_client.disconnect()
            _prisma_client = None

    # ══════════════════════════════════════════════════════
    # TASKS
    # ══════════════════════════════════════════════════════

    async def create_task(self, data: dict) -> dict:
        """Create a new task."""
        db = await _ensure_connected()
        task = await db.task.create(
            data={
                "organizationId": self.org_id,
                "title": data["title"],
                "description": data.get("description", ""),
                "status": data.get("status", "TODO"),
                "priority": data.get("priority", "MEDIUM"),
                "assigneeId": data.get("assignee_id"),
                "projectId": data.get("project_id"),
                "dueDate": data.get("due_date"),
                "labels": data.get("labels", []),
                "createdById": self.user_id,
            }
        )
        return task.model_dump() if hasattr(task, "model_dump") else dict(task)

    async def update_task(self, task_id: str, data: dict) -> dict:
        """Update an existing task."""
        db = await _ensure_connected()
        update_data = {}
        field_map = {
            "title": "title", "description": "description",
            "status": "status", "priority": "priority",
            "assignee_id": "assigneeId", "due_date": "dueDate",
            "labels": "labels", "project_id": "projectId",
        }
        for key, db_field in field_map.items():
            if key in data:
                update_data[db_field] = data[key]
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

        task = await db.task.update(
            where={"id": task_id, "organizationId": self.org_id},
            data=update_data,
        )
        return task.model_dump() if hasattr(task, "model_dump") else dict(task)

    async def complete_task(self, task_id: str) -> dict:
        """Mark a task as complete."""
        return await self.update_task(task_id, {
            "status": "DONE",
        })

    async def list_tasks(self, filters: dict = None) -> dict:
        """List tasks with optional filters."""
        db = await _ensure_connected()
        where: dict[str, Any] = {"organizationId": self.org_id}
        if filters:
            if filters.get("status"):
                where["status"] = filters["status"]
            if filters.get("assignee_id"):
                where["assigneeId"] = filters["assignee_id"]
            if filters.get("project_id"):
                where["projectId"] = filters["project_id"]
            if filters.get("priority"):
                where["priority"] = filters["priority"]

        tasks = await db.task.find_many(
            where=where,
            order={"createdAt": "desc"},
            take=filters.get("limit", 50) if filters else 50,
        )
        return {
            "data": [t.model_dump() if hasattr(t, "model_dump") else dict(t) for t in tasks],
            "total": len(tasks),
        }

    async def assign_task(self, task_id: str, assignee_id: str) -> dict:
        """Assign a task to a team member."""
        return await self.update_task(task_id, {"assignee_id": assignee_id})

    async def search_tasks(self, query: str, limit: int = 20) -> dict:
        """Search tasks by title or description."""
        db = await _ensure_connected()
        tasks = await db.task.find_many(
            where={
                "organizationId": self.org_id,
                "OR": [
                    {"title": {"contains": query, "mode": "insensitive"}},
                    {"description": {"contains": query, "mode": "insensitive"}},
                ],
            },
            order={"createdAt": "desc"},
            take=limit,
        )
        return {
            "data": [t.model_dump() if hasattr(t, "model_dump") else dict(t) for t in tasks],
            "total": len(tasks),
        }

    # ══════════════════════════════════════════════════════
    # PROJECTS
    # ══════════════════════════════════════════════════════

    async def create_project(self, data: dict) -> dict:
        """Create a new project."""
        db = await _ensure_connected()
        project = await db.project.create(
            data={
                "organizationId": self.org_id,
                "name": data["name"],
                "description": data.get("description", ""),
                "status": data.get("status", "PLANNING"),
                "startDate": data.get("start_date"),
                "endDate": data.get("end_date"),
                "ownerId": data.get("owner_id", self.user_id),
                "createdById": self.user_id,
            }
        )
        return project.model_dump() if hasattr(project, "model_dump") else dict(project)

    async def add_phase(self, project_id: str, data: dict) -> dict:
        """Add a phase to a project."""
        db = await _ensure_connected()
        phase = await db.projectphase.create(
            data={
                "projectId": project_id,
                "name": data["name"],
                "description": data.get("description", ""),
                "order": data.get("order", 0),
                "startDate": data.get("start_date"),
                "endDate": data.get("end_date"),
                "status": data.get("status", "PENDING"),
            }
        )
        return phase.model_dump() if hasattr(phase, "model_dump") else dict(phase)

    async def add_milestone(self, project_id: str, data: dict) -> dict:
        """Add a milestone to a project."""
        db = await _ensure_connected()
        milestone = await db.milestone.create(
            data={
                "projectId": project_id,
                "name": data["name"],
                "description": data.get("description", ""),
                "dueDate": data.get("due_date"),
                "status": data.get("status", "PENDING"),
            }
        )
        return milestone.model_dump() if hasattr(milestone, "model_dump") else dict(milestone)

    async def create_canvas(self, project_id: str, nodes: list[dict]) -> dict:
        """
        Create a WfCanvas with sequential node creation.
        Nodes are created one-at-a-time in order (NOT Promise.all)
        to preserve ordering and allow inter-node references.
        """
        db = await _ensure_connected()
        canvas = await db.wfcanvas.create(
            data={
                "projectId": project_id,
                "name": f"Canvas for project {project_id}",
                "organizationId": self.org_id,
                "createdById": self.user_id,
            }
        )

        created_nodes = []
        for i, node_data in enumerate(nodes):
            node = await db.wfcanvasnode.create(
                data={
                    "canvasId": canvas.id,
                    "type": node_data.get("type", "STEP"),
                    "label": node_data["label"],
                    "description": node_data.get("description", ""),
                    "positionX": node_data.get("position_x", i * 200),
                    "positionY": node_data.get("position_y", 100),
                    "order": i,
                    "config": json.dumps(node_data.get("config", {})),
                }
            )
            created_nodes.append(
                node.model_dump() if hasattr(node, "model_dump") else dict(node)
            )

        result = canvas.model_dump() if hasattr(canvas, "model_dump") else dict(canvas)
        result["nodes"] = created_nodes
        return result

    async def get_project_status(self, project_id: str) -> dict:
        """Get project with phases, milestones, and task counts."""
        db = await _ensure_connected()
        project = await db.project.find_unique(
            where={"id": project_id},
            include={
                "phases": True,
                "milestones": True,
                "tasks": {"select": {"id": True, "status": True}},
            },
        )
        if not project:
            return {"error": f"Project {project_id} not found"}

        result = project.model_dump() if hasattr(project, "model_dump") else dict(project)
        tasks = result.get("tasks", [])
        result["taskSummary"] = {
            "total": len(tasks),
            "done": sum(1 for t in tasks if t.get("status") == "DONE"),
            "in_progress": sum(1 for t in tasks if t.get("status") == "IN_PROGRESS"),
            "todo": sum(1 for t in tasks if t.get("status") == "TODO"),
        }
        return result

    # ══════════════════════════════════════════════════════
    # BRIEFS
    # ══════════════════════════════════════════════════════

    async def create_brief(self, data: dict) -> dict:
        """Create a new brief."""
        db = await _ensure_connected()
        brief = await db.brief.create(
            data={
                "organizationId": self.org_id,
                "title": data["title"],
                "description": data.get("description", ""),
                "type": data.get("type", "GENERAL"),
                "status": data.get("status", "DRAFT"),
                "clientName": data.get("client_name", ""),
                "objectives": data.get("objectives", []),
                "deliverables": data.get("deliverables", []),
                "budget": data.get("budget"),
                "deadline": data.get("deadline"),
                "createdById": self.user_id,
            }
        )
        return brief.model_dump() if hasattr(brief, "model_dump") else dict(brief)

    async def add_brief_phase(self, brief_id: str, data: dict) -> dict:
        """Add a phase to a brief."""
        db = await _ensure_connected()
        phase = await db.briefphase.create(
            data={
                "briefId": brief_id,
                "name": data["name"],
                "description": data.get("description", ""),
                "order": data.get("order", 0),
                "status": data.get("status", "PENDING"),
                "deliverables": data.get("deliverables", []),
            }
        )
        return phase.model_dump() if hasattr(phase, "model_dump") else dict(phase)

    async def generate_artifact(self, brief_id: str, data: dict) -> dict:
        """Generate an artifact draft for a brief (document, copy, etc.)."""
        db = await _ensure_connected()
        artifact = await db.briefartifact.create(
            data={
                "briefId": brief_id,
                "type": data["type"],
                "title": data.get("title", ""),
                "content": data.get("content", ""),
                "status": "DRAFT",
                "version": 1,
                "createdById": self.user_id,
            }
        )
        return artifact.model_dump() if hasattr(artifact, "model_dump") else dict(artifact)

    async def submit_for_review(self, artifact_id: str) -> dict:
        """Submit a brief artifact for review."""
        db = await _ensure_connected()
        artifact = await db.briefartifact.update(
            where={"id": artifact_id},
            data={"status": "IN_REVIEW", "submittedAt": datetime.now(timezone.utc).isoformat()},
        )
        return artifact.model_dump() if hasattr(artifact, "model_dump") else dict(artifact)

    async def record_review(self, artifact_id: str, data: dict) -> dict:
        """Record a review decision on an artifact."""
        db = await _ensure_connected()
        review = await db.briefreview.create(
            data={
                "artifactId": artifact_id,
                "reviewerId": self.user_id,
                "decision": data["decision"],  # APPROVED, REJECTED, REVISION_REQUESTED
                "comments": data.get("comments", ""),
            }
        )
        # Update artifact status based on decision
        new_status = {
            "APPROVED": "APPROVED",
            "REJECTED": "REJECTED",
            "REVISION_REQUESTED": "REVISION_NEEDED",
        }.get(data["decision"], "IN_REVIEW")
        await db.briefartifact.update(
            where={"id": artifact_id},
            data={"status": new_status},
        )
        return review.model_dump() if hasattr(review, "model_dump") else dict(review)

    # ══════════════════════════════════════════════════════
    # ORDERS
    # ══════════════════════════════════════════════════════

    async def create_customer(self, data: dict) -> dict:
        """Create a new customer."""
        db = await _ensure_connected()
        customer = await db.customer.create(
            data={
                "organizationId": self.org_id,
                "name": data["name"],
                "email": data.get("email", ""),
                "phone": data.get("phone", ""),
                "company": data.get("company", ""),
                "address": data.get("address", ""),
                "notes": data.get("notes", ""),
                "createdById": self.user_id,
            }
        )
        return customer.model_dump() if hasattr(customer, "model_dump") else dict(customer)

    async def create_order(self, data: dict) -> dict:
        """Create a new order."""
        db = await _ensure_connected()
        order = await db.order.create(
            data={
                "organizationId": self.org_id,
                "customerId": data["customer_id"],
                "status": data.get("status", "PENDING"),
                "items": data.get("items", []),
                "subtotal": data.get("subtotal", 0),
                "tax": data.get("tax", 0),
                "total": data.get("total", 0),
                "currency": data.get("currency", "USD"),
                "notes": data.get("notes", ""),
                "createdById": self.user_id,
            }
        )
        return order.model_dump() if hasattr(order, "model_dump") else dict(order)

    async def update_order(self, order_id: str, data: dict) -> dict:
        """Update an existing order."""
        db = await _ensure_connected()
        update_data = {}
        for key in ["status", "items", "subtotal", "tax", "total", "notes"]:
            if key in data:
                update_data[key] = data[key]
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

        order = await db.order.update(
            where={"id": order_id, "organizationId": self.org_id},
            data=update_data,
        )
        return order.model_dump() if hasattr(order, "model_dump") else dict(order)

    async def generate_invoice(self, order_id: str) -> dict:
        """Generate an invoice from an order."""
        db = await _ensure_connected()
        order = await db.order.find_unique(
            where={"id": order_id},
            include={"customer": True},
        )
        if not order:
            return {"error": f"Order {order_id} not found"}

        invoice = await db.invoice.create(
            data={
                "organizationId": self.org_id,
                "orderId": order_id,
                "customerId": order.customerId,
                "invoiceNumber": f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid4())[:8]}",
                "status": "DRAFT",
                "items": order.items if isinstance(order.items, list) else [],
                "subtotal": float(order.subtotal) if order.subtotal else 0,
                "tax": float(order.tax) if order.tax else 0,
                "total": float(order.total) if order.total else 0,
                "currency": order.currency or "USD",
                "issuedAt": datetime.now(timezone.utc).isoformat(),
                "createdById": self.user_id,
            }
        )
        return invoice.model_dump() if hasattr(invoice, "model_dump") else dict(invoice)

    async def record_payment(self, invoice_id: str, data: dict) -> dict:
        """Record a payment against an invoice."""
        db = await _ensure_connected()
        payment = await db.payment.create(
            data={
                "invoiceId": invoice_id,
                "amount": data["amount"],
                "method": data.get("method", "BANK_TRANSFER"),
                "reference": data.get("reference", ""),
                "paidAt": data.get("paid_at", datetime.now(timezone.utc).isoformat()),
                "recordedById": self.user_id,
            }
        )
        # Update invoice status
        await db.invoice.update(
            where={"id": invoice_id},
            data={"status": "PAID", "paidAt": datetime.now(timezone.utc).isoformat()},
        )
        return payment.model_dump() if hasattr(payment, "model_dump") else dict(payment)

    # ══════════════════════════════════════════════════════
    # CONTEXT GRAPH
    # ══════════════════════════════════════════════════════

    async def read_context(
        self,
        categories: list[str] = None,
        types: list[str] = None,
        limit: int = 50,
    ) -> dict:
        """
        Read context entries for this organization.
        Supports filtering by category and/or entry type.
        """
        db = await _ensure_connected()
        where: dict[str, Any] = {"organizationId": self.org_id}
        if categories:
            where["category"] = {"in": categories}
        if types:
            where["entryType"] = {"in": types}

        entries = await db.contextentry.find_many(
            where=where,
            order={"updatedAt": "desc"},
            take=limit,
        )
        return {
            "data": [e.model_dump() if hasattr(e, "model_dump") else dict(e) for e in entries],
            "total": len(entries),
        }

    async def write_context(
        self,
        entry_type: str,
        category: str,
        key: str,
        value: Any,
        confidence: float = 1.0,
        source_agent_type: str = None,
    ) -> dict:
        """
        Write or upsert a context entry.
        Uses (organizationId, category, key) as the upsert key.
        """
        db = await _ensure_connected()
        value_str = json.dumps(value) if not isinstance(value, str) else value

        entry = await db.contextentry.upsert(
            where={
                "organizationId_category_key": {
                    "organizationId": self.org_id,
                    "category": category,
                    "key": key,
                }
            },
            data={
                "create": {
                    "organizationId": self.org_id,
                    "entryType": entry_type,
                    "category": category,
                    "key": key,
                    "value": value_str,
                    "confidence": confidence,
                    "sourceAgentType": source_agent_type,
                    "createdById": self.user_id,
                },
                "update": {
                    "value": value_str,
                    "confidence": confidence,
                    "sourceAgentType": source_agent_type,
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                },
            },
        )
        return entry.model_dump() if hasattr(entry, "model_dump") else dict(entry)
