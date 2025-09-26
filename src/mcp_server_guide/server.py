"""MCP server for developer guidelines and project rules with hybrid file access."""

from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP
from .session import resolve_session_path
from .session_tools import SessionManager
from .file_source import FileSource, FileAccessor
from .logging_config import get_logger
from . import tools

logger = get_logger(__name__)
mcp = FastMCP(name="Developer Guide MCP")


# Register MCP Tools
@mcp.tool()
def get_current_project() -> str:
    """Get the active project name."""
    logger.debug("Getting current project")
    return tools.get_current_project()


@mcp.tool()
def switch_project(name: str) -> Dict[str, Any]:
    """Switch to a different project."""
    logger.info(f"Switching to project: {name}")
    return tools.switch_project(name)


@mcp.tool()
def list_projects() -> List[str]:
    """List available projects."""
    logger.debug("Listing available projects")
    return tools.list_projects()


@mcp.tool()
def get_project_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get project configuration."""
    return tools.get_project_config(project)


@mcp.tool()
def set_project_config_values(config_dict: Dict[str, Any], project: Optional[str] = None) -> Dict[str, Any]:
    """Set multiple project configuration values at once."""
    return tools.set_project_config_values(config_dict, project)


@mcp.tool()
def set_project_config(key: str, value: Any, project: Optional[str] = None) -> Dict[str, Any]:
    """Update project settings."""
    return tools.set_project_config(key, value, project)


@mcp.tool()
def get_effective_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get merged configuration (file + session)."""
    return tools.get_effective_config(project)


@mcp.tool()
def get_tools(project: Optional[str] = None) -> List[str]:
    """Get project-specific tools list."""
    return tools.get_tools(project)


@mcp.tool()
def set_tools(tools_array: List[str], project: Optional[str] = None) -> Dict[str, Any]:
    """Set tools for project."""
    return tools.set_tools(tools_array, project)


@mcp.tool()
def get_guide(project: Optional[str] = None) -> str:
    """Get project guidelines for AI injection."""
    return tools.get_guide(project)


@mcp.tool()
def get_language_guide(project: Optional[str] = None) -> str:
    """Get language-specific guidelines for AI injection."""
    return tools.get_language_guide(project)


@mcp.tool()
def get_project_context(project: Optional[str] = None) -> str:
    """Get project context document for AI injection."""
    return tools.get_project_context(project)


@mcp.tool()
def get_all_guides(project: Optional[str] = None) -> Dict[str, str]:
    """Get all guide files for comprehensive AI context."""
    return tools.get_all_guides(project)


@mcp.tool()
def search_content(query: str, project: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search across project content."""
    return tools.search_content(query, project)


@mcp.tool()
def show_guide(project: Optional[str] = None) -> Dict[str, Any]:
    """Display guide to user."""
    return tools.show_guide(project)


@mcp.tool()
def show_language_guide(project: Optional[str] = None) -> Dict[str, Any]:
    """Display language guide to user."""
    return tools.show_language_guide(project)


@mcp.tool()
def show_project_summary(project: Optional[str] = None) -> Dict[str, Any]:
    """Display project overview to user."""
    return tools.show_project_summary(project)


@mcp.tool()
def list_files(file_type: str, project: Optional[str] = None) -> List[str]:
    """List available files (guides, languages, etc.)."""
    return tools.list_files(file_type, project)


@mcp.tool()
def file_exists(path: str, project: Optional[str] = None) -> bool:
    """Check if a file exists."""
    return tools.file_exists(path, project)


@mcp.tool()
def get_file_content(path: str, project: Optional[str] = None) -> str:
    """Get raw file content."""
    return tools.get_file_content(path, project)


@mcp.tool()
def save_session() -> Dict[str, Any]:
    """Persist current session state."""
    return tools.save_session()


@mcp.tool()
def load_session(project_path: Optional[str] = None) -> Dict[str, Any]:
    """Load session from project."""
    from pathlib import Path

    path = Path(project_path) if project_path else None
    return tools.load_session(path)


@mcp.tool()
def reset_session() -> Dict[str, Any]:
    """Reset to defaults."""
    return tools.reset_session()


def create_server(
    docroot: str = ".",
    guidesdir: str = "aidocs/guide/",
    langsdir: str = "aidocs/lang/",
    contextdir: str = "aidocs/context/",
    cache_dir: Optional[str] = None,
) -> FastMCP:
    """Create MCP server instance with hybrid file access."""
    server = FastMCP(name="Developer Guide MCP")

    # Initialize hybrid file access
    server.file_accessor = FileAccessor(cache_dir=cache_dir)  # type: ignore[attr-defined]
    server._session_manager = SessionManager()  # type: ignore[assignment]

    # Store config
    server.config = {  # type: ignore[attr-defined]
        "docroot": docroot,
        "guidesdir": guidesdir,
        "langsdir": langsdir,
        "contextdir": contextdir,
    }

    # Add file source resolution method
    def _get_file_source(config_key: str, project_context: str) -> FileSource:
        """Get file source for a configuration key."""
        if hasattr(server, "_session_manager") and server._session_manager is not None:
            config = server._session_manager.session_state.get_project_config(project_context)  # type: ignore[attr-defined]
        else:
            # Fallback to default config
            from .session_tools import SessionManager

            session_manager = SessionManager()
            config = session_manager.session_state.get_project_config(project_context)

        # Map config_key to directory and filename keys
        if config_key == "guide":
            dir_key, file_key = "guidesdir", "guide"
        elif config_key == "language":
            dir_key, file_key = "langdir", "language"
        else:
            # Fallback for unknown keys
            session_path = config.get(config_key)
            if session_path:
                return FileSource.from_session_path(session_path, project_context)
            default_path = server.config.get(config_key, "./")  # type: ignore[attr-defined]
            return FileSource("server", default_path)

        # Get the filename value from config
        filename = config.get(file_key, "")

        # If filename has a session path prefix, use it directly
        if filename and (":" in filename and filename.split(":", 1)[0] in ["local", "server", "http", "https", "file"]):
            return FileSource.from_session_path(filename, project_context)

        # Otherwise, construct path from directory and filename
        directory = config.get(dir_key, "")
        if directory and filename:
            # Construct full path: directory + filename + .md
            if not filename.endswith(".md"):
                filename += ".md"
            full_path = f"{directory.rstrip('/')}/{filename}"
            return FileSource.from_session_path(full_path, project_context)
        else:
            # Fallback to server default
            default_path = server.config.get(dir_key, "./")  # type: ignore[attr-defined]
            return FileSource("server", default_path)

    server._get_file_source = _get_file_source  # type: ignore[attr-defined]

    # Add content reading methods
    def read_guide(project_context: str) -> str:
        """Read guide content using hybrid file access."""
        source = _get_file_source("guide", project_context)
        result = server.file_accessor.read_file("", source)  # type: ignore[attr-defined]
        return str(result)

    def read_language(project_context: str) -> str:
        """Read language content using hybrid file access."""
        source = _get_file_source("language", project_context)
        result = server.file_accessor.read_file("", source)  # type: ignore[attr-defined]
        return str(result)

    server.read_guide = read_guide  # type: ignore[attr-defined]
    server.read_language = read_language  # type: ignore[attr-defined]

    return server


def create_server_with_config(config: Dict[str, Any]) -> FastMCP:
    """Create MCP server instance with session-aware configuration."""
    logger.debug("Creating server with session-aware configuration")
    server = FastMCP(name="Developer Guide MCP")

    # Get config filename (default or custom)
    config_filename = config.get("config_filename", ".mcp-server-guide.config.json")

    # Auto-load session configuration if it exists
    try:
        from pathlib import Path
        from .project_config import ProjectConfigManager

        session_manager = SessionManager()
        manager = ProjectConfigManager()

        # Try to load full session state
        if manager.load_full_session_state(Path("."), session_manager, config_filename):
            logger.info("Auto-loaded saved session configuration")
        else:
            logger.debug("No saved session found, using defaults")
    except Exception as e:
        logger.warning(f"Failed to auto-load session: {e}")
        session_manager = SessionManager()

    # Use the same session manager instance (singleton)
    current_project = session_manager.get_current_project()
    logger.debug(f"Current project: {current_project}")

    # Get session config for current project
    session_config = session_manager.session_state.get_project_config(current_project)

    # Start with session defaults
    merged_config = session_config.copy()

    # Override with provided config for keys not set in session
    current_project_overrides = session_manager.session_state.projects.get(current_project, {})
    for key, value in config.items():
        # Only use provided config if session doesn't have this key set
        if key not in current_project_overrides and key != "config_filename":
            merged_config[key] = value

    # Ensure session overrides take precedence
    for key, value in current_project_overrides.items():
        merged_config[key] = value

    logger.debug(f"Merged configuration: {merged_config}")
    # Store session config on server for testing
    server.session_config = merged_config  # type: ignore[attr-defined]

    # Add session path resolution method
    server.resolve_session_path = lambda path: resolve_session_path(path, current_project)  # type: ignore[attr-defined]

    return server
