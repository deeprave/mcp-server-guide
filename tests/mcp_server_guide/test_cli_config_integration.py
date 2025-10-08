"""Tests for CLI config integration."""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from mcp_server_guide.main import resolve_config_file_path


class TestCLIConfigIntegration:
    """Test CLI config integration with path resolution."""

    def test_cli_config_relative_path(self):
        """Test that CLI config resolution works with relative paths."""
        config_obj = Mock()
        kwargs = {"config": "server.yaml"}

        result = resolve_config_file_path(kwargs, config_obj)
        expected_path = Path("server.yaml").resolve()
        assert Path(result).resolve() == expected_path

    def test_cli_config_absolute_path(self):
        """Test that absolute config paths work correctly."""
        config_obj = Mock()
        kwargs = {"config": "/absolute/config.yaml"}

        result = resolve_config_file_path(kwargs, config_obj)
        expected = "/absolute/config.yaml"
        assert result == expected

    def test_cli_config_global_flag(self):
        """Test that global config flag works."""
        config_obj = Mock()
        config_obj.get_global_config_path.return_value = "/etc/mcp/config.yaml"
        kwargs = {"global_config": True}

        result = resolve_config_file_path(kwargs, config_obj)
        # Path resolution may add /private prefix on macOS
        assert result.endswith("/etc/mcp/config.yaml")

    def test_cli_config_env_var(self):
        """Test that environment variable config works."""
        config_obj = Mock()
        kwargs = {}

        with patch.dict("os.environ", {"MG_CONFIG": "env-config.yaml"}):
            result = resolve_config_file_path(kwargs, config_obj)
            expected_path = Path("env-config.yaml").resolve()
            assert Path(result).resolve() == expected_path

    def test_cli_config_default(self):
        """Test that default config filename works."""
        config_obj = Mock()
        kwargs = {}

        with patch("mcp_server_guide.main.config_filename") as mock_filename:
            mock_filename.return_value = ".mcp-server-guide.yaml"

            result = resolve_config_file_path(kwargs, config_obj)
            expected_path = Path(".mcp-server-guide.yaml").resolve()
            assert Path(result).resolve() == expected_path

    def test_cli_config_directory_handling(self):
        """Test that directory config paths get proper filename appended."""
        config_obj = Mock()
        kwargs = {"config": "config-dir"}

        with patch("mcp_server_guide.main.config_filename") as mock_filename:
            mock_filename.return_value = ".mcp-server-guide.yaml"

            # Mock the resolved path to be a directory
            with patch("pathlib.Path.is_dir") as mock_is_dir:
                mock_is_dir.return_value = True

                result = resolve_config_file_path(kwargs, config_obj)
                expected_path = Path("config-dir/mcp-server-guide.yaml").resolve()
                assert Path(result).resolve() == expected_path

    def test_cli_config_uri_prefix_support(self):
        """Test that URI prefixes work in CLI config resolution."""
        config_obj = Mock()
        kwargs = {"config": "file://config.yaml"}

        result = resolve_config_file_path(kwargs, config_obj)
        expected_path = Path("config.yaml").resolve()
        assert result == str(expected_path)

    def test_cli_config_unsupported_uri_prefix(self):
        """Test that unsupported or malformed URI prefixes are handled correctly."""
        config_obj = Mock()
        unsupported_prefixes = [
            "ftp://config.yaml",
            "invalid://config.yaml",
        ]

        for config_value in unsupported_prefixes:
            kwargs = {"config": config_value}
            with pytest.raises(ValueError, match="Unsupported URL scheme"):
                resolve_config_file_path(kwargs, config_obj)

        # Test malformed URLs (no proper scheme)
        malformed_urls = [
            "://config.yaml",
            "http:/config.yaml",  # malformed
        ]

        for config_value in malformed_urls:
            kwargs = {"config": config_value}
            result = resolve_config_file_path(kwargs, config_obj)
            # These fall back to treating as regular path
            expected_path = Path(config_value).resolve()
            # Normalize paths to handle /private prefix on macOS
            assert Path(result).resolve() == expected_path


class TestCLIConfigEdgeCases:
    """Test edge cases in CLI config integration."""

    def test_cli_config_no_global_flag_overrides(self):
        """Test that --no-global-config flag works correctly."""
        config_obj = Mock()
        kwargs = {"global_config": False}  # Using new combined flag

        with patch("mcp_server_guide.main.config_filename") as mock_filename:
            mock_filename.return_value = ".mcp-server-guide.yaml"

            result = resolve_config_file_path(kwargs, config_obj)
            expected_path = Path(".mcp-server-guide.yaml").resolve()
            assert Path(result).resolve() == expected_path

    def test_cli_config_custom_overrides_global(self):
        """Test that --config overrides --global-config (CLI args have precedence)."""
        config_obj = Mock()
        config_obj.get_global_config_path.return_value = "/etc/mcp/config.yaml"
        kwargs = {"config": "custom.yaml", "global_config": True}

        result = resolve_config_file_path(kwargs, config_obj)
        # --config should win over --global-config
        assert result.endswith("custom.yaml")

    def test_cli_config_overrides_env_var(self):
        """Test that --config takes precedence over MG_CONFIG when both are set."""
        config_obj = Mock()
        kwargs = {"config": "cli-config.yaml"}

        with patch.dict("os.environ", {"MG_CONFIG": "env-config.yaml"}):
            result = resolve_config_file_path(kwargs, config_obj)
            # --config should win over MG_CONFIG
            assert result.endswith("cli-config.yaml")

    def test_cli_config_env_global_flag(self):
        """Test that MG_CONFIG_GLOBAL environment variable works."""
        config_obj = Mock()
        config_obj.get_global_config_path.return_value = "/etc/mcp/config.yaml"
        kwargs = {}

        with patch.dict("os.environ", {"MG_CONFIG_GLOBAL": "1"}):
            result = resolve_config_file_path(kwargs, config_obj)
            # Path resolution may add /private prefix on macOS
            assert result.endswith("/etc/mcp/config.yaml")
