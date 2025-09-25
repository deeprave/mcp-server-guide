"""Tests for logging configuration (Issue 007)."""

import tempfile
import os
from mcpguide.config import Config


def test_config_has_logging_options():
    """Test that Config class has logging options."""
    config = Config()

    # Should have logging configuration options
    assert hasattr(config, 'log_level')
    assert hasattr(config, 'log_file')
    assert hasattr(config, 'log_console')

    # Check default values
    assert config.log_level.default == "OFF"
    assert config.log_file.default == ""
    assert config.log_console.default is True


def test_logging_cli_options():
    """Test that CLI has logging options."""
    from mcpguide.main import main

    command = main()
    option_names = [param.name for param in command.params if hasattr(param, 'name')]

    assert 'log_level' in option_names
    assert 'log_file' in option_names
    assert 'log_console' in option_names


def test_logging_environment_variables():
    """Test logging environment variable support."""
    config = Config()

    assert config.log_level.env_var == "MCP_LOG_LEVEL"
    assert config.log_file.env_var == "MCP_LOG_FILE"
    assert config.log_console.env_var == "MCP_LOG_CONSOLE"


def test_setup_logging_stderr_default():
    """Test that logging defaults to stderr when no file specified."""
    from mcpguide.logging_config import setup_logging

    logger = setup_logging(level="INFO", log_file="", log_console=True)

    # Should have stderr handler
    handlers = logger.handlers
    assert len(handlers) > 0
    # Check that at least one handler writes to stderr
    import sys
    stderr_handlers = [h for h in handlers if getattr(h, 'stream', None) is sys.stderr]
    assert len(stderr_handlers) > 0


def test_setup_logging_file_only():
    """Test logging to file only (no console)."""
    from mcpguide.logging_config import setup_logging

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    try:
        logger = setup_logging(level="DEBUG", log_file=tmp_path, log_console=False)

        # Should have file handler only
        handlers = logger.handlers
        file_handlers = [h for h in handlers if hasattr(h, 'baseFilename')]
        assert len(file_handlers) > 0

        # Should not have stderr handler
        import sys
        stderr_handlers = [h for h in handlers if getattr(h, 'stream', None) is sys.stderr]
        assert len(stderr_handlers) == 0

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_setup_logging_both_file_and_console():
    """Test logging to both file and console."""
    from mcpguide.logging_config import setup_logging

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    try:
        logger = setup_logging(level="INFO", log_file=tmp_path, log_console=True)

        # Should have both file and stderr handlers
        handlers = logger.handlers
        file_handlers = [h for h in handlers if hasattr(h, 'baseFilename')]
        assert len(file_handlers) > 0

        import sys
        stderr_handlers = [h for h in handlers if getattr(h, 'stream', None) is sys.stderr]
        assert len(stderr_handlers) > 0

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
