"""Test SessionManager config file update behavior (Issue 012 Phase 2)."""

import json
import os

from mcp_server_guide.session_tools import SessionManager


class TestSessionManagerUpdates:
    """Test that SessionManager only updates config files, never overwrites them."""

    async def test_session_manager_preserves_existing_config_data(self, tmp_path, chdir):
        """Test that existing config data is preserved when updating."""
        config_file = tmp_path / ".mcp-server-guide.config.json"

        # Create existing config with data
        existing_config = {
            "projects": {
                "project-a": {"guidesdir": "custom/guides/", "language": "python", "docroot": "/custom/root"},
                "project-b": {"guidesdir": "other/guides/", "language": "rust"},
            }
        }
        config_file.write_text(json.dumps(existing_config, indent=2))

        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)

            # Create session manager and make changes
            session = SessionManager()
            session.session_state.set_project_config("project-a", "language", "typescript")

            # Save session - should UPDATE not OVERWRITE
            await session.save_to_file(str(config_file))

            # Verify existing data is preserved and new data is added
            updated_config = json.loads(config_file.read_text())

            # Original project-b should be untouched
            assert "project-b" in updated_config["projects"]
            assert updated_config["projects"]["project-b"]["language"] == "rust"
            assert updated_config["projects"]["project-b"]["guidesdir"] == "other/guides/"

            # project-a should have updated language but preserved other fields
            assert updated_config["projects"]["project-a"]["language"] == "typescript"
            assert updated_config["projects"]["project-a"]["guidesdir"] == "custom/guides/"
            assert updated_config["projects"]["project-a"]["docroot"] == "/custom/root"

        finally:
            chdir(original_cwd)

    async def test_session_manager_uses_current_project_manager(self, tmp_path, chdir):
        """Test that SessionManager uses CurrentProjectManager instead of storing current_project in config."""
        config_file = tmp_path / ".mcp-server-guide.config.json"
        current_file = tmp_path / ".mcp-server-guide.current"

        # Create existing config WITHOUT current_project field
        existing_config = {"projects": {"existing-project": {"language": "python"}}}
        config_file.write_text(json.dumps(existing_config, indent=2))

        # Set current project via CurrentProjectManager
        current_file.write_text("test-project")

        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)

            session = SessionManager()

            # Should read current project from .current file, not config
            assert session.get_current_project() == "test-project"

            # Save session
            await session.save_to_file(str(config_file))

            # Config file should NOT contain current_project field
            updated_config = json.loads(config_file.read_text())
            assert "current_project" not in updated_config

            # Should only contain projects data
            assert "projects" in updated_config
            assert "existing-project" in updated_config["projects"]

        finally:
            chdir(original_cwd)

    async def test_session_manager_handles_missing_config_file(self, tmp_path, chdir):
        """Test that SessionManager creates new config file when none exists."""
        config_file = tmp_path / ".mcp-server-guide.config.json"

        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)

            session = SessionManager()
            session.session_state.set_project_config("new-project", "language", "go")

            # Save to non-existent file
            await session.save_to_file(str(config_file))

            # Should create new file with proper structure
            assert config_file.exists()
            config_data = json.loads(config_file.read_text())

            # Should NOT have current_project field
            assert "current_project" not in config_data

            # Should have projects data
            assert "projects" in config_data
            assert config_data["projects"]["new-project"]["language"] == "go"

        finally:
            chdir(original_cwd)

    async def test_session_manager_handles_corrupted_config_file(self, tmp_path, chdir):
        """Test graceful handling of corrupted config files."""
        config_file = tmp_path / ".mcp-server-guide.config.json"

        # Create corrupted JSON file
        config_file.write_text("{ invalid json")

        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)

            session = SessionManager()

            # Should handle corrupted file gracefully
            # Either backup and recreate, or merge with defaults
            session.session_state.set_project_config("test-project", "language", "python")
            await session.save_to_file(str(config_file))

            # File should now be valid JSON
            config_data = json.loads(config_file.read_text())
            assert "projects" in config_data

        finally:
            chdir(original_cwd)

    async def test_single_config_manager_responsibility(self, tmp_path, chdir):
        """Test that only one class manages config file writes."""
        # This test ensures we have a single point of responsibility
        # for config file management to prevent overwrites

        config_file = tmp_path / ".mcp-server-guide.config.json"

        # Create config with existing data
        existing_config = {"projects": {"project-1": {"language": "python"}, "project-2": {"language": "rust"}}}
        config_file.write_text(json.dumps(existing_config, indent=2))

        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)

            # Multiple operations should all go through the same manager
            session = SessionManager()

            # Operation 1: Update existing project
            session.session_state.set_project_config("project-1", "guidesdir", "guides/")

            # Operation 2: Add new project
            session.session_state.set_project_config("project-3", "language", "go")

            # Save all changes
            await session.save_to_file(str(config_file))

            # Verify all data is preserved and updated
            final_config = json.loads(config_file.read_text())

            # All projects should exist
            assert len(final_config["projects"]) == 3

            # Original data preserved
            assert final_config["projects"]["project-2"]["language"] == "rust"

            # Updates applied
            assert final_config["projects"]["project-1"]["language"] == "python"
            assert final_config["projects"]["project-1"]["guidesdir"] == "guides/"

            # New project added
            assert final_config["projects"]["project-3"]["language"] == "go"

        finally:
            chdir(original_cwd)
