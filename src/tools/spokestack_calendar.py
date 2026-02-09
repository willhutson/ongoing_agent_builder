"""
SpokeStack Calendar Tools (Integration Spec Section 11.4)

Tools for creating content calendar entries in SpokeStack.
Emits Agent Work Protocol SSE events for the Mission Control UI.
"""

from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel
import asyncio
import logging

from ..agents.base import AgentContext
from ..protocols.work import AgentWorkModule, AgentActionType
from .spokestack_base import SpokeStackToolBase

logger = logging.getLogger(__name__)


class CalendarEntry(BaseModel):
    """A single content calendar entry."""
    date: str
    platform: str
    content_type: str
    caption: str
    hashtags: list[str] = []
    visual_concept: Optional[str] = None
    status: str = "IDEA"


class CreateCalendarEntriesParams(BaseModel):
    """Parameters for creating calendar entries."""
    client_id: str
    entries: list[CalendarEntry]


class CreateCalendarEntriesResult(BaseModel):
    """Result from creating calendar entries."""
    success: bool
    created_count: int = 0
    entry_ids: list[str] = []
    errors: list[str] = []


class CalendarTools(SpokeStackToolBase):
    """Tools for the Studio/Calendar module in SpokeStack."""

    MODULE = AgentWorkModule.STUDIO_CALENDAR

    @staticmethod
    def tool_definitions() -> list[dict]:
        """Return Claude tool definitions for calendar operations."""
        return [
            {
                "name": "create_calendar_entries",
                "description": "Create content calendar entries in SpokeStack. Shows each entry being created in the Agent Work pane.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client ID"},
                        "entries": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "date": {"type": "string", "description": "ISO date (YYYY-MM-DD)"},
                                    "platform": {
                                        "type": "string",
                                        "enum": ["instagram", "linkedin", "facebook", "tiktok", "twitter", "youtube"],
                                    },
                                    "content_type": {
                                        "type": "string",
                                        "enum": ["POST", "CAROUSEL", "REEL", "STORY", "ARTICLE", "VIDEO", "THREAD"],
                                    },
                                    "caption": {"type": "string"},
                                    "hashtags": {"type": "array", "items": {"type": "string"}},
                                    "visual_concept": {"type": "string"},
                                    "status": {
                                        "type": "string",
                                        "enum": ["IDEA", "SCHEDULED", "APPROVED"],
                                        "default": "IDEA",
                                    },
                                },
                                "required": ["date", "platform", "content_type", "caption"],
                            },
                        },
                    },
                    "required": ["client_id", "entries"],
                },
            },
            {
                "name": "get_calendar_entries",
                "description": "Get existing content calendar entries for a client.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client ID"},
                        "start_date": {"type": "string", "description": "Start date (ISO)"},
                        "end_date": {"type": "string", "description": "End date (ISO)"},
                        "platform": {"type": "string", "description": "Filter by platform"},
                    },
                    "required": ["client_id"],
                },
            },
        ]

    async def create_calendar_entries(self, params: CreateCalendarEntriesParams,
                                       context: AgentContext) -> CreateCalendarEntriesResult:
        """Create content calendar entries with work events."""
        total = len(params.entries)

        await context.emit_sse({
            "type": "work_start",
            "module": self.MODULE.value,
            "route": "/studio/calendar",
            "pendingFields": [f"entry_{i+1}" for i in range(total)],
        })

        entry_ids = []
        errors = []

        for i, entry in enumerate(params.entries):
            try:
                display = f"{entry.date} - {entry.platform.title()} {entry.content_type}"

                await context.emit_sse({
                    "type": "action",
                    "action": {
                        "id": f"act_{uuid4().hex[:8]}",
                        "type": AgentActionType.CREATE.value,
                        "displayValue": display,
                        "status": "filling",
                        "module": self.MODULE.value,
                        "route": "/studio/calendar",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                })

                org_id = context.organization_id or context.tenant_id
                entry_data = {
                    "clientId": params.client_id,
                    "date": entry.date,
                    "platform": entry.platform,
                    "contentType": entry.content_type,
                    "caption": entry.caption,
                    "hashtags": entry.hashtags,
                    "visualConcept": entry.visual_concept,
                    "status": entry.status,
                }
                entry_data = {k: v for k, v in entry_data.items() if v is not None}

                response = await self.client.post(
                    "/api/v1/studio/calendar/entries",
                    json=entry_data,
                    organization_id=org_id,
                )

                entry_id = response.get("id", str(uuid4()))
                entry_ids.append(entry_id)

                await context.emit_sse({
                    "type": "entity_created",
                    "entity": {
                        "id": entry_id,
                        "type": "calendar_entry",
                        "title": display,
                        "module": self.MODULE.value,
                        "url": f"/studio/calendar/entries/{entry_id}",
                    },
                })

                await asyncio.sleep(0.05)

            except Exception as e:
                logger.error(f"Failed to create calendar entry {i+1}: {e}")
                errors.append(f"Entry {i+1}: {str(e)}")

        await context.emit_sse({
            "type": "work_complete",
            "state": {
                "isWorking": False,
                "createdEntities": [
                    {"id": eid, "type": "calendar_entry", "title": "Calendar entry",
                     "module": self.MODULE.value, "url": f"/studio/calendar/entries/{eid}"}
                    for eid in entry_ids
                ],
            },
        })

        return CreateCalendarEntriesResult(
            success=len(errors) == 0,
            created_count=len(entry_ids),
            entry_ids=entry_ids,
            errors=errors,
        )

    async def get_calendar_entries(self, client_id: str, start_date: str = None,
                                    end_date: str = None, platform: str = None,
                                    context: AgentContext = None) -> dict:
        """Get calendar entries from SpokeStack."""
        try:
            org_id = context.organization_id or context.tenant_id if context else None
            params = {"clientId": client_id}
            if start_date:
                params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date
            if platform:
                params["platform"] = platform
            return await self.client.get("/api/v1/studio/calendar/entries", params=params, organization_id=org_id)
        except Exception as e:
            logger.error(f"Failed to get calendar entries: {e}")
            return {"entries": [], "error": str(e)}
