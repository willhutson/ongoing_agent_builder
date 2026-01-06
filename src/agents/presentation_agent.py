from typing import Any
import httpx
from .base import BaseAgent


class PresentationAgent(BaseAgent):
    """
    Agent for generating presentations and pitch decks.

    Capabilities:
    - Generate full decks from briefs
    - Generate individual slides
    - Apply brand templates
    - Insert ERP data (charts, stats, timelines)
    - Apply moodboard styling
    - Export to various formats
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
        return "presentation_agent"

    @property
    def system_prompt(self) -> str:
        base_prompt = """You are an expert presentation designer and storyteller.

Your role is to create compelling, visually-driven presentations by:
1. Understanding the audience and objectives
2. Structuring content for maximum impact
3. Applying brand guidelines consistently
4. Incorporating data and visuals effectively
5. Creating clear, memorable narratives

When creating presentations:
- Start with a strong hook/opening
- Follow a clear narrative arc
- Use data to support key points
- Keep slides clean and focused (one idea per slide)
- End with clear call-to-action

Slide types you can create:
- Title/Cover slides
- Agenda/Overview slides
- Content slides (text, bullets, quotes)
- Data slides (charts, graphs, statistics)
- Image/Visual slides
- Comparison slides
- Timeline slides
- Team/About slides
- Summary/Conclusion slides
- CTA/Next steps slides"""

        if self.language != "en":
            base_prompt += f"\n\nPrimary language: {self.language}"
        if self.client_specific_id:
            base_prompt += f"\n\nApply client-specific brand guidelines for client: {self.client_specific_id}"

        return base_prompt

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_deck",
                "description": "Generate a complete presentation deck from a brief or topic.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brief_id": {
                            "type": "string",
                            "description": "Brief ID to generate deck from",
                        },
                        "topic": {
                            "type": "string",
                            "description": "Topic if no brief ID provided",
                        },
                        "audience": {
                            "type": "string",
                            "description": "Target audience for the presentation",
                        },
                        "num_slides": {
                            "type": "integer",
                            "description": "Approximate number of slides",
                            "default": 10,
                        },
                        "template_id": {
                            "type": "string",
                            "description": "Brand template to use",
                        },
                        "moodboard_id": {
                            "type": "string",
                            "description": "Moodboard for style reference",
                        },
                        "include_data": {
                            "type": "boolean",
                            "description": "Include ERP data/charts",
                            "default": True,
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "generate_slide",
                "description": "Generate a single slide for an existing deck.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deck_id": {
                            "type": "string",
                            "description": "Deck to add slide to",
                        },
                        "slide_type": {
                            "type": "string",
                            "enum": [
                                "title",
                                "agenda",
                                "content",
                                "data",
                                "image",
                                "comparison",
                                "timeline",
                                "team",
                                "summary",
                                "cta",
                            ],
                            "description": "Type of slide to generate",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content/topic for the slide",
                        },
                        "position": {
                            "type": "integer",
                            "description": "Position in deck (0-indexed)",
                        },
                    },
                    "required": ["slide_type", "content"],
                },
            },
            {
                "name": "get_brand_template",
                "description": "Retrieve a brand presentation template.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {
                            "type": "string",
                            "description": "Client for client-specific template",
                        },
                        "template_type": {
                            "type": "string",
                            "enum": ["pitch", "proposal", "report", "internal", "creative"],
                            "description": "Type of presentation",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_moodboard",
                "description": "Fetch a moodboard for style reference.",
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
                "description": "Extract style attributes from a moodboard.",
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
                            "description": "What to extract: colors, typography, imagery, mood, layout",
                        },
                    },
                    "required": ["moodboard_id"],
                },
            },
            {
                "name": "insert_erp_data",
                "description": "Insert data visualization from ERP into a slide.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "slide_id": {
                            "type": "string",
                            "description": "Slide to insert data into",
                        },
                        "data_type": {
                            "type": "string",
                            "enum": ["chart", "table", "stat", "timeline", "funnel"],
                            "description": "Type of data visualization",
                        },
                        "data_source": {
                            "type": "string",
                            "enum": ["project", "client", "pipeline", "resources", "financial"],
                            "description": "ERP data source",
                        },
                        "query": {
                            "type": "object",
                            "description": "Query parameters for data",
                        },
                    },
                    "required": ["slide_id", "data_type", "data_source"],
                },
            },
            {
                "name": "apply_style",
                "description": "Apply moodboard/brand style to a deck or slide.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deck_id": {
                            "type": "string",
                            "description": "Deck to style",
                        },
                        "slide_id": {
                            "type": "string",
                            "description": "Single slide to style",
                        },
                        "moodboard_id": {
                            "type": "string",
                            "description": "Moodboard for style reference",
                        },
                        "style_elements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Elements to style: colors, fonts, imagery, layout",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "save_deck",
                "description": "Save deck to DAM/studio.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deck_id": {
                            "type": "string",
                            "description": "Deck ID if updating",
                        },
                        "title": {"type": "string"},
                        "slides": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Slide content array",
                        },
                        "project_id": {"type": "string"},
                        "client_id": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["draft", "review", "approved", "final"],
                            "default": "draft",
                        },
                    },
                    "required": ["title", "slides"],
                },
            },
            {
                "name": "export_deck",
                "description": "Export deck to various formats.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deck_id": {"type": "string"},
                        "format": {
                            "type": "string",
                            "enum": ["pdf", "pptx", "google_slides", "keynote", "images"],
                        },
                        "options": {
                            "type": "object",
                            "properties": {
                                "include_notes": {"type": "boolean"},
                                "include_animations": {"type": "boolean"},
                            },
                        },
                    },
                    "required": ["deck_id", "format"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "generate_deck":
                return await self._generate_deck(tool_input)
            elif tool_name == "generate_slide":
                return await self._generate_slide(tool_input)
            elif tool_name == "get_brand_template":
                return await self._get_brand_template(tool_input)
            elif tool_name == "get_moodboard":
                return await self._get_moodboard(tool_input)
            elif tool_name == "analyze_moodboard":
                return await self._analyze_moodboard(tool_input)
            elif tool_name == "insert_erp_data":
                return await self._insert_erp_data(tool_input)
            elif tool_name == "apply_style":
                return await self._apply_style(tool_input)
            elif tool_name == "save_deck":
                return await self._save_deck(tool_input)
            elif tool_name == "export_deck":
                return await self._export_deck(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _generate_deck(self, params: dict) -> dict:
        """Generate a complete deck."""
        # Get brief if provided
        brief_context = ""
        if params.get("brief_id"):
            response = await self.http_client.get(f"/api/v1/briefs/{params['brief_id']}")
            if response.status_code == 200:
                brief_context = response.json()

        return {
            "status": "ready_to_generate",
            "brief": brief_context,
            "topic": params.get("topic"),
            "audience": params.get("audience"),
            "num_slides": params.get("num_slides", 10),
            "template_id": params.get("template_id"),
            "moodboard_id": params.get("moodboard_id"),
            "instruction": "Generate a complete presentation deck with the specified number of slides.",
        }

    async def _generate_slide(self, params: dict) -> dict:
        """Generate a single slide."""
        return {
            "status": "ready_to_generate",
            "slide_type": params["slide_type"],
            "content": params["content"],
            "position": params.get("position"),
            "instruction": f"Generate a {params['slide_type']} slide with the provided content.",
        }

    async def _get_brand_template(self, params: dict) -> dict:
        """Get brand template."""
        response = await self.http_client.get(
            "/api/v1/studio/templates",
            params={
                "client_id": params.get("client_id") or self.client_specific_id,
                "type": params.get("template_type", "pitch"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"template": None, "note": "Using default template"}

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
        """Analyze moodboard for style extraction."""
        response = await self.http_client.get(
            f"/api/v1/studio/moodboards/{params['moodboard_id']}/analyze",
            params={"extract": ",".join(params.get("extract", ["colors", "mood"]))},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "moodboard_id": params["moodboard_id"],
            "instruction": "Analyze the moodboard visually and extract style attributes.",
        }

    async def _insert_erp_data(self, params: dict) -> dict:
        """Get ERP data for visualization."""
        response = await self.http_client.get(
            f"/api/v1/{params['data_source']}/data",
            params=params.get("query", {}),
        )
        if response.status_code == 200:
            return {
                "data": response.json(),
                "visualization_type": params["data_type"],
                "slide_id": params["slide_id"],
            }
        return {"error": "Could not fetch data", "data_source": params["data_source"]}

    async def _apply_style(self, params: dict) -> dict:
        """Apply style to deck/slide."""
        return {
            "deck_id": params.get("deck_id"),
            "slide_id": params.get("slide_id"),
            "moodboard_id": params.get("moodboard_id"),
            "style_elements": params.get("style_elements", ["colors", "fonts"]),
            "instruction": "Apply the moodboard style to the specified deck or slide.",
        }

    async def _save_deck(self, params: dict) -> dict:
        """Save deck to studio."""
        response = await self.http_client.post(
            "/api/v1/studio/decks",
            json={
                "title": params["title"],
                "slides": params["slides"],
                "project_id": params.get("project_id"),
                "client_id": params.get("client_id") or self.client_specific_id,
                "status": params.get("status", "draft"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to save deck"}

    async def _export_deck(self, params: dict) -> dict:
        """Export deck to format."""
        response = await self.http_client.post(
            f"/api/v1/studio/decks/{params['deck_id']}/export",
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
