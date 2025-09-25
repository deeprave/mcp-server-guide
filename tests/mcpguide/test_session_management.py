"""Tests for session management tools."""

from unittest.mock import Mock, patch
from pathlib import Path
from mcpguide.tools.session_management import save_session, load_session, reset_session


def test_save_session_error_handling():
    """Test save_session with error conditions."""
    # Test save_session with exception
    with patch("mcpguide.tools.session_management.SessionManager", side_effect=Exception("Session error")):
        result = save_session()
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "Failed to save session" in result["message"]


def test_load_session_error_handling():
    """Test load_session with error conditions."""
    # Test load_session with exception
    with patch("mcpguide.tools.session_management.SessionManager", side_effect=Exception("Load error")):
        result = load_session()
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "Failed to load session" in result["message"]

    # Test load_session with path
    test_path = Path("/test/path")
    with patch("mcpguide.tools.session_management.SessionManager", side_effect=Exception("Load error")):
        result = load_session(test_path)
        assert isinstance(result, dict)
        assert result["success"] is False


def test_reset_session_error_handling():
    """Test reset_session with error conditions."""
    # Test reset_session with exception
    with patch("mcpguide.tools.session_management.SessionManager", side_effect=Exception("Reset error")):
        result = reset_session()
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "Failed to reset session" in result["message"]


def test_session_management_success_paths():
    """Test session management success paths."""
    # Mock successful SessionManager
    mock_session = Mock()
    mock_session.get_current_project.return_value = "test_project"

    # Mock successful ProjectConfigManager
    mock_manager = Mock()

    # Test successful save_session
    with patch("mcpguide.tools.session_management.SessionManager", return_value=mock_session):
        with patch("mcpguide.tools.session_management.ProjectConfigManager", return_value=mock_manager):
            result = save_session()
            assert isinstance(result, dict)
            assert result["success"] is True
            assert result["project"] == "test_project"

    # Test successful load_session
    with patch("mcpguide.tools.session_management.SessionManager", return_value=mock_session):
        with patch("mcpguide.tools.session_management.ProjectConfigManager", return_value=mock_manager):
            result = load_session()
            assert isinstance(result, dict)
            assert result["success"] is True

    # Test successful reset_session
    with patch("mcpguide.tools.session_management.SessionManager", return_value=mock_session):
        result = reset_session()
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["project"] == "mcpguide"
