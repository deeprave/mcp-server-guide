"""Tests for server lifespan and deferred configuration."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestServerLifespan:
    """Test server lifespan functionality."""

    async def test_server_lifespan_with_deferred_config(self):
        """Test server_lifespan calls deferred configuration."""
        mock_server = MagicMock()

        # Mock the deferred config
        mock_config = {"guidesdir": "/test/guides"}

        with patch("mcp_server_guide.main._deferred_builtin_config") as mock_contextvar:
            mock_contextvar.get.return_value = mock_config
            with patch("mcp_server_guide.main.configure_builtin_categories", new_callable=AsyncMock) as mock_configure:
                with patch("mcp_server_guide.server.logger") as mock_logger:
                    # Import and test the server_lifespan function
                    from mcp_server_guide.server import server_lifespan

                    # Test the async context manager
                    async with server_lifespan(mock_server):
                        pass

                    # Verify deferred configuration was called
                    mock_configure.assert_called_once_with(mock_config)
                    mock_logger.debug.assert_any_call("Configuring built-in categories from deferred CLI config")
                    mock_logger.debug.assert_any_call("Built-in categories configured successfully")

    async def test_server_lifespan_with_empty_deferred_config(self):
        """Test server_lifespan with empty deferred config."""
        mock_server = MagicMock()

        # Mock empty deferred config
        with patch("mcp_server_guide.main._deferred_builtin_config") as mock_contextvar:
            mock_contextvar.get.return_value = {}
            with patch("mcp_server_guide.main.configure_builtin_categories", new_callable=AsyncMock) as mock_configure:
                with patch("mcp_server_guide.server.logger"):
                    from mcp_server_guide.server import server_lifespan

                    async with server_lifespan(mock_server):
                        pass

                    # Should not call configure when config is empty
                    mock_configure.assert_not_called()

    async def test_server_lifespan_configure_fails(self):
        """Test server_lifespan when configuration fails."""
        mock_server = MagicMock()

        mock_config = {"guidesdir": "/test/guides"}

        with patch("mcp_server_guide.main._deferred_builtin_config") as mock_contextvar:
            mock_contextvar.get.return_value = mock_config
            with patch("mcp_server_guide.main.configure_builtin_categories", new_callable=AsyncMock) as mock_configure:
                with patch("mcp_server_guide.server.logger") as mock_logger:
                    mock_configure.side_effect = Exception("Config failed")

                    from mcp_server_guide.server import server_lifespan

                    # Should not raise exception, just log warning
                    async with server_lifespan(mock_server):
                        pass

                    mock_configure.assert_called_once_with(mock_config)
                    mock_logger.warning.assert_called_once_with(
                        "Failed to configure built-in categories: Config failed"
                    )

    async def test_server_lifespan_initialization_error(self):
        """Test server_lifespan when initialization fails."""
        mock_server = MagicMock()

        with patch("mcp_server_guide.main._deferred_builtin_config") as mock_contextvar:
            mock_contextvar.get.return_value = {}
            with patch("mcp_server_guide.server.logger") as mock_logger:
                from mcp_server_guide.server import server_lifespan

                # Test that exceptions during initialization are properly handled
                with pytest.raises(Exception, match="Test error"):
                    async with server_lifespan(mock_server):
                        raise Exception("Test error")

                mock_logger.error.assert_called_once()
                mock_logger.info.assert_any_call("MCP server shutting down")
