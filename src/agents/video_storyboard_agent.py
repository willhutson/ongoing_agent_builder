from typing import Any
import httpx
from .base import BaseAgent


class VideoStoryboardAgent(BaseAgent):
    """
    Agent for generating video storyboards.

    Capabilities:
    - Generate storyboards from scripts
    - Create frame-by-frame visual plans
    - Specify camera angles and movements
    - Add technical annotations
    - Apply moodboard styling
    - Generate shot lists
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        client_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "video_storyboard_agent"

    @property
    def system_prompt(self) -> str:
        base_prompt = """You are an expert storyboard artist and visual planner for video production.

Your role is to translate scripts into detailed visual plans:
1. Create frame-by-frame visual descriptions
2. Specify camera angles, movements, and transitions
3. Note lighting and color palette requirements
4. Describe talent blocking and action
5. Include technical specifications for production

Storyboard elements you define:
- Frame/shot number and duration
- Visual description (composition, subjects, background)
- Camera angle (wide, medium, close-up, extreme close-up)
- Camera movement (static, pan, tilt, dolly, crane, handheld)
- Transitions (cut, dissolve, fade, wipe)
- Audio notes (dialogue, VO, SFX, music)
- On-screen text placement
- Lighting notes
- Color/mood reference

Shot types you work with:
- Establishing shots
- Master shots
- Insert shots
- Cutaways
- Reaction shots
- POV shots
- Over-the-shoulder
- Two-shots
- Product shots"""

        if self.client_specific_id:
            base_prompt += f"\n\nApply client-specific visual guidelines for client: {self.client_specific_id}"

        return base_prompt

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_storyboard",
                "description": "Generate a complete storyboard from a script.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script_id": {
                            "type": "string",
                            "description": "Script ID to storyboard",
                        },
                        "style": {
                            "type": "string",
                            "enum": ["detailed", "rough", "animatic"],
                            "description": "Level of detail",
                            "default": "detailed",
                        },
                        "moodboard_id": {
                            "type": "string",
                            "description": "Moodboard for visual style",
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "enum": ["16:9", "9:16", "1:1", "4:5"],
                            "description": "Frame aspect ratio",
                        },
                    },
                    "required": ["script_id"],
                },
            },
            {
                "name": "generate_frame",
                "description": "Generate a single storyboard frame.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "storyboard_id": {
                            "type": "string",
                            "description": "Storyboard to add frame to",
                        },
                        "scene_description": {
                            "type": "string",
                            "description": "What happens in this frame",
                        },
                        "position": {
                            "type": "integer",
                            "description": "Frame position in sequence",
                        },
                        "reference_image_id": {
                            "type": "string",
                            "description": "DAM image for reference",
                        },
                    },
                    "required": ["scene_description"],
                },
            },
            {
                "name": "generate_shot_list",
                "description": "Generate a production shot list from storyboard.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "storyboard_id": {
                            "type": "string",
                            "description": "Storyboard to create shot list from",
                        },
                        "group_by": {
                            "type": "string",
                            "enum": ["scene", "location", "talent", "equipment"],
                            "description": "How to organize shots",
                        },
                        "include_equipment": {
                            "type": "boolean",
                            "description": "Include equipment requirements",
                            "default": True,
                        },
                    },
                    "required": ["storyboard_id"],
                },
            },
            {
                "name": "get_script",
                "description": "Retrieve a script to storyboard.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script_id": {
                            "type": "string",
                            "description": "Script ID to fetch",
                        },
                    },
                    "required": ["script_id"],
                },
            },
            {
                "name": "get_moodboard",
                "description": "Fetch a moodboard for visual reference.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "moodboard_id": {
                            "type": "string",
                            "description": "Moodboard ID to fetch",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Get moodboard for a project",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_moodboard",
                "description": "Extract visual style from moodboard for storyboard.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "moodboard_id": {
                            "type": "string",
                            "description": "Moodboard to analyze",
                        },
                        "extract": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to extract: colors, lighting, composition, camera_style",
                        },
                    },
                    "required": ["moodboard_id"],
                },
            },
            {
                "name": "add_annotations",
                "description": "Add technical annotations to storyboard frames.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "frame_id": {
                            "type": "string",
                            "description": "Frame to annotate",
                        },
                        "annotations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "content": {"type": "string"},
                                    "position": {"type": "object"},
                                },
                            },
                            "description": "Annotations to add",
                        },
                    },
                    "required": ["frame_id", "annotations"],
                },
            },
            {
                "name": "get_reference_images",
                "description": "Search DAM for reference images.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags to filter by",
                        },
                        "client_id": {
                            "type": "string",
                            "description": "Filter by client",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "save_storyboard",
                "description": "Save storyboard to project/DAM.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "storyboard_id": {
                            "type": "string",
                            "description": "Storyboard ID if updating",
                        },
                        "title": {"type": "string"},
                        "frames": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Frame data array",
                        },
                        "script_id": {"type": "string"},
                        "project_id": {"type": "string"},
                        "client_id": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["draft", "review", "approved", "production"],
                            "default": "draft",
                        },
                    },
                    "required": ["title", "frames"],
                },
            },
            {
                "name": "export_storyboard",
                "description": "Export storyboard to various formats.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "storyboard_id": {"type": "string"},
                        "format": {
                            "type": "string",
                            "enum": ["pdf", "pptx", "images", "animatic"],
                        },
                        "options": {
                            "type": "object",
                            "properties": {
                                "include_notes": {"type": "boolean"},
                                "include_shot_list": {"type": "boolean"},
                                "frames_per_page": {"type": "integer"},
                            },
                        },
                    },
                    "required": ["storyboard_id", "format"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "generate_storyboard":
                return await self._generate_storyboard(tool_input)
            elif tool_name == "generate_frame":
                return await self._generate_frame(tool_input)
            elif tool_name == "generate_shot_list":
                return await self._generate_shot_list(tool_input)
            elif tool_name == "get_script":
                return await self._get_script(tool_input)
            elif tool_name == "get_moodboard":
                return await self._get_moodboard(tool_input)
            elif tool_name == "analyze_moodboard":
                return await self._analyze_moodboard(tool_input)
            elif tool_name == "add_annotations":
                return await self._add_annotations(tool_input)
            elif tool_name == "get_reference_images":
                return await self._get_reference_images(tool_input)
            elif tool_name == "save_storyboard":
                return await self._save_storyboard(tool_input)
            elif tool_name == "export_storyboard":
                return await self._export_storyboard(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _generate_storyboard(self, params: dict) -> dict:
        """Generate a storyboard from script."""
        response = await self.http_client.get(
            f"/api/v1/studio/scripts/{params['script_id']}"
        )
        script = response.json() if response.status_code == 200 else None

        moodboard = None
        if params.get("moodboard_id"):
            response = await self.http_client.get(
                f"/api/v1/studio/moodboards/{params['moodboard_id']}"
            )
            if response.status_code == 200:
                moodboard = response.json()

        return {
            "status": "ready_to_generate",
            "script": script,
            "style": params.get("style", "detailed"),
            "moodboard": moodboard,
            "aspect_ratio": params.get("aspect_ratio", "16:9"),
            "instruction": "Generate a complete storyboard with frame-by-frame visual descriptions.",
        }

    async def _generate_frame(self, params: dict) -> dict:
        """Generate a single frame."""
        reference = None
        if params.get("reference_image_id"):
            response = await self.http_client.get(
                f"/api/v1/dam/assets/{params['reference_image_id']}"
            )
            if response.status_code == 200:
                reference = response.json()

        return {
            "status": "ready_to_generate",
            "scene_description": params["scene_description"],
            "position": params.get("position"),
            "reference": reference,
            "instruction": "Generate a detailed storyboard frame with camera and technical notes.",
        }

    async def _generate_shot_list(self, params: dict) -> dict:
        """Generate shot list from storyboard."""
        response = await self.http_client.get(
            f"/api/v1/studio/storyboards/{params['storyboard_id']}"
        )
        storyboard = response.json() if response.status_code == 200 else None

        return {
            "status": "ready_to_generate",
            "storyboard": storyboard,
            "group_by": params.get("group_by", "scene"),
            "include_equipment": params.get("include_equipment", True),
            "instruction": "Generate a production shot list organized for efficient shooting.",
        }

    async def _get_script(self, params: dict) -> dict:
        """Get script."""
        response = await self.http_client.get(
            f"/api/v1/studio/scripts/{params['script_id']}"
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Script not found"}

    async def _get_moodboard(self, params: dict) -> dict:
        """Fetch moodboard."""
        moodboard_id = params.get("moodboard_id")
        project_id = params.get("project_id")

        if moodboard_id:
            response = await self.http_client.get(
                f"/api/v1/studio/moodboards/{moodboard_id}"
            )
        elif project_id:
            response = await self.http_client.get(
                "/api/v1/studio/moodboards",
                params={"project_id": project_id},
            )
        else:
            return {"error": "Provide moodboard_id or project_id"}

        if response.status_code == 200:
            return response.json()
        return {"moodboard": None, "note": "Moodboard not found"}

    async def _analyze_moodboard(self, params: dict) -> dict:
        """Analyze moodboard for visual style."""
        response = await self.http_client.get(
            f"/api/v1/studio/moodboards/{params['moodboard_id']}/analyze",
            params={"extract": ",".join(params.get("extract", ["colors", "composition"]))},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "moodboard_id": params["moodboard_id"],
            "instruction": "Analyze moodboard for visual style, camera style, and composition.",
        }

    async def _add_annotations(self, params: dict) -> dict:
        """Add annotations to frame."""
        response = await self.http_client.patch(
            f"/api/v1/studio/storyboards/frames/{params['frame_id']}/annotations",
            json={"annotations": params["annotations"]},
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to add annotations"}

    async def _get_reference_images(self, params: dict) -> dict:
        """Search DAM for references."""
        response = await self.http_client.get(
            "/api/v1/dam/search",
            params={
                "q": params["query"],
                "tags": ",".join(params.get("tags", [])),
                "client_id": params.get("client_id") or self.client_specific_id,
                "type": "image",
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"results": [], "note": "No matches found"}

    async def _save_storyboard(self, params: dict) -> dict:
        """Save storyboard."""
        response = await self.http_client.post(
            "/api/v1/studio/storyboards",
            json={
                "title": params["title"],
                "frames": params["frames"],
                "script_id": params.get("script_id"),
                "project_id": params.get("project_id"),
                "client_id": params.get("client_id") or self.client_specific_id,
                "status": params.get("status", "draft"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to save storyboard"}

    async def _export_storyboard(self, params: dict) -> dict:
        """Export storyboard."""
        response = await self.http_client.post(
            f"/api/v1/studio/storyboards/{params['storyboard_id']}/export",
            json={
                "format": params["format"],
                "options": params.get("options", {}),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Export failed", "format": params["format"]}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
