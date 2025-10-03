"""Tests for DAIC command functionality."""

import pytest
from mcp_server_guide.server import mcp
from mcp.types import GetPromptResult


@pytest.mark.asyncio
async def test_daic_prompt_returns_current_state(tmp_path, monkeypatch):
    """Test that @daic returns current DAIC state."""
    # Change to temp directory for test isolation
    monkeypatch.chdir(tmp_path)
    # Set PWD environment variable for CurrentProjectManager
    monkeypatch.setenv("PWD", str(tmp_path))

    # Test ENABLED state (no .consent file)
    consent_file = tmp_path / ".consent"
    if consent_file.exists():
        consent_file.unlink()

    result = await mcp.get_prompt("daic", {})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "DAIC mode: ENABLED (Discussion-Alignment-Implementation-Check)" in result.messages[0].content.text

    # Test DISABLED state (.consent file exists)
    consent_file.touch()

    result = await mcp.get_prompt("daic", {})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "DAIC mode: DISABLED (Implementation allowed)" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_daic_prompt_error_when_client_dir_none(monkeypatch):
    """Test that @daic returns error when CurrentProjectManager.directory is None."""
    from mcp_server_guide.current_project_manager import CurrentProjectManager

    # Mock directory property to return None
    monkeypatch.setattr(CurrentProjectManager, "directory", property(lambda self: None))

    result = await mcp.get_prompt("daic", {})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "Error: Client working directory not available" in result.messages[0].content.text
