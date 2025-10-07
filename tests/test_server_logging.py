"""Tests for server logging and tool decoration functionality."""

import pytest
from unittest.mock import patch
from mcp_server_guide.server import log_tool_usage


def test_log_tool_usage_logs_function_calls():
    """Test that log_tool_usage decorator logs function calls."""

    @log_tool_usage
    def sample_function(arg1, arg2=None):
        return f"result: {arg1}, {arg2}"

    with patch("mcp_server_guide.server.logger") as mock_logger:
        result = sample_function("test", arg2="value")
        assert result == "result: test, value"
        mock_logger.debug.assert_called()


def test_log_tool_usage_preserves_exceptions():
    """Test that log_tool_usage decorator preserves exceptions."""

    @log_tool_usage
    def failing_function():
        raise ValueError("Test error")

    with patch("mcp_server_guide.server.logger"):
        with pytest.raises(ValueError):
            failing_function()


def test_log_tool_usage_logs_non_async_function_calls():
    """Test that log_tool_usage decorator logs non-async function calls with NON-ASYNC prefix."""

    @log_tool_usage
    def sync_function():
        return "sync result"

    with patch("mcp_server_guide.server.logger") as mock_logger:
        result = sync_function()
        assert result == "sync result"

        # Check that NON-ASYNC TOOL CALL was logged
        debug_calls = [call.args[0] for call in mock_logger.debug.call_args_list]
        non_async_calls = [call for call in debug_calls if "NON-ASYNC TOOL CALL" in call]
        assert len(non_async_calls) > 0
        assert "sync_function" in non_async_calls[0]


def test_log_tool_usage_captures_caller_info():
    """Test that log_tool_usage decorator captures caller information for non-async functions."""

    @log_tool_usage
    def sync_function():
        return "sync result"

    with patch("mcp_server_guide.server.logger") as mock_logger:
        result = sync_function()
        assert result == "sync result"

        # Check that caller info is captured in the log message
        debug_calls = [call.args[0] for call in mock_logger.debug.call_args_list]
        non_async_calls = [call for call in debug_calls if "NON-ASYNC TOOL CALL" in call]
        assert len(non_async_calls) > 0

        # Check that caller info includes filename, line number, and function name
        caller_log = non_async_calls[0]
        assert "test_server_logging.py" in caller_log
        assert "in test_log_tool_usage_captures_caller_info" in caller_log


def test_log_tool_usage_handles_stack_inspection_errors():
    """Test that log_tool_usage decorator handles stack inspection errors gracefully."""

    @log_tool_usage
    def sync_function():
        return "sync result"

    with (
        patch("mcp_server_guide.server.logger") as mock_logger,
        patch("inspect.stack", side_effect=Exception("Stack inspection failed")),
    ):
        result = sync_function()
        assert result == "sync result"

        # Check that fallback message is logged when stack inspection fails
        debug_calls = [call.args[0] for call in mock_logger.debug.call_args_list]
        fallback_calls = [call for call in debug_calls if "caller info unavailable" in call]
        assert len(fallback_calls) > 0


def test_ext_mcp_tool_decorator_initialization():
    """Test ExtMcpToolDecorator initializes with correct attributes."""
    from mcp_server_guide.server import ExtMcpToolDecorator, FastMCP

    mcp_instance = FastMCP()
    decorator = ExtMcpToolDecorator(mcp_instance, prefix="test_")

    assert decorator.mcp == mcp_instance
    assert decorator.default_prefix == "test_"
