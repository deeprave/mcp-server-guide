"""Comprehensive tests for tool decoration module."""

import os
from unittest.mock import Mock, patch
import pytest
from mcp_server_guide.tool_decoration import log_tool_usage, get_tool_prefix, ExtMcpToolDecorator


def test_log_tool_usage_sync_function():
    """Test log_tool_usage decorator with sync function."""

    @log_tool_usage
    def sync_function(x, y):
        return x + y

    result = sync_function(1, 2)
    assert result == 3


def test_log_tool_usage_sync_function_with_exception():
    """Test log_tool_usage decorator handles sync function exceptions."""

    @log_tool_usage
    def failing_sync_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        failing_sync_function()


@pytest.mark.asyncio
async def test_log_tool_usage_async_function():
    """Test log_tool_usage decorator with async function."""

    @log_tool_usage
    async def async_function(x, y):
        return x * y

    result = await async_function(3, 4)
    assert result == 12


@pytest.mark.asyncio
async def test_log_tool_usage_async_function_with_exception():
    """Test log_tool_usage decorator handles async function exceptions."""

    @log_tool_usage
    async def failing_async_function():
        raise RuntimeError("Async error")

    with pytest.raises(RuntimeError, match="Async error"):
        await failing_async_function()


def test_get_tool_prefix_default():
    """Test get_tool_prefix returns default value."""
    with patch.dict(os.environ, {}, clear=True):
        prefix = get_tool_prefix()
        assert prefix == "guide"


def test_get_tool_prefix_from_env():
    """Test get_tool_prefix reads from environment variable."""
    with patch.dict(os.environ, {"MCP_TOOL_PREFIX": "custom"}, clear=True):
        prefix = get_tool_prefix()
        assert prefix == "custom"


def test_ext_mcp_tool_decorator_init_default_prefix():
    """Test ExtMcpToolDecorator initialization with default prefix."""
    mock_server = Mock()
    decorator = ExtMcpToolDecorator(mock_server)
    assert decorator.prefix == "guide_"


def test_ext_mcp_tool_decorator_init_custom_prefix():
    """Test ExtMcpToolDecorator initialization with custom prefix."""
    mock_server = Mock()
    decorator = ExtMcpToolDecorator(mock_server, prefix="custom_")
    assert decorator.prefix == "custom_"


def test_ext_mcp_tool_decorator_tool_with_name():
    """Test ExtMcpToolDecorator.tool with custom name."""
    mock_server = Mock()
    mock_tool_decorator = Mock()
    mock_server.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_server, prefix="test_")

    @decorator.tool(name="custom_name")
    def test_function():
        pass

    mock_server.tool.assert_called_once_with(name="test_custom_name")


def test_ext_mcp_tool_decorator_tool_without_name():
    """Test ExtMcpToolDecorator.tool without custom name."""
    mock_server = Mock()
    mock_tool_decorator = Mock()
    mock_server.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_server, prefix="test_")

    @decorator.tool()
    def test_function():
        pass

    mock_server.tool.assert_called_once_with(name="test_test_function")


def test_ext_mcp_tool_decorator_tool_with_description():
    """Test ExtMcpToolDecorator.tool passes through description."""
    mock_server = Mock()
    mock_tool_decorator = Mock()
    mock_server.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_server, prefix="test_")

    @decorator.tool(description="Test description")
    def test_function():
        pass

    mock_server.tool.assert_called_once_with(name="test_test_function", description="Test description")


def test_ext_mcp_tool_decorator_tool_with_schema():
    """Test ExtMcpToolDecorator.tool passes through schema."""
    mock_server = Mock()
    mock_tool_decorator = Mock()
    mock_server.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_server, prefix="test_")
    schema = {"type": "object"}

    @decorator.tool(schema=schema)
    def test_function():
        pass

    mock_server.tool.assert_called_once_with(name="test_test_function", schema=schema)


def test_ext_mcp_tool_decorator_tool_passes_through_all_kwargs():
    """Test ExtMcpToolDecorator.tool passes through all kwargs."""
    mock_server = Mock()
    mock_tool_decorator = Mock()
    mock_server.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_server, prefix="test_")

    @decorator.tool(description="Valid", custom_param="Should be passed")
    def test_function():
        pass

    mock_server.tool.assert_called_once_with(
        name="test_test_function", description="Valid", custom_param="Should be passed"
    )


def test_ext_mcp_tool_decorator_tool_with_custom_prefix():
    """Test ExtMcpToolDecorator.tool with custom prefix parameter."""
    mock_server = Mock()
    mock_tool_decorator = Mock()
    mock_server.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_server, prefix="default_")

    @decorator.tool(prefix="custom_")
    def test_function():
        pass

    mock_server.tool.assert_called_once_with(name="custom_test_function")


def test_ext_mcp_tool_decorator_tool_with_empty_prefix():
    """Test ExtMcpToolDecorator.tool with empty prefix."""
    mock_server = Mock()
    mock_tool_decorator = Mock()
    mock_server.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_server, prefix="default_")

    @decorator.tool(prefix="")
    def test_function():
        pass

    mock_server.tool.assert_called_once_with(name="test_function")


def test_ext_mcp_tool_decorator_tool_with_none_prefix():
    """Test ExtMcpToolDecorator.tool with None prefix."""
    mock_server = Mock()
    mock_tool_decorator = Mock()
    mock_server.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_server, prefix="default_")

    @decorator.tool(prefix=None)
    def test_function():
        pass

    mock_server.tool.assert_called_once_with(name="default_test_function")
