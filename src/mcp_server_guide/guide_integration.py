"""Guide prompt integration with Click-based CLI parsing support."""

from typing import List, Optional

from mcp.server.fastmcp import Context

from .logging_config import get_logger
from .utils.error_handler import ErrorHandler
from .tools.category_tools import get_category_content
from .tools.collection_tools import get_collection_content
from .cli_parser_click import parse_command, Command

logger = get_logger(__name__)


class GuidePromptHandler:
    """Guide prompt handler with Click-based CLI parsing support."""

    def __init__(self) -> None:
        self.error_handler = ErrorHandler()

    async def handle_guide_request(self, args: List[str], ctx: Optional[Context] = None) -> str:
        """Handle guide prompt request with Click-based CLI parsing."""
        # Set up context project name in session manager if context is available
        if ctx:
            try:
                from .session_manager import SessionManager

                session_manager = SessionManager()
                await session_manager.ensure_context_project_loaded(ctx)
                logger.debug("Context project name set up from guide prompt")
            except Exception as e:
                logger.debug(f"Failed to set up context project name from guide prompt: {e}")

        if not args:
            return "Guide: Provide a category name, collection name, or category/document path.\nExample: @guide docs/readme"

        # Parse command using Click-based CLI parser
        command = parse_command(args)

        # Import all handlers
        from .prompts import implement_prompt, plan_prompt, discuss_prompt, check_prompt, status_prompt
        from .help_system import format_guide_help, generate_context_help

        # Direct dispatch with match
        match command.type:
            case "implement":
                return await implement_prompt(command.data)
            case "plan":
                return await plan_prompt(command.data)
            case "discuss":
                return await discuss_prompt(command.data)
            case "check":
                return await check_prompt(command.data)
            case "status":
                return await status_prompt(command.data)
            case "search":
                return f"Search functionality not yet implemented. Query: {command.data}"
            case "category_access":
                # Handle category access
                if command.category:
                    result = await get_category_content(command.category)
                    if result.get("success"):
                        return str(result.get("content", ""))
                    else:
                        # Try collection fallback
                        collection_result = await get_collection_content(command.category)
                        if collection_result.get("success"):
                            return str(collection_result.get("content", ""))
                        else:
                            return f"Category or collection '{command.category}' not found."
                else:
                    return "No category specified."
            case "help":
                if command.target:
                    # Context-sensitive help
                    return generate_context_help(command.target)
                else:
                    # General help - use verbose flag from CLI parser, default to False for basic help
                    verbose = command.data.get("verbose", False) if command.data else False
                    return await format_guide_help(verbose)
            case "crud":
                return await self._handle_crud_command(command)
            case "content":
                return await self._handle_content_command(command)
            case _:
                # Handle unknown commands - try content lookup
                if len(args) == 1 and not args[0].startswith("-"):
                    return await self._get_content(args[0])
                else:
                    return f"Error: Unknown command format: {' '.join(args)}"

    async def _handle_crud_command(self, command: Command) -> str:
        """Handle CRUD operations using the JSON tool factory."""
        try:
            # Import the JSON operation executor and display wrapper
            from .operations.base import execute_json_operation
            from .help_system import _wrap_display_content

            # Prepare data for the operation
            data = command.data or {}
            data["action"] = command.operation

            # Execute the operation - ensure target is not None
            if command.target is None:
                return _wrap_display_content("Error: No target specified for operation")

            result = await execute_json_operation(command.target, data)

            # Format the response
            if result.get("success"):
                # For list operations, format the output nicely
                if command.operation == "list":
                    # Handle different result formats based on target type
                    if command.target == "category":
                        # Categories are returned as a dict under 'categories' key
                        categories_dict = result.get("categories", {})
                        if not categories_dict:
                            return _wrap_display_content("No categories found.")

                        output = ["Categories:"]
                        for name, category_info in categories_dict.items():
                            if command.data and command.data.get("verbose"):
                                # Verbose output with additional details
                                desc = category_info.get("description", "")
                                if desc:
                                    output.append(f"  - {name}: {desc}")
                                else:
                                    output.append(f"  - {name}")
                            else:
                                # Simple list
                                output.append(f"  - {name}")
                        return _wrap_display_content("\n".join(output))

                    elif command.target == "collection":
                        # Collections are returned as a dict under 'collections' key
                        collections_dict = result.get("collections", {})
                        if not collections_dict:
                            return _wrap_display_content("No collections found.")

                        output = ["Collections:"]
                        for name, collection_info in collections_dict.items():
                            if command.data and command.data.get("verbose"):
                                # Verbose output with additional details
                                desc = collection_info.get("description", "")
                                if desc:
                                    output.append(f"  - {name}: {desc}")
                                else:
                                    output.append(f"  - {name}")
                            else:
                                # Simple list
                                output.append(f"  - {name}")
                        return _wrap_display_content("\n".join(output))

                    elif command.target == "document":
                        # Documents are returned as a list under 'documents' key
                        documents_list = result.get("documents", [])
                        if not documents_list:
                            return _wrap_display_content("No documents found.")

                        output = ["Documents:"]
                        for doc_info in documents_list:
                            if isinstance(doc_info, dict):
                                name = doc_info.get("name", "Unknown")
                                if command.data and command.data.get("verbose"):
                                    # Verbose output with additional details
                                    mime_type = doc_info.get("mime_type", "")
                                    if mime_type:
                                        output.append(f"  - {name} ({mime_type})")
                                    else:
                                        output.append(f"  - {name}")
                                else:
                                    # Simple list
                                    output.append(f"  - {name}")
                            else:
                                output.append(f"  - {doc_info}")
                        return _wrap_display_content("\n".join(output))

                    else:
                        # Fallback for other entities using 'items' format
                        items = result.get("items", [])
                        target = command.target or "item"  # Fallback if target is None
                        if not items:
                            entity_plural = target + "s"
                            return _wrap_display_content(f"No {entity_plural} found.")

                        # Format list output
                        entity_plural = target + "s"
                        output = [f"{entity_plural.title()}:"]
                        for item in items:
                            if isinstance(item, dict):
                                name = item.get("name", "Unknown")
                                if command.data and command.data.get("verbose"):
                                    # Verbose output with additional details
                                    desc = item.get("description", "")
                                    if desc:
                                        output.append(f"  - {name}: {desc}")
                                    else:
                                        output.append(f"  - {name}")
                                else:
                                    # Simple list
                                    output.append(f"  - {name}")
                            else:
                                output.append(f"  - {item}")
                        return _wrap_display_content("\n".join(output))
                else:
                    # For other operations, return the message or a success indicator
                    operation = command.operation or "operation"  # Fallback if operation is None
                    message = result.get("message", f"{operation.title()} operation completed successfully.")
                    return _wrap_display_content(message)
            else:
                error_msg = f"Error: {result.get('error', 'Unknown error occurred')}"
                return _wrap_display_content(error_msg)

        except Exception as e:
            logger.error(f"Error handling CRUD command: {e}", exc_info=True)
            operation = command.operation or "operation"
            target = command.target or "target"
            error_msg = f"Error executing {operation} on {target}: {str(e)}"
            return _wrap_display_content(error_msg)

    async def _handle_content_command(self, command: Command) -> str:
        """Handle content access commands."""
        if command.category is None:
            return "Error: No category specified"
        return await self._get_content(command.category)

    async def _get_content(self, arg: str) -> str:
        """Get content from category/document or collection lookup."""
        # Parse category and optional document
        args = arg.split("/", 1)
        category, document = args[0], args[1] if len(args) > 1 else None

        # Try category first
        category_result = await get_category_content(category, file=document)
        if category_result.get("success"):
            return str(category_result.get("content", ""))

        # If category failed and no document specified, try collection
        if document is None:
            collection_result = await get_collection_content(category)
            if collection_result.get("success"):
                return str(collection_result.get("content", ""))

        # Return the category error
        return f"Error: {category_result.get('error', 'Unknown error')}"
