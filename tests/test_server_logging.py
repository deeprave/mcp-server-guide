"""Tests for server logging and tool decoration functionality."""

import pytest
from unittest.mock import patch
from mcp_server_guide.server import log_tool_usage


def test_log_tool_usage_logs_function_calls():
    """Test that log_tool_usage decorator logs function calls."""

    @log_tool_usage
    def sample_function(arg1, arg2=None):
        return f"result: {arg1}, {arg2}"

    with patch("mcp_server_guide.tool_decoration.logger") as mock_logger:
        result = sample_function("test", arg2="value")
        assert result == "result: test, value"
        mock_logger.info.assert_called()


def test_log_tool_usage_preserves_exceptions():
    """Test that log_tool_usage decorator preserves exceptions."""

    @log_tool_usage
    def failing_function():
        raise ValueError("Test error")

    with patch("mcp_server_guide.tool_decoration.logger"):
        with pytest.raises(ValueError):
            failing_function()


def test_log_tool_usage_logs_non_async_function_calls():
    """Test that log_tool_usage decorator logs non-async function calls."""

    @log_tool_usage
    def sync_function():
        return "sync result"

    with patch("mcp_server_guide.tool_decoration.logger") as mock_logger:
        result = sync_function()
        assert result == "sync result"
        mock_logger.info.assert_called()


def test_log_tool_usage_captures_caller_info():
    """Test that log_tool_usage decorator captures caller information for non-async functions."""

    @log_tool_usage
    def sync_function():
        return "sync result"

    with patch("mcp_server_guide.tool_decoration.logger") as mock_logger:
        result = sync_function()
        assert result == "sync result"
        mock_logger.info.assert_called()


def test_log_tool_usage_handles_stack_inspection_errors():
    """Test that log_tool_usage decorator handles stack inspection errors gracefully."""

    @log_tool_usage
    def sync_function():
        return "sync result"

    with patch("mcp_server_guide.tool_decoration.logger") as mock_logger:
        result = sync_function()
        assert result == "sync result"
        mock_logger.info.assert_called()


def test_log_tool_usage_handles_none_return():
    """Test that log_tool_usage decorator handles functions returning None."""

    @log_tool_usage
    def function_returning_none():
        return None

    with patch("mcp_server_guide.tool_decoration.logger") as mock_logger:
        result = function_returning_none()
        assert result is None
        mock_logger.info.assert_called()


def test_log_tool_usage_handles_system_exit():
    """Test that log_tool_usage decorator handles SystemExit."""

    @log_tool_usage
    def function_raising_system_exit():
        raise SystemExit("Test exit")

    with patch("mcp_server_guide.tool_decoration.logger") as mock_logger:
        with pytest.raises(SystemExit):
            function_raising_system_exit()
        mock_logger.info.assert_called()


def test_ext_mcp_tool_decorator_initialization():
    """Test ExtMcpToolDecorator initializes with correct attributes."""
    from mcp_server_guide.server import ExtMcpToolDecorator, FastMCP

    mcp_instance = FastMCP("test")
    decorator = ExtMcpToolDecorator(mcp_instance, prefix="test_")

    assert decorator.server == mcp_instance
    assert decorator.default_prefix == "test_"
