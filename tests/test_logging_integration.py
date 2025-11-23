"""Integration tests for logging fix to ensure no conflicts."""

import logging
from unittest.mock import MagicMock, patch

from src.mcp_server_guide.logging_config import _configure_fastmcp_logging, setup_consolidated_logging


class TestLoggingIntegration:
    """Test logging integration functionality."""

    def test_fastmcp_logs_flow_through_our_handlers(self):
        """Test that FastMCP logs flow through our handlers after configuration."""
        # Setup our logging with a test handler
        test_handler = MagicMock()

        with patch("logging.getLogger") as mock_get_logger:
            # Mock root logger
            mock_root_logger = MagicMock()
            mock_root_logger.handlers = [test_handler]
            mock_root_logger.level = logging.DEBUG

            # Mock FastMCP loggers
            mock_fastmcp_loggers = {}
            for logger_name in ["fastmcp", "mcp", "mcp.server", "mcp.client"]:
                mock_logger = MagicMock()
                mock_logger.handlers = []
                mock_fastmcp_loggers[logger_name] = mock_logger

            def get_logger_side_effect(name=""):
                if name == "":
                    return mock_root_logger
                return mock_fastmcp_loggers.get(name, MagicMock())

            mock_get_logger.side_effect = get_logger_side_effect

            # Call the configuration function
            _configure_fastmcp_logging()

            # Verify each FastMCP logger was configured correctly
            for logger_name in ["fastmcp", "mcp", "mcp.server", "mcp.client"]:
                mock_logger = mock_fastmcp_loggers[logger_name]
                mock_logger.addHandler.assert_called_with(test_handler)
                mock_logger.setLevel.assert_called_with(logging.DEBUG)
                assert mock_logger.propagate is True

    def test_consolidated_logging_integration(self):
        """Test that consolidated logging setup works end-to-end."""
        with patch("src.mcp_server_guide.logging_config.setup_logging") as mock_setup:
            with patch("src.mcp_server_guide.logging_config._configure_fastmcp_logging") as mock_configure:
                # Test with prevent_fastmcp_override=True (default)
                setup_consolidated_logging(
                    "stdio",
                    config_source={"log_level": "DEBUG", "log_console": False},
                    cli_overrides={"log_level": "INFO"},
                    prevent_fastmcp_override=True,
                )

                # Verify setup_logging was called with correct parameters
                mock_setup.assert_called_once_with("INFO", "", False, False)

                # Verify FastMCP configuration was called
                mock_configure.assert_called_once()

    def test_no_logging_conflicts_in_stdio_mode(self):
        """Test that there are no logging conflicts in stdio mode."""
        with patch("src.mcp_server_guide.logging_config.setup_logging") as mock_setup:
            with patch("src.mcp_server_guide.logging_config._configure_fastmcp_logging") as mock_configure:
                # Test stdio mode with default settings
                setup_consolidated_logging("stdio")

                # In stdio mode, console logging should be disabled by default
                mock_setup.assert_called_once_with("INFO", "", False, False)

                # FastMCP configuration should be called to prevent conflicts
                mock_configure.assert_called_once()
