"""Comprehensive tests for collection tools functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from mcp_server_guide.tools.collection_tools import (
    add_collection,
    update_collection,
    add_to_collection,
    remove_from_collection,
    remove_collection,
    list_collections,
    get_collection_content,
)
from mcp_server_guide.project_config import ProjectConfig, Collection, Category


class TestCollectionToolsComprehensive:
    """Comprehensive tests for collection tools operations."""

    @pytest.mark.asyncio
    async def test_add_collection_value_error(self):
        """Test that add_collection handles invalid input gracefully."""
        result = await add_collection("test", None, "Test collection")
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_update_collection_success(self):
        """Test update_collection success path."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_session.save_session = AsyncMock()  # Fix: make this AsyncMock

            result = await update_collection("test", description="new desc")
            assert result["success"]
            # Assert that the collection's description is updated in the config
            assert config.collections["test"].description == "new desc"

    @pytest.mark.asyncio
    async def test_update_collection_description_only(self):
        """Test that update_collection currently only supports description updates.

        Note: This test documents the current limitation that update_collection
        does not support updating categories or other fields. This could be
        enhanced in the future to support more comprehensive updates.
        """
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test1", patterns=["*.py"]),
                "cat2": Category(dir="/test2", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_session.save_session = AsyncMock()

            # Currently only description updates are supported
            result = await update_collection("test", description="updated description")
            assert result["success"]
            assert config.collections["test"].description == "updated description"

            # Categories remain unchanged (limitation of current implementation)
            assert config.collections["test"].categories == ["cat1"]

    @pytest.mark.asyncio
    async def test_update_collection_not_found(self):
        """Test update_collection with non-existent collection."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await update_collection("missing", description="desc")
            assert not result["success"]
            assert "does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_add_to_collection_duplicate_category(self):
        """Test add_to_collection with duplicate category."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test", patterns=["*.py"]),
                "existing": Category(dir="/existing", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["existing"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_session.save_session = AsyncMock()

            result = await add_to_collection("test", ["existing"])
            assert not result["success"]
            assert "All categories already exist" in result["error"]

    @pytest.mark.asyncio
    async def test_add_to_collection_success(self):
        """Test add_to_collection success path."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test", patterns=["*.py"]),
                "existing": Category(dir="/existing", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["existing"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_session.save_session = AsyncMock()  # Fix: make this AsyncMock

            result = await add_to_collection("test", categories=["cat1"])
            assert result["success"]
            # Assert that the new category appears in the collection's categories list
            assert "cat1" in config.collections["test"].categories

    @pytest.mark.asyncio
    async def test_add_to_collection_not_found(self):
        """Test add_to_collection with non-existent collection."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await add_to_collection("missing", categories=["cat1"])
            assert not result["success"]

    @pytest.mark.asyncio
    async def test_add_to_collection_invalid_category(self):
        """Test add_to_collection with invalid category."""
        config = ProjectConfig(
            categories={"existing": Category(dir="/existing", patterns=["*.js"])},
            collections={"test": Collection(categories=["existing"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await add_to_collection("test", categories=["invalid"])
            assert not result["success"]
            assert "does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_add_to_collection_mixed_valid_invalid_categories(self):
        """Test add_to_collection with both valid and invalid categories."""
        config = ProjectConfig(
            categories={"existing": Category(dir="/existing", patterns=["*.js"])},
            collections={"test": Collection(categories=["existing"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            # Mix of valid and invalid categories
            result = await add_to_collection("test", categories=["existing", "invalid"])
            assert not result["success"]
            assert "does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_add_to_collection_empty_categories(self):
        """Test add_to_collection with empty categories list."""
        config = ProjectConfig(
            categories={"existing": Category(dir="/existing", patterns=["*.js"])},
            collections={"test": Collection(categories=["existing"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await add_to_collection("test", categories=[])
            assert not result["success"]
            assert "categories" in result["error"] or "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_remove_from_collection_success(self):
        """Test remove_from_collection success path."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test1", patterns=["*.py"]),
                "cat2": Category(dir="/test2", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["cat1", "cat2"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_session.save_session = AsyncMock()  # Fix: make this AsyncMock

            result = await remove_from_collection("test", categories=["cat1"])
            assert result["success"]
            # Assert that the category was actually removed from the collection
            assert "cat1" not in config.collections["test"].categories
            assert "cat2" in config.collections["test"].categories

    @pytest.mark.asyncio
    async def test_remove_from_collection_nonexistent_category(self):
        """Test remove_from_collection with category not in collection."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test1", patterns=["*.py"]),
                "cat2": Category(dir="/test2", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await remove_from_collection("test", categories=["cat2"])
            assert not result["success"]

    @pytest.mark.asyncio
    async def test_remove_from_collection_mixed_present_absent_categories(self):
        """Test remove_from_collection with both existing and non-existing categories."""
        config = ProjectConfig(
            categories={
                "cat1": Category(dir="/test1", patterns=["*.py"]),
                "cat2": Category(dir="/test2", patterns=["*.js"]),
            },
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            # Mix of present and absent categories - would remove all, so should fail
            result = await remove_from_collection("test", categories=["cat1", "cat2"])
            assert not result["success"]
            assert "Cannot remove all categories" in result["error"]

    @pytest.mark.asyncio
    async def test_remove_from_collection_empty_error(self):
        """Test remove_from_collection when would leave empty collection."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await remove_from_collection("test", categories=["cat1"])
            assert not result["success"]
            assert "Cannot remove all categories" in result["error"]  # Fix: use actual error message

    @pytest.mark.asyncio
    async def test_remove_from_collection_not_found(self):
        """Test remove_from_collection with non-existent collection."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await remove_from_collection("missing", categories=["cat1"])
            assert not result["success"]

    @pytest.mark.asyncio
    async def test_remove_collection_success(self):
        """Test remove_collection success path."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_session.save_session = AsyncMock()  # Fix: make this AsyncMock

            result = await remove_collection("test")
            assert result["success"]

    @pytest.mark.asyncio
    async def test_remove_collection_not_found(self):
        """Test remove_collection with non-existent collection."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await remove_collection("missing")
            assert not result["success"]

    @pytest.mark.asyncio
    async def test_list_collections_verbose_true(self):
        """Test list_collections with verbose=True."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"], description="desc")},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await list_collections(verbose=True)
            assert result["success"]

    @pytest.mark.asyncio
    async def test_list_collections_empty(self):
        """Test list_collections with no collections present."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await list_collections()
            assert result["success"]
            assert result["collections"] == {}
            assert "message" in result
            assert "No collections found" in result["message"]

    @pytest.mark.asyncio
    async def test_list_collections_verbose_false(self):
        """Test list_collections with verbose=False."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await list_collections(verbose=False)
            assert result["success"]
            # Assert structure and contents of the returned collections
            collections = result["collections"]
            assert isinstance(collections, dict)
            assert "test" in collections
            test_collection = collections["test"]
            # In non-verbose mode, typically only category names and description are present
            assert isinstance(test_collection, dict)
            assert "categories" in test_collection
            assert isinstance(test_collection["categories"], list)
            assert test_collection["categories"] == ["cat1"]

    @pytest.mark.asyncio
    async def test_get_collection_content_success(self):
        """Test get_collection_content success path."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with (
            patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm,
            patch("mcp_server_guide.tools.collection_tools.get_category_content") as mock_get_cat,
        ):
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_get_cat.return_value = {"success": True, "matched_files": ["file1.py"]}

            result = await get_collection_content("test")
            assert result["success"]

    @pytest.mark.asyncio
    async def test_get_collection_content_category_error(self):
        """Test get_collection_content when category access fails."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with (
            patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm,
            patch("mcp_server_guide.tools.collection_tools.get_category_content") as mock_get_cat,
        ):
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_get_cat.side_effect = Exception("Category error")

            result = await get_collection_content("test")
            assert result["success"]  # Should still succeed with empty files

    @pytest.mark.asyncio
    async def test_get_collection_content_not_found(self):
        """Test get_collection_content with non-existent collection."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)

            result = await get_collection_content("missing")
            assert not result["success"]
