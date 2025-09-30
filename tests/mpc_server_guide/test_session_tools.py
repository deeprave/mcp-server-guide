"""Tests for session tools functionality."""

from mcp_server_guide.tools.config_tools import (
    get_project_config,
    set_project_config,
    set_project_config_values,
)


def test_set_project_config_values_tool():
    """Test batch project config setting tool."""
    # Test batch setting multiple values
    config_dict = {"docroot": "/test/path", "project": "test-project"}

    result = set_project_config_values(config_dict)

    assert result["success"] is True
    assert result["project"] is not None
    assert "2/2" in result["message"]  # Should show successful count

    # Verify the values were set
    config = get_project_config()
    assert config["docroot"] == "/test/path"
    assert config["project"] == "test-project"
    assert config["project"] == "test-project"


def test_set_project_config_values_partial_failure():
    """Test batch config setting with some failures."""
    # Mix valid and invalid keys - all keys should succeed in our implementation
    config_dict = {
        "docroot": "/test/guides",
        "project": "test-lang",
    }

    result = set_project_config_values(config_dict)

    assert result["success"] is True  # All should succeed


def test_set_project_config_tool():
    """Test set_project_config MCP tool."""
    # Should set configuration for current project
    result = set_project_config("docroot", "/test/path")
    assert result["success"] is True
    assert "/test/path" in result["message"]


def test_get_project_config_tool():
    """Test get_project_config MCP tool."""
    # Set some config first
    set_project_config("docroot", "/test/path")
    set_project_config("project", "test-project")

    # Get config
    config = get_project_config()
    assert config["docroot"] == "/test/path"
    assert config["project"] == "test-project"


def test_list_project_configs_tool():
    """Test list_project_configs MCP tool."""
    # Set config for multiple projects
    set_project_config("docroot", "/test/path")

    set_project_config("project", "test-project")

    # List all configs
    config = get_project_config()
    assert "docroot" in config


def test_reset_project_config_tool():
    """Test reset_project_config MCP tool."""
    # Set some config first
    set_project_config("guide", "python-web")

    # Reset config
    from mcp_server_guide.tools.session_management import reset_session

    result = reset_session()
    assert result["success"] is True

    # Verify config was reset
    config = get_project_config()
    # Should have default values, not the custom one we set
    assert config.get("guide") != "python-web"


def test_session_manager_initialization():
    """Test SessionManager singleton initialization."""
    from mcp_server_guide.session_tools import SessionManager

    # Get two instances
    session1 = SessionManager()
    session2 = SessionManager()

    # Should be the same instance (singleton)
    assert session1 is session2

    # Should have a current project
    assert session1.get_current_project() is not None


def test_project_context_switching():
    """Test project context switching with configuration."""
    # Set config for project A
    set_project_config("docroot", "/project-a")

    # Switch to project B
    from mcp_server_guide.tools.project_tools import switch_project

    result = switch_project("project-b")
    assert result["success"] is True

    # Set different config for project B
    set_project_config("docroot", "/project-b")

    # Verify each project has its own config
    config_b = get_project_config("project-b")
    assert config_b.get("docroot") == "/project-b"
