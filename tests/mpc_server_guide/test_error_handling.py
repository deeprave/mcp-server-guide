"""Tests for error handling and exception scenarios in session management and config tools."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from mcp_server_guide.session_tools import SessionManager
from mcp_server_guide.tools.config_tools import set_project_config_values, set_project_config


async def test_session_manager_read_error():
    """Test SessionManager handles file read errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SessionManager()
        manager.set_directory(Path(temp_dir))

        # Create a file with invalid permissions to trigger read error
        current_file = manager.current_file
        current_file.write_text("test-project")
        current_file.chmod(0o000)  # Remove all permissions

        try:
            # This should trigger the exception handling path
            result = await manager.get_current_project()
            # Should fallback to directory name
            assert result == Path(temp_dir).name
        finally:
            # Restore permissions for cleanup
            current_file.chmod(0o644)


async def test_session_manager_write_error():
    """Test SessionManager handles write errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SessionManager()
        manager.set_directory(Path(temp_dir))  # NOT awaited

        # Create the current file first, then make it read-only
        current_file = Path(temp_dir) / ".mcp-server-guide.current"
        current_file.write_text("initial")
        current_file.chmod(0o444)  # Make file read-only

        try:
            # This should trigger the exception handling path and raise
            with pytest.raises((OSError, IOError, PermissionError)):
                await manager.set_current_project("test-project")
        finally:
            # Restore permissions for cleanup
            current_file.chmod(0o644)


async def test_set_project_config_values_exception():
    """Test exception handling in set_project_config_values."""
    with patch("mcp_server_guide.tools.config_tools.SessionManager") as mock_session:
        # Mock session to raise exception during auto-save
        mock_instance = MagicMock()
        mock_session.return_value = mock_instance
        mock_instance.get_current_project_safe = AsyncMock(return_value="test-project")
        mock_instance.save_to_file = AsyncMock(side_effect=Exception("Save failed"))

        # This should trigger the exception handling but still succeed
        result = await set_project_config_values({"docroot": "/test/path"})
        assert result["success"] is True


async def test_set_project_config_exception():
    """Test exception handling in set_project_config."""
    with patch("mcp_server_guide.tools.config_tools.SessionManager") as mock_session:
        # Mock session to raise exception during auto-save
        mock_instance = MagicMock()
        mock_session.return_value = mock_instance
        mock_instance.get_current_project_safe = AsyncMock(return_value="test-project")
        mock_instance.save_to_file = AsyncMock(side_effect=Exception("Save failed"))

        # This should trigger the exception handling but still succeed
        result = await set_project_config("language", "python")
        assert result["success"] is True
