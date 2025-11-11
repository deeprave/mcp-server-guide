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
                return f"CRUD operations not yet implemented. Target: {command.target}, Operation: {command.operation}, Data: {command.data}"
            case "content":
                return await self._handle_content_command(command)
            case _:
                # Handle unknown commands - try content lookup
                if len(args) == 1 and not args[0].startswith("-"):
                    return await self._get_content(args[0])
                else:
                    return f"Error: Unknown command format: {' '.join(args)}"

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
