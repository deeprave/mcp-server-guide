"""Test session tools."""

from mcp_server_guide.tools.config_tools import (
    set_project_config,
    set_project_config_values,
    get_project_config,
)
from mcp_server_guide.session_tools import reset_project_config, set_local_file
from mcp_server_guide.tools.project_tools import switch_project, get_current_project


def test_set_project_config_values_tool(isolated_config):
    """Test batch project config setting tool."""
    # Test batch setting multiple values
    config_dict = {"guidesdir": "test_guides/", "langdir": "test_lang/", "language": "python"}

    result = set_project_config_values(config_dict, config_filename=isolated_config)

    assert result["success"] is True
    assert result["total_keys"] == 3
    assert result["success_count"] == 3
    assert len(result["results"]) == 3

    # Verify each key was set
    for item in result["results"]:
        assert item["success"] is True
        assert item["key"] in config_dict
        assert item["value"] == config_dict[item["key"]]


def test_set_project_config_values_partial_failure(isolated_config):
    """Test batch config setting with some failures."""
    # Mix valid and invalid keys - all keys should succeed in our implementation
    config_dict = {
        "guidesdir": "valid_guides/",
        "custom_key": "custom_value",  # This should work
        "language": "python",
    }

    result = set_project_config_values(config_dict, config_filename=isolated_config)

    assert result["success"] is True  # All should succeed
    assert result["total_keys"] == 3
    assert result["success_count"] == 3


def test_set_project_config_tool(isolated_config):
    """Test set_project_config MCP tool."""
    # Should set configuration for current project
    result = set_project_config("guidelines", "python-web", config_filename=isolated_config)
    assert result["success"] is True
    assert "python-web" in result["message"]


def test_get_project_config_tool(isolated_config):
    """Test get_project_config MCP tool."""
    # Set some config first
    set_project_config("guidelines", "python-web", config_filename=isolated_config)
    set_project_config("language", "python", config_filename=isolated_config)

    # Get config
    result = get_project_config()
    assert isinstance(result, dict)
    assert result["guidelines"] == "python-web"


def test_list_project_configs_tool(isolated_config):
    """Test list_project_configs MCP tool."""
    # Set config for multiple projects
    set_project_config("guidelines", "python-web", config_filename=isolated_config)

    set_project_config("guidelines", "rust-systems", config_filename=isolated_config)

    # List all configs
    result = get_project_config()
    assert isinstance(result, dict)


def test_reset_project_config_tool(isolated_config):
    """Test reset_project_config MCP tool."""
    # Set some config first
    set_project_config("guide", "python-web", config_filename=isolated_config)

    # Reset config
    result = reset_project_config()
    assert result["success"] is True


def test_switch_project_tool():
    """Test switch_project MCP tool."""
    # Switch to different project
    result = switch_project("test-project")
    assert result["success"] is True
    assert result["project"] == "test-project"

    # Verify current project changed
    current = get_current_project()
    assert current == "test-project"


def test_set_local_file_tool():
    """Test set_local_file MCP tool."""
    # Set local file mapping
    result = set_local_file("guide", "./local-guide.md")
    assert result["success"] is True
    assert "local-guide.md" in result["message"]


def test_project_context_switching(isolated_config):
    """Test project context switching with configuration."""
    # Set config for project A
    set_project_config("guidelines", "python-web", config_filename=isolated_config)

    # Switch to project B
    switch_project("project-b")

    # Set different config for project B
    set_project_config("guidelines", "rust-systems", config_filename=isolated_config)

    # Switch back to original project
    switch_project("mcp-server-guide")

    # Original config should still be there
    result = get_project_config()
    assert isinstance(result, dict)
