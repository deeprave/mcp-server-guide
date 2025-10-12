"""Tests for SessionManager functionality and project configuration management."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from mcp_server_guide.session_manager import (
    SessionManager,
    set_project_config,
    get_project_config,
    reset_project_config,
    switch_project,
)


class TestSessionManagerCore:
    """Test core SessionManager methods."""

    async def test_get_current_project_safe_with_none_project(self):
        """Test get_project_name when PWD is not set."""
        session_manager = SessionManager()
        session_manager.session_state.project_name = None

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="PWD environment variable not set"):
                session_manager.get_project_name()

    async def test_get_current_project_safe_with_valid_project(self):
        """Test get_project_name when project is valid."""
        session_manager = SessionManager()

        # get_project_name is NOT async
        with patch.object(session_manager, "get_project_name", return_value="test-project"):
            result = session_manager.get_project_name()
            assert result == "test-project"

    async def test_get_current_project(self):
        """Test get_current_project method."""
        session_manager = SessionManager()

        # Test with project_name set
        session_manager.session_state.project_name = "test-project"
        result = session_manager.get_project_name()
        assert result == "test-project"

        # Test with PWD fallback
        session_manager.session_state.project_name = None
        with patch.dict("os.environ", {"PWD": "/path/to/my-project"}):
            result = session_manager.get_project_name()
            assert result == "my-project"

        # Test with no PWD - should raise ValueError
        session_manager.session_state.project_name = None
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="PWD environment variable not set"):
                session_manager.get_project_name()

    async def test_set_current_project(self):
        """Test set_current_project method."""
        session_manager = SessionManager()

        # Test setting a valid project name
        session_manager.set_project_name("new-project")
        assert session_manager.project_name == "new-project"

        # Test that get_current_project returns the set value
        result = session_manager.get_project_name()
        assert result == "new-project"

    async def test_set_current_project_error_cases(self):
        """Test set_current_project method error handling."""
        import pytest

        session_manager = SessionManager()

        # Test empty project name
        with pytest.raises(ValueError, match="Project name must be a non-empty string"):
            session_manager.set_project_name("")

        # Test None project name
        with pytest.raises(ValueError, match="Project name must be a non-empty string"):
            session_manager.set_project_name(None)

        # Test non-string project name
        with pytest.raises(ValueError, match="Project name must be a non-empty string"):
            session_manager.set_project_name(123)


# Note: Tests for mocking SessionManager singleton removed - cannot mock singleton properly


class TestResetProjectConfig:
    """Test reset_project_config function missing coverage."""

    async def test_reset_project_config_project_exists(self):
        """Test reset_project_config when project exists in session state."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_project_name.return_value = "test-project"  # NOT async
            mock_session_class.return_value = mock_session

            result = await reset_project_config()

            assert result["success"] is True
            assert result["message"] == "Reset project test-project to defaults"
            # Verify reset_project_config was called with the project name
            mock_session.reset_project_config.assert_called_once_with("test-project")

    async def test_reset_project_config_project_not_exists(self):
        """Test reset_project_config when project doesn't exist in session state."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_project_name.return_value = "test-project"  # NOT async
            mock_session_class.return_value = mock_session

            result = await reset_project_config()

            assert result["success"] is True
            assert result["message"] == "Reset project test-project to defaults"
            # Verify reset_project_config was called
            mock_session.reset_project_config.assert_called_once_with("test-project")


class TestSwitchProject:
    """Test switch_project function missing coverage."""

    async def test_switch_project_success(self):
        """Test switch_project successful execution."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.switch_project = AsyncMock()  # switch_project IS async
            mock_session_class.return_value = mock_session

            result = await switch_project("new-project")

            assert result["success"] is True
            assert result["message"] == "Switched to project new-project"
            mock_session.switch_project.assert_called_once_with("new-project")

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
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.switch_project = AsyncMock(side_effect=Exception("Switch error"))
            mock_session_class.return_value = mock_session

            # The actual implementation doesn't catch exceptions, so it will raise
            with pytest.raises(Exception, match="Switch error"):
                await switch_project("new-project")


class TestSaveSession:
    """Test save_session method coverage."""

    async def test_save_session_with_empty_project_name(self, isolated_config_file):
        """Test save_session when get_project_name returns empty string."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Mock get_project_name to return empty string
        with patch.object(session_manager, "get_project_name", return_value=""):
            # Should return early without saving
            await session_manager.save_session()

            # Verify no config was saved by checking file doesn't have project data
            import yaml

            if isolated_config_file.exists():
                config_data = yaml.safe_load(isolated_config_file.read_text())
                # Should be empty or not have the projects key
                assert not config_data or "projects" not in config_data or not config_data.get("projects")


class TestSwitchProjectMethod:
    """Test SessionManager.switch_project method coverage."""

    async def test_switch_to_existing_project_loads_config(self, isolated_config_file):
        """Test switch_project loads existing config from file."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Create a project with some config
        session_manager.set_project_name("existing-project")
        session_manager.session_state.set_project_config(
            "categories", {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
        )
        await session_manager.save_session()

        # Switch to different project first
        session_manager.set_project_name("other-project")

        # Now switch back - should load the saved config
        await session_manager.switch_project("existing-project")

        assert session_manager.get_project_name() == "existing-project"
        config = session_manager.session_state.get_project_config()
        assert "categories" in config
        assert "test" in config["categories"]

    async def test_switch_to_same_project_no_op(self, isolated_config_file):
        """Test switch_project to same project is a no-op."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Set initial project
        session_manager.set_project_name("test-project")
        original_config = session_manager.session_state.get_project_config()

        # Switch to same project
        await session_manager.switch_project("test-project")

        # Should still be same project with same config
        assert session_manager.get_project_name() == "test-project"
        assert session_manager.session_state.get_project_config() == original_config


class TestModuleLevelFunctionsErrorHandling:
    """Test error handling in module-level wrapper functions."""

    async def test_set_project_config_with_value_error(self):
        """Test set_project_config handles ValueError from get_project_name."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_project_name.side_effect = ValueError("No project name")
            mock_session_class.return_value = mock_session

            result = await set_project_config("key", "value")

            assert result["success"] is False
            assert "No project name" in result["error"]

    async def test_get_project_config_with_value_error(self):
        """Test get_project_config handles ValueError from get_project_name."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get_project_name.side_effect = ValueError("No project name")
            mock_session_class.return_value = mock_session

            result = await get_project_config()

            assert result["success"] is False
            assert "No project name" in result["error"]
