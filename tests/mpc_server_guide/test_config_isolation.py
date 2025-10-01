"""Tests for configuration file isolation (prevent tests from affecting working files)."""

import tempfile
from pathlib import Path

from mcp_server_guide.session_tools import SessionManager
from mcp_server_guide.tools.config_tools import set_project_config
from mcp_server_guide.tools.session_management import save_session, load_session


class TestConfigIsolation:
    """Test that configuration operations don't affect working files."""

    def setup_method(self):
        """Reset SessionManager singleton before each test."""
        SessionManager._instance = None

    async def test_save_session_uses_custom_filename(self):
        """Test that save_session can use a custom config filename."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                # Initialize session with test data
                session = SessionManager()
                session.set_current_project("test-project")

                # Save with custom filename
                custom_filename = "test-config.json"

                # Set config with custom filename to avoid auto-save to default file
                await set_project_config("language", "python", config_filename_param=custom_filename)

                # Also explicitly save with custom filename
                result = await save_session(config_filename=custom_filename)

                assert result["success"] is True

                # Custom file should exist
                custom_file = Path(temp_dir) / custom_filename
                assert custom_file.exists()

                # Default file should NOT exist
                default_file = Path(temp_dir) / ".mcp-server-guide.config.json"
                assert not default_file.exists()

            finally:
                os.chdir(original_cwd)

    async def test_load_session_uses_custom_filename(self):
        """Test that load_session can use a custom config filename."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                # Create custom config file
                custom_filename = "test-config.json"
                config_file = Path(temp_dir) / custom_filename
                config_data = {
                    "current_project": "loaded-project",
                    "projects": {"loaded-project": {"language": "rust"}},
                }

                import json

                config_file.write_text(json.dumps(config_data))

                # Create .current file for new behavior
                current_file = Path(temp_dir) / ".mcp-server-guide.current"
                current_file.write_text("loaded-project")

                # Load with custom filename
                result = load_session(config_filename=custom_filename)

                assert result["success"] is True

                # Verify loaded data
                session = SessionManager()
                assert session.get_current_project() == "loaded-project"
                project_config = session.session_state.get_project_config("loaded-project")
                assert project_config["language"] == "rust"

            finally:
                os.chdir(original_cwd)

    async def test_server_startup_uses_custom_filename(self):
        """Test that server startup can use custom config filename."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                # Create custom config file
                custom_filename = "server-config.json"
                config_file = Path(temp_dir) / custom_filename
                config_data = {
                    "current_project": "server-project",
                    "projects": {"server-project": {"language": "typescript"}},
                }

                import json

                config_file.write_text(json.dumps(config_data))

                # Server startup should be able to use custom filename
                from mcp_server_guide.server import create_server_with_config

                config = {"docroot": ".", "config_filename": custom_filename}
                create_server_with_config(config)

                # Should have loaded the custom config
                session = SessionManager()
                assert session.current_project == "server-project"

            finally:
                os.chdir(original_cwd)

    async def test_tests_dont_affect_working_directory(self):
        """Test that running tests doesn't create files in working directory."""
        # Record initial state
        working_dir = Path.cwd()
        initial_files = set(working_dir.glob("*config*.json"))

        # Run some config operations in a test
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                session = SessionManager()
                session.set_current_project("isolated-test")
                await set_project_config("language", "java")

                # This should create files in temp_dir, not working_dir
                await save_session()

                temp_files = list(Path(temp_dir).glob("*config*.json"))
                assert len(temp_files) > 0  # Files created in temp dir

            finally:
                os.chdir(original_cwd)

        # Working directory should be unchanged
        final_files = set(working_dir.glob("*config*.json"))
        assert final_files == initial_files  # No new files in working dir

    async def test_auto_save_respects_custom_filename(self):
        """Test that auto-save functionality respects custom filename."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                # Set custom filename for auto-save
                custom_filename = "auto-save-config.json"

                # Initialize session
                session = SessionManager()
                session.set_current_project("auto-save-test")

                # This should trigger auto-save with custom filename
                await set_project_config("language", "go", config_filename_param=custom_filename)

                # Custom file should exist
                custom_file = Path(temp_dir) / custom_filename
                assert custom_file.exists()

                # Default file should NOT exist
                default_file = Path(temp_dir) / ".mcp-server-guide.config.json"
                assert not default_file.exists()

            finally:
                os.chdir(original_cwd)
