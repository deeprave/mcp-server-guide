"""Tests for document tools error handling paths."""

import pytest
from unittest.mock import patch
from mcp_server_guide.tools.document_tools import (
    create_mcp_document,
    update_mcp_document,
    delete_mcp_document,
    list_mcp_documents,
    _validate_content_size,
)


class TestValidationErrorPaths:
    """Test validation function error paths."""

    def test_validate_content_size_exceeds_limit(self):
        """Test content size validation with oversized content."""
        large_content = "x" * (11 * 1024 * 1024)  # 11MB > 10MB default limit
        assert _validate_content_size(large_content) is False

    def test_validate_content_size_custom_limit(self):
        """Test content size validation with custom limit."""
        content = "x" * 1000
        assert _validate_content_size(content, max_size=500) is False
        assert _validate_content_size(content, max_size=2000) is True


class TestCreateDocumentErrorPaths:
    """Test create_mcp_document error handling."""

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools._get_docs_dir")
    async def test_create_document_file_not_found_error(self, mock_get_docs_dir):
        """Test FileNotFoundError handling in create_mcp_document."""
        mock_get_docs_dir.side_effect = FileNotFoundError("Directory not found")

        result = await create_mcp_document("test_category", "test.txt", "content", explicit_action="CREATE_DOCUMENT")

        assert result["success"] is False
        assert result["error_type"] == "not_found"
        assert "Directory not found" in result["error"]

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools._get_docs_dir")
    async def test_create_document_permission_error(self, mock_get_docs_dir):
        """Test PermissionError handling in create_mcp_document."""
        mock_get_docs_dir.side_effect = PermissionError("Permission denied")

        result = await create_mcp_document("test_category", "test.txt", "content", explicit_action="CREATE_DOCUMENT")

        assert result["success"] is False
        assert result["error_type"] == "permission"
        assert "Permission denied" in result["error"]

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools._get_docs_dir")
    async def test_create_document_os_error(self, mock_get_docs_dir):
        """Test OSError handling in create_mcp_document."""
        mock_get_docs_dir.side_effect = OSError("File system error")

        result = await create_mcp_document("test_category", "test.txt", "content", explicit_action="CREATE_DOCUMENT")

        assert result["success"] is False
        assert result["error_type"] == "filesystem"
        assert "File system error" in result["error"]

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools._get_docs_dir")
    async def test_create_document_unexpected_error(self, mock_get_docs_dir):
        """Test generic Exception handling in create_mcp_document."""
        mock_get_docs_dir.side_effect = RuntimeError("Unexpected error")

        result = await create_mcp_document("test_category", "test.txt", "content", explicit_action="CREATE_DOCUMENT")

        assert result["success"] is False
        assert result["error_type"] == "unexpected"
        assert "Unexpected error" in result["error"]


class TestUpdateDocumentErrorPaths:
    """Test update_mcp_document error handling."""

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools._get_docs_dir")
    async def test_update_document_permission_error(self, mock_get_docs_dir):
        """Test PermissionError handling in update_mcp_document."""
        mock_get_docs_dir.side_effect = PermissionError("Permission denied")

        result = await update_mcp_document("test_category", "test.txt", "content", explicit_action="UPDATE_DOCUMENT")

        assert result["success"] is False
        assert result["error_type"] == "permission"

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools._get_docs_dir")
    async def test_update_document_os_error(self, mock_get_docs_dir):
        """Test OSError handling in update_mcp_document."""
        mock_get_docs_dir.side_effect = OSError("File system error")

        result = await update_mcp_document("test_category", "test.txt", "content", explicit_action="UPDATE_DOCUMENT")

        assert result["success"] is False
        assert result["error_type"] == "filesystem"


class TestDeleteDocumentErrorPaths:
    """Test delete_mcp_document error handling."""

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools._get_docs_dir")
    async def test_delete_document_permission_error(self, mock_get_docs_dir):
        """Test PermissionError handling in delete_mcp_document."""
        mock_get_docs_dir.side_effect = PermissionError("Permission denied")

        result = await delete_mcp_document("test_category", "test.txt", explicit_action="DELETE_DOCUMENT")

        assert result["success"] is False
        assert result["error_type"] == "permission"

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools._get_docs_dir")
    async def test_delete_document_unexpected_error(self, mock_get_docs_dir):
        """Test generic Exception handling in delete_mcp_document."""
        mock_get_docs_dir.side_effect = RuntimeError("Unexpected error")

        result = await delete_mcp_document("test_category", "test.txt", explicit_action="DELETE_DOCUMENT")

        assert result["success"] is False
        assert result["error_type"] == "unexpected"


class TestListDocumentsErrorPaths:
    """Test list_mcp_documents error handling."""

    @pytest.mark.asyncio
    @patch("mcp_server_guide.tools.document_tools._get_docs_dir")
    async def test_list_documents_os_error(self, mock_get_docs_dir):
        """Test OSError handling in list_mcp_documents."""
        mock_get_docs_dir.side_effect = OSError("File system error")

        result = await list_mcp_documents("test_category")

        assert result["success"] is False
        assert result["error_type"] == "filesystem"
