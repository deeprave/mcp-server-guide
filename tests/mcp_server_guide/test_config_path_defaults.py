"""Tests for config file path resolution defaults."""

import getpass
from pathlib import Path
from unittest.mock import patch

from mcp_server_guide.main import resolve_config_path_with_client_defaults


class TestConfigPathDefaults:
    """Test config file path resolution defaults to client-relative."""

    def test_unprefixed_config_path_defaults_to_client(self):
        """Test that unprefixed config paths resolve relative to client."""
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            # Unprefixed path should default to client-relative
            result = resolve_config_path_with_client_defaults("config.yaml")
            expected = Path("/client/root/config.yaml")
            assert result == expected

    def test_explicit_client_prefix_works(self):
        """Test that explicit client:// prefix works."""
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_path_with_client_defaults("client://config.yaml")
            expected = Path("/client/root/config.yaml")
            assert result == expected

    def test_server_prefix_bypasses_client_default(self):
        """Test that server:// prefix bypasses client-relative behavior."""
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_path_with_client_defaults("server://config.yaml")
            expected = Path("config.yaml").resolve()
            assert result == expected

    def test_absolute_path_bypasses_client_default(self):
        """Test that absolute paths bypass client-relative behavior."""
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_path_with_client_defaults("/absolute/config.yaml")
            expected = Path("/absolute/config.yaml")
            assert result == expected

    def test_no_client_root_falls_back_to_server(self):
        """Test fallback to server-side resolution when no client root."""
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = None

            result = resolve_config_path_with_client_defaults("config.yaml")
            expected = Path("config.yaml").resolve()
            assert result == expected

    def test_global_config_paths_work_correctly(self):
        """Test that global config paths work correctly."""
        # Test common global config locations
        global_paths = [
            "/etc/mcp-server-guide/config.yaml",
            "~/.config/mcp-server-guide/config.yaml",
            "/usr/local/etc/mcp-server-guide/config.yaml",
        ]

        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            for global_path in global_paths:
                result = resolve_config_path_with_client_defaults(global_path)
                expected = Path(global_path).expanduser().resolve()
                assert result == expected

    def test_http_urls_preserved(self):
        """Test that HTTP URLs are preserved as-is."""
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_path_with_client_defaults("http://example.com/config.yaml")
            # HTTP URLs should be returned as Path objects (current behavior)
            assert "example.com/config.yaml" in str(result)

    def test_environment_variable_config_path(self):
        """Test that environment variable config paths work."""
        with patch.dict("os.environ", {"MCP_CONFIG": "/env/config.yaml", "HOME": "/home/user"}):
            # Test $VAR expansion
            result = resolve_config_path_with_client_defaults("$MCP_CONFIG")
            expected = Path("/env/config.yaml")
            assert result == expected

            # Test ${VAR} expansion
            result = resolve_config_path_with_client_defaults("${MCP_CONFIG}")
            assert result == expected

            # Test combined expansion
            result = resolve_config_path_with_client_defaults("$HOME/.config/app.yaml")
            # Use string comparison to handle path normalization differences
            assert str(result).endswith("/home/user/.config/app.yaml")

    def test_home_directory_expansion(self):
        """Test that home directory paths are expanded correctly."""
        # Test ~ expansion
        result = resolve_config_path_with_client_defaults("~/config.yaml")
        assert result.is_absolute()
        assert "config.yaml" in str(result)

        # Test ~username expansion (if user exists)
        current_user = getpass.getuser()
        result = resolve_config_path_with_client_defaults(f"~{current_user}/config.yaml")
        assert result.is_absolute()
        assert "config.yaml" in str(result)

    def test_combined_expansion_scenarios(self):
        """Test combined environment variable and home directory expansion."""
        with patch.dict("os.environ", {"CONFIG_DIR": "~/.config"}):
            result = resolve_config_path_with_client_defaults("$CONFIG_DIR/app.yaml")
            assert result.is_absolute()
            assert str(result).endswith(".config/app.yaml")


class TestConfigPathIntegration:
    """Test config path resolution integration with CLI."""

    def test_config_loading_with_client_relative_paths(self):
        """Test end-to-end config loading with client-relative paths."""
        # This will test the full pipeline once implemented
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = True

                with patch("pathlib.Path.read_text") as mock_read:
                    mock_read.return_value = "port: 8080\nhost: localhost"

                    # Test that config is loaded from client-relative path
                    result = resolve_config_path_with_client_defaults("server.yaml")
                    expected = Path("/client/root/server.yaml")
                    assert result == expected


class TestConfigPathEdgeCases:
    """Test edge cases in config path resolution."""

    def test_empty_config_path(self):
        """Test handling of empty config path."""
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_path_with_client_defaults("")
            expected = Path("/client/root/")
            assert result == expected

    def test_dot_config_path(self):
        """Test handling of '.' config path."""
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_path_with_client_defaults(".")
            expected = Path("/client/root/.")
            assert result == expected

    def test_relative_path_with_parent_dirs(self):
        """Test relative paths with parent directory references."""
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            result = resolve_config_path_with_client_defaults("../config/server.yaml")
            expected = Path("/client/root/../config/server.yaml")
            assert result == expected

    def test_windows_style_paths(self):
        """Test Windows-style paths (if on Windows or for compatibility)."""
        with patch("mcp_server_guide.main.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            # Test backslash paths
            result = resolve_config_path_with_client_defaults("config\\server.yaml")
            expected = Path("/client/root/config\\server.yaml")
            assert result == expected
