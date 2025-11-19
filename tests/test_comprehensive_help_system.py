"""Tests for comprehensive help system."""

import pytest
from src.mcp_server_guide.help_system import format_guide_help, generate_context_help
from src.mcp_server_guide.guide_integration import GuidePromptHandler


class TestComprehensiveHelpSystem:
    """Test comprehensive help system functionality."""

    @pytest.mark.asyncio
    async def test_format_guide_help_comprehensive(self):
        """Test that comprehensive help includes key sections."""
        help_content = await format_guide_help(verbose=True)

        # Check for major sections that still exist
        assert "# MCP Server Guide Help" in help_content
        assert "Commands:" in help_content
        assert "clone" in help_content  # New clone command
        assert "## Categories and Collections" in help_content

    @pytest.mark.asyncio
    async def test_format_guide_help_basic(self):
        """Test that basic help shows only CLI usage."""
        help_content = await format_guide_help(verbose=False)

        # Check for basic CLI content
        assert "Usage:  [OPTIONS] COMMAND [ARGS]..." in help_content
        assert "MCP Server Guide - Project documentation and guidelines." in help_content
        assert "Use --verbose or -v for more detailed information" in help_content

        # Should NOT contain comprehensive sections
        assert "# MCP Server Guide Help" not in help_content
        assert "## Available Prompts" not in help_content

    @pytest.mark.asyncio
    async def test_format_guide_help_includes_cli_help(self):
        """Test that comprehensive help includes CLI interface info."""
        help_content = await format_guide_help(verbose=True)

        # Should include CLI commands
        assert "Commands:" in help_content
        assert "category" in help_content
        assert "collection" in help_content

    def test_generate_context_help_category(self):
        """Test context-sensitive help for categories."""
        help_content = generate_context_help("category")

        assert "Category management operations" in help_content
        assert "add" in help_content
        assert "list" in help_content
        assert "remove" in help_content

    def test_generate_context_help_collection(self):
        """Test context-sensitive help for collections."""
        help_content = generate_context_help("collection")

        assert "Collection management operations" in help_content
        assert "add" in help_content
        assert "list" in help_content

    def test_generate_context_help_document(self):
        """Test context-sensitive help for documents."""
        help_content = generate_context_help("document")

        assert "Document management operations" in help_content
        assert "create" in help_content
        assert "list" in help_content

    @pytest.mark.asyncio
    async def test_guide_integration_help_command(self):
        """Test guide integration handles help commands."""
        handler = GuidePromptHandler()

        # Test general help (basic)
        result = await handler.handle_guide_request(["--help"])
        assert "Use --verbose or -v for more detailed information" in result

        # Test verbose help (comprehensive)
        result = await handler.handle_guide_request(["--help", "--verbose"])
        assert "MCP Server Guide Help" in result

        # Test context-sensitive help
        result = await handler.handle_guide_request(["category", "--help"])
        assert "Category management operations" in result

    @pytest.mark.asyncio
    async def test_prompts_section_included(self):
        """Test that help includes commands section."""
        help_content = await format_guide_help(verbose=True)

        assert "Commands:" in help_content

