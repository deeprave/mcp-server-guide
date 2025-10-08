"""Test removal of current_file properties."""

import pytest
from mcp_server_guide.session_tools import SessionManager


@pytest.mark.asyncio
async def test_current_file_property_removed():
    """Test that current_file property is removed."""
    session_manager = SessionManager()

    # Should not have current_file property
    assert not hasattr(session_manager, "current_file")


@pytest.mark.asyncio
async def test_current_file_name_property_removed():
    """Test that current_file_name property is removed."""
    session_manager = SessionManager()

    # Should not have current_file_name property
    assert not hasattr(session_manager, "current_file_name")
