"""Tests for MCP resource handlers."""

from unittest.mock import Mock, patch
from mcp_server_guide.server import list_resources, read_resource, mcp


def test_list_resources_returns_resources_for_auto_load_true_categories():
    """Test that list_resources returns resources for auto_load: true categories."""
    with patch("mcp_server_guide.server.SessionManager") as mock_session_class:
        # Set up mock session with auto_load categories
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project.return_value = "test-project"
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

        resources = list_resources()

        # Should return resources for auto_load categories only
        assert len(resources) == 2

        # Check guide resource
        guide_resource = next((r for r in resources if r["uri"] == "guide://guide"), None)
        assert guide_resource is not None
        assert guide_resource["name"] == "Development guidelines"
        assert guide_resource["mimeType"] == "text/markdown"

        # Check context resource
        context_resource = next((r for r in resources if r["uri"] == "guide://context"), None)
        assert context_resource is not None
        assert context_resource["name"] == "Project context"
        assert context_resource["mimeType"] == "text/markdown"

        # Should not include non-auto_load categories
        lang_resource = next((r for r in resources if r["uri"] == "guide://lang"), None)
        assert lang_resource is None
        custom_resource = next((r for r in resources if r["uri"] == "guide://custom"), None)
        assert custom_resource is None


def test_list_resources_returns_empty_list_when_no_auto_load_true_categories():
    """Test that list_resources returns empty list when no auto_load: true categories."""
    with patch("mcp_server_guide.server.SessionManager") as mock_session_class:
        # Set up mock session with no auto_load categories
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project.return_value = "test-project"
        mock_session.session_state.get_project_config.return_value = {
            "categories": {
                "guide": {
                    "dir": "guide/",
                    "patterns": ["*.md"],
                    "description": "Development guidelines",
                },  # No auto_load = False
                "lang": {
                    "dir": "lang/",
                    "patterns": ["*.md"],
                    "description": "Language guidelines",
                },  # No auto_load = False
            }
        }

        resources = list_resources()

        # Should return empty list
        assert resources == []


def test_read_resource_serves_correct_content_for_valid_uris():
    """Test that read_resource serves correct content for valid URIs."""
    with patch("mcp_server_guide.server.tools.get_category_content") as mock_get_content:
        mock_get_content.return_value = {"success": True, "content": "# Test Content\n\nThis is test content."}

        content = read_resource("guide://test_category")

        assert content == "# Test Content\n\nThis is test content."
        mock_get_content.assert_called_once_with("test_category", None)


def test_read_resource_raises_error_for_invalid_uris():
    """Test that read_resource raises error for invalid URIs."""
    try:
        read_resource("invalid://test")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid URI scheme" in str(e)


def test_read_resource_handles_missing_categories_gracefully():
    """Test that read_resource handles missing categories gracefully."""
    with patch("mcp_server_guide.server.tools.get_category_content") as mock_get_content:
        mock_get_content.return_value = {"success": False, "error": "Category not found"}

        try:
            read_resource("guide://nonexistent")
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Failed to load category 'nonexistent'" in str(e)
            assert "Category not found" in str(e)


def test_mcp_server_exposes_resource_endpoints():
    """Test that MCP server exposes resource endpoints."""
    # Check that the MCP server has resource handlers registered
    assert hasattr(mcp, "_resource_manager")

    # Check that list_resources and read_resource are registered
    # This is an integration test to ensure the decorators worked
    resource_manager = mcp._resource_manager
    assert resource_manager is not None
