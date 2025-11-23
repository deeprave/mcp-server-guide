"""Test FastMCP API compatibility fix."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_server_guide.main import start_mcp_server


@pytest.mark.asyncio
async def test_fastmcp_run_stdio_async_no_invalid_parameters():
    """Test that run_stdio_async is called without invalid parameters."""
    with patch("mcp_server_guide.server.get_current_server") as mock_get_server:
        mock_server = AsyncMock()
        mock_get_server.return_value = mock_server

        # This should not raise TypeError about unexpected keyword arguments
        await start_mcp_server("stdio", {})

        # Verify run_stdio_async was called with no parameters
        mock_server.run_stdio_async.assert_called_once_with()
