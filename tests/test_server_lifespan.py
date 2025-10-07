"""Tests for server lifespan and deferred configuration."""

import pytest
from unittest.mock import patch, MagicMock


class TestServerLifespan:
    """Test server lifespan functionality."""

    async def test_server_lifespan_basic(self):
        """Test server_lifespan basic initialization."""
        mock_server = MagicMock()

        with patch("mcp_server_guide.server.logger") as mock_logger:
            from mcp_server_guide.server import server_lifespan

            # Test the async context manager
            async with server_lifespan(mock_server):
                pass

            # Verify basic initialization messages
            mock_logger.info.assert_any_call("=== Starting MCP server initialization ===")
            mock_logger.info.assert_any_call("MCP server initialized successfully")
            mock_logger.info.assert_any_call("MCP server shutting down")

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
