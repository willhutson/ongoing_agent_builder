"""
Tool Executor — generic HTTP executor that takes a tool name + parameters
and makes the corresponding API call to spokestack-core.

Handles path params, query params, body params, and fixed_body overrides.
All calls include X-Agent-Secret and X-Organization-Id headers.
"""

import json
import logging
import os

import httpx

from src.tools.spokestack_crud_tools import TOOLS

logger = logging.getLogger(__name__)

SPOKESTACK_CORE_URL = os.environ.get("SPOKESTACK_CORE_URL", "https://spokestack-core.vercel.app")
AGENT_SECRET = os.environ.get("AGENT_RUNTIME_SECRET", "")


async def execute_tool(tool_name: str, parameters: dict, tenant_id: str) -> dict:
    """
    Execute a CRUD tool against spokestack-core's API.

    Args:
        tool_name: The tool to execute (e.g., "create_task", "approve_brief")
        parameters: The parameters the LLM provided
        tenant_id: The org ID for X-Organization-Id header

    Returns:
        The JSON response from spokestack-core, or an error dict
    """
    tool = TOOLS.get(tool_name)
    if not tool:
        return {"error": f"Unknown tool: {tool_name}"}

    method = tool["method"]
    path = tool["path"]
    tool_params = tool.get("parameters", {})

    # Separate path params, query params, and body params
    path_params = {}
    query_params = {}
    body_params = {}

    for key, value in parameters.items():
        if value is None:
            continue
        param_def = tool_params.get(key, {})
        location = param_def.get("in", "body")
        if location == "path":
            path_params[key] = value
        elif location == "query":
            query_params[key] = value
        else:
            body_params[key] = value

    # Substitute path parameters
    for key, value in path_params.items():
        path = path.replace(f"{{{key}}}", str(value))

    # Apply fixed_body if present (overrides everything)
    if "fixed_body" in tool:
        body_params = dict(tool["fixed_body"])
    # Apply fixed_body_merge if present (merges fixed fields into body)
    elif "fixed_body_merge" in tool:
        merged = dict(tool["fixed_body_merge"])
        merged.update(body_params)
        body_params = merged

    url = f"{SPOKESTACK_CORE_URL}{path}"
    headers = {
        "Content-Type": "application/json",
        "X-Agent-Secret": AGENT_SECRET,
        "X-Organization-Id": tenant_id,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers, params=query_params)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=body_params)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=body_params)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                return {"error": f"Unsupported method: {method}"}

        if response.status_code >= 400:
            logger.error(f"Tool {tool_name}: {response.status_code} {response.text[:300]}")
            return {"error": f"spokestack-core returned {response.status_code}", "body": response.text[:500]}

        try:
            return response.json()
        except Exception:
            return {"text": response.text[:1000]}

    except httpx.TimeoutException:
        logger.error(f"Tool {tool_name}: timeout calling {url}")
        return {"error": f"Timeout calling spokestack-core for {tool_name}"}
    except httpx.RequestError as e:
        logger.error(f"Tool {tool_name}: network error: {e}")
        return {"error": f"Network error calling spokestack-core: {str(e)}"}
