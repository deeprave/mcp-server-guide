"""MCP server creation and management."""

from typing import Dict, Any, Optional
from collections.abc import Mapping

from mcp.server.fastmcp import FastMCP

from .server_extensions import ServerExtensions
from .server_lifecycle import server_lifespan
from .logging_config import get_logger
from .tool_decoration import log_tool_usage
from .naming import mcp_name, MCP_GUIDE_VERSION
from .file_cache import FileCache
from .file_source import FileSource, FileAccessor, FileSourceType

logger = get_logger()


class GuideMCP(FastMCP):
    """MCP server with guide extensions."""

    def __init__(
        self,
        name: str,
        project: Optional[str] = None,
        docroot: Optional[str] = None,
        config_file: Optional[str] = None,
        lifespan: Optional[Any] = None,
        *args: Any,
        **kwargs: Any,
    ):
        # Extract lifespan from kwargs if present
        if lifespan is not None:
            kwargs["lifespan"] = lifespan
        super().__init__(name, *args, **kwargs)
        self.ext: ServerExtensions  # Will be assigned during server creation
        self.project = project
        self.docroot = docroot
        self.config_file = config_file


def create_server(
    name: Optional[str] = None,
    version: Optional[str] = None,
    docroot: Optional[str] = None,
    project: Optional[str] = None,
    config_file: Optional[str] = None,
    log_level: str = "INFO",
    **kwargs: Any,
) -> GuideMCP:
    """Create and configure the MCP server."""

    # Import here to avoid circular imports
    from .session_manager import SessionManager
    from .prompts import register_prompts
    from .tool_registry import register_tools
    from .tools import get_category_content

    # Use dynamic defaults
    actual_name = name or mcp_name()
    actual_version = version or MCP_GUIDE_VERSION

    # Configure logging
    if log_level:
        from .logging_config import setup_logging

        setup_logging(log_level)

    # Create GuideMCP server
    server = GuideMCP(
        name=actual_name, project=project, docroot=docroot, config_file=config_file, lifespan=server_lifespan
    )

    # Create file accessor for compatibility with tests
    cache_dir = kwargs.get("cache_dir")
    cache = FileCache(cache_dir) if cache_dir else FileCache()
    file_accessor = FileAccessor(cache=cache)

    # Add missing methods for compatibility (from original server.py)
    async def _get_file_source(config_key: str, project_context: str) -> FileSource:
        """Get file source for a configuration key."""

        if hasattr(server, "ext") and server.ext._session_manager is not None:
            await server.ext._session_manager.get_or_create_project_config(project_context)
        else:
            # Fallback to default config
            session_manager = SessionManager()
            await session_manager.get_or_create_project_config(project_context)

        # Map config_key to category names for unified system
        category_mapping = {"guide": "guide", "language": "lang", "context": "context"}
        category_name = category_mapping.get(config_key, config_key)

        # Try to get category content first
        try:
            result = await get_category_content(category_name, project_context)
            if result.get("is_http") and result.get("url"):
                return FileSource(FileSourceType.HTTP, result["url"])
            # For file categories, return file source
            return FileSource(FileSourceType.FILE, result.get("path", "."))
        except Exception:
            pass

        # Fallback to old behavior if category doesn't exist
        fallback_source = FileSource(FileSourceType.FILE, ".")
        return fallback_source

    async def _read_category_content(category_name: str, project_context: str = "") -> str:
        """Common helper for reading category content."""
        try:
            result = await get_category_content(category_name, project_context)
            if result.get("is_http") and result.get("url"):
                source = FileSource(FileSourceType.HTTP, result["url"])
                content = await server.ext.file_accessor.read_file("", source)
                return str(content)
            return str(result.get("content", ""))
        except Exception:
            pass

        # Fallback to old behavior
        config_key = "guide" if category_name == "guide" else "language"
        source = await _get_file_source(config_key, project_context)
        content = await server.ext.file_accessor.read_file("", source)
        return str(content)

    async def read_guide(project_context: str = "") -> str:
        """Read guide content for a project context."""
        return await _read_category_content("guide", project_context)

    async def read_language(project_context: str = "") -> str:
        """Read language content for a project context."""
        return await _read_category_content("lang", project_context)

    # Create extensions object with all server additions
    extensions = ServerExtensions(
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

    # Register tools using the server
    register_tools(server, log_tool_usage)

    # Log server creation with actual version
    logger.info(f"Created MCP server: {actual_name} v{actual_version}")

    return server


def create_server_with_config(config: Dict[str, Any]) -> GuideMCP:
    """Create server with configuration dictionary."""
    if not isinstance(config, Mapping):
        raise TypeError("Config must be a mapping (e.g., dict)")
    return create_server(**config)


# Create a default server instance for backward compatibility
mcp: Optional[GuideMCP] = None
try:
    mcp = create_server()
except Exception as e:
    logger.error(f"Failed to create server: {e}")
    mcp = None  # Allow module to be imported even if server creation fails
