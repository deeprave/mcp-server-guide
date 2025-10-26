"""Tests for MCP server functionality."""

from unittest.mock import patch
from mcp_server_guide import server
from mcp_server_guide.session_manager import SessionManager


async def test_server_tool_functions(isolated_config_file):
    """Test all MCP server tool functions."""
    from mcp_server_guide.session_manager import SessionManager

    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    # Test get_current_project
    result = await server.get_current_project()
    assert isinstance(result, dict)
    # Assert expected keys in the returned dict
    assert "success" in result
    if result["success"]:
        assert "project" in result

    # Test switch_project
    result = await server.switch_project("test_project")
    assert isinstance(result, dict)


async def test_get_current_project_no_project_set():
    """Test get_current_project when no project is set."""
    with patch("mcp_server_guide.server.tools.get_current_project", return_value=None):
        result = await server.get_current_project()
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "No project set" in result["error"]

    # Test get_project_config
    result = await server.get_project_config()
    assert isinstance(result, dict)

    result = await server.get_project_config("test_project")
    assert isinstance(result, dict)

    # Test set_project_config with valid categories
    categories = {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
    result = await server.set_project_config("categories", categories)
    assert isinstance(result, dict)

    # Set current project first, then set config
    session = SessionManager()
    session.set_project_name("test_project")
    result = await server.set_project_config("categories", categories)
    assert isinstance(result, dict)


async def test_server_content_functions():
    """Test server content-related functions."""
    # Test get_guide
    result = await server.get_guide()
    assert isinstance(result, str)

    result = await server.get_guide("test_project")
    assert isinstance(result, str)

    # Test get_language_guide
    result = await server.get_language_guide()
    assert isinstance(result, str)

    result = await server.get_language_guide("test_project")
    assert isinstance(result, str)

    # Test get_project_context
    result = await server.get_project_context()
    assert isinstance(result, str)

    result = await server.get_project_context("test_project")
    assert isinstance(result, str)

    # Test search_content
    result = await server.search_content("test")
    assert isinstance(result, list)

    result = await server.search_content("test", "test_project")
    assert isinstance(result, list)

    # Test search_content
    result = await server.search_content("test")
    assert isinstance(result, list)

    result = await server.search_content("test", "test_project")
    assert isinstance(result, list)


async def test_server_display_functions():
    """Test server display functions."""
    # Test show_guide
    result = await server.show_guide()
    assert isinstance(result, dict)

    result = await server.show_guide("test_project")
    assert isinstance(result, dict)

    # Test show_language_guide
    result = await server.show_language_guide()
    assert isinstance(result, dict)

    result = await server.show_language_guide("test_project")
    assert isinstance(result, dict)

    # Test list_prompts
    result = await server.list_prompts()
    assert isinstance(result, dict)


async def test_server_file_functions():
    """Test server file-related functions."""
    # Test get_file_content
    result = await server.get_file_content("test.txt")
    assert isinstance(result, str)

    result = await server.get_file_content("test.txt", "test_project")
    assert isinstance(result, str)


async def test_server_session_functions():
    """Test server session management functions."""
    # Session functions are tested elsewhere
    pass


async def test_create_server_functions():
    """Test server creation functions."""
    # Test create_server
    server_instance = server.create_server()
    assert server_instance is not None

    # Test create_server_with_config
    config = {"docroot": "/test", "project": "test"}
    server_instance = server.create_server_with_config(config)
    assert server_instance is not None
