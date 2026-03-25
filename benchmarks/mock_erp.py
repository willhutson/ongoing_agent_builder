"""
Mock ERP Toolkit for benchmarking — returns realistic fixture data
without making real HTTP calls.
"""

from typing import Optional


# Fixture data for each ERP method
FIXTURE_CLIENT = {
    "id": "client-001",
    "name": "Acme Corp",
    "industry": "Technology",
    "logoUrl": "https://example.com/acme-logo.png",
    "contacts": [
        {"name": "Jane Smith", "role": "Marketing Director", "email": "jane@acme.com"},
        {"name": "Bob Chen", "role": "Brand Manager", "email": "bob@acme.com"},
    ],
    "brandPack": {
        "primaryColor": "#2563EB",
        "secondaryColor": "#F59E0B",
        "fonts": ["Inter", "Georgia"],
        "tone": "Professional yet approachable",
        "values": ["Innovation", "Trust", "Simplicity"],
    },
    "recentBriefs": [
        {"id": "brief-101", "title": "Q3 Campaign", "status": "completed"},
        {"id": "brief-102", "title": "Website Redesign", "status": "in_progress"},
    ],
}

FIXTURE_BRIEFS = {
    "data": [
        {
            "id": "brief-101",
            "title": "Q3 Brand Awareness Campaign",
            "clientId": "client-001",
            "status": "completed",
            "objectives": ["Increase brand awareness by 20%", "Drive 50K website visits"],
            "deliverables": ["3 hero videos", "10 social posts", "1 landing page"],
            "budget": 50000,
            "timeline": "2026-07-01 to 2026-09-30",
        },
        {
            "id": "brief-102",
            "title": "Website Redesign",
            "clientId": "client-001",
            "status": "in_progress",
            "objectives": ["Modernize brand presence", "Improve conversion rate"],
            "deliverables": ["Full website redesign", "Content migration"],
            "budget": 80000,
            "timeline": "2026-03-01 to 2026-06-30",
        },
    ],
    "total": 2,
}

FIXTURE_CONTENT_POSTS = {
    "data": [
        {
            "id": "post-001",
            "title": "Product Launch Announcement",
            "platform": "instagram",
            "status": "published",
            "publishedAt": "2026-03-15T10:00:00Z",
            "engagement": {"likes": 1250, "comments": 89, "shares": 45},
        },
        {
            "id": "post-002",
            "title": "Behind the Scenes",
            "platform": "linkedin",
            "status": "draft",
            "scheduledFor": "2026-03-25T14:00:00Z",
        },
    ],
    "total": 2,
}

FIXTURE_PROJECTS = {
    "data": [
        {
            "id": "proj-001",
            "name": "Acme Q3 Campaign",
            "clientId": "client-001",
            "status": "active",
            "startDate": "2026-07-01",
            "endDate": "2026-09-30",
            "team": ["Sarah K.", "Mike L.", "Priya R."],
        },
    ],
    "total": 1,
}

FIXTURE_ANALYTICS = {
    "period": "2026-03-01 to 2026-03-24",
    "impressions": 245000,
    "clicks": 12300,
    "ctr": 5.02,
    "conversions": 890,
    "spend": 15600,
    "roas": 3.2,
}

FIXTURE_PENDING_REVIEWS = {
    "data": [
        {
            "id": "review-001",
            "type": "content",
            "title": "Instagram Carousel Draft",
            "submittedBy": "Copy Team",
            "submittedAt": "2026-03-23T16:00:00Z",
            "priority": "high",
        },
    ],
    "total": 1,
}

FIXTURE_WORKLOAD = {
    "team": [
        {"name": "Sarah K.", "role": "Designer", "utilization": 85, "activeTasks": 4},
        {"name": "Mike L.", "role": "Copywriter", "utilization": 60, "activeTasks": 2},
        {"name": "Priya R.", "role": "Strategist", "utilization": 90, "activeTasks": 5},
    ],
}

FIXTURE_SEARCH = {
    "results": [
        {"module": "briefs", "id": "brief-101", "title": "Q3 Campaign", "relevance": 0.95},
        {"module": "projects", "id": "proj-001", "title": "Acme Q3 Campaign", "relevance": 0.88},
    ],
    "total": 2,
}


class MockERPToolkit:
    """
    Drop-in replacement for ERPToolkit that returns fixture data.
    Matches the ERPToolkit interface without making HTTP calls.
    """

    def __init__(self):
        self._call_log: list[dict] = []

    @property
    def call_log(self) -> list[dict]:
        """All ERP method calls recorded during execution."""
        return self._call_log

    def _log(self, method: str, **kwargs) -> None:
        self._call_log.append({"method": method, **kwargs})

    async def close(self) -> None:
        pass

    async def get_client(self, org_id: str, client_id: str) -> dict:
        self._log("get_client", org_id=org_id, client_id=client_id)
        return FIXTURE_CLIENT

    async def list_briefs(self, org_id: str, client_id: str = None,
                          status: str = None, limit: int = 20) -> dict:
        self._log("list_briefs", org_id=org_id, client_id=client_id, status=status)
        return FIXTURE_BRIEFS

    async def get_brief(self, org_id: str, brief_id: str) -> dict:
        self._log("get_brief", org_id=org_id, brief_id=brief_id)
        return FIXTURE_BRIEFS["data"][0]

    async def list_content_posts(self, org_id: str, client_id: str = None,
                                 date_from: str = None, date_to: str = None) -> dict:
        self._log("list_content_posts", org_id=org_id, client_id=client_id)
        return FIXTURE_CONTENT_POSTS

    async def list_projects(self, org_id: str, client_id: str = None) -> dict:
        self._log("list_projects", org_id=org_id, client_id=client_id)
        return FIXTURE_PROJECTS

    async def get_project(self, org_id: str, project_id: str) -> dict:
        self._log("get_project", org_id=org_id, project_id=project_id)
        return FIXTURE_PROJECTS["data"][0]

    async def get_analytics(self, org_id: str, client_id: str = None,
                            period: str = "7d") -> dict:
        self._log("get_analytics", org_id=org_id, client_id=client_id, period=period)
        return FIXTURE_ANALYTICS

    async def list_scheduled_posts(self, org_id: str, client_id: str = None,
                                   status: str = None) -> dict:
        self._log("list_scheduled_posts", org_id=org_id, client_id=client_id)
        return FIXTURE_CONTENT_POSTS

    async def get_pending_reviews(self, org_id: str, user_id: str) -> dict:
        self._log("get_pending_reviews", org_id=org_id, user_id=user_id)
        return FIXTURE_PENDING_REVIEWS

    async def get_workload(self, org_id: str, team_id: str = None) -> dict:
        self._log("get_workload", org_id=org_id, team_id=team_id)
        return FIXTURE_WORKLOAD

    async def search(self, org_id: str, query: str,
                     modules: str = None, client_id: str = None) -> dict:
        self._log("search", org_id=org_id, query=query)
        return FIXTURE_SEARCH

    # Write methods — signatures match ERPToolkit exactly
    async def create_brief(self, org_id: str, user_id: str, data: dict) -> dict:
        self._log("create_brief", org_id=org_id, user_id=user_id, data=data)
        return {"id": "brief-new-001", "status": "created", **data}

    async def create_content_posts(self, org_id: str, user_id: str, data: dict) -> dict:
        self._log("create_content_posts", org_id=org_id, user_id=user_id, data=data)
        return {"id": "post-new-001", "status": "created", **data}

    async def create_project(self, org_id: str, user_id: str, data: dict) -> dict:
        self._log("create_project", org_id=org_id, user_id=user_id, data=data)
        return {"id": "proj-new-001", "status": "created", **data}

    async def update_post(self, org_id: str, user_id: str,
                          post_id: str, data: dict) -> dict:
        self._log("update_post", org_id=org_id, user_id=user_id, post_id=post_id, data=data)
        return {"id": post_id, "status": "updated", **data}

    async def schedule_post(self, org_id: str, user_id: str, data: dict) -> dict:
        self._log("schedule_post", org_id=org_id, user_id=user_id, data=data)
        return {"id": "sched-new-001", "status": "scheduled", **data}

    async def create_media_plan(self, org_id: str, user_id: str, data: dict) -> dict:
        self._log("create_media_plan", org_id=org_id, user_id=user_id, data=data)
        return {"id": "plan-new-001", "status": "created", **data}

    # Video Studio methods
    async def get_video_project(self, org_id: str, project_id: str) -> dict:
        self._log("get_video_project", org_id=org_id, project_id=project_id)
        return {"id": project_id, "status": "draft", "composition": {}}

    async def create_video_project(self, org_id: str, user_id: str, data: dict) -> dict:
        self._log("create_video_project", org_id=org_id, user_id=user_id, data=data)
        return {"id": "vid-new-001", "status": "created", **data}

    async def update_video_composition(self, org_id: str, user_id: str,
                                       project_id: str, data: dict) -> dict:
        self._log("update_video_composition", org_id=org_id, user_id=user_id, data=data)
        return {"id": project_id, "status": "updated", **data}

    async def trigger_video_render(self, org_id: str, user_id: str,
                                   project_id: str, data: dict = None) -> dict:
        self._log("trigger_video_render", org_id=org_id, project_id=project_id)
        return {"id": project_id, "status": "rendering"}

    async def get_video_templates(self, org_id: str) -> dict:
        self._log("get_video_templates", org_id=org_id)
        return {"templates": []}
