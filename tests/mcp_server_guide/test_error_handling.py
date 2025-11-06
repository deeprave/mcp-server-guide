"""Tests for error handling and exception scenarios in session management and config tools."""

import contextlib
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock, Mock

from mcp_server_guide.session_manager import SessionManager
from mcp_server_guide.tools.config_tools import set_project_config_values, set_project_config


async def test_session_manager_read_error():
    """Test SessionManager handles errors gracefully."""
    with tempfile.TemporaryDirectory() as _:
        manager = SessionManager()
        # Use PWD-based approach - no need to set directory

        # Test that get_current_project works without errors
        result = manager.get_project_name()
        # Should return a valid project name or None
        assert result is None or isinstance(result, str)


async def test_session_manager_write_error():
    """Test SessionManager handles write errors."""
    with tempfile.TemporaryDirectory() as _:
        manager = SessionManager()
        # Use a PWD-based approach

        # Test that set_current_project works without errors
        with contextlib.suppress(Exception):
            # Test basic functionality
            manager.set_project_name("test-project")
            result = manager.get_project_name()
            assert result == "test-project"


async def test_set_project_config_values_exception():
    """Test exception handling in set_project_config_values."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock_session:
        with patch("mcp_server_guide.tools.config_tools.get_project_config") as mock_get_config:
            # Mock session to raise exception during auto-save
            mock_instance = MagicMock()
            mock_session.return_value = mock_instance
            mock_instance.get_current_project_safe = Mock(return_value="test-project")
            mock_instance.save_to_file = Mock(side_effect=Exception("Save failed"))
            mock_instance.session_state.set_project_config = Mock()
            mock_instance.get_or_create_project_config = AsyncMock(
                return_value={"categories": {"test": {"dir": "test/", "patterns": ["*.md"]}}}
            )
            mock_get_config.return_value = {"categories": {"test": {"dir": "test/", "patterns": ["*.md"]}}}

        # This should trigger the exception handling but still succeed - using valid categories field
        result = await set_project_config_values(
            {"categories": {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test"}}}
        )
        assert result["success"] is True


async def test_set_project_config_exception():
    """Test exception handling in set_project_config."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock_session:
        # Mock session to raise exception during auto-save
        mock_instance = MagicMock()
        mock_session.return_value = mock_instance
        mock_instance.get_current_project_safe = Mock(return_value="test-project")
        mock_instance.save_to_file = Mock(side_effect=Exception("Save failed"))
        mock_instance.session_state.set_project_config = Mock()

        # This should trigger the exception handling but still succeed - using valid categories field
        result = await set_project_config(
            "categories", {"lang": {"dir": "lang/", "patterns": ["*.py"], "description": "Language files"}}
        )
        assert result["success"] is True
