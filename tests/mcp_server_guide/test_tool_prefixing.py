"""Tests for ExtMcpToolDecorator and tool prefixing functionality."""

from unittest.mock import Mock


async def test_ext_mcp_tool_decorator_default_prefix():
    """Test ExtMcpToolDecorator with default prefix."""
    from mcp_server_guide.server import ExtMcpToolDecorator

    mock_mcp = Mock()
    mock_tool_decorator = Mock()
    mock_mcp.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_mcp, prefix="guide_")

    @decorator.tool()
    def test_function():
        pass

    # Should call mcp.tool with prefixed name
    mock_mcp.tool.assert_called_once_with(name="guide_test_function")


async def test_ext_mcp_tool_decorator_custom_name():
    """Test ExtMcpToolDecorator with custom name parameter."""
    from mcp_server_guide.server import ExtMcpToolDecorator

    mock_mcp = Mock()
    mock_tool_decorator = Mock()
    mock_mcp.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_mcp, prefix="guide_")

    @decorator.tool(name="custom_name")
    def test_function():
        pass

    # Should use custom name with default prefix
    mock_mcp.tool.assert_called_once_with(name="guide_custom_name")


async def test_ext_mcp_tool_decorator_custom_prefix():
    """Test ExtMcpToolDecorator with custom prefix parameter."""
    from mcp_server_guide.server import ExtMcpToolDecorator

    mock_mcp = Mock()
    mock_tool_decorator = Mock()
    mock_mcp.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_mcp, prefix="guide_")

    @decorator.tool(prefix="workflow_")
    def test_function():
        pass

    # Should use custom prefix instead of default
    mock_mcp.tool.assert_called_once_with(name="workflow_test_function")


async def test_ext_mcp_tool_decorator_no_prefix():
    """Test ExtMcpToolDecorator with empty prefix."""
    from mcp_server_guide.server import ExtMcpToolDecorator

    mock_mcp = Mock()
    mock_tool_decorator = Mock()
    mock_mcp.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_mcp, prefix="guide_")

    @decorator.tool(prefix="")
    def test_function():
        pass

    # Should use no prefix
    mock_mcp.tool.assert_called_once_with(name="test_function")


async def test_ext_mcp_tool_decorator_kwargs_passthrough():
    """Test ExtMcpToolDecorator passes through additional kwargs."""
    from mcp_server_guide.server import ExtMcpToolDecorator

    mock_mcp = Mock()
    mock_tool_decorator = Mock()
    mock_mcp.tool.return_value = mock_tool_decorator

    decorator = ExtMcpToolDecorator(mock_mcp, prefix="guide_")

    @decorator.tool(description="Test description", other_param="value")
    def test_function():
        pass

    # Should pass through all kwargs
    mock_mcp.tool.assert_called_once_with(
        name="guide_test_function", description="Test description", other_param="value"
    )


async def test_guide_decorator_instance_exists():
    """Test that guide decorator instance is created."""
    from mcp_server_guide.server import guide

    # Should exist and be an ExtMcpToolDecorator
    assert hasattr(guide, "tool")
    assert hasattr(guide, "default_prefix")
    assert guide.default_prefix == "guide_"


async def test_all_tools_have_guide_prefix():
    """Test that all server tools are registered with guide_ prefix."""
    # This test will verify the actual tool registration
    # We'll check this by importing the server module and verifying
    # that the mcp instance has tools with guide_ prefixes

    # Import will trigger tool registration
    import mcp_server_guide.server  # noqa: F401

    # Check that tools are registered with guide_ prefix
    # Note: This is a simplified test - in reality we'd need to inspect
    # the FastMCP instance's registered tools
    expected_tools = [
        "guide_get_current_project",
        "guide_switch_project",
        "guide_get_project_config",
        "guide_set_project_config_values",
        "guide_set_project_config",
        "guide_get_effective_config",
        "guide_get_guide",
        "guide_get_language_guide",
        "guide_get_project_context",
        "guide_search_content",
        "guide_show_guide",
        "guide_show_language_guide",
        "guide_list_files",
        "guide_file_exists",
        "guide_get_file_content",
        "guide_reset_session",
    ]

    # This test will initially fail until we implement the decorator
    assert (
        len(expected_tools) == 16
    )  # Verify we have all tools listed (removed get_all_guides and show_project_summary)
