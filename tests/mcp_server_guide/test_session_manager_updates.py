"""Test SessionManager config file update behavior (Issue 012 Phase 2)."""

import os
import yaml

from mcp_server_guide.session_manager import SessionManager


class TestSessionManagerUpdates:
    """Test that SessionManager only updates config files, never overwrites them."""

    async def test_session_manager_preserves_existing_config_data(self, tmp_path, chdir):
        """Test that existing config data is preserved when updating."""
        config_file = tmp_path / "config.yaml"

        # Create existing config with proper category structure
        existing_config = {
            "projects": {
                "project-a": {
                    "docroot": "/custom/root",
                    "categories": {
                        "guide": {"dir": "custom/guides/", "patterns": ["*.md"]},
                        "context": {"dir": "custom/context/", "patterns": ["*.txt"]},
                    },
                },
                "project-b": {
                    "categories": {
                        "guide": {"dir": "other/guides/", "patterns": ["*.md"]},
                    }
                },
            }
        }
        config_file.write_text(yaml.dump(existing_config, indent=2))

        # Create project-a directory and chdir to it so PWD detection works
        project_dir = tmp_path / "project-a"
        project_dir.mkdir()

        original_cwd = os.getcwd()
        try:
            chdir(project_dir)

            # Create session manager and make changes
            session = SessionManager()
            session._set_config_filename(config_file)

            # Add a new category to the current project
            from mcp_server_guide.project_config import Category

            # Get existing categories or create empty dict
            if "categories" not in session.session_state.project_config:
                session.session_state.project_config["categories"] = {}
            # Add new category
            session.session_state.project_config["categories"]["language"] = Category(dir="lang/", patterns=["*.ts"])

            # Save session (will auto-detect project name from PWD)
            await session.save_session()

            # Verify existing data is preserved and new data is added
            updated_config = yaml.safe_load(config_file.read_text())

            # Original project-b should be untouched
            assert "project-b" in updated_config["projects"]
            assert updated_config["projects"]["project-b"]["categories"]["guide"]["dir"] == "other/guides/"

            # project-a should have new category but preserved other fields
            assert updated_config["projects"]["project-a"]["docroot"] == "/custom/root"
            assert "guide" in updated_config["projects"]["project-a"]["categories"]
            assert "context" in updated_config["projects"]["project-a"]["categories"]
            assert "language" in updated_config["projects"]["project-a"]["categories"]
            assert updated_config["projects"]["project-a"]["categories"]["language"]["dir"] == "lang/"

        finally:
            chdir(original_cwd)

    async def test_session_manager_uses_current_project_manager(self, tmp_path, chdir):
        """Test that SessionManager uses CurrentProjectManager instead of storing current_project in config."""
        config_file = tmp_path / "config.yaml"

        # Create existing config WITHOUT current_project field
        existing_config = {"projects": {"existing-project": {"language": "python"}}}
        config_file.write_text(yaml.dump(existing_config, indent=2))

        # Create a directory with the expected project name
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        original_cwd = os.getcwd()
        try:
            chdir(project_dir)  # Change to the project directory

            session = SessionManager()
            session._set_config_filename(config_file)

            # Should read the current project from PWD (directory name)
            current_project = session.get_project_name()
            assert current_project == "test-project"

            # Save session
            await session.save_session()

            # Config file should NOT contain current_project field
            updated_config = yaml.safe_load(config_file.read_text())
            assert "current_project" not in updated_config

            # Should only contain projects data
            assert "projects" in updated_config
            assert "existing-project" in updated_config["projects"]

        finally:
            chdir(original_cwd)

    async def test_session_manager_handles_missing_config_file(self, tmp_path, chdir):
        """Test that SessionManager creates new config file when none exists."""
        config_file = tmp_path / "config.yaml"

        # Create new-project directory for PWD detection
        project_dir = tmp_path / "new-project"
        project_dir.mkdir()

        original_cwd = os.getcwd()
        try:
            chdir(project_dir)

            session = SessionManager()
            session._set_config_filename(config_file)

            # Add a category to the project
            from mcp_server_guide.project_config import Category

            session.session_state.set_project_config(
                "categories", {"guide": Category(dir="guides/", patterns=["*.md"])}
            )

            # Save to non-existent file (will auto-detect project name from PWD)
            await session.save_session()

            # Should create new file with proper structure
            assert config_file.exists()
            config_data = yaml.safe_load(config_file.read_text())

            # Should NOT have current_project field
            assert "current_project" not in config_data

            # Should have projects data
            assert "projects" in config_data
            assert "new-project" in config_data["projects"]
            assert "categories" in config_data["projects"]["new-project"]
            assert "guide" in config_data["projects"]["new-project"]["categories"]

        finally:
            chdir(original_cwd)

    async def test_session_manager_handles_corrupted_config_file(self, tmp_path, chdir):
        """Test graceful handling of corrupted config files."""
        config_file = tmp_path / "config.yaml"

        # Create corrupted YAML file
        config_file.write_text("{ invalid yaml")

        # Create corrupted-project directory for PWD detection
        project_dir = tmp_path / "corrupted-project"
        project_dir.mkdir()

        original_cwd = os.getcwd()
        try:
            chdir(project_dir)

            session = SessionManager()
            session._set_config_filename(config_file)

            # Should handle a corrupted file gracefully
            # Either backup and recreate, or merge with defaults
            session.session_state.set_project_config("language", "python")
            # Save session (will auto-detect project name from PWD)
            await session.save_session()

            # File should now be valid YAML
            config_data = yaml.safe_load(config_file.read_text())
            assert "projects" in config_data

        finally:
            chdir(original_cwd)

    async def test_single_config_manager_responsibility(self, tmp_path, chdir):
        """Test that only one class manages config file writes."""
        # This test ensures we have a single point of responsibility
        # for config file management to prevent overwrites
        config_file = tmp_path / "config.yaml"

        # Create config with existing data for multiple projects
        existing_config = {
            "projects": {
                "project-1": {
                    "categories": {
                        "guide": {"dir": "guides/", "patterns": ["*.md"]},
                    }
                },
                "project-2": {
                    "categories": {
                        "guide": {"dir": "docs/", "patterns": ["*.rst"]},
                    }
                },
            }
        }
        config_file.write_text(yaml.dump(existing_config, indent=2))

        # Create project-1 directory for PWD detection
        project_dir = tmp_path / "project-1"
        project_dir.mkdir()

        original_cwd = os.getcwd()
        try:
            chdir(project_dir)

            # Multiple operations should all go through the same manager
            session = SessionManager()
            session._set_config_filename(config_file)

            # Operation 1: Set docroot for current project
            session.session_state.set_project_config("docroot", "/custom/root")

            # Operation 2: Add new category
            from mcp_server_guide.project_config import Category

            session.session_state.set_project_config(
                "categories", {"context": Category(dir="context/", patterns=["*.txt"])}
            )

            # Save all changes
            await session.save_session()

            # Verify all data is preserved and updated
            final_config = yaml.safe_load(config_file.read_text())

            # Both projects should still exist
            assert len(final_config["projects"]) == 2

            # Original project-2 data should be untouched
            assert final_config["projects"]["project-2"]["categories"]["guide"]["dir"] == "docs/"

            # project-1 should have updates applied
            assert final_config["projects"]["project-1"]["docroot"] == "/custom/root"
            # Original guide category should still exist
            assert "guide" in final_config["projects"]["project-1"]["categories"]
            # New context category should be added
            assert "context" in final_config["projects"]["project-1"]["categories"]

        finally:
            chdir(original_cwd)
