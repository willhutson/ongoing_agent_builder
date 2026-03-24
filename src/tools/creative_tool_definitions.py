"""
Creative Tool Definitions — OpenAI function-format tools for
AI-powered creative asset generation (images, video, voice,
presentations, video compositions).

Selectively injected into agents via AGENT_CREATIVE_TOOL_MAP.
"""


CREATIVE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": (
                "Generate an image from a text prompt or reference image. "
                "Returns one or more image URLs. Quality tier controls "
                "cost/quality tradeoff (draft=$0.003, standard=$0.02, premium=$0.05)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Image generation prompt"},
                    "quality_tier": {
                        "type": "string",
                        "enum": ["draft", "standard", "premium"],
                        "default": "standard",
                    },
                    "resolution": {
                        "type": "string",
                        "description": "Image size e.g. '1024x1024', '1024x1536'",
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "description": "Aspect ratio e.g. '1:1', '16:9', '9:16'",
                    },
                    "reference_image_url": {
                        "type": "string",
                        "description": "URL of a reference image for style transfer / image-to-image",
                    },
                    "num_variants": {
                        "type": "integer",
                        "description": "Number of image variants to generate",
                        "default": 1,
                    },
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_video",
            "description": (
                "Generate a short video from a text prompt or reference image. "
                "Returns a video URL. Duration 3-10 seconds. "
                "Cost: draft=$0.30, standard=$0.50, premium=$1.00."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Video generation prompt"},
                    "quality_tier": {
                        "type": "string",
                        "enum": ["draft", "standard", "premium"],
                        "default": "standard",
                    },
                    "duration_seconds": {
                        "type": "integer",
                        "description": "Video duration (3-10 seconds)",
                        "default": 5,
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "description": "Aspect ratio: '16:9', '9:16', '1:1'",
                        "default": "16:9",
                    },
                    "reference_image_url": {
                        "type": "string",
                        "description": "Reference image for image-to-video generation",
                    },
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_voiceover",
            "description": (
                "Generate a voiceover audio file from text. "
                "Returns an audio URL. "
                "Draft uses OpenAI TTS ($0.003), standard/premium use ElevenLabs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert to speech"},
                    "quality_tier": {
                        "type": "string",
                        "enum": ["draft", "standard", "premium"],
                        "default": "standard",
                    },
                    "voice_id": {
                        "type": "string",
                        "description": "Voice ID (provider-specific). Omit for default voice.",
                    },
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_presentation",
            "description": (
                "Generate a presentation deck from a description. "
                "Returns an editor URL or structured JSON spec. "
                "Uses Beautiful.ai with fallback to ERP's internal renderer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Presentation topic/description"},
                    "num_slides": {
                        "type": "integer",
                        "description": "Number of slides to generate",
                        "default": 10,
                    },
                    "style": {
                        "type": "string",
                        "description": "Presentation style: corporate, startup, creative, minimal",
                    },
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_video_composition",
            "description": (
                "Create a Remotion video composition spec (JSON) describing scenes, "
                "text overlays, animations, and asset references. The ERP's Remotion "
                "renderer will turn this into a real MP4. Use generate_image and "
                "generate_voiceover first to get asset URLs for scenes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "scenes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "duration_seconds": {"type": "number"},
                                "background": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["image", "video", "color"]},
                                        "url": {"type": "string"},
                                        "color": {"type": "string"},
                                    },
                                },
                                "text_overlays": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "text": {"type": "string"},
                                            "position": {"type": "string"},
                                            "style": {"type": "string"},
                                        },
                                    },
                                },
                                "animation": {"type": "string"},
                                "voiceover_url": {"type": "string"},
                            },
                        },
                    },
                    "music_url": {"type": "string", "description": "Background music URL"},
                    "aspect_ratio": {
                        "type": "string",
                        "description": "Output aspect ratio: '16:9', '9:16', '1:1'",
                        "default": "16:9",
                    },
                    "brand": {
                        "type": "object",
                        "properties": {
                            "logo_url": {"type": "string"},
                            "primary_color": {"type": "string"},
                            "font": {"type": "string"},
                        },
                    },
                },
                "required": ["scenes"],
            },
        },
    },
]


# ══════════════════════════════════════════════════════════════
# AGENT → CREATIVE TOOL MAPPING
# ══════════════════════════════════════════════════════════════

AGENT_CREATIVE_TOOL_MAP: dict[str, list[str]] = {
    # Studio
    "image": ["generate_image"],
    "brand_visual": ["generate_image"],
    "copy": ["generate_image"],
    "presentation": ["generate_presentation", "generate_image"],
    # Video pipeline
    "video_script": ["generate_voiceover"],
    "video_storyboard": ["generate_image", "generate_video"],
    "video_production": [
        "generate_image", "generate_video", "generate_voiceover",
        "generate_video_composition",
    ],
    # Content / Social
    "content": ["generate_image"],
    "community": ["generate_image"],
    "social_listening": ["generate_image"],
    "publisher": ["generate_image", "generate_video"],
}

# Set of all creative tool names for fast lookup in BaseAgent
CREATIVE_TOOL_NAMES = {t["function"]["name"] for t in CREATIVE_TOOLS}
