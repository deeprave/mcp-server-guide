"""Tests for MCP server startup (Issue 006 Phase 2)."""

import pytest
from unittest.mock import Mock, patch
from mcpguide.main import start_mcp_server


def test_stdio_mode_starts_mcp_server():
    """Test that stdio mode starts actual MCP server."""
    config = {"docroot": ".", "project": "test"}

    with patch("mcpguide.server.mcp") as mock_mcp:
        mock_mcp.run = Mock()
        result = start_mcp_server("stdio", config)

        # Should call mcp.run() for stdio mode
        mock_mcp.run.assert_called_once()
        assert "MCP server started in stdio mode" in result


def test_sse_mode_starts_http_server():
    """Test that SSE mode starts HTTP server."""
    config = {"docroot": ".", "project": "test", "mode_config": "http://localhost:8080/sse"}

    with patch("mcpguide.server.mcp") as mock_mcp:
        mock_mcp.run_server = Mock()
        result = start_mcp_server("sse", config)

        # Should call mcp.run_server() for SSE mode
        mock_mcp.run_server.assert_called_once()
        assert "MCP server started in sse mode" in result


def test_server_startup_uses_resolved_config():
    """Test that server startup uses the resolved configuration."""
    config = {"docroot": "/custom/docs", "guidesdir": "custom_guides/", "project": "myapp"}

    with patch("mcpguide.server.create_server_with_config") as mock_create:
        mock_server = Mock()
        mock_create.return_value = mock_server

        with patch("mcpguide.server.mcp") as mock_mcp:
            mock_mcp.run = Mock()
            start_mcp_server("stdio", config)

            # Should create server with resolved config
            mock_create.assert_called_once_with(config)


def test_server_handles_startup_errors():
    """Test that server handles startup errors gracefully."""
    config = {"docroot": ".", "project": "test"}

    with patch("mcpguide.server.mcp") as mock_mcp:
        mock_mcp.run.side_effect = Exception("Server startup failed")

        with pytest.raises(Exception) as exc_info:
            start_mcp_server("stdio", config)

        assert "Server startup failed" in str(exc_info.value)
