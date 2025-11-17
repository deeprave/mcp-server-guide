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

        # Should NOT have docroot field (it's in ConfigFile now, not ProjectConfig)
        assert not hasattr(config, "docroot")

        # Should have categories field only
        assert hasattr(config, "categories")

    async def test_config_serialization_structure(self):
        """Test that config serialization has correct structure."""
        from mcp_server_guide.models.category import Category

        config = ProjectConfig(categories={"test": Category(dir="test/", patterns=["*.md"], description="Test")})

        config_dict = config.to_dict()

        # Should not contain current_project
        assert "current_project" not in config_dict

        # Should NOT contain docroot (it's in ConfigFile, not ProjectConfig)
        assert "docroot" not in config_dict

        # Should contain categories
        assert "categories" in config_dict
        assert "test" in config_dict["categories"]

    async def test_config_save_format(self, tmp_path, monkeypatch):
        """Test that saving config uses correct format."""
        from mcp_server_guide.models.category import Category

        manager = ProjectConfigManager()

        # Set the config path to use tmp_path with YAML extension
        config_file_path = tmp_path / "config.yaml"
        manager.set_config_filename(config_file_path)

        config = ProjectConfig(
            categories={"guide": Category(dir="guide/", patterns=["*.md"], description="Guide files")}
        )
        await manager.save_config("new-project", config)

        # Read saved file from global config location (now YAML format)
        saved_data = yaml.safe_load(config_file_path.read_text())

        # Should not have current_project
        assert "current_project" not in saved_data

        # Should have projects structure
        assert "projects" in saved_data
        assert "new-project" in saved_data["projects"]

        # Should use correct field names
        project_data = saved_data["projects"]["new-project"]
        # docroot should NOT be in project_data (it's at global level in ConfigFile)
        assert "docroot" not in project_data
        assert "categories" in project_data
        assert "guide" in project_data["categories"]
