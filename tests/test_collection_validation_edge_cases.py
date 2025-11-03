"""Tests for collection validation edge cases."""

import pytest
from unittest.mock import Mock, patch
from mcp_server_guide.tools.collection_tools import add_collection, remove_collection
from mcp_server_guide.project_config import ProjectConfig
from mcp_server_guide.models.collection import Collection
from mcp_server_guide.models.category import Category


class TestCollectionValidationEdgeCases:
    """Tests for collection validation edge cases."""

    @pytest.mark.asyncio
    async def test_add_collection_empty_name(self):
        """Test add_collection with empty name."""
        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session

            result = await add_collection("", categories=["cat1"])
            assert not result["success"]
            assert "Collection name cannot be empty" in result["error"]

    @pytest.mark.asyncio
    async def test_add_collection_whitespace_name(self):
        """Test add_collection with whitespace-only name."""
        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session

            result = await add_collection("   ", categories=["cat1"])
            assert not result["success"]
            assert "Collection name cannot be empty" in result["error"]

    @pytest.mark.asyncio
    async def test_add_collection_invalid_name_length(self):
        """Test add_collection with name too long."""
        long_name = "a" * 31  # Over 30 character limit

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session

            result = await add_collection(long_name, categories=["cat1"])
            assert not result["success"]
            assert "Invalid collection name" in result["error"]

    @pytest.mark.asyncio
    async def test_add_collection_no_categories(self):
        """Test add_collection with no categories."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"

            async def mock_get_config(project=None):
                return config

            mock_session.get_or_create_project_config = mock_get_config

            result = await add_collection("test", categories=[])
            assert not result["success"]
            assert "Collection must have at least one category" in result["error"]

    @pytest.mark.asyncio
    async def test_add_collection_empty_category_values(self):
        """Test add_collection with empty/None category values."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"

            async def mock_get_config(project=None):
                return config

            mock_session.get_or_create_project_config = mock_get_config

            result = await add_collection("test", categories=["cat1", None, "", "  "])
            assert not result["success"]
            assert "empty or whitespace-only values" in result["error"]

    @pytest.mark.asyncio
    async def test_add_collection_duplicate_categories_case_insensitive(self):
        """Test add_collection with duplicate categories (case-insensitive)."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"

            async def mock_get_config(project=None):
                return config

            mock_session.get_or_create_project_config = mock_get_config

            result = await add_collection("test", categories=["Cat1", "cat1"])
            assert not result["success"]
            assert "Duplicate category names (case-insensitive)" in result["error"]

    @pytest.mark.asyncio
    async def test_remove_collection_nonexistent(self):
        """Test remove_collection with nonexistent collection."""
        config = ProjectConfig(categories={}, collections={})

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"

            async def mock_get_config(project=None):
                return config

            mock_session.get_or_create_project_config = mock_get_config

            result = await remove_collection("nonexistent")
            assert not result["success"]
            assert "Collection 'nonexistent' does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_remove_collection_success(self):
        """Test remove_collection success case."""
        config = ProjectConfig(
            categories={"cat1": Category(dir="/test", patterns=["*.py"])},
            collections={"test": Collection(categories=["cat1"])},
        )

        with patch("mcp_server_guide.tools.collection_tools.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.get_project_name.return_value = "test"

            async def mock_get_config(project=None):
                return config

            mock_session.get_or_create_project_config = mock_get_config

            async def mock_save():
                pass

            mock_session.save_session = mock_save

            result = await remove_collection("test")
            assert result["success"]
            assert "removed successfully" in result["message"]
