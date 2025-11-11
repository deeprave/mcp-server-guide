"""Tests for configuration resolution flow from CLI to server initialization."""

import os
from unittest.mock import patch
from mcp_server_guide.main import resolve_config_file_path, resolve_config_path
from mcp_server_guide.path_resolver import LazyPath


class TestConfigResolutionFlow:
    """Test the complete config resolution flow."""

    def test_resolve_config_file_path_with_explicit_config(self):
        """Test that --config argument takes highest priority."""
        kwargs = {"config": "/custom/path/config.yaml"}

        result = resolve_config_file_path(kwargs)

        # Should return LazyPath wrapping the custom path
        assert isinstance(result, LazyPath)
        assert str(result) == "/custom/path/config.yaml"

    @patch.dict(os.environ, {"MG_CONFIG": "/env/config.yaml"})
    def test_resolve_config_file_path_with_env_var(self):
        """Test that MG_CONFIG environment variable is used when no CLI arg."""
        kwargs = {}

        result = resolve_config_file_path(kwargs)

        # Should return LazyPath wrapping the env var path
        assert isinstance(result, LazyPath)
        assert str(result) == "/env/config.yaml"

    @patch.dict(os.environ, {"MG_CONFIG": "/env/config.yaml"})
    def test_resolve_config_file_path_cli_overrides_env(self):
        """Test that --config takes precedence over MG_CONFIG."""
        kwargs = {"config": "/custom/config.yaml"}

        result = resolve_config_file_path(kwargs)

        # Should use CLI arg, not env var
        assert isinstance(result, LazyPath)
        assert str(result) == "/custom/config.yaml"

    def test_resolve_config_file_path_with_no_config(self):
        """Test behavior when no config is specified."""
        kwargs = {}

        with patch.dict(os.environ, {}, clear=True):
            result = resolve_config_file_path(kwargs)

            # Should return None when no config specified
            assert result is None

    def test_resolve_config_path_expands_environment_variables(self):
        """Test that config paths support environment variable expansion."""
        with patch.dict(os.environ, {"HOME": "/home/user"}):
            result = resolve_config_path("$HOME/.config/mcp.yaml")

            assert isinstance(result, LazyPath)
            assert str(result) == "/home/user/.config/mcp.yaml"

    def test_resolve_config_path_expands_tilde(self):
        """Test that config paths support ~ expansion."""
        result = resolve_config_path("~/config.yaml")

        assert isinstance(result, LazyPath)
        # Should expand to user's home directory
        assert not str(result).startswith("~")
        assert str(result).endswith("/config.yaml")

    def test_resolve_config_path_handles_relative_paths(self):
        """Test that relative paths are wrapped in LazyPath."""
        result = resolve_config_path("relative/config.yaml")

        assert isinstance(result, LazyPath)
        assert str(result) == "relative/config.yaml"

    def test_resolve_config_path_handles_absolute_paths(self):
        """Test that absolute paths are wrapped in LazyPath."""
        result = resolve_config_path("/absolute/config.yaml")

        assert isinstance(result, LazyPath)
        assert str(result) == "/absolute/config.yaml"

    def test_lazy_path_preserves_original_path(self):
        """Test that LazyPath preserves the original path string."""
        lazy_path = LazyPath("/test/path.yaml")

        assert str(lazy_path) == "/test/path.yaml"

    def test_config_resolution_returns_lazy_path_not_string(self):
        """Test that config resolution returns LazyPath, not string."""
        kwargs = {"config": "/test/config.yaml"}

        result = resolve_config_file_path(kwargs)

        # IMPORTANT: Must be LazyPath, not string
        assert isinstance(result, LazyPath)
        assert not isinstance(result, str)
        # But should behave like a string when needed
        assert str(result) == "/test/config.yaml"


class TestServerInitialization:
    """Test server initialization with project setup."""
