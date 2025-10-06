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


def test_ext_mcp_tool_decorator_initialization():
    """Test ExtMcpToolDecorator initializes with correct attributes."""
    from mcp_server_guide.server import ExtMcpToolDecorator, FastMCP

    mcp_instance = FastMCP()
    decorator = ExtMcpToolDecorator(mcp_instance, prefix="test_")

    assert decorator.mcp == mcp_instance
    assert decorator.default_prefix == "test_"
