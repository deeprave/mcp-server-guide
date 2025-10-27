"""All MCP tools consolidated in a single module."""

from typing import Any, Callable
from mcp.server.fastmcp import FastMCP

# Import all tool functions
from .tools.project_tools import get_current_project, switch_project
from .tools.config_tools import get_project_config, set_project_config, set_project_config_values
from .tools.content_tools import (
    get_guide,
    get_language_guide,
    get_project_context,
    search_content,
    show_guide,
    show_language_guide,
)
from .tools.file_tools import get_file_content
from .tools.category_tools import add_category, remove_category, update_category, list_categories, get_category_content
from .tools.collection_tools import add_collection, update_collection, list_collections, remove_collection
from .tools.prompt_tools import list_prompts


def register_tools(mcp: FastMCP, guide_decorator: Any, log_tool_usage: Callable) -> None:
    """Register all MCP tools with the server."""

    # Project Management Tools
    guide_decorator.tool()(log_tool_usage(get_current_project))
    guide_decorator.tool()(log_tool_usage(switch_project))

    # Configuration Tools
    guide_decorator.tool()(log_tool_usage(get_project_config))
    guide_decorator.tool()(log_tool_usage(set_project_config_values))
    guide_decorator.tool()(log_tool_usage(set_project_config))

    # Content Tools
    guide_decorator.tool()(log_tool_usage(get_guide))
    guide_decorator.tool()(log_tool_usage(get_language_guide))
    guide_decorator.tool()(log_tool_usage(get_project_context))
    guide_decorator.tool()(log_tool_usage(search_content))
    guide_decorator.tool()(log_tool_usage(show_guide))
    guide_decorator.tool()(log_tool_usage(show_language_guide))

    # File Tools
    guide_decorator.tool()(log_tool_usage(get_file_content))

    # Category Management Tools
    guide_decorator.tool()(log_tool_usage(add_category))
    guide_decorator.tool()(log_tool_usage(remove_category))
    guide_decorator.tool()(log_tool_usage(update_category))
    guide_decorator.tool()(log_tool_usage(list_categories))
    guide_decorator.tool()(log_tool_usage(get_category_content))

    # Collection Management Tools
    guide_decorator.tool()(log_tool_usage(add_collection))
    guide_decorator.tool()(log_tool_usage(update_collection))
    guide_decorator.tool()(log_tool_usage(list_collections))
    guide_decorator.tool()(log_tool_usage(remove_collection))

    # Prompt Tools
    guide_decorator.tool()(log_tool_usage(list_prompts))
