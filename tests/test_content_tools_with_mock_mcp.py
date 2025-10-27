"""Tests for content_tools.py error paths using MockMCP."""

import pytest
from unittest.mock import patch, AsyncMock
from mcp_server_guide.tools.content_tools import get_content


class TestContentToolsWithMockMCP:
    """Tests for content_tools error paths."""

    @pytest.mark.asyncio
    async def test_get_content_category_exception_with_logging(self):
        """Test get_content category exception with logging."""
        with (
            patch("mcp_server_guide.tools.content_tools.CategoryDocumentCache") as mock_cache,
            patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_cat,
            patch("mcp_server_guide.tools.content_tools.get_collection_document") as mock_col,
        ):
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            mock_cat.side_effect = Exception("Category error")
            mock_col.return_value = {"success": False}

            result = await get_content("test", "doc")
            assert result is None
            mock_cache.set.assert_called()

    @pytest.mark.asyncio
    async def test_get_content_both_exceptions_critical_logging(self):
        """Test get_content with both category and collection exceptions."""
        with (
            patch("mcp_server_guide.tools.content_tools.CategoryDocumentCache") as mock_cache,
            patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_cat,
            patch("mcp_server_guide.tools.content_tools.get_collection_document") as mock_col,
        ):
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            mock_cat.side_effect = Exception("Category error")
            mock_col.side_effect = Exception("Collection error")

            result = await get_content("test", "doc")
            assert result is None
            mock_cache.set.assert_called()

    @pytest.mark.asyncio
    async def test_get_content_collection_only_exception(self):
        """Test get_content with only collection exception."""
        with (
            patch("mcp_server_guide.tools.content_tools.CategoryDocumentCache") as mock_cache,
            patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_cat,
            patch("mcp_server_guide.tools.content_tools.get_collection_document") as mock_col,
        ):
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            mock_cat.side_effect = Exception("Category error")
            mock_col.side_effect = Exception("Collection error")

            result = await get_content("test", "doc")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_content_cache_failed_collection_lookup(self):
        """Test get_content caching failed collection lookup."""
        with (
            patch("mcp_server_guide.tools.content_tools.CategoryDocumentCache") as mock_cache,
            patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_cat,
            patch("mcp_server_guide.tools.content_tools.get_collection_document") as mock_col,
        ):
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            mock_cat.side_effect = Exception("Category error")
            mock_col.return_value = {"success": False}

            result = await get_content("test", "doc")
            assert result is None
            # Verify cache.set was called to cache the failed lookup
            assert mock_cache.set.call_count >= 1
