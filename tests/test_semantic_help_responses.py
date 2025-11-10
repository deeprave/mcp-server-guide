"""Tests for semantic help response handling."""

import pytest
from mcp_server_guide.cli_parser_click import detect_help_request
from mcp_server_guide.help_system import format_guide_help


def test_show_vs_get_semantics():
    """Test that show vs get requests are detected differently."""
    # Test show semantics
    show_result = detect_help_request(["show", "help"])
    assert show_result is not None
    assert show_result.semantic_intent == "display"

    # Test get semantics
    get_result = detect_help_request(["get", "help"])
    assert get_result is not None
    assert get_result.semantic_intent == "retrieve"


@pytest.mark.asyncio
async def test_user_focused_language():
    """Test that help content uses user-focused language."""
    help_content = await format_guide_help()

    # Should contain user-focused language
    assert "you can" in help_content.lower()
    assert "your" in help_content.lower()

    # Should not contain agent-focused language
    assert "agents should" not in help_content.lower()
    assert "the agent" not in help_content.lower()
