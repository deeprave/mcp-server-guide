"""Tests for MCP server startup functionality."""

from unittest.mock import Mock, patch

from mcpguide.main import start_mcp_server


def test_stdio_mode_starts_mcp_server():
    """Test that stdio mode starts actual MCP server."""
    config = {"docroot": ".", "project": "test"}

    # Mock both the server creation and mcp.run to avoid stdio issues
    with patch("mcpguide.server.create_server_with_config") as mock_create:
        with patch("mcpguide.server.mcp") as mock_mcp:
            mock_mcp.run = Mock()

            result = start_mcp_server("stdio", config)

            # Should call create_server_with_config and mcp.run
            mock_create.assert_called_once_with(config)
            mock_mcp.run.assert_called_once()
            assert "MCP server started in stdio mode" in result


def test_sse_mode_starts_uvicorn():
    """Test that SSE mode starts uvicorn server."""
    config = {"docroot": ".", "project": "test", "mode_config": "http://localhost:8080/sse"}

    with patch("uvicorn.run") as mock_uvicorn:
        result = start_mcp_server("sse", config)

        # Should call uvicorn.run for SSE mode
        mock_uvicorn.assert_called_once()
        call_args = mock_uvicorn.call_args
        assert call_args[1]["host"] == "localhost"
        assert call_args[1]["port"] == 8080
        assert "MCP server started in sse mode" in result


def test_stdio_mode_handles_keyboard_interrupt():
    """Test that stdio mode handles KeyboardInterrupt gracefully."""
    config = {"docroot": ".", "project": "test"}

    with patch("mcpguide.server.mcp") as mock_mcp:
        mock_mcp.run = Mock(side_effect=KeyboardInterrupt())

        result = start_mcp_server("stdio", config)

        # Should still return success message
        assert "MCP server started in stdio mode" in result


def test_stdio_mode_handles_broken_pipe():
    """Test that stdio mode handles BrokenPipeError gracefully."""
    config = {"docroot": ".", "project": "test"}

    with patch("mcpguide.server.mcp") as mock_mcp:
        mock_mcp.run = Mock(side_effect=BrokenPipeError())

        result = start_mcp_server("stdio", config)

        # Should still return success message
        assert "MCP server started in stdio mode" in result


def test_sse_mode_handles_keyboard_interrupt():
    """Test that SSE mode handles KeyboardInterrupt gracefully."""
    config = {"docroot": ".", "project": "test", "mode_config": "http://localhost:8080/sse"}

    with patch("uvicorn.run") as mock_uvicorn:
        mock_uvicorn.side_effect = KeyboardInterrupt()

        result = start_mcp_server("sse", config)

        # Should still return success message
        assert "MCP server started in sse mode" in result


def test_server_startup_with_config():
    """Test server startup uses provided configuration."""
    config = {"docroot": "/custom/path", "project": "test_project", "guide": "custom_guide", "lang": "python"}

    with patch("mcpguide.server.mcp") as mock_mcp:
        with patch("mcpguide.server.create_server_with_config") as mock_create:
            mock_mcp.run = Mock()

            start_mcp_server("stdio", config)

            # Should call create_server_with_config with the provided config
            mock_create.assert_called_once_with(config)
