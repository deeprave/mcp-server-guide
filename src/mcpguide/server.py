"""MCP server for developer guidelines and project rules with session support."""

from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from .session import resolve_session_path
from .session_tools import SessionManager

mcp = FastMCP(name="Developer Guide MCP")

defaults = {
    "guide": "./guide/",
    "project": "./project/",
    "lang": "./lang/",
}


def create_server_with_config(config: Dict[str, Any]) -> FastMCP:
    """Create MCP server instance with session-aware configuration."""
    server = FastMCP(name="Developer Guide MCP")

    # Get session manager
    session_manager = SessionManager()

    # Get session config for current project
    session_config = session_manager.session_state.get_project_config(session_manager.current_project)

    # Start with provided config
    merged_config = config.copy()

    # Override with session config (session takes precedence)
    current_project_overrides = session_manager.session_state.projects.get(session_manager.current_project, {})
    for key, value in current_project_overrides.items():
        merged_config[key] = value

    # Fill in any missing keys with session defaults
    for key, value in session_config.items():
        if key not in merged_config:
            merged_config[key] = value

    # Store session config on server for testing
    server.session_config = merged_config

    # Add session path resolution method
    server.resolve_session_path = lambda path: resolve_session_path(path, session_manager.current_project)

    return server
