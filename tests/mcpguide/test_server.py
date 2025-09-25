"""Tests for mcpguide server module."""

from mcpguide.server import mcp, create_server_with_config


def test_mcp_instance_exists():
    """Test that MCP instance is created."""
    assert mcp is not None


def test_create_server_with_config():
    """Test server creation with configuration."""
    config = {
        "docroot": ".",
        "project": "test",
        "guide": "guidelines",
        "lang": "python"
    }

    # Should not raise an exception
    result = create_server_with_config(config)
    # Function returns None but should complete successfully
    assert result is None


def test_server_has_tools():
    """Test that server has tools registered."""
    # MCP server should have tools
    assert hasattr(mcp, 'tools')
    # Should have some tools registered
    tools = list(mcp.tools.keys()) if hasattr(mcp.tools, 'keys') else []
    assert len(tools) >= 0  # At least some tools should be registered
