"""Server lifecycle management for MCP server."""

from typing import Any
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP
from .session_manager import SessionManager
from .logging_config import get_logger
from .utils.error_handler import ErrorHandler
from .resource_registry import register_resources
from .prompts import register_prompts

logger = get_logger()
error_handler = ErrorHandler()


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> Any:
    """Manage server lifecycle with proper startup and shutdown."""
    import os

    logger.info("Starting MCP Server Guide...")

    # Validate PWD environment variable
    if not os.environ.get("PWD"):
        raise ValueError("PWD environment variable not set")

    try:
        session_manager = SessionManager()

        # Apply server configuration parameters in correct order if this is a GuideMCP instance
        try:
            config_file = getattr(server, "config_file", None)
            project = getattr(server, "project", None)
            docroot = getattr(server, "docroot", None)

            if config_file or project or docroot:
                # 1. Set config file first (affects where project config is loaded from)
                if config_file:
                    session_manager._config_manager.set_config_filename(config_file)

                # 2. Switch project second (loads project config from the config file)
                if project and isinstance(project, str):
                    await session_manager.switch_project(project)
                    project_name = project
                else:
                    # Extract project name from PWD as fallback
                    pwd = os.environ.get("PWD", "")
                    project_name = os.path.basename(pwd) if pwd else "default"

                # 3. Set docroot last (part of main config, not project config)
                if docroot:
                    from .path_resolver import LazyPath

                    # Set docroot at config manager level since it's part of main config
                    session_manager._config_manager._docroot = LazyPath(docroot)
            else:
                # Extract project name from PWD
                pwd = os.environ.get("PWD", "")
                project_name = os.path.basename(pwd) if pwd else "default"
        except Exception as e:
            logger.error(f"Failed to apply server parameters: {e}")
            raise RuntimeError(f"Server parameter application failed: {e}") from e

        config = await session_manager.get_or_create_project_config(project_name or "default")
        logger.info(f"Loaded configuration: {len(config.categories)} categories, {len(config.collections)} collections")

        await register_resources(server, config)

        register_prompts(server)

        # Tools are already registered in create_server() - no need to register again here

        logger.info("MCP server initialized successfully")
        yield

    except Exception as e:
        logger.error(f"Error during server startup: {e}")
        raise
    finally:
        logger.info("MCP server shutting down")
        try:
            if "session_manager" in locals() and hasattr(session_manager, "cleanup"):
                await session_manager.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        logger.info("MCP Server Guide shutdown complete")
