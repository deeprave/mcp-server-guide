"""Test configuration format updates (Issue 012 Phase 3)."""

import json

from mcp_server_guide.project_config import ProjectConfigManager, ProjectConfig


class TestConfigFormatUpdates:
    """Test that config format no longer includes current_project field."""

    def test_project_config_dataclass_no_current_project(self):
        """Test that ProjectConfig dataclass doesn't have current_project field."""
        config = ProjectConfig(project="test-project")

        # Should not have current_project field
        assert not hasattr(config, "current_project")

        # Should have expected fields
        assert hasattr(config, "project")
        assert hasattr(config, "contextdir")  # New field name
        assert not hasattr(config, "projdir")  # Old field name should be gone

    def test_config_serialization_excludes_current_project(self):
        """Test that config serialization doesn't include current_project."""
        config = ProjectConfig(project="test-project", language="python", contextdir="context/")

        config_dict = config.to_dict()

        # Should not contain current_project
        assert "current_project" not in config_dict

        # Should contain expected fields
        assert config_dict["project"] == "test-project"
        assert config_dict["language"] == "python"
        assert config_dict["contextdir"] == "context/"

    def test_config_migration_from_old_format(self, tmp_path):
        """Test migration from old config format with current_project."""
        config_file = tmp_path / ".mcp-server-guide.config.json"

        # Create old format config
        old_config = {
            "current_project": "old-project",
            "projects": {
                "old-project": {
                    "projdir": "old/project/",  # Old field name
                    "language": "python",
                }
            },
        }
        config_file.write_text(json.dumps(old_config, indent=2))

        # Load with new manager
        manager = ProjectConfigManager()
        loaded_config = manager.load_config(tmp_path, "old-project")

        # Should migrate projdir to contextdir
        assert loaded_config.contextdir == "old/project/"
        assert not hasattr(loaded_config, "projdir")

        # Should preserve other fields
        assert loaded_config.language == "python"
        assert loaded_config.project == "old-project"

    def test_config_save_uses_new_format(self, tmp_path):
        """Test that saving config uses new format without current_project."""
        manager = ProjectConfigManager()

        config = ProjectConfig(project="new-project", language="rust", contextdir="new/context/")

        manager.save_config(tmp_path, config)

        # Check saved file format
        config_file = tmp_path / ".mcp-server-guide.config.json"
        saved_data = json.loads(config_file.read_text())

        # Should not have current_project at root level
        assert "current_project" not in saved_data

        # Should have projects structure
        assert "projects" in saved_data
        assert "new-project" in saved_data["projects"]

        # Should use new field names
        project_data = saved_data["projects"]["new-project"]
        assert project_data["contextdir"] == "new/context/"
        assert "projdir" not in project_data

    def test_backward_compatibility_with_existing_configs(self, tmp_path):
        """Test that existing configs are preserved during migration."""
        config_file = tmp_path / ".mcp-server-guide.config.json"

        # Create config with mixed old and new projects
        mixed_config = {
            "current_project": "project-a",  # Should be removed
            "projects": {
                "project-a": {
                    "projdir": "old/style/",  # Should be migrated
                    "language": "python",
                },
                "project-b": {
                    "contextdir": "new/style/",  # Should be preserved
                    "language": "rust",
                },
            },
        }
        config_file.write_text(json.dumps(mixed_config, indent=2))

        # Load and save to trigger migration
        manager = ProjectConfigManager()
        config_a = manager.load_config(tmp_path, "project-a")
        config_b = manager.load_config(tmp_path, "project-b")

        # Save both configs
        manager.save_config(tmp_path, config_a)
        manager.save_config(tmp_path, config_b)

        # Check final format
        final_data = json.loads(config_file.read_text())

        # Should not have current_project
        assert "current_project" not in final_data

        # Both projects should use new format
        assert final_data["projects"]["project-a"]["contextdir"] == "old/style/"
        assert final_data["projects"]["project-b"]["contextdir"] == "new/style/"
        assert "projdir" not in final_data["projects"]["project-a"]
        assert "projdir" not in final_data["projects"]["project-b"]
