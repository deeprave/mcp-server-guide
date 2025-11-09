"""Tests for MCP server startup functionality."""

from unittest.mock import patch, AsyncMock

from mcp_server_guide.main import start_mcp_server


async def test_stdio_mode_starts_mcp_server():
    """Test that stdio mode starts actual MCP server."""
    from mcp_server_guide.server import reset_server_state

    reset_server_state()  # Reset global state

    config = {"docroot": ".", "project": "test"}

    # Mock the server creation and server.run to avoid stdio issues
    with patch("mcp_server_guide.server.get_current_server") as mock_get_server:
        mock_server = AsyncMock()
        mock_server.run_stdio_async = AsyncMock()
        mock_get_server.return_value = mock_server

        result = await start_mcp_server("stdio", config)

        # Should call get_current_server and server.run_stdio_async
        mock_get_server.assert_called_once()
        mock_server.run_stdio_async.assert_called_once()
        assert "MCP server started in stdio mode" in result


async def test_stdio_mode_handles_keyboard_interrupt():
    """Test that stdio mode handles KeyboardInterrupt gracefully."""
    from mcp_server_guide.server import reset_server_state

    reset_server_state()  # Reset global state

    config = {"docroot": ".", "project": "test"}

    with patch("mcp_server_guide.server.get_current_server") as mock_get_server:
        mock_server = AsyncMock()
        mock_server.run_stdio_async = AsyncMock(side_effect=KeyboardInterrupt())
        mock_get_server.return_value = mock_server

        result = await start_mcp_server("stdio", config)

        # Should still return success message
        assert "MCP server started in stdio mode" in result


async def test_stdio_mode_handles_broken_pipe():
    """Test that stdio mode handles BrokenPipeError gracefully."""
    from mcp_server_guide.server import reset_server_state

    reset_server_state()  # Reset global state

    config = {"docroot": ".", "project": "test"}

    with patch("mcp_server_guide.server.get_current_server") as mock_get_server:
        mock_server = AsyncMock()
        mock_server.run_stdio_async = AsyncMock(side_effect=BrokenPipeError())
        mock_get_server.return_value = mock_server

        result = await start_mcp_server("stdio", config)

        # Should still return success message
        assert "MCP server started in stdio mode" in result


async def test_server_startup_with_config():
    """Test server startup uses provided configuration."""
    from mcp_server_guide.server import reset_server_state

    reset_server_state()  # Reset global state

    config = {"docroot": "/custom/path", "project": "test_project", "guide": "custom_guide", "lang": "python"}

    with patch("mcp_server_guide.server.get_current_server") as mock_get_server:
        mock_server = AsyncMock()
        mock_server.run_stdio_async = AsyncMock()
        mock_get_server.return_value = mock_server

        await start_mcp_server("stdio", config)

        # Should call get_current_server
        mock_get_server.assert_called_once()
