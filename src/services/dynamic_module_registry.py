"""
Dynamic Module Registry — holds runtime-registered marketplace module agents.

When a user installs a marketplace module, spokestack-core calls
POST /api/v1/modules/register and the module's agent is registered here.

In-memory for now — reloads on restart are handled by re-registration.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class DynamicModuleAgent:
    module_type: str
    system_prompt: str
    tools: list[dict]
    org_id: str
    agent_name: str
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DynamicModuleRegistry:
    def __init__(self):
        self._registry: dict[str, DynamicModuleAgent] = {}

    def register(self, module_type: str, system_prompt: str, tools: list[dict],
                 org_id: str, agent_name: str) -> None:
        self._registry[module_type] = DynamicModuleAgent(
            module_type=module_type, system_prompt=system_prompt,
            tools=tools, org_id=org_id, agent_name=agent_name,
        )

    def get(self, module_type: str) -> Optional[DynamicModuleAgent]:
        return self._registry.get(module_type)

    def has(self, module_type: str) -> bool:
        return module_type in self._registry

    def list_all(self) -> list[DynamicModuleAgent]:
        return list(self._registry.values())

    def unregister(self, module_type: str) -> bool:
        return self._registry.pop(module_type, None) is not None


# Singleton
dynamic_registry = DynamicModuleRegistry()
