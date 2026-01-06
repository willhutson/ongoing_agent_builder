from typing import Any
import httpx
from .base import BaseAgent


class ImageAgent(BaseAgent):
    """
    Agent for AI image generation and manipulation.

    Capabilities:
    - Generate images from text prompts
    - Generate images from moodboard style
    - Style transfer and consistency
    - Upscaling and enhancement
    - DAM integration
    - Brand style application
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        image_provider: str = "dall-e",  # dall-e, midjourney, stable-diffusion
        client_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.image_provider = image_provider
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=120.0,  # Longer timeout for image generation
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return f"image_agent_{self.image_provider}"

    @property
    def system_prompt(self) -> str:
        base_prompt = """You are an expert visual designer and AI image generation specialist.

Your role is to create compelling visual assets by:
1. Crafting effective prompts for AI image generation
2. Maintaining brand consistency across visuals
3. Understanding composition, color, and visual hierarchy
4. Applying moodboard styles to generated content
5. Ensuring high-quality, usable output

When generating images:
- Be specific about style, mood, lighting, and composition
- Include relevant details (environment, objects, colors)
- Specify aspect ratio and resolution needs
- Consider how images will be used (social, print, web)
- Maintain brand visual guidelines

Image types you can create:
- Hero images and banners
- Social media graphics
- Product visualizations
- Conceptual/abstract imagery
- Lifestyle photography style
- Illustrations and graphics
- Backgrounds and textures
- Marketing assets"""

        base_prompt += f"\n\nImage generation provider: {self.image_provider}"

        if self.client_specific_id:
            base_prompt += f"\n\nApply client-specific brand visuals for client: {self.client_specific_id}"

        return base_prompt

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_from_prompt",
                "description": "Generate an image from a text prompt.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Detailed text prompt for image generation",
                        },
                        "negative_prompt": {
                            "type": "string",
                            "description": "What to avoid in the image",
                        },
                        "style": {
                            "type": "string",
                            "enum": ["photorealistic", "illustration", "3d_render", "digital_art", "watercolor", "minimalist", "vintage", "modern"],
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "enum": ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9"],
                            "default": "1:1",
                        },
                        "quality": {
                            "type": "string",
                            "enum": ["draft", "standard", "hd"],
                            "default": "standard",
                        },
                        "num_variations": {
                            "type": "integer",
                            "description": "Number of variations to generate",
                            "default": 1,
                        },
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "generate_from_moodboard",
                "description": "Generate an image matching a moodboard's style.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "moodboard_id": {
                            "type": "string",
                            "description": "Moodboard to use as style reference",
                        },
                        "subject": {
                            "type": "string",
                            "description": "What the image should depict",
                        },
                        "additional_guidance": {
                            "type": "string",
                            "description": "Additional style or content guidance",
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "enum": ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9"],
                            "default": "1:1",
                        },
                        "num_variations": {
                            "type": "integer",
                            "default": 1,
                        },
                    },
                    "required": ["moodboard_id", "subject"],
                },
            },
            {
                "name": "get_moodboard",
                "description": "Fetch moodboard for style reference.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "moodboard_id": {"type": "string"},
                        "project_id": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_moodboard",
                "description": "Analyze moodboard to extract visual style for generation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "moodboard_id": {"type": "string"},
                        "extract": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to extract: colors, lighting, composition, mood, texture, style",
                            "default": ["colors", "mood", "style"],
                        },
                    },
                    "required": ["moodboard_id"],
                },
            },
            {
                "name": "upscale_image",
                "description": "Upscale an image to higher resolution.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "Image ID from DAM",
                        },
                        "image_url": {
                            "type": "string",
                            "description": "Image URL if not in DAM",
                        },
                        "scale_factor": {
                            "type": "integer",
                            "enum": [2, 4],
                            "default": 2,
                        },
                        "enhance": {
                            "type": "boolean",
                            "description": "Apply enhancement during upscale",
                            "default": True,
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "style_transfer",
                "description": "Apply a style from one image to another.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_image_id": {
                            "type": "string",
                            "description": "Image to transform",
                        },
                        "style_image_id": {
                            "type": "string",
                            "description": "Image to take style from",
                        },
                        "moodboard_id": {
                            "type": "string",
                            "description": "Or use moodboard as style reference",
                        },
                        "strength": {
                            "type": "number",
                            "description": "Style application strength (0-1)",
                            "default": 0.7,
                        },
                    },
                    "required": ["content_image_id"],
                },
            },
            {
                "name": "get_brand_visuals",
                "description": "Fetch brand visual guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "include_palette": {
                            "type": "boolean",
                            "default": True,
                        },
                        "include_examples": {
                            "type": "boolean",
                            "default": True,
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "apply_brand_style",
                "description": "Ensure an image matches brand visual guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_id": {"type": "string"},
                        "client_id": {"type": "string"},
                        "adjustments": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to adjust: colors, contrast, saturation, filter",
                        },
                    },
                    "required": ["image_id"],
                },
            },
            {
                "name": "save_to_dam",
                "description": "Save generated image to DAM.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_data": {
                            "type": "string",
                            "description": "Base64 image data or URL",
                        },
                        "filename": {"type": "string"},
                        "title": {"type": "string"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "project_id": {"type": "string"},
                        "client_id": {"type": "string"},
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata (prompt, style, etc.)",
                        },
                    },
                    "required": ["title"],
                },
            },
            {
                "name": "get_from_dam",
                "description": "Retrieve an image from DAM.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_id": {"type": "string"},
                        "search_query": {
                            "type": "string",
                            "description": "Search for images by query",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tags",
                        },
                        "project_id": {"type": "string"},
                        "limit": {
                            "type": "integer",
                            "default": 10,
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "create_variations",
                "description": "Create variations of an existing image.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_id": {"type": "string"},
                        "variation_type": {
                            "type": "string",
                            "enum": ["color", "composition", "style", "crop", "all"],
                            "default": "all",
                        },
                        "num_variations": {
                            "type": "integer",
                            "default": 3,
                        },
                    },
                    "required": ["image_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "generate_from_prompt":
                return await self._generate_from_prompt(tool_input)
            elif tool_name == "generate_from_moodboard":
                return await self._generate_from_moodboard(tool_input)
            elif tool_name == "get_moodboard":
                return await self._get_moodboard(tool_input)
            elif tool_name == "analyze_moodboard":
                return await self._analyze_moodboard(tool_input)
            elif tool_name == "upscale_image":
                return await self._upscale_image(tool_input)
            elif tool_name == "style_transfer":
                return await self._style_transfer(tool_input)
            elif tool_name == "get_brand_visuals":
                return await self._get_brand_visuals(tool_input)
            elif tool_name == "apply_brand_style":
                return await self._apply_brand_style(tool_input)
            elif tool_name == "save_to_dam":
                return await self._save_to_dam(tool_input)
            elif tool_name == "get_from_dam":
                return await self._get_from_dam(tool_input)
            elif tool_name == "create_variations":
                return await self._create_variations(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _generate_from_prompt(self, params: dict) -> dict:
        """Generate image from prompt."""
        response = await self.http_client.post(
            "/api/v1/studio/images/generate",
            json={
                "provider": self.image_provider,
                "prompt": params["prompt"],
                "negative_prompt": params.get("negative_prompt"),
                "style": params.get("style"),
                "aspect_ratio": params.get("aspect_ratio", "1:1"),
                "quality": params.get("quality", "standard"),
                "num_variations": params.get("num_variations", 1),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "status": "generation_requested",
            "prompt": params["prompt"],
            "provider": self.image_provider,
            "instruction": "Generate image using the specified prompt and settings.",
        }

    async def _generate_from_moodboard(self, params: dict) -> dict:
        """Generate image from moodboard style."""
        # Get moodboard first
        moodboard = await self._get_moodboard({"moodboard_id": params["moodboard_id"]})
        style_analysis = await self._analyze_moodboard({
            "moodboard_id": params["moodboard_id"],
            "extract": ["colors", "mood", "style", "lighting"],
        })

        return {
            "status": "ready_to_generate",
            "moodboard": moodboard,
            "style_analysis": style_analysis,
            "subject": params["subject"],
            "additional_guidance": params.get("additional_guidance"),
            "aspect_ratio": params.get("aspect_ratio", "1:1"),
            "num_variations": params.get("num_variations", 1),
            "provider": self.image_provider,
            "instruction": "Generate image matching the moodboard style for the specified subject.",
        }

    async def _get_moodboard(self, params: dict) -> dict:
        """Fetch moodboard."""
        moodboard_id = params.get("moodboard_id")
        project_id = params.get("project_id")

        if moodboard_id:
            response = await self.http_client.get(f"/api/v1/studio/moodboards/{moodboard_id}")
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
            params={"extract": ",".join(params.get("extract", ["colors", "mood", "style"]))},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "moodboard_id": params["moodboard_id"],
            "instruction": "Analyze the moodboard to extract visual style attributes.",
        }

    async def _upscale_image(self, params: dict) -> dict:
        """Upscale image."""
        response = await self.http_client.post(
            "/api/v1/studio/images/upscale",
            json={
                "image_id": params.get("image_id"),
                "image_url": params.get("image_url"),
                "scale_factor": params.get("scale_factor", 2),
                "enhance": params.get("enhance", True),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Upscale failed"}

    async def _style_transfer(self, params: dict) -> dict:
        """Apply style transfer."""
        response = await self.http_client.post(
            "/api/v1/studio/images/style-transfer",
            json={
                "content_image_id": params["content_image_id"],
                "style_image_id": params.get("style_image_id"),
                "moodboard_id": params.get("moodboard_id"),
                "strength": params.get("strength", 0.7),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Style transfer failed"}

    async def _get_brand_visuals(self, params: dict) -> dict:
        """Get brand visual guidelines."""
        client_id = params.get("client_id") or self.client_specific_id
        if client_id:
            response = await self.http_client.get(
                f"/api/v1/brand/visuals",
                params={
                    "client_id": client_id,
                    "include_palette": params.get("include_palette", True),
                    "include_examples": params.get("include_examples", True),
                },
            )
            if response.status_code == 200:
                return response.json()
        return {
            "visuals": {
                "primary_colors": ["#000000", "#FFFFFF"],
                "style": "modern and clean",
            },
            "note": "Using default brand visuals",
        }

    async def _apply_brand_style(self, params: dict) -> dict:
        """Apply brand style to image."""
        brand_visuals = await self._get_brand_visuals({"client_id": params.get("client_id")})
        return {
            "image_id": params["image_id"],
            "brand_visuals": brand_visuals,
            "adjustments": params.get("adjustments", ["colors"]),
            "instruction": "Adjust the image to match brand visual guidelines.",
        }

    async def _save_to_dam(self, params: dict) -> dict:
        """Save image to DAM."""
        response = await self.http_client.post(
            "/api/v1/dam/images",
            json={
                "image_data": params.get("image_data"),
                "filename": params.get("filename"),
                "title": params["title"],
                "tags": params.get("tags", []),
                "project_id": params.get("project_id"),
                "client_id": params.get("client_id") or self.client_specific_id,
                "metadata": params.get("metadata", {}),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to save to DAM"}

    async def _get_from_dam(self, params: dict) -> dict:
        """Get image from DAM."""
        if params.get("image_id"):
            response = await self.http_client.get(f"/api/v1/dam/images/{params['image_id']}")
        else:
            response = await self.http_client.get(
                "/api/v1/dam/images",
                params={
                    "query": params.get("search_query"),
                    "tags": ",".join(params.get("tags", [])),
                    "project_id": params.get("project_id"),
                    "limit": params.get("limit", 10),
                },
            )
        if response.status_code == 200:
            return response.json()
        return {"images": [], "note": "No images found"}

    async def _create_variations(self, params: dict) -> dict:
        """Create image variations."""
        response = await self.http_client.post(
            "/api/v1/studio/images/variations",
            json={
                "image_id": params["image_id"],
                "variation_type": params.get("variation_type", "all"),
                "num_variations": params.get("num_variations", 3),
                "provider": self.image_provider,
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to create variations"}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
