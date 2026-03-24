"""
ERP Read/Write Toolkit — Real HTTP access to ERP module data.

Replaces mock _execute_tool() calls with actual API requests
to the ERP's service API (Contract B1 endpoints).

Auth: X-API-Key header (service-to-service key, matches
AGENT_BUILDER_SERVICE_KEY on the ERP side).
"""

import httpx
from typing import Optional


class ERPToolkit:
    """HTTP toolkit for reading and writing ERP module data."""

    def __init__(self, erp_base_url: str, service_key: str):
        self.base_url = erp_base_url
        self.client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"X-API-Key": service_key},
            timeout=30.0,
        )

    def _headers(self, org_id: str, user_id: str = "system") -> dict:
        return {
            "X-Organization-Id": org_id,
            "X-User-Id": user_id,
        }

    async def close(self) -> None:
        await self.client.aclose()

    # ══════════════════════════════════════════════
    # READ: Client / Brand Context
    # ══════════════════════════════════════════════

    async def get_client(self, org_id: str, client_id: str) -> dict:
        """Full client profile including brand pack, recent briefs, projects."""
        r = await self.client.get(
            f"/api/v1/service/clients/{client_id}",
            headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # READ: Briefs
    # ══════════════════════════════════════════════

    async def list_briefs(self, org_id: str, client_id: str = None,
                          status: str = None, limit: int = 20) -> dict:
        params: dict = {"limit": limit}
        if client_id:
            params["clientId"] = client_id
        if status:
            params["status"] = status
        r = await self.client.get(
            "/api/v1/service/briefs",
            params=params, headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    async def get_brief(self, org_id: str, brief_id: str) -> dict:
        r = await self.client.get(
            f"/api/v1/service/briefs/{brief_id}",
            headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # READ: Studio / Content
    # ══════════════════════════════════════════════

    async def list_content_posts(self, org_id: str, client_id: str = None,
                                 date_from: str = None, date_to: str = None) -> dict:
        params: dict = {}
        if client_id:
            params["clientId"] = client_id
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        r = await self.client.get(
            "/api/v1/service/studio/posts",
            params=params, headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # READ: Projects
    # ══════════════════════════════════════════════

    async def list_projects(self, org_id: str, client_id: str = None) -> dict:
        params: dict = {}
        if client_id:
            params["clientId"] = client_id
        r = await self.client.get(
            "/api/v1/service/projects",
            params=params, headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    async def get_project(self, org_id: str, project_id: str) -> dict:
        r = await self.client.get(
            f"/api/v1/service/projects/{project_id}",
            headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # READ: Analytics
    # ══════════════════════════════════════════════

    async def get_analytics(self, org_id: str, client_id: str = None,
                            period: str = "7d") -> dict:
        params: dict = {"period": period}
        if client_id:
            params["clientId"] = client_id
        r = await self.client.get(
            "/api/v1/service/analytics",
            params=params, headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # READ: Social / Publisher
    # ══════════════════════════════════════════════

    async def list_scheduled_posts(self, org_id: str, client_id: str = None,
                                   status: str = None) -> dict:
        params: dict = {}
        if client_id:
            params["clientId"] = client_id
        if status:
            params["status"] = status
        r = await self.client.get(
            "/api/v1/service/social/scheduled",
            params=params, headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # READ: Cross-cutting
    # ══════════════════════════════════════════════

    async def get_pending_reviews(self, org_id: str, user_id: str) -> dict:
        """What's awaiting review for this user across all modules."""
        r = await self.client.get(
            "/api/v1/service/reviews/pending",
            params={"userId": user_id},
            headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    async def get_workload(self, org_id: str, team_id: str = None) -> dict:
        params: dict = {}
        if team_id:
            params["teamId"] = team_id
        r = await self.client.get(
            "/api/v1/service/resources/workload",
            params=params, headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    async def search(self, org_id: str, query: str,
                     modules: str = None, client_id: str = None) -> dict:
        params: dict = {"q": query}
        if modules:
            params["modules"] = modules
        if client_id:
            params["clientId"] = client_id
        r = await self.client.get(
            "/api/v1/service/search",
            params=params, headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # WRITE: Briefs
    # ══════════════════════════════════════════════

    async def create_brief(self, org_id: str, user_id: str, data: dict) -> dict:
        r = await self.client.post(
            "/api/v1/service/briefs",
            json=data,
            headers=self._headers(org_id, user_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # WRITE: Content Posts (batch)
    # ══════════════════════════════════════════════

    async def create_content_posts(self, org_id: str, user_id: str, data: dict) -> dict:
        r = await self.client.post(
            "/api/v1/service/studio/posts/batch",
            json=data,
            headers=self._headers(org_id, user_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # WRITE: Projects
    # ══════════════════════════════════════════════

    async def create_project(self, org_id: str, user_id: str, data: dict) -> dict:
        r = await self.client.post(
            "/api/v1/service/projects",
            json=data,
            headers=self._headers(org_id, user_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # WRITE: Scheduled Posts
    # ══════════════════════════════════════════════

    async def schedule_post(self, org_id: str, user_id: str, data: dict) -> dict:
        r = await self.client.post(
            "/api/v1/service/social/scheduled",
            json=data,
            headers=self._headers(org_id, user_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # WRITE: Media Plans
    # ══════════════════════════════════════════════

    async def create_media_plan(self, org_id: str, user_id: str, data: dict) -> dict:
        r = await self.client.post(
            "/api/v1/service/media-buying/plans",
            json=data,
            headers=self._headers(org_id, user_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # WRITE: Update Post
    # ══════════════════════════════════════════════

    async def update_post(self, org_id: str, user_id: str,
                          post_id: str, data: dict) -> dict:
        r = await self.client.patch(
            f"/api/v1/service/studio/posts/{post_id}",
            json=data,
            headers=self._headers(org_id, user_id),
        )
        r.raise_for_status()
        return r.json()

    # ══════════════════════════════════════════════
    # Video Studio
    # ══════════════════════════════════════════════

    async def get_video_project(self, org_id: str, project_id: str) -> dict:
        """Get a video project with full composition data."""
        r = await self.client.get(
            f"/api/v1/video-studio/{project_id}",
            headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()

    async def create_video_project(self, org_id: str, user_id: str, data: dict) -> dict:
        """Create a new video project, optionally from a template."""
        r = await self.client.post(
            "/api/v1/video-studio",
            json=data,
            headers=self._headers(org_id, user_id),
        )
        r.raise_for_status()
        return r.json()

    async def update_video_composition(self, org_id: str, user_id: str,
                                       project_id: str, data: dict) -> dict:
        """Update composition data for a video project."""
        r = await self.client.patch(
            f"/api/v1/video-studio/{project_id}",
            json=data,
            headers=self._headers(org_id, user_id),
        )
        r.raise_for_status()
        return r.json()

    async def trigger_video_render(self, org_id: str, user_id: str,
                                   project_id: str, resolution: str = "1080p") -> dict:
        """Trigger server-side render of a video project."""
        r = await self.client.post(
            f"/api/v1/video-studio/{project_id}/render",
            json={"resolution": resolution},
            headers=self._headers(org_id, user_id),
        )
        r.raise_for_status()
        return r.json()

    async def get_video_templates(self, org_id: str) -> dict:
        """List available video templates."""
        r = await self.client.get(
            "/api/v1/video-studio/templates",
            headers=self._headers(org_id),
        )
        r.raise_for_status()
        return r.json()
