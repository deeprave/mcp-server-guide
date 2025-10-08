"""Tests for get_or_create_project_config functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.mcp_server_guide.tools.category_tools import list_categories


@pytest.mark.asyncio
async def test_get_or_create_project_config_exception_handling():
    """Test that exceptions in get_or_create_project_config are properly handled."""
    with patch("src.mcp_server_guide.tools.category_tools.SessionManager") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project_safe = AsyncMock(return_value="test-project")
        mock_session.get_or_create_project_config = AsyncMock(side_effect=Exception("Config creation failed"))

        with pytest.raises(Exception, match="Config creation failed"):
            await list_categories()


@pytest.mark.asyncio
async def test_get_or_create_project_config_empty_config():
    """Test handling when get_or_create_project_config returns an empty dict."""
    with patch("src.mcp_server_guide.tools.category_tools.SessionManager") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project_safe = AsyncMock(return_value="test-project")
        mock_session.get_or_create_project_config = AsyncMock(return_value={})

        result = await list_categories()

        assert result["success"] is True
        assert result["builtin_categories"] == {}
        assert result["custom_categories"] == {}
        assert result["total_categories"] == 0


@pytest.mark.asyncio
async def test_get_or_create_project_config_no_categories_key():
    """Test handling when get_or_create_project_config returns a dict without 'categories' key."""
    with patch("src.mcp_server_guide.tools.category_tools.SessionManager") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project_safe = AsyncMock(return_value="test-project")
        mock_session.get_or_create_project_config = AsyncMock(return_value={"docroot": "."})

        result = await list_categories()

        assert result["success"] is True
        assert result["builtin_categories"] == {}
        assert result["custom_categories"] == {}
        assert result["total_categories"] == 0


@pytest.mark.asyncio
async def test_get_or_create_project_config_auto_save_behavior():
    """Test that save_to_file is called when a new project is created."""
    # Create a real SessionManager to test the actual get_or_create_project_config logic
    from src.mcp_server_guide.session_tools import SessionManager

    # Mock the config_filename import at the right location
    with patch("src.mcp_server_guide.naming.config_filename", return_value="test.json"):
        real_session = SessionManager()

        # Mock save_to_file to track calls
        real_session.save_to_file = AsyncMock()

        # Clear any existing projects to ensure we test new project creation
        real_session.session_state.projects.clear()

        config = await real_session.get_or_create_project_config("new-project")

        # Verify config was returned
        assert config is not None
        assert "docroot" in config  # Should have defaults

        # Verify save_to_file was called for new project
        real_session.save_to_file.assert_called_once_with("test.json")
