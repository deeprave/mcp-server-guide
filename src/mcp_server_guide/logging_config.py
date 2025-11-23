"""Logging configuration for MCP server."""

import contextlib
import json
import logging
import os
import shutil
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
    """Setup logging configuration with Rich compatibility for FastMCP."""
    # Get root logger for FastMCP compatibility
    root_logger = logging.getLogger()

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    # Handle OFF level
    if level.upper() == "OFF":
        root_logger.setLevel(logging.CRITICAL + 1)
        return logging.getLogger(logger_name())

    # Set level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    # Add the file handler to ROOT logger if specified
    if log_file:
        with contextlib.suppress(OSError, IOError):
            file_handler = FlushingFileHandler(log_file)
            file_handler.setLevel(numeric_level)
            formatter = (
                JSONFormatter()
                if log_json
                else logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
    # Add Rich console handler for FastMCP compatibility
    if log_console:
        try:
            from rich.console import Console
            from rich.logging import RichHandler

            term_width = int(os.environ.get("TERM_WIDTH", shutil.get_terminal_size().columns))
            console = Console(stderr=True, width=term_width - 10)  # 10 chars narrower than terminal
            console_handler = RichHandler(console=console, rich_tracebacks=True, log_time_format="%Y-%m-%d %H:%M:%S")
            console_handler.setLevel(numeric_level)
            root_logger.addHandler(console_handler)
        except ImportError:
            # Fallback to standard handler
            fallback_handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            fallback_handler.setFormatter(formatter)
            fallback_handler.setLevel(numeric_level)
            root_logger.addHandler(fallback_handler)

    # Return the named logger that propagates to the configured root
    return logging.getLogger(logger_name())


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get configured logger instance."""
    if not name:  # Handles None and empty string
        name = logger_name()
    return logging.getLogger(name)


def setup_consolidated_logging(
    mode: str,
    config_source: Optional[Dict[str, Any]] = None,
    cli_overrides: Optional[Dict[str, Any]] = None,
    prevent_fastmcp_override: bool = True,
) -> None:
    """Consolidated logging setup for all scenarios.

    Args:
        mode: Server mode (stdio, etc.)
        config_source: Configuration dict (None for early setup)
        cli_overrides: CLI argument overrides
        prevent_fastmcp_override: Whether to prevent FastMCP logging override
    """
    cli_overrides = cli_overrides or {}

    # Determine source priority: CLI overrides > config > defaults
    if config_source:
        # Final setup - use config with CLI overrides
        log_level = cli_overrides.get("log_level") or config_source.get("log_level", "OFF")
        log_file = cli_overrides.get("log_file") or config_source.get("log_file", "")
        log_console = cli_overrides.get("log_console")
        if log_console is None:
            log_console = config_source.get("log_console", True)
        log_json = cli_overrides.get("log_json")
        if log_json is None:
            log_json = config_source.get("log_json", False)
    else:
        # Early setup - use CLI args with defaults
        log_level = cli_overrides.get("log_level", "INFO")
        log_file = cli_overrides.get("log_file", "")
        log_console = cli_overrides.get("log_console", True)
        log_json = cli_overrides.get("log_json", False)

    # Apply stdio mode logic (shared between both scenarios)
    if mode == "stdio" and "log_console" not in cli_overrides:
        log_console = False

    # Force console if file logging (only for early setup and not explicitly disabled)
    if log_file and config_source is None and "log_console" not in cli_overrides:
        log_console = True

    # Setup logging - use main setup_logging function
    setup_logging(log_level or "INFO", log_file or "", bool(log_console), bool(log_json))

    # Prevent FastMCP override if requested
    if prevent_fastmcp_override:
        _configure_fastmcp_logging()


def _configure_fastmcp_logging() -> None:
    """Configure FastMCP to use our logging setup."""
    # Get our root logger configuration
    root_logger = logging.getLogger()
    our_handlers = root_logger.handlers[:]
    our_level = root_logger.level

    # Configure FastMCP loggers to use our setup
    fastmcp_loggers = ["fastmcp", "mcp", "mcp.server", "mcp.client"]

    for fastmcp_logger_name in fastmcp_loggers:
        logger = logging.getLogger(fastmcp_logger_name)
        # Only configure if not already configured with our handlers
        if not any(handler in our_handlers for handler in logger.handlers):
            logger.handlers = []
            for handler in our_handlers:
                logger.addHandler(handler)
        logger.setLevel(our_level)
        logger.propagate = True
