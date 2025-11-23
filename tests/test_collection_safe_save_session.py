"""Test that collection modifying functions call safe_save_session."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_server_guide.models.category import Category
from mcp_server_guide.models.collection import Collection
from mcp_server_guide.models.project_config import ProjectConfig
from mcp_server_guide.tools.collection_tools import (
    add_collection,
    add_to_collection,
    create_spec_kit_collection,
    remove_collection,
    remove_from_collection,
    update_collection,
)


class TestCollectionSafeSaveSession:
    """Test that collection functions call safe_save_session."""

    @pytest.fixture
    def mock_session_with_config(self):
        """Create a mock session with basic config."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            # Mock config with categories
            config = ProjectConfig(
                categories={
                    "cat1": Category(dir="cat1/", patterns=["*.md"], description="Category 1"),
                    "cat2": Category(dir="cat2/", patterns=["*.md"], description="Category 2"),
                    "cat3": Category(dir="cat3/", patterns=["*.md"], description="Category 3"),
                },
                collections={
                    "existing": Collection(
                        categories=["cat1", "cat2"], description="Existing collection", source_type="user"
                    )
                },
            )

            mock_session.get_project_name.return_value = "test"
            mock_session.get_or_create_project_config = AsyncMock(return_value=config)
            mock_session.safe_save_session = AsyncMock()

            yield mock_session

    @pytest.mark.asyncio
    async def test_create_spec_kit_collection_calls_safe_save_session(self, mock_session_with_config):
        """Test create_spec_kit_collection calls safe_save_session."""
        result = await create_spec_kit_collection("new_collection", ["cat1"], "Test collection")

        assert result["success"] is True
        mock_session_with_config.safe_save_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_collection_calls_safe_save_session(self, mock_session_with_config):
        """Test add_collection calls safe_save_session."""
        result = await add_collection("new_collection", ["cat1"], "Test collection")

        assert result["success"] is True
        mock_session_with_config.safe_save_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_collection_calls_safe_save_session(self, mock_session_with_config):
        """Test update_collection calls safe_save_session."""
        result = await update_collection("existing", description="Updated description")

        assert result["success"] is True
        mock_session_with_config.safe_save_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_to_collection_calls_safe_save_session(self, mock_session_with_config):
        """Test add_to_collection calls safe_save_session."""
        result = await add_to_collection("existing", ["cat3"])

        assert result["success"] is True
        mock_session_with_config.safe_save_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_from_collection_calls_safe_save_session(self, mock_session_with_config):
        """Test remove_from_collection calls safe_save_session."""
        result = await remove_from_collection("existing", ["cat1"])

        assert result["success"] is True
        mock_session_with_config.safe_save_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_collection_calls_safe_save_session(self, mock_session_with_config):
        """Test remove_collection calls safe_save_session."""
        result = await remove_collection("existing")

        assert result["success"] is True
        mock_session_with_config.safe_save_session.assert_called_once()
