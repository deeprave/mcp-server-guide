"""Tests for tools structure and functionality."""

from mcp_server_guide.server import mcp
from mcp_server_guide.tools.file_tools import list_files, file_exists, get_file_content
from mcp_server_guide.tools.project_tools import get_current_project, switch_project, list_projects
from mcp_server_guide.tools.session_management import save_session, load_session, reset_session


def test_tools_are_importable():
    """Test that all tool modules can be imported."""
    from mcp_server_guide.tools import config_tools, content_tools, file_tools, project_tools, session_management

    # Basic smoke test - modules should import without error
    assert config_tools is not None
    assert content_tools is not None
    assert file_tools is not None
    assert project_tools is not None
    assert session_management is not None


def test_tools_have_expected_functions():
    """Test that tool modules have expected functions."""
    from mcp_server_guide.tools import config_tools, content_tools, file_tools, project_tools, session_management

    # Check config_tools
    assert hasattr(config_tools, "get_project_config")
    assert hasattr(config_tools, "set_project_config")

    # Check content_tools
    assert hasattr(content_tools, "get_guide")
    assert hasattr(content_tools, "get_language_guide")

    # Check file_tools
    assert hasattr(file_tools, "list_files")
    assert hasattr(file_tools, "file_exists")
    assert hasattr(file_tools, "get_file_content")

    # Check project_tools
    assert hasattr(project_tools, "get_current_project")
    assert hasattr(project_tools, "switch_project")
    assert hasattr(project_tools, "list_projects")

    # Check session_management
    assert hasattr(session_management, "save_session")
    assert hasattr(session_management, "load_session")
    assert hasattr(session_management, "reset_session")


def test_mcp_server_has_tools():
    """Test that MCP server has tools registered."""
    # Test that mcp is a FastMCP instance
    assert hasattr(mcp, "name")
    assert mcp.name == "Developer Guide MCP"

    # Test that tools are registered by checking the decorated functions exist
    # These are the actual @mcp.tool() decorated functions in server.py
    expected_tools = [
        "get_current_project",
        "switch_project",
        "list_projects",
        "get_project_config",
        "set_project_config",
        "get_effective_config",
        "get_tools",
        "set_tools",
        "get_guide",
        "get_language_guide",
        "get_project_context",
        "get_all_guides",
        "search_content",
        "show_guide",
        "show_language_guide",
        "show_project_summary",
        "list_files",
        "file_exists",
        "get_file_content",
        "save_session",
        "load_session",
        "reset_session",
    ]

    # Check that the functions exist in the server module
    from mcp_server_guide import server

    for tool_name in expected_tools:
        assert hasattr(server, tool_name), f"Tool {tool_name} not found in server module"


def test_tools_are_callable():
    """Test that tools are callable functions."""
    from mcp_server_guide.tools.config_tools import get_project_config
    from mcp_server_guide.tools.content_tools import get_guide
    from mcp_server_guide.tools.file_tools import list_files
    from mcp_server_guide.tools.project_tools import get_current_project
    from mcp_server_guide.tools.session_management import save_session

    # Test that functions are callable
    assert callable(get_project_config)
    assert callable(get_guide)
    assert callable(list_files)
    assert callable(get_current_project)
    assert callable(save_session)


def test_tools_return_expected_types():
    """Test that tools return expected types."""
    from mcp_server_guide.tools.config_tools import get_project_config
    from mcp_server_guide.tools.content_tools import get_guide
    from mcp_server_guide.tools.file_tools import list_files
    from mcp_server_guide.tools.project_tools import get_current_project
    from mcp_server_guide.tools.session_management import save_session

    # Test return types
    config = get_project_config()
    assert isinstance(config, dict)

    guide = get_guide()
    assert isinstance(guide, str)

    files = list_files("guide")
    assert isinstance(files, list)

    project = get_current_project()
    assert isinstance(project, str)

    session = save_session()
    assert isinstance(session, dict)


def test_tools_with_parameters():
    """Test tools with different parameters."""
    from mcp_server_guide.tools.config_tools import get_project_config, set_project_config
    from mcp_server_guide.tools.content_tools import get_guide, get_language_guide

    # Test with project parameter
    config = get_project_config("test_project")
    assert isinstance(config, dict)

    # Test set_project_config
    result = set_project_config("test_key", "test_value")
    assert isinstance(result, dict)

    # Test content tools with project
    guide = get_guide("test_project")
    assert isinstance(guide, str)

    lang_guide = get_language_guide("test_project")
    assert isinstance(lang_guide, str)


def test_file_tools_comprehensive():
    """Test file_tools functions comprehensively."""
    # Test list_files with different types
    result = list_files("guide")
    assert isinstance(result, list)

    result = list_files("lang", "test_project")
    assert isinstance(result, list)

    # Test file_exists - just call the function
    result = file_exists("test.txt")
    assert isinstance(result, bool)

    result = file_exists("nonexistent.txt")
    assert isinstance(result, bool)

    # Test get_file_content - just call the function
    result = get_file_content("test.txt")
    assert isinstance(result, str)


def test_project_tools_comprehensive():
    """Test project_tools functions comprehensively."""
    # Test get_current_project
    result = get_current_project()
    assert isinstance(result, str)

    # Test switch_project
    result = switch_project("test_project")
    assert isinstance(result, dict)

    # Test list_projects
    result = list_projects()
    assert isinstance(result, list)


def test_session_management_comprehensive():
    """Test session_management functions comprehensively."""
    # Test save_session
    result = save_session()
    assert isinstance(result, dict)

    # Test load_session
    result = load_session()
    assert isinstance(result, dict)

    # Test reset_session
    result = reset_session()
    assert isinstance(result, dict)


def test_content_tools_comprehensive():
    """Test content_tools functions comprehensively."""
    from mcp_server_guide.tools.content_tools import (
        get_guide,
        get_language_guide,
        get_project_context,
        get_all_guides,
        search_content,
        show_guide,
        show_language_guide,
        show_project_summary,
    )

    # Test all content tools
    result = get_guide("test_project")
    assert isinstance(result, str)

    result = get_language_guide("test_project")
    assert isinstance(result, str)

    result = get_project_context("test_project")
    assert isinstance(result, str)

    result = get_all_guides("test_project")
    assert isinstance(result, dict)

    result = search_content("test", "test_project")
    assert isinstance(result, list)

    result = show_guide("test_project")
    assert isinstance(result, dict)

    result = show_language_guide("test_project")
    assert isinstance(result, dict)

    result = show_project_summary("test_project")
    assert isinstance(result, dict)


def test_config_tools_comprehensive():
    """Test config_tools functions comprehensively."""
    from mcp_server_guide.tools.config_tools import (
        get_project_config,
        set_project_config,
        get_effective_config,
        get_tools,
        set_tools,
    )

    # Test all config tools
    result = get_project_config("test_project")
    assert isinstance(result, dict)

    result = set_project_config("test_key", "test_value", "test_project")
    assert isinstance(result, dict)
    assert result["success"] is True

    result = get_effective_config("test_project")
    assert isinstance(result, dict)

    result = get_tools("test_project")
    assert isinstance(result, list)

    result = set_tools(["tool1", "tool2"], "test_project")
    assert isinstance(result, dict)


def test_tools_error_handling():
    """Test tools error handling."""
    # Test file_exists - just call the function without mocking
    result = file_exists("error.txt")
    assert isinstance(result, bool)

    # Test get_file_content - just call the function without mocking
    result = get_file_content("error.txt")
    assert isinstance(result, str)
