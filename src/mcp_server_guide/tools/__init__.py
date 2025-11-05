from .project_tools import get_current_project, switch_project
from .config_tools import (
    get_project_config,
    set_project_config,
    set_project_config_values,
)
from .content_tools import (
    search_content,
    get_guide,
)
from .file_tools import get_file_content
from .category_tools import (
    add_category,
    remove_category,
    update_category,
    list_categories,
    get_category_content,
)
from .collection_tools import (
    add_collection,
    update_collection,
    list_collections,
    remove_collection,
    get_collection_content,
)
from .prompt_tools import list_prompts, list_resources
from .document_tools import (
    create_mcp_document,
    update_mcp_document,
    delete_mcp_document,
    list_mcp_documents,
)

__all__ = [
    # Project Management
    "get_current_project",
    "switch_project",
    # Configuration Access
    "get_project_config",
    "set_project_config",
    "set_project_config_values",
    # Content Retrieval
    "search_content",
    "get_guide",
    # File Operations
    "get_file_content",
    # Category Management
    "add_category",
    "remove_category",
    "update_category",
    "list_categories",
    "get_category_content",
    # Collection Management
    "add_collection",
    "update_collection",
    "list_collections",
    "remove_collection",
    "get_collection_content",
    # Prompt Discovery
    "list_prompts",
    "list_resources",
    # Document Management
    "create_mcp_document",
    "update_mcp_document",
    "delete_mcp_document",
    "list_mcp_documents",
]
