"""Tests for MCP tools structure and functionality."""

from mcp_server_guide.session_manager import SessionManager
from mcp_server_guide.tools.config_tools import (
    get_project_config,
    set_project_config,
)


async def test_tools_return_expected_types():
    """Test that all tools return expected data types."""
    # Test config tools
    result = await get_project_config()
    assert isinstance(result, dict)
    assert "success" in result


async def test_tools_with_parameters():
    """Test tools accept and handle parameters correctly."""
    # Test config tool with parameters
    result = await set_project_config("docroot", "/test/path")
    assert result["success"] is True
    assert result["key"] == "docroot"
    assert result["value"] == "/test/path"


async def test_session_management_comprehensive():
    """Test comprehensive session management functionality."""
    # Session management functionality removed
    pass


async def test_config_tools_comprehensive():
    """Test comprehensive configuration tools functionality."""
    # Set the current project first, then set config
    session = SessionManager()
    session.set_project_name("test_project")
    result = await set_project_config("docroot", "/test/path")
    assert result["success"] is True
    assert result["project"] == "test_project"

    # Get config
    result = await get_project_config("test_project")
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["config"]["docroot"] == "/test/path"

    # Test get_project_config with a non-existent project
    non_existent_config = await get_project_config("non_existent_project")
    assert isinstance(non_existent_config, dict)  # Should return empty dict or default config
