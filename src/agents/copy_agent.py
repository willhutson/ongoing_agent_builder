from typing import Any
import httpx
from .base import BaseAgent


class CopyAgent(BaseAgent):
    """
    Agent for generating written content with brand voice.

    Specializable by language: en, ar, fr, etc.

    Capabilities:
    - Headlines and taglines
    - Body copy (long-form)
    - Social media copy (platform-specific)
    - Email copy (sequences, campaigns)
    - Website copy (pages, UX copy)
    - Scripts (video, audio, animation)
    - Brand voice application
    - Revision workflows
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
            timeout=30.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return f"copy_agent_{self.language}"

    @property
    def system_prompt(self) -> str:
        base_prompt = """You are an expert copywriter and content strategist.

Your role is to create compelling, on-brand written content by:
1. Understanding the brand voice and tone
2. Writing for the target audience
3. Adapting style to the medium/platform
4. Creating clear, engaging, action-driving copy
5. Following best practices for each content type

Content types you excel at:
- Headlines & taglines: Punchy, memorable, benefit-driven
- Body copy: Clear, scannable, persuasive
- Social media: Platform-native, engaging, shareable
- Email: Subject lines that open, copy that converts
- Website: SEO-friendly, user-focused, conversion-optimized
- Scripts: Natural dialogue, clear direction, emotional beats

Writing principles:
- Lead with benefits, not features
- Use active voice
- Keep sentences concise
- Include clear CTAs
- Match the audience's language level
- Test multiple variations"""

        if self.language == "ar":
            base_prompt += """

ARABIC LANGUAGE SPECIALIZATION:
- Write in Modern Standard Arabic or Gulf dialect as appropriate
- Ensure proper RTL formatting
- Apply Arabic typography best practices
- Consider cultural nuances and sensitivities
- Use appropriate formality levels
- Localize idioms and expressions appropriately"""
        elif self.language == "fr":
            base_prompt += """

FRENCH LANGUAGE SPECIALIZATION:
- Write in appropriate French register (formal/informal)
- Consider regional variations (France, Canada, etc.)
- Apply French grammar and style conventions
- Localize cultural references appropriately"""

        if self.client_specific_id:
            base_prompt += f"\n\nApply client-specific brand voice for client: {self.client_specific_id}"

        return base_prompt

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_headline",
                "description": "Generate headlines or taglines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic or product to write about",
                        },
                        "style": {
                            "type": "string",
                            "enum": ["punchy", "emotional", "benefit-driven", "question", "how-to", "news"],
                            "description": "Headline style",
                        },
                        "num_variations": {
                            "type": "integer",
                            "description": "Number of variations to generate",
                            "default": 5,
                        },
                        "max_length": {
                            "type": "integer",
                            "description": "Maximum character length",
                        },
                        "include_subheadline": {
                            "type": "boolean",
                            "default": False,
                        },
                    },
                    "required": ["topic"],
                },
            },
            {
                "name": "generate_body_copy",
                "description": "Generate long-form body copy.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "purpose": {
                            "type": "string",
                            "enum": ["inform", "persuade", "entertain", "educate"],
                        },
                        "length": {
                            "type": "string",
                            "enum": ["short", "medium", "long"],
                            "description": "Approximate length",
                        },
                        "key_points": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key points to cover",
                        },
                        "tone": {
                            "type": "string",
                            "enum": ["formal", "casual", "professional", "friendly", "authoritative"],
                        },
                        "include_cta": {
                            "type": "boolean",
                            "default": True,
                        },
                    },
                    "required": ["topic"],
                },
            },
            {
                "name": "generate_social_copy",
                "description": "Generate social media copy for specific platforms.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "enum": ["instagram", "twitter", "linkedin", "facebook", "tiktok", "threads"],
                        },
                        "content_type": {
                            "type": "string",
                            "enum": ["post", "story", "reel_caption", "carousel", "ad"],
                        },
                        "topic": {"type": "string"},
                        "include_hashtags": {
                            "type": "boolean",
                            "default": True,
                        },
                        "include_emoji": {
                            "type": "boolean",
                            "default": True,
                        },
                        "num_variations": {
                            "type": "integer",
                            "default": 3,
                        },
                        "cta": {
                            "type": "string",
                            "description": "Call to action to include",
                        },
                    },
                    "required": ["platform", "topic"],
                },
            },
            {
                "name": "generate_email_copy",
                "description": "Generate email copy.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "email_type": {
                            "type": "string",
                            "enum": ["newsletter", "promotional", "transactional", "welcome", "nurture", "cold_outreach"],
                        },
                        "subject_lines": {
                            "type": "integer",
                            "description": "Number of subject line variations",
                            "default": 3,
                        },
                        "topic": {"type": "string"},
                        "cta": {"type": "string"},
                        "preview_text": {
                            "type": "boolean",
                            "description": "Include preview text",
                            "default": True,
                        },
                        "personalization": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Personalization fields to use",
                        },
                    },
                    "required": ["email_type", "topic"],
                },
            },
            {
                "name": "generate_website_copy",
                "description": "Generate website copy.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "page_type": {
                            "type": "string",
                            "enum": ["homepage", "about", "services", "product", "landing", "contact", "faq"],
                        },
                        "sections": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Sections to write (hero, features, benefits, etc.)",
                        },
                        "seo_keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Keywords to incorporate",
                        },
                        "topic": {"type": "string"},
                        "include_meta": {
                            "type": "boolean",
                            "description": "Include meta title/description",
                            "default": True,
                        },
                    },
                    "required": ["page_type"],
                },
            },
            {
                "name": "generate_script",
                "description": "Generate video/audio script.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script_type": {
                            "type": "string",
                            "enum": ["video", "animation", "podcast", "radio", "voiceover"],
                        },
                        "duration_seconds": {
                            "type": "integer",
                            "description": "Target duration in seconds",
                        },
                        "topic": {"type": "string"},
                        "tone": {
                            "type": "string",
                            "enum": ["conversational", "professional", "energetic", "calm", "dramatic"],
                        },
                        "include_directions": {
                            "type": "boolean",
                            "description": "Include visual/audio directions",
                            "default": True,
                        },
                        "speakers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Speaker names/roles",
                        },
                    },
                    "required": ["script_type", "topic"],
                },
            },
            {
                "name": "get_brand_voice",
                "description": "Fetch brand voice guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "include_examples": {
                            "type": "boolean",
                            "default": True,
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "apply_brand_voice",
                "description": "Rewrite copy to match brand voice.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "copy": {
                            "type": "string",
                            "description": "Copy to rewrite",
                        },
                        "client_id": {"type": "string"},
                        "voice_attributes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Voice attributes to apply",
                        },
                    },
                    "required": ["copy"],
                },
            },
            {
                "name": "create_revision",
                "description": "Create a revision of existing copy based on feedback.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "original_copy": {"type": "string"},
                        "feedback": {"type": "string"},
                        "revision_type": {
                            "type": "string",
                            "enum": ["minor_edit", "rewrite", "tone_shift", "shorten", "expand"],
                        },
                    },
                    "required": ["original_copy", "feedback"],
                },
            },
            {
                "name": "save_copy",
                "description": "Save copy to content library.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "copy_type": {
                            "type": "string",
                            "enum": ["headline", "body", "social", "email", "website", "script"],
                        },
                        "content": {"type": "string"},
                        "variations": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "project_id": {"type": "string"},
                        "client_id": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["draft", "review", "approved"],
                            "default": "draft",
                        },
                        "language": {"type": "string"},
                    },
                    "required": ["title", "copy_type", "content"],
                },
            },
            {
                "name": "get_moodboard",
                "description": "Fetch moodboard for tone/voice inspiration.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "moodboard_id": {"type": "string"},
                        "project_id": {"type": "string"},
                    },
                    "required": [],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "generate_headline":
                return await self._generate_headline(tool_input)
            elif tool_name == "generate_body_copy":
                return await self._generate_body_copy(tool_input)
            elif tool_name == "generate_social_copy":
                return await self._generate_social_copy(tool_input)
            elif tool_name == "generate_email_copy":
                return await self._generate_email_copy(tool_input)
            elif tool_name == "generate_website_copy":
                return await self._generate_website_copy(tool_input)
            elif tool_name == "generate_script":
                return await self._generate_script(tool_input)
            elif tool_name == "get_brand_voice":
                return await self._get_brand_voice(tool_input)
            elif tool_name == "apply_brand_voice":
                return await self._apply_brand_voice(tool_input)
            elif tool_name == "create_revision":
                return await self._create_revision(tool_input)
            elif tool_name == "save_copy":
                return await self._save_copy(tool_input)
            elif tool_name == "get_moodboard":
                return await self._get_moodboard(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _generate_headline(self, params: dict) -> dict:
        """Generate headlines."""
        brand_voice = await self._get_brand_voice({"client_id": self.client_specific_id})
        return {
            "status": "ready_to_generate",
            "topic": params["topic"],
            "style": params.get("style", "benefit-driven"),
            "num_variations": params.get("num_variations", 5),
            "max_length": params.get("max_length"),
            "include_subheadline": params.get("include_subheadline", False),
            "brand_voice": brand_voice,
            "language": self.language,
            "instruction": f"Generate {params.get('num_variations', 5)} headline variations in {self.language}.",
        }

    async def _generate_body_copy(self, params: dict) -> dict:
        """Generate body copy."""
        brand_voice = await self._get_brand_voice({"client_id": self.client_specific_id})
        return {
            "status": "ready_to_generate",
            "topic": params["topic"],
            "purpose": params.get("purpose", "inform"),
            "length": params.get("length", "medium"),
            "key_points": params.get("key_points", []),
            "tone": params.get("tone", "professional"),
            "include_cta": params.get("include_cta", True),
            "brand_voice": brand_voice,
            "language": self.language,
            "instruction": f"Generate body copy in {self.language}.",
        }

    async def _generate_social_copy(self, params: dict) -> dict:
        """Generate social media copy."""
        brand_voice = await self._get_brand_voice({"client_id": self.client_specific_id})
        return {
            "status": "ready_to_generate",
            "platform": params["platform"],
            "content_type": params.get("content_type", "post"),
            "topic": params["topic"],
            "include_hashtags": params.get("include_hashtags", True),
            "include_emoji": params.get("include_emoji", True),
            "num_variations": params.get("num_variations", 3),
            "cta": params.get("cta"),
            "brand_voice": brand_voice,
            "language": self.language,
            "instruction": f"Generate {params['platform']} copy in {self.language}.",
        }

    async def _generate_email_copy(self, params: dict) -> dict:
        """Generate email copy."""
        brand_voice = await self._get_brand_voice({"client_id": self.client_specific_id})
        return {
            "status": "ready_to_generate",
            "email_type": params["email_type"],
            "topic": params["topic"],
            "subject_lines": params.get("subject_lines", 3),
            "cta": params.get("cta"),
            "preview_text": params.get("preview_text", True),
            "personalization": params.get("personalization", []),
            "brand_voice": brand_voice,
            "language": self.language,
            "instruction": f"Generate {params['email_type']} email in {self.language}.",
        }

    async def _generate_website_copy(self, params: dict) -> dict:
        """Generate website copy."""
        brand_voice = await self._get_brand_voice({"client_id": self.client_specific_id})
        return {
            "status": "ready_to_generate",
            "page_type": params["page_type"],
            "sections": params.get("sections", []),
            "seo_keywords": params.get("seo_keywords", []),
            "topic": params.get("topic"),
            "include_meta": params.get("include_meta", True),
            "brand_voice": brand_voice,
            "language": self.language,
            "instruction": f"Generate {params['page_type']} page copy in {self.language}.",
        }

    async def _generate_script(self, params: dict) -> dict:
        """Generate script."""
        brand_voice = await self._get_brand_voice({"client_id": self.client_specific_id})
        return {
            "status": "ready_to_generate",
            "script_type": params["script_type"],
            "duration_seconds": params.get("duration_seconds"),
            "topic": params["topic"],
            "tone": params.get("tone", "conversational"),
            "include_directions": params.get("include_directions", True),
            "speakers": params.get("speakers", []),
            "brand_voice": brand_voice,
            "language": self.language,
            "instruction": f"Generate {params['script_type']} script in {self.language}.",
        }

    async def _get_brand_voice(self, params: dict) -> dict:
        """Get brand voice guidelines."""
        client_id = params.get("client_id") or self.client_specific_id
        if client_id:
            response = await self.http_client.get(
                f"/api/v1/brand/voice",
                params={
                    "client_id": client_id,
                    "include_examples": params.get("include_examples", True),
                },
            )
            if response.status_code == 200:
                return response.json()
        return {
            "voice": {
                "tone": "professional yet approachable",
                "style": "clear and concise",
                "personality": "confident and helpful",
            },
            "note": "Using default brand voice",
        }

    async def _apply_brand_voice(self, params: dict) -> dict:
        """Rewrite copy with brand voice."""
        brand_voice = await self._get_brand_voice({"client_id": params.get("client_id")})
        return {
            "original_copy": params["copy"],
            "brand_voice": brand_voice,
            "voice_attributes": params.get("voice_attributes", []),
            "language": self.language,
            "instruction": "Rewrite the copy to match the brand voice guidelines.",
        }

    async def _create_revision(self, params: dict) -> dict:
        """Create a revision based on feedback."""
        return {
            "original_copy": params["original_copy"],
            "feedback": params["feedback"],
            "revision_type": params.get("revision_type", "minor_edit"),
            "language": self.language,
            "instruction": f"Create a {params.get('revision_type', 'minor_edit')} revision based on the feedback.",
        }

    async def _save_copy(self, params: dict) -> dict:
        """Save copy to content library."""
        response = await self.http_client.post(
            "/api/v1/content/copy",
            json={
                "title": params["title"],
                "copy_type": params["copy_type"],
                "content": params["content"],
                "variations": params.get("variations", []),
                "project_id": params.get("project_id"),
                "client_id": params.get("client_id") or self.client_specific_id,
                "status": params.get("status", "draft"),
                "language": params.get("language") or self.language,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to save copy"}

    async def _get_moodboard(self, params: dict) -> dict:
        """Fetch moodboard for tone inspiration."""
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

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
