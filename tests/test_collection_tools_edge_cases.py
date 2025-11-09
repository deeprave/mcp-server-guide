"""Edge case tests for collection tools functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from mcp_server_guide.tools.collection_tools import (
    add_collection,
    update_collection,
    add_to_collection,
    remove_from_collection,
    list_collections,
    get_collection_content,
)
from mcp_server_guide.project_config import ProjectConfig
from mcp_server_guide.models.collection import Collection
from mcp_server_guide.models.category import Category


class TestCollectionToolsEdgeCases:
    """Tests for collection tools edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_add_collection_duplicate_name(self):
        """Test add_collection with duplicate collection name."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"existing": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await add_collection("existing", categories=["cat1"])
            assert not result["success"]
            assert "Collection 'existing' already exists" in result["error"]

    @pytest.mark.asyncio
    async def test_add_collection_nonexistent_category(self):
        """Test add_collection with non-existent category."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await add_collection("new", categories=["nonexistent"])
            assert not result["success"]
            assert "does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_add_collection_success_with_description(self):
        """Test add_collection success path with description."""
        config = ProjectConfig(categories={"cat1": Category(dir="/test", patterns=["*.py"])}, collections={})

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            async def mock_save():
                pass

            mock_session.safe_save_session = mock_save

            result = await add_collection("new", categories=["cat1"], description="Test collection")
            assert result["success"]
            assert "created successfully" in result["message"]
            assert "collection" in result

    @pytest.mark.asyncio
    async def test_add_collection_success_without_description(self):
        """Test add_collection success path without description."""
        config = ProjectConfig(categories={"cat1": Category(dir="/test", patterns=["*.py"])}, collections={})

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            async def mock_save():
                pass

            mock_session.safe_save_session = mock_save

            result = await add_collection("new", categories=["cat1"])
            assert result["success"]

    @pytest.mark.asyncio
    async def test_add_collection_pydantic_validation_error(self):
        """Test add_collection with Pydantic validation error."""
        config = ProjectConfig(categories={"cat1": Category(dir="/test", patterns=["*.py"])}, collections={})

        with (
            patch("mcp_server_guide.session_manager.SessionManager") as mock_sm,
            patch("mcp_server_guide.tools.collection_tools.Collection") as mock_collection,
        ):
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_collection.side_effect = ValueError("Invalid collection data")

            result = await add_collection("new", categories=["cat1"])
            assert not result["success"]
            assert "Invalid collection configuration" in result["error"]

    @pytest.mark.asyncio
    async def test_update_collection_no_description_provided(self):
        """Test update_collection when no description is provided."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            async def mock_save():
                pass

            mock_session.safe_save_session = mock_save

            result = await update_collection("test")  # No description provided
            assert result["success"]

    @pytest.mark.asyncio
    async def test_add_to_collection_duplicate_category(self):
        """Test add_to_collection with duplicate category (should be handled by Pydantic)."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            async def mock_save():
                pass

            mock_session.safe_save_session = mock_save

            result = await add_to_collection("test", categories=["cat1"])  # Already exists
            assert not result["success"]  # Should fail for duplicates
            assert "All categories already exist" in result["error"]

    @pytest.mark.asyncio
    async def test_remove_from_collection_multiple_categories(self):
        """Test remove_from_collection with multiple categories."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test1", patterns=["*.py"]),
                "cat2": Category(dir="/test2", patterns=["*.js"]),
                "cat3": Category(dir="/test3", patterns=["*.ts"]),
            },
            collections={"test": Collection(categories=["cat1", "cat2", "cat3"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            async def mock_save():
                pass

            mock_session.safe_save_session = mock_save

            result = await remove_from_collection("test", categories=["cat1", "cat2"])
            assert result["success"]

    @pytest.mark.asyncio
    async def test_remove_from_collection_category_not_in_collection(self):
        """Test remove_from_collection with category not in collection."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test1", patterns=["*.py"]),
                "cat2": Category(dir="/test2", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await remove_from_collection("test", categories=["cat2"])
            assert not result["success"]
            assert "None of the specified categories exist" in result["error"]

    @pytest.mark.asyncio
    async def test_remove_from_collection_ambiguous_case(self):
        """Test remove_from_collection with ambiguous case-only differences."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test1", patterns=["*.py"]),
                "Cat1": Category(dir="/test2", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["cat1", "Cat1"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await remove_from_collection("test", categories=["cat1"])
            assert not result["success"]
            assert "Ambiguous removal" in result["error"]
            assert "ambiguous" in result
            assert "cat1" in result["ambiguous"]
            assert result["ambiguous"]["cat1"] == ["cat1", "Cat1"]

    @pytest.mark.asyncio
    async def test_remove_from_collection_empty_categories(self):
        """Test remove_from_collection with empty categories list."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await remove_from_collection("test", categories=[])
            assert not result["success"]
            assert "categories" in result["error"] or "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_remove_from_collection_none_categories(self):
        """Test remove_from_collection with categories=None."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await remove_from_collection("test", categories=None)
            assert not result["success"]
            assert "categories" in result["error"] or "none" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_remove_from_collection_partial_category_not_found(self):
        """Test remove_from_collection when some categories don't exist in collection."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test1", patterns=["*.py"]),
                "cat2": Category(dir="/test2", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await remove_from_collection("test", categories=["cat1", "cat2"])  # cat2 not in collection
            assert not result["success"]
            assert "Cannot remove all categories" in result["error"]

    @pytest.mark.asyncio
    async def test_get_collection_content_with_successful_categories(self):
        """Test get_collection_content with successful category content retrieval."""
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
            mock_get_cat.return_value = {"success": True, "content": "# Test content"}

            result = await get_collection_content("test")
            assert result["success"]
            assert "Test content" in result["content"]

    @pytest.mark.asyncio
    async def test_get_collection_content_with_failed_categories(self):
        """Test get_collection_content with failed category content retrieval."""
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
            mock_get_cat.return_value = {"success": False}

            result = await get_collection_content("test")
            assert result["success"]
            assert "Error: Unknown error" in result["content"]  # Function adds error message

    @pytest.mark.asyncio
    async def test_get_collection_content_with_no_matched_files(self):
        """Test get_collection_content with no content."""
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
            mock_get_cat.return_value = {"success": True, "content": ""}

            result = await get_collection_content("test")
            assert result["success"]
            assert "=== Category: cat1 ===" in result["content"]

    @pytest.mark.asyncio
    async def test_get_collection_content_with_exception_logging(self):
        """Test get_collection_content with exception in category processing."""
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
            mock_get_cat.side_effect = Exception("Category processing error")

            result = await get_collection_content("test")
            assert result["success"]
            assert "Error:" in result["content"]

    @pytest.mark.asyncio
    async def test_list_collections_empty_collections(self):
        """Test list_collections with no collections."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await list_collections()
            assert result["success"]
            assert result["collections"] == {}  # Fix: returns dict, not list

    @pytest.mark.asyncio
    async def test_get_collection_listing_with_files(self):
        """Test get_collection_listing function (different from get_collection_content)."""
        from mcp_server_guide.tools.collection_tools import get_collection_listing

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
            mock_get_cat.return_value = {"success": True, "matched_files": ["file1.py", "file2.py"]}

            result = await get_collection_listing("test")
            assert result["success"]
            assert len(result["files_by_category"]) == 1
            assert result["files_by_category"][0]["category"] == "cat1"
            assert result["files_by_category"][0]["files"] == ["file1.py", "file2.py"]

    @pytest.mark.asyncio
    async def test_get_collection_listing_with_exception(self):
        """Test get_collection_listing with exception in category processing."""
        from mcp_server_guide.tools.collection_tools import get_collection_listing

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
            mock_get_cat.side_effect = Exception("Category processing error")

            result = await get_collection_listing("test")
            assert result["success"]
            assert result["files_by_category"] == []
            mock_logger.warning.assert_called_once()
