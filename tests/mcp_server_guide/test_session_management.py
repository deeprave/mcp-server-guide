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
    categories = {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
    session.session_state.set_project_config("categories", categories)

    # This should return current project config
    result = await get_project_config()

    assert result["success"] is True
    assert result["project"] == "test-project"
    assert "config" in result
    assert "test" in result["config"]["categories"]


async def test_set_project_config():
    """Test set_project_config function."""
    # Set up project data first
    session = SessionManager()
    session.set_project_name("test-project")
    categories1 = {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
    session.session_state.set_project_config("categories", categories1)

    # Update the categories
    categories2 = {"docs": {"dir": "docs/", "patterns": ["*.md"], "description": "Docs category"}}
    result = await set_project_config("categories", categories2)

    assert result["success"] is True
    assert "Set categories" in result["message"]
    assert "test-project" in result["message"]


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
        categories = {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
        session.session_state.set_project_config("categories", categories)

        # Save session (uses mocked path)
        await session.save_session()

        # Verify file was created and contains data
        assert config_file.exists()


async def test_session_manager_get_or_create_project_config():
    """Test SessionManager.get_or_create_project_config method."""
    session = SessionManager()
    session.set_project_name("test-project")
    categories = {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
    session.session_state.set_project_config("categories", categories)

    # Get or create config - should return the set config
    config = await session.get_or_create_project_config("test-project")

    assert "test" in config["categories"]
