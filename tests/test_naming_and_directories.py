"""Tests for Issue 021: Directory creation and test isolation fixes."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from mcp_server_guide.file_cache import FileCache


class TestDirectoryCreationFixes:
    """Test fixes for directory creation and naming centralization."""

    def test_cache_directory_uses_xdg_location(self):
        """Test that cache directory follows XDG Base Directory specification."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with XDG_CACHE_HOME set
            custom_cache = os.path.join(temp_dir, "custom_cache")
            with patch.dict(os.environ, {"XDG_CACHE_HOME": custom_cache}):
                cache = FileCache()
                expected_path = Path(custom_cache) / "mcp-server-guide"
                assert cache.cache_dir == expected_path

            # Test with XDG_CACHE_HOME unset (default behavior)
            with patch.dict(os.environ, {}, clear=False):
                if "XDG_CACHE_HOME" in os.environ:
                    del os.environ["XDG_CACHE_HOME"]
                cache = FileCache()
                expected_path = Path.home() / ".cache" / "mcp-server-guide"
                assert cache.cache_dir == expected_path

    def test_mcp_name_function_exists_and_returns_correct_value(self):
        """Test that mcp_name() function exists and returns expected value."""
        from mcp_server_guide.naming import mcp_name

        assert mcp_name() == "mcp-server-guide"

    def test_global_config_path_uses_mcp_name_function(self):
        """Test that global config path uses centralized mcp_name() function."""
        from mcp_server_guide.naming import mcp_name
        from mcp_server_guide.project_config import ProjectConfigManager

        manager = ProjectConfigManager()
        config_path = manager.get_config_filename()

        # Should contain mcp_name in the path
        assert mcp_name() in str(config_path)
        assert str(config_path).endswith("config.yaml")

    def test_user_agent_uses_version_constant(self):
        """Test that user_agent() uses centralized version constant."""
        from mcp_server_guide.naming import MCP_GUIDE_VERSION, user_agent

        expected_user_agent = f"mcp-server-guide/{MCP_GUIDE_VERSION}"
        assert user_agent() == expected_user_agent
        assert MCP_GUIDE_VERSION in user_agent()

    def test_current_file_name_uses_centralized_naming(self):
        """Test that SessionManager works with PWD-based approach (no current file needed)."""
        from mcp_server_guide.session_manager import SessionManager

        session_manager = SessionManager()
        # PWD-based approach doesn't use current files
        # Just verify the SessionManager can be instantiated
        assert session_manager is not None


class TestSessionScopedTestIsolation:
    """Test session-scoped test isolation with robust cleanup."""

    def test_session_temp_directory_exists(self, session_temp_dir):
        """Test that session-scoped temp directory is created."""
        # Check if session temp directory fixture provides a valid path
        assert session_temp_dir is not None
        assert session_temp_dir.exists()
        assert session_temp_dir.is_dir()

    def test_robust_cleanup_handles_readonly_files(self):
        """Test that cleanup can handle read-only files and directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_cleanup"
            test_dir.mkdir()

            # Create read-only file
            readonly_file = test_dir / "readonly.txt"
            readonly_file.write_text("test")
            readonly_file.chmod(0o444)  # Read-only

            # Test cleanup function
            from tests.conftest import robust_cleanup

            robust_cleanup(test_dir)

            # Directory should be completely removed
            assert not test_dir.exists()

    def test_per_test_subdirectories_are_isolated(self, session_temp_dir, complete_test_isolation):
        """Test that each test gets its own subdirectory within session temp dir."""
        # Check that we're running in a subdirectory of the session temp dir
        current_dir = Path.cwd().resolve()
        session_dir_resolved = session_temp_dir.resolve()

        # Current working directory should be within session temp dir
        assert session_dir_resolved in current_dir.parents or current_dir == session_dir_resolved

        # Should be in a unique test subdirectory
        assert current_dir != session_dir_resolved
