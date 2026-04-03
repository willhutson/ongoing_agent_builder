"""
Sandbox Executor — executes module tools in an isolated context.

Uses a dedicated sandbox org (SANDBOX_ORG_ID). Cleans up after each run.
Never touches real org data.
"""

import logging
import os
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

SANDBOX_ORG_ID = os.getenv("SANDBOX_ORG_ID", "sandbox-test-org-000")
SANDBOX_AUTH_TOKEN = os.getenv("SANDBOX_AUTH_TOKEN", "")
CORE_URL = os.getenv("SPOKESTACK_CORE_URL", "https://spokestack-core.vercel.app")
AGENT_SECRET = os.getenv("AGENT_RUNTIME_SECRET", "")


class SandboxExecutor:

    def __init__(self, api_base_url: str = None):
        self.api_base_url = api_base_url or CORE_URL
        self.created_ids: dict[str, list[str]] = {}

    async def run_module_tests(self, module_package: dict) -> dict:
        """Run all tools in a module against the sandbox org."""
        tools = module_package.get("tools", [])

        if not SANDBOX_AUTH_TOKEN and not AGENT_SECRET:
            return {
                "passed": False,
                "error": "SANDBOX_AUTH_TOKEN or AGENT_RUNTIME_SECRET not configured",
                "results": [],
            }

        ordered = self._order_tools(tools)
        results = []

        for tool in ordered:
            result = await self._execute_tool_test(tool)
            results.append(result)

        await self._cleanup()

        passed_count = sum(1 for r in results if r["passed"])
        return {
            "passed": all(r["passed"] for r in results),
            "toolCount": len(results),
            "passedCount": passed_count,
            "failedCount": len(results) - passed_count,
            "results": results,
        }

    def _order_tools(self, tools: list[dict]) -> list[dict]:
        order = {"POST": 0, "GET": 1, "PATCH": 2, "DELETE": 3}
        return sorted(tools, key=lambda t: order.get(t.get("method", "GET"), 1))

    async def _execute_tool_test(self, tool: dict) -> dict:
        method = tool.get("method", "GET")
        path = tool.get("path", "")
        tool_name = tool.get("name", "unknown")

        actual_path = self._substitute_path_params(path)
        url = f"{self.api_base_url}{actual_path}"
        body = self._generate_test_data(tool.get("parameters", {}), tool_name) if method in ["POST", "PATCH"] else None

        headers = {
            "Content-Type": "application/json",
            "X-Agent-Secret": AGENT_SECRET,
            "X-Organization-Id": SANDBOX_ORG_ID,
        }

        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                kwargs: dict[str, Any] = {"url": url, "headers": headers}
                if body:
                    kwargs["json"] = body
                response = await getattr(client, method.lower())(**kwargs)
                elapsed_ms = round((time.monotonic() - start) * 1000)

                passed = response.status_code in [200, 201, 204]

                if method == "POST" and response.is_success:
                    try:
                        data = response.json()
                        created_id = data.get("id")
                        if created_id:
                            entity = actual_path.split("/api/v1/")[1].split("/")[0] if "/api/v1/" in actual_path else ""
                            if entity:
                                self.created_ids.setdefault(entity, []).append(created_id)
                    except Exception:
                        pass

                return {
                    "tool": tool_name, "method": method, "path": actual_path,
                    "passed": passed, "statusCode": response.status_code,
                    "elapsedMs": elapsed_ms, "slow": elapsed_ms > 3000, "error": None,
                }
        except httpx.TimeoutException:
            return {"tool": tool_name, "method": method, "path": actual_path,
                    "passed": False, "statusCode": None, "elapsedMs": 10000,
                    "slow": True, "error": "Timeout (10s)"}
        except Exception as e:
            return {"tool": tool_name, "method": method, "path": actual_path,
                    "passed": False, "statusCode": None, "elapsedMs": 0,
                    "slow": False, "error": str(e)}

    def _substitute_path_params(self, path: str) -> str:
        if "{id}" not in path:
            return path
        entity = path.split("/api/v1/")[1].split("/")[0] if "/api/v1/" in path else ""
        ids = self.created_ids.get(entity, [])
        if ids:
            return path.replace("{id}", ids[-1])
        return path.replace("{id}", "sandbox-nonexistent-id")

    def _generate_test_data(self, parameters: dict, tool_name: str) -> dict:
        data = {}
        name_overrides = {
            "name": f"Sandbox Test ({tool_name})",
            "title": f"Sandbox Test ({tool_name})",
            "email": "sandbox@test.spokestack.dev",
            "status": "ACTIVE",
            "address": "123 Sandbox Street",
        }
        type_defaults = {"string": "test-value", "number": 100, "boolean": True, "array": [], "object": {}}
        for pname, pdef in parameters.items():
            if pname == "id":
                continue
            if pname in name_overrides:
                data[pname] = name_overrides[pname]
            elif isinstance(pdef, dict) and pdef.get("enum"):
                data[pname] = pdef["enum"][0]
            else:
                ptype = pdef.get("type", "string") if isinstance(pdef, dict) else "string"
                data[pname] = type_defaults.get(ptype, "test-value")
        return data

    async def _cleanup(self) -> None:
        async with httpx.AsyncClient(timeout=5.0) as client:
            headers = {"X-Agent-Secret": AGENT_SECRET, "X-Organization-Id": SANDBOX_ORG_ID}
            for entity, ids in self.created_ids.items():
                for rid in ids:
                    try:
                        await client.delete(f"{self.api_base_url}/api/v1/{entity}/{rid}", headers=headers)
                    except Exception:
                        pass
        self.created_ids.clear()
