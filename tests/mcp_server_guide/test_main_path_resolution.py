"""Tests for main.py config file path resolution function."""

import os
from pathlib import Path
from unittest.mock import Mock, patch


from mcp_server_guide.main import resolve_config_file_path


class TestResolveConfigFilePath:
    """Test config file path resolution function."""

    @patch("mcp_server_guide.main.config_filename")
    @patch("os.getcwd")
    @patch("os.path.join")
    @patch("os.path.isabs")
    def test_resolve_config_file_path_default(self, mock_isabs, mock_join, mock_getcwd, mock_config_filename):
        """Test config file path resolution with defaults."""
        mock_config_filename.return_value = ".mcp_server_guide.toml"
        mock_isabs.return_value = False
        mock_getcwd.return_value = "/current/dir"
        mock_join.return_value = "/current/dir/.mcp_server_guide.toml"

        result = resolve_config_file_path({}, Mock())

        assert result == "/current/dir/.mcp_server_guide.toml"

    def test_resolve_config_file_path_custom_config(self):
        """Test config file path resolution with custom config."""
        kwargs = {"config": "/custom/path/config.toml"}

        result = resolve_config_file_path(kwargs, Mock())

        assert result == "/custom/path/config.toml"

    @patch.dict(os.environ, {"MG_CONFIG": "/env/config.toml"})
    def test_resolve_config_file_path_env_var(self):
        """Test config file path resolution with environment variable."""
        result = resolve_config_file_path({}, Mock())

        assert result == "/env/config.toml"

    def test_resolve_config_file_path_global_config(self):
        """Test config file path resolution with global config."""
        kwargs = {"global_config": True}
        mock_config = Mock()
        mock_config.get_global_config_path.return_value = "/global/config.toml"

        result = resolve_config_file_path(kwargs, mock_config)

        assert result == "/global/config.toml"

    @patch.dict(os.environ, {"MG_CONFIG_GLOBAL": "1"})
    def test_resolve_config_file_path_global_env(self):
        """Test config file path resolution with global environment variable."""
        mock_config = Mock()
        mock_config.get_global_config_path.return_value = "/global/config.toml"

        result = resolve_config_file_path({}, mock_config)

        assert result == "/global/config.toml"

    def test_resolve_config_file_path_no_global_override(self):
        """Test config file path resolution with global_config=False."""

        kwargs = {"global_config": False}
        mock_config = Mock()

        with patch("mcp_server_guide.main.config_filename") as mock_filename:
            mock_filename.return_value = ".mcp_server_guide.toml"

            result = resolve_config_file_path(kwargs, mock_config)

            # Should use PWD-based path, not global config
            # Verify it's an absolute path ending with the config filename
            assert result.endswith("/.mcp_server_guide.toml")
            assert Path(result).is_absolute()
            mock_config.get_global_config_path.assert_not_called()

    def test_resolve_config_file_path_relative_to_absolute(self):
        """Test config file path resolution converts relative to PWD-relative."""

        kwargs = {"config": "relative/config.toml"}

        result = resolve_config_file_path(kwargs, Mock())

        # Should convert relative path to absolute path
        assert result.endswith("/relative/config.toml")
        assert Path(result).is_absolute()

    def test_resolve_config_file_path_directory_to_file(self):
        """Test config file path resolution converts directory to file."""
        kwargs = {"config": "/some/directory"}

        with patch("mcp_server_guide.main.config_filename") as mock_config_filename:
            mock_config_filename.return_value = ".mcp_server_guide.toml"

            with patch("pathlib.Path.is_dir") as mock_is_dir:
                mock_is_dir.return_value = True

                result = resolve_config_file_path(kwargs, Mock())

                assert result == "/some/directory/mcp_server_guide.toml"

    def test_resolve_config_file_path_custom_overrides_global(self):
        """Test --config takes precedence over --global-config."""
        kwargs = {"config": "/custom/config.toml", "global_config": True}
        mock_config = Mock()
        mock_config.get_global_config_path.return_value = "/global/config.toml"

        result = resolve_config_file_path(kwargs, mock_config)

        assert result == "/custom/config.toml"

    @patch.dict(os.environ, {"MG_CONFIG": "/env/config.toml"})
    def test_resolve_config_file_path_env_overrides_global(self):
        """Test that --global-config overrides MG_CONFIG environment variable."""
        kwargs = {"global_config": True}
        mock_config = Mock()
        mock_config.get_global_config_path.return_value = "/global/config.toml"

        result = resolve_config_file_path(kwargs, mock_config)

        assert result == "/global/config.toml"
        mock_config.get_global_config_path.assert_called_once()
