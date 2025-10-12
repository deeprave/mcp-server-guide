"""Tests to improve session management functionality coverage above 90%."""

import tempfile
from pathlib import Path
from mcp_server_guide.session_manager import (
    SessionManager,
    get_project_config,
    switch_project,
    set_project_config,
)


async def test_get_project_config():
    """Test get_project_config function."""
    # Set up some project data first
    session = SessionManager()
    session.set_project_name("test-project")
    session.session_state.set_project_config("language", "python")

    # This should return current project config
    result = await get_project_config()

    assert result["success"] is True
    assert result["project"] == "test-project"
    assert "config" in result
    assert result["config"]["language"] == "python"


async def test_set_project_config():
    """Test set_project_config function."""
    # Set up project data first
    session = SessionManager()
    session.set_project_name("test-project")
    session.session_state.set_project_config("language", "python")

    # Reset the project
    result = await set_project_config("language", "go")

    assert result["success"] is True
    assert "Set language to 'go' for project test-project" in result["message"]


async def test_switch_project(isolated_config_file):
    """Test switch_project function."""
    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    result = await switch_project("new-project")

    assert result["success"] is True
    assert result["message"] == "Switched to project new-project"

    # Verify the switch worked
    session = SessionManager()
    current_project = session.get_project_name()
    assert current_project == "new-project"


async def test_session_manager_save_session(isolated_config_file):
    """Test SessionManager.save_session method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_save.yaml"

        session = SessionManager()
        # Use isolated config file to prevent touching global config
        session._set_config_filename(str(config_file))

        session.set_project_name("test-project")
        session.session_state.set_project_config("language", "python")

        # Save session (uses mocked path)
        await session.save_session()

        # Verify file was created and contains data
        assert config_file.exists()


async def test_session_manager_get_effective_config():
    """Test SessionManager.get_effective_config method."""
    session = SessionManager()
    session.set_project_name("test-project")
    session.session_state.set_project_config("language", "python")

    # Get effective config - it merges with defaults so just check language
    config = await session.get_effective_config("test-project")

    assert config["language"] == "python"
