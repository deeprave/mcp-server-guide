"""All MCP tools consolidated in a single module.

IMPORTANT: ALL TOOLS MUST BE REGISTERED HERE IN register_tools()
DO NOT USE @guide.tool() DECORATORS IN TOOL DEFINITIONS
Tools are plain functions - decoration happens only during registration
"""

from typing import Callable
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
from .tools.document_tools import create_mcp_document, update_mcp_document, delete_mcp_document, list_mcp_documents
from .tools.category_tools import add_category, remove_category, update_category, list_categories, get_category_content
from .tools.collection_tools import add_collection, update_collection, list_collections, remove_collection
from .tools.prompt_tools import list_prompts


def register_tools(mcp: FastMCP, log_tool_usage: Callable) -> None:
    """Register all MCP tools with the server.

    IMPORTANT: This is the ONLY place where tools are registered.
    All new tools must be added here - do not use decorators in tool files.
    """

    # Import here to avoid circular imports
    from .tool_decoration import ExtMcpToolDecorator

    # Create the guide decorator with the server
    guide_decorator = ExtMcpToolDecorator(mcp, prefix="guide_")

    # Project Management Tools
    guide_decorator.tool("get_current_project")(log_tool_usage(get_current_project))
    guide_decorator.tool("switch_project")(log_tool_usage(switch_project))

    # Configuration Tools
    guide_decorator.tool("get_project_config")(log_tool_usage(get_project_config))
    guide_decorator.tool("set_project_config_values")(log_tool_usage(set_project_config_values))
    guide_decorator.tool("set_project_config")(log_tool_usage(set_project_config))

    # Content Tools
    guide_decorator.tool("get_guide")(log_tool_usage(get_guide))
    guide_decorator.tool("get_language_guide")(log_tool_usage(get_language_guide))
    guide_decorator.tool("get_project_context")(log_tool_usage(get_project_context))
    guide_decorator.tool("search_content")(log_tool_usage(search_content))
    guide_decorator.tool("show_guide")(log_tool_usage(show_guide))
    guide_decorator.tool("show_language_guide")(log_tool_usage(show_language_guide))

    # File Tools
    guide_decorator.tool("get_file_content")(log_tool_usage(get_file_content))

    # Document Management Tools
    guide_decorator.tool("create_mcp_document")(log_tool_usage(create_mcp_document))
    guide_decorator.tool("update_mcp_document")(log_tool_usage(update_mcp_document))
    guide_decorator.tool("delete_mcp_document")(log_tool_usage(delete_mcp_document))
    guide_decorator.tool("list_mcp_documents")(log_tool_usage(list_mcp_documents))

    # Category Management Tools
    guide_decorator.tool("add_category")(log_tool_usage(add_category))
    guide_decorator.tool("remove_category")(log_tool_usage(remove_category))
    guide_decorator.tool("update_category")(log_tool_usage(update_category))
    guide_decorator.tool("list_categories")(log_tool_usage(list_categories))
    guide_decorator.tool("get_category_content")(log_tool_usage(get_category_content))

    # Collection Management Tools
    guide_decorator.tool("add_collection")(log_tool_usage(add_collection))
    guide_decorator.tool("update_collection")(log_tool_usage(update_collection))
    guide_decorator.tool("list_collections")(log_tool_usage(list_collections))
    guide_decorator.tool("remove_collection")(log_tool_usage(remove_collection))

    # Prompt Tools
    guide_decorator.tool("list_prompts")(log_tool_usage(list_prompts))
