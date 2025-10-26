"""Command handler for executing slash commands."""

import shlex
from typing import Dict, Any, List, Optional

from ..utils import normalize_patterns, is_valid_name
from ..tools.content_tools import get_all_guides, get_category_content
from ..tools.category_tools import (
    add_category,
    update_category,
    list_categories,
    add_to_category,
    remove_from_category,
    remove_category,
)
from ..tools.collection_tools import (
    add_collection,
    update_collection,
    list_collections,
    add_to_collection,
    remove_from_collection,
    remove_collection,
)


def _parse_verbose_flag(params: Dict[str, Any], args: List[str]) -> bool:
    """Parse verbose flag from params and args."""
    verbose = False

    # Check params for verbose
    verbose_param = params.get("verbose", False)
    if isinstance(verbose_param, str):
        verbose_param_str = verbose_param.strip().lower()
        verbose = verbose_param_str in ("true", "1", "yes", "on")
    elif isinstance(verbose_param, bool):
        verbose = verbose_param
    else:
        verbose = bool(verbose_param)

    # Check args for verbose flags and --verbose=<value>
    for arg in args:
        if arg in ("-v", "--verbose"):
            verbose = True
        elif arg.startswith("--verbose="):
            value = arg.split("=", 1)[1].strip().lower()
            if value in ("true", "1", "yes", "on"):
                verbose = True
            elif value in ("false", "0", "no", "off"):
                verbose = False

    return verbose


class CommandHandler:
    """Handler for executing parsed slash commands."""

    def __init__(self) -> None:
        """Initialize command handler."""
        pass

    async def execute_command(
        self, command: str, args: List[str], params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a parsed command.

        Args:
            command: The command name (without slash)
            args: List of command arguments
            params: Dictionary of parsed parameters

        Returns:
            Dict with success status and content or error
        """
        if params is None:
            params = {}

        if command == "guide":
            return await self._execute_guide_command(args)
        elif command == "category":
            return await self._execute_category_command(args, params)
        elif command == "collection":
            return await self._execute_collection_command(args, params)

        # Try as content shortcut (collections first, then categories)
        return await self._try_content_shortcut(command, args)

    async def _execute_guide_command(self, args: List[str]) -> Dict[str, Any]:
        """Execute guide command variants."""
        try:
            if not args:
                # /guide - show usage and built-in guide content
                content = await get_all_guides()
                return {"success": True, "content": content}
            else:
                # /guide <name> - try category first, then collection
                name = args[0]

                # Standardized name validation (matches _try_content_shortcut)
                if not is_valid_name(name):
                    return {
                        "success": False,
                        "error": f"Invalid category/collection name: '{name}'. Only letters, numbers, dash, and underscore are allowed.",
                    }

                # Try category first
                result = await get_category_content(name, None)
                if result.get("success"):
                    return {"success": True, "content": result["content"]}

                # Try collection if category failed
                from ..tools.collection_tools import get_collection_content

                result = await get_collection_content(name, None)
                if result.get("success"):
                    return {"success": True, "content": result["content"]}

                return {"success": False, "error": f"Category or collection '{name}' not found"}
        except Exception as e:
            return {"success": False, "error": f"Error executing guide command: {str(e)}"}

    async def _execute_category_command(self, args: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute category command with subcommands."""
        if not args:
            return {
                "success": False,
                "error": "Category subcommand required (add, update, add-to, remove-from, remove, list)",
            }

        subcommand = args[0]

        if subcommand == "add":
            if len(args) < 3:
                return {
                    "success": False,
                    "error": (
                        "Usage: category add <name> <dir> [pattern1] [pattern2...] [--description 'desc']\n"
                        'Patterns are parsed using shell-like quoting rules. If a pattern contains spaces, enclose it in quotes (e.g., "my pattern").\n'
                        "Multiple patterns can be separated by spaces or quoted as needed."
                    ),
                }
            name, dir_path = args[1], args[2]
            # Use shlex to parse patterns, handling quoted patterns with spaces
            # **IMPORTANT INSTRUCTION**:
            # Don't do manual handling here, as it can lead to incorrect parsing.
            patterns_args = []
            i = 3
            while i < len(args) and not args[i].startswith("--"):
                patterns_args.append(args[i])
                i += 1

            # Join and robustly parse with shlex to handle quoted patterns properly
            if patterns_args:
                patterns_str = " ".join(patterns_args)
                try:
                    parsed_patterns = shlex.split(patterns_str)
                    add_patterns = normalize_patterns(parsed_patterns)
                except ValueError as e:
                    return {
                        "success": False,
                        "error": f"Malformed pattern input: {e}",
                    }
            else:
                add_patterns = []

            description = params.get("description")
            return await add_category(name, dir_path, add_patterns, description)

        elif subcommand == "update":
            if len(args) < 2:
                return {
                    "success": False,
                    "error": "Usage: category update <name> [--description 'desc'] [--dir 'path'] [--patterns 'p1,p2']",
                }
            name = args[1]
            description = params.get("description")
            dir_path = params.get("dir")  # type: ignore
            clear_patterns = params.get("clear-patterns", False)
            patterns_str_provided = "patterns" in params
            patterns_str = params.get("patterns")  # type: ignore

            # Validate conflicting pattern options
            if clear_patterns and patterns_str_provided:
                return {
                    "success": False,
                    "error": "Conflicting pattern options: Use either --clear-patterns to remove all patterns or --patterns to set new patterns.",
                }

            # Explicit clearing of patterns if --clear-patterns is set,
            # or if --patterns is provided as an empty string (documented behavior)
            patterns: Optional[List[str]]
            if clear_patterns:
                patterns = []
            elif patterns_str_provided:
                if patterns_str is not None and str(patterns_str).strip() != "":
                    patterns = normalize_patterns(patterns_str)
                else:
                    # Documented behavior: empty string for patterns clears all patterns
                    patterns = []
            else:
                patterns = None
            return await update_category(name, description=description, dir=dir_path, patterns=patterns)

        elif subcommand == "add-to":
            if len(args) < 3:
                return {"success": False, "error": "Usage: category add-to <name> <pattern1> [pattern2...]"}
            name = args[1]
            patterns = normalize_patterns(args[2:])
            return await add_to_category(name, patterns)

        elif subcommand == "remove-from":
            if len(args) < 3:
                return {"success": False, "error": "Usage: category remove-from <name> <pattern1> [pattern2...]"}
            name = args[1]
            patterns = normalize_patterns(args[2:])
            return await remove_from_category(name, patterns)

        elif subcommand == "remove":
            if len(args) < 2:
                return {"success": False, "error": "Usage: category remove <name>"}
            name = args[1]
            return await remove_category(name)

        elif subcommand == "list":
            verbose = _parse_verbose_flag(params, args)
            return await list_categories(verbose)

        else:
            return {"success": False, "error": f"Unknown category subcommand: {subcommand}"}

    async def _execute_collection_command(self, args: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute collection command with subcommands."""
        if not args:
            return {
                "success": False,
                "error": "Collection subcommand required (add, update, add-to, remove-from, remove, list)",
            }

        subcommand = args[0]

        if subcommand == "add":
            if len(args) < 3:
                return {
                    "success": False,
                    "error": "Usage: collection add <name> <cat1> [cat2...] [--description 'desc']",
                }
            name = args[1]
            categories = args[2:]
            description = params.get("description")
            return await add_collection(name, categories, description)

        elif subcommand == "update":
            if len(args) < 2:
                return {"success": False, "error": "Usage: collection update <name> [--description 'desc']"}
            name = args[1]
            description = params.get("description")
            return await update_collection(name, description=description)

        elif subcommand == "add-to":
            if len(args) < 3:
                return {"success": False, "error": "Usage: collection add-to <name> <cat1> [cat2...]"}
            name = args[1]
            categories = args[2:]
            return await add_to_collection(name, categories)

        elif subcommand == "remove-from":
            if len(args) < 3:
                return {"success": False, "error": "Usage: collection remove-from <name> <cat1> [cat2...]"}
            name = args[1]
            categories = args[2:]
            return await remove_from_collection(name, categories)

        elif subcommand == "remove":
            if len(args) < 2:
                return {"success": False, "error": "Usage: collection remove <name>"}
            name = args[1]
            return await remove_collection(name)

        elif subcommand == "list":
            verbose = _parse_verbose_flag(params, args)
            return await list_collections(verbose)

        else:
            return {"success": False, "error": f"Unknown collection subcommand: {subcommand}"}

    async def _try_content_shortcut(self, name: str, args: List[str]) -> Dict[str, Any]:
        """Try to execute command as collection or category shortcut (collections have precedence)."""
        if not is_valid_name(name):
            return {
                "success": False,
                "error": f"Invalid name: '{name}'. Only letters, numbers, dash, and underscore are allowed.",
            }

        try:
            # Try collection first (collections have precedence over categories)
            from ..tools.collection_tools import get_collection_content

            result = await get_collection_content(name, None)
            if result.get("success"):
                return {"success": True, "content": result["content"]}

            # Try category if collection failed
            result = await get_category_content(name, None)
            if result.get("success"):
                return {"success": True, "content": result["content"]}

            return {"success": False, "error": f"Category or collection '{name}' not found"}
        except Exception as e:
            return {"success": False, "error": f"Error accessing {name}: {str(e)}"}

    async def _execute_help_command(self) -> Dict[str, Any]:
        """Execute help command to show available commands and categories."""
        try:
            categories_result = await list_categories(False)
            collections_result = await list_collections(False)

            help_content = {
                "commands": {
                    "/guide": "Show all guides",
                    "/guide <category>": "Show specific category content",
                    "/category add <name> <dir> <pattern1> [pattern2...]": "Create new category",
                    "/category update <name> [--description 'desc'] [--dir 'path'] [--patterns 'p1,p2']": "Update category",
                    "/category add-to <name> <pattern1> [pattern2...]": "Add patterns to category",
                    "/category remove-from <name> <pattern1> [pattern2...]": "Remove patterns from category",
                    "/category remove <name>": "Delete category",
                    "/category list [-v|--verbose]": "List categories",
                    "/collection add <name> <cat1> [cat2...]": "Create new collection",
                    "/collection update <name> [--description 'desc']": "Update collection",
                    "/collection add-to <name> <cat1> [cat2...]": "Add categories to collection",
                    "/collection remove-from <name> <cat1> [cat2...]": "Remove categories from collection",
                    "/collection remove <name>": "Delete collection",
                    "/collection list [-v|--verbose]": "List collections",
                },
                "categories": list(categories_result.get("categories", {}).keys()),
                "collections": list(collections_result.get("collections", {}).keys()),
            }
            return {"success": True, "help": help_content}
        except Exception as e:
            return {"success": False, "error": f"Error generating help: {str(e)}"}
