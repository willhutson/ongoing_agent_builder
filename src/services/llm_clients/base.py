"""
Base client class for external LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any
from enum import Enum
import httpx
import asyncio


class TaskStatus(str, Enum):
    """Status of an async generation task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GenerationResult:
    """Result from a generation task."""
    success: bool
    task_id: Optional[str] = None
    status: TaskStatus = TaskStatus.COMPLETED
    output_url: Optional[str] = None
    output_data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None


class BaseExternalLLMClient(ABC):
    """Base class for external LLM API clients."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: float = 60.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-initialize the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self._get_headers(),
            )
        return self._client

    def _get_headers(self) -> dict:
        """Get default headers. Override in subclasses for different auth schemes."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _post(self, endpoint: str, data: dict) -> dict:
        """Make a POST request."""
        response = await self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()

    async def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a GET request."""
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    async def _poll_status(
        self,
        task_id: str,
        status_endpoint: str,
        interval: float = 2.0,
        max_attempts: int = 150,  # 5 minutes at 2s intervals
    ) -> GenerationResult:
        """Poll for task completion."""
        for _ in range(max_attempts):
            result = await self._get(f"{status_endpoint}/{task_id}")
            status = self._parse_status(result)

            if status == TaskStatus.COMPLETED:
                return self._parse_completed_result(result)
            elif status == TaskStatus.FAILED:
                return GenerationResult(
                    success=False,
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error=result.get("error", "Unknown error"),
                )

            await asyncio.sleep(interval)

        return GenerationResult(
            success=False,
            task_id=task_id,
            status=TaskStatus.FAILED,
            error="Timeout waiting for task completion",
        )

    @abstractmethod
    def _parse_status(self, result: dict) -> TaskStatus:
        """Parse task status from API response. Override in subclasses."""
        pass

    @abstractmethod
    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse completed result from API response. Override in subclasses."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the API is accessible."""
        pass
