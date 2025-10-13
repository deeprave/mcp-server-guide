"""Tests for configuration file isolation (prevent tests from affecting working files)."""

import tempfile
import yaml
from pathlib import Path

from mcp_server_guide.session_manager import SessionManager
from mcp_server_guide.tools.config_tools import set_project_config


class TestConfigIsolation:
    """Test that configuration operations don't affect working files."""

    def setup_method(self):
        """Reset SessionManager singleton before each test."""
        SessionManager.clear()

    async def test_config_filename_mocking_works(self, mock_config_filename, monkeypatch):
        """Test that ProjectConfigManager.get_config_filename() can be mocked for test isolation."""
        # Mock config filename to use custom name
        custom_filename = "test-config.yaml"

        def mock_getter(self):
            return custom_filename

        from mcp_server_guide.project_config import ProjectConfigManager

        monkeypatch.setattr(ProjectConfigManager, "get_config_filename", mock_getter)

        # Create a ProjectConfigManager instance and verify the mock works
        manager = ProjectConfigManager()
        assert manager.get_config_filename() == custom_filename

        # Create the custom config file to verify file operations would use it
        config_file = Path(custom_filename)
        config_file.write_text(yaml.dump({"projects": {}}, default_flow_style=False))

        # Verify the file exists (showing that tests can use custom filenames)
        assert config_file.exists()

        # Clean up
        config_file.unlink()

    async def test_tests_dont_affect_working_directory(self, isolated_config_file):
        """Test that running tests doesn't create files in working directory."""
        # Record initial state (excluding the isolated_config_file which is expected)
        working_dir = Path.cwd()
        set(working_dir.glob("*config*.yaml"))

        # Run some config operations in a test
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                session = SessionManager()
                session._set_config_filename(isolated_config_file)  # Use isolated config
                session.set_project_name("isolated-test")
                await set_project_config(
                    "categories", {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test"}}
                )

                # This should create files using isolated config, not in working_dir
                await session.save_session()

                # Isolated config file should exist
                assert isolated_config_file.exists()

            finally:
                os.chdir(original_cwd)

        # Working directory should only have the isolated_config_file, no other config files
        final_files = set(working_dir.glob("*config*.yaml"))
        # The isolated_config_file is expected to be in the working dir
        expected_files = {isolated_config_file} if isolated_config_file.exists() else set()
        assert final_files == expected_files
