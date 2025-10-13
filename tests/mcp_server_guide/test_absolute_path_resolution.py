"""Tests for docroot property in SessionManager."""

import pytest
from mcp_server_guide.session_manager import SessionManager


@pytest.mark.asyncio
async def test_docroot_defaults_to_current():
    """Test that docroot defaults to current directory when not explicitly set."""
    # Reset singleton to ensure fresh state
    SessionManager.clear()
    session = SessionManager()

    # Set up project with categories only (no docroot in project config)
    session.session_state.set_project_name("test-project")
    session.session_state.set_project_config("categories", {"guide": {"dir": "guide/", "patterns": ["*.md"]}})

    # Access docroot via SessionManager property
    docroot = session.docroot

    # Should default to "."
    assert docroot is not None
    assert str(docroot) == "."


@pytest.mark.asyncio
async def test_docroot_property_accessible():
    """Test that docroot can be accessed via SessionManager.docroot property."""
    SessionManager.clear()
    session = SessionManager()

    session.session_state.set_project_name("test-project")
    session.session_state.set_project_config("categories", {"guide": {"dir": "guide/", "patterns": ["*.md"]}})

    # docroot should be accessible
    assert session.docroot is not None


@pytest.mark.asyncio
async def test_project_config_does_not_contain_docroot():
    """Test that project config never contains docroot field."""
    SessionManager.clear()
    session = SessionManager()

    session.session_state.set_project_name("test-project")
    session.session_state.set_project_config("categories", {"guide": {"dir": "guide/", "patterns": ["*.md"]}})

    # Get project config
    config = session.get_full_project_config()

    # Should NOT contain docroot
    assert "docroot" not in config
    # Should only contain categories
    assert "categories" in config


@pytest.mark.asyncio
async def test_docroot_not_settable_in_project_config():
    """Test that attempting to set docroot in project config raises validation error."""
    SessionManager.clear()
    session = SessionManager()

    session.session_state.set_project_name("test-project")

    # Attempting to set docroot in project config should fail
    with pytest.raises(ValueError, match="Invalid project configuration"):
        session.session_state.set_project_config("docroot", "/some/path")
