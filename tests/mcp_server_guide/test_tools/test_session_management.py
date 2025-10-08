"""Tests for session management tools."""

import pytest
from unittest.mock import patch, AsyncMock
from mcp_server_guide.tools.session_management import (
    cleanup_config,
    save_session,
    load_session,
    reset_session,
)


class TestCleanupConfig:
    """Test cleanup_config function."""

    @pytest.mark.asyncio
    async def test_cleanup_config_success(self):
        """Test successful config cleanup."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            mock_session.save_to_file = AsyncMock()

            result = await cleanup_config("test_config.json")

            assert result["success"] is True
            assert "Configuration saved" in result["message"]
            mock_session.save_to_file.assert_called_once_with("test_config.json")

    @pytest.mark.asyncio
    async def test_cleanup_config_exception(self):
        """Test handling exception during config cleanup."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            mock_session.save_to_file = AsyncMock(side_effect=Exception("Save failed"))

            result = await cleanup_config("test_config.json")

            assert result["success"] is False
            assert "Save failed" in result["error"]
            assert "Failed to save configuration" in result["message"]


class TestSaveSession:
    """Test save_session function."""

    @pytest.mark.asyncio
    async def test_save_session_success(self):
        """Test successful session saving."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            mock_session.get_current_project = AsyncMock(return_value="test_project")
            mock_session.save_to_file = AsyncMock()

            result = await save_session("test_config.json")

            assert result["success"] is True
            assert result["project"] == "test_project"
            assert "Session saved for project test_project" in result["message"]

    @pytest.mark.asyncio
    async def test_save_session_exception(self):
        """Test handling exception during session saving."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            mock_session.get_current_project = AsyncMock(side_effect=Exception("Get project failed"))

            result = await save_session("test_config.json")

            assert result["success"] is False
            assert "Get project failed" in result["error"]
            assert "Failed to save session" in result["message"]


class TestLoadSession:
    """Test load_session function."""

    @pytest.mark.asyncio
    async def test_load_session_success_with_full_state(self, tmp_path):
        """Test successful session loading with full state."""
        with (
            patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class,
            patch("mcp_server_guide.tools.session_management.ProjectConfigManager") as mock_manager_class,
        ):
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            mock_session.get_current_project = AsyncMock(return_value="test_project")

            mock_manager = AsyncMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.load_full_session_state = AsyncMock(return_value=True)

            result = await load_session(tmp_path, "test_config.json")

            assert result["success"] is True
            assert result["project"] == "test_project"
            assert str(tmp_path) in result["path"]
            mock_manager.load_full_session_state.assert_called_once_with(tmp_path, mock_session, "test_config.json")

    @pytest.mark.asyncio
    async def test_load_session_exception(self, tmp_path):
        """Test handling exception during session loading."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session_class.side_effect = Exception("Session creation failed")

            result = await load_session(tmp_path, "test_config.json")

            assert result["success"] is False
            assert "Session creation failed" in result["error"]
            assert "Failed to load session" in result["message"]


class TestResetSession:
    """Test reset_session function."""

    @pytest.mark.asyncio
    async def test_reset_session_success(self):
        """Test successful session reset."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            mock_session.set_current_project = AsyncMock()

            with patch("os.getcwd", return_value="/test/project"):
                with patch("mcp_server_guide.session_tools.reset_project_config", new_callable=AsyncMock):
                    result = await reset_session()

            assert result["success"] is True
            assert result["project"] == "project"
            mock_session.set_current_project.assert_called_once_with("project")

    @pytest.mark.asyncio
    async def test_reset_session_exception(self):
        """Test handling exception during session reset."""
        with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
            mock_session_class.side_effect = Exception("Reset failed")

            result = await reset_session()

            assert result["success"] is False
            assert "Reset failed" in result["error"]
            assert "Failed to reset session" in result["message"]
