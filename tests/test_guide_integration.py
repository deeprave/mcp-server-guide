"""Tests for minimal guide integration with document access."""

import pytest
from unittest.mock import patch
from mcp_server_guide.guide_integration import GuidePromptHandler


class TestGuidePromptIntegration:
    """Test guide prompt integration with minimal document access."""

    @pytest.mark.asyncio
    async def test_guide_prompt_document_access(self):
        """Test guide prompt supports category/document syntax."""
        handler = GuidePromptHandler()

        with patch("mcp_server_guide.guide_integration.get_category_content") as mock_get:
            mock_get.return_value = {"success": True, "content": "Document content"}

            # Test document access
            result = await handler.handle_guide_request(["docs/readme"])

            # Should call get_category_content with combined path
            mock_get.assert_called_once_with("docs/readme")
            assert result == "Document content"

    @pytest.mark.asyncio
    async def test_guide_prompt_category_access(self):
        """Test guide prompt maintains category access."""
        handler = GuidePromptHandler()

        with patch("mcp_server_guide.guide_integration.get_category_content") as mock_get:
            mock_get.return_value = {"success": True, "content": "Category content"}

            # Test category access
            result = await handler.handle_guide_request(["docs"])

            # Should call get_category_content with category name only
            mock_get.assert_called_once_with("docs")
            assert result == "Category content"

    @pytest.mark.asyncio
    async def test_guide_prompt_collection_fallback(self):
        """Test guide prompt falls back to collection access."""
        handler = GuidePromptHandler()

        with patch("mcp_server_guide.guide_integration.get_category_content") as mock_get_cat:
            with patch("mcp_server_guide.guide_integration.get_collection_content") as mock_get_col:
                mock_get_cat.return_value = {"success": False, "error": "Category not found"}
                mock_get_col.return_value = {"success": True, "content": "Collection content"}

                # Test collection fallback
                result = await handler.handle_guide_request(["my-collection"])

                # Should try category first, then collection
                mock_get_cat.assert_called_once_with("my-collection")
                mock_get_col.assert_called_once_with("my-collection")
                assert result == "Collection content"

    @pytest.mark.asyncio
    async def test_guide_prompt_error_handling(self):
        """Test guide prompt handles errors properly."""
        handler = GuidePromptHandler()

        with patch("mcp_server_guide.guide_integration.get_category_content") as mock_get_cat:
            with patch("mcp_server_guide.guide_integration.get_collection_content") as mock_get_col:
                mock_get_cat.return_value = {"success": False, "error": "Category not found"}
                mock_get_col.return_value = {"success": False, "error": "Collection not found"}

                # Test error handling
                result = await handler.handle_guide_request(["nonexistent"])

                # Should return category error
                assert "Category or collection 'nonexistent' not found." in result

    @pytest.mark.asyncio
    async def test_guide_prompt_no_args(self):
        """Test guide prompt with no arguments."""
        handler = GuidePromptHandler()

        result = await handler.handle_guide_request([])

        # Should return help message
        assert "category name" in result
        assert "docs/readme" in result
