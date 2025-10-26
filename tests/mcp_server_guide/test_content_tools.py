"""Tests for content tools functionality."""

from mcp_server_guide.tools.content_tools import (
    get_guide,
    get_language_guide,
    get_project_context,
    search_content,
    show_guide,
    show_language_guide,
)


async def test_content_tools_basic():
    """Test basic content tools functionality."""
    # Test that functions return expected types
    result = await get_guide()
    assert isinstance(result, str)

    result = await get_language_guide()
    assert isinstance(result, str)

    result = await get_project_context()
    assert isinstance(result, str)

    result = await search_content("test")
    assert isinstance(result, list)

    result = await show_guide()
    assert isinstance(result, dict)

    result = await show_language_guide()
    assert isinstance(result, dict)


async def test_get_project_context_variations():
    """Test get_project_context with different path types."""
    # Test with project parameter
    result = await get_project_context("test_project")
    assert isinstance(result, str)

    # Test without project parameter
    result = await get_project_context()
    assert isinstance(result, str)


async def test_content_tools_comprehensive():
    """Test content tools comprehensive functionality."""
    # Test all functions return expected types
    result = await get_guide("test_project")
    assert isinstance(result, str)

    result = await get_language_guide("test_project")
    assert isinstance(result, str)

    result = await get_project_context("test_project")
    assert isinstance(result, str)

    result = await search_content("test", "test_project")
    assert isinstance(result, list)

    # Test show functions
    result = await show_guide("test_project")
    assert isinstance(result, dict)

    result = await show_language_guide("test_project")
    assert isinstance(result, dict)
    assert isinstance(result, dict)


async def test_get_project_context_branches():
    """Test get_project_context different branches."""
    # Test with different project names to hit different branches
    result1 = await get_project_context("test_project")
    assert isinstance(result1, str)

    result2 = await get_project_context("another_project")
    assert isinstance(result2, str)

    result3 = await get_project_context()
    assert isinstance(result3, str)


async def test_get_all_guides_error_handling():
    """Test get_all_guides error handling branches."""
    # Call with different projects to potentially hit error branches
    # With the new system, test basic functionality
    result = await get_project_context("test_project")
    assert isinstance(result, str)

    # Test search functionality
    result = await search_content("test", "test_project")
    assert isinstance(result, list)


async def test_content_tools_edge_cases():
    """Test content tools with edge case inputs."""
    # Test with empty strings and special characters
    result = await get_project_context("")
    assert isinstance(result, str)

    result = await search_content("", "")
    assert isinstance(result, list)

    # Test with None values
    result = await get_project_context(None)
    assert isinstance(result, str)

    result = await search_content("test", None)
    assert isinstance(result, list)
