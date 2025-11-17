"""Tests for config_paths module."""

import os
from pathlib import Path
from unittest.mock import patch

from mcp_server_guide.config_paths import get_default_config_file, get_default_docroot


class TestGetDefaultConfigFile:
    """Test default config file path resolution."""

    @patch("platform.system")
    @patch.dict(os.environ, {"APPDATA": "/test/appdata"})
    def test_windows_with_appdata_env(self, mock_system):
        """Test Windows path with APPDATA environment variable."""
        mock_system.return_value = "Windows"

        result = get_default_config_file()

        expected = Path("/test/appdata") / "mcp-server-guide" / "config.yaml"
        assert result == expected

    @patch("platform.system")
    @patch.dict(os.environ, {}, clear=True)
    @patch("pathlib.Path.home")
    def test_windows_without_appdata_env(self, mock_home, mock_system):
        """Test Windows path fallback when APPDATA not set."""
        mock_system.return_value = "Windows"
        mock_home.return_value = Path("/test/home")

        result = get_default_config_file()

        expected = Path("/test/home") / "AppData" / "Roaming" / "mcp-server-guide" / "config.yaml"
        assert result == expected

    @patch("platform.system")
    @patch.dict(os.environ, {"XDG_CONFIG_HOME": "/test/xdg"})
    def test_unix_with_xdg_config_home(self, mock_system):
        """Test Unix path with XDG_CONFIG_HOME environment variable."""
        mock_system.return_value = "Linux"

        result = get_default_config_file()

        expected = Path("/test/xdg") / "mcp-server-guide" / "config.yaml"
        assert result == expected

    @patch("platform.system")
    @patch.dict(os.environ, {}, clear=True)
    @patch("pathlib.Path.home")
    def test_unix_without_xdg_config_home(self, mock_home, mock_system):
        """Test Unix path fallback when XDG_CONFIG_HOME not set."""
        mock_system.return_value = "Linux"
        mock_home.return_value = Path("/test/home")

        result = get_default_config_file()

        expected = Path("/test/home") / ".config" / "mcp-server-guide" / "config.yaml"
        assert result == expected


class TestGetDefaultDocroot:
    """Test default docroot path resolution."""

    @patch("mcp_server_guide.config_paths.get_default_config_file")
    def test_docroot_relative_to_config(self, mock_config_file):
        """Test docroot is relative to config file directory."""
        mock_config_file.return_value = Path("/test/config") / "mcp-server-guide" / "config.yaml"

        result = get_default_docroot()

        expected = Path("/test/config") / "mcp-server-guide" / "docs"
        assert result == expected
