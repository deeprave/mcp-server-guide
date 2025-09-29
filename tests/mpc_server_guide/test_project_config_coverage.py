"""Tests to improve project_config.py coverage above 90%."""

import tempfile
import json
from pathlib import Path
from mcp_server_guide.project_config import ProjectConfigManager, ProjectConfig


def test_project_config_manager_save_config_corrupted_file():
    """Test ProjectConfigManager.save_config with corrupted existing file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / ".mcp-server-guide.config.json"

        # Create corrupted JSON file
        config_file.write_text("invalid json content")

        manager = ProjectConfigManager()
        config = ProjectConfig(project="test-project", docroot="/test/path")

        # Should handle corrupted file and create new one
        manager.save_config(Path(temp_dir), config)

        # Verify file was recreated with valid content
        data = json.loads(config_file.read_text())
        assert "projects" in data
        assert "test-project" in data["projects"]


def test_project_config_manager_watch_config():
    """Test ProjectConfigManager.watch_config method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = ProjectConfigManager()

        def callback():
            pass

        # This should create and start a watcher
        watcher = manager.watch_config(Path(temp_dir), callback)

        # Verify watcher was created
        assert watcher is not None

        # Stop the watcher
        watcher.stop()


def test_project_config_to_dict_excludes_empty():
    """Test ProjectConfig.to_dict excludes None and empty values."""
    config = ProjectConfig(
        project="test-project",
        docroot=None,  # Should be excluded
        tools=[],  # Should be excluded if empty
    )

    data = config.to_dict()
    assert data["project"] == "test-project"
    assert "docroot" not in data  # None values excluded
    assert "tools" not in data  # Empty lists excluded


def test_project_config_manager_load_config_default():
    """Test ProjectConfigManager.load_config returns default when no file exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = ProjectConfigManager()

        # Should return None when no config file exists
        config = manager.load_config(Path(temp_dir), "nonexistent-project")

        assert config is None


def test_project_config_manager_load_config_with_projects():
    """Test ProjectConfigManager.load_config with projects structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / ".mcp-server-guide.config.json"

        # Create config with projects structure
        config_data = {
            "projects": {"test-project": {"project": "test-project", "docroot": "/test/path"}}
        }
        config_file.write_text(json.dumps(config_data))

        manager = ProjectConfigManager()
        config = manager.load_config(Path(temp_dir), "test-project")

        assert config is not None
        assert config.project == "test-project"
        assert config.docroot == "/test/path"


def test_project_config_manager_load_config_nonexistent():
    """Test ProjectConfigManager.load_config with nonexistent project."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / ".mcp-server-guide.config.json"

        # Create config with projects structure but different project
        config_data = {"projects": {"other-project": {"project": "other-project", "docroot": "/other/path"}}}
        config_file.write_text(json.dumps(config_data))

        manager = ProjectConfigManager()
        config = manager.load_config(Path(temp_dir), "test-project")

        assert config is None
