"""Tests for automatic configuration persistence (Issue 009)."""

import tempfile
from pathlib import Path

from mcp_server_guide.server import create_server_with_config
from mcp_server_guide.session_tools import SessionManager
from mcp_server_guide.tools.config_tools import set_project_config


class TestAutoConfigPersistence:
    """Test automatic configuration persistence functionality."""

    def setup_method(self):
        """Reset SessionManager singleton before each test."""
        # Reset the singleton instance
        SessionManager._instance = None

    def test_startup_auto_loads_saved_configuration(self):
        """Test that MCP server automatically loads saved configuration on startup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a saved configuration file
            test_config_filename = "test-startup-config.json"
            config_file = Path(temp_dir) / test_config_filename
            config_data = {
                "projects": {
                    "test-project": {"language": "python", "guidesdir": "custom/guides/", "langdir": "custom/lang/"}
                }
                # Note: No current_project field - this is now handled by .current file
            }

            import json

            config_file.write_text(json.dumps(config_data))

            # Create .current file to set current project
            current_file = Path(temp_dir) / ".mcp-server-guide.current"
            current_file.write_text("test-project")

            # Change to temp directory and create server
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                # Create server - should auto-load configuration
                config = {"docroot": ".", "mode": "stdio", "config_filename": test_config_filename}
                create_server_with_config(config)

                # Verify configuration was loaded
                session = SessionManager()
                assert session.get_current_project() == "test-project"

                project_config = session.session_state.get_project_config("test-project")
                assert project_config["language"] == "python"
                assert project_config["guidesdir"] == "custom/guides/"
                assert project_config["langdir"] == "custom/lang/"

            finally:
                os.chdir(original_cwd)

    def test_config_changes_auto_save_except_project(self):
        """Test that configuration changes automatically save (except project changes)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                test_config_filename = "test-auto-save-config.json"

                # Initialize session
                session = SessionManager()
                session.set_current_project("auto-save-test")

                # Change a configuration value (not project)
                result = set_project_config("language", "rust", config_filename=test_config_filename)
                assert result["success"] is True

                # Configuration should be automatically saved
                config_file = Path(temp_dir) / test_config_filename
                assert config_file.exists()

                import json

                saved_config = json.loads(config_file.read_text())
                assert saved_config["projects"]["auto-save-test"]["language"] == "rust"

            finally:
                os.chdir(original_cwd)

    def test_project_changes_do_not_auto_save(self):
        """Test that project changes do not trigger auto-save."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                test_config_filename = "test-no-auto-save-config.json"

                # Initialize session
                session = SessionManager()
                session.set_current_project("initial-project")

                # Manually save initial state
                from mcp_server_guide.tools.session_management import save_session

                save_session(test_config_filename)

                config_file = Path(temp_dir) / test_config_filename
                initial_mtime = config_file.stat().st_mtime

                # Wait a bit to ensure different mtime
                import time

                time.sleep(0.1)

                # Change project (should not auto-save)
                from mcp_server_guide.tools.project_tools import switch_project

                switch_project("new-project")

                # Config file should not have been modified
                current_mtime = config_file.stat().st_mtime
                assert current_mtime == initial_mtime

            finally:
                os.chdir(original_cwd)

    def test_graceful_handling_when_no_saved_session_exists(self):
        """Test graceful handling when no saved session exists on startup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                test_config_filename = "test-nonexistent-config.json"

                # Ensure no config file exists
                config_file = Path(temp_dir) / test_config_filename
                assert not config_file.exists()

                # Create server - should handle missing config gracefully
                config = {"docroot": ".", "mode": "stdio", "config_filename": test_config_filename}
                create_server_with_config(config)

                # Should use default configuration
                session = SessionManager()
                # Should fallback to directory name when no config exists
                expected_project = Path(temp_dir).name
                assert session.current_project == expected_project

            finally:
                os.chdir(original_cwd)

    def test_multiple_config_changes_auto_save(self):
        """Test that multiple configuration changes all auto-save."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                test_config_filename = "test-multi-config.json"

                # Initialize session
                session = SessionManager()
                session.set_current_project("multi-config-test")

                # Make multiple configuration changes
                set_project_config("language", "typescript", config_filename=test_config_filename)
                set_project_config("guidesdir", "docs/guides/", config_filename=test_config_filename)
                set_project_config("langdir", "docs/languages/", config_filename=test_config_filename)

                # All changes should be saved
                config_file = Path(temp_dir) / test_config_filename
                assert config_file.exists()

                import json

                saved_config = json.loads(config_file.read_text())
                project_config = saved_config["projects"]["multi-config-test"]

                assert project_config["language"] == "typescript"
                assert project_config["guidesdir"] == "docs/guides/"
                assert project_config["langdir"] == "docs/languages/"

            finally:
                os.chdir(original_cwd)
