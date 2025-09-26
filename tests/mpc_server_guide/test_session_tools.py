"""Tests for session MCP tools."""

from mcp_server_guide.session_tools import (
    set_project_config,
    get_project_config,
    list_project_configs,
    reset_project_config,
    switch_project,
    set_local_file,
)


def test_set_project_config_tool():
    """Test set_project_config MCP tool."""
    # Should set configuration for current project
    result = set_project_config("guidelines", "python-web")
    assert result["success"] is True
    assert "python-web" in result["message"]


def test_get_project_config_tool():
    """Test get_project_config MCP tool."""
    # Set some config first
    set_project_config("guidelines", "python-web")
    set_project_config("language", "python")

    # Get config
    result = get_project_config()
    assert result["success"] is True
    assert result["config"]["guidelines"] == "python-web"
    assert result["config"]["language"] == "python"


def test_list_project_configs_tool():
    """Test list_project_configs MCP tool."""
    # Set configs for multiple projects
    set_project_config("guidelines", "python-web")
    switch_project("projectB")
    set_project_config("guidelines", "rust-systems")

    # List all configs
    result = list_project_configs()
    assert result["success"] is True
    assert len(result["projects"]) >= 2


def test_reset_project_config_tool():
    """Test reset_project_config MCP tool."""
    # Set some config
    set_project_config("guide", "python-web")

    # Reset
    result = reset_project_config()
    assert result["success"] is True

    # Should be back to defaults
    config_result = get_project_config()
    assert config_result["config"]["guide"] == "guidelines"  # Default


def test_switch_project_tool():
    """Test switch_project MCP tool."""
    # Switch to different project
    result = switch_project("new-project")
    assert result["success"] is True
    assert "new-project" in result["message"]


def test_set_local_file_tool():
    """Test set_local_file MCP tool."""
    # Should set local file path
    result = set_local_file("guidelines", "./team-guide.md")
    assert result["success"] is True

    # Should be stored with local: prefix
    config_result = get_project_config()
    assert config_result["config"]["guidelines"] == "local:./team-guide.md"


def test_project_context_switching():
    """Test that project context affects tool behavior."""
    # Set config for project A
    switch_project("projectA")
    set_project_config("guidelines", "python-web")

    # Switch to project B
    switch_project("projectB")
    set_project_config("guidelines", "rust-systems")

    # Switch back to project A
    switch_project("projectA")
    config_result = get_project_config()
    assert config_result["config"]["guidelines"] == "python-web"

    # Switch back to project B
    switch_project("projectB")
    config_result = get_project_config()
    assert config_result["config"]["guidelines"] == "rust-systems"
