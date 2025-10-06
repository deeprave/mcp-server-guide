"""Tests for session management tools."""

from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
from mcp_server_guide.tools.session_management import save_session, load_session, reset_session


async def test_save_session_error_handling():
    """Test save_session with error conditions."""
    # Test save_session with exception
    with patch("mcp_server_guide.tools.session_management.SessionManager", side_effect=Exception("Session error")):
        result = await save_session()
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "Failed to save session" in result["message"]


async def test_load_session_error_handling():
    """Test load_session with error conditions."""
    # Test load_session with exception
    with patch("mcp_server_guide.tools.session_management.SessionManager", side_effect=Exception("Load error")):
        result = await load_session()
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "Failed to load session" in result["message"]

    # Test load_session with path
    test_path = Path("/test/path")
    with patch("mcp_server_guide.tools.session_management.SessionManager", side_effect=Exception("Load error")):
        result = await load_session(test_path)
        assert isinstance(result, dict)
        assert result["success"] is False


async def test_reset_session_error_handling():
    """Test reset_session with error conditions."""
    # Test reset_session with exception
    with patch("mcp_server_guide.tools.session_management.SessionManager", side_effect=Exception("Reset error")):
        result = await reset_session()
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "Failed to reset session" in result["message"]


async def test_session_management_success_paths():
    """Test session management success paths."""
    # Mock successful SessionManager
    mock_session = Mock()
    mock_session.get_current_project = AsyncMock(return_value="test_project")
    mock_session.save_to_file = AsyncMock()

    # Mock successful ProjectConfigManager
    mock_manager = Mock()

    # Test successful save_session
    with patch("mcp_server_guide.tools.session_management.SessionManager", return_value=mock_session):
        with patch("mcp_server_guide.tools.session_management.ProjectConfigManager", return_value=mock_manager):
            result = await save_session()
            print(f"DEBUG: save_session result = {result}")
            assert isinstance(result, dict)
            assert result["success"] is True
            assert result["project"] == "test_project"

    # Test successful load_session
    mock_manager.load_full_session_state = AsyncMock(return_value=True)
    with patch("mcp_server_guide.tools.session_management.SessionManager", return_value=mock_session):
        with patch("mcp_server_guide.tools.session_management.ProjectConfigManager", return_value=mock_manager):
            result = await load_session()
            assert isinstance(result, dict)
            assert result["success"] is True

    # Test successful reset_session
    import os

    mock_session.set_current_project = AsyncMock()
    with patch("mcp_server_guide.tools.session_management.SessionManager", return_value=mock_session):
        result = await reset_session()  # Now properly awaited
        print(f"DEBUG: reset_session result in success_paths = {result}")
        assert isinstance(result, dict)
        assert result["success"] is True
        # Should use current directory name, not hardcoded tool name
        expected_project = os.path.basename(os.getcwd())
        assert result["project"] == expected_project
