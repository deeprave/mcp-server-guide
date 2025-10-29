"""Server lifecycle management for MCP server."""

from typing import Any
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP
from .session_manager import SessionManager
from .logging_config import get_logger
from .error_handler import ErrorHandler
from .resource_registry import register_resources
from .prompts import register_prompts
from .tool_registry import register_tools
from .tool_decoration import log_tool_usage, ExtMcpToolDecorator

logger = get_logger()
error_handler = ErrorHandler(logger)


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> Any:
    """Manage server lifecycle with proper startup and shutdown."""
    import os

    logger.info("=== Starting MCP server initialization ===")
    logger.info("Starting MCP Server Guide...")

    # Validate PWD environment variable
    if not os.environ.get("PWD"):
        raise ValueError("PWD environment variable not set")

    try:
        session_manager = SessionManager()

        # Extract project name from PWD
        pwd = os.environ.get("PWD", "")
        project_name = os.path.basename(pwd) if pwd else None

        config = await session_manager.get_or_create_project_config(project_name or "default")
        logger.info(
            f"Loaded configuration with {len(config.categories)} categories and {len(config.collections)} collections"
        )

        await register_resources(server, config)

        register_prompts(server)

        # Use the existing guide decorator from server extensions
        if hasattr(server, "ext") and hasattr(server.ext, "guide"):
            register_tools(server, server.ext.guide, log_tool_usage)
        else:
            # Fallback for servers without extensions (shouldn't happen in normal use)
            register_tools(server, ExtMcpToolDecorator(server, prefix="guide_"), log_tool_usage)

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
