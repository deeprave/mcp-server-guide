"""Tests for CLI help system restoration."""

import pytest
from unittest.mock import patch
from mcp_server_guide.help_system import format_guide_help
from mcp_server_guide.cli_parser import parse_command
from mcp_server_guide.guide_integration import GuidePromptHandler


@pytest.mark.asyncio
async def test_format_guide_help_basic():
    """Test basic help formatting functionality."""
    help_text = await format_guide_help()

    assert isinstance(help_text, str)
    assert "MCP Server Guide Help" in help_text
    assert "Version:" in help_text
    assert "Description:" in help_text


@pytest.mark.asyncio
async def test_format_guide_help_includes_prompts():
    """Test help includes prompts section."""
    with patch("mcp_server_guide.tools.list_prompts") as mock_list_prompts:
        mock_list_prompts.return_value = {
            "success": True,
            "prompts": [{"name": "test_prompt", "description": "Test prompt", "arguments": []}],
        }

        help_text = await format_guide_help()

        assert "Available Prompts" in help_text
        assert "test_prompt" in help_text


@pytest.mark.asyncio
async def test_format_guide_help_includes_categories():
    """Test help includes categories section."""
    with patch("mcp_server_guide.tools.list_categories") as mock_list_categories:
        mock_list_categories.return_value = {
            "success": True,
            "categories": {"test_category": {"description": "Test category", "collections": []}},
        }

        help_text = await format_guide_help()

        assert "Categories and Collections" in help_text
        assert "test_category" in help_text


@pytest.mark.asyncio
async def test_format_guide_help_includes_resources():
    """Test help includes resources section."""
    with patch("mcp_server_guide.tools.list_resources") as mock_list_resources:
        mock_list_resources.return_value = {
            "success": True,
            "resources": [{"uri": "test://resource", "description": "Test resource"}],
        }

        help_text = await format_guide_help()

        assert "Available Resources" in help_text
        assert "test://resource" in help_text


@pytest.mark.asyncio
async def test_format_guide_help_handles_errors():
    """Test help handles errors gracefully."""
    with patch("mcp_server_guide.tools.list_prompts") as mock_list_prompts:
        mock_list_prompts.side_effect = Exception("Test error")

        help_text = await format_guide_help()

        assert "Error loading prompts" in help_text
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
    assert command.data is None

    command = parse_command(["--help"])
    assert command.type == "help"
    assert command.data is None


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

    with patch("mcp_server_guide.help_system.format_guide_help") as mock_help:
        mock_help.return_value = "Test help content"

        result = await handler.handle_guide_request(["-h"])

        assert result == "Test help content"
        mock_help.assert_called_once()


@pytest.mark.asyncio
async def test_guide_integration_handles_help_with_context():
    """Test guide integration handles help with context."""
    handler = GuidePromptHandler()

    with patch("mcp_server_guide.help_system.format_guide_help") as mock_help:
        mock_help.return_value = "Context-specific help"

        result = await handler.handle_guide_request(["-h", "planning"])

        assert result == "Context-specific help"
        mock_help.assert_called_once()  # No context parameter in original implementation


@pytest.mark.asyncio
async def test_guide_integration_handles_long_help_flag():
    """Test guide integration handles --help flag."""
    handler = GuidePromptHandler()

    with patch("mcp_server_guide.help_system.format_guide_help") as mock_help:
        mock_help.return_value = "Test help content"

        result = await handler.handle_guide_request(["--help"])

        assert result == "Test help content"
        mock_help.assert_called_once()
