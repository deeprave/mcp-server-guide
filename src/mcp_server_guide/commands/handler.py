"""Command handler for executing slash commands."""

from typing import Dict, Any, List, Optional
from ..tools.content_tools import get_all_guides, get_category_content
from ..tools.category_tools import add_category, update_category, list_categories


class CommandHandler:
    """Handler for executing parsed slash commands."""

    def __init__(self) -> None:
        """Initialize command handler."""
        pass

    async def execute_command(
        self, command: str, args: List[str], params: Optional[Dict[str, Any]] = None, subcommand: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a parsed command.

        Args:
            command: The command name (without slash)
            args: List of command arguments
            params: Dictionary of parsed parameters
            subcommand: Optional subcommand for colon syntax

        Returns:
            Dict with success status and content or error
        """
        if params is None:
            params = {}

        # Handle colon syntax commands
        if subcommand is not None:
            return await self._execute_colon_command(command, subcommand, args, params)

        if command == "guide":
            return await self._execute_guide_command(args)
        elif command == "guide-new":
            return await self._execute_guide_new_command(args, params)
        elif command == "guide-edit":
            return await self._execute_guide_edit_command(args, params)
        elif command == "guide-del":
            return await self._execute_guide_del_command(args, params)

        # Try as category shortcut (/<category>)
        return await self._try_category_shortcut(command, args)

    async def _execute_colon_command(
        self, command: str, subcommand: str, args: List[str], params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute colon syntax commands (/guide:subcommand or /g:subcommand).

        Args:
            command: Main command (guide or g)
            subcommand: Subcommand after colon
            args: Command arguments
            params: Command parameters

        Returns:
            Dict with success status and content or error
        """
        # Both /guide: and /g: work the same way
        if command not in ["guide", "g"]:
            return {"success": False, "error": f"Unknown command: {command}"}

        # Handle help subcommand
        if subcommand == "help":
            return await self._execute_help_command()

        # Handle management subcommands
        if subcommand == "new":
            return await self._execute_guide_new_command(args, params)
        elif subcommand == "edit":
            return await self._execute_guide_edit_command(args, params)
        elif subcommand == "del":
            return await self._execute_guide_del_command(args, params)

        # Handle category subcommands (e.g., /guide:lang, /g:context)
        return await self._execute_category_command(subcommand, args)

    async def _execute_guide_command(self, args: List[str]) -> Dict[str, Any]:
        """Execute guide command variants.

        Args:
            args: Command arguments

        Returns:
            Dict with success status and content
        """
        try:
            if not args or (len(args) == 1 and args[0] == "all"):
                # /guide or /guide all - show all guides
                content = await get_all_guides()
                return {"success": True, "content": content}
            else:
                # /guide <category> - show specific category
                category = args[0]
                # Validate category: non-empty, only allow alphanumeric, dash, underscore
                import re

                if not category or not re.match(r"^[\w-]+$", category):
                    return {
                        "success": False,
                        "error": f"Invalid category name: '{category}'. "
                        "Only letters, numbers, dash, and underscore are allowed.",
                    }
                result = await get_category_content(category, None)
                if result.get("success"):
                    return {"success": True, "content": result["content"]}
                else:
                    return {"success": False, "error": result.get("error", f"Failed to get category: {category}")}
        except Exception as e:
            return {"success": False, "error": f"Error executing guide command: {str(e)}"}

    async def _execute_guide_new_command(self, args: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute guide-new command.

        Args:
            args: Command arguments (category name)
            params: Command parameters

        Returns:
            Dict with success status and message
        """
        if not args:
            return {"success": False, "error": "Category name is required for guide-new command"}

        category_name = args[0]

        # Sanitize category_name for use as a directory name
        import re

        def sanitize_dir_name(name: str) -> str:
            return re.sub(r"[^A-Za-z0-9_\-]", "_", name.strip())

        # Apply defaults
        if "dir" in params:
            dir_path = params["dir"]
        else:
            dir_path = sanitize_dir_name(category_name)
        patterns = params.get("patterns", ["*.md"])
        auto_load = params.get("auto-load", False)
        description = params.get("description", "")

        try:
            result = await add_category(
                name=category_name,
                dir=dir_path,
                patterns=patterns,
                description=description,
                project=None,
                auto_load=auto_load,
            )
            return result
        except Exception as e:
            return {"success": False, "error": f"Error creating category: {str(e)}"}

    async def _execute_guide_edit_command(self, args: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute guide-edit command.

        Args:
            args: Command arguments (category name)
            params: Command parameters (only provided ones will be updated)

        Returns:
            Dict with success status and message
        """
        if not args:
            return {"success": False, "error": "Category name is required for guide-edit command"}

        category_name = args[0]

        try:
            # Get current categories to find existing values
            categories_result = await list_categories(None)
            all_categories = {**categories_result["builtin_categories"], **categories_result["custom_categories"]}

            if category_name not in all_categories:
                return {"success": False, "error": f"Category '{category_name}' not found"}

            current_category = all_categories[category_name]

            # Use provided params or fall back to current values
            dir_path = params.get("dir", current_category["dir"])
            patterns = params.get("patterns", current_category["patterns"])
            description = params.get("description", current_category.get("description", ""))
            auto_load = params.get("auto-load", current_category.get("auto_load"))

            result = await update_category(
                name=category_name,
                dir=dir_path,
                patterns=patterns,
                description=description,
                project=None,
                auto_load=auto_load,
            )
            return result
        except Exception as e:
            return {"success": False, "error": f"Error updating category: {str(e)}"}

    async def _execute_guide_del_command(self, args: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute guide-del command with confirmation.

        Args:
            args: Command arguments (category name)
            params: Command parameters

        Returns:
            Dict with success status and confirmation request
        """
        if not args:
            return {"success": False, "error": "Category name is required for guide-del command"}

        category_name = args[0]

        # For now, just return confirmation request
        # In a real implementation, this would need a confirmation mechanism
        return {
            "success": True,
            "confirm": f"Are you sure you want to delete category '{category_name}'?",
            "category": category_name,
        }

    async def _try_category_shortcut(self, category: str, args: List[str]) -> Dict[str, Any]:
        """Try to execute command as category shortcut.

        Args:
            category: Category name to try
            args: Command arguments (should be empty for shortcuts)

        Returns:
            Dict with success status and content or error
        """
        # Validate category: non-empty, only allow alphanumeric, dash, underscore
        import re

        if not category or not re.match(r"^[\w-]+$", category):
            return {
                "success": False,
                "error": f"Invalid category name: '{category}'. "
                "Only letters, numbers, dash, and underscore are allowed.",
            }

        try:
            result = await get_category_content(category, None)
            if result.get("success"):
                return {"success": True, "content": result["content"]}
            else:
                return {"success": False, "error": result.get("error", f"Category not found: {category}")}
        except Exception as e:
            return {"success": False, "error": f"Error accessing category {category}: {str(e)}"}

    async def _execute_help_command(self) -> Dict[str, Any]:
        """Execute help command to show available commands and categories.

        Returns:
            Dict with success status and help content
        """
        try:
            # Get available categories
            categories_result = await list_categories(None)

            help_content = {
                "commands": {
                    "/guide": "Show all guides",
                    "/guide:<category>": "Show specific category content",
                    "/g:<category>": "Show specific category content (shorthand)",
                    "/guide:help": "Show this help",
                    "/g:help": "Show this help (shorthand)",
                    "/guide:new <name> [params]": "Create new category",
                    "/g:new <name> [params]": "Create new category (shorthand)",
                    "/guide:edit <name> [params]": "Edit existing category",
                    "/g:edit <name> [params]": "Edit existing category (shorthand)",
                    "/guide:del <name>": "Delete category",
                    "/g:del <name>": "Delete category (shorthand)",
                },
                "categories": {
                    "builtin": [cat["name"] for cat in categories_result.get("builtin_categories", [])],
                    "custom": [cat["name"] for cat in categories_result.get("custom_categories", [])],
                },
                "examples": [
                    "/guide",
                    "/guide:lang",
                    "/g:context",
                    "/guide:new typescript dir=lang/ts patterns=*.ts,*.tsx",
                    "/g:edit typescript patterns=*.ts,*.tsx,*.d.ts",
                    "/guide:del typescript",
                ],
            }

            return {"success": True, "help": help_content}
        except Exception as e:
            return {"success": False, "error": f"Error generating help: {str(e)}"}

    async def _execute_category_command(self, category: str, args: List[str]) -> Dict[str, Any]:
        """Execute category command (e.g., /guide:lang, /g:context).

        Args:
            category: Category name
            args: Command arguments (should be empty for category commands)

        Returns:
            Dict with success status and content or error
        """
        # Validate category: non-empty, only allow alphanumeric, dash, underscore
        import re

        if not category or not re.match(r"^[\w-]+$", category):
            return {
                "success": False,
                "error": f"Invalid category name: '{category}'. "
                "Only letters, numbers, dash, and underscore are allowed.",
            }

        try:
            result = await get_category_content(category, None)
            if result.get("success"):
                return {"success": True, "content": result["content"]}
            else:
                return {"success": False, "error": result.get("error", f"Category not found: {category}")}
        except Exception as e:
            return {"success": False, "error": f"Error accessing category {category}: {str(e)}"}
