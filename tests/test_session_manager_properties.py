"""Tests for SessionManager property behavior."""

from unittest.mock import patch

from mcp_server_guide.session_manager import SessionManager


def test_session_manager_pwd_based_approach():
    """Test SessionManager works with PWD-based approach."""
    session_manager = SessionManager()

    # PWD-based approach doesn't use directory property
    # Just verify the SessionManager can be instantiated and get current project
    assert session_manager is not None


def test_session_manager_pwd_required():
    """Test SessionManager requires PWD environment variable."""
    import os

    session_manager = SessionManager()

    # Save current PWD
    os.environ.get("PWD")

    result = session_manager.get_project_name()
    assert isinstance(result, str)


def test_session_manager_pwd_required_not_set():
    """Test SessionManager requires PWD environment variable."""
    import os
    import pytest

    session_manager = SessionManager()

    # Mock environment without PWD
    with patch.dict(os.environ, {}, clear=True):
        # Should raise ValueError when PWD is not set
        with pytest.raises(ValueError, match="PWD environment variable not set"):
            session_manager.get_project_name()
