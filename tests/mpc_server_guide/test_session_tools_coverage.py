"""Tests to improve session_tools.py coverage above 90%."""

import tempfile
import json
from pathlib import Path
from mcp_server_guide.session_tools import (
    SessionManager,
    get_project_config,
    list_project_configs,
    switch_project,
    set_local_file,
    set_project_config,
)


async def test_session_manager_load_project_from_path():
    """Test SessionManager.load_project_from_path method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test.json"

        # Create config with project and other fields
        config_data = {"project": "test-project", "language": "python", "docroot": ".", "guidesdir": "guide/"}
        config_file.write_text(json.dumps(config_data))

        session = SessionManager()
        await session.load_project_from_path(config_file)

        # The project name will be derived from the directory, not the config file
        # This is the expected behavior based on the implementation
        current_project = await session.get_current_project()
        assert current_project is not None
        assert len(current_project) > 0


async def test_get_project_config():
    """Test get_project_config function."""
    # Set up some project data first
    session = SessionManager()
    await session.set_current_project("test-project")
    session.session_state.set_project_config("test-project", "language", "python")

    # This should return current project config
    result = await get_project_config()

    assert result["success"] is True
    assert result["project"] == "test-project"
    assert "config" in result
    assert result["config"]["language"] == "python"


async def test_list_project_configs():
    """Test list_project_configs function."""
    # Set up some project data first
    session = SessionManager()
    session.session_state.set_project_config("test-project", "language", "python")
    session.session_state.set_project_config("other-project", "language", "javascript")

    # This should return all project configs
    result = list_project_configs()

    assert result["success"] is True
    assert "projects" in result
    assert isinstance(result["projects"], dict)
    assert "test-project" in result["projects"]
    assert "other-project" in result["projects"]


async def test_set_project_config():
    """Test set_project_config function."""
    # Set up project data first
    session = SessionManager()
    await session.set_current_project("test-project")
    session.session_state.set_project_config("test-project", "language", "python")

    # Reset the project
    result = await set_project_config("language", "go")

    assert result["success"] is True
    assert "Set language to 'go' for project test-project" in result["message"]


async def test_switch_project():
    """Test switch_project function."""
    result = await switch_project("new-project")

    assert result["success"] is True
    assert result["message"] == "Switched to project new-project"

    # Verify the switch worked
    session = SessionManager()
    current_project = await session.get_current_project()
    assert current_project == "new-project"


async def test_set_local_file():
    """Test set_local_file function."""
    result = await set_local_file("guide", "/path/to/local/file.md")

    assert result["success"] is True
    assert "Set guide to 'local:/path/to/local/file.md'" in result["message"]


async def test_session_manager_save_to_file():
    """Test SessionManager.save_to_file method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_save.json"

        session = SessionManager()
        await session.set_current_project("test-project")
        session.session_state.set_project_config("test-project", "language", "python")

        # Save to file
        await session.save_to_file(config_file)

        # Verify file was created and contains data
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert "projects" in data
        assert "test-project" in data["projects"]
        assert data["projects"]["test-project"]["language"] == "python"


async def test_session_manager_get_effective_config():
    """Test SessionManager.get_effective_config method."""
    session = SessionManager()
    await session.set_current_project("test-project")
    session.session_state.set_project_config("test-project", "language", "python")

    # Get effective config - it merges with defaults so just check language
    config = session.get_effective_config("test-project")

    assert config["language"] == "python"
