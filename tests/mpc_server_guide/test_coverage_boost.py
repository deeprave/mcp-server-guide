"""Tests to boost coverage for error handling paths."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from mcp_server_guide.current_project_manager import CurrentProjectManager
from mcp_server_guide.tools.config_tools import set_project_config_values, set_project_config


async def test_current_project_manager_read_error():
    """Test CurrentProjectManager handles file read errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = CurrentProjectManager(Path(temp_dir))

        # Create a file with invalid permissions to trigger read error
        current_file = manager.current_file
        current_file.write_text("test-project")
        current_file.chmod(0o000)  # Remove all permissions

        try:
            # This should trigger the exception handling path
            result = manager.get_current_project()
            # Should fallback to directory name
            assert result == Path(temp_dir).name
        finally:
            # Restore permissions for cleanup
            current_file.chmod(0o644)


async def test_current_project_manager_clear_error():
    """Test CurrentProjectManager handles clear errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = CurrentProjectManager(Path(temp_dir))

        # Create current file
        manager.set_current_project("test-project")

        # Make directory read-only to prevent file deletion
        Path(temp_dir).chmod(0o444)

        try:
            # This should trigger the exception handling path but not raise
            manager.clear_current_project()
        finally:
            # Restore permissions for cleanup
            Path(temp_dir).chmod(0o755)


async def test_current_project_manager_write_error():
    """Test CurrentProjectManager handles write errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = CurrentProjectManager(Path(temp_dir))

        # Make directory read-only to prevent file creation
        Path(temp_dir).chmod(0o444)

        try:
            # This should trigger the exception handling path and raise
            with pytest.raises((OSError, IOError)):
                manager.set_current_project("test-project")
        finally:
            # Restore permissions for cleanup
            Path(temp_dir).chmod(0o755)


async def test_set_project_config_values_exception():
    """Test exception handling in set_project_config_values."""
    with patch("mcp_server_guide.tools.config_tools.SessionManager") as mock_session:
        # Mock session to raise exception during auto-save
        mock_instance = MagicMock()
        mock_session.return_value = mock_instance
        mock_instance.save_to_file.side_effect = Exception("Save failed")

        # This should trigger the exception handling but still succeed
        result = await set_project_config_values({"docroot": "/test/path"})
        assert result["success"] is True


async def test_set_project_config_exception():
    """Test exception handling in set_project_config."""
    with patch("mcp_server_guide.tools.config_tools.SessionManager") as mock_session:
        # Mock session to raise exception during auto-save
        mock_instance = MagicMock()
        mock_session.return_value = mock_instance
        mock_instance.save_to_file.side_effect = Exception("Save failed")

        # This should trigger the exception handling but still succeed
        result = await set_project_config("language", "python")
        assert result["success"] is True
