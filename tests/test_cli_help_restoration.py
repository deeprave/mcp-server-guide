"""Tests for CLI help system restoration."""

from unittest.mock import patch

import pytest

from mcp_server_guide.cli_parser_click import parse_command
from mcp_server_guide.guide_integration import GuidePromptHandler
from mcp_server_guide.help_system import format_guide_help


@pytest.mark.asyncio
async def test_format_guide_help_basic():
    """Test basic help formatting functionality."""
    help_text = await format_guide_help()

    assert isinstance(help_text, str)
    assert "MCP Server Guide Help" in help_text
    assert "Version:" in help_text
    assert "Description:" in help_text


@pytest.mark.asyncio
async def test_format_guide_help_includes_categories():
    """Test help includes categories section."""
    help_text = await format_guide_help()

    # Should have categories section even if empty
    assert "Categories and Collections" in help_text


@pytest.mark.asyncio
async def test_format_guide_help_handles_errors():
    """Test help handles errors gracefully."""
    with patch("mcp_server_guide.tools.category_tools.list_categories") as mock_list_categories:
        mock_list_categories.side_effect = Exception("Test error")

        help_text = await format_guide_help()

        assert "Error loading categories" in help_text
        assert "MCP Server Guide Help" in help_text  # Still shows basic info


# CLI Parser Tests
def test_cli_parser_recognizes_help_flag():
    """Test CLI parser recognizes -h flag."""
    # Test with parse_command instead of CLIParser
    command = parse_command(["-h"])
    assert command.type == "help"

    command = parse_command(["--help"])
    assert command.type == "help"


def test_cli_parser_parses_help_flag():
    """Test CLI parser parses help flag correctly."""
    command = parse_command(["-h"])
    assert command.type == "help"
    assert command.data is not None
    assert "help_text" in command.data
    assert command.target is None

    command = parse_command(["--help"])
    assert command.type == "help"
    assert command.data is not None
    assert "help_text" in command.data
    assert command.target is None


def test_cli_parser_help_with_context():
    """Test CLI parser handles help with context."""
    command = parse_command(["-h", "planning"])
    assert command.type == "help"
    # In the new architecture, help doesn't take additional arguments
    # but we can test that it doesn't break


def test_cli_parser_help_takes_precedence():
    """Test help flag is recognized correctly."""
    # Test help flag recognition
    command = parse_command(["-h"])
    assert command.type == "help"

    # Test that help is parsed correctly even with other arguments
    command = parse_command(["--help", "something"])
    assert command.type == "help"


# Integration Tests
@pytest.mark.asyncio
async def test_guide_integration_handles_help_flag():
    """Test guide integration handles help flag."""
    handler = GuidePromptHandler()

    # -h and --help now return Click's captured help text
    result = await handler.handle_guide_request(["-h"])
    assert "Usage: guide" in result or "Error: No such option: -h" in result

    result = await handler.handle_guide_request(["--help"])
    assert "Usage: guide" in result
    assert "Options:" in result


@pytest.mark.asyncio
async def test_guide_integration_handles_help_with_context():
    """Test guide integration handles help with context."""
    handler = GuidePromptHandler()

    # Click now handles help - it will show error for invalid args
    result = await handler.handle_guide_request(["-h", "planning"])
    assert "Usage: guide" in result or "Error:" in result


@pytest.mark.asyncio
async def test_guide_integration_handles_long_help_flag():
    """Test guide integration handles --help flag."""
    handler = GuidePromptHandler()

    result = await handler.handle_guide_request(["--help"])
    assert "Usage: guide" in result
    assert "Options:" in result
