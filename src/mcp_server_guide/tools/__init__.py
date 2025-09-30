"""MCP Tools for mcp-server-guide server."""

from .project_tools import get_current_project, switch_project, list_projects
from .config_tools import (
    get_project_config,
    set_project_config,
    set_project_config_values,
    get_effective_config,
)
from .content_tools import (
    get_guide,
    get_language_guide,
    get_project_context,
    get_all_guides,
    search_content,
    show_guide,
    show_language_guide,
    show_project_summary,
)
from .file_tools import list_files, file_exists, get_file_content
from .session_management import save_session, load_session, reset_session
from .category_tools import (
    add_category,
    remove_category,
    update_category,
    list_categories,
    get_category_content,
)

__all__ = [
    # Project Management
    "get_current_project",
    "switch_project",
    "list_projects",
    # Configuration Access
    "get_project_config",
    "set_project_config",
    "set_project_config_values",
    "get_effective_config",
    # Content Retrieval
    "get_guide",
    "get_language_guide",
    "get_project_context",
    "get_all_guides",
    "search_content",
    "show_guide",
    "show_language_guide",
    "show_project_summary",
    # File Operations
    "list_files",
    "file_exists",
    "get_file_content",
    # Session Management
    "save_session",
    "load_session",
    "reset_session",
    # Category Management
    "add_category",
    "remove_category",
    "update_category",
    "list_categories",
    "get_category_content",
]
