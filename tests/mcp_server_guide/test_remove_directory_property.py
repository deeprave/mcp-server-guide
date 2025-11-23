"""Test removal of directory property and file handling."""

import pytest

from mcp_server_guide.session_manager import SessionManager


@pytest.mark.asyncio
async def test_directory_property_removed():
    """Test that directory property is removed."""
    session_manager = SessionManager()

    # Should not have directory property
    assert not hasattr(session_manager, "directory")


@pytest.mark.asyncio
async def test_is_directory_set_removed():
    """Test that is_directory_set method is removed."""
    session_manager = SessionManager()

    # Should not have is_directory_set method
    assert not hasattr(session_manager, "is_directory_set")


@pytest.mark.asyncio
async def test_set_directory_removed():
    """Test that set_directory method is removed."""
    session_manager = SessionManager()

    # Should not have set_directory method
    assert not hasattr(session_manager, "set_directory")


@pytest.mark.asyncio
async def test_override_directory_removed():
    """Test that _override_directory attribute is removed."""
    session_manager = SessionManager()

    # Should not have _override_directory attribute
    assert not hasattr(session_manager, "_override_directory")
