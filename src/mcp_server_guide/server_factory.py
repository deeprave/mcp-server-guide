"""Server factory for creating MCP server instances."""

from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP

from .file_cache import FileCache
from .file_source import FileSource, FileAccessor, FileSourceType
from .logging_config import get_logger
from .prompts import register_prompts
from .server_extensions import ServerExtensions
from .server_lifecycle import server_lifespan
from .session_manager import SessionManager
from .tool_decoration import ExtMcpToolDecorator
from .tools import get_category_content

logger = get_logger()


def create_server(
    name: str = "mcp-server-guide",
    version: str = "0.5.0",
    description: str = "Developer guidelines and project rules MCP server",
    docroot: Optional[str] = None,
    project: Optional[str] = None,
    config_file: Optional[str] = None,
    log_level: str = "INFO",
    **kwargs: Any,
) -> FastMCP:
    """Create and configure the MCP server."""

    # Create FastMCP server with only the parameters it expects
    server = FastMCP(name=name, lifespan=server_lifespan)

    # Create file accessor for compatibility with tests
    file_source = FileSource(type=FileSourceType.FILE, base_path=".")
    cache_dir = kwargs.get("cache_dir")
    cache = FileCache(cache_dir) if cache_dir else FileCache()
    file_accessor = FileAccessor(cache=cache)

    # Add missing methods for compatibility (from original server.py)
    async def _get_file_source(config_key: str, project_context: str) -> FileSource:
        """Get file source for a configuration key."""

        if hasattr(server, "ext") and server.ext._session_manager is not None:  # type: ignore[attr-defined]
            await server.ext._session_manager.get_or_create_project_config(project_context)  # type: ignore[attr-defined]
        else:
            # Fallback to default config
            session_manager = SessionManager()
            await session_manager.get_or_create_project_config(project_context)

        # Map config_key to category names for unified system
        category_mapping = {"guide": "guide", "language": "lang", "context": "context"}

        category = category_mapping.get(config_key)
        if category:
            # Use category system to get content
            result = await get_category_content(category, project_context)
            if result.get("success"):
                # Check if this is an HTTP-based category
                if result.get("is_http") and result.get("url"):
                    return FileSource(FileSourceType.HTTP, result["url"])
                # Otherwise it's a file-based category
                elif result.get("search_dir"):
                    return FileSource(FileSourceType.FILE, result["search_dir"])

        # Fallback to default file source
        return file_source

    async def read_guide(project_context: str) -> str:
        """Read guide content using hybrid file access."""

        # Try to get content from guide category
        result = await get_category_content("guide", project_context)
        if result.get("success"):
            # For HTTP categories, fetch using HTTP client
            if result.get("is_http") and result.get("url"):
                source = FileSource(FileSourceType.HTTP, result["url"])
                content = await server.ext.file_accessor.read_file("", source)  # type: ignore[attr-defined]
                return str(content)
            # For file categories, content is already read
            elif result.get("content") is not None:
                return str(result["content"])

        # Fallback to old behavior if category doesn't exist
        source = await _get_file_source("guide", project_context)
        content = await server.ext.file_accessor.read_file("", source)  # type: ignore[attr-defined]
        return str(content)

    async def read_language(project_context: str) -> str:
        """Read language content using hybrid file access."""

        # Try to get content from lang category
        result = await get_category_content("lang", project_context)
        if result.get("success"):
            # For HTTP categories, fetch using HTTP client
            if result.get("is_http") and result.get("url"):
                source = FileSource(FileSourceType.HTTP, result["url"])
                content = await server.ext.file_accessor.read_file("", source)  # type: ignore[attr-defined]
                return str(content)
            # For file categories, content is already read
            elif result.get("content") is not None:
                return str(result["content"])

        # Fallback to old behavior if category doesn't exist
        source = await _get_file_source("language", project_context)
        content = await server.ext.file_accessor.read_file("", source)  # type: ignore[attr-defined]
        return str(content)

    # Create extensions object with all server additions
    extensions = ServerExtensions(
        guide=ExtMcpToolDecorator(server, prefix="guide_"),
        _session_manager=SessionManager(),
        file_accessor=file_accessor,
        _get_file_source=_get_file_source,
        read_guide=read_guide,
        read_language=read_language,
    )

    # Single setattr to add all extensions
    setattr(server, "ext", extensions)

    # Register prompts immediately for test compatibility
    register_prompts(server)

    # Register tools using the extensions
    from .tool_registry import register_tools
    from .tool_decoration import log_tool_usage

    register_tools(server, extensions.guide, log_tool_usage)

    logger.info(f"Created MCP server: {name} v{version}")
    return server


def create_server_with_config(config: Dict[str, Any]) -> FastMCP:
    """Create server with configuration dictionary."""
    if not hasattr(config, "items"):
        raise AttributeError("Config must be a dictionary-like object")
    return create_server(**config)
