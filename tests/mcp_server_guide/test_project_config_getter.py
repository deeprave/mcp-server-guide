"""Test for ProjectConfigManager getter method."""

from mcp_server_guide.project_config import ProjectConfigManager
from mcp_server_guide.naming import mcp_name
from pathlib import Path
import tempfile
import yaml


async def test_project_config_manager_has_getter_method():
    """Test that ProjectConfigManager has get_config_filename method."""
    manager = ProjectConfigManager()

    # Should have the getter method
    assert hasattr(manager, "get_config_filename")

    # Should return the global config path
    filename = manager.get_config_filename()
    # Should be a full path containing mcp_name and ending with config.yaml
    assert mcp_name() in str(filename)
    assert str(filename).endswith("config.yaml")


async def test_project_config_manager_getter_is_mockable():
    """Test that the getter method can be mocked for testing."""
    from unittest.mock import patch

    manager = ProjectConfigManager()

    # Mock the getter method
    with patch.object(manager, "get_config_filename", return_value="test-config.yaml"):
        filename = manager.get_config_filename()
        assert filename == "test-config.yaml"


async def test_project_config_manager_uses_getter_internally():
    """Test that ProjectConfigManager uses getter method for file operations."""
    from unittest.mock import patch
    from mcp_server_guide.project_config import ProjectConfig

    manager = ProjectConfigManager()

    # Mock the getter to return a custom filename
    with patch.object(manager, "get_config_filename", return_value="custom-config.yaml"):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir)
            config = ProjectConfig(categories={})

            # Save config - should use the mocked filename
            manager.save_config("test-project", config)

            # The custom filename should exist (global config location)
            custom_file = Path("custom-config.yaml")
            assert custom_file.exists()

            # Clean up
            custom_file.unlink(missing_ok=True)


async def test_project_config_manager_load_uses_getter():
    """Test that load_config also uses getter method."""

    manager = ProjectConfigManager()

    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir)

        # Create a config file with custom name
        # Create custom config file in current directory (will be found by mocked getter)
        custom_config_file = Path("custom-load-config.yaml")
        manager.set_config_filename(custom_config_file)
        config_data = {
            "projects": {
                "test-project": {
                    "categories": {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test"}}
                }
            }
        }
        custom_config_file.write_text(yaml.dump(config_data))

        try:
            config = manager.load_config("test-project")

            # Should successfully load the config
            assert config is not None
            assert "test" in config.categories
            assert config.categories["test"].dir == "test/"
        finally:
            # Clean up
            custom_config_file.unlink(missing_ok=True)
