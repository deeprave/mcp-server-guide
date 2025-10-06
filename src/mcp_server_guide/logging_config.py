"""Logging configuration for MCP server."""

import json
import logging
import sys
from typing import Any, Dict, Optional
from .naming import logger_name


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry: Dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record.__dict__ if present
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "message",
            ]:
                log_entry[key] = value

        return json.dumps(log_entry, ensure_ascii=False)


class FlushingFileHandler(logging.FileHandler):
    """File handler that flushes after every log message."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record and flush immediately."""
        super().emit(record)
        self.flush()


def setup_logging(level: str, log_file: str = "", log_console: bool = True, log_json: bool = False) -> logging.Logger:
    """Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARN, ERROR, OFF)
        log_file: Path to log file (empty for no file logging)
        log_console: Enable console logging to stderr
        log_json: Enable JSON structured logging to file (console remains text format)

    Returns:
        Configured logger instance
    """
    global _logging_initialized

    # Get or create logger
    logger = logging.getLogger(logger_name())

    # Clear any existing handlers
    logger.handlers.clear()

    # Handle OFF level
    if level.upper() == "OFF":
        logger.setLevel(logging.CRITICAL + 1)  # Disable all logging
        return logger

    # Set logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Create formatters
    text_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    json_formatter = JSONFormatter()

    # Add file handler if specified
    if log_file:
        try:
            file_handler = FlushingFileHandler(log_file)
            file_handler.setLevel(numeric_level)
            # Use JSON formatter for file if requested, otherwise text
            file_handler.setFormatter(json_formatter if log_json else text_formatter)
            logger.addHandler(file_handler)

        except (OSError, IOError) as e:
            # If file logging fails, fall back to console
            if log_console:
                stderr_handler = logging.StreamHandler(sys.stderr)
                stderr_handler.setLevel(numeric_level)
                stderr_handler.setFormatter(text_formatter)
                logger.addHandler(stderr_handler)
                logger.error(f"Failed to setup file logging: {e}")
            return logger

    # Add console handler if enabled (always uses text format)
    if log_console:
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(numeric_level)
        stderr_handler.setFormatter(text_formatter)
        logger.addHandler(stderr_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get configured logger instance."""
    if not name:  # Handles None and empty string
        name = logger_name()
    return logging.getLogger(name)
