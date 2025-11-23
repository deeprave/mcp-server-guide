"""Tests for explicit action parameters in MCP document functions."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_server_guide.tools.document_tools import (
    create_mcp_document,
    delete_mcp_document,
    update_mcp_document,
)


class TestDocumentExplicitActions:
    """Test explicit action parameter requirements."""

    @pytest.mark.asyncio
    async def test_create_mcp_document_requires_explicit_action(self):
        """Test that create_mcp_document fails without explicit_action parameter."""
        with pytest.raises(TypeError, match="missing.*required.*explicit_action"):
            await create_mcp_document(category_dir="test", name="test.md", content="test content")

    @pytest.mark.asyncio
    async def test_update_mcp_document_requires_explicit_action(self):
        """Test that update_mcp_document fails without explicit_action parameter."""
        with pytest.raises(TypeError, match="missing.*required.*explicit_action"):
            await update_mcp_document(category_dir="test", name="test.md", content="updated content")

    @pytest.mark.asyncio
    async def test_delete_mcp_document_requires_explicit_action(self):
        """Test that delete_mcp_document fails without explicit_action parameter."""
        with pytest.raises(TypeError, match="missing.*required.*explicit_action"):
            await delete_mcp_document(category_dir="test", name="test.md")

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools._validate_document_name", return_value=True)
    @patch("mcp_server_guide.tools.document_tools._validate_content_size", return_value=True)
    @patch("mcp_server_guide.tools.document_tools.add_category", new_callable=AsyncMock)
    @patch("mcp_server_guide.tools.document_tools.lock_update", new_callable=AsyncMock)
    async def test_create_mcp_document_succeeds_with_correct_action(
        self, mock_lock, mock_add_cat, mock_size, mock_name
    ):
        """Test that create_mcp_document succeeds with correct explicit_action."""
        mock_lock.return_value.__aenter__ = AsyncMock(return_value=None)
        mock_lock.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await create_mcp_document(
            category_dir="test", name="test.md", content="test content", explicit_action="CREATE_DOCUMENT"
        )

        assert isinstance(result, dict)
        # Function should execute without raising exceptions

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools.Path.exists", return_value=True)
    @patch("mcp_server_guide.tools.document_tools.lock_update", new_callable=AsyncMock)
    async def test_update_mcp_document_succeeds_with_correct_action(self, mock_lock, mock_exists):
        """Test that update_mcp_document succeeds with correct explicit_action."""
        mock_lock.return_value.__aenter__ = AsyncMock(return_value=None)
        mock_lock.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await update_mcp_document(
            category_dir="test", name="test.md", content="updated content", explicit_action="UPDATE_DOCUMENT"
        )

        assert isinstance(result, dict)
        # Function should execute without raising exceptions

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools.Path.exists", return_value=True)
    @patch("mcp_server_guide.tools.document_tools.Path.unlink")
    async def test_delete_mcp_document_succeeds_with_correct_action(self, mock_unlink, mock_exists):
        """Test that delete_mcp_document succeeds with correct explicit_action."""
        result = await delete_mcp_document(category_dir="test", name="test.md", explicit_action="DELETE_DOCUMENT")

        assert isinstance(result, dict)
        # Function should execute without raising exceptions
