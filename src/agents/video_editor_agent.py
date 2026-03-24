from typing import Any
import httpx
from .base import BaseAgent


class VideoEditorAgent(BaseAgent):
    """
    Builds and edits video compositions for the Video Studio module.

    Capabilities:
    - Populate a template with content (images, text, timing)
    - Convert a brief/script into a full composition spec
    - Edit individual scenes (change text, swap images, adjust timing)
    - Generate missing assets inline (images, voiceover, music)
    - Optimize timing and pacing based on voiceover duration

    This agent returns video_composition artifacts that the ERP renders via Remotion.
    """

    def __init__(self, client, model: str, erp_base_url: str = "",
                 erp_api_key: str = "", **kwargs):
        super().__init__(client, model, erp_base_url=erp_base_url,
                         erp_api_key=erp_api_key, **kwargs)

    @property
    def name(self) -> str:
        return "video_editor_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a professional video editor and motion designer.

You build video compositions as structured JSON specs that get rendered into
real MP4 videos. You understand timing, pacing, visual hierarchy, and storytelling.

AVAILABLE TEMPLATES:
- news: Headline → story images (ken burns) → key quote → end card
- press_release: Company announcement → key facts → supporting visual → CTA
- product_demo: Product intro → feature callouts (3) → demo clip → pricing/CTA
- talking_head: Title card → interview video with lower third + subtitles → end card
- reaction: Title → split-screen (original + reaction) → end card
- blank: Empty canvas, build from scratch

SCENE TYPES: image, video, split-screen, title, lower-third, ken-burns, text-only, transition

ANIMATIONS: none, fade-in, slide-up, slide-left, typewriter, bounce, scale-in

TRANSITIONS: none, fade, wipe-left, wipe-right, slide-up, dissolve, zoom

RULES:
1. Keep scenes 3-8 seconds each. Total video should be 15-60 seconds for social.
2. Every scene needs at least one text overlay for accessibility.
3. Use ken-burns animation on still images to add motion.
4. Match text animation to the energy — news = slide-up, product = bounce, interview = fade-in.
5. Always include a title scene and an end card with CTA.
6. If voiceover is provided, sync scene durations to the transcript segments.
7. Use the brand colors from context for all text and UI elements.
8. For split-screen, ensure both panels have similar energy/framing.

When you produce a composition, use the emit_artifact tool with type "video_composition".
The composition MUST match the VideoComposition schema exactly."""

    def _define_tools(self) -> list[dict]:
        """Video editor agent-specific tools (scene manipulation helpers)."""
        return [
            {
                "name": "analyze_script_timing",
                "description": (
                    "Analyze a voiceover script to estimate per-sentence timing. "
                    "Use this to sync scene durations to voiceover segments."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script": {"type": "string", "description": "The full voiceover script"},
                        "words_per_minute": {
                            "type": "integer",
                            "description": "Speaking rate (default: 150 wpm)",
                            "default": 150,
                        },
                    },
                    "required": ["script"],
                },
            },
            {
                "name": "calculate_scene_timing",
                "description": (
                    "Calculate optimal scene durations based on content type and total target duration. "
                    "Returns suggested duration for each scene."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "scene_count": {"type": "integer"},
                        "total_duration_seconds": {"type": "number"},
                        "scene_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Type of each scene: title, content, quote, end_card, etc.",
                        },
                        "has_voiceover": {"type": "boolean", "default": False},
                    },
                    "required": ["scene_count", "total_duration_seconds"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            if tool_name == "analyze_script_timing":
                return self._analyze_script_timing(tool_input)
            elif tool_name == "calculate_scene_timing":
                return self._calculate_scene_timing(tool_input)
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    def _analyze_script_timing(self, params: dict) -> dict:
        """Estimate per-sentence timing from a script."""
        script = params["script"]
        wpm = params.get("words_per_minute", 150)

        # Split into sentences
        import re
        sentences = [s.strip() for s in re.split(r'[.!?]+', script) if s.strip()]

        segments = []
        total_seconds = 0.0
        for sentence in sentences:
            word_count = len(sentence.split())
            duration = (word_count / wpm) * 60
            duration = max(duration, 2.0)  # minimum 2s per segment
            segments.append({
                "text": sentence,
                "word_count": word_count,
                "estimated_seconds": round(duration, 1),
            })
            total_seconds += duration

        return {
            "segments": segments,
            "total_seconds": round(total_seconds, 1),
            "sentence_count": len(sentences),
            "total_words": sum(s["word_count"] for s in segments),
        }

    def _calculate_scene_timing(self, params: dict) -> dict:
        """Calculate optimal scene durations."""
        scene_count = params["scene_count"]
        total = params["total_duration_seconds"]
        scene_types = params.get("scene_types", ["content"] * scene_count)

        # Weight by scene type
        weights = {
            "title": 0.8,
            "content": 1.0,
            "quote": 1.2,
            "end_card": 0.7,
            "transition": 0.3,
            "intro": 0.6,
            "demo": 1.5,
        }

        raw_weights = [weights.get(st, 1.0) for st in scene_types[:scene_count]]
        total_weight = sum(raw_weights)
        durations = [round((w / total_weight) * total, 1) for w in raw_weights]

        # Enforce min/max
        durations = [max(2.0, min(d, 10.0)) for d in durations]

        # Adjust to hit target total
        diff = total - sum(durations)
        if durations and abs(diff) > 0.1:
            # Distribute difference across content scenes
            content_indices = [i for i, st in enumerate(scene_types[:scene_count]) if st == "content"]
            if content_indices:
                per_scene = diff / len(content_indices)
                for i in content_indices:
                    durations[i] = round(durations[i] + per_scene, 1)

        return {
            "scenes": [
                {"index": i, "type": scene_types[i] if i < len(scene_types) else "content",
                 "duration_seconds": durations[i]}
                for i in range(len(durations))
            ],
            "total_seconds": round(sum(durations), 1),
            "target_seconds": total,
        }
