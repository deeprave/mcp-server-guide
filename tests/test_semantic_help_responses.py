"""Tests for semantic help response handling."""

import pytest

from mcp_server_guide.help_system import format_guide_help


@pytest.mark.asyncio
async def test_user_focused_language():
    """Test that help content uses user-focused language."""
    help_content = await format_guide_help()

    # Should contain user-focused language and command information
    assert "Phase Commands:" in help_content or "Utility Commands:" in help_content

    # Should not contain agent-focused language
    assert "agents should" not in help_content.lower()
    assert "the agent" not in help_content.lower()
