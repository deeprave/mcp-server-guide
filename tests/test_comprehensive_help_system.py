"""Tests for comprehensive help system."""

import pytest
from src.mcp_server_guide.help_system import format_guide_help, generate_context_help
from src.mcp_server_guide.guide_integration import GuidePromptHandler


class TestComprehensiveHelpSystem:
    """Test comprehensive help system functionality."""

    @pytest.mark.asyncio
    async def test_format_guide_help_comprehensive(self):
        """Test that comprehensive help includes all sections."""
        help_content = await format_guide_help()

        # Check for all major sections
        assert "# MCP Server Guide Help" in help_content
        assert "## For AI Agents" in help_content
        assert "## Complete CLI Interface" in help_content
        assert "## Available Prompts" in help_content
        assert "## Categories and Collections" in help_content
        assert "## Available Resources" in help_content
        assert "## Context-Sensitive Help" in help_content
        assert "## Troubleshooting" in help_content

    @pytest.mark.asyncio
    async def test_format_guide_help_includes_cli_help(self):
        """Test that help includes auto-generated CLI help."""
        help_content = await format_guide_help()

        # Should include Click-generated CLI help
        assert "Commands:" in help_content
        assert "category" in help_content
        assert "collection" in help_content
        assert "document" in help_content

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

        # Test general help
        result = await handler.handle_guide_request(["--help"])
        assert "MCP Server Guide Help" in result

        # Test context-sensitive help
        result = await handler.handle_guide_request(["category", "--help"])
        assert "Category management operations" in result

    @pytest.mark.asyncio
    async def test_ai_agent_guidance_included(self):
        """Test that AI agent guidance is included in help."""
        help_content = await format_guide_help()

        assert "When to use this MCP server:" in help_content
        assert "How to interact effectively:" in help_content
        assert "CLI Interface:" in help_content

    @pytest.mark.asyncio
    async def test_troubleshooting_section_included(self):
        """Test that troubleshooting section is comprehensive."""
        help_content = await format_guide_help()

        assert "Common Issues" in help_content
        assert "Category not found" in help_content
        assert "Debug Commands" in help_content
