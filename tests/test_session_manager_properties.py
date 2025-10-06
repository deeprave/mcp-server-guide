"""Tests for SessionManager property behavior."""

from pathlib import Path
from unittest.mock import patch
from mcp_server_guide.session_tools import SessionManager


def test_session_manager_directory_property_with_override():
    """Test that directory property returns override when set."""
    session_manager = SessionManager()

    test_path = Path("/test/path")
    session_manager._override_directory = test_path

    assert session_manager.directory == test_path


def test_session_manager_directory_property_no_override_no_client_path():
    """Test directory property when override is None and ClientPath returns None."""
    session_manager = SessionManager()
    session_manager._override_directory = None

    with patch("mcp_server_guide.client_path.ClientPath.get_primary_root", return_value=None):
        assert session_manager.directory is None
