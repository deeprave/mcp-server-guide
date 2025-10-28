"""MCP server for developer guidelines and project rules with hybrid file access."""

import functools
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from .project_config import Category, Collection
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP
from .session_manager import SessionManager
from .file_source import FileSource, FileAccessor
from .logging_config import get_logger
from .error_handler import ErrorHandler
from .prompts import register_prompts
from .tool_registry import register_tools

if TYPE_CHECKING:
    from .project_config import ProjectConfig

logger = get_logger()
error_handler = ErrorHandler(logger)


async def _register_category_resources(server: FastMCP, config: "ProjectConfig") -> None:
    """Register dynamic resources for categories and collections."""
    from .tools.category_tools import get_category_content

    def make_category_reader(cat_name: str, cat_config: Category) -> object:
        desc = cat_config.description
        if desc is None or (isinstance(desc, str) and not desc.strip()):
            desc = cat_name

        @server.resource(f"guide://category/{cat_name}", name=cat_name, description=desc, mime_type="text/markdown")
        async def read_category() -> str:
            """Get content for a specific category."""
            result = await get_category_content(cat_name, None)
            if result.get("success"):
                return str(result.get("content", ""))
            raise ValueError(f"Failed to load category '{cat_name}': {result.get('error', 'Unknown error')}")

        return read_category

    # Register individual category resources for all categories
    for category_name, category_config in config.categories.items():
        make_category_reader(category_name, category_config)
        logger.info(f"Registered resource: guide://category/{category_name}")

    # Register collection resources
    from .tools.collection_tools import get_collection_content

    def make_collection_reader(coll_name: str, coll_config: Collection) -> object:
        desc = coll_config.description
        if desc is None or (isinstance(desc, str) and not desc.strip()):
            desc = coll_name

        @server.resource(f"guide://collection/{coll_name}", name=coll_name, description=desc, mime_type="text/markdown")
        async def read_collection() -> str:
            try:
                result = await get_collection_content(coll_name, None)
                if result.get("success"):
                    return str(result.get("content", ""))
                else:
                    return f"Error loading collection '{coll_name}': {result.get('error', 'Unknown error')}"
            except Exception as e:
                logger.error(f"Error in collection reader for '{coll_name}': {e}")
                return f"Error loading collection '{coll_name}': {str(e)}"

        return read_collection

    for collection_name, collection_config in config.collections.items():
        make_collection_reader(collection_name, collection_config)
        logger.info(f"Registered resource: guide://collection/{collection_name}")

    # Register help resource
    @server.resource("guide://help", name="help", description="MCP Server Guide Help", mime_type="text/markdown")
    async def read_help() -> str:
        """Get comprehensive help content for the guide system."""
        return await _format_guide_help()


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
            config = await session_manager.get_or_create_project_config(project_name)
            logger.info(f"Project configuration initialized for: {project_name}")

            # Register dynamic resources based on categories and collections
            await _register_category_resources(server, config)
            logger.info("Dynamic resources registered successfully")

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

# Register prompts with the global MCP instance
register_prompts(mcp)


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


NO_PREFIX = ("", "none", "false")


def get_tool_prefix() -> str:
    import os

    # Get the prefix from environment, or use "guide_" if not set
    # Note: if GUIDE_TOOL_PREFIX="" (empty string), this will return ""
    prefix = os.getenv("GUIDE_TOOL_PREFIX")
    return "guide_" if prefix is None else "" if prefix in NO_PREFIX else prefix


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
guide = ExtMcpToolDecorator(mcp, prefix=get_tool_prefix())

# Register all tools with the server
try:
    register_tools(mcp, guide, log_tool_usage)
except Exception as e:
    logger.error("Failed to register tools with the server: %s", e, exc_info=True)
    raise


# Register MCP Tools directly from tools module
async def _format_guide_help() -> str:
    """Format comprehensive help content for the guide prompt."""
    from .naming import MCP_GUIDE_VERSION

    help_sections = []

    # About section
    help_sections.append(f"""# MCP Server Guide Help

**Version:** {MCP_GUIDE_VERSION}
**Description:** Developer guidelines and project rules MCP server

This server provides access to project documentation, categories, collections, and development guidelines through MCP prompts, tools, and resources.""")

    # Available Prompts
    try:
        from .tools import list_prompts

        prompts_result = await list_prompts()
        if prompts_result.get("success"):
            prompts = prompts_result.get("prompts", [])
            help_sections.append("")
            help_sections.append("## Available Prompts")
            for prompt in prompts:
                args_info = ""
                if prompt.get("arguments"):
                    args = [f"`{arg['name']}`{'*' if arg['required'] else ''}" for arg in prompt["arguments"]]
                    args_info = f" ({', '.join(args)})"
                help_sections.append(f" - **{prompt['name']}**{args_info}: {prompt.get('description', '')}")
    except Exception as e:
        help_sections.append("")
        help_sections.append(f"## Available Prompts")
        help_sections.append(f" *Error loading prompts: {e}*")

    # Categories and Collections
    try:
        from .tools import list_categories

        categories_result = await list_categories(verbose=True)
        if categories_result.get("success"):
            categories = categories_result.get("categories", {})
            help_sections.append("")
            help_sections.append("## Categories and Collections")
            for cat_name, cat_info in categories.items():
                collections = cat_info.get("collections", [])
                collections_text = f" (in collections: {', '.join(collections)})" if collections else ""
                help_sections.append(f" - **{cat_name}**{collections_text}: {cat_info.get('description', '')}")
    except Exception as e:
        help_sections.append("")
        help_sections.append("## Categories and Collections")
        help_sections.append(f" *Error loading categories: {e}*")

    # Available Resources
    try:
        from .tools import list_resources

        resources_result = await list_resources()
        if resources_result.get("success"):
            resources = resources_result.get("resources", [])
            help_sections.append("")
            help_sections.append("## Available Resources")
            for resource in resources:
                mime_info = f" ({resource['mime_type']})" if resource.get("mime_type") else ""
                help_sections.append(f" - **{resource['uri']}**{mime_info}: {resource.get('description', '')}")
    except Exception as e:
        help_sections.append("")
        help_sections.append("## Available Resources")
        help_sections.append(f" *Error loading resources: {e}*")

    # Usage Examples
    help_sections.append("")
    help_sections.append("## Usage Examples")
    help_sections.append(" - `guide` or `guide --help` - Show this help")
    help_sections.append(" - `guide <category>` - Get content from a specific category")
    help_sections.append(" - `guide <collection>` - Get content from a collection")
    help_sections.append(" - Use MCP tools for management operations")
    help_sections.append(" - Access resources via their URIs")

    return "\n".join(help_sections)


# MCP Prompt Handlers
@mcp.prompt("guide")
async def guide_prompt(category: Optional[str] = None) -> str:
    """Get built-in guides or specific category/collection."""
    normalized_category = category.strip().lower() if category else None

    # Show help for no arguments or help flags (Claude compatibility)
    if not normalized_category or normalized_category in ["-", "-h", "--help"]:
        return "Use the Guide MCP resource `guide://help` to display the complete Guide MCP Server help as a markdown document."
    else:
        # Try category first
        from .tools import get_category_content

        result = await get_category_content(normalized_category, None)
        if result.get("success"):
            content = result.get("content", "")
            return content if isinstance(content, str) else str(content)

        # Try collection if category failed
        from .tools import get_collection_content

        result = await get_collection_content(normalized_category, None)
        if result.get("success"):
            content = result.get("content", "")
            return content if isinstance(content, str) else str(content)

        return f"Category or collection '{normalized_category}' not found."


@mcp.prompt("category")
async def category_prompt(action: str, name: str, dir: Optional[str] = None, patterns: Optional[str] = None) -> str:
    """Manage categories (new, edit, del)."""
    # No initialization needed - PWD-based project detection handles context

    if action == "new":
        # Check for duplicate category name
        from .tools import list_categories

        categories_result = await list_categories(verbose=False)
        all_categories = categories_result["categories"]
        if name in all_categories:
            return f"Error: Category with name '{name}' already exists."

        # Parse patterns from comma-separated string
        pattern_list = patterns.split(",") if patterns else ["*.md"]

        from .tools import add_category

        result = await add_category(name=name, dir=dir or name, patterns=pattern_list, description="")

        if result.get("success"):
            return f"Successfully created category '{name}'"
        else:
            return f"Error creating category: {result.get('error', 'Unknown error')}"

    elif action == "edit":
        # Get current category to preserve existing values
        from .tools import list_categories

        categories_result = await list_categories(verbose=False)
        existing_categories = categories_result["categories"]

        if name not in existing_categories:
            return f"Error: Category '{name}' not found"

        current_category = existing_categories[name]

        # Use provided values or fall back to current values
        new_dir = dir or current_category["dir"]

        def parse_patterns(patterns_str: str) -> List[str]:
            import re

            # This regex splits on commas not inside quotes
            pattern = r"""((?:[^,"']|"[^"]*"|'[^']*')+)"""
            items = [item.strip() for item in re.findall(pattern, patterns_str) if item.strip()]

            # Remove surrounding quotes if present
            def unquote(s: str) -> str:
                if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
                    return s[1:-1]
                return s

            return [unquote(item) for item in items]

        new_patterns = parse_patterns(patterns) if patterns else current_category["patterns"]

        from .tools import update_category

        result = await update_category(
            name=name,
            description=current_category.get("description", ""),
            dir=new_dir,
            patterns=new_patterns,
        )

        if result.get("success"):
            return f"Successfully updated category '{name}'"
        else:
            return f"Error updating category: {result.get('error', 'Unknown error')}"

    elif action == "del":
        from .tools import remove_category

        result = await remove_category(name)

        if result.get("success"):
            return f"Successfully deleted category '{name}'"
        else:
            return f"Error deleting category: {result.get('error', 'Unknown error')}"

    else:
        return f"Error: Unknown action '{action}'. Use 'new', 'edit', or 'del'."


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
        # Import here to ensure available in all code paths
        from .file_source import FileSource, FileSourceType

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
            from .tools import get_category_content

            result = await get_category_content(category, project_context)
            if result.get("success"):
                # Check if this is an HTTP-based category
                if result.get("is_http") and result.get("url"):
                    return FileSource(FileSourceType.HTTP, result["url"])
                # Otherwise it's a file-based category
                elif result.get("search_dir"):
                    return FileSource(FileSourceType.FILE, result["search_dir"])

        # Fallback for unknown keys
        session_path = getattr(config, config_key, None)
        if session_path:
            return FileSource.from_session_path(session_path, project_context)
        default_path = server.config.get(config_key, "./")  # type: ignore[attr-defined]
        return FileSource(FileSourceType.FILE, default_path)

    server._get_file_source = _get_file_source  # type: ignore[attr-defined]

    # Add content reading methods
    async def read_guide(project_context: str) -> str:
        """Read guide content using hybrid file access."""
        from .tools import get_category_content
        from .file_source import FileSource, FileSourceType

        # Try to get content from guide category
        result = await get_category_content("guide", project_context)
        if result.get("success"):
            # For HTTP categories, fetch using HTTP client
            if result.get("is_http") and result.get("url"):
                source = FileSource(FileSourceType.HTTP, result["url"])
                content = await server.file_accessor.read_file("", source)  # type: ignore[attr-defined]
                return str(content)
            # For file categories, content is already read
            elif result.get("content") is not None:
                return str(result["content"])

        # Fallback to old behavior if category doesn't exist
        source = await _get_file_source("guide", project_context)
        content = await server.file_accessor.read_file("", source)  # type: ignore[attr-defined]
        return str(content)

    async def read_language(project_context: str) -> str:
        """Read language content using hybrid file access."""
        from .tools import get_category_content
        from .file_source import FileSource, FileSourceType

        # Try to get content from lang category
        result = await get_category_content("lang", project_context)
        if result.get("success"):
            # For HTTP categories, fetch using HTTP client
            if result.get("is_http") and result.get("url"):
                source = FileSource(FileSourceType.HTTP, result["url"])
                content = await server.file_accessor.read_file("", source)  # type: ignore[attr-defined]
                return str(content)
            # For file categories, content is already read
            elif result.get("content") is not None:
                return str(result["content"])

        # Fallback to old behavior if category doesn't exist
        source = await _get_file_source("language", project_context)
        content = await server.file_accessor.read_file("", source)  # type: ignore[attr-defined]
        return str(content)

    server.read_guide = read_guide  # type: ignore[attr-defined]
    server.read_language = read_language  # type: ignore[attr-defined]

    # Register all prompt handlers
    register_prompts(server)

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

    # Register all prompt handlers
    register_prompts(server)

    return server
