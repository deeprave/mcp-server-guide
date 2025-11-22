"""Tests for core P0 tools (Issue 005 Phase 2)."""

from unittest.mock import patch, Mock, AsyncMock
from mcp_server_guide.tools import get_current_project, get_project_config, switch_project, get_guide


async def test_get_current_project():
    """Test getting current project name."""
    mock_ctx = Mock()
    mock_ctx.error = AsyncMock()
    result = await get_current_project(mock_ctx)
    assert isinstance(result, str)  # Always returns string (empty if not set)


async def test_get_current_project_none():
    """Test get_current_project returns empty string when no project is set."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
        mock_session = Mock()
        mock_session.get_project_name = Mock(side_effect=ValueError("No project"))
        mock_session_class.return_value = mock_session

        mock_ctx = Mock()
        mock_ctx.error = AsyncMock()
        result = await get_current_project(mock_ctx)
        assert result == ""
        mock_ctx.error.assert_called_once()


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


async def test_switch_project(isolated_config_file):
    """Test switching to different project."""
    from mcp_server_guide.session_manager import SessionManager

    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    result = await switch_project("test-project")
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["project"] == "test-project"

    # Verify the switch worked
    mock_ctx = Mock()
    mock_ctx.error = AsyncMock()
    current = await get_current_project(mock_ctx)
    assert current == "test-project"


@patch("mcp_server_guide.tools.content_tools.get_category_content")
async def test_get_guide_success(mock_get_category):
    """Test get_guide with successful document retrieval."""
    mock_get_category.return_value = {
        "success": True,
        "content": "# doc1\nSome content\n# doc2\nOther content",
        "matched_files": ["doc1.md"],
    }

    result = await get_guide("category1", "doc1")
    assert result == "Some content"
    mock_get_category.assert_called_once_with("category1")


@patch("mcp_server_guide.tools.content_tools.get_category_content")
async def test_get_guide_missing_document(mock_get_category):
    """Test get_guide with missing document."""
    mock_get_category.return_value = {
        "success": True,
        "content": "# other_doc\nSome content",
        "matched_files": ["other_doc.md"],
    }

    result = await get_guide("category1", "missing_doc")
    assert result is None
    mock_get_category.assert_called_once_with("category1")


@patch("mcp_server_guide.tools.content_tools.get_category_content")
async def test_get_guide_invalid_category(mock_get_category):
    """Test get_guide with invalid category."""
    mock_get_category.side_effect = Exception("Invalid category")

    result = await get_guide("invalid_category", "doc1")
    assert result is None
    mock_get_category.assert_called_once_with("invalid_category")
