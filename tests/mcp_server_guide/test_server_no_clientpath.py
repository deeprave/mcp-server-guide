"""Test server functions without ClientPath dependency."""

import pytest

from mcp_server_guide import server


@pytest.mark.asyncio
async def test_server_imports_without_clientpath():
    """Test that server module can be imported without ClientPath."""
    # Should be able to import server functions without ClientPath
    assert hasattr(server, "create_server")


@pytest.mark.asyncio
async def test_ensure_client_roots_removed():
    """Test that ensure_client_roots_initialized function is removed."""
    # Should not have this function anymore
    assert not hasattr(server, "ensure_client_roots_initialized")
