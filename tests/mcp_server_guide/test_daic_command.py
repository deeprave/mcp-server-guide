"""Tests for DAIC command functionality."""

import os
import pytest
from pathlib import Path
from mcp_server_guide.server import mcp
from mcp.types import GetPromptResult


@pytest.mark.asyncio
async def test_daic_prompt_returns_current_state(tmp_path, monkeypatch):
    """Test that @daic returns current DAIC state."""

    # Change to test directory for PWD-based resolution
    original_cwd = Path.cwd()
    os.chdir(tmp_path)

    try:
        # Test ENABLED state (no .consent file)
        consent_file = tmp_path / ".consent"
        if consent_file.exists():
            consent_file.unlink()

        result = await mcp.get_prompt("daic", {})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert "DISCUSSION/ALIGNMENT mode" in result.messages[0].content.text
        assert "Discussion-Alignment-Implementation-Check" in result.messages[0].content.text

        # Test DISABLED state (.consent file exists)
        consent_file.touch()

        result = await mcp.get_prompt("daic", {})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert "IMPLEMENTATION/CHECK mode" in result.messages[0].content.text

    finally:
        # Restore original directory
        os.chdir(original_cwd)
