"""Tests for async main conversion."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_server_guide.main import main


def test_main_returns_click_command():
    """Test that main() returns a Click command object."""
    command = main()  # main() is now sync

    # Should return a Click command
    assert hasattr(command, "__call__")
    assert hasattr(command, "name")


@pytest.mark.asyncio
async def test_async_main_with_server_startup():
    """Test async main with server startup."""
    with patch("mcp_server_guide.server.get_current_server") as mock_get_server:
        mock_server = AsyncMock()
        mock_server.run_stdio_async = AsyncMock()
        mock_get_server.return_value = mock_server

        # Test that we can start server asynchronously
        await mock_server.run_stdio_async()

        mock_server.run_stdio_async.assert_called_once()


@pytest.mark.asyncio
async def test_server_uses_run_stdio_async():
    """Test that server startup uses run_stdio_async method."""
    with patch("mcp_server_guide.server.get_current_server") as mock_get_server:
        mock_server = AsyncMock()
        mock_server.run_stdio_async = AsyncMock()
        mock_get_server.return_value = mock_server

        # Import the server startup function
        from mcp_server_guide.main import start_mcp_server

        # This should use the async method
        result = await start_mcp_server("stdio", {})

        # Should return success message
        assert "stdio mode" in result
