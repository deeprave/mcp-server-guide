"""Tests for logging configuration (Issue 007)."""

import logging
from unittest.mock import patch
from mcpguide.config import Config
from mcpguide.logging_config import setup_logging


def test_config_has_logging_options():
    """Test that Config class has logging options."""
    config = Config()

    # Should have logging configuration options
    assert hasattr(config, "log_level")
    assert hasattr(config, "log_file")
    assert hasattr(config, "log_console")

    # Check default values
    assert config.log_level.default == "OFF"
    assert config.log_file.default == ""
    assert config.log_console.default is True


def test_setup_logging_console_only():
    """Test logging setup with console output only."""
    setup_logging("INFO", "", True)

    # Verify logger is configured
    import logging

    logger = logging.getLogger("mcpguide")
    assert logger.level == logging.INFO


def test_setup_logging_off_level():
    """Test logging setup with OFF level."""
    setup_logging("OFF", "", False)

    import logging

    logger = logging.getLogger("mcpguide")
    # OFF level should disable logging
    assert logger.level >= logging.CRITICAL


def test_setup_logging_file_directory_creation():
    """Test logging setup with file path."""
    # Just test that the function works with a file path
    logger = setup_logging("INFO", "/tmp/test.log", True)
    assert isinstance(logger, logging.Logger)
    assert logger.name == "mcpguide"


def test_setup_logging_all_levels():
    """Test logging setup with all valid levels."""
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    for level in levels:
        setup_logging(level, "", True)

        import logging

        logger = logging.getLogger("mcpguide")
        expected_level = getattr(logging, level)
        assert logger.level == expected_level


def test_setup_logging_edge_cases():
    """Test logging setup edge cases to hit all branches."""
    # Test OFF level
    logger = setup_logging("OFF", "", False)
    assert logger.level > logging.CRITICAL

    # Test different log levels
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logger = setup_logging(level, "", True)
        expected_level = getattr(logging, level)
        assert logger.level == expected_level

    # Test with file logging
    logger = setup_logging("INFO", "/tmp/test.log", True)
    assert isinstance(logger, logging.Logger)

    # Test console only
    logger = setup_logging("INFO", "", True)
    assert isinstance(logger, logging.Logger)


def test_setup_logging_file_error_handling():
    """Test logging setup with file errors."""
    # Test file logging error with console fallback
    with patch("logging.FileHandler", side_effect=OSError("Permission denied")):
        logger = setup_logging("INFO", "/invalid/path/test.log", True)
        assert isinstance(logger, logging.Logger)
        # Should have console handler as fallback
        assert len(logger.handlers) > 0

    # Test file logging error without console fallback
    with patch("logging.FileHandler", side_effect=IOError("Disk full")):
        logger = setup_logging("INFO", "/invalid/path/test.log", False)
        assert isinstance(logger, logging.Logger)


def test_get_logger():
    """Test get_logger function."""
    from mcpguide.logging_config import get_logger

    # Test default logger name
    logger1 = get_logger()
    assert logger1.name == "mcpguide"

    # Test custom logger name
    logger2 = get_logger("custom")
    assert logger2.name == "custom"
