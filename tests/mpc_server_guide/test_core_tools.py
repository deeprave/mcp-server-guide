"""Tests for core P0 tools (Issue 005 Phase 2)."""

from unittest.mock import patch
from mcp_server_guide.tools import get_current_project, get_guide, get_project_config, switch_project


def test_get_current_project():
    """Test getting current project name."""
    result = get_current_project()
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_guide_default_project():
    """Test getting guide for default project."""
    with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_category:
        mock_category.return_value = {"success": True, "content": "# Test Guide Content"}
        result = get_guide()
        assert isinstance(result, str)
        assert len(result) > 0


def test_get_guide_specific_project():
    """Test getting guide for specific project."""
    with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_category:
        mock_category.return_value = {"success": True, "content": "# Test Guide Content"}
        result = get_guide("mcp_server_guide")
        assert isinstance(result, str)
        assert len(result) > 0


def test_get_project_config_default():
    """Test getting project config for default project."""
    result = get_project_config()
    assert isinstance(result, dict)
    assert "project" in result


def test_get_project_config_specific():
    """Test getting project config for specific project."""
    result = get_project_config("mcp_server_guide")
    assert isinstance(result, dict)
    assert "project" in result


def test_switch_project():
    """Test switching to different project."""
    result = switch_project("test-project")
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["project"] == "test-project"

    # Verify the switch worked
    current = get_current_project()
    assert current == "test-project"
