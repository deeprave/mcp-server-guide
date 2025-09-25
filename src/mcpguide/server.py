"""MCP server for developer guidelines and project rules with hybrid file access."""

from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from .session import resolve_session_path
from .session_tools import SessionManager
from .file_source import FileSource, FileAccessor

mcp = FastMCP(name="Developer Guide MCP")

defaults = {
    "guide": "./guide/",
    "project": "./project/",
    "lang": "./lang/",
}


def create_server(docroot: str = ".", guidesdir: str = "guide/",
                 langsdir: str = "lang/", projdir: str = "project/",
                 cache_dir: Optional[str] = None) -> FastMCP:
    """Create MCP server instance with hybrid file access."""
    server = FastMCP(name="Developer Guide MCP")

    # Initialize hybrid file access
    server.file_accessor = FileAccessor(cache_dir=cache_dir)
    server._session_manager = SessionManager()  # Use underscore to avoid conflicts

    # Store config
    server.config = {
        "docroot": docroot,
        "guidesdir": guidesdir,
        "langsdir": langsdir,
        "projdir": projdir,
    }

    # Add file source resolution method
    def _get_file_source(config_key: str, project_context: str) -> FileSource:
        """Get file source for a configuration key."""
        session_path = server._session_manager.session_state.get_project_config(project_context).get(config_key)
        if session_path:
            return FileSource.from_session_path(session_path, project_context)
        else:
            # Fallback to server default
            default_path = server.config.get(config_key, "./")
            return FileSource("server", default_path)

    server._get_file_source = _get_file_source

    # Add content reading methods
    def read_guide(project_context: str) -> str:
        """Read guide content using hybrid file access."""
        source = _get_file_source("guide", project_context)
        return server.file_accessor.read_file("", source)

    def read_language(project_context: str) -> str:
        """Read language content using hybrid file access."""
        source = _get_file_source("language", project_context)
        return server.file_accessor.read_file("", source)

    server.read_guide = read_guide
    server.read_language = read_language

    return server


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
