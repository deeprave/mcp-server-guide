"""MCP server creation and management."""

import asyncio
from typing import Dict, Any, Optional, List
from collections.abc import Mapping

from mcp.server.fastmcp import FastMCP

from .server_extensions import ServerExtensions
from .server_lifecycle import server_lifespan
from .logging_config import get_logger
from .tool_decoration import log_tool_usage
from .naming import mcp_name, MCP_GUIDE_VERSION
from .file_cache import FileCache
from .file_source import FileAccessor
from .session_manager import SessionManager
from .tool_registry import register_tools

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
        self.extensions: ServerExtensions  # Will be assigned during server creation
        self.project = project
        self.docroot = docroot
        self.config_file = config_file

    def get_registered_prompts(self) -> List[Any]:
        """Get list of registered prompts from this server instance."""
        return self._prompt_manager.list_prompts()

    def get_registered_tools(self) -> List[Any]:
        """Get list of registered tools from this server instance."""
        return list(self._tool_manager.list_tools())

    def get_registered_resources(self) -> List[Any]:
        """Get list of registered resources from this server instance."""
        return list(self._resource_manager.list_resources())

    async def cleanup(self) -> None:
        """Clean up server resources."""
        try:
            # Clean up extensions if they have cleanup methods
            if hasattr(self.extensions, "_session_manager") and hasattr(self.extensions._session_manager, "cleanup"):
                await self.extensions._session_manager.cleanup()

            if hasattr(self.extensions, "file_accessor") and hasattr(self.extensions.file_accessor, "cleanup"):
                await self.extensions.file_accessor.cleanup()

        except Exception as e:
            logger.error(f"Error during server cleanup: {e}")

    async def __aenter__(self) -> "GuideMCP":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit with cleanup."""
        await self.cleanup()


async def create_server(
    name: Optional[str] = None,
    version: Optional[str] = None,
    docroot: Optional[str] = None,
    project: Optional[str] = None,
    config_file: Optional[str] = None,
    log_level: str = "INFO",
    **kwargs: Any,
) -> GuideMCP:
    """Create and configure the MCP server (async version)."""

    # Use dynamic defaults
    actual_name = name or mcp_name()
    actual_version = version or MCP_GUIDE_VERSION

    # Configure logging - handled by main.py setup_consolidated_logging
    # Removed redundant setup_logging call that was overriding file logging

    # Create GuideMCP server
    server = GuideMCP(
        name=actual_name, project=project, docroot=docroot, config_file=config_file, lifespan=server_lifespan
    )

    # Create file accessor
    cache_dir = kwargs.get("cache_dir")
    cache = FileCache(cache_dir) if cache_dir else FileCache()
    file_accessor = FileAccessor(cache=cache)

    # Create extensions object with all server additions
    extensions = ServerExtensions(
        _session_manager=SessionManager(),
        file_accessor=file_accessor,
    )

    # Single setattr to add all extensions
    server.extensions = extensions

    # Set as current server
    set_current_server(server)

    # Register tools using the server with duplicate protection
    await server.extensions.register_tools_once(server, lambda srv: register_tools(srv, log_tool_usage))

    # Log server creation with the actual version
    logger.info(f"Created MCP server: {actual_name} v{actual_version}")

    return server


async def create_server_with_config(config: Dict[str, Any]) -> GuideMCP:
    """Create server with configuration dictionary (async version)."""
    if not isinstance(config, Mapping):
        raise TypeError("Config must be a mapping (e.g., dict)")
    return await create_server(**config)


# Global server instance and config (singleton)
_current_server: Optional[GuideMCP] = None
_current_config: Optional[Dict[str, Any]] = None
_server_lock = asyncio.Lock()


async def get_current_server() -> Optional[GuideMCP]:
    """Get the current server instance, creating it if needed."""
    global _current_server, _current_config

    if _current_server is not None:
        return _current_server

    async with _server_lock:
        # Double-check pattern
        if _current_server is None and _current_config is not None:
            _current_server = await create_server_with_config(_current_config)

    return _current_server


def set_current_server(server: GuideMCP) -> None:
    """Set the current server instance."""
    global _current_server
    _current_server = server


def set_current_config(config: Dict[str, Any]) -> None:
    """Set the current config for lazy server creation."""
    global _current_config
    _current_config = config


def reset_server_state() -> None:
    """Reset global server state (for testing purposes)."""
    global _current_server, _current_config
    _current_server = None
    _current_config = None
