"""Tests for agent detection functionality."""

from mcp.types import Implementation, InitializeRequestParams
from src.mcp_server_guide.agent_detection import AGENT_PREFIX_MAP, AgentInfo, detect_agent, normalize_agent_name


def test_agent_info_creation():
    """Test AgentInfo dataclass creation."""
    info = AgentInfo(name="test-client", normalized_name="test", version="1.0.0", prompt_prefix="@")
    assert info.name == "test-client"
    assert info.normalized_name == "test"
    assert info.version == "1.0.0"
    assert info.prompt_prefix == "@"


def test_normalize_kiro():
    """Test normalization of Kiro/Amazon Q agents."""
    assert normalize_agent_name("kiro-cli") == "kiro"
    assert normalize_agent_name("amazon-q") == "kiro"
    assert normalize_agent_name("KIRO-CLI") == "kiro"
    assert normalize_agent_name("Q DEV CLI") == "kiro"
    assert normalize_agent_name("q dev cli") == "kiro"


def test_normalize_claude():
    """Test normalization of Claude agents."""
    assert normalize_agent_name("claude-desktop") == "claude"
    assert normalize_agent_name("claude-code") == "claude"
    assert normalize_agent_name("Claude") == "claude"


def test_normalize_cursor():
    """Test normalization of Cursor agents."""
    assert normalize_agent_name("cursor") == "cursor"
    assert normalize_agent_name("cursor-agent") == "cursor"
    assert normalize_agent_name("CURSOR") == "cursor"


def test_normalize_copilot():
    """Test normalization of Copilot agents."""
    assert normalize_agent_name("github-copilot") == "copilot"
    assert normalize_agent_name("copilot") == "copilot"


def test_normalize_gemini():
    """Test normalization of Gemini agents."""
    assert normalize_agent_name("gemini-cli") == "gemini"
    assert normalize_agent_name("gemini") == "gemini"


def test_normalize_windsurf():
    """Test normalization of Windsurf agents."""
    assert normalize_agent_name("windsurf") == "windsurf"


def test_normalize_unknown():
    """Test normalization of unknown agents."""
    assert normalize_agent_name("unknown-client") == "unknown"
    assert normalize_agent_name("some-random-agent") == "unknown"


def test_prefix_mapping():
    """Test agent prefix mapping."""
    assert AGENT_PREFIX_MAP["kiro"] == "@"
    assert AGENT_PREFIX_MAP["claude"] == "/{mcp_name}:"
    assert AGENT_PREFIX_MAP["cursor"] == "@"
    assert AGENT_PREFIX_MAP["copilot"] == "/"
    assert AGENT_PREFIX_MAP["gemini"] == "@"
    assert AGENT_PREFIX_MAP["windsurf"] == "/"


def test_detect_agent_kiro():
    """Test agent detection for Kiro."""
    params = InitializeRequestParams(
        protocolVersion="1.0", capabilities={}, clientInfo=Implementation(name="kiro-cli", version="1.0.0")
    )

    info = detect_agent(params)
    assert info.name == "kiro-cli"
    assert info.normalized_name == "kiro"
    assert info.version == "1.0.0"
    assert info.prompt_prefix == "@"


def test_detect_agent_claude():
    """Test agent detection for Claude."""
    params = InitializeRequestParams(
        protocolVersion="1.0", capabilities={}, clientInfo=Implementation(name="claude-desktop", version="2.0.0")
    )

    info = detect_agent(params)
    assert info.name == "claude-desktop"
    assert info.normalized_name == "claude"
    assert info.version == "2.0.0"
    assert info.prompt_prefix == "/{mcp_name}:"


def test_detect_agent_unknown():
    """Test agent detection for unknown agent."""
    params = InitializeRequestParams(
        protocolVersion="1.0", capabilities={}, clientInfo=Implementation(name="unknown-agent", version="1.0.0")
    )

    info = detect_agent(params)
    assert info.name == "unknown-agent"
    assert info.normalized_name == "unknown"
    assert info.version == "1.0.0"
    assert info.prompt_prefix == "/"  # Default fallback


import json
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest


@pytest.mark.asyncio
async def test_agent_info_returns_result_json_format():
    """Test that guide_get_agent_info returns Result.to_json() format."""
    from mcp_server_guide.agent_detection import AgentInfo
    from mcp_server_guide.tools.agent_tools import guide_get_agent_info

    # Mock context
    mock_ctx = MagicMock()
    mock_ctx.session.client_params.client_info.name = "test-agent"
    mock_ctx.session.client_params.client_info.version = "1.0.0"

    # Mock server
    mock_server = MagicMock()
    mock_server.name = "test-server"
    mock_server.extensions.agent_info = AgentInfo(
        name="test-agent", normalized_name="test", version="1.0.0", prompt_prefix="@"
    )

    with patch("mcp_server_guide.server.get_current_server", new=AsyncMock(return_value=mock_server)):
        result = await guide_get_agent_info(mock_ctx)

        # Should be JSON string with Result format
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "value" in parsed
        assert "instruction" in parsed
        assert "test-agent" in parsed["value"]


@pytest.mark.asyncio
async def test_agent_info_server_unavailable_error():
    """Server unavailable: get_current_server returns None -> error_type=server_unavailable."""
    from mcp_server_guide.tools.agent_tools import guide_get_agent_info

    mock_ctx = MagicMock()

    with patch("mcp_server_guide.server.get_current_server", new=AsyncMock(return_value=None)):
        result = await guide_get_agent_info(mock_ctx)

    parsed = json.loads(result)

    assert parsed["success"] is False
    assert parsed["error_type"] == "server_unavailable"
    assert "Server not available" in parsed["error"]


@pytest.mark.asyncio
async def test_agent_info_session_unavailable_error():
    """Session unavailable: accessing session.client_params raises AttributeError."""
    from mcp_server_guide.tools.agent_tools import guide_get_agent_info

    mock_ctx = MagicMock()
    mock_server = MagicMock()
    mock_server.extensions.agent_info = None

    # Make detect_agent raise AttributeError when accessing client_params
    with (
        patch("mcp_server_guide.server.get_current_server", new=AsyncMock(return_value=mock_server)),
        patch(
            "mcp_server_guide.tools.agent_tools.detect_agent", side_effect=AttributeError("client_params not available")
        ),
    ):
        result = await guide_get_agent_info(mock_ctx)

    parsed = json.loads(result)

    assert parsed["success"] is False
    assert parsed["error_type"] == "session_unavailable"
    assert "Agent detection requires an active MCP session" in parsed["error"]


@pytest.mark.asyncio
async def test_agent_info_unexpected_exception_error():
    """Unexpected exception: detect_agent raises -> error_type=unexpected and exception details."""
    from mcp_server_guide.tools.agent_tools import guide_get_agent_info

    mock_ctx = MagicMock()
    mock_server = MagicMock()
    mock_server.extensions.agent_info = None

    unexpected_error = RuntimeError("boom")

    with (
        patch("mcp_server_guide.server.get_current_server", new=AsyncMock(return_value=mock_server)),
        patch("mcp_server_guide.tools.agent_tools.detect_agent", side_effect=unexpected_error),
    ):
        result = await guide_get_agent_info(mock_ctx)

    parsed = json.loads(result)

    assert parsed["success"] is False
    assert parsed["error_type"] == "unexpected"
    # Exception diagnostics should be present
    assert parsed.get("exception_type") == "RuntimeError"
    assert parsed.get("exception_message") == "boom"
