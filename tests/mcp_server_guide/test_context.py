"""Tests for context variables."""

from mcp_server_guide.context import (
    clear_context,
    get_current_project_context,
    get_session_id_context,
    set_current_project_context,
    set_session_id_context,
)


def test_project_context():
    """Test project context management."""
    # Initially should be None
    assert get_current_project_context() is None

    # Set and get project
    set_current_project_context("test-project")
    assert get_current_project_context() == "test-project"

    # Clear context
    clear_context()
    assert get_current_project_context() is None


def test_session_id_context():
    """Test session ID context management."""
    # Initially should be None
    assert get_session_id_context() is None

    # Set and get session ID
    set_session_id_context("test-session-123")
    assert get_session_id_context() == "test-session-123"

    # Clear context
    clear_context()
    assert get_session_id_context() is None


def test_clear_context():
    """Test clearing all context variables."""
    # Set both contexts
    set_current_project_context("test-project")
    set_session_id_context("test-session")

    # Verify they're set
    assert get_current_project_context() == "test-project"
    assert get_session_id_context() == "test-session"

    # Clear and verify
    clear_context()
    assert get_current_project_context() is None
    assert get_session_id_context() is None
