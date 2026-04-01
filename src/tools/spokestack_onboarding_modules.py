"""
Onboarding Module Recommendations — recommend_and_install_modules tool.

When the onboarding agent understands the business type, it calls this tool
to suggest relevant marketplace modules. Two-step flow:
1. confirmed=false → return recommendations with reasons (agent presents to user)
2. confirmed=true → call spokestack-core's batch install endpoint
"""

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# Industry → Module Mapping
# ══════════════════════════════════════════════════════════════

INDUSTRY_MODULE_MAP: dict[str, list[str]] = {
    "agency": ["CRM", "CONTENT_STUDIO", "WORKFLOWS", "TIME_LEAVE", "SOCIAL_PUBLISHING"],
    "saas": ["CRM", "ANALYTICS", "WORKFLOWS", "NPS", "FINANCE"],
    "services": ["CRM", "TIME_LEAVE", "FINANCE", "NPS", "WORKFLOWS"],
    "ecommerce": ["CRM", "ANALYTICS", "SOCIAL_PUBLISHING", "FINANCE"],
    "construction": ["TIME_LEAVE", "WORKFLOWS", "FINANCE"],
    "consulting": ["CRM", "TIME_LEAVE", "FINANCE", "ANALYTICS"],
    "media": ["CONTENT_STUDIO", "SOCIAL_PUBLISHING", "ANALYTICS", "CRM"],
    "education": ["LMS", "NPS", "WORKFLOWS", "ANALYTICS"],
}

MODULE_REASONS: dict[str, str] = {
    "CRM": "Manage client relationships, deal pipeline, and contact history",
    "CONTENT_STUDIO": "Creative asset management, moodboards, video pipeline, and approval workflows",
    "WORKFLOWS": "Automate recurring processes like brief intake, review cycles, and onboarding",
    "TIME_LEAVE": "Track billable hours, manage leave requests, and monitor team capacity",
    "SOCIAL_PUBLISHING": "Schedule and publish across social platforms with engagement tracking",
    "ANALYTICS": "Performance dashboards, metrics, and automated reporting",
    "FINANCE": "Invoicing, budget tracking, and revenue forecasting",
    "NPS": "Client satisfaction surveys and feedback collection",
    "LMS": "Team training courses, assessments, and learning paths",
    "LISTENING": "Social listening, brand monitoring, and sentiment analysis",
    "MEDIA_BUYING": "Ad campaign management across Meta, Google, TikTok, and more",
}


# ══════════════════════════════════════════════════════════════
# Tool Definition
# ══════════════════════════════════════════════════════════════

RECOMMEND_MODULES_TOOL = {
    "type": "function",
    "function": {
        "name": "recommend_and_install_modules",
        "description": (
            "After learning about the business, recommend marketplace modules that match their "
            "industry and needs. Call this ONCE after you understand the business type (usually "
            "after question 1-2). Present the recommendations to the user and ask for confirmation "
            "before installing. The user can approve all, remove some, or skip entirely."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "industry": {
                    "type": "string",
                    "enum": list(INDUSTRY_MODULE_MAP.keys()),
                    "description": "The detected industry/business type",
                },
                "confirmed": {
                    "type": "boolean",
                    "description": (
                        "True if the user has confirmed the recommendations. "
                        "False for initial recommendation (present to user first)."
                    ),
                    "default": False,
                },
                "selected_modules": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Module types to install (only used when confirmed=true). "
                        "Defaults to the industry template if not provided."
                    ),
                },
            },
            "required": ["industry"],
        },
    },
}

ONBOARDING_MODULE_TOOLS = [RECOMMEND_MODULES_TOOL]

ONBOARDING_MODULE_TOOL_NAMES = {"recommend_and_install_modules"}


# ══════════════════════════════════════════════════════════════
# Tool Handler
# ══════════════════════════════════════════════════════════════

async def handle_recommend_and_install(params: dict, org_id: str) -> dict:
    """
    Handle the recommend_and_install_modules tool call.

    When confirmed=false: Return recommendations for the agent to present.
    When confirmed=true: Call spokestack-core's batch install endpoint.
    """
    industry = params.get("industry", "services")
    confirmed = params.get("confirmed", False)
    selected = params.get("selected_modules") or INDUSTRY_MODULE_MAP.get(industry, [])

    if not confirmed:
        # Return recommendations for the agent to present to the user
        recommendations = []
        for mod_type in INDUSTRY_MODULE_MAP.get(industry, []):
            recommendations.append({
                "moduleType": mod_type,
                "reason": MODULE_REASONS.get(mod_type, ""),
            })
        return {
            "status": "recommendation",
            "industry": industry,
            "recommendations": recommendations,
            "message": (
                f"Based on your {industry} business, I recommend these modules. "
                "Present them to the user and ask for confirmation."
            ),
        }

    # Confirmed — install via spokestack-core batch endpoint
    core_url = os.environ.get("SPOKESTACK_CORE_URL", "https://spokestack-core.vercel.app")
    agent_secret = os.environ.get("AGENT_RUNTIME_SECRET", "")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{core_url}/api/v1/modules/install-batch",
                headers={
                    "Content-Type": "application/json",
                    "X-Agent-Secret": agent_secret,
                },
                json={
                    "moduleTypes": selected,
                    "orgId": org_id,
                },
            )
            response.raise_for_status()
            result = response.json()
            return {
                "status": "installed",
                "installed": result.get("installed", []),
                "skipped": result.get("skipped", []),
                "message": "Modules installed successfully.",
            }
    except httpx.HTTPStatusError as e:
        logger.error(f"Module install failed: {e.response.status_code} {e.response.text}")
        return {
            "status": "error",
            "message": f"Failed to install modules: {e.response.status_code}",
        }
    except Exception as e:
        logger.error(f"Module install failed: {e}")
        return {
            "status": "error",
            "message": f"Failed to install modules: {str(e)}",
        }
