"""Tests for MCP server startup functionality."""

from unittest.mock import Mock, patch

from mcp_server_guide.main import start_mcp_server


async def test_stdio_mode_starts_mcp_server():
    """Test that stdio mode starts actual MCP server."""
    from mcp_server_guide.server import reset_server_state

    reset_server_state()  # Reset global state

    config = {"docroot": ".", "project": "test"}

    # Mock the server creation and server.run to avoid stdio issues
    with patch("mcp_server_guide.server.create_server_with_config") as mock_create:
        mock_server = Mock()
        mock_create.return_value = mock_server

        result = start_mcp_server("stdio", config)

        # Should call create_server_with_config and server.run
        mock_create.assert_called_once_with(config)
        mock_server.run.assert_called_once()
        assert "MCP server started in stdio mode" in result


async def test_stdio_mode_handles_keyboard_interrupt():
    """Test that stdio mode handles KeyboardInterrupt gracefully."""
    from mcp_server_guide.server import reset_server_state

    reset_server_state()  # Reset global state

    config = {"docroot": ".", "project": "test"}

    with patch("mcp_server_guide.server.create_server_with_config") as mock_create:
        mock_server = Mock()
        mock_server.run = Mock(side_effect=KeyboardInterrupt())
        mock_create.return_value = mock_server

        result = start_mcp_server("stdio", config)

        # Should still return success message
        assert "MCP server started in stdio mode" in result


async def test_stdio_mode_handles_broken_pipe():
    """Test that stdio mode handles BrokenPipeError gracefully."""
    from mcp_server_guide.server import reset_server_state

    reset_server_state()  # Reset global state

    config = {"docroot": ".", "project": "test"}

    with patch("mcp_server_guide.server.create_server_with_config") as mock_create:
        mock_server = Mock()
        mock_server.run = Mock(side_effect=BrokenPipeError())
        mock_create.return_value = mock_server

        result = start_mcp_server("stdio", config)

        # Should still return success message
        assert "MCP server started in stdio mode" in result


async def test_server_startup_with_config():
    """Test server startup uses provided configuration."""
    from mcp_server_guide.server import reset_server_state

    reset_server_state()  # Reset global state

    config = {"docroot": "/custom/path", "project": "test_project", "guide": "custom_guide", "lang": "python"}

    with patch("mcp_server_guide.server.create_server_with_config") as mock_create:
        mock_server = Mock()
        mock_server.run = Mock()
        mock_create.return_value = mock_server

        start_mcp_server("stdio", config)

        # Should call create_server_with_config with the provided config
        mock_create.assert_called_once_with(config)
