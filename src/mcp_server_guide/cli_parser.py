"""CLI parser with short-form argument mapping."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Any, Dict, Type

# Argument mapping from short-form to long-form
ARGUMENT_MAPPING = {
    # Phase commands
    "-h": "--help",
    "-d": "--discuss",
    "-p": "--plan",
    "-i": "--implement",
    "-c": "--check",
    "-s": "--status",
    "-q": "--search",
    # CRUD targets
    "-C": "--category",
    "-M": "--collection",
    "-D": "--document",
    # CRUD operations
    "-l": "--list",
    "-a": "--add",
    "-r": "--remove",
    "-u": "--update",
    "-A": "--add-to",
    "-R": "--remove-from",
    # Natural argument flags
    "-n": "--name",
    "-f": "--file",
    "-T": "--content",
}


@dataclass
class Command:
    """Structured command object."""

    type: str
    target: Optional[str] = None
    operation: Optional[str] = None
    category: Optional[str] = None
    data: Optional[Any] = None


class CommandHandler(ABC):
    """Base class for command handlers."""

    @abstractmethod
    async def handle(self, command: Command) -> str:
        """Handle a command and return result."""
        pass


class CommandRegistry:
    """Registry for command handlers with dispatch functionality."""

    def __init__(self) -> None:
        self.handlers: Dict[str, CommandHandler] = {}

    def register(self, command_type: str, handler: CommandHandler) -> None:
        """Register a handler for a command type."""
        self.handlers[command_type] = handler

    async def dispatch(self, command: Command) -> str:
        """Dispatch command to appropriate handler."""
        if command.type in self.handlers:
            return await self.handlers[command.type].handle(command)
        return f"Unknown command type: {command.type}"


# Global registry instance
_default_registry = CommandRegistry()


def register_handler(command_type: str, registry: Optional[CommandRegistry] = None) -> Any:
    """Decorator to register command handlers."""
    if registry is None:
        registry = _default_registry

    def decorator(handler_class: Type[CommandHandler]) -> Type[CommandHandler]:
        handler_instance = handler_class()
        registry.register(command_type, handler_instance)
        return handler_class

    return decorator


def _flag_needs_argument(flag: str, target: Optional[str] = None) -> bool:
    """Determine if a flag needs an argument based on context."""
    # Flags that always need arguments
    always_need_args = {"-n", "-f", "-T"}
    if flag in always_need_args:
        return True

    # Phase commands that can take optional arguments
    phase_commands = {"-d", "-p", "-i", "-c", "-s", "-q"}
    if flag in phase_commands:
        return True

    # Context-sensitive argument flags (support both short and long form targets)
    context_args = {
        "-D": {"-C"},
        "--document": {"-C"},
        "-C": {"-D"},
        "--category": {"-D"},
        "-M": {"-C"},
        "--collection": {"-C"},
    }

    return flag in context_args.get(target or "", set())


def normalize_args(args: List[str]) -> List[str]:
    """Convert short-form arguments to long-form and handle concatenation.

    Args:
        args: List of command line arguments

    Returns:
        List of arguments with short-forms converted to long-forms
    """
    result: List[str] = []
    i = 0

    while i < len(args):
        arg = args[i]

        # Handle concatenated flags (single dash, multiple chars, not just numbers)
        if arg.startswith("-") and len(arg) > 2 and not arg.startswith("--") and not arg[1:].isdigit():
            # Expand concatenated flags
            expanded = []
            for char in arg[1:]:
                expanded.append(f"-{char}")

            # Find target to determine context (check both expanded flags and existing args)
            target_flags = {"-D", "-C", "-M", "--document", "--category", "--collection"}
            target = None

            # First check if target already exists in previous args
            for prev_arg in result:
                if prev_arg in target_flags:
                    target = prev_arg
                    break

            # If no target found, check in current expanded flags
            if target is None:
                for flag in expanded:
                    if flag in target_flags:
                        target = flag
                        break

            # Process expanded flags with argument positioning
            j = i + 1
            for flag in expanded:
                mapped_flag = ARGUMENT_MAPPING.get(flag, flag)
                result.append(mapped_flag)

                # Handle flags that need arguments in target context
                if _flag_needs_argument(flag, target) and j < len(args):
                    result.append(args[j])
                    j += 1

            i = j
        else:
            # Use standard mapping
            mapped_arg = ARGUMENT_MAPPING.get(arg, arg)
            result.append(mapped_arg)

            # Handle phase commands that need arguments
            if _flag_needs_argument(arg) and i + 1 < len(args):
                result.append(args[i + 1])
                i += 2
            else:
                i += 1

    return result


def parse_command(args: List[str]) -> Command:
    """Parse command line arguments into structured command object.

    Args:
        args: List of command line arguments

    Returns:
        Command object with parsed structure
    """
    # Input is already List[str], no string processing needed
    processed_args = args[:]

    normalized = normalize_args(processed_args)

    # Help command (check for target-specific help)
    if "--help" in normalized:
        target = None
        target_flags = {"--document": "document", "--category": "category", "--collection": "collection"}
        for flag, target_name in target_flags.items():
            if flag in normalized:
                target = target_name
                break
        return Command(type="help", target=target)

    # Phase commands with data
    phase_commands = {
        "--discuss": "discuss",
        "--plan": "plan",
        "--implement": "implement",
        "--check": "check",
        "--status": "status",
        "--search": "search",
    }

    for flag, cmd_type in phase_commands.items():
        if flag in normalized:
            idx = normalized.index(flag)
            # Collect all arguments after the phase command that don't start with --
            data_parts = []
            for i in range(idx + 1, len(normalized)):
                if normalized[i].startswith("--"):
                    break
                data_parts.append(normalized[i])

            # Join all parts into a single string, or None if no parts
            data = " ".join(data_parts) if data_parts else None
            return Command(type=cmd_type, data=data)

    # CRUD commands
    crud_targets = {"--category": "category", "--collection": "collection", "--document": "document"}
    crud_operations = {
        "--list": "list",
        "--add": "add",
        "--remove": "remove",
        "--update": "update",
        "--add-to": "add-to",
        "--remove-from": "remove-from",
    }

    target = None
    operation = None

    # Find CRUD target (must be at the beginning, not as an argument)
    for i, arg in enumerate(normalized):
        if arg in crud_targets:
            # Only consider it a target if it's not preceded by another flag that would use it as an argument
            if i == 0 or not _is_argument_flag(normalized[i - 1]):
                target = crud_targets[arg]
                break

    for flag, op_name in crud_operations.items():
        if flag in normalized:
            operation = op_name
            break

    if target and operation:
        # Parse natural arguments into structured data
        crud_data = _parse_natural_arguments(normalized, target, operation)
        return Command(type="crud", target=target, operation=operation, data=crud_data)

    # Legacy content command (single argument that doesn't start with --)
    if len(normalized) == 1 and not normalized[0].startswith("--"):
        return Command(type="content", category=normalized[0])

    # Default fallback
    return Command(type="unknown", data=normalized)


def _parse_natural_arguments(args: List[str], target: str, operation: str) -> Dict[str, Any]:
    """Parse natural CLI arguments into structured data for operations.

    Args:
        args: Normalized command line arguments
        target: CRUD target (category, collection, document)
        operation: CRUD operation (list, add, remove, update, etc.)

    Returns:
        Structured data for the operation
    """
    data: Dict[str, Any] = {}
    i = 0

    # Common argument patterns
    arg_patterns = {
        "--name": "name",
        "--category": "category",
        "--collection": "collection",
        "--content": "content",
        "--file": "file",
        "--description": "description",
        "--dir": "dir",
        "--patterns": "patterns",
        "--categories": "categories",
    }

    while i < len(args):
        arg = args[i]

        if arg in arg_patterns:
            key = arg_patterns[arg]
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1]

                # Handle special cases
                if key == "patterns" or key == "categories":
                    # Split comma-separated values
                    data[key] = [v.strip() for v in value.split(",")]
                else:
                    data[key] = value
                i += 2
            else:
                i += 1
        else:
            # Handle positional arguments based on context
            if not arg.startswith("--") and not _is_operation_or_target(arg):
                if target == "document" and "name" not in data:
                    # First non-flag argument is document name
                    data["name"] = arg
                elif target == "category" and "name" not in data:
                    # First non-flag argument is category name
                    data["name"] = arg
                elif target == "collection" and "name" not in data:
                    # First non-flag argument is collection name
                    data["name"] = arg
            i += 1

    # Handle operation-specific defaults and requirements
    if operation == "list":
        if target == "document" and "category" not in data:
            # For document listing, if no category specified, list all
            data["category"] = "all"
        elif target == "category" and not data:
            # For category listing, no additional data needed
            data = {}
        elif target == "collection" and not data:
            # For collection listing, no additional data needed
            data = {}

    return data if data else {}


def _is_argument_flag(arg: str) -> bool:
    """Check if argument is a flag that takes a value."""
    argument_flags = {"--name", "--content", "--file", "--description", "--dir", "--patterns", "--categories"}
    return arg in argument_flags


def _is_operation_or_target(arg: str) -> bool:
    """Check if argument is an operation or target flag."""
    operations = {"--list", "--add", "--remove", "--update", "--add-to", "--remove-from"}
    targets = {"--category", "--collection", "--document"}
    phases = {"--discuss", "--plan", "--implement", "--check", "--status", "--search", "--help"}
    return arg in operations or arg in targets or arg in phases
