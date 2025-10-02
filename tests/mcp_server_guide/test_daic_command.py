"""Tests for DAIC command functionality."""

import pytest
from pathlib import Path
from mcp_server_guide.server import mcp
from mcp.types import GetPromptResult


@pytest.mark.asyncio
async def test_daic_prompt_returns_current_state(tmp_path, monkeypatch):
    """Test that @daic returns current DAIC state."""
    # Change to temp directory for test isolation
    monkeypatch.chdir(tmp_path)

    # Test DISABLED state (no .consent file)
    consent_file = Path(".consent")
    if consent_file.exists():
        consent_file.unlink()

    result = await mcp.get_prompt("daic", {})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "DAIC state: DISABLED" in result.messages[0].content.text

    # Test ENABLED state (.consent file exists)
    consent_file.touch()

    result = await mcp.get_prompt("daic", {})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "DAIC state: ENABLED" in result.messages[0].content.text
