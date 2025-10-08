"""Test DAIC prompt delegates file operations to agent."""

import pytest
from mcp_server_guide import server


@pytest.mark.asyncio
async def test_daic_prompt_includes_agent_instructions():
    """Test that DAIC prompt includes instructions for agent to handle .consent file."""
    # Test enabling DAIC
    result = await server.daic_prompt("on")

    # Should include instruction to remove .consent file
    assert "remove" in result.lower()
    assert ".consent" in result

    # Test disabling DAIC
    result = await server.daic_prompt("Implementation allowed")

    # Should include instruction to create .consent file
    assert "create" in result.lower() or "touch" in result.lower()
    assert ".consent" in result


@pytest.mark.asyncio
async def test_daic_status_check():
    """Test DAIC status check without file operations."""
    result = await server.daic_prompt()

    # Should return status without trying to access files
    assert "DAIC" in result
    assert "mode" in result
