"""Tests for MCP resources functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.mcp_server_guide.server import list_resources, read_resource


class TestResourceHandlers:
    """Test MCP resource handlers."""

    @pytest.mark.asyncio
    async def test_list_resources_empty_when_no_categories(self):
        """Test that list_resources returns empty list when no categories exist."""
        # Mock SessionManager and its methods
        mock_session = Mock()
        mock_session.get_current_project_safe = AsyncMock(return_value="test-project")
        mock_session.session_state = Mock()
        mock_session.session_state.get_project_config = Mock(return_value={"categories": {}})
        mock_session.get_or_create_project_config = AsyncMock(return_value={"categories": {}})

        with patch("src.mcp_server_guide.server.SessionManager", return_value=mock_session):
            resources = await list_resources()
            assert resources == []

    @pytest.mark.asyncio
    async def test_list_resources_includes_aggregate_resource(self):
        """Test that list_resources includes aggregate resource when auto-load categories exist."""
        # Mock SessionManager with a category that has auto_load: true
        mock_session = Mock()
        mock_session.get_current_project_safe = AsyncMock(return_value="test-project")
        mock_session.session_state = Mock()
        config_data = {"categories": {"test-category": {"description": "Test category", "auto_load": True}}}
        mock_session.session_state.get_project_config = Mock(return_value=config_data)
        mock_session.get_or_create_project_config = AsyncMock(return_value=config_data)

        with patch("src.mcp_server_guide.server.SessionManager", return_value=mock_session):
            resources = await list_resources()

            assert len(resources) == 2  # aggregate + individual

            # Check aggregate resource
            aggregate_resource = next((r for r in resources if str(r.uri) == "guide://category/"), None)
            assert aggregate_resource is not None
            assert aggregate_resource.name == "all-guides"
            assert aggregate_resource.description == "All auto-load guide categories combined"
            assert aggregate_resource.mimeType == "text/markdown"

            # Check individual resource
            individual_resource = next((r for r in resources if str(r.uri) == "guide://category/test-category"), None)
            assert individual_resource is not None
            assert individual_resource.name == "test-category"
            assert individual_resource.description == "Test category"
            assert individual_resource.mimeType == "text/markdown"

    @pytest.mark.asyncio
    async def test_read_resource_invalid_uri_scheme(self):
        """Test that read_resource raises error for invalid URI scheme."""
        with pytest.raises(ValueError, match="Invalid URI scheme"):
            await read_resource("invalid://uri")

    @pytest.mark.asyncio
    async def test_read_resource_aggregate_uri(self):
        """Test that read_resource handles aggregate URI correctly."""
        expected_content = "# All Guides\n\nCombined content from all categories."

        with patch("src.mcp_server_guide.server.tools.get_all_guides") as mock_get_all:
            mock_get_all.return_value = {"success": True, "content": expected_content}

            result = await read_resource("guide://category/")
            assert result == expected_content
            mock_get_all.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_read_resource_nonexistent_category(self):
        """Test that read_resource raises error for non-existent category."""
        with patch("src.mcp_server_guide.server.tools.get_category_content") as mock_get_content:
            mock_get_content.return_value = {"success": False, "error": "Category not found"}

            with pytest.raises(Exception, match="Failed to load category 'nonexistent'"):
                await read_resource("guide://category/nonexistent")

    @pytest.mark.asyncio
    async def test_read_resource_successful_content_retrieval(self):
        """Test that read_resource returns content for valid category."""
        expected_content = "# Test Category\n\nThis is test content."

        with patch("src.mcp_server_guide.server.tools.get_category_content") as mock_get_content:
            mock_get_content.return_value = {"success": True, "content": expected_content}

            result = await read_resource("guide://category/test-category")
            assert result == expected_content
