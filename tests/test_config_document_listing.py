"""Tests for config document listing."""

import pytest
from unittest.mock import patch
from src.mcp_server_guide.prompts import _list_category_documents


@pytest.mark.asyncio
async def test_list_category_documents():
    """List documents in a category."""
    with patch("src.mcp_server_guide.tools.document_tools.list_mcp_documents") as mock_list:
        mock_list.return_value = {"success": True, "documents": [{"name": "doc1.md"}, {"name": "doc2.txt"}]}

        result = await _list_category_documents("cat1")
        assert "doc1.md" in result
        assert "doc2.txt" in result


@pytest.mark.asyncio
async def test_list_category_documents_empty():
    """List documents when category has no documents."""
    with patch("src.mcp_server_guide.tools.document_tools.list_mcp_documents") as mock_list:
        mock_list.return_value = {"success": True, "documents": []}

        result = await _list_category_documents("cat1")
        assert result == []


@pytest.mark.asyncio
async def test_list_category_documents_error():
    """Handle errors when listing documents - exception propagates."""
    with patch("src.mcp_server_guide.tools.document_tools.list_mcp_documents") as mock_list:
        mock_list.side_effect = Exception("Test error")

        with pytest.raises(Exception, match="Test error"):
            await _list_category_documents("cat1")
