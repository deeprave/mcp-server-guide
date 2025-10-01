"""Tests for MCP server functionality."""

from mcp_server_guide import server


async def test_server_tool_functions():
    """Test all MCP server tool functions."""
    # Test get_current_project
    result = server.get_current_project()
    assert isinstance(result, str)

    # Test switch_project
    result = await server.switch_project("test_project")
    assert isinstance(result, dict)

    # Test list_projects
    result = server.list_projects()
    assert isinstance(result, list)

    # Test get_project_config
    result = server.get_project_config()
    assert isinstance(result, dict)

    result = server.get_project_config("test_project")
    assert isinstance(result, dict)

    # Test set_project_config
    result = await server.set_project_config("test_key", "test_value")
    assert isinstance(result, dict)

    result = await server.set_project_config("test_key", "test_value", "test_project")
    assert isinstance(result, dict)

    # Test get_effective_config
    result = server.get_effective_config()
    assert isinstance(result, dict)

    result = server.get_effective_config("test_project")
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

    # Test get_all_guides
    result = await server.get_all_guides()
    assert isinstance(result, dict)

    result = await server.get_all_guides("test_project")
    assert isinstance(result, dict)

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

    # Test show_project_summary
    result = await server.show_project_summary()
    assert isinstance(result, dict)

    result = await server.show_project_summary("test_project")
    assert isinstance(result, dict)


async def test_server_file_functions():
    """Test server file-related functions."""
    # Test list_files
    result = server.list_files("guide")
    assert isinstance(result, list)

    result = server.list_files("guide", "test_project")
    assert isinstance(result, list)

    # Test file_exists
    result = server.file_exists("test.txt")
    assert isinstance(result, bool)

    result = server.file_exists("test.txt", "test_project")
    assert isinstance(result, bool)

    # Test get_file_content
    result = await server.get_file_content("test.txt")
    assert isinstance(result, str)

    result = await server.get_file_content("test.txt", "test_project")
    assert isinstance(result, str)


async def test_server_session_functions():
    """Test server session management functions."""
    # Test save_session
    result = await server.save_session()
    assert isinstance(result, dict)

    # Test load_session
    result = server.load_session()
    assert isinstance(result, dict)

    result = server.load_session("/test/path")
    assert isinstance(result, dict)

    # Test reset_session
    result = server.reset_session()
    assert isinstance(result, dict)


async def test_create_server_functions():
    """Test server creation functions."""
    # Test create_server
    server_instance = server.create_server()
    assert server_instance is not None

    # Test create_server_with_config
    config = {"docroot": "/test", "project": "test"}
    server_instance = server.create_server_with_config(config)
    assert server_instance is not None
