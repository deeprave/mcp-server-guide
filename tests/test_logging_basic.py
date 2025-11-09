"""Basic logging functionality tests."""

import tempfile
from pathlib import Path


from mcp_server_guide.logging_config import setup_logging, get_logger, setup_consolidated_logging


class TestLoggingBasic:
    """Test basic logging functionality."""

    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        logger = setup_logging("INFO")
        assert logger.name == "mcp-server-guide"

    def test_setup_logging_with_file(self):
        """Test logging setup with file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            logger = setup_logging("INFO", tmp.name)
            logger.info("Test message")

            # Check file exists and has content
            log_path = Path(tmp.name)
            assert log_path.exists()
            content = log_path.read_text()
            assert "Test message" in content

            # Cleanup
            log_path.unlink()

    def test_setup_logging_off_level(self):
        """Test OFF level disables logging."""
        logger = setup_logging("OFF")
        assert logger.name == "mcp-server-guide"

    def test_get_logger_default(self):
        """Test get_logger with default name."""
        logger = get_logger()
        assert logger.name == "mcp-server-guide"

    def test_get_logger_custom_name(self):
        """Test get_logger with custom name."""
        logger = get_logger("custom")
        assert logger.name == "custom"

    def test_setup_consolidated_logging_early(self):
        """Test consolidated logging early setup."""
        setup_consolidated_logging("stdio", cli_overrides={"log_level": "DEBUG"})
        # Should not raise exception

    def test_setup_consolidated_logging_final(self):
        """Test consolidated logging final setup."""
        config = {"log_level": "INFO", "log_console": True}
        setup_consolidated_logging("stdio", config_source=config)
        # Should not raise exception
