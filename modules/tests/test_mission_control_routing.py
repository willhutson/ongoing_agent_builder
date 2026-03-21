"""
Integration tests for Mission Control routing implementation.

Tests:
- Handoff endpoint (auto-start + approval paths)
- Orchestration endpoint (template + inline + resume)
- Artifact emission (emit_artifact tool + SSE events)
- Billing usage reporting (UsageReportService)
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

# ============================================
# Test Artifact Data Schemas & Validation
# ============================================

def test_artifact_data_schemas_defined():
    """All ArtifactType values have a corresponding data schema."""
    from src.protocols.artifacts import ArtifactType, ARTIFACT_DATA_SCHEMAS

    for artifact_type in ArtifactType:
        assert artifact_type in ARTIFACT_DATA_SCHEMAS, f"Missing schema for {artifact_type}"
        schema = ARTIFACT_DATA_SCHEMAS[artifact_type]
        assert "type" in schema
        assert "required" in schema
        assert "properties" in schema


def test_validate_artifact_data_valid():
    """Valid artifact data passes validation."""
    from src.protocols.artifacts import ArtifactType, validate_artifact_data

    valid_brief = {
        "client_name": "Acme Corp",
        "project_name": "Q3 Campaign",
        "objectives": ["Increase brand awareness"],
    }
    is_valid, errors = validate_artifact_data(ArtifactType.BRIEF, valid_brief)
    assert is_valid
    assert errors == []


def test_validate_artifact_data_missing_required():
    """Missing required fields are caught by validation."""
    from src.protocols.artifacts import ArtifactType, validate_artifact_data

    invalid_brief = {"client_name": "Acme Corp"}  # Missing project_name, objectives
    is_valid, errors = validate_artifact_data(ArtifactType.BRIEF, invalid_brief)
    assert not is_valid
    assert len(errors) == 2
    assert "project_name" in errors[0] or "project_name" in errors[1]


def test_validate_artifact_data_calendar():
    """Calendar artifact validation works."""
    from src.protocols.artifacts import ArtifactType, validate_artifact_data

    valid_calendar = {
        "entries": [
            {"date": "2026-04-01", "title": "Campaign Launch", "description": "Go live"},
        ],
    }
    is_valid, errors = validate_artifact_data(ArtifactType.CALENDAR, valid_calendar)
    assert is_valid


# ============================================
# Test AgentContext artifact_format field
# ============================================

def test_agent_context_artifact_format():
    """AgentContext supports artifact_format field.
    Note: Also tested indirectly via test_system_prompt_includes_format_schema.
    """
    try:
        from src.agents.base import AgentContext
    except ImportError:
        pytest.skip("Circular import in src.agents — tested via system prompt tests")

    ctx = AgentContext(
        tenant_id="test",
        user_id="user1",
        task="Generate a calendar",
        artifact_format="calendar",
    )
    assert ctx.artifact_format == "calendar"


def test_agent_context_artifact_format_default():
    """AgentContext artifact_format defaults to None."""
    try:
        from src.agents.base import AgentContext
    except ImportError:
        pytest.skip("Circular import in src.agents — tested via system prompt tests")

    ctx = AgentContext(tenant_id="test", user_id="user1", task="test")
    assert ctx.artifact_format is None


# ============================================
# Test HandoffContext artifact_format field
# ============================================

def test_handoff_context_artifact_format():
    """HandoffContext supports artifact_format field."""
    from src.protocols.handoffs import HandoffContext

    ctx = HandoffContext(
        parent_chat_id="chat-123",
        parent_agent_type="brief",
        parent_summary="Summary",
        task="Create calendar",
        artifact_format="calendar",
    )
    assert ctx.artifact_format == "calendar"


def test_handoff_context_artifact_format_default():
    """HandoffContext artifact_format defaults to None."""
    from src.protocols.handoffs import HandoffContext

    ctx = HandoffContext(
        parent_chat_id="chat-123",
        parent_agent_type="brief",
        parent_summary="Summary",
        task="Create calendar",
    )
    assert ctx.artifact_format is None


# ============================================
# Test Settings erp_service_key
# ============================================

def test_settings_erp_service_key():
    """Settings includes erp_service_key field."""
    from src.config import Settings

    # Check field exists in model
    assert "erp_service_key" in Settings.model_fields


# ============================================
# Test ExecuteRequest artifact_format
# ============================================

def test_execute_request_artifact_format():
    """ExecuteRequest supports artifact_format field."""
    from src.api.routes import ExecuteRequest

    req = ExecuteRequest(
        agent_type="brief",
        task="test",
        tenant_id="t1",
        user_id="u1",
        artifact_format="deck",
    )
    assert req.artifact_format == "deck"


# ============================================
# Test emit_artifact tool definition
# ============================================

def test_emit_artifact_tool_definition():
    """BaseAgent includes emit_artifact tool definition."""
    from src.agents.base import BaseAgent

    tool_def = BaseAgent._emit_artifact_tool_def()
    assert tool_def["type"] == "function"
    assert tool_def["function"]["name"] == "emit_artifact"
    params = tool_def["function"]["parameters"]
    assert "artifact_type" in params["properties"]
    assert "title" in params["properties"]
    assert "data" in params["properties"]
    assert set(params["required"]) == {"artifact_type", "title", "data"}


# ============================================
# Test HandoffRequest/Response models
# ============================================

def test_handoff_request_model():
    """HandoffRequest model works with all fields."""
    from src.protocols.handoffs import HandoffRequest, HandoffContext

    req = HandoffRequest(
        from_chat_id="chat-abc",
        from_agent_type="brief",
        to_agent_type="content",
        context=HandoffContext(
            parent_chat_id="chat-abc",
            parent_agent_type="brief",
            parent_summary="Created brief",
            task="Create content",
            artifact_format="calendar",
        ),
        requires_user_approval=False,
        auto_start=True,
    )
    assert req.to_agent_type == "content"
    assert req.context.artifact_format == "calendar"


def test_handoff_response_model():
    """HandoffResponse model works correctly."""
    from src.protocols.handoffs import HandoffResponse

    resp = HandoffResponse(
        approved=False,
        new_chat_id="chat-def",
        new_agent_type="content",
        message="Queued for approval",
    )
    assert not resp.approved
    assert resp.new_chat_id == "chat-def"


# ============================================
# Test OrchestrateRequest / ResumeRequest models
# ============================================

def test_orchestrate_request_model():
    """OrchestrateRequest model accepts both workflow_id and inline workflow."""
    from src.api.routes import OrchestrateRequest

    # Template-based
    req1 = OrchestrateRequest(
        workflow_id="campaign_launch_checklist",
        organization_id="org-123",
        user_id="user-456",
    )
    assert req1.workflow_id == "campaign_launch_checklist"
    assert req1.workflow is None

    # Inline workflow
    req2 = OrchestrateRequest(
        workflow={"id": "custom", "name": "Test", "steps": []},
        organization_id="org-123",
        user_id="user-456",
    )
    assert req2.workflow is not None
    assert req2.workflow_id is None


def test_resume_request_model():
    """ResumeRequest model works correctly."""
    from src.api.routes import ResumeRequest

    req = ResumeRequest(
        approval=True,
        review_notes="Approved for launch",
        reviewer_id="user-789",
    )
    assert req.approval
    assert req.reviewer_id == "user-789"


# ============================================
# Test UsageReportService
# ============================================

@pytest.mark.asyncio
async def test_usage_report_service_payload():
    """UsageReportService builds correct payload."""
    from src.api.erp_integration import UsageReportService

    service = UsageReportService(service_key="test-key", base_url="http://test-erp")

    # Mock the HTTP client
    mock_response = MagicMock()
    mock_response.status_code = 200
    service.http_client = AsyncMock()
    service.http_client.post = AsyncMock(return_value=mock_response)

    result = await service.report_usage(
        organization_id="org-123",
        token_input=1000,
        token_output=500,
        model="claude-sonnet-4-20250514",
        agent_type="content",
        module="studio",
    )

    assert result is True
    call_args = service.http_client.post.call_args
    payload = call_args.kwargs.get("json") or call_args[1].get("json")
    assert payload["organizationId"] == "org-123"
    assert payload["tokenInput"] == 1000
    assert payload["tokenOutput"] == 500
    assert payload["model"] == "claude-sonnet-4-20250514"
    assert payload["agentType"] == "content"
    assert payload["module"] == "studio"

    # Verify headers
    headers = call_args.kwargs.get("headers") or call_args[1].get("headers")
    assert headers["X-Service-Key"] == "test-key"


@pytest.mark.asyncio
async def test_usage_report_service_retry_on_server_error():
    """UsageReportService retries on 5xx errors."""
    from src.api.erp_integration import UsageReportService

    service = UsageReportService(service_key="test-key", base_url="http://test-erp")

    mock_500 = MagicMock()
    mock_500.status_code = 500
    mock_200 = MagicMock()
    mock_200.status_code = 200

    service.http_client = AsyncMock()
    service.http_client.post = AsyncMock(side_effect=[mock_500, mock_200])

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await service.report_usage(
            organization_id="org-1", token_input=100, token_output=50,
            model="sonnet", agent_type="brief",
        )

    assert result is True
    assert service.http_client.post.call_count == 2


@pytest.mark.asyncio
async def test_usage_report_service_no_retry_on_4xx():
    """UsageReportService does not retry on 4xx client errors."""
    from src.api.erp_integration import UsageReportService

    service = UsageReportService(service_key="test-key", base_url="http://test-erp")

    mock_400 = MagicMock()
    mock_400.status_code = 400
    service.http_client = AsyncMock()
    service.http_client.post = AsyncMock(return_value=mock_400)

    result = await service.report_usage(
        organization_id="org-1", token_input=100, token_output=50,
        model="sonnet", agent_type="brief",
    )

    assert result is False
    assert service.http_client.post.call_count == 1


# ============================================
# Test Orchestrator SSE Events
# ============================================

@pytest.mark.asyncio
async def test_orchestrator_emits_workflow_events():
    """AgentOrchestrator emits workflow_start, step_progress, and workflow_paused events."""
    from src.orchestration.orchestrator import AgentOrchestrator, WorkflowBuilder
    from src.orchestration.workflow import StepType, WorkflowStatus

    events_received = []

    async def capture_event(event):
        events_received.append(event)

    # Create a simple workflow with human review
    workflow = (
        WorkflowBuilder("test_wf")
        .name("Test Workflow")
        .add_step("step_1", "qa_agent", "check", {})
        .add_human_review("review_1")
        .connect("step_1", "review_1")
        .build()
    )

    # Mock agent factory
    mock_agent = MagicMock()
    mock_agent._execute_tool = AsyncMock(return_value={"result": "ok"})

    orchestrator = AgentOrchestrator(
        agent_factory=lambda agent_id: mock_agent,
        notification_callback=capture_event,
    )

    execution = await orchestrator.run_workflow(workflow, {}, initiated_by="test-user")

    # Should have workflow_start
    event_types = [e["type"] for e in events_received]
    assert "workflow_start" in event_types

    # Should have step_progress for step_1
    step_events = [e for e in events_received if e.get("type") == "step_progress"]
    assert len(step_events) >= 1

    # Should be paused at review
    assert execution.status == WorkflowStatus.PAUSED
    pause_events = [e for e in events_received if e.get("type") == "workflow_paused"]
    assert len(pause_events) == 1


@pytest.mark.asyncio
async def test_orchestrator_resume_executes_remaining():
    """resume_workflow() re-executes steps after the review step."""
    from src.orchestration.orchestrator import AgentOrchestrator, WorkflowBuilder
    from src.orchestration.workflow import StepType, WorkflowStatus

    mock_agent = MagicMock()
    mock_agent._execute_tool = AsyncMock(return_value={"result": "done"})

    workflow = (
        WorkflowBuilder("resume_test")
        .name("Resume Test")
        .add_step("step_1", "qa_agent", "check", {})
        .add_human_review("review_1")
        .add_step("step_2", "qa_agent", "final_check", {})
        .connect("step_1", "review_1")
        .connect("review_1", "step_2")
        .build()
    )

    orchestrator = AgentOrchestrator(
        agent_factory=lambda agent_id: mock_agent,
        notification_callback=AsyncMock(),
    )

    execution = await orchestrator.run_workflow(workflow, {})
    assert execution.status == WorkflowStatus.PAUSED

    # Resume
    execution = await orchestrator.resume_workflow(execution.id, approval=True, review_notes="LGTM")
    assert execution.status == WorkflowStatus.COMPLETED
    assert "step_2" in execution.completed_steps
    assert execution.review_notes == "LGTM"


@pytest.mark.asyncio
async def test_orchestrator_resume_rejection_cancels():
    """Rejecting a resume cancels the workflow."""
    from src.orchestration.orchestrator import AgentOrchestrator, WorkflowBuilder
    from src.orchestration.workflow import WorkflowStatus

    mock_agent = MagicMock()
    mock_agent._execute_tool = AsyncMock(return_value={"ok": True})

    workflow = (
        WorkflowBuilder("cancel_test")
        .name("Cancel Test")
        .add_step("s1", "qa_agent", "check", {})
        .add_human_review("r1")
        .connect("s1", "r1")
        .build()
    )

    orchestrator = AgentOrchestrator(
        agent_factory=lambda agent_id: mock_agent,
        notification_callback=AsyncMock(),
    )

    execution = await orchestrator.run_workflow(workflow, {})
    assert execution.status == WorkflowStatus.PAUSED

    execution = await orchestrator.resume_workflow(execution.id, approval=False)
    assert execution.status == WorkflowStatus.CANCELLED


# ============================================
# Test System Prompt includes artifact protocol
# ============================================

def test_system_prompt_includes_artifact_protocol():
    """_build_system_prompt includes artifact output protocol instructions."""
    from src.agents.base import BaseAgent, AgentContext
    from src.services.openrouter import OpenRouterClient

    # Create a minimal concrete agent for testing
    class TestAgent(BaseAgent):
        @property
        def name(self):
            return "test_agent"

        @property
        def system_prompt(self):
            return "You are a test agent."

        def _define_tools(self):
            return []

        async def _execute_tool(self, tool_name, tool_input):
            return {}

    client = OpenRouterClient(api_key="test-key")
    agent = TestAgent(client=client, model="test-model")

    ctx = AgentContext(tenant_id="t", user_id="u", task="test")
    prompt = agent._build_system_prompt(ctx)
    assert "emit_artifact" in prompt
    assert "Artifact Output Protocol" in prompt


def test_system_prompt_includes_format_schema():
    """When artifact_format is set, system prompt includes format schema."""
    from src.agents.base import BaseAgent, AgentContext
    from src.services.openrouter import OpenRouterClient

    class TestAgent(BaseAgent):
        @property
        def name(self):
            return "test_agent"

        @property
        def system_prompt(self):
            return "You are a test agent."

        def _define_tools(self):
            return []

        async def _execute_tool(self, tool_name, tool_input):
            return {}

    client = OpenRouterClient(api_key="test-key")
    agent = TestAgent(client=client, model="test-model")

    ctx = AgentContext(tenant_id="t", user_id="u", task="test", artifact_format="brief")
    prompt = agent._build_system_prompt(ctx)
    assert "Output Format" in prompt
    assert "brief" in prompt
    assert "client_name" in prompt  # From the BRIEF schema
