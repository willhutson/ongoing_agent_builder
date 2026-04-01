"""Tests for action_reporter and CoreToolkit._report integration."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import httpx
from unittest.mock import AsyncMock, patch
from src.services.action_reporter import report_action


class TestReportAction:
    """Tests for report_action — fire-and-forget behavior is critical."""

    @pytest.mark.asyncio
    async def test_payload_format(self):
        """report_action sends correct payload structure."""
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            mock_client.post = AsyncMock()

            await report_action(
                org_id="org_123",
                action="task.created",
                entity_type="TASK",
                entity_id="task_456",
                entity_title="Write proposal",
                agent_type="core_tasks",
            )

            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args

            # Check headers
            headers = call_kwargs.kwargs["headers"]
            assert headers["X-Org-Id"] == "org_123"
            assert headers["Content-Type"] == "application/json"

            # Check payload structure
            payload = call_kwargs.kwargs["json"]
            assert payload["entryType"] == "PATTERN"
            assert payload["category"] == "agent.action"
            assert payload["key"] == "task.created:task_456"
            assert payload["confidence"] == 1.0

            value = payload["value"]
            assert value["action"] == "task.created"
            assert value["entityType"] == "TASK"
            assert value["entityId"] == "task_456"
            assert value["entityTitle"] == "Write proposal"
            assert value["agentType"] == "core_tasks"
            assert "timestamp" in value

    @pytest.mark.asyncio
    async def test_network_error_does_not_raise(self):
        """Network failures must not propagate — fire-and-forget."""
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

            # Must not raise
            await report_action(
                org_id="org_123",
                action="task.created",
                entity_type="TASK",
                entity_id="task_456",
                entity_title="Test Task",
                agent_type="core_tasks",
            )

    @pytest.mark.asyncio
    async def test_timeout_does_not_raise(self):
        """Timeouts must not propagate."""
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

            await report_action(
                org_id="org_123",
                action="task.created",
                entity_type="TASK",
                entity_id="task_456",
                entity_title="Test Task",
                agent_type="core_tasks",
            )

    @pytest.mark.asyncio
    async def test_metadata_included_in_value(self):
        """Optional metadata is merged into the value dict."""
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            mock_client.post = AsyncMock()

            await report_action(
                org_id="org_123",
                action="task.created",
                entity_type="TASK",
                entity_id="task_456",
                entity_title="Test Task",
                agent_type="core_tasks",
                metadata={"priority": "high", "assignee": "user_789"},
            )

            payload = mock_client.post.call_args.kwargs["json"]
            assert payload["value"]["priority"] == "high"
            assert payload["value"]["assignee"] == "user_789"


class TestCoreToolkitReport:
    """Tests for the _report helper method on CoreToolkit."""

    @pytest.mark.asyncio
    async def test_report_extracts_id_from_flat_response(self):
        """_report handles flat response: {"id": ..., "title": ...}."""
        from src.tools.core_toolkit import CoreToolkit

        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"

        with patch("src.tools.core_toolkit.report_action", new_callable=AsyncMock) as mock_report:
            await toolkit._report(
                action="task.created",
                entity_type="TASK",
                result={"id": "task_abc", "title": "My Task", "status": "TODO"},
                agent_type="core_tasks",
            )
            mock_report.assert_called_once_with(
                org_id="org_123",
                action="task.created",
                entity_type="TASK",
                entity_id="task_abc",
                entity_title="My Task",
                agent_type="core_tasks",
            )

    @pytest.mark.asyncio
    async def test_report_extracts_name_field(self):
        """_report falls back to 'name' field for entity_title."""
        from src.tools.core_toolkit import CoreToolkit

        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"

        with patch("src.tools.core_toolkit.report_action", new_callable=AsyncMock) as mock_report:
            await toolkit._report(
                action="project.created",
                entity_type="PROJECT",
                result={"id": "proj_abc", "name": "Q2 Campaign"},
                agent_type="core_projects",
            )
            mock_report.assert_called_once()
            assert mock_report.call_args.kwargs["entity_title"] == "Q2 Campaign"

    @pytest.mark.asyncio
    async def test_report_skips_on_error_response(self):
        """_report does not call report_action if response contains 'error'."""
        from src.tools.core_toolkit import CoreToolkit

        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"

        with patch("src.tools.core_toolkit.report_action", new_callable=AsyncMock) as mock_report:
            await toolkit._report(
                action="task.created",
                entity_type="TASK",
                result={"error": "Not found", "id": "task_abc"},
                agent_type="core_tasks",
            )
            mock_report.assert_not_called()

    @pytest.mark.asyncio
    async def test_report_skips_when_no_entity_id(self):
        """_report does not call report_action if no entity ID can be extracted."""
        from src.tools.core_toolkit import CoreToolkit

        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"

        with patch("src.tools.core_toolkit.report_action", new_callable=AsyncMock) as mock_report:
            await toolkit._report(
                action="task.created",
                entity_type="TASK",
                result={"title": "No ID response"},
                agent_type="core_tasks",
            )
            mock_report.assert_not_called()

    @pytest.mark.asyncio
    async def test_report_exception_does_not_propagate(self):
        """_report swallows exceptions from report_action."""
        from src.tools.core_toolkit import CoreToolkit

        toolkit = CoreToolkit.__new__(CoreToolkit)
        toolkit.org_id = "org_123"

        with patch("src.tools.core_toolkit.report_action", new_callable=AsyncMock, side_effect=RuntimeError("boom")) as mock_report:
            # Must not raise
            await toolkit._report(
                action="task.created",
                entity_type="TASK",
                result={"id": "task_abc", "title": "Test"},
                agent_type="core_tasks",
            )
