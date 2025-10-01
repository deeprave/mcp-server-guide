"""Tests for content tools functionality."""

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


async def test_content_tools_basic():
    """Test basic content tools functionality."""
    # Test that functions return expected types
    result = await get_guide()
    assert isinstance(result, str)

    result = await get_language_guide()
    assert isinstance(result, str)

    result = await get_project_context()
    assert isinstance(result, str)

    result = await get_all_guides()
    assert isinstance(result, dict)

    result = await search_content("test")
    assert isinstance(result, list)

    result = await show_guide()
    assert isinstance(result, dict)

    result = await show_language_guide()
    assert isinstance(result, dict)

    result = await show_project_summary()
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

    result = await get_all_guides("test_project")
    assert isinstance(result, dict)

    result = await search_content("test", "test_project")
    assert isinstance(result, list)

    # Test show functions
    result = await show_guide("test_project")
    assert isinstance(result, dict)

    result = await show_language_guide("test_project")
    assert isinstance(result, dict)

    result = await show_project_summary("test_project")
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
    result1 = await get_all_guides("test_project")
    assert isinstance(result1, dict)

    result2 = await get_all_guides("nonexistent_project")
    assert isinstance(result2, dict)

    result3 = await get_all_guides()
    assert isinstance(result3, dict)

    # With the new auto_load system, results may be empty if no categories have auto_load: true
    # This is expected behavior - the function should return empty dict if no auto_load categories exist


async def test_content_tools_edge_cases():
    """Test content tools with edge case inputs."""
    # Test with empty strings and special characters
    result = await get_project_context("")
    assert isinstance(result, str)

    result = await get_all_guides("")
    assert isinstance(result, dict)

    result = await search_content("", "")
    assert isinstance(result, list)

    # Test with None values
    result = await get_project_context(None)
    assert isinstance(result, str)

    result = await get_all_guides(None)
    assert isinstance(result, dict)


async def test_get_all_guides_individual_errors():
    """Test get_all_guides with individual category errors."""
    # This test is no longer relevant since get_all_guides now uses auto_load system
    # and only loads categories with auto_load: true. Error handling is tested in
    # test_get_all_guides_auto_load.py
    pass
