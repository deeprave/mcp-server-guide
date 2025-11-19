"""Additional tests for help_system.py to improve coverage."""

import pytest
from unittest.mock import patch
from mcp_server_guide.help_system import format_guide_help, generate_context_help


class TestHelpSystemAdditional:
    """Additional tests for help system functionality."""

    @pytest.mark.asyncio
    async def test_format_guide_help_categories_error(self):
        """Test help formatting when categories loading fails."""
        with patch("mcp_server_guide.tools.category_tools.list_categories") as mock_list_categories:
            mock_list_categories.side_effect = Exception("Categories failed")

            result = await format_guide_help()
            assert "Error loading categories: Categories failed" in result

    @pytest.mark.asyncio
    async def test_format_guide_help_categories_unsuccessful_result(self):
        """Test help formatting when categories returns unsuccessful result."""
        with patch("mcp_server_guide.tools.category_tools.list_categories") as mock_list_categories:
            mock_list_categories.return_value = {"success": False, "error": "No categories found"}

            result = await format_guide_help()
            assert "Error loading categories: No categories found" in result

    @pytest.mark.asyncio
    async def test_format_guide_help_empty_categories(self):
        """Test help formatting with empty categories."""
        with patch("mcp_server_guide.tools.category_tools.list_categories") as mock_list_categories:
            mock_list_categories.return_value = {"success": True, "categories": {}}

            result = await format_guide_help()
            assert "No categories available" in result

    @pytest.mark.asyncio
    async def test_format_guide_help_categories_with_collections(self):
        """Test help formatting with categories that have collections."""
        with patch("mcp_server_guide.tools.category_tools.list_categories") as mock_list_categories:
            mock_list_categories.return_value = {
                "success": True,
                "categories": {
                    "test_category": {
                        "description": "Test category description",
                        "collections": ["collection1", "collection2"],
                    }
                },
            }

            result = await format_guide_help()
            assert "test_category" in result
            assert "Test category description" in result

    def test_generate_context_help_error_handling(self):
        """Test context help generation error handling."""
        with patch("mcp_server_guide.cli_parser_click.generate_context_help") as mock_context_help:
            mock_context_help.side_effect = Exception("Context help failed")

            result = generate_context_help("category", "add")
            assert "Error generating help for category: Context help failed" in result

    def test_generate_context_help_success(self):
        """Test successful context help generation."""
        with patch("mcp_server_guide.cli_parser_click.generate_context_help") as mock_context_help:
            mock_context_help.return_value = "Context help content"

            result = generate_context_help("category", "add")
            assert "Context help content" in result

    def test_generate_context_help_none_target(self):
        """Test context help generation with None target."""
        with patch("mcp_server_guide.cli_parser_click.generate_context_help") as mock_context_help:
            mock_context_help.return_value = "General help content"

            result = generate_context_help(None, "add")
            assert "General help content" in result
