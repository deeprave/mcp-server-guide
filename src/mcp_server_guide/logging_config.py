"""Logging configuration for MCP server."""

import logging
import sys


def setup_logging(level: str, log_file: str = "", log_console: bool = True) -> logging.Logger:
    """Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARN, ERROR, OFF)
        log_file: Path to log file (empty for no file logging)
        log_console: Enable console logging to stderr

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger("mcp-server-guide")

    # Clear any existing handlers
    logger.handlers.clear()

    # Handle OFF level
    if level.upper() == "OFF":
        logger.setLevel(logging.CRITICAL + 1)  # Disable all logging
        return logger

    # Set logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # Add file handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            # If file logging fails, fall back to console
            if log_console:
                stderr_handler = logging.StreamHandler(sys.stderr)
                stderr_handler.setLevel(numeric_level)
                stderr_handler.setFormatter(formatter)
                logger.addHandler(stderr_handler)
                logger.error(f"Failed to setup file logging: {e}")
            return logger

    # Add console handler if enabled (and not stdio mode)
    if log_console:
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(numeric_level)
        stderr_handler.setFormatter(formatter)
        logger.addHandler(stderr_handler)

    return logger


def get_logger(name: str = "mcp-server-guide") -> logging.Logger:
    """Get configured logger instance."""
    return logging.getLogger(name)
