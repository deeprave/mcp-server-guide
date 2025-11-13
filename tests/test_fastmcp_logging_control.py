"""Tests for FastMCP logging control functionality."""

import logging
from unittest.mock import patch

from src.mcp_server_guide.logging_config import setup_consolidated_logging


class TestFastMCPLoggingControl:
    """Test FastMCP logging control functionality."""

    def test_configure_fastmcp_logging_function_exists(self):
        """Test that _configure_fastmcp_logging function exists."""
        from src.mcp_server_guide.logging_config import _configure_fastmcp_logging

        assert callable(_configure_fastmcp_logging)

    def test_configure_fastmcp_logging_configures_loggers(self):
        """Test that _configure_fastmcp_logging properly configures FastMCP loggers."""
        from src.mcp_server_guide.logging_config import _configure_fastmcp_logging

        # Setup root logger with test handlers
        root_logger = logging.getLogger()
        test_handler = logging.StreamHandler()
        root_logger.addHandler(test_handler)
        root_logger.setLevel(logging.DEBUG)

        try:
            # Call the function
            _configure_fastmcp_logging()

            # Verify FastMCP loggers are configured
            fastmcp_loggers = ["fastmcp", "mcp", "mcp.server", "mcp.client"]

            for logger_name in fastmcp_loggers:
                logger = logging.getLogger(logger_name)
                assert test_handler in logger.handlers
                assert logger.level == logging.DEBUG
                assert logger.propagate is True

        finally:
            # Cleanup
            root_logger.removeHandler(test_handler)

    def test_setup_consolidated_logging_uses_prevent_fastmcp_override(self):
        """Test that setup_consolidated_logging uses prevent_fastmcp_override parameter."""
        with patch("src.mcp_server_guide.logging_config._configure_fastmcp_logging") as mock_configure:
            # Test with prevent_fastmcp_override=True (default)
            setup_consolidated_logging("stdio", prevent_fastmcp_override=True)
            mock_configure.assert_called_once()

            mock_configure.reset_mock()

            # Test with prevent_fastmcp_override=False
            setup_consolidated_logging("stdio", prevent_fastmcp_override=False)
            mock_configure.assert_not_called()
