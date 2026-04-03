"""
Module Builder Service — implements local-execution tools for ModuleBuilderAgent.

scaffold_module: generates a complete module package (manifest + tools + prompt).
validate_module: security + completeness checks.
"""

import hashlib
import json
import re
from datetime import datetime, timezone


FORBIDDEN_PREFIXES = ["/api/v1/admin/", "/api/v1/auth/", "/api/v1/marketplace/"]

INJECTION_PATTERNS = [
    (r"ignore (previous|all|the above) instructions", "instruction override"),
    (r"you are now", "identity override"),
    (r"pretend (you are|to be)", "identity impersonation"),
    (r"disregard (your|the) (system|previous)", "system override"),
    (r"act as (a|an) (different|new|another)", "role injection"),
    (r"override (your|the) (instructions|prompt|system)", "override injection"),
]


def scaffold_module(params: dict) -> dict:
    """Generate a complete module package from structured parameters."""
    name = params["name"]
    slug = params["slug"]
    module_type = params["module_type"]
    entity_name = params["entity_name"]
    entity_plural = params["entity_name_plural"]
    fields = params.get("fields", [])
    category = params.get("category", "Operations")
    description = params.get("description", f"Manage your {entity_plural} with AI assistance.")
    pricing_type = params.get("pricing_type", "free")
    price_cents = params.get("price_cents")
    monthly_price_cents = params.get("monthly_price_cents")

    base_path = f"/api/v1/{entity_plural}"

    field_params = {
        f["name"]: {
            "type": f.get("type", "string"),
            "description": f.get("description", f"The {f['name']}"),
            **({"required": True} if f.get("required") else {}),
        }
        for f in fields
    }

    id_param = {
        "id": {"type": "string", "required": True, "in": "path", "description": f"The {entity_name} ID"},
    }

    tools = [
        {
            "name": f"list_{entity_plural}",
            "description": f"List all {entity_plural}",
            "method": "GET",
            "path": base_path,
            "parameters": {},
        },
        {
            "name": f"get_{entity_name}",
            "description": f"Get a specific {entity_name} by ID",
            "method": "GET",
            "path": f"{base_path}/{{id}}",
            "parameters": id_param,
        },
        {
            "name": f"create_{entity_name}",
            "description": f"Create a new {entity_name}",
            "method": "POST",
            "path": base_path,
            "parameters": field_params,
        },
        {
            "name": f"update_{entity_name}",
            "description": f"Update an existing {entity_name}",
            "method": "PATCH",
            "path": f"{base_path}/{{id}}",
            "parameters": {**id_param, **field_params},
        },
        {
            "name": f"delete_{entity_name}",
            "description": f"Delete a {entity_name}",
            "method": "DELETE",
            "path": f"{base_path}/{{id}}",
            "parameters": id_param,
        },
    ]

    field_list = "\n".join(
        f"- **{f['name']}** ({f.get('type', 'string')})"
        + (f": {f['description']}" if f.get("description") else "")
        for f in fields
    )

    system_prompt = f"""You manage {entity_plural} for this organization.

## What you can do

- List all {entity_plural}
- Get details for a specific {entity_name}
- Create new {entity_plural}
- Update existing {entity_plural}
- Delete {entity_plural}

## {entity_name.capitalize()} fields

{field_list}

## Guidelines

Collect all required fields before creating a {entity_name}. Present data clearly. Confirm before deleting."""

    manifest = {
        "name": name,
        "slug": slug,
        "moduleType": module_type,
        "description": description,
        "category": category,
        "version": "1.0.0",
    }

    pricing: dict = {"type": pricing_type}
    if pricing_type == "paid" and price_cents:
        pricing["priceCents"] = price_cents
    elif pricing_type == "subscription" and monthly_price_cents:
        pricing["monthlyPriceCents"] = monthly_price_cents

    canonical = json.dumps({"manifest": manifest, "tools": tools, "systemPrompt": system_prompt, "pricing": pricing}, separators=(",", ":"))
    pkg_hash = hashlib.sha256(canonical.encode()).hexdigest()

    return {
        "manifest": manifest,
        "tools": tools,
        "systemPrompt": system_prompt,
        "pricing": pricing,
        "hash": pkg_hash,
        "packagedAt": datetime.now(timezone.utc).isoformat(),
    }


def validate_module(module_package: dict) -> dict:
    """Run security and completeness checks on a module package."""
    issues = []
    tools = module_package.get("tools", [])
    system_prompt = module_package.get("systemPrompt", "")
    manifest = module_package.get("manifest", {})

    # Manifest checks
    if not manifest.get("name") or len(manifest.get("name", "")) < 3:
        issues.append({"severity": "BLOCKER", "field": "manifest.name", "message": "Name must be at least 3 characters"})
    if not manifest.get("slug") or not re.match(r'^[a-z0-9-]+$', manifest.get("slug", "")):
        issues.append({"severity": "BLOCKER", "field": "manifest.slug", "message": "Slug must be lowercase letters, numbers, and hyphens"})

    # Tool checks
    if not tools:
        issues.append({"severity": "BLOCKER", "field": "tools", "message": "Module must define at least one tool"})
    if len(tools) > 50:
        issues.append({"severity": "BLOCKER", "field": "tools", "message": "Maximum 50 tools per module"})

    for tool in tools:
        path = tool.get("path", "")
        name = tool.get("name", "unknown")
        if not path.startswith("/api/v1/"):
            issues.append({"severity": "BLOCKER", "tool": name, "message": f"Path must start with /api/v1/, got: {path}"})
        for prefix in FORBIDDEN_PREFIXES:
            if path.startswith(prefix):
                issues.append({"severity": "BLOCKER", "tool": name, "message": f"Forbidden prefix: {prefix}"})
        if re.match(r'^https?://', path):
            issues.append({"severity": "BLOCKER", "tool": name, "message": "External URLs not allowed"})
        if tool.get("method") not in ["GET", "POST", "PATCH", "DELETE"]:
            issues.append({"severity": "BLOCKER", "tool": name, "message": f"Invalid method: {tool.get('method')}"})
        if not tool.get("description"):
            issues.append({"severity": "WARNING", "tool": name, "message": "Missing description"})

    # Prompt checks
    if not system_prompt or len(system_prompt) < 50:
        issues.append({"severity": "BLOCKER", "field": "systemPrompt", "message": "System prompt must be at least 50 characters"})
    if len(system_prompt) > 10000:
        issues.append({"severity": "WARNING", "field": "systemPrompt", "message": "System prompt exceeds 10,000 characters"})
    for pattern, label in INJECTION_PATTERNS:
        if re.search(pattern, system_prompt, re.IGNORECASE):
            issues.append({"severity": "BLOCKER", "field": "systemPrompt", "message": f"Injection pattern: {label}"})

    blockers = [i for i in issues if i["severity"] == "BLOCKER"]
    warnings = [i for i in issues if i["severity"] == "WARNING"]
    security_score = max(1, min(10, 10 - len(blockers) * 3 - len(warnings) * 0.5))

    return {
        "passed": len(blockers) == 0,
        "readyToPublish": len(blockers) == 0 and len(warnings) < 5,
        "issues": issues,
        "blockers": blockers,
        "warnings": warnings,
        "securityScore": round(security_score),
    }


def analyze_tools(tools: list, module_id: str) -> dict:
    """Static analysis of tool definitions (used by module_reviewer)."""
    issues = []
    for tool in tools:
        path = tool.get("path", "")
        name = tool.get("name", "unknown")
        if not path.startswith("/api/v1/"):
            issues.append({"severity": "BLOCKER", "tool": name, "message": f"Bad path: {path}"})
        for prefix in FORBIDDEN_PREFIXES:
            if path.startswith(prefix):
                issues.append({"severity": "BLOCKER", "tool": name, "message": f"Forbidden: {prefix}"})
        if re.match(r'^https?://', path):
            issues.append({"severity": "BLOCKER", "tool": name, "message": "External URL"})
        if tool.get("method") not in ["GET", "POST", "PATCH", "DELETE"]:
            issues.append({"severity": "BLOCKER", "tool": name, "message": f"Bad method: {tool.get('method')}"})

    blockers = [i for i in issues if i["severity"] == "BLOCKER"]
    return {
        "moduleId": module_id,
        "toolCount": len(tools),
        "issues": issues,
        "blockers": blockers,
        "securityScore": max(1, 10 - len(blockers) * 3),
        "passed": len(blockers) == 0,
    }


def analyze_prompt(system_prompt: str, module_id: str) -> dict:
    """Check system prompt for injection patterns."""
    found = []
    for pattern, label in INJECTION_PATTERNS:
        if re.search(pattern, system_prompt, re.IGNORECASE):
            found.append(label)
    return {
        "moduleId": module_id,
        "charCount": len(system_prompt),
        "hasSubstance": len(system_prompt) >= 50,
        "lengthOk": len(system_prompt) <= 10000,
        "injectionPatternsFound": found,
        "passed": len(found) == 0 and len(system_prompt) >= 50,
    }
