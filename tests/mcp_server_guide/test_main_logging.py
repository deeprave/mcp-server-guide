"""Tests for main.py logging setup functions."""

from unittest.mock import patch


from mcp_server_guide.main import setup_early_logging, setup_final_logging


class TestSetupEarlyLogging:
    """Test early logging setup function."""

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_early_logging_stdio_mode_default(self, mock_setup_logging):
        """Test early logging setup for stdio mode with default console disabled."""
        setup_early_logging("stdio", log_level="DEBUG")

        mock_setup_logging.assert_called_once_with("DEBUG", "", False, False)

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_early_logging_stdio_mode_console_explicit(self, mock_setup_logging):
        """Test early logging setup for stdio mode with explicit console enabled."""
        setup_early_logging("stdio", log_level="INFO", log_console=True)

        mock_setup_logging.assert_called_once_with("INFO", "", True, False)

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_early_logging_with_log_file(self, mock_setup_logging):
        """Test early logging setup with log file enables console."""
        setup_early_logging("stdio", log_level="WARNING", log_file="/tmp/test.log")

        mock_setup_logging.assert_called_once_with("WARNING", "/tmp/test.log", True, False)

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_early_logging_non_stdio_mode(self, mock_setup_logging):
        """Test early logging setup for non-stdio mode keeps console enabled."""
        setup_early_logging("server", log_level="ERROR")

        mock_setup_logging.assert_called_once_with("ERROR", "", True, False)

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_early_logging_with_json_format(self, mock_setup_logging):
        """Test early logging setup with JSON format."""
        setup_early_logging("server", log_level="DEBUG", log_json=True)

        mock_setup_logging.assert_called_once_with("DEBUG", "", True, True)

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_early_logging_default_level(self, mock_setup_logging):
        """Test early logging setup with default INFO level."""
        setup_early_logging("server")

        mock_setup_logging.assert_called_once_with("INFO", "", True, False)


class TestSetupFinalLogging:
    """Test final logging setup function."""

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_final_logging_stdio_mode_default(self, mock_setup_logging):
        """Test final logging setup for stdio mode with default console disabled."""
        config = {"log_level": "DEBUG", "log_file": "", "log_console": True, "log_json": False}
        setup_final_logging(config, "stdio")

        mock_setup_logging.assert_called_once_with("DEBUG", "", False, False)

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_final_logging_stdio_mode_console_explicit(self, mock_setup_logging):
        """Test final logging setup for stdio mode with explicit console in kwargs."""
        config = {"log_level": "INFO", "log_file": "", "log_console": True, "log_json": False}
        setup_final_logging(config, "stdio", log_console=True)

        mock_setup_logging.assert_called_once_with("INFO", "", True, False)

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_final_logging_with_file_and_json(self, mock_setup_logging):
        """Test final logging setup with file and JSON format."""
        config = {"log_level": "WARNING", "log_file": "/tmp/app.log", "log_console": False, "log_json": True}
        setup_final_logging(config, "server")

        mock_setup_logging.assert_called_once_with("WARNING", "/tmp/app.log", False, True)

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_final_logging_off_level_passes_through(self, mock_setup_logging):
        """Test final logging setup with OFF level passes through to setup_logging."""
        config = {"log_level": "OFF", "log_file": "", "log_console": True, "log_json": False}
        setup_final_logging(config, "server")

        mock_setup_logging.assert_called_once_with("OFF", "", True, False)

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_final_logging_empty_level_fallback(self, mock_setup_logging):
        """Test final logging setup with empty level falls back to INFO."""
        config = {"log_level": "", "log_file": "", "log_console": True, "log_json": False}
        setup_final_logging(config, "server")

        mock_setup_logging.assert_called_once_with("INFO", "", True, False)

    @patch("mcp_server_guide.logging_config.setup_logging")
    def test_setup_final_logging_empty_file_fallback(self, mock_setup_logging):
        """Test final logging setup with empty file string."""
        config = {"log_level": "ERROR", "log_file": "", "log_console": True, "log_json": False}
        setup_final_logging(config, "server")

        mock_setup_logging.assert_called_once_with("ERROR", "", True, False)
