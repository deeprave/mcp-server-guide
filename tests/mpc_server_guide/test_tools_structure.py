"""Tests for MCP tools structure and functionality."""

from mcp_server_guide.tools.config_tools import (
    get_project_config,
    set_project_config,
)
from mcp_server_guide.tools.session_management import (
    save_session,
    load_session,
    reset_session,
)


async def test_tools_return_expected_types():
    """Test that all tools return expected data types."""
    # Test session management tools
    session = await save_session()
    assert isinstance(session, dict)
    assert "success" in session

    # Test config tools
    config = get_project_config()
    assert isinstance(config, dict)


async def test_tools_with_parameters():
    """Test tools accept and handle parameters correctly."""
    # Test config tool with parameters
    result = await set_project_config("docroot", "/test/path")
    assert result["success"] is True
    assert result["key"] == "docroot"
    assert result["value"] == "/test/path"


async def test_session_management_comprehensive():
    """Test comprehensive session management functionality."""
    # Save session
    result = await save_session()
    assert result["success"] is True

    # Load session
    result = load_session()
    assert result["success"] is True

    # Reset session
    result = reset_session()
    assert result["success"] is True


async def test_config_tools_comprehensive():
    """Test comprehensive configuration tools functionality."""
    # Set config
    result = await set_project_config("docroot", "/test/path", "test_project")
    assert result["success"] is True
    assert result["project"] == "test_project"

    # Get config
    config = get_project_config("test_project")
    assert isinstance(config, dict)
    assert config["docroot"] == "/test/path"
