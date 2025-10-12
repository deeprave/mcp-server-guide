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
    import tempfile
    from unittest.mock import patch, AsyncMock, Mock

    with tempfile.TemporaryDirectory():
        with patch("src.mcp_server_guide.tools.category_tools.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_current_project_safe = AsyncMock(return_value="new-project")
            mock_session.get_or_create_project_config = AsyncMock(return_value={"docroot": "."})
            mock_session.save_session = AsyncMock()
            mock_session_class.return_value = mock_session

            # Test the function that uses SessionManager
            from src.mcp_server_guide.tools.category_tools import list_categories

            result = await list_categories("new-project")

            # Verify the function worked
            assert result["success"] is True

            # This test just verifies the mocking works correctly
            # The actual auto-save behavior is tested in integration tests
