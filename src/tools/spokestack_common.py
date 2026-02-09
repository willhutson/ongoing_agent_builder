"""
SpokeStack Common Tools (Integration Spec Section 11.4)

Universal tools available to all agents: navigate_to, get_form_schema,
fill_form_field, submit_form.
"""

from datetime import datetime, timezone
from uuid import uuid4
import logging

from ..agents.base import AgentContext
from ..protocols.work import AgentWorkModule, AgentActionType
from .spokestack_base import SpokeStackToolBase

logger = logging.getLogger(__name__)


class CommonTools(SpokeStackToolBase):
    """Universal tools available to all agents."""

    @staticmethod
    def tool_definitions() -> list[dict]:
        """Return Claude tool definitions for common operations."""
        return [
            {
                "name": "navigate_to",
                "description": "Navigate to a specific SpokeStack module or route.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string",
                            "enum": [m.value for m in AgentWorkModule],
                        },
                        "route": {"type": "string", "description": "Route path"},
                        "entity_id": {"type": "string", "description": "Entity ID"},
                    },
                    "required": ["module", "route"],
                },
            },
            {
                "name": "get_form_schema",
                "description": "Get the schema of a form including fields, types, and options.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "module": {"type": "string", "enum": [m.value for m in AgentWorkModule]},
                        "form_type": {"type": "string", "enum": ["create", "edit"]},
                        "entity_id": {"type": "string"},
                    },
                    "required": ["module", "form_type"],
                },
            },
            {
                "name": "fill_form_field",
                "description": "Fill a single field in the current form.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string", "description": "Field name"},
                        "value": {"description": "Field value"},
                        "display_value": {"type": "string", "description": "Human-readable display value"},
                    },
                    "required": ["field", "value"],
                },
            },
            {
                "name": "submit_form",
                "description": "Submit the currently open form.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "validate": {"type": "boolean", "default": True},
                    },
                },
            },
        ]

    async def navigate_to(self, module: str, route: str, entity_id: str = None,
                           context: AgentContext = None) -> dict:
        """Navigate to a SpokeStack route."""
        work_module = AgentWorkModule(module)
        await self.emit_navigate(context, work_module, route)
        return {"success": True, "module": module, "route": route}

    async def get_form_schema(self, module: str, form_type: str,
                               entity_id: str = None, context: AgentContext = None) -> dict:
        """Get form schema from SpokeStack."""
        try:
            org_id = context.organization_id or context.tenant_id if context else None
            params = {"formType": form_type}
            if entity_id:
                params["entityId"] = entity_id
            return await self.client.get(f"/api/v1/{module}/form-schema", params=params, organization_id=org_id)
        except Exception as e:
            logger.error(f"Failed to get form schema: {e}")
            return {"fields": [], "error": str(e)}

    async def fill_form_field(self, field: str, value, display_value: str = None,
                               module: AgentWorkModule = None, route: str = None,
                               context: AgentContext = None) -> dict:
        """Fill a form field with SSE event emission."""
        await context.emit_sse({
            "type": "action",
            "action": {
                "id": f"act_{uuid4().hex[:8]}",
                "type": AgentActionType.FILL_FIELD.value,
                "field": field,
                "fieldLabel": field.replace("_", " ").title(),
                "displayValue": display_value or str(value)[:50],
                "status": "filled",
                "module": module.value if module else None,
                "route": route,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        })
        return {"success": True, "field": field, "filled": True}

    async def submit_form(self, validate: bool = True,
                           module: AgentWorkModule = None, route: str = None,
                           context: AgentContext = None) -> dict:
        """Submit the current form."""
        if module:
            await self.emit_submit(context, module, route or "")
        return {"success": True, "submitted": True}
