"""Test config format and structure."""

import yaml
from mcp_server_guide.project_config import ProjectConfig, ProjectConfigManager


class TestConfigFormatUpdates:
    """Test config format updates and structure."""

    async def test_project_config_dataclass_structure(self):
        """Test that ProjectConfig has expected structure."""
        config = ProjectConfig(categories={})

        # Should not have current_project field
        assert not hasattr(config, "current_project")

        # Should have expected fields (project name is now a dict key, not a field)
        assert hasattr(config, "docroot")
        assert hasattr(config, "categories")

    async def test_config_serialization_structure(self):
        """Test that config serialization has correct structure."""
        config = ProjectConfig(docroot="/test/path", categories={})

        config_dict = config.to_dict()

        # Should not contain current_project
        assert "current_project" not in config_dict

        # Should contain expected fields (project is not a field, it's a dict key in ConfigFile)
        assert config_dict["docroot"] == "/test/path"

    async def test_config_save_format(self, tmp_path, monkeypatch):
        """Test that saving config uses correct format."""
        manager = ProjectConfigManager()

        # Set the config path to use tmp_path with YAML extension
        config_file_path = tmp_path / "config.yaml"
        manager.set_config_filename(config_file_path)

        config = ProjectConfig(docroot="/new/path", categories={})
        manager.save_config("new-project", config)

        # Read saved file from global config location (now YAML format)
        saved_data = yaml.safe_load(config_file_path.read_text())

        # Should not have current_project
        assert "current_project" not in saved_data

        # Should have projects structure
        assert "projects" in saved_data
        assert "new-project" in saved_data["projects"]

        # Should use correct field names
        project_data = saved_data["projects"]["new-project"]
        assert project_data["docroot"] == "/new/path"
