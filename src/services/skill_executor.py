"""
SkillExecutor: Execute Custom Instance Skills (Layer 3)

Handles secure execution of webhook-based custom tools.
Skills are defined per-instance and executed when agents invoke them.
"""

import httpx
import json
import asyncio
from typing import Any, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.models import InstanceSkill


class SkillExecutionError(Exception):
    """Raised when skill execution fails."""

    def __init__(self, skill_name: str, message: str, status_code: Optional[int] = None):
        self.skill_name = skill_name
        self.status_code = status_code
        super().__init__(f"Skill '{skill_name}' failed: {message}")


class SkillExecutor:
    """
    Executes custom skills defined at the instance level.

    Skills are webhook-based tools that extend agent capabilities
    without modifying core agent code.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Lazy-initialize HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                follow_redirects=True,
            )
        return self._http_client

    async def close(self):
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def execute(
        self,
        skill: InstanceSkill,
        input_data: dict[str, Any],
        context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Execute a skill with the given input.

        Args:
            skill: The skill definition to execute
            input_data: Input data matching the skill's input_schema
            context: Optional execution context (instance_id, user_id, etc.)

        Returns:
            Skill execution result

        Raises:
            SkillExecutionError: If execution fails
        """
        if not skill.is_active:
            raise SkillExecutionError(skill.name, "Skill is inactive")

        # Validate input against schema
        self._validate_input(skill, input_data)

        # Execute based on type
        if skill.execution_type == "webhook":
            return await self._execute_webhook(skill, input_data, context)
        elif skill.execution_type == "internal":
            return await self._execute_internal(skill, input_data, context)
        else:
            raise SkillExecutionError(
                skill.name,
                f"Unknown execution type: {skill.execution_type}"
            )

    async def execute_by_name(
        self,
        instance_id: UUID,
        skill_name: str,
        input_data: dict[str, Any],
        context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Execute a skill by name for an instance.

        Args:
            instance_id: Instance the skill belongs to
            skill_name: Name of the skill to execute
            input_data: Input data for the skill
            context: Optional execution context

        Returns:
            Skill execution result
        """
        # Load skill from database
        result = await self.db.execute(
            select(InstanceSkill)
            .where(
                InstanceSkill.instance_id == instance_id,
                InstanceSkill.name == skill_name,
            )
        )
        skill = result.scalar_one_or_none()

        if not skill:
            raise SkillExecutionError(skill_name, "Skill not found")

        return await self.execute(skill, input_data, context)

    def _validate_input(self, skill: InstanceSkill, input_data: dict[str, Any]):
        """
        Validate input against skill's JSON schema.
        Basic validation - can be enhanced with jsonschema library.
        """
        schema = skill.input_schema
        if not schema:
            return

        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in input_data:
                raise SkillExecutionError(
                    skill.name,
                    f"Missing required field: {field}"
                )

        # Check field types (basic)
        properties = schema.get("properties", {})
        for field, value in input_data.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type and not self._check_type(value, expected_type):
                    raise SkillExecutionError(
                        skill.name,
                        f"Invalid type for {field}: expected {expected_type}"
                    )

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected JSON Schema type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        expected = type_map.get(expected_type)
        if expected is None:
            return True  # Unknown type, skip validation
        return isinstance(value, expected)

    async def _execute_webhook(
        self,
        skill: InstanceSkill,
        input_data: dict[str, Any],
        context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Execute a webhook-based skill."""
        if not skill.webhook_url:
            raise SkillExecutionError(skill.name, "No webhook URL configured")

        # Build headers
        headers = dict(skill.webhook_headers or {})
        headers["Content-Type"] = "application/json"

        # Add authentication
        if skill.webhook_auth:
            auth_type = skill.webhook_auth.get("type")
            if auth_type == "bearer":
                token = skill.webhook_auth.get("token")
                headers["Authorization"] = f"Bearer {token}"
            elif auth_type == "api_key":
                header_name = skill.webhook_auth.get("header", "X-API-Key")
                api_key = skill.webhook_auth.get("value")
                headers[header_name] = api_key

        # Build request body
        body = {
            "input": input_data,
            "context": context or {},
            "skill": {
                "name": skill.name,
                "instance_id": str(skill.instance_id),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Execute with retries
        last_error = None
        for attempt in range(skill.retry_count + 1):
            try:
                response = await self.http_client.request(
                    method=skill.webhook_method or "POST",
                    url=skill.webhook_url,
                    headers=headers,
                    json=body,
                    timeout=skill.timeout_seconds or 30,
                )

                if response.status_code >= 400:
                    raise SkillExecutionError(
                        skill.name,
                        f"HTTP {response.status_code}: {response.text[:200]}",
                        status_code=response.status_code,
                    )

                # Parse response
                try:
                    result = response.json()
                except json.JSONDecodeError:
                    result = {"raw_response": response.text}

                return {
                    "success": True,
                    "data": result,
                    "status_code": response.status_code,
                }

            except httpx.TimeoutException:
                last_error = SkillExecutionError(skill.name, "Request timed out")
            except httpx.RequestError as e:
                last_error = SkillExecutionError(skill.name, f"Request failed: {e}")
            except SkillExecutionError:
                raise

            # Wait before retry
            if attempt < skill.retry_count:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        raise last_error or SkillExecutionError(skill.name, "Unknown error")

    async def _execute_internal(
        self,
        skill: InstanceSkill,
        input_data: dict[str, Any],
        context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Execute an internal skill.
        Internal skills are predefined handlers for common operations.
        """
        # Internal skill registry
        internal_handlers = {
            "erp_query": self._handle_erp_query,
            "cache_lookup": self._handle_cache_lookup,
            "format_output": self._handle_format_output,
        }

        handler_name = skill.webhook_url  # Reuse field for internal handler name
        handler = internal_handlers.get(handler_name)

        if not handler:
            raise SkillExecutionError(
                skill.name,
                f"Unknown internal handler: {handler_name}"
            )

        return await handler(input_data, context)

    async def _handle_erp_query(
        self, input_data: dict, context: Optional[dict]
    ) -> dict:
        """Internal handler for ERP queries."""
        # Placeholder - would integrate with ERP API
        return {"success": True, "data": {"message": "ERP query placeholder"}}

    async def _handle_cache_lookup(
        self, input_data: dict, context: Optional[dict]
    ) -> dict:
        """Internal handler for cache lookups."""
        # Placeholder - would integrate with Redis
        return {"success": True, "data": {"cached": False}}

    async def _handle_format_output(
        self, input_data: dict, context: Optional[dict]
    ) -> dict:
        """Internal handler for output formatting."""
        # Placeholder - would apply formatting rules
        return {"success": True, "data": input_data}

    def skill_to_tool_schema(self, skill: InstanceSkill) -> dict:
        """
        Convert a skill to Claude tool schema format.
        Used when injecting skills into agent tools.
        """
        return {
            "name": skill.name,
            "description": skill.description,
            "input_schema": skill.input_schema or {
                "type": "object",
                "properties": {},
            },
        }
