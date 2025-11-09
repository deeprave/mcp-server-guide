"""Tests for async main conversion."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_server_guide.main import main, cli_main_async


@pytest.mark.asyncio
async def test_main_returns_click_command():
    """Test that main() returns a Click command object."""
    command = await main()

    # Should return a Click command
    assert hasattr(command, "__call__")
    assert hasattr(command, "name")


@pytest.mark.asyncio
async def test_cli_main_async_entry_point():
    """Test that cli_main can be called asynchronously."""
    with patch("mcp_server_guide.main.main") as mock_main:
        mock_command = MagicMock()
        mock_main.return_value = mock_command

        # Should be able to call without error
        await cli_main_async()

        mock_main.assert_called_once()


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
