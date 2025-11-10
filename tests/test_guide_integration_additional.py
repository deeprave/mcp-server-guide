"""Additional tests for guide_integration.py to improve coverage."""

import pytest
from unittest.mock import patch
from mcp_server_guide.guide_integration import GuidePromptHandler
from mcp_server_guide.cli_parser_click import Command


class TestGuideIntegrationAdditional:
    """Additional tests for guide integration functionality."""

    @pytest.mark.asyncio
    async def test_handle_content_command_no_category(self):
        """Test _handle_content_command with no category."""
        handler = GuidePromptHandler()
        command = Command(type="content", category=None)

        result = await handler._handle_content_command(command)
        assert "Error: No category specified" in result

    @pytest.mark.asyncio
    async def test_get_content_with_document_path(self):
        """Test _get_content with category/document path."""
        handler = GuidePromptHandler()

        with patch("mcp_server_guide.guide_integration.get_category_content") as mock_get:
            mock_get.return_value = {"success": True, "content": "Document content"}

            result = await handler._get_content("category/document.md")
            assert "Document content" in result
            mock_get.assert_called_once_with("category", file="document.md")

    @pytest.mark.asyncio
    async def test_get_content_category_fails_collection_succeeds(self):
        """Test _get_content when category fails but collection succeeds."""
        handler = GuidePromptHandler()

        with (
            patch("mcp_server_guide.guide_integration.get_category_content") as mock_cat,
            patch("mcp_server_guide.guide_integration.get_collection_content") as mock_col,
        ):
            mock_cat.return_value = {"success": False, "error": "Category not found"}
            mock_col.return_value = {"success": True, "content": "Collection content"}

            result = await handler._get_content("test")
            assert "Collection content" in result

    @pytest.mark.asyncio
    async def test_get_content_both_fail(self):
        """Test _get_content when both category and collection fail."""
        handler = GuidePromptHandler()

        with (
            patch("mcp_server_guide.guide_integration.get_category_content") as mock_cat,
            patch("mcp_server_guide.guide_integration.get_collection_content") as mock_col,
        ):
            mock_cat.return_value = {"success": False, "error": "Category not found"}
            mock_col.return_value = {"success": False, "error": "Collection not found"}

            result = await handler._get_content("test")
            assert "Error: Category not found" in result

    @pytest.mark.asyncio
    async def test_handle_search_command(self):
        """Test handling of search command."""
        handler = GuidePromptHandler()

        with patch("mcp_server_guide.guide_integration.parse_command") as mock_parse:
            mock_parse.return_value = Command(type="search", data="test query")

            result = await handler.handle_guide_request(["search", "test", "query"])
            assert "Search functionality not yet implemented" in result
            assert "test query" in result

    @pytest.mark.asyncio
    async def test_handle_category_access_no_category(self):
        """Test category access with no category specified."""
        handler = GuidePromptHandler()

        with patch("mcp_server_guide.guide_integration.parse_command") as mock_parse:
            mock_parse.return_value = Command(type="category_access", category=None)

            result = await handler.handle_guide_request(["category"])
            assert "No category specified" in result

    @pytest.mark.asyncio
    async def test_handle_help_with_target(self):
        """Test help command with specific target."""
        handler = GuidePromptHandler()

        with (
            patch("mcp_server_guide.guide_integration.parse_command") as mock_parse,
            patch("mcp_server_guide.help_system.generate_context_help") as mock_help,
        ):
            mock_parse.return_value = Command(type="help", target="category")
            mock_help.return_value = "Context help for category"

            result = await handler.handle_guide_request(["help", "category"])
            assert "Context help for category" in result

    @pytest.mark.asyncio
    async def test_handle_help_general(self):
        """Test general help command."""
        handler = GuidePromptHandler()

        with (
            patch("mcp_server_guide.guide_integration.parse_command") as mock_parse,
            patch("mcp_server_guide.help_system.format_guide_help") as mock_help,
        ):
            mock_parse.return_value = Command(type="help", target=None)
            mock_help.return_value = "General help content"

            result = await handler.handle_guide_request(["help"])
            assert "General help content" in result

    @pytest.mark.asyncio
    async def test_unknown_command_fallback_to_content(self):
        """Test unknown command falling back to content lookup."""
        handler = GuidePromptHandler()

        with (
            patch("mcp_server_guide.guide_integration.parse_command") as mock_parse,
            patch.object(handler, "_get_content") as mock_get,
        ):
            mock_parse.return_value = Command(type="unknown")
            mock_get.return_value = "Content from fallback"

            result = await handler.handle_guide_request(["test"])
            assert "Content from fallback" in result

    @pytest.mark.asyncio
    async def test_unknown_command_with_options(self):
        """Test unknown command with options (not single arg)."""
        handler = GuidePromptHandler()

        with patch("mcp_server_guide.guide_integration.parse_command") as mock_parse:
            mock_parse.return_value = Command(type="unknown")

            result = await handler.handle_guide_request(["--unknown", "option"])
            assert "Error: Unknown command format" in result
