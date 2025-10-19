"""Test for guide://category/all resource handler."""

import pytest
from unittest.mock import patch
from mcp_server_guide.project_config import ProjectConfig, Category


@pytest.mark.asyncio
async def test_read_all_categories_resource_formats_content_as_markdown():
    """Test that guide://category/all resource formats content as markdown sections."""
    # Import here to test the actual resource handler logic
    from mcp_server_guide.server import _register_category_resources
    from mcp.server.fastmcp import FastMCP

    # Create a test server
    server = FastMCP(name="test")

    # Create ProjectConfig with auto_load categories
    config = ProjectConfig(
        categories={
            "guide": Category(
                dir="guide/",
                patterns=["*.md"],
                description="Development guidelines",
                auto_load=True,
            ),
            "context": Category(
                dir="context/",
                patterns=["*.md"],
                description="Project context",
                auto_load=True,
            ),
            "lang": Category(
                dir="lang/",
                patterns=["*.md"],
                description="Language guidelines",
                auto_load=False,  # Should not be included
            ),
        }
    )

    # Mock get_all_guides to return expected dict format
    async def mock_get_all_guides_impl(project):
        return {
            "guide": "# Guide Content\n\nThis is the guide.",
            "context": "# Context Content\n\nThis is the context.",
        }

    with patch("mcp_server_guide.tools.content_tools.get_all_guides", side_effect=mock_get_all_guides_impl):
        # Register the resources
        await _register_category_resources(server, config)

        # Find the registered resource handler for "guide://category/all"
        resource_uri = "guide://category/all"
        resource_handler = None
        for uri, func_resource in server._resource_manager._resources.items():
            if str(uri) == resource_uri:
                resource_handler = func_resource.fn
                break

        assert resource_handler is not None, "Resource handler not found"

        # Call the resource handler
        result = await resource_handler()

        # Should format as markdown sections with category headers
        assert "# guide" in result
        assert "# Guide Content" in result
        assert "This is the guide." in result
        assert "# context" in result
        assert "# Context Content" in result
        assert "This is the context." in result


@pytest.mark.asyncio
async def test_read_all_categories_resource_handles_empty_result():
    """Test that guide://category/all resource handles empty dict gracefully."""
    from mcp_server_guide.server import _register_category_resources
    from mcp.server.fastmcp import FastMCP

    server = FastMCP(name="test")

    # Create ProjectConfig with auto_load categories
    config = ProjectConfig(
        categories={
            "guide": Category(
                dir="guide/",
                patterns=["*.md"],
                description="Development guidelines",
                auto_load=True,
            ),
        }
    )

    # Mock get_all_guides to return empty dict
    async def mock_get_all_guides_impl(project):
        return {}

    with patch("mcp_server_guide.tools.content_tools.get_all_guides", side_effect=mock_get_all_guides_impl):
        # Register the resources
        await _register_category_resources(server, config)

        # Find the registered resource handler
        resource_uri = "guide://category/all"
        resource_handler = None
        for uri, func_resource in server._resource_manager._resources.items():
            if str(uri) == resource_uri:
                resource_handler = func_resource.fn
                break

        assert resource_handler is not None, "Resource handler not found"

        # Call the resource handler - should return empty string, not raise
        result = await resource_handler()
        assert result == ""


@pytest.mark.asyncio
async def test_read_all_categories_resource_handles_exception():
    """Test that guide://category/all resource handles exceptions properly."""
    from mcp_server_guide.server import _register_category_resources
    from mcp.server.fastmcp import FastMCP

    server = FastMCP(name="test")

    # Create ProjectConfig with auto_load categories
    config = ProjectConfig(
        categories={
            "guide": Category(
                dir="guide/",
                patterns=["*.md"],
                description="Development guidelines",
                auto_load=True,
            ),
        }
    )

    # Mock get_all_guides to raise an exception
    async def mock_get_all_guides_impl(project):
        raise Exception("Test error")

    with patch("mcp_server_guide.tools.content_tools.get_all_guides", side_effect=mock_get_all_guides_impl):
        # Register the resources
        await _register_category_resources(server, config)

        # Find the registered resource handler
        resource_uri = "guide://category/all"
        resource_handler = None
        for uri, func_resource in server._resource_manager._resources.items():
            if str(uri) == resource_uri:
                resource_handler = func_resource.fn
                break

        assert resource_handler is not None, "Resource handler not found"

        # Call the resource handler - should propagate exception
        with pytest.raises(Exception, match="Test error"):
            await resource_handler()
