"""Tests for CLI config integration with client-relative paths."""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from mcp_server_guide.main import resolve_config_file_path


class TestCLIConfigIntegration:
    """Test CLI config integration with client-relative path resolution."""

    def test_cli_config_uses_client_relative_resolution(self):
        """Test that CLI config resolution uses client-relative paths."""
        config_obj = Mock()
        kwargs = {"config": "server.yaml"}

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_file_path(kwargs, config_obj)
            expected = "/client/root/server.yaml"
            assert result == expected

    def test_cli_config_absolute_path_bypasses_client_relative(self):
        """Test that absolute config paths bypass client-relative resolution."""
        config_obj = Mock()
        kwargs = {"config": "/absolute/config.yaml"}

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_file_path(kwargs, config_obj)
            expected = "/absolute/config.yaml"
            assert result == expected

    def test_cli_config_global_flag_bypasses_client_relative(self):
        """Test that global config flag bypasses client-relative resolution."""
        config_obj = Mock()
        config_obj.get_global_config_path.return_value = "/etc/mcp/config.yaml"
        kwargs = {"global_config": True}

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_file_path(kwargs, config_obj)
            # Path resolution may add /private prefix on macOS
            assert result.endswith("/etc/mcp/config.yaml")

    def test_cli_config_env_var_uses_client_relative(self):
        """Test that environment variable config uses client-relative resolution."""
        config_obj = Mock()
        kwargs = {}

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            with patch.dict("os.environ", {"MG_CONFIG": "env-config.yaml"}):
                result = resolve_config_file_path(kwargs, config_obj)
                expected = "/client/root/env-config.yaml"
                assert result == expected

    def test_cli_config_default_uses_client_relative(self):
        """Test that default config filename uses client-relative resolution."""
        config_obj = Mock()
        kwargs = {}

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            with patch("mcp_server_guide.main.config_filename") as mock_filename:
                mock_filename.return_value = ".mcp-server-guide.yaml"

                result = resolve_config_file_path(kwargs, config_obj)
                expected = "/client/root/.mcp-server-guide.yaml"
                assert result == expected

    def test_cli_config_directory_handling(self):
        """Test that directory config paths get proper filename appended."""
        config_obj = Mock()
        kwargs = {"config": "config-dir"}

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            with patch("mcp_server_guide.main.config_filename") as mock_filename:
                mock_filename.return_value = ".mcp-server-guide.yaml"

                # Mock the resolved path to be a directory
                with patch("pathlib.Path.is_dir") as mock_is_dir:
                    mock_is_dir.return_value = True

                    result = resolve_config_file_path(kwargs, config_obj)
                    expected = "/client/root/config-dir/mcp-server-guide.yaml"
                    assert result == expected

    def test_cli_config_no_client_root_fallback(self):
        """Test fallback when no client root is available."""
        config_obj = Mock()
        kwargs = {"config": "server.yaml"}

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = None

            result = resolve_config_file_path(kwargs, config_obj)
            # Should resolve relative to current working directory
            expected_path = Path("server.yaml").resolve()
            assert result == str(expected_path)

    def test_cli_config_uri_prefix_support(self):
        """Test that URI prefixes work in CLI config resolution."""
        config_obj = Mock()
        kwargs = {"config": "server://config.yaml"}

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

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

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            with patch("mcp_server_guide.main.config_filename") as mock_filename:
                mock_filename.return_value = ".mcp-server-guide.yaml"

                result = resolve_config_file_path(kwargs, config_obj)
                expected = "/client/root/.mcp-server-guide.yaml"
                assert result == expected

    def test_cli_config_custom_overrides_global(self):
        """Test that custom config path overrides global config."""
        config_obj = Mock()
        config_obj.get_global_config_path.return_value = "/etc/mcp/config.yaml"
        kwargs = {"config": "custom.yaml", "global_config": True}

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_file_path(kwargs, config_obj)
            expected = "/client/root/custom.yaml"
            assert result == expected

    def test_cli_config_env_global_flag(self):
        """Test that MG_CONFIG_GLOBAL environment variable works."""
        config_obj = Mock()
        config_obj.get_global_config_path.return_value = "/etc/mcp/config.yaml"
        kwargs = {}

        with patch.dict("os.environ", {"MG_CONFIG_GLOBAL": "1"}):
            result = resolve_config_file_path(kwargs, config_obj)
            # Path resolution may add /private prefix on macOS
            assert result.endswith("/etc/mcp/config.yaml")
