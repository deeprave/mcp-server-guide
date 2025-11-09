"""Tests for logging configuration (Issue 007)."""

import logging
from unittest.mock import patch
from mcp_server_guide.config import Config
from mcp_server_guide.logging_config import setup_logging


async def test_config_has_logging_options():
    """Test that Config class has logging options."""
    config = Config()

    # Should have logging configuration options
    assert hasattr(config, "log_level")
    assert hasattr(config, "log_file")
    assert hasattr(config, "log_console")

    # Check default values
    assert config.log_level.default == "OFF"
    assert config.log_file.default == ""
    assert config.log_console.default() == "true"


async def test_setup_logging_console_only():
    """Test logging setup with console output only."""
    setup_logging("INFO", "", True)

    # Verify ROOT logger is configured (where handlers are now placed)
    import logging

    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO


async def test_setup_logging_off_level():
    """Test logging setup with OFF level."""
    setup_logging("OFF", "", False)

    import logging

    root_logger = logging.getLogger()
    # OFF level should disable logging
    assert root_logger.level >= logging.CRITICAL


async def test_setup_logging_file_directory_creation():
    """Test logging setup with file path."""
    # Just test that the function works with a file path
    logger = setup_logging("INFO", "/tmp/test.log", True)
    assert isinstance(logger, logging.Logger)
    assert logger.name == "mcp-server-guide"


async def test_setup_logging_all_levels():
    """Test logging setup with all valid levels."""
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    for level in levels:
        setup_logging(level, "", True)

        import logging

        root_logger = logging.getLogger()
        expected_level = getattr(logging, level)
        assert root_logger.level == expected_level


async def test_setup_logging_edge_cases():
    """Test logging setup edge cases to hit all branches."""
    # Test OFF level
    logger = setup_logging("OFF", "", False)
    root_logger = logging.getLogger()
    assert root_logger.level > logging.CRITICAL

    # Test different log levels
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logger = setup_logging(level, "", True)
        root_logger = logging.getLogger()
        expected_level = getattr(logging, level)
        assert root_logger.level == expected_level

    # Test with file logging
    logger = setup_logging("INFO", "/tmp/test.log", True)
    assert isinstance(logger, logging.Logger)

    # Test console only
    logger = setup_logging("INFO", "", True)
    assert isinstance(logger, logging.Logger)


async def test_setup_logging_file_error_handling():
    """Test logging setup with file errors."""
    # Test file logging error with console fallback
    with patch("logging.FileHandler", side_effect=OSError("Permission denied")):
        logger = setup_logging("INFO", "/invalid/path/test.log", True)
        assert isinstance(logger, logging.Logger)
        # Should have console handler as fallback on ROOT logger
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0

    # Test file logging error without console fallback
    with patch("logging.FileHandler", side_effect=IOError("Disk full")):
        logger = setup_logging("INFO", "/invalid/path/test.log", False)
        assert isinstance(logger, logging.Logger)


async def test_get_logger():
    """Test get_logger function."""
    from mcp_server_guide.logging_config import get_logger

    # Test default logger name
    logger1 = get_logger()
    assert logger1.name == "mcp-server-guide"

    # Test custom logger name
    logger2 = get_logger("custom")
    assert logger2.name == "custom"
