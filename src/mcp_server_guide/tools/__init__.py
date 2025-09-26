"""MCP Tools for mcp-server-guide server."""

from .project_tools import get_current_project, switch_project, list_projects
from .config_tools import (
    get_project_config,
    set_project_config,
    set_project_config_values,
    get_effective_config,
    get_tools,
    set_tools,
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
    "get_tools",
    "set_tools",
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
]
