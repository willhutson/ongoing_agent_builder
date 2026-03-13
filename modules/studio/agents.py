"""
Studio Module Agents — Image, VideoScript, VideoStoryboard, VideoProduction, Presentation.

Media generation and creative production. API-heavy, potentially GPU-bound.
"""

from typing import Any
from shared.base_agent import BaseAgent
from shared.openrouter import OpenRouterClient
from shared.config import BaseModuleSettings, get_model_id


class ImageAgent(BaseAgent):
    """AI image generation — prompts, style transfer, brand consistency."""

    @property
    def name(self) -> str:
        return "image"

    @property
    def system_prompt(self) -> str:
        return """You are an expert visual designer and AI image generation specialist.

Create compelling visual assets by:
- Crafting effective prompts for AI image generation
- Maintaining brand consistency across visuals
- Understanding composition, color, and visual hierarchy
- Specifying aspect ratios and resolution for intended use (social, print, web)

Image types: hero images, social graphics, product vis, lifestyle, illustrations, backgrounds."""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_image",
                "description": "Generate an image from a text prompt.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Detailed image prompt"},
                        "negative_prompt": {"type": "string"},
                        "style": {"type": "string", "enum": ["photorealistic", "illustration", "3d_render", "digital_art", "watercolor", "minimalist"]},
                        "aspect_ratio": {"type": "string", "enum": ["1:1", "16:9", "9:16", "4:3"], "default": "1:1"},
                        "quality": {"type": "string", "enum": ["draft", "standard", "hd"], "default": "standard"},
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "create_variations",
                "description": "Create style variations of an image concept.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "base_prompt": {"type": "string"},
                        "variation_type": {"type": "string", "enum": ["color", "composition", "style", "mood"]},
                        "count": {"type": "integer", "default": 3},
                    },
                    "required": ["base_prompt"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "generate_image":
            return {"status": "prompt_ready", "spec": tool_input, "instruction": "Image generation prompt crafted."}
        elif tool_name == "create_variations":
            return {"status": "ready", "spec": tool_input}
        return {"error": f"Unknown tool: {tool_name}"}


class VideoScriptAgent(BaseAgent):
    """Video scripts, dialogue, and screenplay writing."""

    @property
    def name(self) -> str:
        return "video_script"

    @property
    def system_prompt(self) -> str:
        return """You are an expert video scriptwriter.

Write compelling video scripts for:
- Social media (15s, 30s, 60s formats)
- Explainer videos and tutorials
- Brand stories and commercials
- Product demos and walkthroughs
- Testimonial frameworks

Include: scene descriptions, dialogue, voiceover, timing, and visual cues."""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "write_script",
                "description": "Write a video script.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string", "enum": ["social_short", "social_long", "explainer", "commercial", "demo", "testimonial"]},
                        "duration_seconds": {"type": "integer"},
                        "topic": {"type": "string"},
                        "tone": {"type": "string"},
                        "key_messages": {"type": "array", "items": {"type": "string"}},
                        "cta": {"type": "string"},
                    },
                    "required": ["format", "topic"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input, "instruction": "Write the script now."}


class VideoStoryboardAgent(BaseAgent):
    """Shot planning and visual storytelling."""

    @property
    def name(self) -> str:
        return "video_storyboard"

    @property
    def system_prompt(self) -> str:
        return """You are an expert storyboard artist and visual planner.

Create detailed storyboards with:
- Shot-by-shot breakdowns with framing and composition
- Camera movements and transitions
- Visual references and mood
- Timing and pacing notes
- Audio/music cues per shot"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_storyboard",
                "description": "Create a shot-by-shot storyboard.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script": {"type": "string", "description": "Video script to storyboard"},
                        "style": {"type": "string", "enum": ["cinematic", "documentary", "animation", "social_media"]},
                        "shots_per_scene": {"type": "integer", "default": 3},
                    },
                    "required": ["script"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input, "instruction": "Create the storyboard."}


class VideoProductionAgent(BaseAgent):
    """Video production guidance, direction, and AI video generation."""

    @property
    def name(self) -> str:
        return "video_production"

    @property
    def system_prompt(self) -> str:
        return """You are a video production director and AI video specialist.

Guide video production from concept to final cut:
- AI video generation prompting (Sora, Runway, Kling)
- Production planning and shot lists
- Editing guidance and pacing
- Color grading and visual consistency
- Audio/music selection and mixing"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_video",
                "description": "Generate AI video from a prompt.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "duration_seconds": {"type": "integer", "default": 5},
                        "style": {"type": "string"},
                        "aspect_ratio": {"type": "string", "enum": ["16:9", "9:16", "1:1"]},
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "create_shot_list",
                "description": "Create a detailed production shot list.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script": {"type": "string"},
                        "location": {"type": "string"},
                        "equipment": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["script"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input}


class PresentationAgent(BaseAgent):
    """Deck generation and presentation design."""

    @property
    def name(self) -> str:
        return "presentation"

    @property
    def system_prompt(self) -> str:
        return """You are an expert presentation designer.

Create compelling presentations:
- Slide structure and narrative flow
- Key message hierarchy per slide
- Visual layout recommendations
- Data visualization guidance
- Speaker notes and talking points

Formats: pitch decks, client presentations, internal reports, training materials."""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_deck",
                "description": "Create a presentation deck outline with content.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "purpose": {"type": "string", "enum": ["pitch", "report", "training", "proposal", "review"]},
                        "slide_count": {"type": "integer"},
                        "key_messages": {"type": "array", "items": {"type": "string"}},
                        "audience": {"type": "string"},
                    },
                    "required": ["title", "purpose"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        return {"status": "ready", "spec": tool_input, "instruction": "Build the deck."}


def create_agents(llm: OpenRouterClient, settings: BaseModuleSettings) -> dict[str, BaseAgent]:
    model = get_model_id(settings, "standard")
    return {
        "image": ImageAgent(llm, model),
        "video_script": VideoScriptAgent(llm, model),
        "video_storyboard": VideoStoryboardAgent(llm, model),
        "video_production": VideoProductionAgent(llm, model),
        "presentation": PresentationAgent(llm, model),
    }
