from typing import Any
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill


class PRAgent(BaseAgent):
    """Agent for public relations and media relations with coverage capture."""

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str, client_id: str = None, instance_id: str = None):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.instance_id = instance_id
        self.http_client = httpx.AsyncClient(base_url=erp_base_url, headers={"Authorization": f"Bearer {erp_api_key}"}, timeout=60.0)
        session_name = f"pr_{instance_id}" if instance_id else "pr"
        self.browser = AgentBrowserSkill(session_name=session_name)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "pr_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a PR and media relations expert. Manage press releases, media outreach, and coverage.

You have browser automation to capture press coverage, media mentions, and news articles as proof."""

    def _define_tools(self) -> list[dict]:
        return [
            {"name": "create_press_release", "description": "Create press release.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "embargo_date": {"type": "string"}}, "required": ["title", "content"]}},
            {"name": "get_media_list", "description": "Get media contacts list.", "input_schema": {"type": "object", "properties": {"beat": {"type": "string"}, "region": {"type": "string"}}, "required": []}},
            {"name": "distribute_release", "description": "Distribute press release.", "input_schema": {"type": "object", "properties": {"release_id": {"type": "string"}, "media_list_id": {"type": "string"}}, "required": ["release_id"]}},
            {"name": "track_coverage", "description": "Track media coverage.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "date_range": {"type": "object"}}, "required": []}},
            {"name": "calculate_avr", "description": "Calculate ad value equivalent.", "input_schema": {"type": "object", "properties": {"coverage_ids": {"type": "array", "items": {"type": "string"}}}, "required": ["coverage_ids"]}},
            {"name": "create_media_kit", "description": "Create media kit.", "input_schema": {"type": "object", "properties": {"client_id": {"type": "string"}, "include": {"type": "array", "items": {"type": "string"}}}, "required": []}},
            {"name": "capture_press_coverage", "description": "Screenshot press article.", "input_schema": {"type": "object", "properties": {"article_url": {"type": "string"}, "publication": {"type": "string"}}, "required": ["article_url"]}},
            {"name": "capture_media_mention", "description": "Screenshot media mention.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "mention_type": {"type": "string"}}, "required": ["url"]}},
            {"name": "save_article_pdf", "description": "Save article as PDF.", "input_schema": {"type": "object", "properties": {"article_url": {"type": "string"}, "article_name": {"type": "string"}}, "required": ["article_url", "article_name"]}},
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id
            if tool_name == "create_press_release":
                response = await self.http_client.post("/api/v1/pr/releases", json={**tool_input, "client_id": client_id})
                return response.json() if response.status_code in (200, 201) else {"error": "Failed"}
            elif tool_name == "get_media_list":
                response = await self.http_client.get("/api/v1/pr/media-lists", params=tool_input)
                return response.json() if response.status_code == 200 else {"contacts": []}
            elif tool_name == "distribute_release":
                response = await self.http_client.post(f"/api/v1/pr/releases/{tool_input['release_id']}/distribute", json=tool_input)
                return response.json() if response.status_code == 200 else {"error": "Failed"}
            elif tool_name == "track_coverage":
                response = await self.http_client.get("/api/v1/pr/coverage", params={**tool_input, "client_id": client_id})
                return response.json() if response.status_code == 200 else {"coverage": []}
            elif tool_name == "calculate_avr":
                response = await self.http_client.post("/api/v1/pr/coverage/avr", json=tool_input)
                return response.json() if response.status_code == 200 else {"avr": None}
            elif tool_name == "create_media_kit":
                return {"status": "ready_to_create", "instruction": "Create comprehensive media kit."}
            elif tool_name == "capture_press_coverage":
                return await self._capture_coverage(tool_input["article_url"], tool_input.get("publication", "article"))
            elif tool_name == "capture_media_mention":
                return await self._capture_mention(tool_input["url"], tool_input.get("mention_type", "mention"))
            elif tool_name == "save_article_pdf":
                return await self._save_pdf(tool_input["article_url"], tool_input["article_name"])
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_coverage(self, url: str, publication: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            snapshot = await self.browser.snapshot(interactive_only=False)
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/pr_proofs", prefix=f"coverage_{publication}")
            return {"url": url, "publication": publication, "snapshot": snapshot.raw, "screenshot": screenshot_path, "timestamp": snapshot.timestamp.isoformat()}
        except Exception as e:
            return {"error": str(e)}

    async def _capture_mention(self, url: str, mention_type: str) -> dict:
        try:
            screenshot_path = await self.browser.capture_proof(url=url, output_dir="/tmp/pr_proofs", prefix=f"mention_{mention_type}")
            return {"url": url, "mention_type": mention_type, "screenshot": screenshot_path, "success": True}
        except Exception as e:
            return {"error": str(e)}

    async def _save_pdf(self, url: str, name: str) -> dict:
        try:
            await self.browser.open(url)
            await self.browser.wait(2000)
            pdf_path = f"/tmp/pr_proofs/{name}.pdf"
            await self.browser.pdf(pdf_path)
            return {"url": url, "pdf_path": pdf_path, "success": True}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.http_client.aclose()
        await self.browser.close()
