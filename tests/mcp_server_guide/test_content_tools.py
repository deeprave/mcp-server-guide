"""Tests for content tools functionality."""

from mcp_server_guide.tools.content_tools import (
    search_content,
)


async def test_search_content_basic():
    """Test basic search content functionality."""
    # Test that search_content returns expected types
    result = await search_content("test query")
    assert isinstance(result, list)


async def test_search_content_with_project():
    """Test search_content with specific project."""
    result = await search_content("test query", "test_project")
    assert isinstance(result, list)


async def test_search_content_edge_cases():
    """Test search_content with edge case inputs."""
    # Test with empty query
    result = await search_content("")
    assert isinstance(result, list)

    # Test with None project
    result = await search_content("test", None)
    assert isinstance(result, list)
