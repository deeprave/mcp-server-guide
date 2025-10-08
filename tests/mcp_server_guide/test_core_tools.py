"""Tests for core P0 tools (Issue 005 Phase 2)."""

from unittest.mock import patch, Mock, AsyncMock
from mcp_server_guide.tools import get_current_project, get_guide, get_project_config, switch_project


async def test_get_current_project():
    """Test getting current project name."""
    result = await get_current_project()
    assert isinstance(result, str) or result is None  # Can be None if not set


async def test_get_current_project_none():
    """Test get_current_project returns None when no project is set."""
    with patch("mcp_server_guide.tools.project_tools.SessionManager") as mock_session_class:
        mock_session = Mock()
        mock_session.get_current_project = AsyncMock(return_value=None)
        mock_session_class.return_value = mock_session

        result = await get_current_project()
        assert result is None


async def test_get_guide_default_project():
    """Test getting guide for default project."""
    with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_category:
        mock_category.return_value = {"success": True, "content": "# Test Guide Content"}
        result = await get_guide()
        assert isinstance(result, str)
        assert len(result) > 0


async def test_get_guide_specific_project():
    """Test getting guide for specific project."""
    with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_category:
        mock_category.return_value = {"success": True, "content": "# Test Guide Content"}
        result = await get_guide("mcp_server_guide")
        assert isinstance(result, str)
        assert len(result) > 0


async def test_get_project_config_default():
    """Test getting project config for default project."""
    result = await get_project_config()
    assert isinstance(result, dict)
    assert "project" in result


async def test_get_project_config_specific():
    """Test getting project config for specific project."""
    result = await get_project_config("mcp_server_guide")
    assert isinstance(result, dict)
    assert "project" in result


async def test_switch_project():
    """Test switching to different project."""
    result = await switch_project("test-project")
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["project"] == "test-project"

    # Verify the switch worked
    current = await get_current_project()
    assert current == "test-project"
