from typing import Any, Optional, List
import httpx
from .base import BaseAgent


class VideoStoryboardAgent(BaseAgent):
    """
    Agent for generating video storyboards with AI animation capabilities.

    Capabilities:
    - Generate storyboards from scripts
    - Create frame-by-frame visual plans
    - Specify camera angles and movements
    - Add technical annotations
    - Apply moodboard styling
    - Generate shot lists
    - AI Animation (Higgsfield):
      - Sketch-to-video conversion
      - Frame animation/animatics
      - Draw-to-video for rough concepts
      - Storyboard frame image generation
    """

    # Higgsfield supported models for storyboard work
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
        # Higgsfield client for AI video/animation generation
        self.higgsfield_client = httpx.AsyncClient(
            base_url=higgsfield_base_url,
            headers={"Authorization": f"Bearer {higgsfield_api_key}"},
            timeout=300.0,
        ) if higgsfield_api_key else None
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
- Product shots

AI Animation (Higgsfield):
You have access to AI animation via Higgsfield for:
- Sketch-to-video: Convert rough sketches into animated video
- Draw-to-video: Animate hand-drawn storyboard frames
- Frame animation: Bring static storyboard frames to life
- Animatic generation: Create moving storyboards with timing

Use AI animation to:
- Create quick animatics for client review
- Test shot timing and pacing
- Visualize camera movements
- Generate moving storyboards before production"""

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
            # =========================================================================
            # Higgsfield AI Animation Tools
            # =========================================================================
            {
                "name": "animate_storyboard_frame",
                "description": "Animate a single storyboard frame using Higgsfield sketch-to-video.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "frame_id": {
                            "type": "string",
                            "description": "Storyboard frame ID to animate",
                        },
                        "frame_image_url": {
                            "type": "string",
                            "description": "URL of the frame image/sketch to animate",
                        },
                        "motion_description": {
                            "type": "string",
                            "description": "Description of desired motion/animation",
                        },
                        "model": {
                            "type": "string",
                            "enum": ["sora2", "veo3", "wan", "kling", "minimax"],
                            "default": "kling",
                        },
                        "duration": {
                            "type": "number",
                            "description": "Animation duration in seconds",
                            "default": 3,
                        },
                        "motion_intensity": {
                            "type": "string",
                            "enum": ["subtle", "moderate", "dynamic"],
                            "default": "moderate",
                        },
                    },
                    "required": ["motion_description"],
                },
            },
            {
                "name": "generate_animatic",
                "description": "Generate a full animatic (moving storyboard) from storyboard frames using Higgsfield.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "storyboard_id": {
                            "type": "string",
                            "description": "Storyboard to create animatic from",
                        },
                        "frame_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific frames to include (or all if empty)",
                        },
                        "model": {
                            "type": "string",
                            "enum": ["sora2", "veo3", "wan", "kling", "minimax"],
                            "default": "wan",
                        },
                        "include_transitions": {
                            "type": "boolean",
                            "description": "Generate transitions between frames",
                            "default": True,
                        },
                        "timing_source": {
                            "type": "string",
                            "enum": ["frame_duration", "audio_track", "fixed"],
                            "description": "How to determine timing",
                            "default": "frame_duration",
                        },
                        "audio_track_id": {
                            "type": "string",
                            "description": "Audio track to sync timing with",
                        },
                    },
                    "required": ["storyboard_id"],
                },
            },
            {
                "name": "sketch_to_video",
                "description": "Convert a rough sketch or drawing directly to video using Higgsfield.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sketch_url": {
                            "type": "string",
                            "description": "URL of the sketch image",
                        },
                        "sketch_id": {
                            "type": "string",
                            "description": "DAM asset ID of the sketch",
                        },
                        "style_prompt": {
                            "type": "string",
                            "description": "Visual style to apply (realistic, animated, cinematic, etc.)",
                        },
                        "motion_prompt": {
                            "type": "string",
                            "description": "Description of desired motion",
                        },
                        "model": {
                            "type": "string",
                            "enum": ["sora2", "veo3", "wan", "kling", "minimax"],
                            "default": "kling",
                        },
                        "duration": {
                            "type": "number",
                            "default": 5,
                        },
                        "preserve_sketch_style": {
                            "type": "boolean",
                            "description": "Keep the sketch/drawing aesthetic",
                            "default": False,
                        },
                    },
                    "required": ["motion_prompt"],
                },
            },
            {
                "name": "generate_frame_image",
                "description": "Generate a storyboard frame image from text description using AI.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "scene_description": {
                            "type": "string",
                            "description": "Detailed description of the frame",
                        },
                        "style": {
                            "type": "string",
                            "enum": ["sketch", "detailed", "realistic", "animated"],
                            "default": "sketch",
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "enum": ["16:9", "9:16", "1:1", "4:5"],
                            "default": "16:9",
                        },
                        "camera_angle": {
                            "type": "string",
                            "description": "Camera angle for the frame",
                        },
                        "reference_moodboard_id": {
                            "type": "string",
                            "description": "Moodboard for style reference",
                        },
                    },
                    "required": ["scene_description"],
                },
            },
            {
                "name": "get_animation_status",
                "description": "Check status of an animation generation job.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "Animation job ID",
                        },
                    },
                    "required": ["job_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API or Higgsfield API."""
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
            # Higgsfield AI Animation Tools
            elif tool_name == "animate_storyboard_frame":
                return await self._higgsfield_animate_frame(tool_input)
            elif tool_name == "generate_animatic":
                return await self._higgsfield_generate_animatic(tool_input)
            elif tool_name == "sketch_to_video":
                return await self._higgsfield_sketch_to_video(tool_input)
            elif tool_name == "generate_frame_image":
                return await self._higgsfield_generate_frame_image(tool_input)
            elif tool_name == "get_animation_status":
                return await self._higgsfield_get_status(tool_input)
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

    async def _higgsfield_animate_frame(self, params: dict) -> dict:
        """Animate a single storyboard frame using Higgsfield."""
        if not self.higgsfield_client:
            return {"error": "Higgsfield API not configured. Set higgsfield_api_key."}

        # Get frame image URL
        image_url = params.get("frame_image_url")
        if params.get("frame_id"):
            response = await self.http_client.get(
                f"/api/v1/studio/storyboards/frames/{params['frame_id']}"
            )
            if response.status_code == 200:
                frame = response.json()
                image_url = frame.get("image_url", image_url)

        if not image_url:
            return {"error": "No frame_image_url or valid frame_id provided"}

        payload = {
            "image_url": image_url,
            "motion_prompt": params.get("motion_description", ""),
            "model": params.get("model", "kling"),
            "duration": params.get("duration", 3),
            "motion_intensity": params.get("motion_intensity", "moderate"),
        }

        response = await self.higgsfield_client.post(
            "/generate/image-to-video",
            json=payload,
        )

        if response.status_code in (200, 201, 202):
            result = response.json()
            # Track the animation job
            await self.http_client.post(
                "/api/v1/studio/animation-jobs",
                json={
                    "job_id": result.get("job_id"),
                    "type": "frame_animation",
                    "frame_id": params.get("frame_id"),
                    "source_image": image_url,
                    "status": "processing",
                    "client_id": self.client_specific_id,
                },
            )
            return {
                "status": "submitted",
                "job_id": result.get("job_id"),
                "frame_id": params.get("frame_id"),
                "model": params.get("model", "kling"),
                "estimated_time": result.get("estimated_time", "1-2 minutes"),
            }
        return {"error": f"Higgsfield API error: {response.status_code}"}

    async def _higgsfield_generate_animatic(self, params: dict) -> dict:
        """Generate a full animatic from storyboard frames."""
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

        # Filter frames if specified
        frame_ids = params.get("frame_ids", [])
        if frame_ids:
            frames = [f for f in frames if f.get("id") in frame_ids]

        if not frames:
            return {"error": "No frames found in storyboard"}

        # Generate animations for each frame
        animation_jobs = []
        for frame in frames:
            image_url = frame.get("image_url")
            if not image_url:
                continue

            payload = {
                "image_url": image_url,
                "motion_prompt": frame.get("camera_movement", "subtle motion"),
                "model": params.get("model", "wan"),
                "duration": frame.get("duration", 2),
                "motion_intensity": "moderate",
            }

            response = await self.higgsfield_client.post(
                "/generate/image-to-video",
                json=payload,
            )

            if response.status_code in (200, 201, 202):
                result = response.json()
                animation_jobs.append({
                    "frame_id": frame.get("id"),
                    "frame_number": frame.get("number"),
                    "job_id": result.get("job_id"),
                    "duration": frame.get("duration", 2),
                    "status": "processing",
                })

        # Store animatic batch job
        await self.http_client.post(
            "/api/v1/studio/animatic-jobs",
            json={
                "storyboard_id": params["storyboard_id"],
                "frame_jobs": animation_jobs,
                "include_transitions": params.get("include_transitions", True),
                "timing_source": params.get("timing_source", "frame_duration"),
                "audio_track_id": params.get("audio_track_id"),
                "status": "processing",
                "client_id": self.client_specific_id,
            },
        )

        return {
            "status": "animatic_generation_started",
            "storyboard_id": params["storyboard_id"],
            "total_frames": len(frames),
            "jobs_created": len(animation_jobs),
            "frame_jobs": animation_jobs,
            "include_transitions": params.get("include_transitions", True),
            "message": "Animatic generation started. Each frame will be animated.",
        }

    async def _higgsfield_sketch_to_video(self, params: dict) -> dict:
        """Convert a rough sketch directly to video."""
        if not self.higgsfield_client:
            return {"error": "Higgsfield API not configured. Set higgsfield_api_key."}

        # Get sketch URL
        sketch_url = params.get("sketch_url")
        if params.get("sketch_id"):
            response = await self.http_client.get(
                f"/api/v1/dam/assets/{params['sketch_id']}"
            )
            if response.status_code == 200:
                asset = response.json()
                sketch_url = asset.get("url", sketch_url)

        if not sketch_url:
            return {"error": "No sketch_url or valid sketch_id provided"}

        # Build prompt combining style and motion
        prompt_parts = []
        if params.get("style_prompt"):
            prompt_parts.append(f"Style: {params['style_prompt']}")
        if params.get("motion_prompt"):
            prompt_parts.append(f"Motion: {params['motion_prompt']}")

        payload = {
            "image_url": sketch_url,
            "motion_prompt": " | ".join(prompt_parts) if prompt_parts else "gentle animation",
            "model": params.get("model", "kling"),
            "duration": params.get("duration", 5),
            "preserve_style": params.get("preserve_sketch_style", False),
        }

        response = await self.higgsfield_client.post(
            "/generate/sketch-to-video",
            json=payload,
        )

        if response.status_code in (200, 201, 202):
            result = response.json()
            await self.http_client.post(
                "/api/v1/studio/animation-jobs",
                json={
                    "job_id": result.get("job_id"),
                    "type": "sketch_to_video",
                    "source_sketch": sketch_url,
                    "status": "processing",
                    "client_id": self.client_specific_id,
                },
            )
            return {
                "status": "submitted",
                "job_id": result.get("job_id"),
                "model": params.get("model", "kling"),
                "source_sketch": sketch_url,
                "estimated_time": result.get("estimated_time", "2-4 minutes"),
            }
        return {"error": f"Higgsfield API error: {response.status_code}"}

    async def _higgsfield_generate_frame_image(self, params: dict) -> dict:
        """Generate a storyboard frame image from text description."""
        if not self.higgsfield_client:
            return {"error": "Higgsfield API not configured. Set higgsfield_api_key."}

        # Get moodboard style reference if provided
        style_reference = None
        if params.get("reference_moodboard_id"):
            response = await self.http_client.get(
                f"/api/v1/studio/moodboards/{params['reference_moodboard_id']}/analyze"
            )
            if response.status_code == 200:
                style_reference = response.json()

        # Build the prompt
        prompt = params["scene_description"]
        if params.get("camera_angle"):
            prompt = f"{params['camera_angle']} shot: {prompt}"
        if style_reference:
            prompt = f"{prompt}. Style reference: {style_reference.get('style_summary', '')}"

        # Map our style to Higgsfield style presets
        style_map = {
            "sketch": "storyboard_sketch",
            "detailed": "detailed_illustration",
            "realistic": "photorealistic",
            "animated": "animation_style",
        }

        payload = {
            "prompt": prompt,
            "style": style_map.get(params.get("style", "sketch"), "storyboard_sketch"),
            "aspect_ratio": params.get("aspect_ratio", "16:9"),
        }

        response = await self.higgsfield_client.post(
            "/generate/image",
            json=payload,
        )

        if response.status_code in (200, 201):
            result = response.json()
            return {
                "status": "completed",
                "image_url": result.get("image_url"),
                "style": params.get("style", "sketch"),
                "aspect_ratio": params.get("aspect_ratio", "16:9"),
                "prompt_used": prompt[:200],
            }
        return {"error": f"Image generation failed: {response.status_code}"}

    async def _higgsfield_get_status(self, params: dict) -> dict:
        """Check animation job status."""
        if not self.higgsfield_client:
            return {"error": "Higgsfield API not configured. Set higgsfield_api_key."}

        response = await self.higgsfield_client.get(
            f"/jobs/{params['job_id']}/status"
        )

        if response.status_code == 200:
            result = response.json()
            # Update local job status
            await self.http_client.patch(
                f"/api/v1/studio/animation-jobs/{params['job_id']}",
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

    async def close(self):
        """Clean up HTTP clients."""
        await self.http_client.aclose()
        if self.higgsfield_client:
            await self.higgsfield_client.aclose()
