from typing import Any
import httpx
from .base import BaseAgent


class VideoScriptAgent(BaseAgent):
    """
    Agent for generating video scripts.

    Capabilities:
    - Generate scripts from briefs
    - Create multiple script versions
    - Adapt scripts for different formats (social, commercial, long-form)
    - Apply brand voice and tone
    - Generate shot descriptions
    - Handle multi-language scripts
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        language: str = "en",
        client_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.language = language
        self.client_specific_id = client_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return f"video_script_agent_{self.language}"

    @property
    def system_prompt(self) -> str:
        base_prompt = """You are an expert video scriptwriter specializing in commercial and brand content.

Your role is to create compelling video scripts that:
1. Hook viewers in the first 3 seconds
2. Tell a clear, emotionally resonant story
3. Match the brand voice and tone
4. Work within the specified duration
5. Guide visual direction through shot descriptions

Script formats you handle:
- Social media (6s, 15s, 30s, 60s)
- TV commercials (15s, 30s, 60s)
- YouTube pre-roll (6s, 15s)
- Brand films (2-5 min)
- Explainer videos
- Testimonials/interviews
- Product demos

Script elements to include:
- Scene/shot numbers
- Visual descriptions
- Dialogue/voiceover
- On-screen text (supers)
- Sound/music notes
- Duration markers"""

        if self.language == "ar":
            base_prompt += """

Arabic Script Considerations:
- RTL text formatting
- Cultural nuances and expressions
- Arabic wordplay and rhythm
- Regional dialect awareness (Gulf, Levantine, Egyptian)
- Formal vs colloquial Arabic based on audience"""

        if self.language != "en":
            base_prompt += f"\n\nPrimary language: {self.language}"
        if self.client_specific_id:
            base_prompt += f"\n\nApply client-specific brand voice for client: {self.client_specific_id}"

        return base_prompt

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_script",
                "description": "Generate a complete video script from a brief or concept.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief ID to generate script from",
                        },
                        "concept": {
                            "type": "string",
                            "description": "Concept/idea if no brief provided",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["social", "tv", "youtube", "brand_film", "explainer", "testimonial", "demo"],
                            "description": "Video format type",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Target duration in seconds",
                        },
                        "tone": {
                            "type": "string",
                            "description": "Desired tone (energetic, emotional, professional, etc.)",
                        },
                        "moodboard_id": {
                            "type": "string",
                            "description": "Moodboard for style reference",
                        },
                    },
                    "required": ["format", "duration"],
                },
            },
            {
                "name": "generate_variations",
                "description": "Generate multiple script variations for A/B testing.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script_id": {
                            "type": "string",
                            "description": "Base script to create variations from",
                        },
                        "num_variations": {
                            "type": "integer",
                            "description": "Number of variations to generate",
                            "default": 3,
                        },
                        "variation_type": {
                            "type": "string",
                            "enum": ["hook", "cta", "tone", "structure", "full"],
                            "description": "What to vary",
                        },
                    },
                    "required": ["script_id", "variation_type"],
                },
            },
            {
                "name": "adapt_duration",
                "description": "Adapt a script to a different duration.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script_id": {
                            "type": "string",
                            "description": "Script to adapt",
                        },
                        "target_duration": {
                            "type": "integer",
                            "description": "New target duration in seconds",
                        },
                        "preserve": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Elements to preserve (hook, cta, key_message)",
                        },
                    },
                    "required": ["script_id", "target_duration"],
                },
            },
            {
                "name": "get_brand_voice",
                "description": "Retrieve brand voice guidelines for script writing.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {
                            "type": "string",
                            "description": "Client ID for brand voice",
                        },
                        "content_type": {
                            "type": "string",
                            "enum": ["video", "social", "corporate"],
                            "description": "Type of content",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_moodboard",
                "description": "Fetch a moodboard for tone/style reference.",
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
                "name": "translate_script",
                "description": "Translate script to another language with cultural adaptation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script_id": {
                            "type": "string",
                            "description": "Script to translate",
                        },
                        "target_language": {
                            "type": "string",
                            "description": "Target language code",
                        },
                        "adapt_cultural": {
                            "type": "boolean",
                            "description": "Adapt cultural references",
                            "default": True,
                        },
                    },
                    "required": ["script_id", "target_language"],
                },
            },
            {
                "name": "save_script",
                "description": "Save script to project/DAM.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script_id": {
                            "type": "string",
                            "description": "Script ID if updating",
                        },
                        "title": {"type": "string"},
                        "content": {
                            "type": "object",
                            "description": "Script content with scenes",
                        },
                        "project_id": {"type": "string"},
                        "client_id": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["draft", "review", "approved", "production"],
                            "default": "draft",
                        },
                    },
                    "required": ["title", "content"],
                },
            },
            {
                "name": "get_brief",
                "description": "Retrieve brief details for script generation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief ID to fetch",
                        },
                    },
                    "required": ["brief_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "generate_script":
                return await self._generate_script(tool_input)
            elif tool_name == "generate_variations":
                return await self._generate_variations(tool_input)
            elif tool_name == "adapt_duration":
                return await self._adapt_duration(tool_input)
            elif tool_name == "get_brand_voice":
                return await self._get_brand_voice(tool_input)
            elif tool_name == "get_moodboard":
                return await self._get_moodboard(tool_input)
            elif tool_name == "translate_script":
                return await self._translate_script(tool_input)
            elif tool_name == "save_script":
                return await self._save_script(tool_input)
            elif tool_name == "get_brief":
                return await self._get_brief(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _generate_script(self, params: dict) -> dict:
        """Generate a video script."""
        brief_context = ""
        if params.get("brief_id"):
            response = await self.http_client.get(f"/api/v1/briefs/{params['brief_id']}")
            if response.status_code == 200:
                brief_context = response.json()

        moodboard_context = None
        if params.get("moodboard_id"):
            response = await self.http_client.get(
                f"/api/v1/studio/moodboards/{params['moodboard_id']}"
            )
            if response.status_code == 200:
                moodboard_context = response.json()

        return {
            "status": "ready_to_generate",
            "brief": brief_context,
            "concept": params.get("concept"),
            "format": params["format"],
            "duration": params["duration"],
            "tone": params.get("tone"),
            "moodboard": moodboard_context,
            "language": self.language,
            "instruction": f"Generate a {params['duration']}s {params['format']} video script.",
        }

    async def _generate_variations(self, params: dict) -> dict:
        """Generate script variations."""
        response = await self.http_client.get(
            f"/api/v1/studio/scripts/{params['script_id']}"
        )
        base_script = response.json() if response.status_code == 200 else None

        return {
            "status": "ready_to_generate",
            "base_script": base_script,
            "num_variations": params.get("num_variations", 3),
            "variation_type": params["variation_type"],
            "instruction": f"Generate {params.get('num_variations', 3)} variations focusing on {params['variation_type']}.",
        }

    async def _adapt_duration(self, params: dict) -> dict:
        """Adapt script to new duration."""
        response = await self.http_client.get(
            f"/api/v1/studio/scripts/{params['script_id']}"
        )
        script = response.json() if response.status_code == 200 else None

        return {
            "status": "ready_to_adapt",
            "script": script,
            "target_duration": params["target_duration"],
            "preserve": params.get("preserve", ["hook", "cta"]),
            "instruction": f"Adapt script to {params['target_duration']}s while preserving key elements.",
        }

    async def _get_brand_voice(self, params: dict) -> dict:
        """Get brand voice guidelines."""
        response = await self.http_client.get(
            "/api/v1/brand/voice",
            params={
                "client_id": params.get("client_id") or self.client_specific_id,
                "content_type": params.get("content_type", "video"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"voice": None, "note": "Using default voice guidelines"}

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

    async def _translate_script(self, params: dict) -> dict:
        """Translate script."""
        response = await self.http_client.get(
            f"/api/v1/studio/scripts/{params['script_id']}"
        )
        script = response.json() if response.status_code == 200 else None

        return {
            "status": "ready_to_translate",
            "script": script,
            "target_language": params["target_language"],
            "adapt_cultural": params.get("adapt_cultural", True),
            "instruction": f"Translate script to {params['target_language']} with cultural adaptation.",
        }

    async def _save_script(self, params: dict) -> dict:
        """Save script to studio."""
        response = await self.http_client.post(
            "/api/v1/studio/scripts",
            json={
                "title": params["title"],
                "content": params["content"],
                "project_id": params.get("project_id"),
                "client_id": params.get("client_id") or self.client_specific_id,
                "status": params.get("status", "draft"),
                "language": self.language,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to save script"}

    async def _get_brief(self, params: dict) -> dict:
        """Get brief details."""
        response = await self.http_client.get(f"/api/v1/briefs/{params['brief_id']}")
        if response.status_code == 200:
            return response.json()
        return {"error": "Brief not found"}

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
