"""Tests for document tools docroot functionality."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from mcp_server_guide.constants import DOCUMENT_SUBDIR


class TestDocumentToolsDocroot:
    """Test document tools use docroot correctly."""

    @pytest.mark.asyncio
    async def test_create_mcp_document_uses_docroot(self):
        """Test that create_mcp_document uses docroot to resolve category paths."""
        from mcp_server_guide.tools.document_tools import create_mcp_document
        from mcp_server_guide.path_resolver import LazyPath

        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up docroot and category structure
            docroot_path = Path(temp_dir) / "docroot"
            docroot_path.mkdir()

            category_path = docroot_path / "review"
            category_path.mkdir()

            # Mock SessionManager to return our test docroot
            with patch("mcp_server_guide.tools.document_tools.SessionManager") as mock_session_class:
                mock_session = Mock()
                # Simplified mock
                mock_session.docroot = LazyPath(str(docroot_path))

                mock_session_class.return_value = mock_session

                # Create document with relative category path
                result = await create_mcp_document(
                    category_dir="review",  # Relative path - should use docroot
                    name="test.md",
                    content="# Test Document\n\nThis is a test.",
                )

                # Should succeed
                assert result["success"] is True
                assert "test.md" in result["message"]

                # Verify file was created in docroot/review/__docs__/
                expected_path = docroot_path / "review" / DOCUMENT_SUBDIR / "test.md"
                assert expected_path.exists()
                assert expected_path.read_text() == "# Test Document\n\nThis is a test."

    @pytest.mark.asyncio
    async def test_create_mcp_document_fallback_to_current_dir(self):
        """Test that create_mcp_document falls back to current directory when no docroot."""
        from mcp_server_guide.tools.document_tools import create_mcp_document

        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Mock SessionManager to return None docroot
                with patch("mcp_server_guide.tools.document_tools.SessionManager") as mock_session_class:
                    mock_session = Mock()
                    # Simplified mock
                    mock_session.docroot = None  # No docroot configured

                    mock_session_class.return_value = mock_session

                    # Create document with relative category path
                    result = await create_mcp_document(
                        category_dir="review",  # Should use current directory
                        name="test.md",
                        content="# Test Document",
                    )

                    # Should succeed
                    assert result["success"] is True

                    # Verify file was created in current_dir/review/__docs__/
                    expected_path = Path(temp_dir) / "review" / DOCUMENT_SUBDIR / "test.md"
                    assert expected_path.exists()

            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_update_mcp_document_uses_docroot(self):
        """Test that update_mcp_document uses docroot to resolve category paths."""
        from mcp_server_guide.tools.document_tools import create_mcp_document, update_mcp_document
        from mcp_server_guide.path_resolver import LazyPath

        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up docroot and category structure
            docroot_path = Path(temp_dir) / "docroot"
            docroot_path.mkdir()

            category_path = docroot_path / "review"
            category_path.mkdir()

            # Mock SessionManager to return our test docroot
            with patch("mcp_server_guide.tools.document_tools.SessionManager") as mock_session_class:
                mock_session = Mock()
                # Simplified mock
                mock_session.docroot = LazyPath(str(docroot_path))

                mock_session_class.return_value = mock_session

                # Create initial document
                await create_mcp_document(category_dir="review", name="test.md", content="# Original Content")

                # Update the document
                result = await update_mcp_document(category_dir="review", name="test.md", content="# Updated Content")

                # Should succeed
                assert result["success"] is True

                # Verify file was updated in docroot/review/__docs__/
                expected_path = docroot_path / "review" / DOCUMENT_SUBDIR / "test.md"
                assert expected_path.exists()
                assert expected_path.read_text() == "# Updated Content"

    @pytest.mark.asyncio
    async def test_delete_mcp_document_uses_docroot(self):
        """Test that delete_mcp_document uses docroot to resolve category paths."""
        from mcp_server_guide.tools.document_tools import create_mcp_document, delete_mcp_document
        from mcp_server_guide.path_resolver import LazyPath

        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up docroot and category structure
            docroot_path = Path(temp_dir) / "docroot"
            docroot_path.mkdir()

            category_path = docroot_path / "review"
            category_path.mkdir()

            # Mock SessionManager to return our test docroot
            with patch("mcp_server_guide.tools.document_tools.SessionManager") as mock_session_class:
                mock_session = Mock()
                # Simplified mock
                mock_session.docroot = LazyPath(str(docroot_path))

                mock_session_class.return_value = mock_session

                # Create document
                await create_mcp_document(category_dir="review", name="test.md", content="# Test Document")

                # Verify file exists
                expected_path = docroot_path / "review" / DOCUMENT_SUBDIR / "test.md"
                assert expected_path.exists()

                # Delete the document
                result = await delete_mcp_document(category_dir="review", name="test.md")

                # Should succeed
                assert result["success"] is True

                # Verify file was deleted from docroot/review/__docs__/
                assert not expected_path.exists()

    @pytest.mark.asyncio
    async def test_list_mcp_documents_uses_docroot(self):
        """Test that list_mcp_documents uses docroot to resolve category paths."""
        from mcp_server_guide.tools.document_tools import create_mcp_document, list_mcp_documents
        from mcp_server_guide.path_resolver import LazyPath

        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up docroot and category structure
            docroot_path = Path(temp_dir) / "docroot"
            docroot_path.mkdir()

            category_path = docroot_path / "review"
            category_path.mkdir()

            # Mock SessionManager to return our test docroot
            with patch("mcp_server_guide.tools.document_tools.SessionManager") as mock_session_class:
                mock_session = Mock()
                # Simplified mock
                mock_session.docroot = LazyPath(str(docroot_path))

                mock_session_class.return_value = mock_session

                # Create documents
                await create_mcp_document(category_dir="review", name="doc1.md", content="# Document 1")
                await create_mcp_document(category_dir="review", name="doc2.md", content="# Document 2")

                # List documents
                result = await list_mcp_documents(category_dir="review")

                # Should succeed and find both documents
                assert result["success"] is True
                assert len(result["documents"]) == 2

                doc_names = [doc["name"] for doc in result["documents"]]
                assert "doc1.md" in doc_names
                assert "doc2.md" in doc_names
