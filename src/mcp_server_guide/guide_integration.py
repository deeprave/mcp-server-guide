"""Guide prompt integration with Click-based CLI parsing support."""

from typing import Any, List, Optional

from mcp.server.fastmcp import Context

from .agent_detection import format_agent_info
from .cli_parser_click import Command, parse_command
from .commands import (
    CMD_AGENT_INFO,
    CMD_CATEGORY,
    CMD_CHECK,
    CMD_CLONE,
    CMD_COLLECTION,
    CMD_CONFIG,
    CMD_DISCUSS,
    CMD_DOCUMENT,
    CMD_HELP,
    CMD_IMPLEMENT,
    CMD_PLAN,
    CMD_SEARCH,
    CMD_STATUS,
)
from .logging_config import get_logger
from .tools.category_tools import get_category_content
from .tools.collection_tools import get_collection_content
from .utils.error_handler import ErrorHandler

logger = get_logger(__name__)


class GuidePromptHandler:
    """Guide prompt handler with Click-based CLI parsing support."""

    def __init__(self) -> None:
        self.error_handler = ErrorHandler()

    async def handle_guide_request(self, args: List[str], ctx: Optional["Context[Any, Any]"] = None) -> str:
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
        from .help_system import format_guide_help, generate_context_help
        from .prompts import check_prompt, config_prompt, discuss_prompt, implement_prompt, plan_prompt, status_prompt

        # Command dispatch handlers
        async def handle_implement() -> str:
            return await implement_prompt(command.data)

        async def handle_plan() -> str:
            return await plan_prompt(command.data)

        async def handle_discuss() -> str:
            return await discuss_prompt(command.data)

        async def handle_check() -> str:
            return await check_prompt(command.data)

        async def handle_status() -> str:
            return await status_prompt(command.data)

        async def handle_config() -> str:
            project = command.data.get("project") if command.data else None
            list_projects = command.data.get("list_projects", False) if command.data else False
            verbose = command.data.get("verbose", False) if command.data else False
            return await config_prompt(project=project, list_projects=list_projects, verbose=verbose)

        async def handle_search() -> str:
            return f"Search functionality not yet implemented. Query: {command.data}"

        async def handle_clone() -> str:
            return await self._handle_clone_command(command)

        async def handle_help() -> str:
            import json

            # If Click captured help text, wrap it in JSON response
            if command.data and "help_text" in command.data:
                return json.dumps({
                    "success": True,
                    "value": str(command.data["help_text"]),
                    "instruction": "Present this information to the user, take no action and return to the prompt"
                })
            # Otherwise generate help
            if command.target:
                return generate_context_help(command.target)
            else:
                verbose = command.data.get("verbose", False) if command.data else False
                return await format_guide_help(verbose)

        async def handle_agent_info() -> str:
            return await self._handle_agent_info(ctx)

        async def handle_category_access() -> str:
            if command.category:
                result = await get_category_content(command.category)
                if result.get("success"):
                    return str(result.get("content", ""))
                else:
                    collection_result = await get_collection_content(command.category)
                    if collection_result.get("success"):
                        return str(collection_result.get("content", ""))
                    else:
                        return f"Category or collection '{command.category}' not found."
            else:
                return "No category specified."

        async def handle_crud() -> str:
            return await self._handle_crud_command(command)

        # Dispatch table
        handlers = {
            CMD_IMPLEMENT: handle_implement,
            CMD_PLAN: handle_plan,
            CMD_DISCUSS: handle_discuss,
            CMD_CHECK: handle_check,
            CMD_STATUS: handle_status,
            CMD_CONFIG: handle_config,
            CMD_SEARCH: handle_search,
            CMD_CLONE: handle_clone,
            CMD_HELP: handle_help,
            CMD_AGENT_INFO: handle_agent_info,
            "category_access": handle_category_access,
            "crud": handle_crud,
        }

        handler = handlers.get(command.type)
        if handler:
            return await handler()

        # Handle content command
        if command.type == "content":
            return await self._handle_content_command(command)

        # Handle unknown commands - try content lookup
        if len(args) == 1 and not args[0].startswith("-"):
            return await self._get_content(args[0])
        else:
            return f"Error: Unknown command format: {' '.join(args)}"

    async def _handle_agent_info(self, ctx: Optional["Context[Any, Any]"]) -> str:
        """Handle agent-info command to display detected agent information."""
        try:
            import json

            from .server import get_current_server

            server = await get_current_server()
            if not server:
                return json.dumps({"success": False, "error": "Server not available"})

            # Check cache
            if server.extensions.agent_info:
                agent_info = server.extensions.agent_info
                markdown_output = format_agent_info(agent_info, server.name, markdown=True)
                return json.dumps({"success": True, "value": markdown_output})
            else:
                # Not cached - instruct to call tool
                # Prompts may not have valid session context, so tool must be called
                return json.dumps(
                    {
                        "success": False,
                        "error": "Agent information not yet captured",
                        "remediation": "Call the get_agent_info tool to fetch and cache agent information",
                    }
                )
        except Exception as e:
            import json

            logger.error(f"Failed to get agent info: {e}")
            return json.dumps({"success": False, "error": f"Could not access agent info: {str(e)}"})

    async def _handle_crud_command(self, command: Command) -> str:
        """Handle CRUD operations using the JSON tool factory."""
        try:
            # Import the JSON operation executor and display wrapper
            from .help_system import _wrap_display_content
            from .operations.base import execute_json_operation

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
                    if command.target == CMD_CATEGORY:
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

                    elif command.target == CMD_COLLECTION:
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

                    elif command.target == CMD_DOCUMENT:
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

    async def _handle_clone_command(self, command: Command) -> str:
        """Handle project clone command."""
        from .help_system import _wrap_display_content
        from .tools.project_tools import clone_project

        if not command.data:
            return _wrap_display_content("Error: No clone parameters provided")

        source_project = command.data.get("source_project")
        target_project = command.data.get("target_project")
        force = command.data.get("force", False)

        if not source_project:
            return _wrap_display_content("Error: Source project name required")

        result = await clone_project(source_project=source_project, target_project=target_project, force=force)

        if result.get("success"):
            message = result.get("message", "Project cloned successfully")
            return _wrap_display_content(message)
        else:
            error_msg = result.get("error", "Clone operation failed")
            return _wrap_display_content(f"Error: {error_msg}")

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
