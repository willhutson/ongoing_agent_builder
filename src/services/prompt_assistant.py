"""
Prompt Assistant Service

Uses Claude Sonnet to help users craft better prompts for visual, video,
and design generation tools. This is a cost-effective way to improve
generation quality without wasting expensive API calls on bad prompts.
"""

import anthropic
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from ..config import get_settings


class PromptType(str, Enum):
    """Types of prompts the assistant can help with."""
    VIDEO = "video"  # Higgsfield, Runway
    IMAGE = "image"  # DALL-E, Flux, Stability
    PRESENTATION = "presentation"  # Beautiful.ai, Gamma
    VOICE = "voice"  # ElevenLabs voice description
    STORYBOARD = "storyboard"  # Video storyboard sequences


@dataclass
class PromptTemplate:
    """Template for a specific prompt type."""
    type: PromptType
    name: str
    description: str
    system_prompt: str
    example_input: str
    example_output: str


# Prompt templates for each type
PROMPT_TEMPLATES: dict[PromptType, PromptTemplate] = {
    PromptType.VIDEO: PromptTemplate(
        type=PromptType.VIDEO,
        name="Video Generation",
        description="Craft prompts for AI video generation (Higgsfield, Runway, Sora, Veo)",
        system_prompt="""You are an expert at crafting prompts for AI video generation models like Sora, Veo, Kling, and Runway.

Your job is to take a user's rough idea and transform it into an optimized video generation prompt.

Guidelines for great video prompts:
1. Be specific about camera movements (pan, zoom, dolly, crane, tracking shot)
2. Describe lighting conditions (golden hour, studio lighting, neon, dramatic shadows)
3. Specify the visual style (cinematic, documentary, commercial, artistic)
4. Include motion descriptions (slow motion, time-lapse, smooth movement)
5. Mention aspect ratio and duration preferences if relevant
6. Describe the mood and atmosphere
7. Include specific details about subjects, settings, and actions
8. Use film terminology when appropriate (shallow depth of field, wide angle, close-up)

Output ONLY the optimized prompt - no explanations or additional text.""",
        example_input="product video of sneakers",
        example_output="Cinematic product shot of premium white sneakers rotating on a minimalist circular platform. Studio lighting with soft shadows, shallow depth of field. Camera slowly orbits 180 degrees around the shoe, capturing texture details and clean lines. Subtle particle effects catch the light. Commercial aesthetic, 4K quality, 5 second duration.",
    ),
    PromptType.IMAGE: PromptTemplate(
        type=PromptType.IMAGE,
        name="Image Generation",
        description="Craft prompts for AI image generation (DALL-E, Flux, Stable Diffusion)",
        system_prompt="""You are an expert at crafting prompts for AI image generation models like DALL-E 3, Flux, and Stable Diffusion.

Your job is to take a user's rough idea and transform it into an optimized image generation prompt.

Guidelines for great image prompts:
1. Start with the main subject and its key characteristics
2. Describe the setting/background in detail
3. Specify lighting (natural, studio, dramatic, soft, golden hour)
4. Include art style (photorealistic, illustration, 3D render, watercolor, etc.)
5. Mention composition (rule of thirds, centered, symmetrical)
6. Add quality modifiers (highly detailed, professional, 8K, award-winning)
7. Include mood and atmosphere descriptors
8. Specify camera/lens details for photorealistic images

Output ONLY the optimized prompt - no explanations or additional text.""",
        example_input="a cat wearing sunglasses",
        example_output="A sophisticated orange tabby cat wearing oversized vintage aviator sunglasses, sitting regally on a velvet cushion. Soft studio lighting with a subtle gradient background in warm cream tones. Photorealistic style, sharp focus on the cat's face, shallow depth of field. Professional pet photography aesthetic, highly detailed fur texture, 8K quality.",
    ),
    PromptType.PRESENTATION: PromptTemplate(
        type=PromptType.PRESENTATION,
        name="Presentation Design",
        description="Craft briefs for AI presentation tools (Beautiful.ai, Gamma)",
        system_prompt="""You are an expert at crafting briefs for AI presentation generation tools like Beautiful.ai and Gamma.

Your job is to take a user's rough idea and create a structured presentation brief.

Guidelines for great presentation briefs:
1. Define the target audience clearly
2. Specify the presentation goal (inform, persuade, train, pitch)
3. Outline key sections/slides with main points
4. Suggest visual themes and color schemes
5. Recommend chart/graph types for data
6. Include tone guidance (formal, casual, inspiring, technical)
7. Specify approximate slide count
8. Note any brand guidelines to follow

Output a structured brief that can be used with AI presentation tools.""",
        example_input="quarterly sales presentation",
        example_output="""Presentation Brief: Q4 Sales Review

Audience: Executive leadership team
Goal: Report quarterly performance and set expectations for next quarter
Tone: Professional, data-driven, confident
Slides: 12-15
Color scheme: Corporate blue with accent orange for highlights

Structure:
1. Title slide with quarter/year
2. Executive summary - 3 key wins
3. Revenue overview - bar chart comparing to previous quarters
4. Regional breakdown - map visualization
5. Top performing products - horizontal bar chart
6. Customer acquisition metrics - line graph showing trend
7. Challenges faced - brief bullet points
8. Solutions implemented - icons with short descriptions
9. Team highlights - photos with achievements
10. Q1 forecast - projected numbers
11. Strategic initiatives - timeline graphic
12. Call to action - next steps
13. Q&A slide""",
    ),
    PromptType.VOICE: PromptTemplate(
        type=PromptType.VOICE,
        name="Voice Description",
        description="Craft voice descriptions for AI voice synthesis (ElevenLabs)",
        system_prompt="""You are an expert at describing voices for AI voice synthesis tools like ElevenLabs.

Your job is to take a user's rough idea and create a detailed voice description for voice cloning or voice design.

Guidelines for great voice descriptions:
1. Describe the basic characteristics (gender, age range, accent)
2. Specify tone qualities (warm, authoritative, friendly, professional)
3. Include pace and rhythm (measured, energetic, calm)
4. Mention any distinctive qualities (slight rasp, melodic, deep resonance)
5. Suggest emotional range if needed
6. Reference well-known voice archetypes if helpful
7. Describe use case fit (narration, commercial, character, podcast)

Output ONLY the voice description - no explanations or additional text.""",
        example_input="voice for a meditation app",
        example_output="Calm, soothing female voice in her 30s-40s with a neutral American accent. Warm and nurturing tone with a naturally slow, measured pace. Gentle resonance with soft, breathy quality. Consistent low-to-mid pitch range that creates a sense of safety and relaxation. Perfect for guided meditations, sleep stories, and wellness content. Think: spa receptionist meets yoga instructor - professional yet deeply calming.",
    ),
    PromptType.STORYBOARD: PromptTemplate(
        type=PromptType.STORYBOARD,
        name="Video Storyboard",
        description="Create shot-by-shot storyboards for video production",
        system_prompt="""You are an expert at creating video storyboards for AI video production.

Your job is to take a user's concept and break it into a shot-by-shot storyboard.

Guidelines for great storyboards:
1. Break the concept into 4-8 distinct shots
2. For each shot, specify:
   - Shot number and duration
   - Camera angle and movement
   - Subject/action description
   - Visual style notes
   - Transition to next shot
3. Maintain visual continuity
4. Consider pacing and rhythm
5. Include any text overlays or graphics
6. Note audio/music suggestions

Output a structured storyboard that can be used to generate individual video clips.""",
        example_input="30 second ad for a fitness app",
        example_output="""STORYBOARD: Fitness App Ad (30 seconds)

SHOT 1 (0-4s)
- Wide shot, sunrise over city skyline
- Slow zoom in
- Text overlay: "Your journey starts now"
- Transition: Quick cut

SHOT 2 (4-8s)
- Close-up of running shoes hitting pavement
- Tracking shot, eye level
- Morning golden light, slight motion blur
- Transition: Match cut to...

SHOT 3 (8-12s)
- Phone screen showing app interface
- Over-shoulder POV of user
- Clean UI visible with workout progress
- Transition: Swipe animation

SHOT 4 (12-18s)
- Montage: 3 quick cuts of different workouts
- Gym, outdoor yoga, home HIIT
- Dynamic camera movements
- Upbeat energy
- Transition: Flash cut

SHOT 5 (18-24s)
- User checking phone, smiling at progress
- Medium shot, warm indoor lighting
- Genuine satisfaction expression
- Transition: Fade

SHOT 6 (24-30s)
- App logo center screen
- Clean gradient background
- Tagline: "Transform your routine"
- Call to action: "Download free"
- End card with app store badges

Audio: Upbeat electronic track, builds through shots 1-4, softens for 5-6""",
    ),
}


class PromptAssistant:
    """Service for helping users craft better prompts using Claude Sonnet."""

    # Using Sonnet for cost-effectiveness
    MODEL = "claude-sonnet-4-20250514"

    def __init__(self):
        settings = get_settings()
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def enhance_prompt(
        self,
        prompt_type: PromptType,
        user_input: str,
        context: Optional[str] = None,
        brand_guidelines: Optional[str] = None,
    ) -> dict:
        """
        Enhance a user's rough prompt into an optimized generation prompt.

        Args:
            prompt_type: The type of content being generated
            user_input: The user's rough idea/prompt
            context: Optional additional context (e.g., campaign info)
            brand_guidelines: Optional brand guidelines to follow

        Returns:
            Dict with enhanced prompt and metadata
        """
        template = PROMPT_TEMPLATES.get(prompt_type)
        if not template:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        # Build the system prompt with optional brand guidelines
        system = template.system_prompt
        if brand_guidelines:
            system += f"\n\nBrand Guidelines to follow:\n{brand_guidelines}"

        # Build the user message
        user_message = f"User's idea: {user_input}"
        if context:
            user_message += f"\n\nAdditional context: {context}"

        # Call Claude Sonnet
        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=1024,
            system=system,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        enhanced_prompt = response.content[0].text

        return {
            "original_input": user_input,
            "enhanced_prompt": enhanced_prompt,
            "prompt_type": prompt_type.value,
            "model_used": self.MODEL,
            "tokens_used": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
            }
        }

    async def get_suggestions(
        self,
        prompt_type: PromptType,
        user_input: str,
        num_variations: int = 3,
    ) -> dict:
        """
        Generate multiple prompt variations for the user to choose from.

        Args:
            prompt_type: The type of content being generated
            user_input: The user's rough idea/prompt
            num_variations: Number of variations to generate (1-5)

        Returns:
            Dict with multiple prompt variations
        """
        template = PROMPT_TEMPLATES.get(prompt_type)
        if not template:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        num_variations = max(1, min(5, num_variations))

        system = template.system_prompt + f"""

Generate exactly {num_variations} different variations of the prompt, each with a different creative direction.
Format your response as:
VARIATION 1:
[prompt]

VARIATION 2:
[prompt]

etc."""

        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=2048,
            system=system,
            messages=[
                {"role": "user", "content": f"User's idea: {user_input}"}
            ]
        )

        # Parse variations from response
        raw_text = response.content[0].text
        variations = []

        # Split by variation markers
        parts = raw_text.split("VARIATION")
        for part in parts[1:]:  # Skip empty first part
            # Extract the prompt after the number and colon
            lines = part.strip().split("\n", 1)
            if len(lines) > 1:
                variations.append(lines[1].strip())
            elif lines:
                # Handle case where prompt is on same line
                prompt = lines[0].split(":", 1)[-1].strip()
                if prompt:
                    variations.append(prompt)

        return {
            "original_input": user_input,
            "variations": variations,
            "prompt_type": prompt_type.value,
            "model_used": self.MODEL,
            "tokens_used": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
            }
        }


def get_prompt_templates() -> list[dict]:
    """Get all available prompt templates for the UI."""
    return [
        {
            "type": template.type.value,
            "name": template.name,
            "description": template.description,
            "example_input": template.example_input,
            "example_output": template.example_output,
        }
        for template in PROMPT_TEMPLATES.values()
    ]


# Singleton instance
_assistant: Optional[PromptAssistant] = None


def get_prompt_assistant() -> PromptAssistant:
    """Get or create the prompt assistant instance."""
    global _assistant
    if _assistant is None:
        _assistant = PromptAssistant()
    return _assistant
