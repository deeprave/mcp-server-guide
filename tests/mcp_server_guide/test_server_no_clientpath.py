"""Test server functions without ClientPath dependency."""

import pytest
from unittest.mock import patch
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


@pytest.mark.asyncio
async def test_daic_check_without_clientpath():
    """Test DAIC check works without ClientPath dependency."""
    # Mock the session to avoid actual MCP context
    with patch("mcp_server_guide.session.get_session") as mock_session:
        mock_session.return_value = None

        # Should not raise an error about ClientPath
        result = await server.check_daic_status()
        # Should return True since we delegate file operations to agent
        assert result is True
