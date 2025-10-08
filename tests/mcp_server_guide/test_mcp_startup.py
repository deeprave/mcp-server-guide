"""Tests for MCP server startup functionality."""

from unittest.mock import Mock, patch

from mcp_server_guide.main import start_mcp_server


async def test_stdio_mode_starts_mcp_server():
    """Test that stdio mode starts actual MCP server."""
    config = {"docroot": ".", "project": "test"}

    # Mock both the server creation and mcp.run to avoid stdio issues
    with patch("mcp_server_guide.server.create_server_with_config") as mock_create:
        with patch("mcp_server_guide.server.mcp") as mock_mcp:
            mock_mcp.run = Mock()

            result = start_mcp_server("stdio", config)

            # Should call create_server_with_config and mcp.run
            mock_create.assert_called_once_with(config)
            mock_mcp.run.assert_called_once()
            assert "MCP server started in stdio mode" in result


async def test_stdio_mode_handles_keyboard_interrupt():
    """Test that stdio mode handles KeyboardInterrupt gracefully."""
    config = {"docroot": ".", "project": "test"}

    with patch("mcp_server_guide.server.mcp") as mock_mcp:
        mock_mcp.run = Mock(side_effect=KeyboardInterrupt())

        result = start_mcp_server("stdio", config)

        # Should still return success message
        assert "MCP server started in stdio mode" in result


async def test_stdio_mode_handles_broken_pipe():
    """Test that stdio mode handles BrokenPipeError gracefully."""
    config = {"docroot": ".", "project": "test"}

    with patch("mcp_server_guide.server.mcp") as mock_mcp:
        mock_mcp.run = Mock(side_effect=BrokenPipeError())

        result = start_mcp_server("stdio", config)

        # Should still return success message
        assert "MCP server started in stdio mode" in result


async def test_server_startup_with_config():
    """Test server startup uses provided configuration."""
    config = {"docroot": "/custom/path", "project": "test_project", "guide": "custom_guide", "lang": "python"}

    with patch("mcp_server_guide.server.mcp") as mock_mcp:
        with patch("mcp_server_guide.server.create_server_with_config") as mock_create:
            mock_mcp.run = Mock()

            start_mcp_server("stdio", config)

            # Should call create_server_with_config with the provided config
            mock_create.assert_called_once_with(config)
