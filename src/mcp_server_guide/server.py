"""MCP server for developer guidelines and project rules with hybrid file access."""

from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP
from pathlib import Path
from .session import resolve_session_path
from .session_tools import SessionManager
from .file_source import FileSource, FileAccessor
from .logging_config import get_logger
from .naming import config_filename
from . import tools

logger = get_logger(__name__)
mcp = FastMCP(name="Developer Guide MCP")


class ExtMcpToolDecorator:
    """Extended MCP tool decorator with flexible prefixing."""

    def __init__(self, mcp_instance: FastMCP, prefix: str = "") -> None:
        self.mcp = mcp_instance
        self.default_prefix = prefix

    def tool(self, name: Optional[str] = None, prefix: Optional[str] = None, **kwargs: Any) -> Any:
        def decorator(func: Any) -> Any:
            if name:
                tool_name = f"{self.default_prefix}{name}"
            elif prefix is not None:
                tool_name = f"{prefix}{func.__name__}"
            else:
                tool_name = f"{self.default_prefix}{func.__name__}"
            return self.mcp.tool(name=tool_name, **kwargs)(func)

        return decorator


# Create guide decorator instance
guide = ExtMcpToolDecorator(mcp, prefix="guide_")


# Register MCP Tools
@guide.tool()
def guide_set_directory(directory: str) -> Dict[str, Any]:
    """Set the working directory for the MCP server."""
    from .tools.session_management import set_directory

    return set_directory(directory)


@guide.tool()
def get_current_project() -> Dict[str, Any]:
    """Get the active project name."""
    logger.debug("Getting current project")
    project = tools.get_current_project()
    if project is None:
        return {"success": False, "error": "No project set. Use 'set directory /path/to/project' first."}
    return {"success": True, "project": project}


@guide.tool()
async def switch_project(name: str) -> Dict[str, Any]:
    """Switch to a different project."""
    logger.info(f"Switching to project: {name}")
    return await tools.switch_project(name)


@guide.tool()
def list_projects() -> List[str]:
    """List available projects."""
    logger.debug("Listing available projects")
    return tools.list_projects()


@guide.tool()
def get_project_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get project configuration."""
    return tools.get_project_config(project)


@guide.tool()
async def set_project_config_values(config_dict: Dict[str, Any], project: Optional[str] = None) -> Dict[str, Any]:
    """Set multiple project configuration values at once."""
    return await tools.set_project_config_values(config_dict, project)


@guide.tool()
async def set_project_config(key: str, value: Any, project: Optional[str] = None) -> Dict[str, Any]:
    """Update project settings."""
    return await tools.set_project_config(key, value, project)


@guide.tool()
def get_effective_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get merged configuration (file + session)."""
    return tools.get_effective_config(project)


@guide.tool()
async def get_guide(project: Optional[str] = None) -> str:
    """Get project guidelines for AI injection."""
    return await tools.get_guide(project)


@guide.tool()
async def get_language_guide(project: Optional[str] = None) -> str:
    """Get language-specific guidelines for AI injection."""
    return await tools.get_language_guide(project)


@guide.tool()
async def get_project_context(project: Optional[str] = None) -> str:
    """Get project context document for AI injection."""
    return await tools.get_project_context(project)


@guide.tool()
async def get_all_guides(project: Optional[str] = None) -> Dict[str, str]:
    """Get all guide files for comprehensive AI context."""
    return await tools.get_all_guides(project)


@guide.tool()
async def search_content(query: str, project: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search across project content."""
    return await tools.search_content(query, project)


@guide.tool()
async def show_guide(project: Optional[str] = None) -> Dict[str, Any]:
    """Display guide to user."""
    return await tools.show_guide(project)


@guide.tool()
async def show_language_guide(project: Optional[str] = None) -> Dict[str, Any]:
    """Display language guide to user."""
    return await tools.show_language_guide(project)


@guide.tool()
async def show_project_summary(project: Optional[str] = None) -> Dict[str, Any]:
    """Display project overview to user."""
    return await tools.show_project_summary(project)


@guide.tool()
def list_files(file_type: str, project: Optional[str] = None) -> List[str]:
    """List available files (guides, languages, etc.)."""
    return tools.list_files(file_type, project)


@guide.tool()
def file_exists(path: str, project: Optional[str] = None) -> bool:
    """Check if a file exists."""
    return tools.file_exists(path, project)


@guide.tool()
async def get_file_content(path: str, project: Optional[str] = None) -> str:
    """Get raw file content."""
    return await tools.get_file_content(path, project)


@guide.tool()
async def save_session() -> Dict[str, Any]:
    """Persist current session state."""
    return await tools.save_session()


@guide.tool()
def load_session(project_path: Optional[str] = None) -> Dict[str, Any]:
    """Load session from project."""
    from pathlib import Path

    path = Path(project_path) if project_path else None
    return tools.load_session(path)


@guide.tool()
def reset_session() -> Dict[str, Any]:
    """Reset to defaults."""
    return tools.reset_session()


# Category Management Tools
@guide.tool()
async def add_category(
    name: str,
    dir: str,
    patterns: List[str],
    project: Optional[str] = None,
    description: str = "",
    auto_load: bool = False,
) -> Dict[str, Any]:
    """Add a new custom category."""
    return await tools.add_category(name, dir, patterns, description, project, auto_load)


@guide.tool()
async def remove_category(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Remove a custom category."""
    return await tools.remove_category(name, project)


@guide.tool()
async def update_category(
    name: str,
    dir: str,
    patterns: List[str],
    project: Optional[str] = None,
    description: str = "",
    auto_load: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update an existing category."""
    return await tools.update_category(name, dir, patterns, description, project, auto_load)


@guide.tool()
def list_categories(project: Optional[str] = None) -> Dict[str, Any]:
    """List all categories (built-in and custom)."""
    return tools.list_categories(project)


@guide.tool()
async def get_category_content(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Get content from a category using glob patterns."""
    return await tools.get_category_content(name, project)


# MCP Prompt Handlers
@mcp.prompt("guide")
async def guide_prompt(category: Optional[str] = None) -> str:
    """Get all auto-load guides or specific category."""
    if category:
        result = await tools.get_category_content(category, None)
        if result.get("success"):
            return str(result.get("content", ""))
        else:
            return f"Error: {result.get('error', 'Failed to get category')}"
    else:
        guides = await tools.get_all_guides(None)
        if guides:
            content_parts = [
                f"## {category_name}\n\n{content}"
                for category_name, content in guides.items()
            ]
            return "\n\n".join(content_parts)
        else:
            return "No guides available."


@mcp.prompt("guide-category")
async def guide_category_prompt(
    action: str, name: str, dir: Optional[str] = None, patterns: Optional[str] = None, auto_load: Optional[str] = None
) -> str:
    """Manage categories (new, edit, del)."""
    if action == "new":
        # Check for duplicate category name
        categories_result = tools.list_categories(None)
        all_categories = {**categories_result["builtin_categories"], **categories_result["custom_categories"]}
        if name in all_categories:
            return f"Error: Category with name '{name}' already exists."

        # Parse patterns from comma-separated string
        pattern_list = patterns.split(",") if patterns else ["*.md"]
        auto_load_bool = auto_load == "true" if auto_load else False

        result = await tools.add_category(
            name=name, dir=dir or name, patterns=pattern_list, description="", project=None, auto_load=auto_load_bool
        )

        if result.get("success"):
            return f"Successfully created category '{name}'"
        else:
            return f"Error creating category: {result.get('error', 'Unknown error')}"

    elif action == "edit":
        # Get current category to preserve existing values
        categories_result = tools.list_categories(None)
        existing_categories: dict[str, Any] = {
            **categories_result["builtin_categories"],
            **categories_result["custom_categories"],
        }

        if name not in existing_categories:
            return f"Error: Category '{name}' not found"

        current_category = existing_categories[name]

        # Use provided values or fall back to current values
        new_dir = dir if dir else current_category["dir"]
        new_patterns = patterns.split(",") if patterns else current_category["patterns"]
        new_auto_load = auto_load == "true" if auto_load else current_category.get("auto_load", False)

        result = await tools.update_category(
            name=name,
            dir=new_dir,
            patterns=new_patterns,
            description=current_category.get("description", ""),
            project=None,
            auto_load=new_auto_load,
        )

        if result.get("success"):
            return f"Successfully updated category '{name}'"
        else:
            return f"Error updating category: {result.get('error', 'Unknown error')}"

    elif action == "del":
        result = await tools.remove_category(name, None)

        if result.get("success"):
            return f"Successfully deleted category '{name}'"
        else:
            return f"Error deleting category: {result.get('error', 'Unknown error')}"

    else:
        return f"Error: Unknown action '{action}'. Use 'new', 'edit', or 'del'."


@mcp.prompt("g-category")
async def g_category_prompt(
    action: str, name: str, dir: Optional[str] = None, patterns: Optional[str] = None, auto_load: Optional[str] = None
) -> str:
    """Manage categories - shorthand."""
    # Delegate to guide_category_prompt
    result = await guide_category_prompt(action, name, dir, patterns, auto_load)
    return str(result)


@mcp.prompt("daic")
async def daic_prompt(action: Optional[str] = None) -> str:
    """Manage DAIC (Discussion-Alignment-Implementation-Check) state."""
    from .current_project_manager import CurrentProjectManager

    # Get client working directory for .consent file
    project_manager = CurrentProjectManager()

    client_dir = project_manager.directory
    if client_dir is None:
        return "Error: Client working directory not available"
    client_dir = Path(client_dir)
    consent_file = client_dir / ".consent"

    if action is None:
        # Return current state
        return (
            "DAIC state: DISABLED"
            if consent_file.exists()
            else "DAIC state: ENABLED"
        )
    # Handle enable/disable actions
    enable_values = {"on", "true", "1", "+", "enabled"}
    disable_values = {"off", "false", "0", "-", "disabled"}

    normalized_action = action.strip().lower()
    if normalized_action in enable_values:
        # Enable DAIC (remove .consent file)
        consent_file.unlink(missing_ok=True)
        return "DAIC state: ENABLED"
    elif normalized_action in disable_values:
        # Disable DAIC (create .consent file)
        consent_file.touch()
        return "DAIC state: ENABLED"
    else:
        return f"Invalid action '{action}'. Use: on|true or off|false"


# MCP Resource Handlers
def list_resources() -> List[Dict[str, Any]]:
    """List resources for auto_load categories."""
    session = SessionManager()
    current_project = session.get_current_project_safe()

    # Get project config to find categories with auto_load: true
    config = session.session_state.get_project_config(current_project)
    categories = config.get("categories", {})

    # Filter categories with auto_load: true
    auto_load_categories = [
        (name, category_config)
        for name, category_config in categories.items()
        if category_config.get("auto_load", False)
    ]

    # Generate resources for each auto_load category
    resources = []
    for category_name, category_config in auto_load_categories:
        resource = {
            "uri": f"guide://{category_name}",
            "name": category_config.get("description", category_name),
            "mimeType": "text/markdown",
        }
        resources.append(resource)

    return resources


async def read_resource(uri: str) -> str:
    """Read resource content by URI."""
    # Parse guide://category_name URIs
    if not uri.startswith("guide://"):
        raise ValueError(f"Invalid URI scheme: {uri}")

    category_name = uri[8:]  # Remove "guide://" prefix

    # Use existing get_category_content function
    result = await tools.get_category_content(category_name, None)

    if result.get("success"):
        return str(result.get("content", ""))
    else:
        raise Exception(f"Failed to load category '{category_name}': {result.get('error', 'Unknown error')}")


# Register resource handlers with MCP server (type: ignore for method assignment)
mcp.list_resources = list_resources  # type: ignore[method-assign,assignment]
mcp.read_resource = read_resource  # type: ignore[method-assign,assignment]


def create_server(
    docroot: str = ".",
    cache_dir: Optional[str] = None,
) -> FastMCP:
    """Create MCP server instance with hybrid file access."""
    server = FastMCP(name="Developer Guide MCP")

    # Initialize hybrid file access with cache if provided
    server.file_accessor = FileAccessor(cache_dir=cache_dir)  # type: ignore[attr-defined]

    server._session_manager = SessionManager()  # type: ignore[assignment]

    # Store config
    server.config = {  # type: ignore[attr-defined]
        "docroot": docroot,
    }

    # Add file source resolution method
    async def _get_file_source(config_key: str, project_context: str) -> FileSource:
        """Get file source for a configuration key."""
        if hasattr(server, "_session_manager") and server._session_manager is not None:
            config = server._session_manager.session_state.get_project_config(project_context)  # type: ignore[attr-defined]
        else:
            # Fallback to default config
            from .session_tools import SessionManager

            session_manager = SessionManager()
            config = session_manager.session_state.get_project_config(project_context)

        # Map config_key to category names for unified system
        category_mapping = {"guide": "guide", "language": "lang", "context": "context"}

        category = category_mapping.get(config_key)
        if category:
            # Use category system to get content
            from .tools.category_tools import get_category_content

            result = await get_category_content(category, project_context)
            if result.get("success") and result.get("search_dir"):
                return FileSource("server", result["search_dir"])

        # Fallback for unknown keys
        session_path = config.get(config_key)
        if session_path:
            return FileSource.from_session_path(session_path, project_context)
        default_path = server.config.get(config_key, "./")  # type: ignore[attr-defined]
        return FileSource("server", default_path)

    server._get_file_source = _get_file_source  # type: ignore[attr-defined]

    # Add content reading methods
    async def read_guide(project_context: str) -> str:
        """Read guide content using hybrid file access."""
        source = await _get_file_source("guide", project_context)
        result = await server.file_accessor.read_file("", source)  # type: ignore[attr-defined]
        return str(result)

    async def read_language(project_context: str) -> str:
        """Read language content using hybrid file access."""
        source = await _get_file_source("language", project_context)
        result = await server.file_accessor.read_file("", source)  # type: ignore[attr-defined]
        return str(result)

    server.read_guide = read_guide  # type: ignore[attr-defined]
    server.read_language = read_language  # type: ignore[attr-defined]

    return server


def create_server_with_config(config: Dict[str, Any]) -> FastMCP:
    """Create MCP server instance with session-aware configuration."""
    logger.debug("Creating server with session-aware configuration")
    # Use the global mcp instance where tools are registered
    server = mcp

    # Get config filename (default or custom)
    config_file = config.get("config_filename", config_filename())

    # Auto-load session configuration if it exists
    try:
        from pathlib import Path
        from .project_config import ProjectConfigManager

        session_manager = SessionManager()
        manager = ProjectConfigManager()

        # Try to load full session state
        if manager.load_full_session_state(Path("."), session_manager, config_file):
            logger.info("Auto-loaded saved session configuration")
        else:
            logger.debug("No saved session found, using defaults")
    except Exception as e:
        logger.warning(f"Failed to auto-load session: {e}")
        session_manager = SessionManager()

    # Use the same session manager instance (singleton)
    current_project = session_manager.get_current_project_safe()
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
