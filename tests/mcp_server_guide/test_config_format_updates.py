"""Test config format and structure."""

import json
from mcp_server_guide.project_config import ProjectConfig, ProjectConfigManager


class TestConfigFormatUpdates:
    """Test config format updates and structure."""

    async def test_project_config_dataclass_structure(self):
        """Test that ProjectConfig has expected structure."""
        config = ProjectConfig(project="test-project")

        # Should not have current_project field
        assert not hasattr(config, "current_project")

        # Should have expected fields
        assert hasattr(config, "project")
        assert hasattr(config, "docroot")
        assert hasattr(config, "categories")
        assert hasattr(config, "categories")

    async def test_config_serialization_structure(self):
        """Test that config serialization has correct structure."""
        config = ProjectConfig(project="test-project", docroot="/test/path")

        config_dict = config.to_dict()

        # Should not contain current_project
        assert "current_project" not in config_dict

        # Should contain expected fields
        assert config_dict["project"] == "test-project"
        assert config_dict["docroot"] == "/test/path"

    async def test_config_save_format(self, tmp_path):
        """Test that saving config uses correct format."""
        manager = ProjectConfigManager()

        config = ProjectConfig(project="new-project", docroot="/new/path")
        manager.save_config(tmp_path, config)

        # Read saved file
        config_file = tmp_path / ".mcp-server-guide.config.json"
        saved_data = json.loads(config_file.read_text())

        # Should not have current_project
        assert "current_project" not in saved_data

        # Should have projects structure
        assert "projects" in saved_data
        assert "new-project" in saved_data["projects"]

        # Should use correct field names
        project_data = saved_data["projects"]["new-project"]
        assert project_data["docroot"] == "/new/path"
        assert project_data["docroot"] == "/new/path"
