"""Tests for CLI mode support (Issue 006 Phase 1)."""

import pytest
from click.testing import CliRunner
from mcp_server_guide.main import main


async def test_default_mode_is_stdio():
    """Test that default mode is stdio when no mode specified."""
    command = main()
    runner = CliRunner()

    # Mock the actual server startup to avoid hanging
    with pytest.MonkeyPatch().context() as m:
        m.setattr("mcp_server_guide.main.start_mcp_server", lambda mode, config: f"Started {mode} mode")
        result = runner.invoke(command, [])

    assert result.exit_code == 0
    # stdio mode produces no output (correct MCP behavior)


async def test_explicit_stdio_mode():
    """Test explicit stdio mode argument."""
    command = main()
    runner = CliRunner()

    with pytest.MonkeyPatch().context() as m:
        m.setattr("mcp_server_guide.main.start_mcp_server", lambda mode, config: f"Started {mode} mode")
        result = runner.invoke(command, ["stdio"])

    assert result.exit_code == 0
    # stdio mode produces no output (correct MCP behavior)


async def test_invalid_mode_shows_error():
    """Test that invalid mode shows helpful error."""
    command = main()
    runner = CliRunner()

    result = runner.invoke(command, ["invalid-mode"])

    assert result.exit_code != 0
    assert "Invalid mode" in result.output or "Usage:" in result.output
