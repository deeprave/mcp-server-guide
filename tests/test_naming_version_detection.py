"""Tests for naming module version detection functionality."""

import importlib
import importlib.metadata
from unittest.mock import patch


def test_mcp_guide_version_detection_when_available():
    """Test that MCP_GUIDE_VERSION is detected when metadata is available."""
    with patch("importlib.metadata.version", return_value="2.0.0"):
        import mcp_server_guide.naming

        importlib.reload(mcp_server_guide.naming)
        assert mcp_server_guide.naming.MCP_GUIDE_VERSION == "2.0.0"


def test_mcp_guide_version_fallback_when_unavailable():
    """Test that MCP_GUIDE_VERSION falls back to 'unknown' when metadata unavailable."""
    with patch("importlib.metadata.version", side_effect=importlib.metadata.PackageNotFoundError("Package not found")):
        import mcp_server_guide.naming

        importlib.reload(mcp_server_guide.naming)
        assert mcp_server_guide.naming.MCP_GUIDE_VERSION == "unknown"
