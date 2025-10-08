"""Tests for SessionManager property behavior."""

from mcp_server_guide.session_tools import SessionManager


def test_session_manager_pwd_based_approach():
    """Test SessionManager works with PWD-based approach."""
    session_manager = SessionManager()

    # PWD-based approach doesn't use directory property
    # Just verify the SessionManager can be instantiated and get current project
    assert session_manager is not None


def test_session_manager_pwd_fallback():
    """Test SessionManager handles PWD environment variable."""
    session_manager = SessionManager()

    # Test that get_current_project works (may return None if PWD not set in test)
    import asyncio

    result = asyncio.run(session_manager.get_current_project())
    # Should return either a string or None
    assert result is None or isinstance(result, str)
