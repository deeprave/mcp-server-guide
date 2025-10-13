"""Tests for session tools functionality."""

from mcp_server_guide.session_manager import SessionManager
from mcp_server_guide.tools.config_tools import (
    get_project_config,
    set_project_config,
    set_project_config_values,
)


async def test_set_project_config_values_tool(isolated_config_file):
    """Test batch project config setting tool."""
    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)
    session_manager.set_project_name("test-project")

    # Test batch setting multiple values with valid categories
    config_dict = {
        "categories": {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
    }

    result = await set_project_config_values(config_dict)

    assert result["success"] is True
    assert result["project"] == "test-project"
    assert "1/1" in result["message"]  # Should show successful count

    # Verify the values were set
    result = await get_project_config()
    assert result["success"] is True
    assert "test" in result["config"]["categories"]
    assert result["project"] == "test-project"


async def test_set_project_config_values_partial_failure(isolated_config_file):
    """Test batch config setting with valid categories."""
    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    # Set valid categories configuration
    config_dict = {
        "categories": {"guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Guide files"}}
    }

    result = await set_project_config_values(config_dict)

    assert result["success"] is True  # Should succeed


async def test_set_project_config_tool(isolated_config_file):
    """Test set_project_config MCP tool."""
    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    # Should set configuration for current project with valid categories
    result = await set_project_config(
        "categories", {"lang": {"dir": "lang/", "patterns": ["*.py"], "description": "Language files"}}
    )
    assert result["success"] is True
    assert "lang" in result["message"]


async def test_get_project_config_tool(isolated_config_file):
    """Test get_project_config MCP tool."""
    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)
    session_manager.set_project_name("test-project")

    # Set some config first with valid categories
    await set_project_config(
        "categories", {"context": {"dir": "context/", "patterns": ["*.txt"], "description": "Context files"}}
    )

    # Get config
    result = await get_project_config()
    assert result["success"] is True
    assert "context" in result["config"]["categories"]
    assert result["project"] == "test-project"

    # List all configs
    result = await get_project_config()
    assert "config" in result
    assert "categories" in result["config"]


async def test_session_manager_initialization(isolated_config_file):
    """Test SessionManager singleton initialization."""
    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    # Get two instances
    session1 = SessionManager()
    session2 = SessionManager()

    # Should be the same instance (singleton)
    assert session1 is session2

    # Should have a current project
    assert session1.get_project_name() is not None


async def test_project_context_switching(isolated_config_file):
    """Test project context switching with configuration."""
    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    # Switch to project B
    from mcp_server_guide.tools.project_tools import switch_project

    result = await switch_project("project-b")
    assert result["success"] is True

    # Set config for current project with valid categories
    await set_project_config(
        "categories", {"docs": {"dir": "docs/", "patterns": ["*.md"], "description": "Documentation"}}
    )

    # Verify project has the config
    result = await get_project_config("project-b")
    assert result["success"] is True
    assert "docs" in result["config"]["categories"]
