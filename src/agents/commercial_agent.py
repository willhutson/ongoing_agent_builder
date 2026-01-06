from typing import Any
import httpx
from .base import BaseAgent


class CommercialAgent(BaseAgent):
    """
    Agent for pricing intelligence and commercial document creation.

    Capabilities:
    - Analyze historical RFP commercials and outcomes
    - Learn from past pricing → negotiation → final contract patterns
    - Estimate pricing for new RFPs based on similar past work
    - Generate commercial proposals with justified pricing
    - Provide margin analysis and pricing recommendations
    - Track win/loss rates by pricing strategy
    """

    def __init__(self, client, model: str, erp_base_url: str, erp_api_key: str):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=30.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "commercial_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert commercial strategist and pricing analyst for a professional services agency.

Your role is to create winning commercial proposals by:
1. Analyzing historical pricing data and outcomes (submitted → negotiated → final)
2. Understanding what pricing strategies win in different contexts
3. Balancing competitiveness with healthy margins
4. Providing data-backed pricing recommendations
5. Creating professional commercial documents

When estimating pricing:
- Find similar past RFPs by scope, client type, industry, deliverables
- Analyze the pricing journey: initial submission → negotiation → final contract
- Note win/loss outcomes and correlate with pricing strategies
- Consider client budget signals and market positioning
- Factor in team composition and resource costs

When creating commercial documents:
- Structure pricing clearly (by phase, deliverable, or fixed fee)
- Include assumptions and exclusions
- Provide options where appropriate (good/better/best)
- Justify value, not just cost
- Include payment terms and conditions

Key metrics to consider:
- Historical win rate at different price points
- Average negotiation discount percentage
- Margin targets by service type
- Client lifetime value potential
- Resource utilization impact"""

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "search_similar_commercials",
                "description": "Search for similar past RFP commercials to inform pricing. Returns submitted price, negotiated price, final contract value, and outcome.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "service_type": {
                            "type": "string",
                            "description": "Type of service (branding, digital, campaign, etc.)",
                        },
                        "industry": {
                            "type": "string",
                            "description": "Client industry",
                        },
                        "deliverables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of deliverables to match",
                        },
                        "budget_range": {
                            "type": "object",
                            "properties": {
                                "min": {"type": "number"},
                                "max": {"type": "number"},
                                "currency": {"type": "string", "default": "USD"},
                            },
                            "description": "Budget range to filter by",
                        },
                        "outcome_filter": {
                            "type": "string",
                            "enum": ["won", "lost", "all"],
                            "default": "all",
                            "description": "Filter by outcome",
                        },
                        "limit": {"type": "integer", "default": 10},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_pricing_history",
                "description": "Get detailed pricing history for a specific client or project type, including negotiation patterns.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {
                            "type": "string",
                            "description": "Client ID for client-specific history",
                        },
                        "client_name": {
                            "type": "string",
                            "description": "Client name if ID not known",
                        },
                        "service_type": {"type": "string"},
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string"},
                                "end": {"type": "string"},
                            },
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_rfp_scope",
                "description": "Analyze an RFP document to extract scope and estimate effort/pricing components.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rfp_document_id": {
                            "type": "string",
                            "description": "ID of RFP document in DAM",
                        },
                        "rfp_text": {
                            "type": "string",
                            "description": "RFP text if not in DAM",
                        },
                        "extract_deliverables": {"type": "boolean", "default": True},
                        "extract_timeline": {"type": "boolean", "default": True},
                        "extract_budget_hints": {"type": "boolean", "default": True},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_rate_card",
                "description": "Get current rate card and pricing guidelines.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "service_type": {"type": "string"},
                        "client_tier": {
                            "type": "string",
                            "enum": ["standard", "preferred", "strategic"],
                            "description": "Client tier for rate adjustments",
                        },
                        "include_costs": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include internal cost rates",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "calculate_estimate",
                "description": "Calculate a pricing estimate based on deliverables and effort.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "deliverables": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "hours_estimate": {"type": "number"},
                                    "role_mix": {
                                        "type": "object",
                                        "description": "Hours by role (e.g., {senior_designer: 20, junior_designer: 40})",
                                    },
                                    "fixed_costs": {"type": "number"},
                                },
                            },
                        },
                        "margin_target": {
                            "type": "number",
                            "description": "Target margin percentage (e.g., 0.35 for 35%)",
                        },
                        "pricing_model": {
                            "type": "string",
                            "enum": ["fixed", "time_and_materials", "retainer", "hybrid"],
                        },
                        "include_contingency": {
                            "type": "boolean",
                            "default": True,
                        },
                        "contingency_percent": {
                            "type": "number",
                            "default": 0.1,
                        },
                    },
                    "required": ["deliverables"],
                },
            },
            {
                "name": "get_win_rate_analysis",
                "description": "Get win/loss analysis by pricing strategy, discount level, and other factors.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "service_type": {"type": "string"},
                        "industry": {"type": "string"},
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string"},
                                "end": {"type": "string"},
                            },
                        },
                        "group_by": {
                            "type": "string",
                            "enum": ["price_range", "discount_level", "client_type", "service_type"],
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "create_commercial_document",
                "description": "Create and save a commercial proposal document.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rfp_id": {"type": "string"},
                        "client_name": {"type": "string"},
                        "project_name": {"type": "string"},
                        "pricing_summary": {
                            "type": "object",
                            "properties": {
                                "total": {"type": "number"},
                                "currency": {"type": "string"},
                                "pricing_model": {"type": "string"},
                            },
                        },
                        "line_items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "unit_price": {"type": "number"},
                                    "total": {"type": "number"},
                                },
                            },
                        },
                        "phases": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "deliverables": {"type": "array", "items": {"type": "string"}},
                                    "price": {"type": "number"},
                                    "duration": {"type": "string"},
                                },
                            },
                            "description": "Pricing broken down by phase",
                        },
                        "options": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "price": {"type": "number"},
                                },
                            },
                            "description": "Optional add-ons or tiers",
                        },
                        "assumptions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "exclusions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "payment_terms": {"type": "string"},
                        "validity_period": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["client_name", "project_name", "pricing_summary"],
                },
            },
            {
                "name": "compare_to_budget",
                "description": "Compare proposed pricing to client's indicated budget and provide recommendations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "proposed_price": {"type": "number"},
                        "client_budget": {"type": "number"},
                        "currency": {"type": "string", "default": "USD"},
                        "flexibility": {
                            "type": "string",
                            "enum": ["firm", "negotiable", "unknown"],
                        },
                    },
                    "required": ["proposed_price"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            if tool_name == "search_similar_commercials":
                return await self._search_similar_commercials(tool_input)
            elif tool_name == "get_pricing_history":
                return await self._get_pricing_history(tool_input)
            elif tool_name == "analyze_rfp_scope":
                return await self._analyze_rfp_scope(tool_input)
            elif tool_name == "get_rate_card":
                return await self._get_rate_card(tool_input)
            elif tool_name == "calculate_estimate":
                return await self._calculate_estimate(tool_input)
            elif tool_name == "get_win_rate_analysis":
                return await self._get_win_rate_analysis(tool_input)
            elif tool_name == "create_commercial_document":
                return await self._create_commercial_document(tool_input)
            elif tool_name == "compare_to_budget":
                return await self._compare_to_budget(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _search_similar_commercials(self, params: dict) -> dict:
        """Search for similar past commercials."""
        response = await self.http_client.get(
            "/api/v1/rfp/commercials/search",
            params={
                "service_type": params.get("service_type"),
                "industry": params.get("industry"),
                "deliverables": ",".join(params.get("deliverables", [])),
                "budget_min": params.get("budget_range", {}).get("min"),
                "budget_max": params.get("budget_range", {}).get("max"),
                "outcome": params.get("outcome_filter", "all"),
                "limit": params.get("limit", 10),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"commercials": [], "note": "No similar commercials found"}

    async def _get_pricing_history(self, params: dict) -> dict:
        """Get pricing history for client or service type."""
        response = await self.http_client.get(
            "/api/v1/rfp/pricing-history",
            params={
                "client_id": params.get("client_id"),
                "client_name": params.get("client_name"),
                "service_type": params.get("service_type"),
                "start_date": params.get("date_range", {}).get("start"),
                "end_date": params.get("date_range", {}).get("end"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"history": [], "note": "No pricing history found"}

    async def _analyze_rfp_scope(self, params: dict) -> dict:
        """Analyze RFP to extract scope for pricing."""
        if params.get("rfp_document_id"):
            response = await self.http_client.get(
                f"/api/v1/dam/documents/{params['rfp_document_id']}",
            )
            if response.status_code == 200:
                doc = response.json()
                return {
                    "document_id": params["rfp_document_id"],
                    "content": doc.get("content", ""),
                    "instruction": "Extract deliverables, timeline, and budget hints from this RFP.",
                }
        return {
            "rfp_text": params.get("rfp_text", ""),
            "instruction": "Extract deliverables, timeline, and budget hints from this RFP text.",
        }

    async def _get_rate_card(self, params: dict) -> dict:
        """Get rate card from ERP."""
        response = await self.http_client.get(
            "/api/v1/settings/rate-card",
            params={
                "service_type": params.get("service_type"),
                "client_tier": params.get("client_tier", "standard"),
                "include_costs": params.get("include_costs", False),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "rates": {
                "creative_director": 250,
                "senior_designer": 175,
                "designer": 125,
                "junior_designer": 85,
                "strategist": 200,
                "project_manager": 150,
                "developer": 175,
            },
            "currency": "USD",
            "note": "Using default rate card",
        }

    async def _calculate_estimate(self, params: dict) -> dict:
        """Calculate pricing estimate."""
        # Get rate card first
        rate_card = await self._get_rate_card({})
        rates = rate_card.get("rates", {})

        total_cost = 0
        line_items = []

        for deliverable in params.get("deliverables", []):
            item_cost = deliverable.get("fixed_costs", 0)

            # Calculate labor cost
            for role, hours in deliverable.get("role_mix", {}).items():
                rate = rates.get(role, 150)  # default rate
                item_cost += hours * rate

            line_items.append({
                "name": deliverable.get("name"),
                "cost": item_cost,
            })
            total_cost += item_cost

        # Apply margin
        margin = params.get("margin_target", 0.35)
        price_before_contingency = total_cost / (1 - margin)

        # Apply contingency
        if params.get("include_contingency", True):
            contingency = params.get("contingency_percent", 0.1)
            final_price = price_before_contingency * (1 + contingency)
        else:
            final_price = price_before_contingency

        return {
            "cost": total_cost,
            "margin_target": margin,
            "price_before_contingency": price_before_contingency,
            "contingency_percent": params.get("contingency_percent", 0.1) if params.get("include_contingency") else 0,
            "recommended_price": round(final_price, -2),  # Round to nearest 100
            "line_items": line_items,
            "pricing_model": params.get("pricing_model", "fixed"),
        }

    async def _get_win_rate_analysis(self, params: dict) -> dict:
        """Get win/loss analysis."""
        response = await self.http_client.get(
            "/api/v1/rfp/analytics/win-rate",
            params={
                "service_type": params.get("service_type"),
                "industry": params.get("industry"),
                "start_date": params.get("date_range", {}).get("start"),
                "end_date": params.get("date_range", {}).get("end"),
                "group_by": params.get("group_by", "price_range"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "analysis": {
                "overall_win_rate": 0.45,
                "avg_negotiation_discount": 0.12,
                "note": "Using estimated defaults - no historical data available",
            }
        }

    async def _create_commercial_document(self, params: dict) -> dict:
        """Create and save commercial document."""
        response = await self.http_client.post(
            "/api/v1/rfp/commercials",
            json={
                "rfp_id": params.get("rfp_id"),
                "client_name": params["client_name"],
                "project_name": params["project_name"],
                "pricing_summary": params["pricing_summary"],
                "line_items": params.get("line_items", []),
                "phases": params.get("phases", []),
                "options": params.get("options", []),
                "assumptions": params.get("assumptions", []),
                "exclusions": params.get("exclusions", []),
                "payment_terms": params.get("payment_terms", "50% upfront, 50% on completion"),
                "validity_period": params.get("validity_period", "30 days"),
                "notes": params.get("notes"),
                "status": "draft",
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to create commercial document", "status": response.status_code}

    async def _compare_to_budget(self, params: dict) -> dict:
        """Compare proposed price to client budget."""
        proposed = params["proposed_price"]
        budget = params.get("client_budget")

        if not budget:
            return {
                "comparison": "unknown",
                "recommendation": "No client budget indicated. Consider asking for budget range.",
            }

        diff = proposed - budget
        diff_percent = (diff / budget) * 100 if budget else 0

        if diff_percent > 20:
            recommendation = "Significantly over budget. Consider phased approach or scope reduction."
        elif diff_percent > 5:
            recommendation = "Slightly over budget. May need negotiation room or value justification."
        elif diff_percent > -10:
            recommendation = "Within budget range. Good positioning."
        else:
            recommendation = "Well under budget. Consider if leaving money on table or if scope is light."

        return {
            "proposed_price": proposed,
            "client_budget": budget,
            "difference": diff,
            "difference_percent": round(diff_percent, 1),
            "recommendation": recommendation,
            "flexibility": params.get("flexibility", "unknown"),
        }

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
