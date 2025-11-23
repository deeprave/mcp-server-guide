"""Tests for server startup fix to prevent hanging."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.mcp_server_guide.main import start_mcp_server


class TestServerStartupFix:
    """Test server startup fix functionality."""

    @pytest.mark.asyncio
    async def test_run_stdio_async_called_without_log_level(self):
        """Test that run_stdio_async is called without log_level parameter."""
        mock_server = MagicMock()
        mock_server.run_stdio_async = AsyncMock()

        with patch("src.mcp_server_guide.server.get_current_server", return_value=mock_server):
            with patch("src.mcp_server_guide.main._get_safe_logger") as mock_logger:
                mock_logger.return_value.info = MagicMock()
                mock_logger.return_value.debug = MagicMock()

                # Call start_mcp_server in stdio mode
                await start_mcp_server("stdio", {"test": "config"})

                # Verify run_stdio_async was called without log_level parameter
                mock_server.run_stdio_async.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_server_startup_does_not_hang(self):
        """Test that server startup completes without hanging."""
        mock_server = MagicMock()
        mock_server.run_stdio_async = AsyncMock()

        with patch("src.mcp_server_guide.server.get_current_server", return_value=mock_server):
            with patch("src.mcp_server_guide.main._get_safe_logger") as mock_logger:
                mock_logger.return_value.info = MagicMock()
                mock_logger.return_value.debug = MagicMock()

                # This should complete without hanging
                result = await asyncio.wait_for(
                    start_mcp_server("stdio", {"test": "config"}),
                    timeout=1.0,  # 1 second timeout
                )

                # Should return successfully
                assert result is not None
