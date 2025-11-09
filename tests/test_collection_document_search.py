"""Tests for collection document search functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from mcp_server_guide.tools.collection_tools import (
    update_collection,
    add_to_collection,
    remove_from_collection,
    get_collection_document,
)
from mcp_server_guide.models.project_config import ProjectConfig
from mcp_server_guide.models.collection import Collection
from mcp_server_guide.models.category import Category


class TestCollectionDocumentSearch:
    """Tests for collection document search and retrieval."""

    @pytest.mark.asyncio
    async def test_update_collection_value_error(self) -> None:
        """Test update_collection ValueError catch block."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_session.safe_save_session = AsyncMock(side_effect=ValueError("Save error"))

            result = await update_collection("test", description="new desc")
            assert not result["success"]
            assert "Invalid collection configuration" in result["error"]

    @pytest.mark.asyncio
    async def test_add_to_collection_value_error(self) -> None:
        """Test add_to_collection ValueError catch block."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test", patterns=["*.py"]),
                "cat2": Category(dir="/test2", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_session.safe_save_session = AsyncMock(side_effect=ValueError("Save error"))

            result = await add_to_collection("test", categories=["cat2"])  # Use different category
            assert not result["success"]
            assert "Invalid collection configuration" in result["error"]

    @pytest.mark.asyncio
    async def test_remove_from_collection_value_error(self) -> None:
        """Test remove_from_collection ValueError catch block."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test1", patterns=["*.py"]),
                "cat2": Category(dir="/test2", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["cat1", "cat2"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_session.safe_save_session = AsyncMock(side_effect=ValueError("Save error"))

            result = await remove_from_collection("test", categories=["cat1"])
            assert not result["success"]
            assert "Invalid collection configuration" in result["error"]

    @pytest.mark.asyncio
    async def test_get_collection_document_success(self) -> None:
        """Test get_collection_document success path."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with (
            patch("mcp_server_guide.session_manager.SessionManager") as mock_sm,
            patch("mcp_server_guide.tools.collection_tools.get_category_content") as mock_get_cat,
            patch("mcp_server_guide.tools.content_tools._extract_document_from_content") as mock_extract,
        ):
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_get_cat.return_value = {
                "success": True,
                "matched_files": ["/path/to/document.md"],
                "content": "# Document content",
            }
            mock_extract.return_value = "# Document content"  # Mock successful extraction

            result = await get_collection_document("test", "document.md")
            assert result["success"]
            assert result["content"] == "# Document content"
            assert result["found_in_category"] == "cat1"
            assert result["document"] == "document.md"

    @pytest.mark.asyncio
    async def test_get_collection_document_not_found(self) -> None:
        """Test get_collection_document when document not found."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with (
            patch("mcp_server_guide.session_manager.SessionManager") as mock_sm,
            patch("mcp_server_guide.tools.collection_tools.get_category_content") as mock_get_cat,
        ):
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_get_cat.return_value = {
                "success": True,
                "matched_files": ["/path/to/other.md"],
                "content": "# Other content",
            }

            result = await get_collection_document("test", "missing.md")
            assert not result["success"]
            assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_get_collection_document_collection_not_found(self) -> None:
        """Test get_collection_document with non-existent collection."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await get_collection_document("missing", "doc.md")
            assert not result["success"]
            assert "does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_get_collection_document_with_exception(self) -> None:
        """Test get_collection_document with exception in category processing."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with (
            patch("mcp_server_guide.session_manager.SessionManager") as mock_sm,
            patch("mcp_server_guide.tools.collection_tools.get_category_content") as mock_get_cat,
            patch("mcp_server_guide.tools.collection_tools.logger") as mock_logger,
        ):
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_get_cat.side_effect = Exception("Category error")

            result = await get_collection_document("test", "doc.md")
            assert not result["success"]
            assert "error" in result
            assert "not found" in result["error"]
            mock_logger.warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_collection_document_multiple_match_patterns(self) -> None:
        """Test get_collection_document with different file path matching patterns."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with (
            patch("mcp_server_guide.session_manager.SessionManager") as mock_sm,
            patch("mcp_server_guide.tools.collection_tools.get_category_content") as mock_get_cat,
            patch("mcp_server_guide.tools.content_tools._extract_document_from_content") as mock_extract,
        ):
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_extract.return_value = "# Content"  # Mock successful extraction

            # Test exact match in filename
            mock_get_cat.return_value = {
                "success": True,
                "matched_files": ["/path/to/mydocument.md"],
                "content": "# Content",
            }

            result = await get_collection_document("test", "document", partial_match=True)
            assert result["success"]
            # Assert that the matched file is the expected one
            assert result.get("file_path") == "/path/to/mydocument.md"

            # Test path ending match
            mock_get_cat.return_value = {
                "success": True,
                "matched_files": ["/path/to/document"],
                "content": "# Content",
            }

            result = await get_collection_document("test", "document")
            assert result["success"]
            # Assert that the matched file is the expected one
            assert result.get("file_path") == "/path/to/document"

            # Test .md extension match
            mock_get_cat.return_value = {
                "success": True,
                "matched_files": ["/path/to/document.md"],
                "content": "# Content",
            }

            result = await get_collection_document("test", "document")
            assert result["success"]
            # Assert that the matched file is the expected one
            assert result.get("file_path") == "/path/to/document.md"
            assert result["success"]
