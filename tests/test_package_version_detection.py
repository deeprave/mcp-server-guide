"""Tests for package version detection functionality."""

import importlib
import importlib.metadata
from unittest.mock import patch


def test_package_version_detection_when_available():
    """Test that package version is detected when metadata is available."""
    with patch("mcp_server_guide.naming.importlib.metadata.version", return_value="1.0.0"):
        # Need to reload naming module first, then the main module
        import mcp_server_guide.naming

        importlib.reload(mcp_server_guide.naming)

        import mcp_server_guide

        importlib.reload(mcp_server_guide)
        assert mcp_server_guide.__version__ == "1.0.0"


def test_package_version_fallback_when_unavailable():
    """Test that package version falls back to 'unknown' when metadata unavailable."""
    with patch(
        "mcp_server_guide.naming.importlib.metadata.version",
        side_effect=importlib.metadata.PackageNotFoundError("Package not found"),
    ):
        # Need to reload naming module first, then the main module
        import mcp_server_guide.naming

        importlib.reload(mcp_server_guide.naming)

        import mcp_server_guide

        importlib.reload(mcp_server_guide)
        assert mcp_server_guide.__version__ == "unknown"

        importlib.reload(mcp_server_guide)
        assert mcp_server_guide.__version__ == "unknown"
