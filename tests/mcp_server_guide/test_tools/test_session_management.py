"""Tests for session management tools."""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from mcp_server_guide.tools.session_management import (
    set_directory,
    cleanup_config,
    save_session,
    load_session,
    reset_session,
    require_directory_set,
)


class TestRequireDirectorySetDecorator:
    """Test the require_directory_set decorator."""

    def test_require_directory_set_when_directory_not_set(self):
        """Test decorator blocks execution when directory not set."""

        @require_directory_set
        def test_func():
            return {"success": True, "message": "Should not reach here"}

        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.is_directory_set.return_value = False
            mock_session_class.return_value = mock_session

            result = test_func()

            assert result["success"] is False
            assert "Working directory not set" in result["error"]
            assert result["blocked"] is True

    def test_require_directory_set_when_directory_is_set(self):
        """Test decorator allows execution when directory is set."""

        @require_directory_set
        def test_func():
            return {"success": True, "message": "Function executed"}

        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.is_directory_set.return_value = True
            mock_session_class.return_value = mock_session

            result = test_func()

            assert result["success"] is True
            assert result["message"] == "Function executed"


class TestSetDirectory:
    """Test set_directory function."""

    async def test_set_directory_success(self, tmp_path):
        """Test successful directory setting."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_current_project = AsyncMock(return_value="test-project")
            mock_session_class.return_value = mock_session

            result = await set_directory(str(tmp_path))

            assert result["success"] is True
            assert "Working directory set to:" in result["message"]
            assert result["project"] == "test-project"
            mock_session.set_directory.assert_called_once_with(str(tmp_path.resolve()))

    async def test_set_directory_with_path_object(self, tmp_path):
        """Test set_directory with pathlib.Path input."""
        from pathlib import Path

        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_current_project = AsyncMock(return_value="test-project")
            mock_session_class.return_value = mock_session

            result = await set_directory(Path(str(tmp_path)))

            assert result["success"] is True
            assert "Working directory set to:" in result["message"]
            mock_session.set_directory.assert_called_once_with(str(tmp_path.resolve()))

    async def test_set_directory_nonexistent_path(self):
        """Test setting directory that doesn't exist."""
        nonexistent_path = "/path/that/does/not/exist"

        result = await set_directory(nonexistent_path)

        assert result["success"] is False
        assert f"Directory does not exist: {nonexistent_path}" in result["error"]

    async def test_set_directory_path_is_file(self, tmp_path):
        """Test setting directory when path is a file."""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")

        result = await set_directory(str(test_file))

        assert result["success"] is False
        assert f"Path is not a directory: {test_file}" in result["error"]

    async def test_set_directory_none_or_empty(self):
        """Test setting directory with None or empty string."""
        # Test with non-existent path
        result = await set_directory("/nonexistent/path/that/does/not/exist")
        assert result["success"] is False
        assert "Directory does not exist:" in result["error"]

        # Test with None as input
        result_none = await set_directory(None)
        assert result_none["success"] is False
        assert "Directory must be a non-empty string" in result_none["error"]

        # Test with empty string as input
        result_empty = await set_directory("")
        assert result_empty["success"] is False
        assert "Directory must be a non-empty string" in result_empty["error"]

        # Test with whitespace-only string as input
        result_whitespace = await set_directory("   ")
        assert result_whitespace["success"] is False
        assert "Directory must be a non-empty string" in result_whitespace["error"]

    async def test_set_directory_symlinks(self, tmp_path):
        """Test set_directory with symlinks to files and directories."""
        # Create a file and directory
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Test symlink to file (should fail)
        file_symlink = tmp_path / "file_symlink"
        file_symlink.symlink_to(test_file)
        result = await set_directory(str(file_symlink))
        assert result["success"] is False
        assert "Path is not a directory:" in result["error"]

        # Test symlink to directory (should succeed)
        dir_symlink = tmp_path / "dir_symlink"
        dir_symlink.symlink_to(test_dir, target_is_directory=True)

        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_current_project = AsyncMock(return_value="test-project")
            mock_session_class.return_value = mock_session

            result = await set_directory(str(dir_symlink))
            assert result["success"] is True

    async def test_set_directory_exception(self, tmp_path):
        """Test handling exception during directory setting."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.set_directory.side_effect = ValueError("Test error")
            mock_session_class.return_value = mock_session

            result = await set_directory(str(tmp_path))

            assert result["success"] is False
            assert "Failed to set directory: Test error" in result["error"]


class TestCleanupConfig:
    """Test cleanup_config function."""

    @pytest.mark.asyncio
    async def test_cleanup_config_success(self):
        """Test successful config cleanup."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.is_directory_set.return_value = True
            mock_session.save_to_file = AsyncMock()
            mock_session_class.return_value = mock_session

            result = await cleanup_config("test_config.json")

            assert result["success"] is True
            assert result["message"] == "Configuration saved"
            mock_session.save_to_file.assert_called_once_with("test_config.json")

    @pytest.mark.asyncio
    async def test_cleanup_config_exception(self):
        """Test handling exception during config cleanup."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.is_directory_set.return_value = True
            mock_session.save_to_file = AsyncMock(side_effect=Exception("Save error"))
            mock_session_class.return_value = mock_session

            result = await cleanup_config("test_config.json")

            assert result["success"] is False
            assert result["error"] == "Save error"
            assert result["message"] == "Failed to save configuration"


class TestSaveSession:
    """Test save_session function."""

    @pytest.mark.asyncio
    async def test_save_session_success(self):
        """Test successful session saving."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_current_project = AsyncMock(return_value="test-project")
            mock_session.save_to_file = AsyncMock()
            mock_session_class.return_value = mock_session

            result = await save_session("test_config.json")

            assert result["success"] is True
            assert result["project"] == "test-project"
            assert "Session saved for project test-project" in result["message"]
            mock_session.save_to_file.assert_called_once_with("test_config.json")

    @pytest.mark.asyncio
    async def test_save_session_exception(self):
        """Test handling exception during session saving."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_current_project = AsyncMock(side_effect=Exception("Save error"))
            mock_session.save_to_file = AsyncMock()
            mock_session_class.return_value = mock_session

            result = await save_session("test_config.json")

            assert result["success"] is False
            assert result["error"] == "Save error"
            assert result["message"] == "Failed to save session"


class TestLoadSession:
    """Test load_session function."""

    async def test_load_session_success_with_full_state(self, tmp_path):
        """Test successful session loading with full state."""
        with (
            patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class,
            patch("mcp_server_guide.tools.session_management.ProjectConfigManager") as mock_manager_class,
        ):
            mock_session = MagicMock()
            mock_session.get_current_project = AsyncMock(return_value="test-project")
            mock_session.load_project_from_path = AsyncMock()
            mock_session_class.return_value = mock_session

            mock_manager = MagicMock()
            mock_manager.load_full_session_state = AsyncMock(return_value=True)
            mock_manager_class.return_value = mock_manager

            result = await load_session(tmp_path, "test_config.json")

            assert result["success"] is True
            assert result["path"] == str(tmp_path)
            assert result["project"] == "test-project"
            assert f"Session loaded from {tmp_path}" in result["message"]
            mock_manager.load_full_session_state.assert_called_once_with(tmp_path, mock_session, "test_config.json")

    async def test_load_session_fallback_to_project_loading(self, tmp_path):
        """Test session loading falls back to project-based loading."""
        with (
            patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class,
            patch("mcp_server_guide.tools.session_management.ProjectConfigManager") as mock_manager_class,
        ):
            mock_session = MagicMock()
            mock_session.get_current_project = AsyncMock(return_value="test-project")
            mock_session.load_project_from_path = AsyncMock()
            mock_session_class.return_value = mock_session

            mock_manager = MagicMock()
            mock_manager.load_full_session_state = AsyncMock(return_value=False)
            mock_manager_class.return_value = mock_manager

            result = await load_session(tmp_path, "test_config.json")

            assert result["success"] is True
            assert result["path"] == str(tmp_path)
            assert result["project"] == "test-project"
            assert f"Session loaded from {tmp_path}" in result["message"]
            mock_session.load_project_from_path.assert_called_once_with(tmp_path)

    async def test_load_session_default_path(self):
        """Test session loading with default path."""
        with (
            patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class,
            patch("mcp_server_guide.tools.session_management.ProjectConfigManager") as mock_manager_class,
        ):
            mock_session = MagicMock()
            mock_session.get_current_project = AsyncMock(return_value="test-project")
            mock_session_class.return_value = mock_session

            mock_manager = MagicMock()
            mock_manager.load_full_session_state = AsyncMock(return_value=True)
            mock_manager_class.return_value = mock_manager

            result = await load_session(None, "test_config.json")

            assert result["success"] is True
            assert result["project"] == "test-project"
            # Should use Path(".") as default
            mock_manager.load_full_session_state.assert_called_once()
            call_args = mock_manager.load_full_session_state.call_args[0]
            assert str(call_args[0]) == "."

    async def test_load_session_invalid_path_type(self, tmp_path):
        """Test load_session with invalid path type, file path, and symlinks."""
        # Test with invalid path type (should handle gracefully)
        result = await load_session(123, "test_config.json")
        assert result["success"] is False
        assert "Failed to load session" in result["message"]

        # Test with a file path instead of a directory (should fail)
        file_path = tmp_path / "not_a_directory.txt"
        file_path.write_text("dummy content")
        result = await load_session(file_path, "test_config.json")
        assert result["success"] is False
        assert "exists but is not a directory" in result["error"]

        # Test with a symlink to a file (should fail)
        file_symlink = tmp_path / "file_symlink"
        file_symlink.symlink_to(file_path)
        result = await load_session(file_symlink, "test_config.json")
        assert result["success"] is False
        assert "exists but is not a directory" in result["error"]

        # Test with a symlink to a directory (should succeed)
        dir_path = tmp_path / "real_dir"
        dir_path.mkdir()
        dir_symlink = tmp_path / "dir_symlink"
        dir_symlink.symlink_to(dir_path, target_is_directory=True)
        result = await load_session(dir_symlink, "test_config.json")
        assert result["success"] is True

    async def test_load_session_exception(self, tmp_path):
        """Test handling exception during session loading."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session_class.side_effect = Exception("Load error")

            result = await load_session(tmp_path, "test_config.json")

            assert result["success"] is False
            assert result["error"] == "Load error"
            assert result["message"] == "Failed to load session"


class TestResetSession:
    """Test reset_session function."""

    async def test_reset_session_success(self):
        """Test successful session reset."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.set_current_project = AsyncMock()
            mock_session_class.return_value = mock_session

            result = await reset_session()  # Now properly awaited
            expected_project = os.path.basename(os.getcwd())

            assert result["success"] is True
            assert result["project"] == expected_project
            assert result["message"] == "Session reset to defaults"
            # Note: In test context, async calls are skipped to avoid event loop conflicts

    async def test_reset_session_with_none_project(self):
        """Test reset_session when get_current_project returns None."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.set_current_project = AsyncMock()
            mock_session_class.return_value = mock_session

            result = await reset_session()  # Now properly awaited
            expected_project = os.path.basename(os.getcwd())

            assert result["success"] is True
            assert result["project"] == expected_project
            assert result["message"] == "Session reset to defaults"
            # Note: In test context, async calls are skipped to avoid event loop conflicts

    async def test_reset_session_set_current_project_raises_valueerror(self):
        """Test reset_session when set_current_project raises ValueError."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.set_current_project.side_effect = ValueError("Invalid project")
            mock_session_class.return_value = mock_session

            result = await reset_session()

            assert result["success"] is False
            assert "Invalid project" in result["error"]

    async def test_reset_session_exception(self):
        """Test handling exception during session reset."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.set_current_project.side_effect = Exception("Reset error")
            mock_session_class.return_value = mock_session

            result = await reset_session()

            assert result["success"] is False
            assert result["error"] == "Reset error"
            assert result["message"] == "Failed to reset session"
