"""MCP server for developer guidelines and project rules with hybrid file access."""

import functools
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP
from mcp.types import Resource
from pydantic import AnyUrl
from pathlib import Path
from .session_manager import SessionManager
from .file_source import FileSource, FileAccessor
from .logging_config import get_logger
from .error_handler import ErrorHandler
from . import tools

logger = get_logger()
error_handler = ErrorHandler(logger)


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> Any:
    """Server lifespan manager for initialization and cleanup.

    Initializes the current project from PWD and ensures configuration is loaded.
    """
    logger.info("=== Starting MCP server initialization ===")

    try:
        # Initialize current project from PWD environment variable
        session_manager = SessionManager()
        try:
            project_name = session_manager.get_project_name()
            logger.info(f"Initialized project from PWD: {project_name}")

            # Ensure project configuration is loaded or created
            await session_manager.get_or_create_project_config(project_name)
            logger.info(f"Project configuration initialized for: {project_name}")
        except ValueError as e:
            logger.error(f"Failed to initialize project: {e}")
            raise

        logger.info("MCP server initialized successfully")
        yield

    except Exception as e:
        logger.error(f"Unexpected error during server initialization: {e}", exc_info=True)
        raise
    finally:
        logger.info("MCP server shutting down")


mcp = FastMCP(name="Developer Guide MCP", lifespan=server_lifespan)


def log_tool_usage(func: Any) -> Any:
    """Decorator to log tool usage and responses with comprehensive error handling."""
    import inspect

    if inspect.iscoroutinefunction(func):
        # Async wrapper for async functions
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            tool_name = getattr(func, "__name__", "unknown_tool")
            logger.debug(f"Tool '{tool_name}' called with args: {args}, kwargs: {kwargs}")
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"Tool '{tool_name}' completed successfully")
                return result
            except Exception as e:
                # Use ErrorHandler for comprehensive error logging with traceback
                error_handler.handle_error(e, f"tool '{tool_name}'")
                # Re-raise the exception for proper error handling
                raise

        return async_wrapper
    else:
        # Sync wrapper for sync functions
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            tool_name = getattr(func, "__name__", "unknown_tool")

            # Debug log for non-async functions with caller info
            try:
                caller_frame = inspect.stack()[1]
                caller_info = f"{caller_frame.filename}:{caller_frame.lineno} in {caller_frame.function}"
                logger.debug(f"NON-ASYNC TOOL CALL: '{tool_name}' called from {caller_info}")
            except Exception:
                logger.debug(f"NON-ASYNC TOOL CALL: '{tool_name}' (caller info unavailable)")

            logger.debug(f"Tool '{tool_name}' called with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Tool '{tool_name}' completed successfully")
                return result
            except Exception as e:
                # Use ErrorHandler for comprehensive error logging with traceback
                error_handler.handle_error(e, f"tool '{tool_name}'")
                # Re-raise the exception for proper error handling
                raise

        return sync_wrapper


class ExtMcpToolDecorator:
    """Extended MCP tool decorator with flexible prefixing and automatic client root initialization."""

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

            # Wrap function with client root initialization (for async functions)
            import inspect

            if inspect.iscoroutinefunction(func):

                @functools.wraps(func)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    return await func(*args, **kwargs)

                wrapped_func = async_wrapper
            else:
                # Sync function - no initialization needed
                wrapped_func = func

            # Wrap with logging
            logged_func = log_tool_usage(wrapped_func)
            return self.mcp.tool(name=tool_name, **kwargs)(logged_func)

        return decorator


# Create guide decorator instance
guide = ExtMcpToolDecorator(mcp, prefix="guide_")


# Register MCP Tools
# Note: set_directory removed as part of Issue 044 - PWD-based project detection


@guide.tool()
async def get_current_project() -> Dict[str, Any]:
    """Get the active project name."""
    logger.debug("Getting current project")
    project = await tools.get_current_project()
    if project is None:
        return {"success": False, "error": "No project set. Use 'set directory /path/to/project' first."}
    return {"success": True, "project": project}


@guide.tool()
async def switch_project(name: str) -> Dict[str, Any]:
    """Switch to a different project."""
    logger.info(f"Switching to project: {name}")
    return await tools.switch_project(name)


@guide.tool()
async def get_project_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get project configuration."""
    return await tools.get_project_config(project)


@guide.tool()
async def set_project_config_values(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Set multiple project configuration values at once."""
    return await tools.set_project_config_values(config_dict)


@guide.tool()
async def set_project_config(key: str, value: Any) -> Dict[str, Any]:
    """Update project settings."""
    return await tools.set_project_config(key, value)


@guide.tool()
async def get_effective_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get merged configuration (file + session)."""
    return await tools.get_effective_config(project)


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
async def list_files(file_type: str, project: Optional[str] = None) -> List[str]:
    """List available files (guides, languages, etc.)."""
    return await tools.list_files(file_type, project)


@guide.tool()
def file_exists(path: str, project: Optional[str] = None) -> bool:
    """Check if a file exists."""
    return tools.file_exists(path, project)


@guide.tool()
async def get_file_content(path: str, project: Optional[str] = None) -> str:
    """Get raw file content."""
    return await tools.get_file_content(path, project)


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
async def list_categories(project: Optional[str] = None) -> Dict[str, Any]:
    """List all categories (built-in and custom)."""
    return await tools.list_categories(project)


@guide.tool()
async def get_category_content(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Get content from a category using glob patterns."""
    return await tools.get_category_content(name, project)


# MCP Prompt Handlers
@mcp.prompt("guide")
async def guide_prompt(category: Optional[str] = None) -> str:
    """Get all auto-load guides or specific category."""
    # No initialization needed - PWD-based project detection handles context

    if category:
        result = await tools.get_category_content(category, None)
        if result.get("success"):
            return str(result.get("content", ""))
        else:
            return f"Error: {result.get('error', 'Failed to get category')}"
    else:
        guides = await tools.get_all_guides(None)
        if guides:
            content_parts = [f"## {category_name}\n\n{content}" for category_name, content in guides.items()]
            return "\n\n".join(content_parts)
        else:
            return "No guides available."


@mcp.prompt("category")
async def category_prompt(
    action: str, name: str, dir: Optional[str] = None, patterns: Optional[str] = None, auto_load: Optional[str] = None
) -> str:
    """Manage categories (new, edit, del)."""
    # No initialization needed - PWD-based project detection handles context

    if action == "new":
        # Check for duplicate category name
        categories_result = await tools.list_categories(None)
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
        categories_result = await tools.list_categories(None)
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


DAIC_ENABLED = "DAIC mode: ENABLED"
DAIC_DESC = "Discussion-Alignment-Implementation-Check"
DAIC_DISABLED = "DAIC mode: DISABLED"

# Agent instruction constants for file operations
DAIC_ENABLE_INSTRUCTION = "\n\nPlease remove the .consent file from the project root to enable DAIC mode."
DAIC_DISABLE_INSTRUCTION = (
    "\n\nPlease create a .consent file in the project root to disable DAIC mode and allow implementation."
)


async def check_daic_status() -> bool:
    """Check if DAIC mode is enabled."""
    result = await daic_status()
    return result is True


async def daic_status(state: bool | None = None) -> bool | None:
    """Set or check the current DAIC status."""

    # Check for .consent file in current working directory (PWD-based)
    consent_file = Path.cwd() / ".consent"

    if state is not None:
        # Setting state - create or remove consent file
        if state:
            # Enable DAIC - remove consent file if it exists
            if consent_file.exists():
                consent_file.unlink()
        else:
            # Disable DAIC - create consent file
            consent_file.touch()
        return state
    else:
        # Getting state - check if consent file exists
        # DAIC is enabled when consent file does NOT exist
        return not consent_file.exists()


@mcp.prompt("daic")
async def daic_prompt(arg: Optional[str] = None) -> str:
    """Manage DAIC (Discussion-Alignment-Implementation-Check) state."""

    if arg is not None:
        arg = arg.strip()
    if not arg:
        # Return current state - check actual consent file status
        is_enabled = await daic_status()
        if is_enabled:
            return f"{DAIC_ENABLED} ({DAIC_DESC})"
        else:
            return f"{DAIC_DISABLED} (Implementation allowed)"

    if arg.lower() in {"on", "enable", "true", "1", "yes"}:
        # Enable DAIC - instruct agent to remove .consent file
        return f"{DAIC_ENABLED} ({DAIC_DESC}){DAIC_ENABLE_INSTRUCTION}"

    # Disable DAIC - instruct agent to create .consent file
    return f"{DAIC_DISABLED} - {arg.strip()}{DAIC_DISABLE_INSTRUCTION}"


def _get_auto_load_categories(config: Dict[str, Any]) -> List[tuple[str, Dict[str, Any]]]:
    """Get categories with auto_load: true."""
    return [
        (name, category_config)
        for name, category_config in config.get("categories", {}).items()
        if category_config.get("auto_load", False)
    ]


# MCP Resource Handlers
async def list_resources() -> List[Resource]:
    """List resources for auto_load categories."""
    from mcp.types import Resource

    session = SessionManager()
    current_project = session.get_project_name()

    # Get project config to find categories with auto_load: true
    config = await session.get_or_create_project_config(current_project)
    auto_load_categories = _get_auto_load_categories(config)

    # Generate resources for each auto_load category
    resources = []

    # Add aggregate resource for all auto-load categories
    if auto_load_categories:
        aggregate_resource = Resource(
            uri=AnyUrl("guide://category/"),
            name="all-guides",
            description="All auto-load guide categories combined",
            mimeType="text/markdown",
        )
        resources.append(aggregate_resource)

    # Add individual category resources
    for category_name, category_config in auto_load_categories:
        resource = Resource(
            uri=AnyUrl(f"guide://category/{category_name}"),
            name=category_name,
            description=category_config.get("description", category_name),
            mimeType="text/markdown",
        )
        resources.append(resource)

    return resources


async def _get_available_categories() -> List[Dict[str, Any]]:
    """Get available categories for testing purposes."""
    session = SessionManager()
    current_project = session.get_project_name()

    # Get project config to find categories with auto_load: true
    config = await session.get_or_create_project_config(current_project)
    auto_load_categories = _get_auto_load_categories(config)

    return [
        {"name": name, "description": category_config.get("description", name)}
        for name, category_config in auto_load_categories
    ]


async def read_resource(uri: str) -> str:
    """Read resource content by URI."""
    # Parse guide://category/{name} URIs
    if not uri.startswith("guide://category/"):
        raise ValueError(f"Invalid URI scheme: {uri}")

    category_name = uri.removeprefix("guide://category/")

    # Handle aggregate resource (empty category name)
    if category_name == "":
        # Use existing get_all_guides function for combined content
        result = await tools.get_all_guides(None)
        if result.get("success"):
            return str(result.get("content", ""))
        else:
            raise Exception(f"Failed to load all guides: {result.get('error', 'Unknown error')}")

    # Use existing get_category_content function for individual categories
    result = await tools.get_category_content(category_name, None)

    if result.get("success"):
        return str(result.get("content", ""))
    else:
        raise Exception(f"Failed to load category '{category_name}': {result.get('error', 'Unknown error')}")


# Register resource handlers with MCP server (type: ignore for method assignment)
mcp.list_resources = list_resources  # type: ignore[method-assign,assignment]
mcp.read_resource = read_resource  # type: ignore[method-assign,assignment]
mcp._get_available_categories = _get_available_categories  # type: ignore[attr-defined]


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
            config = await server._session_manager.get_or_create_project_config(project_context)  # type: ignore[attr-defined]
        else:
            # Fallback to default config
            from .session_manager import SessionManager

            session_manager = SessionManager()
            config = await session_manager.get_or_create_project_config(project_context)

        # Map config_key to category names for unified system
        category_mapping = {"guide": "guide", "language": "lang", "context": "context"}

        category = category_mapping.get(config_key)
        if category:
            # Use category system to get content
            from .tools.category_tools import get_category_content
            from .file_source import FileSource, FileSourceType

            result = await get_category_content(category, project_context)
            if result.get("success") and result.get("search_dir"):
                return FileSource(FileSourceType.FILE, result["search_dir"])

        # Fallback for unknown keys
        session_path = config.get(config_key)
        if session_path:
            return FileSource.from_session_path(session_path, project_context)
        default_path = server.config.get(config_key, "./")  # type: ignore[attr-defined]
        return FileSource(FileSourceType.FILE, default_path)

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
    config_file = config.get("config_filename")

    # Auto-load session configuration if it exists
    try:
        session_manager = SessionManager()
        config_manager = session_manager.config_manager()
        config_manager.set_config_filename(config_file)

    except Exception as e:
        logger.error(f"Unexpected error during server initialization: {e}", exc_info=True)

        # Force flush all handlers before raising exception
        for handler in logger.handlers:
            handler.flush()

        raise

    return server
