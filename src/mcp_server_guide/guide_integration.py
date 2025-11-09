"""Guide prompt integration with sophisticated CLI parsing support."""

from typing import List
from .logging_config import get_logger
from .utils.error_handler import ErrorHandler
from .tools.category_tools import get_category_content
from .tools.collection_tools import get_collection_content
from .cli_parser import parse_command, Command

logger = get_logger(__name__)


class GuidePromptHandler:
    """Guide prompt handler with sophisticated CLI parsing support."""

    def __init__(self) -> None:
        self.error_handler = ErrorHandler()

    async def handle_guide_request(self, args: List[str]) -> str:
        """Handle guide prompt request with sophisticated CLI parsing."""
        if not args:
            return "Guide: Provide a category name, collection name, or category/document path.\nExample: @guide docs/readme"

        # Parse command using sophisticated CLI parser
        command = parse_command(args)

        # Route based on command type
        if command.type in ["discuss", "plan", "implement", "check", "status", "search"]:
            return await self._handle_phase_command(command)
        elif command.type == "help":
            return await self._handle_help_command(command)
        elif command.type == "crud":
            return await self._handle_crud_command(command)
        elif command.type == "content":
            return await self._handle_content_command(command)
        elif command.type == "unknown":
            # Fallback to legacy behavior for simple content access
            if len(args) == 1 and not args[0].startswith("-"):
                return await self._handle_legacy_content(args[0])
            else:
                return f"Error: Unknown command format: {' '.join(args)}"
        else:
            return f"Error: Unsupported command type: {command.type}"

    async def _handle_phase_command(self, command: Command) -> str:
        """Handle phase commands (discuss, plan, implement, check, status, search)."""
        # Import prompt functions
        from .prompts import implement_prompt, plan_prompt, discuss_prompt, check_prompt, status_prompt

        # Route to appropriate prompt function
        if command.type == "implement":
            return await implement_prompt(command.data)
        elif command.type == "plan":
            return await plan_prompt(command.data)
        elif command.type == "discuss":
            return await discuss_prompt(command.data)
        elif command.type == "check":
            return await check_prompt(command.data)
        elif command.type == "status":
            return await status_prompt(command.data)
        elif command.type == "search":
            # TODO: Implement search functionality
            return f"Search functionality not yet implemented. Query: {command.data}"
        else:
            return f"Error: Unknown phase command: {command.type}"

    async def _handle_help_command(self, command: Command) -> str:
        """Handle help commands."""
        from .help_system import format_guide_help

        return await format_guide_help()

    async def _handle_crud_command(self, command: Command) -> str:
        """Handle CRUD commands (category, collection, document operations)."""
        # TODO: Implement CRUD command handling
        return f"CRUD operations not yet implemented. Target: {command.target}, Operation: {command.operation}, Data: {command.data}"

    async def _handle_content_command(self, command: Command) -> str:
        """Handle content access commands."""
        if command.category is None:
            return "Error: No category specified"
        return await self._handle_legacy_content(command.category)

    async def _handle_legacy_content(self, arg: str) -> str:
        """Handle legacy content access (category/document or collection lookup)."""
        # Core functionality - check for document-specific access first
        if "/" in arg:
            category, document = arg.split("/", 1)
            category_result = await get_category_content(category, None, file=document)
            if category_result.get("success"):
                return str(category_result.get("content", ""))
            else:
                return f"Error: {category_result.get('error', 'Unknown error')}"
        else:
            # Try category first, then collection
            category_result = await get_category_content(arg, None)
            if category_result.get("success"):
                return str(category_result.get("content", ""))
            else:
                # If category lookup failed, try collection lookup
                collection_result = await get_collection_content(arg, None)
                if collection_result.get("success"):
                    return str(collection_result.get("content", ""))
                else:
                    # Both failed, return the original category error
                    return f"Error: {category_result.get('error', 'Unknown error')}"
