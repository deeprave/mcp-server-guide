"""Test MCP resource functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from mcp_server_guide.server import list_resources, read_resource


@pytest.mark.asyncio
async def test_list_resources_returns_resources_for_auto_load_true_categories():
    """Test that list_resources returns resources for auto_load: true categories."""
    with patch("mcp_server_guide.server.SessionManager") as mock_session_class:
        # Set up mock session with auto_load categories
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project_safe = AsyncMock(return_value="test-project")
        mock_session.session_state.get_project_config.return_value = {
            "categories": {
                "guide": {
                    "dir": "guide/",
                    "patterns": ["*.md"],
                    "description": "Development guidelines",
                    "auto_load": True,
                },
                "lang": {
                    "dir": "lang/",
                    "patterns": ["*.md"],
                    "description": "Language guidelines",
                },  # No auto_load = False
                "context": {
                    "dir": "context/",
                    "patterns": ["*.md"],
                    "description": "Project context",
                    "auto_load": True,
                },
                "custom": {"dir": "custom/", "patterns": ["*.md"], "description": "Custom docs", "auto_load": False},
            }
        }

        resources = await list_resources()

        # Should return resources for auto_load categories only (aggregate + 2 individual)
        assert len(resources) == 3

        # Check aggregate resource
        aggregate_resource = next((r for r in resources if str(r.uri) == "guide://category/"), None)
        assert aggregate_resource is not None
        assert aggregate_resource.name == "all-guides"
        assert aggregate_resource.description == "All auto-load guide categories combined"
        assert aggregate_resource.mimeType == "text/markdown"

        # Check guide resource
        guide_resource = next((r for r in resources if str(r.uri) == "guide://category/guide"), None)
        assert guide_resource is not None
        assert guide_resource.name == "guide"
        assert guide_resource.description == "Development guidelines"
        assert guide_resource.mimeType == "text/markdown"

        # Check context resource
        context_resource = next((r for r in resources if str(r.uri) == "guide://category/context"), None)
        assert context_resource is not None
        assert context_resource.name == "context"
        assert context_resource.description == "Project context"
        assert context_resource.mimeType == "text/markdown"


@pytest.mark.asyncio
async def test_list_resources_returns_empty_list_when_no_auto_load_categories():
    """Test that list_resources returns empty list when no auto_load categories exist."""
    with patch("mcp_server_guide.server.SessionManager") as mock_session_class:
        # Set up mock session with no auto_load categories
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project_safe = AsyncMock(return_value="test-project")
        mock_session.session_state.get_project_config.return_value = {
            "categories": {
                "guide": {
                    "dir": "guide/",
                    "patterns": ["*.md"],
                    "description": "Development guidelines",
                    "auto_load": False,
                },
                "lang": {
                    "dir": "lang/",
                    "patterns": ["*.md"],
                    "description": "Language guidelines",
                },  # No auto_load = False
            }
        }

        resources = await list_resources()

        # Should return empty list
        assert len(resources) == 0


@pytest.mark.asyncio
async def test_read_resource_serves_correct_content_for_valid_uris():
    """Test that read_resource serves correct content for valid URIs."""
    with patch("mcp_server_guide.server.tools.get_category_content") as mock_get_content:

        async def mock_return(*args, **kwargs):
            return {"success": True, "content": "# Test Content\n\nThis is test content."}

        mock_get_content.side_effect = mock_return

        content = await read_resource("guide://category/test_category")

        assert content == "# Test Content\n\nThis is test content."
        mock_get_content.assert_called_once_with("test_category", None)


@pytest.mark.asyncio
async def test_read_resource_handles_missing_categories_gracefully():
    """Test that read_resource handles missing categories gracefully."""
    with patch("mcp_server_guide.server.tools.get_category_content") as mock_get_content:

        async def mock_return(*args, **kwargs):
            return {"success": False, "error": "Category not found"}

        mock_get_content.side_effect = mock_return

        try:
            await read_resource("guide://category/nonexistent")
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Failed to load category 'nonexistent'" in str(e)
