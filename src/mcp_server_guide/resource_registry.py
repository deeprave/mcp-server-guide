"""Resource registration for MCP server."""

from typing import TYPE_CHECKING, Callable, Awaitable

from mcp.server.fastmcp import FastMCP

from .logging_config import get_logger
from .models.collection import Collection
from .models.category import Category
from .tools.category_tools import get_category_content
from .tools.collection_tools import get_collection_content
from .help_system import format_guide_help

if TYPE_CHECKING:
    from .project_config import ProjectConfig


logger = get_logger()


async def register_resources(server: FastMCP, config: "ProjectConfig") -> None:
    """Register all dynamic resources for the MCP server."""
    await _register_category_resources(server, config)
    await _register_help_resource(server)


async def _register_category_resources(server: FastMCP, config: "ProjectConfig") -> None:
    """Register dynamic resources for categories and collections."""

    def make_category_reader(cat_name: str, cat_config: Category) -> Callable[[], Awaitable[str]]:
        desc = cat_config.description
        if desc is None or (isinstance(desc, str) and not desc.strip()):
            desc = cat_name

        @server.resource(f"guide://category/{cat_name}", name=cat_name, description=desc, mime_type="text/markdown")
        async def read_category() -> str:
            """Get content for a specific category."""
            result = await get_category_content(cat_name)
            if result.get("success"):
                return str(result.get("content", ""))
            raise ValueError(f"Failed to load category '{cat_name}': {result.get('error', 'Unknown error')}")

        return read_category

    def make_collection_reader(coll_name: str, coll_config: Collection) -> Callable[[], Awaitable[str]]:
        desc = coll_config.description
        if desc is None or (isinstance(desc, str) and not desc.strip()):
            desc = coll_name

        @server.resource(f"guide://collection/{coll_name}", name=coll_name, description=desc, mime_type="text/markdown")
        async def read_collection() -> str:
            try:
                result = await get_collection_content(coll_name)
                if result.get("success"):
                    return str(result.get("content", ""))
                else:
                    return f"Error loading collection '{coll_name}': {result.get('error', 'Unknown error')}"
            except Exception as e:
                logger.error(f"Error in collection reader for '{coll_name}': {e}")
                return f"Error loading collection '{coll_name}': {str(e)}"

        return read_collection

    resource_count = 0
    for category_name, category_config in config.categories.items():
        make_category_reader(category_name, category_config)
        logger.debug(f"Registered resource: guide://category/{category_name}")
        resource_count += 1

    for collection_name, collection_config in config.collections.items():
        make_collection_reader(collection_name, collection_config)
        logger.debug(f"Registered resource: guide://collection/{collection_name}")
        resource_count += 1

    logger.info(f"Registered {resource_count} resources")


async def _register_help_resource(server: FastMCP) -> None:
    """Register help resource."""

    @server.resource("guide://help", name="help", description="MCP Server Guide Help", mime_type="text/markdown")
    async def read_help() -> str:
        """Get comprehensive help content for the guide system."""
        result = await format_guide_help()
        return str(result)
