"""Tests for enhanced logging functionality."""

import json
import tempfile
from pathlib import Path
import pytest

from mcp_server_guide.logging_config import setup_logging, get_logger, JSONFormatter


def test_json_logging_format():
    """Test JSON logging format structure."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False) as f:
        log_file = f.name

    # Setup JSON logging
    logger = setup_logging("INFO", log_file, log_console=False, log_json=True)

    # Log test messages
    logger.info("Test info message")
    logger.error("Test error message", extra={"custom_field": "test_value"})

    # Read and verify JSON format
    log_content = Path(log_file).read_text()
    lines = [line.strip() for line in log_content.split("\n") if line.strip()]

    assert len(lines) == 2

    for line in lines:
        log_entry = json.loads(line)

        # Verify required fields
        assert "timestamp" in log_entry
        assert "level" in log_entry
        assert "logger" in log_entry
        assert "message" in log_entry
        assert "module" in log_entry
        assert "function" in log_entry

    # Verify custom field in second entry
    second_entry = json.loads(lines[1])
    assert second_entry["custom_field"] == "test_value"

    # Cleanup
    Path(log_file).unlink()


def test_text_logging_format():
    """Test text logging format."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False) as f:
        log_file = f.name

    # Setup text logging
    logger = setup_logging("INFO", log_file, log_console=False, log_json=False)

    # Log test message
    logger.info("Test info message")

    # Read and verify text format
    log_content = Path(log_file).read_text()
    lines = [line.strip() for line in log_content.split("\n") if line.strip()]

    assert len(lines) == 1
    assert "[INFO]" in lines[0]
    assert "Test info message" in lines[0]

    # Should not be JSON
    with pytest.raises(json.JSONDecodeError):
        json.loads(lines[0])

    # Cleanup
    Path(log_file).unlink()


async def test_reset_session_uses_current_directory():
    """Test that reset_session uses current directory name, not hardcoded tool name."""

    # This test is no longer needed since we removed reset_session
    pass


def test_centralized_logger_naming():
    """Test that all loggers use centralized naming."""
    from mcp_server_guide.naming import logger_name

    # Test get_logger uses centralized name
    logger1 = get_logger()
    logger2 = get_logger("")

    assert logger1.name == logger_name()
    assert logger2.name == logger_name()

    # Test with custom name
    custom_logger = get_logger("custom.module")
    assert custom_logger.name == "custom.module"


def test_json_formatter_with_exception():
    """Test JSON formatter handles exceptions correctly."""
    formatter = JSONFormatter()

    # Create a log record with exception info
    import logging

    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="Test error with exception",
        args=(),
        exc_info=None,
    )

    # Add fake exception info
    try:
        raise ValueError("Test exception")
    except ValueError:
        import sys

        record.exc_info = sys.exc_info()

    formatted = formatter.format(record)
    log_entry = json.loads(formatted)

    assert "exception" in log_entry
    assert "ValueError: Test exception" in log_entry["exception"]


def test_logging_levels():
    """Test different logging levels work correctly."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False) as f:
        log_file = f.name

    # Setup INFO level logging
    logger = setup_logging("INFO", log_file, log_console=False, log_json=False)

    logger.debug("Debug message")  # Should not appear
    logger.info("Info message")  # Should appear
    logger.warning("Warning message")  # Should appear
    logger.error("Error message")  # Should appear

    # Read log content
    log_content = Path(log_file).read_text()
    lines = [line.strip() for line in log_content.split("\n") if line.strip()]

    # Should have 3 lines (INFO, WARNING, ERROR - no DEBUG)
    assert len(lines) == 3
    assert "Debug message" not in log_content
    assert "Info message" in log_content
    assert "Warning message" in log_content
    assert "Error message" in log_content

    # Cleanup
    Path(log_file).unlink()


def test_invalid_log_level_handling():
    """Test that invalid log level input is handled properly."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False) as f:
        log_file = f.name

    # Test various invalid log levels
    invalid_levels = [None, "", "INVALID", "debug", 123, []]

    for invalid_level in invalid_levels:
        try:
            logger = setup_logging(invalid_level, log_file, log_console=False, log_json=False)
            # If no exception, verify logger still works (fallback behavior)
            assert logger is not None
        except (ValueError, TypeError, AttributeError):
            # Expected for some invalid inputs
            pass

    # Cleanup
    Path(log_file).unlink()


def test_logging_off():
    """Test that OFF level disables all logging."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False) as f:
        log_file = f.name

    # Setup OFF level logging
    logger = setup_logging("OFF", log_file, log_console=False, log_json=False)

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    # Read log content - should be empty
    log_content = Path(log_file).read_text()
    assert log_content.strip() == ""

    # Cleanup
    Path(log_file).unlink()
