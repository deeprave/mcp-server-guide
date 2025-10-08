"""Tests for SessionManager functionality and project configuration management."""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock, AsyncMock
from mcp_server_guide.session_tools import (
    SessionManager,
    set_project_config,
    get_project_config,
    list_project_configs,
    reset_project_config,
    switch_project,
)
from mcp_server_guide.validation import ConfigValidationError


class TestSessionManagerCore:
    """Test core SessionManager methods."""

    async def test_get_current_project_safe_with_none_project(self):
        """Test get_current_project_safe when project is None."""
        session_manager = SessionManager()

        with patch.object(session_manager, "get_current_project", return_value=None):
            with pytest.raises(ValueError, match="Working directory not set. Use set_directory\\(\\) first."):
                await session_manager.get_current_project_safe()

    async def test_get_current_project_safe_with_valid_project(self):
        """Test get_current_project_safe when project is valid."""
        session_manager = SessionManager()

        with patch.object(session_manager, "get_current_project", return_value="test-project"):
            result = await session_manager.get_current_project_safe()
            assert result == "test-project"

    async def test_get_current_project(self):
        """Test get_current_project method."""
        session_manager = SessionManager()

        # Mock the directory and current_file properties using property mock
        with (
            patch.object(session_manager, "is_directory_set", return_value=True),
            patch.object(type(session_manager), "current_file", new_callable=PropertyMock) as mock_current_file,
            patch("aiofiles.open") as mock_aiofiles_open,
        ):
            # Create a mock file object
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            mock_current_file.return_value = mock_file

            # Mock aiofiles context manager
            mock_file_handle = MagicMock()
            mock_file_handle.read = AsyncMock(return_value="test-project")
            mock_aiofiles_open.return_value.__aenter__.return_value = mock_file_handle

            result = await session_manager.get_current_project()
            assert result == "test-project"

    def test_is_directory_set(self):
        """Test is_directory_set method."""
        session_manager = SessionManager()

        with patch.object(type(session_manager), "directory", new_callable=PropertyMock) as mock_directory:
            mock_directory.return_value = None
            assert session_manager.is_directory_set() is False

            mock_directory.return_value = "/some/path"
            assert session_manager.is_directory_set() is True

    def test_set_directory(self):
        """Test set_directory method."""
        import tempfile
        from pathlib import Path

        session_manager = SessionManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            session_manager.set_directory(temp_dir)
            assert session_manager._override_directory == Path(temp_dir).resolve()

    def test_set_directory_with_path_object(self):
        """Test set_directory method with pathlib.Path input."""
        import tempfile
        from pathlib import Path

        session_manager = SessionManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            session_manager.set_directory(Path(temp_dir))
            assert session_manager._override_directory == Path(temp_dir).resolve()

    def test_set_directory_invalid_input(self):
        """Test set_directory method with invalid inputs."""
        import pytest

        session_manager = SessionManager()

        # Test non-existent directory
        with pytest.raises(ValueError, match="does not exist"):
            session_manager.set_directory("/non/existent/directory")

        # Test incorrect type
        with pytest.raises(TypeError):
            session_manager.set_directory(123)

    async def test_set_current_project(self):
        """Test set_current_project method."""
        session_manager = SessionManager()

        with (
            patch.object(session_manager, "is_directory_set", return_value=True),
            patch.object(session_manager, "get_current_project", return_value="old-project"),
            patch.object(type(session_manager), "current_file", new_callable=PropertyMock) as mock_current_file,
        ):
            mock_file = MagicMock()
            mock_current_file.return_value = mock_file

            await session_manager.set_current_project("new-project")
            mock_file.write_text.assert_called_once_with("new-project", encoding="utf-8")

    async def test_set_current_project_error_cases(self):
        """Test set_current_project method error handling."""
        import pytest

        session_manager = SessionManager()

        # Test missing directory
        with patch.object(session_manager, "is_directory_set", return_value=False):
            with pytest.raises(ValueError, match="Directory must be set before setting current project"):
                await session_manager.set_current_project("test-project")

        # Test invalid project name (empty string)
        with patch.object(session_manager, "is_directory_set", return_value=True):
            with pytest.raises(ValueError, match="Project name must be a non-empty string"):
                await session_manager.set_current_project("")


class TestProjectConfigManagement:
    """Test project configuration management functions."""

    async def test_set_project_config_validation_error(self):
        """Test set_project_config with validation error."""
        with (
            patch("mcp_server_guide.session_tools.SessionManager") as mock_session_class,
            patch("mcp_server_guide.session_tools.validate_config_key") as mock_validate,
        ):
            # Mock validation error
            validation_error = ConfigValidationError("Invalid value", ["error message"])
            mock_validate.side_effect = validation_error

            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            result = await set_project_config("test_key", "invalid_value")

            assert result["success"] is False
            assert result["error"] == "Invalid value"
            assert result["errors"] == ["error message"]

    async def test_set_project_config_value_error_from_get_current_project_safe(self):
        """Test set_project_config with ValueError from get_current_project_safe."""
        with (
            patch("mcp_server_guide.session_tools.SessionManager") as mock_session_class,
            patch("mcp_server_guide.session_tools.validate_config_key"),
        ):
            mock_session = MagicMock()
            mock_session.get_current_project_safe.side_effect = ValueError("Directory not set")
            mock_session_class.return_value = mock_session

            result = await set_project_config("test_key", "test_value")

            assert result["success"] is False
            assert result["error"] == "Directory not set"


class TestGetProjectConfig:
    """Test get_project_config function."""

    async def test_get_project_config_value_error(self):
        """Test get_project_config with ValueError from get_current_project_safe."""
        with patch("mcp_server_guide.session_tools.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_current_project_safe.side_effect = ValueError("Directory not set")
            mock_session_class.return_value = mock_session

            result = await get_project_config()

            assert result["success"] is False
            assert result["error"] == "Directory not set"

    async def test_get_project_config_success(self):
        """Test get_project_config successful execution."""
        with patch("mcp_server_guide.session_tools.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_current_project_safe = AsyncMock(return_value="test-project")
            mock_session.session_state.get_project_config = AsyncMock(return_value={"key": "value"})
            mock_session_class.return_value = mock_session

            result = await get_project_config()

            assert result["success"] is True
            assert result["project"] == "test-project"
            assert result["config"] == {"key": "value"}


class TestListProjectConfigs:
    """Test list_project_configs function missing coverage."""

    async def test_list_project_configs_success(self):
        """Test list_project_configs successful execution."""
        with patch("mcp_server_guide.session_tools.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.session_state.projects = ["project1", "project2"]
            mock_session.session_state.get_project_config = AsyncMock(side_effect=lambda p: {f"{p}_key": f"{p}_value"})
            mock_session_class.return_value = mock_session

            result = await list_project_configs()

            assert result["success"] is True
            assert result["projects"] == {
                "project1": {"project1_key": "project1_value"},
                "project2": {"project2_key": "project2_value"},
            }


class TestResetProjectConfig:
    """Test reset_project_config function missing coverage."""

    async def test_reset_project_config_project_exists(self):
        """Test reset_project_config when project exists in session state."""
        with patch("mcp_server_guide.session_tools.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_current_project = AsyncMock(return_value="test-project")
            mock_session.session_state.projects = {"test-project": {"key": "value"}}
            mock_session_class.return_value = mock_session

            result = await reset_project_config()

            assert result["success"] is True
            assert result["message"] == "Reset project test-project to defaults"
            # Verify the project was deleted from session state
            assert "test-project" not in mock_session.session_state.projects

    async def test_reset_project_config_project_not_exists(self):
        """Test reset_project_config when project doesn't exist in session state."""
        with patch("mcp_server_guide.session_tools.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_current_project = AsyncMock(return_value="test-project")
            mock_session.session_state.projects = {}  # Empty projects
            mock_session_class.return_value = mock_session

            result = await reset_project_config()

            assert result["success"] is True
            assert result["message"] == "Reset project test-project to defaults"


class TestSwitchProject:
    """Test switch_project function missing coverage."""

    async def test_switch_project_success(self):
        """Test switch_project successful execution."""
        with patch("mcp_server_guide.session_tools.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.set_current_project = AsyncMock()
            mock_session_class.return_value = mock_session

            result = await switch_project("new-project")

            assert result["success"] is True
            assert result["message"] == "Switched to project new-project"
            mock_session.set_current_project.assert_called_once_with("new-project")

    async def test_switch_project_invalid_project_name(self):
        """Test switch_project with None, empty, or non-string project name."""
        # Test with empty string
        with pytest.raises(ValueError, match="Project name must be a non-empty string"):
            await switch_project("")

        # Test with None
        with pytest.raises(ValueError, match="Project name must be a non-empty string"):
            await switch_project(None)

        # Test with integer
        with pytest.raises(ValueError, match="Project name must be a non-empty string"):
            await switch_project(123)

        # Test with list
        with pytest.raises(ValueError, match="Project name must be a non-empty string"):
            await switch_project(["project1"])

    async def test_switch_project_exception(self):
        """Test switch_project with exception."""
        with patch("mcp_server_guide.session_tools.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.set_current_project = AsyncMock(side_effect=Exception("Switch error"))
            mock_session_class.return_value = mock_session

            # The actual implementation doesn't catch exceptions, so it will raise
            with pytest.raises(Exception, match="Switch error"):
                await switch_project("new-project")
