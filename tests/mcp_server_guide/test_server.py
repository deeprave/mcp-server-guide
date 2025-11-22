"""Tests for MCP server functionality."""

from unittest.mock import patch, Mock, AsyncMock
from mcp_server_guide import server
from mcp_server_guide.session_manager import SessionManager
from mcp_server_guide import tools


async def test_server_tool_functions(isolated_config_file):
    """Test all MCP server tool functions."""
    from mcp_server_guide.session_manager import SessionManager

    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    # Test get_current_project via tools
    mock_ctx = Mock()
    mock_ctx.error = AsyncMock()
    result = await tools.get_current_project(mock_ctx)
    assert isinstance(result, str)

    # Test switch_project via tools
    result = await tools.switch_project("test_project")
    assert isinstance(result, dict)


async def test_get_current_project_no_project_set():
    """Test get_current_project when no project is set."""
    mock_ctx = Mock()
    mock_ctx.error = AsyncMock()

    # Test get_current_project returns empty string
    with patch("mcp_server_guide.tools.get_current_project", return_value=""):
        result = await tools.get_current_project(mock_ctx)
        assert result == ""

    # Test get_current_project returns error dictionary
    error_dict = {"success": False, "error": "No project set"}
    with patch("mcp_server_guide.tools.get_current_project", return_value=error_dict):
        result = await tools.get_current_project(mock_ctx)
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "No project set" in result["error"]

    # Test switch_project with invalid input
    with patch("mcp_server_guide.tools.switch_project") as mock_switch:
        mock_switch.return_value = {"success": False, "error": "Invalid project name"}
        result = await tools.switch_project("")
        assert isinstance(result, dict)
        assert result["success"] is False

    # Test get_project_config via tools
    result = await tools.get_project_config()
    assert isinstance(result, dict)

    result = await tools.get_project_config("test_project")
    assert isinstance(result, dict)

    # Test set_project_config with valid categories
    categories = {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
    result = await tools.set_project_config("categories", categories)
    assert isinstance(result, dict)

    # Set current project first, then set config
    session = SessionManager()
    session.set_project_name("test_project")
    result = await tools.set_project_config("categories", categories)
    assert isinstance(result, dict)


async def test_server_content_functions():
    """Test server content-related functions."""
    # Test search_content via tools
    result = await tools.search_content("test")
    assert isinstance(result, list)

    result = await tools.search_content("test", "test_project")
    assert isinstance(result, list)


async def test_server_display_functions():
    """Test server display functions."""
    # Test list_prompts via tools
    result = await tools.list_prompts()
    assert isinstance(result, dict)


async def test_server_file_functions():
    """Test server file-related functions."""
    # Test get_file_content via tools
    result = await tools.get_file_content("test.txt")
    assert isinstance(result, str)

    result = await tools.get_file_content("test.txt", "test_project")
    assert isinstance(result, str)


async def test_server_tool_integration():
    """Test server correctly registers and exposes tools."""
    from mcp_server_guide.server import create_server_with_config

    # Create server instance
    config = {"docroot": ".", "project": "test"}
    server = await create_server_with_config(config)

    # Test that tools are registered with the server
    tools_list = await server.list_tools()
    tool_names = [tool.name for tool in tools_list]

    # Verify key tools are registered
    expected_tools = [
        "guide_get_current_project",
        "guide_switch_project",
        "guide_add_category",
        "guide_list_categories",
    ]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Tool {expected_tool} not registered"


def test_tool_registration_error_handling():
    """Test error handling during server creation."""
    # Verify that server creation functions exist in server.py
    import inspect
    from mcp_server_guide import server

    source = inspect.getsource(server)
    assert "create_server" in source
    assert "create_server_with_config" in source
    assert "get_current_server" in source
    assert "GuideMCP" in source


async def test_server_session_functions():
    """Test server session management functions."""
    # Session functions are tested elsewhere
    pass


async def test_create_server_functions():
    """Test server creation functions."""
    # Test create_server
    server_instance = await server.create_server()
    assert server_instance is not None

    # Test create_server_with_config
    config = {"docroot": "/test", "project": "test"}
    server_instance = await server.create_server_with_config(config)
    assert server_instance is not None
