"""Tests for package version detection functionality."""

import importlib
import importlib.metadata
from unittest.mock import patch


def test_package_version_detection_when_available():
    """Test that package version is detected when metadata is available."""
    with patch("importlib.metadata.version", return_value="1.0.0"):
        import mcp_server_guide

        importlib.reload(mcp_server_guide)
        assert mcp_server_guide.__version__ == "1.0.0"


def test_package_version_fallback_when_unavailable():
    """Test that package version falls back to 'unknown' when metadata unavailable."""
    with patch("importlib.metadata.version", side_effect=importlib.metadata.PackageNotFoundError("Package not found")):
        import mcp_server_guide

        importlib.reload(mcp_server_guide)
        assert mcp_server_guide.__version__ == "unknown"
