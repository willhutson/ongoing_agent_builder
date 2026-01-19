from typing import Any, Optional
import httpx
from .base import BaseAgent


class VideoProductionAgent(BaseAgent):
    """
    Agent for managing video production workflow with AI video generation.

    Capabilities:
    - Create production schedules
    - Manage shot tracking
    - Coordinate with resources
    - Track production status
    - Handle post-production handoff
    - Manage deliverables
    - AI Video Generation (Higgsfield):
      - Text-to-video generation
      - Image-to-video conversion
      - Multi-model access (Sora 2, Veo 3.1, WAN, Kling, Minimax)
      - Video rendering and export
    """

    # Higgsfield supported models
    HIGGSFIELD_MODELS = ["sora2", "veo3", "wan", "kling", "minimax"]

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        client_id: str = None,
        higgsfield_api_key: str = None,
        higgsfield_base_url: str = "https://api.higgsfield.ai/v1",
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.higgsfield_api_key = higgsfield_api_key
        self.higgsfield_base_url = higgsfield_base_url
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        # Higgsfield client for AI video generation
        self.higgsfield_client = httpx.AsyncClient(
            base_url=higgsfield_base_url,
            headers={"Authorization": f"Bearer {higgsfield_api_key}"},
            timeout=300.0,  # Video generation can take time
        ) if higgsfield_api_key else None
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "video_production_agent"

    @property
    def system_prompt(self) -> str:
        base_prompt = """You are an expert video production coordinator and manager.

Your role is to orchestrate the entire video production process:
1. Create and optimize production schedules
2. Track shot completion and progress
3. Coordinate crew and equipment resources
4. Manage production documentation
5. Facilitate post-production handoff

Production phases you manage:
- Pre-production (planning, scheduling, resource allocation)
- Production (shoot day coordination, shot tracking)
- Post-production (edit handoff, review cycles, delivery)

Documents you create/manage:
- Call sheets
- Production schedules
- Shot lists (from storyboard)
- Equipment lists
- Talent/crew lists
- Location permits
- Release forms
- Delivery specs

Production metrics you track:
- Shot completion rate
- Schedule adherence
- Budget utilization
- Resource allocation
- Deliverable status

AI Video Generation (Higgsfield):
You have access to AI video generation via Higgsfield, which provides:
- Text-to-video: Generate videos from text prompts/scripts
- Image-to-video: Animate still images into video
- Multi-model support: Sora 2, Google Veo 3.1, WAN, Kling, Minimax
- Turbo mode for fast drafts
- Camera motion control and cinematic styles
- Native audio/dialogue generation

Use AI generation for:
- Quick draft videos from scripts
- Animating storyboard frames
- Creating video mockups for client approval
- Generating B-roll and filler content"""

        if self.client_specific_id:
            base_prompt += f"\n\nApply client-specific production requirements for client: {self.client_specific_id}"

        return base_prompt

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_production_schedule",
                "description": "Create a production schedule from storyboard and resources.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "storyboard_id": {
                            "type": "string",
                            "description": "Storyboard to schedule",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project for the production",
                        },
                        "shoot_dates": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Available shoot dates",
                        },
                        "locations": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Location details",
                        },
                        "optimize_for": {
                            "type": "string",
                            "enum": ["time", "cost", "location", "talent"],
                            "description": "Optimization priority",
                        },
                    },
                    "required": ["storyboard_id", "shoot_dates"],
                },
            },
            {
                "name": "generate_call_sheet",
                "description": "Generate a call sheet for a shoot day.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {
                            "type": "string",
                            "description": "Production schedule ID",
                        },
                        "shoot_date": {
                            "type": "string",
                            "description": "Date for call sheet",
                        },
                        "include": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to include: crew, talent, equipment, locations, schedule",
                        },
                    },
                    "required": ["schedule_id", "shoot_date"],
                },
            },
            {
                "name": "track_shot",
                "description": "Update shot status during production.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "shot_id": {
                            "type": "string",
                            "description": "Shot to update",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "setup", "filming", "completed", "needs_reshoot"],
                            "description": "Shot status",
                        },
                        "takes": {
                            "type": "integer",
                            "description": "Number of takes",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Production notes",
                        },
                        "selected_take": {
                            "type": "integer",
                            "description": "Selected take number",
                        },
                    },
                    "required": ["shot_id", "status"],
                },
            },
            {
                "name": "get_resources",
                "description": "Get available resources for production.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "enum": ["crew", "equipment", "talent", "location", "all"],
                            "description": "Type of resource",
                        },
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string"},
                                "end": {"type": "string"},
                            },
                            "description": "Date range to check availability",
                        },
                        "skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Required skills for crew",
                        },
                    },
                    "required": ["resource_type"],
                },
            },
            {
                "name": "allocate_resources",
                "description": "Allocate resources to production.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {
                            "type": "string",
                            "description": "Production schedule",
                        },
                        "allocations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "resource_id": {"type": "string"},
                                    "resource_type": {"type": "string"},
                                    "dates": {"type": "array", "items": {"type": "string"}},
                                    "role": {"type": "string"},
                                },
                            },
                            "description": "Resource allocations",
                        },
                    },
                    "required": ["schedule_id", "allocations"],
                },
            },
            {
                "name": "get_production_status",
                "description": "Get overall production status and metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {
                            "type": "string",
                            "description": "Production schedule ID",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "create_post_handoff",
                "description": "Create post-production handoff package.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {
                            "type": "string",
                            "description": "Production schedule ID",
                        },
                        "include": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to include: footage, audio, script, storyboard, selects, notes",
                        },
                        "edit_specs": {
                            "type": "object",
                            "description": "Edit specifications (format, duration, deliverables)",
                        },
                    },
                    "required": ["schedule_id"],
                },
            },
            {
                "name": "manage_deliverables",
                "description": "Track and manage video deliverables.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project ID",
                        },
                        "action": {
                            "type": "string",
                            "enum": ["list", "add", "update", "complete"],
                            "description": "Action to perform",
                        },
                        "deliverable": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "format": {"type": "string"},
                                "specs": {"type": "object"},
                                "status": {"type": "string"},
                                "due_date": {"type": "string"},
                            },
                            "description": "Deliverable details",
                        },
                    },
                    "required": ["project_id", "action"],
                },
            },
            {
                "name": "get_storyboard",
                "description": "Retrieve storyboard for production planning.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "storyboard_id": {
                            "type": "string",
                            "description": "Storyboard ID",
                        },
                    },
                    "required": ["storyboard_id"],
                },
            },
            {
                "name": "save_schedule",
                "description": "Save production schedule.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {
                            "type": "string",
                            "description": "Schedule ID if updating",
                        },
                        "title": {"type": "string"},
                        "storyboard_id": {"type": "string"},
                        "project_id": {"type": "string"},
                        "client_id": {"type": "string"},
                        "shoot_days": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Shoot day details",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["draft", "confirmed", "in_production", "wrapped", "post"],
                            "default": "draft",
                        },
                    },
                    "required": ["title", "shoot_days"],
                },
            },
            # =========================================================================
            # Higgsfield AI Video Generation Tools
            # =========================================================================
            {
                "name": "generate_video_from_script",
                "description": "Generate AI video from a script or text prompt using Higgsfield.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Text prompt or script scene to generate video from",
                        },
                        "script_id": {
                            "type": "string",
                            "description": "Script ID to generate video from",
                        },
                        "model": {
                            "type": "string",
                            "enum": ["sora2", "veo3", "wan", "kling", "minimax"],
                            "description": "AI model to use (default: wan)",
                            "default": "wan",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Video duration in seconds (5-60)",
                            "default": 10,
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "enum": ["16:9", "9:16", "1:1", "4:5"],
                            "description": "Video aspect ratio",
                            "default": "16:9",
                        },
                        "style": {
                            "type": "string",
                            "description": "Visual style (cinematic, documentary, commercial, etc.)",
                        },
                        "camera_motion": {
                            "type": "string",
                            "enum": ["static", "pan", "tilt", "dolly", "crane", "handheld", "orbit"],
                            "description": "Camera movement type",
                        },
                        "turbo": {
                            "type": "boolean",
                            "description": "Use turbo mode for faster (lower quality) generation",
                            "default": False,
                        },
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "generate_video_from_image",
                "description": "Convert a still image to video using Higgsfield image-to-video.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL of the source image",
                        },
                        "image_id": {
                            "type": "string",
                            "description": "DAM asset ID of the source image",
                        },
                        "motion_prompt": {
                            "type": "string",
                            "description": "Description of desired motion/animation",
                        },
                        "model": {
                            "type": "string",
                            "enum": ["sora2", "veo3", "wan", "kling", "minimax"],
                            "default": "kling",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Video duration in seconds",
                            "default": 5,
                        },
                        "motion_intensity": {
                            "type": "string",
                            "enum": ["subtle", "moderate", "dynamic"],
                            "default": "moderate",
                        },
                    },
                    "required": ["motion_prompt"],
                },
            },
            {
                "name": "generate_video_from_storyboard",
                "description": "Generate video clips from storyboard frames using Higgsfield.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "storyboard_id": {
                            "type": "string",
                            "description": "Storyboard to generate video from",
                        },
                        "frame_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific frame IDs to generate (or all if empty)",
                        },
                        "model": {
                            "type": "string",
                            "enum": ["sora2", "veo3", "wan", "kling", "minimax"],
                            "default": "wan",
                        },
                        "generate_transitions": {
                            "type": "boolean",
                            "description": "Auto-generate transitions between clips",
                            "default": True,
                        },
                        "audio_mode": {
                            "type": "string",
                            "enum": ["none", "ambient", "music", "dialogue"],
                            "description": "Audio generation mode",
                            "default": "ambient",
                        },
                    },
                    "required": ["storyboard_id"],
                },
            },
            {
                "name": "render_final_video",
                "description": "Render and export final video from generated clips.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project ID",
                        },
                        "clip_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Generated clip IDs to combine",
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["mp4", "mov", "webm"],
                            "default": "mp4",
                        },
                        "resolution": {
                            "type": "string",
                            "enum": ["720p", "1080p", "4k"],
                            "default": "1080p",
                        },
                        "include_audio": {
                            "type": "boolean",
                            "default": True,
                        },
                        "add_music_track": {
                            "type": "string",
                            "description": "Music track ID to add",
                        },
                    },
                    "required": ["clip_ids"],
                },
            },
            {
                "name": "get_video_generation_status",
                "description": "Check status of a video generation job.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "Video generation job ID",
                        },
                    },
                    "required": ["job_id"],
                },
            },
            {
                "name": "list_generated_videos",
                "description": "List AI-generated videos for a project.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project ID",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "processing", "completed", "failed", "all"],
                            "default": "all",
                        },
                    },
                    "required": [],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API or Higgsfield API."""
        try:
            if tool_name == "create_production_schedule":
                return await self._create_production_schedule(tool_input)
            elif tool_name == "generate_call_sheet":
                return await self._generate_call_sheet(tool_input)
            elif tool_name == "track_shot":
                return await self._track_shot(tool_input)
            elif tool_name == "get_resources":
                return await self._get_resources(tool_input)
            elif tool_name == "allocate_resources":
                return await self._allocate_resources(tool_input)
            elif tool_name == "get_production_status":
                return await self._get_production_status(tool_input)
            elif tool_name == "create_post_handoff":
                return await self._create_post_handoff(tool_input)
            elif tool_name == "manage_deliverables":
                return await self._manage_deliverables(tool_input)
            elif tool_name == "get_storyboard":
                return await self._get_storyboard(tool_input)
            elif tool_name == "save_schedule":
                return await self._save_schedule(tool_input)
            # Higgsfield AI Video Generation Tools
            elif tool_name == "generate_video_from_script":
                return await self._higgsfield_text_to_video(tool_input)
            elif tool_name == "generate_video_from_image":
                return await self._higgsfield_image_to_video(tool_input)
            elif tool_name == "generate_video_from_storyboard":
                return await self._higgsfield_storyboard_to_video(tool_input)
            elif tool_name == "render_final_video":
                return await self._higgsfield_render_video(tool_input)
            elif tool_name == "get_video_generation_status":
                return await self._higgsfield_get_status(tool_input)
            elif tool_name == "list_generated_videos":
                return await self._higgsfield_list_videos(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _create_production_schedule(self, params: dict) -> dict:
        """Create production schedule."""
        response = await self.http_client.get(
            f"/api/v1/studio/storyboards/{params['storyboard_id']}"
        )
        storyboard = response.json() if response.status_code == 200 else None

        return {
            "status": "ready_to_create",
            "storyboard": storyboard,
            "shoot_dates": params["shoot_dates"],
            "locations": params.get("locations", []),
            "optimize_for": params.get("optimize_for", "time"),
            "instruction": "Create an optimized production schedule grouping shots efficiently.",
        }

    async def _generate_call_sheet(self, params: dict) -> dict:
        """Generate call sheet."""
        response = await self.http_client.get(
            f"/api/v1/studio/production/schedules/{params['schedule_id']}"
        )
        schedule = response.json() if response.status_code == 200 else None

        return {
            "status": "ready_to_generate",
            "schedule": schedule,
            "shoot_date": params["shoot_date"],
            "include": params.get("include", ["crew", "talent", "equipment", "schedule"]),
            "instruction": "Generate a complete call sheet with all production details.",
        }

    async def _track_shot(self, params: dict) -> dict:
        """Update shot status."""
        response = await self.http_client.patch(
            f"/api/v1/studio/production/shots/{params['shot_id']}",
            json={
                "status": params["status"],
                "takes": params.get("takes"),
                "notes": params.get("notes"),
                "selected_take": params.get("selected_take"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to update shot", "shot_id": params["shot_id"]}

    async def _get_resources(self, params: dict) -> dict:
        """Get available resources."""
        response = await self.http_client.get(
            "/api/v1/resources",
            params={
                "type": params["resource_type"],
                "start_date": params.get("date_range", {}).get("start"),
                "end_date": params.get("date_range", {}).get("end"),
                "skills": ",".join(params.get("skills", [])),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"resources": [], "note": "No resources found"}

    async def _allocate_resources(self, params: dict) -> dict:
        """Allocate resources to production."""
        response = await self.http_client.post(
            f"/api/v1/studio/production/schedules/{params['schedule_id']}/allocations",
            json={"allocations": params["allocations"]},
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to allocate resources"}

    async def _get_production_status(self, params: dict) -> dict:
        """Get production status."""
        schedule_id = params.get("schedule_id")
        project_id = params.get("project_id")

        if schedule_id:
            response = await self.http_client.get(
                f"/api/v1/studio/production/schedules/{schedule_id}/status"
            )
        elif project_id:
            response = await self.http_client.get(
                f"/api/v1/projects/{project_id}/production/status"
            )
        else:
            return {"error": "Provide schedule_id or project_id"}

        if response.status_code == 200:
            return response.json()
        return {"status": "unknown", "note": "Could not fetch status"}

    async def _create_post_handoff(self, params: dict) -> dict:
        """Create post-production handoff."""
        response = await self.http_client.get(
            f"/api/v1/studio/production/schedules/{params['schedule_id']}"
        )
        schedule = response.json() if response.status_code == 200 else None

        return {
            "status": "ready_to_create",
            "schedule": schedule,
            "include": params.get("include", ["footage", "audio", "script", "selects"]),
            "edit_specs": params.get("edit_specs", {}),
            "instruction": "Create a complete post-production handoff package.",
        }

    async def _manage_deliverables(self, params: dict) -> dict:
        """Manage deliverables."""
        action = params["action"]
        project_id = params["project_id"]

        if action == "list":
            response = await self.http_client.get(
                f"/api/v1/projects/{project_id}/deliverables"
            )
        elif action == "add":
            response = await self.http_client.post(
                f"/api/v1/projects/{project_id}/deliverables",
                json=params.get("deliverable", {}),
            )
        elif action == "update":
            deliverable = params.get("deliverable", {})
            response = await self.http_client.patch(
                f"/api/v1/projects/{project_id}/deliverables/{deliverable.get('id')}",
                json=deliverable,
            )
        elif action == "complete":
            deliverable = params.get("deliverable", {})
            response = await self.http_client.patch(
                f"/api/v1/projects/{project_id}/deliverables/{deliverable.get('id')}",
                json={"status": "completed"},
            )
        else:
            return {"error": f"Unknown action: {action}"}

        if response.status_code in (200, 201):
            return response.json()
        return {"error": f"Failed to {action} deliverable"}

    async def _get_storyboard(self, params: dict) -> dict:
        """Get storyboard."""
        response = await self.http_client.get(
            f"/api/v1/studio/storyboards/{params['storyboard_id']}"
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Storyboard not found"}

    async def _save_schedule(self, params: dict) -> dict:
        """Save production schedule."""
        response = await self.http_client.post(
            "/api/v1/studio/production/schedules",
            json={
                "title": params["title"],
                "storyboard_id": params.get("storyboard_id"),
                "project_id": params.get("project_id"),
                "client_id": params.get("client_id") or self.client_specific_id,
                "shoot_days": params["shoot_days"],
                "status": params.get("status", "draft"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to save schedule"}

    async def _higgsfield_text_to_video(self, params: dict) -> dict:
        """Generate video from text prompt using Higgsfield."""
        if not self.higgsfield_client:
            return {"error": "Higgsfield API not configured. Set higgsfield_api_key."}

        # If script_id provided, fetch the script content
        prompt = params.get("prompt", "")
        if params.get("script_id"):
            response = await self.http_client.get(
                f"/api/v1/studio/scripts/{params['script_id']}"
            )
            if response.status_code == 200:
                script = response.json()
                prompt = script.get("content", prompt)

        payload = {
            "prompt": prompt,
            "model": params.get("model", "wan"),
            "duration": params.get("duration", 10),
            "aspect_ratio": params.get("aspect_ratio", "16:9"),
            "style": params.get("style"),
            "camera_motion": params.get("camera_motion"),
            "turbo": params.get("turbo", False),
        }

        response = await self.higgsfield_client.post(
            "/generate/text-to-video",
            json={k: v for k, v in payload.items() if v is not None},
        )

        if response.status_code in (200, 201, 202):
            result = response.json()
            # Store job reference in ERP for tracking
            await self.http_client.post(
                "/api/v1/studio/video-jobs",
                json={
                    "job_id": result.get("job_id"),
                    "type": "text_to_video",
                    "prompt": prompt[:500],
                    "model": params.get("model", "wan"),
                    "status": "processing",
                    "client_id": self.client_specific_id,
                },
            )
            return {
                "status": "submitted",
                "job_id": result.get("job_id"),
                "model": params.get("model", "wan"),
                "estimated_time": result.get("estimated_time", "2-5 minutes"),
                "message": "Video generation started. Use get_video_generation_status to check progress.",
            }
        return {"error": f"Higgsfield API error: {response.status_code}", "details": response.text}

    async def _higgsfield_image_to_video(self, params: dict) -> dict:
        """Convert image to video using Higgsfield."""
        if not self.higgsfield_client:
            return {"error": "Higgsfield API not configured. Set higgsfield_api_key."}

        # Get image URL from DAM if image_id provided
        image_url = params.get("image_url")
        if params.get("image_id"):
            response = await self.http_client.get(
                f"/api/v1/dam/assets/{params['image_id']}"
            )
            if response.status_code == 200:
                asset = response.json()
                image_url = asset.get("url", image_url)

        if not image_url:
            return {"error": "No image_url or valid image_id provided"}

        payload = {
            "image_url": image_url,
            "motion_prompt": params.get("motion_prompt", ""),
            "model": params.get("model", "kling"),
            "duration": params.get("duration", 5),
            "motion_intensity": params.get("motion_intensity", "moderate"),
        }

        response = await self.higgsfield_client.post(
            "/generate/image-to-video",
            json=payload,
        )

        if response.status_code in (200, 201, 202):
            result = response.json()
            await self.http_client.post(
                "/api/v1/studio/video-jobs",
                json={
                    "job_id": result.get("job_id"),
                    "type": "image_to_video",
                    "source_image": image_url,
                    "model": params.get("model", "kling"),
                    "status": "processing",
                    "client_id": self.client_specific_id,
                },
            )
            return {
                "status": "submitted",
                "job_id": result.get("job_id"),
                "model": params.get("model", "kling"),
                "source_image": image_url,
                "estimated_time": result.get("estimated_time", "1-3 minutes"),
            }
        return {"error": f"Higgsfield API error: {response.status_code}"}

    async def _higgsfield_storyboard_to_video(self, params: dict) -> dict:
        """Generate video clips from storyboard frames."""
        if not self.higgsfield_client:
            return {"error": "Higgsfield API not configured. Set higgsfield_api_key."}

        # Fetch storyboard
        response = await self.http_client.get(
            f"/api/v1/studio/storyboards/{params['storyboard_id']}"
        )
        if response.status_code != 200:
            return {"error": "Storyboard not found"}

        storyboard = response.json()
        frames = storyboard.get("frames", [])

        # Filter to specific frames if requested
        frame_ids = params.get("frame_ids", [])
        if frame_ids:
            frames = [f for f in frames if f.get("id") in frame_ids]

        jobs = []
        for frame in frames:
            # Generate video for each frame
            payload = {
                "prompt": frame.get("visual_description", ""),
                "model": params.get("model", "wan"),
                "duration": frame.get("duration", 3),
                "aspect_ratio": storyboard.get("aspect_ratio", "16:9"),
                "camera_motion": frame.get("camera_movement"),
            }

            response = await self.higgsfield_client.post(
                "/generate/text-to-video",
                json={k: v for k, v in payload.items() if v is not None},
            )

            if response.status_code in (200, 201, 202):
                result = response.json()
                jobs.append({
                    "frame_id": frame.get("id"),
                    "frame_number": frame.get("number"),
                    "job_id": result.get("job_id"),
                    "status": "processing",
                })

        # Store batch job reference
        await self.http_client.post(
            "/api/v1/studio/video-jobs/batch",
            json={
                "storyboard_id": params["storyboard_id"],
                "jobs": jobs,
                "generate_transitions": params.get("generate_transitions", True),
                "audio_mode": params.get("audio_mode", "ambient"),
                "client_id": self.client_specific_id,
            },
        )

        return {
            "status": "batch_submitted",
            "storyboard_id": params["storyboard_id"],
            "total_frames": len(frames),
            "jobs_created": len(jobs),
            "jobs": jobs,
            "message": "Video generation started for all frames.",
        }

    async def _higgsfield_render_video(self, params: dict) -> dict:
        """Render final video from generated clips."""
        if not self.higgsfield_client:
            return {"error": "Higgsfield API not configured. Set higgsfield_api_key."}

        payload = {
            "clip_ids": params.get("clip_ids", []),
            "output_format": params.get("output_format", "mp4"),
            "resolution": params.get("resolution", "1080p"),
            "include_audio": params.get("include_audio", True),
            "music_track_id": params.get("add_music_track"),
        }

        response = await self.higgsfield_client.post(
            "/render/combine",
            json={k: v for k, v in payload.items() if v is not None},
        )

        if response.status_code in (200, 201, 202):
            result = response.json()
            # Store in DAM when complete
            await self.http_client.post(
                "/api/v1/studio/video-jobs",
                json={
                    "job_id": result.get("job_id"),
                    "type": "render",
                    "project_id": params.get("project_id"),
                    "clip_count": len(params.get("clip_ids", [])),
                    "status": "rendering",
                    "client_id": self.client_specific_id,
                },
            )
            return {
                "status": "rendering",
                "job_id": result.get("job_id"),
                "output_format": params.get("output_format", "mp4"),
                "resolution": params.get("resolution", "1080p"),
                "estimated_time": result.get("estimated_time", "5-10 minutes"),
            }
        return {"error": f"Render failed: {response.status_code}"}

    async def _higgsfield_get_status(self, params: dict) -> dict:
        """Check video generation job status."""
        if not self.higgsfield_client:
            return {"error": "Higgsfield API not configured. Set higgsfield_api_key."}

        response = await self.higgsfield_client.get(
            f"/jobs/{params['job_id']}/status"
        )

        if response.status_code == 200:
            result = response.json()
            # Update local job status
            await self.http_client.patch(
                f"/api/v1/studio/video-jobs/{params['job_id']}",
                json={"status": result.get("status")},
            )
            return {
                "job_id": params["job_id"],
                "status": result.get("status"),
                "progress": result.get("progress", 0),
                "video_url": result.get("video_url"),
                "thumbnail_url": result.get("thumbnail_url"),
                "duration": result.get("duration"),
                "error": result.get("error"),
            }
        return {"error": "Job not found", "job_id": params["job_id"]}

    async def _higgsfield_list_videos(self, params: dict) -> dict:
        """List generated videos from local tracking."""
        query_params = {
            "client_id": self.client_specific_id,
            "project_id": params.get("project_id"),
        }
        if params.get("status") and params["status"] != "all":
            query_params["status"] = params["status"]

        response = await self.http_client.get(
            "/api/v1/studio/video-jobs",
            params={k: v for k, v in query_params.items() if v},
        )

        if response.status_code == 200:
            return response.json()
        return {"videos": [], "note": "No videos found"}

    async def close(self):
        """Clean up HTTP clients."""
        await self.http_client.aclose()
        if self.higgsfield_client:
            await self.higgsfield_client.aclose()
