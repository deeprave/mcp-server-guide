from typing import Optional

from mcp.server.fastmcp import FastMCP

from .server_factory import create_server, create_server_with_config
from .server_lifecycle import server_lifespan
from .tool_decoration import log_tool_usage, ExtMcpToolDecorator
from .logging_config import get_logger
from .session_manager import SessionManager

# Export logger for test compatibility
logger = get_logger()

# Create a default server instance for backward compatibility
mcp: Optional[FastMCP] = None
try:
    mcp = create_server()
except Exception as e:
    logger.error(f"Failed to create server: {e}")

# Export guide decorator instance for test compatibility
guide = getattr(mcp.ext, "guide", None) if mcp and hasattr(mcp, "ext") else None

__all__ = [
    "create_server",
    "create_server_with_config",
    "server_lifespan",
    "log_tool_usage",
    "ExtMcpToolDecorator",
    "SessionManager",
    "logger",
    "guide",
    "mcp",
    "FastMCP",
]
