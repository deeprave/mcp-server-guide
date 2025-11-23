"""Click-based CLI parser for guide commands."""

from dataclasses import dataclass
from typing import Any, List, Optional

import click

from .commands import (
    ALL_COMMANDS,
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


@dataclass
class Command:
    """Structured command object."""

    type: str
    target: Optional[str] = None
    operation: Optional[str] = None
    category: Optional[str] = None
    data: Optional[Any] = None


def _set_result(ctx: click.Context, command: Command) -> None:
    """Set the command result in Click context."""
    # Set on the current context
    ctx.obj = command
    # Also set on the parent context if it exists
    if ctx.parent:
        ctx.parent.obj = command
        # For nested commands, also set on grandparent
        if ctx.parent.parent:
            ctx.parent.parent.obj = command


@click.group(invoke_without_command=True)
@click.pass_context
def guide(ctx: click.Context) -> None:
    """MCP Server Guide - Project documentation and guidelines."""
    if ctx.invoked_subcommand is None:
        _set_result(ctx, Command(type=CMD_HELP))


@guide.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed help information")
@click.pass_context
def help(ctx: click.Context, verbose: bool) -> None:
    """Show help information."""
    _set_result(ctx, Command(type=CMD_HELP, data={"verbose": verbose}))


@guide.command("agent-info")
@click.pass_context
def agent_info(ctx: click.Context) -> None:
    """Show detected agent information."""
    _set_result(ctx, Command(type=CMD_AGENT_INFO, data=None))


# Phase commands
@guide.command()
@click.argument("text", nargs=-1)
@click.pass_context
def discuss(ctx: click.Context, text: tuple[str, ...]) -> None:
    """Start discussion phase with optional text."""
    _set_result(ctx, Command(type=CMD_DISCUSS, data=" ".join(text) if text else None))


@guide.command()
@click.argument("text", nargs=-1)
@click.pass_context
def plan(ctx: click.Context, text: tuple[str, ...]) -> None:
    """Start planning phase with optional text."""
    _set_result(ctx, Command(type=CMD_PLAN, data=" ".join(text) if text else None))


@guide.command()
@click.argument("text", nargs=-1)
@click.pass_context
def implement(ctx: click.Context, text: tuple[str, ...]) -> None:
    """Start implementation phase with optional text."""
    _set_result(ctx, Command(type=CMD_IMPLEMENT, data=" ".join(text) if text else None))


@guide.command()
@click.argument("text", nargs=-1)
@click.pass_context
def check(ctx: click.Context, text: tuple[str, ...]) -> None:
    """Start check phase with optional text."""
    _set_result(ctx, Command(type=CMD_CHECK, data=" ".join(text) if text else None))


@guide.command()
@click.argument("text", nargs=-1)
@click.pass_context
def status(ctx: click.Context, text: tuple[str, ...]) -> None:
    """Show status with optional text."""
    _set_result(ctx, Command(type=CMD_STATUS, data=" ".join(text) if text else None))


@guide.command()
@click.argument("project", required=False)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
@click.option("--projects", is_flag=True, help="List all projects")
@click.pass_context
def config(ctx: click.Context, project: Optional[str], verbose: bool, projects: bool) -> None:
    """Display project configuration."""
    _set_result(ctx, Command(type=CMD_CONFIG, data={"project": project, "list_projects": projects, "verbose": verbose}))


@guide.command()
@click.argument("query", nargs=-1)
@click.pass_context
def search(ctx: click.Context, query: tuple[str, ...]) -> None:
    """Search with query."""
    _set_result(ctx, Command(type=CMD_SEARCH, data=" ".join(query) if query else None))


@guide.command()
@click.argument("source_project")
@click.argument("target_project", required=False)
@click.option("--force", is_flag=True, help="Overwrite target even if it has custom content")
@click.pass_context
def clone(ctx: click.Context, source_project: str, target_project: Optional[str], force: bool) -> None:
    """Clone project configuration from source to target."""
    _set_result(
        ctx,
        Command(
            type=CMD_CLONE,
            data={"source_project": source_project, "target_project": target_project, "force": force},
        ),
    )


# Category commands
@guide.group()
def category() -> None:
    """Category management operations."""
    pass


@category.command("list")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
@click.pass_context
def category_list(ctx: click.Context, verbose: bool) -> None:
    """List all categories."""
    _set_result(ctx, Command(type="crud", target=CMD_CATEGORY, operation="list", data={"verbose": verbose}))


@category.command("add")
@click.argument("name")
@click.argument("patterns", nargs=-1, required=True)
@click.option("--description", "-d", help="Category description")
@click.pass_context
def category_add(ctx: click.Context, name: str, patterns: tuple[str, ...], description: Optional[str]) -> None:
    """Add a new category with patterns."""
    _set_result(
        ctx,
        Command(
            type="crud",
            target=CMD_CATEGORY,
            operation="add",
            data={"name": name, "patterns": list(patterns), "description": description},
        ),
    )


@category.command("remove")
@click.argument("name")
@click.pass_context
def category_remove(ctx: click.Context, name: str) -> None:
    """Remove a category."""
    _set_result(ctx, Command(type="crud", target=CMD_CATEGORY, operation="remove", data={"name": name}))


@category.command("update")
@click.argument("name")
@click.option("--description", "-d", help="New description")
@click.option("--patterns", "-p", help="New patterns (comma-separated)")
@click.pass_context
def category_update(ctx: click.Context, name: str, description: Optional[str], patterns: Optional[str]) -> None:
    """Update a category."""
    data: dict[str, Any] = {"name": name}
    if description:
        data["description"] = description
    if patterns:
        data["patterns"] = [p.strip() for p in patterns.split(",")]
    _set_result(ctx, Command(type="crud", target=CMD_CATEGORY, operation="update", data=data))


@category.command("add-to")
@click.argument("name")
@click.argument("patterns", nargs=-1, required=True)
@click.pass_context
def category_add_to(ctx: click.Context, name: str, patterns: tuple[str, ...]) -> None:
    """Add patterns to existing category."""
    _set_result(
        ctx,
        Command(type="crud", target=CMD_CATEGORY, operation="add-to", data={"name": name, "patterns": list(patterns)}),
    )


@category.command("remove-from")
@click.argument("name")
@click.argument("patterns", nargs=-1, required=True)
@click.pass_context
def category_remove_from(ctx: click.Context, name: str, patterns: tuple[str, ...]) -> None:
    """Remove patterns from existing category."""
    _set_result(
        ctx,
        Command(
            type="crud", target=CMD_CATEGORY, operation="remove-from", data={"name": name, "patterns": list(patterns)}
        ),
    )


# Collection commands
@guide.group()
def collection() -> None:
    """Collection management operations."""
    pass


@collection.command("list")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
@click.pass_context
def collection_list(ctx: click.Context, verbose: bool) -> None:
    """List all collections."""
    _set_result(ctx, Command(type="crud", target=CMD_COLLECTION, operation="list", data={"verbose": verbose}))


@collection.command("add")
@click.argument("name")
@click.argument("categories", nargs=-1, required=True)
@click.option("--description", "-d", help="Collection description")
@click.pass_context
def collection_add(ctx: click.Context, name: str, categories: tuple[str, ...], description: Optional[str]) -> None:
    """Add a new collection with categories."""
    _set_result(
        ctx,
        Command(
            type="crud",
            target=CMD_COLLECTION,
            operation="add",
            data={"name": name, "categories": list(categories), "description": description},
        ),
    )


@collection.command("remove")
@click.argument("name")
@click.pass_context
def collection_remove(ctx: click.Context, name: str) -> None:
    """Remove a collection."""
    _set_result(ctx, Command(type="crud", target=CMD_COLLECTION, operation="remove", data={"name": name}))


@collection.command("update")
@click.argument("name")
@click.option("--description", "-d", help="New description")
@click.pass_context
def collection_update(ctx: click.Context, name: str, description: Optional[str]) -> None:
    """Update a collection description."""
    _set_result(
        ctx,
        Command(
            type="crud", target=CMD_COLLECTION, operation="update", data={"name": name, "description": description}
        ),
    )


@collection.command("add-to")
@click.argument("name")
@click.argument("categories", nargs=-1, required=True)
@click.pass_context
def collection_add_to(ctx: click.Context, name: str, categories: tuple[str, ...]) -> None:
    """Add categories to existing collection."""
    _set_result(
        ctx,
        Command(
            type="crud", target=CMD_COLLECTION, operation="add-to", data={"name": name, "categories": list(categories)}
        ),
    )


@collection.command("remove-from")
@click.argument("name")
@click.argument("categories", nargs=-1, required=True)
@click.pass_context
def collection_remove_from(ctx: click.Context, name: str, categories: tuple[str, ...]) -> None:
    """Remove categories from existing collection."""
    _set_result(
        ctx,
        Command(
            type="crud",
            target=CMD_COLLECTION,
            operation="remove-from",
            data={"name": name, "categories": list(categories)},
        ),
    )


# Document commands
@guide.group()
def document() -> None:
    """Document management operations."""
    pass


@document.command("list")
@click.pass_context
def document_list(ctx: click.Context) -> None:
    """List all documents."""
    _set_result(ctx, Command(type="crud", target=CMD_DOCUMENT, operation="list"))


@document.command("create")
@click.argument("name")
@click.argument("content")
@click.option("--mime-type", help="MIME type of the document")
@click.pass_context
def document_create(ctx: click.Context, name: str, content: str, mime_type: Optional[str]) -> None:
    """Create a new document."""
    data: dict[str, Any] = {"name": name, "content": content}
    if mime_type:
        data["mime_type"] = mime_type
    _set_result(ctx, Command(type="crud", target=CMD_DOCUMENT, operation="create", data=data))


@document.command("update")
@click.argument("name")
@click.argument("content")
@click.pass_context
def document_update(ctx: click.Context, name: str, content: str) -> None:
    """Update an existing document."""
    _set_result(
        ctx, Command(type="crud", target=CMD_DOCUMENT, operation="update", data={"name": name, "content": content})
    )


@document.command("delete")
@click.argument("name")
@click.pass_context
def document_delete(ctx: click.Context, name: str) -> None:
    """Delete a document."""
    _set_result(ctx, Command(type="crud", target=CMD_DOCUMENT, operation="delete", data={"name": name}))


def has_command_prefix(arg: str) -> bool:
    """Check if argument has command prefix (: or ;).

    Args:
        arg: Argument to check

    Returns:
        True if arg starts with : or ;, False otherwise
    """
    return arg.startswith(":") or arg.startswith(";")


def strip_command_prefix(arg: str) -> str:
    """Strip command prefix from argument.

    Args:
        arg: Argument to strip prefix from

    Returns:
        Argument without prefix if it had one, otherwise unchanged
    """
    return arg[1:] if has_command_prefix(arg) else arg


def parse_command(args: List[str]) -> Command:
    """Parse command line arguments using Click-based parser."""
    # Validate input arguments
    if args is None:
        return Command(type=CMD_HELP)

    if not args:
        return Command(type=CMD_HELP)

    # Validate all arguments are strings
    if not all(isinstance(arg, str) for arg in args):
        return Command(type=CMD_HELP)

    # Strip prefix if present
    had_prefix = has_command_prefix(args[0])
    args = [strip_command_prefix(args[0])] + args[1:]

    # If no prefix and single arg → category/collection access
    if not had_prefix and len(args) == 1 and not args[0].startswith("-") and args[0]:
        return Command(type="category_access", category=args[0])

    # Otherwise let Click handle everything
    try:
        ctx = guide.make_context("guide", args, resilient_parsing=True)
        guide.invoke(ctx)
        return ctx.obj or Command(type=CMD_HELP)
    except (click.ClickException, AssertionError, SystemExit, click.exceptions.Exit):
        return Command(type=CMD_HELP)
    except Exception:
        return Command(type=CMD_HELP)


def get_cli_commands() -> dict[str, Any]:
    """Extract command information from commands.py metadata."""
    from .commands import COMMANDS

    commands = {}
    for name, info in COMMANDS.items():
        # Use description from CommandInfo
        commands[f":{name}"] = info.description
    return commands


def generate_basic_cli_help() -> str:
    """Generate basic CLI usage help."""
    from .commands import COMMANDS, MANAGEMENT_COMMANDS, PHASE_COMMANDS, UTILITY_COMMANDS

    # Group commands by category
    phase_cmds = {f":{k}": v.description for k, v in COMMANDS.items() if k in PHASE_COMMANDS}
    utility_cmds = {f":{k}": v.description for k, v in COMMANDS.items() if k in UTILITY_COMMANDS}
    mgmt_cmds = {f":{k}": v.description for k, v in COMMANDS.items() if k in MANAGEMENT_COMMANDS}

    # Build sections
    sections = [
        "Usage: @guide [OPTIONS] COMMAND [ARGS]...",
        "",
        "MCP Server Guide - Project documentation and guidelines.",
        "",
        "Phase Commands:",
    ]

    for name, desc in sorted(phase_cmds.items()):
        sections.append(f"  {name:<15} {desc}")

    sections.extend(
        [
            "",
            "Utility Commands:",
        ]
    )

    for name, desc in sorted(utility_cmds.items()):
        sections.append(f"  {name:<15} {desc}")

    sections.extend(
        [
            "",
            "Management Commands:",
        ]
    )

    for name, desc in sorted(mgmt_cmds.items()):
        sections.append(f"  {name:<15} {desc}")

    sections.extend(
        [
            "",
            "Category/Collection Access:",
            "  <name>          Access category or collection content",
            "",
            "Use :help for more information",
        ]
    )

    return "\n".join(sections)


def generate_cli_help() -> str:
    """Generate comprehensive CLI help from Click command structure."""
    try:
        ctx = click.Context(guide)
        return guide.get_help(ctx)
    except (SystemExit, click.exceptions.Exit):
        # Catch Click exit exceptions that might cause server shutdown
        return "CLI Help (Click exit handled safely)"
    except click.ClickException as e:
        return f"CLI Help (Click error handled safely): {e}"
    except Exception as e:
        return f"CLI Help (Error handled safely): {e}"


def generate_context_help(target: Optional[str] = None, operation: Optional[str] = None) -> str:
    """Generate context-sensitive help for specific operations."""
    try:
        target_handlers = {
            CMD_CATEGORY: category,
            CMD_COLLECTION: collection,
            CMD_DOCUMENT: document,
        }

        if target in target_handlers:
            handler = target_handlers[target]
            ctx = click.Context(handler)
            return handler.get_help(ctx)

        return generate_cli_help()
    except (SystemExit, click.exceptions.Exit):
        # Catch Click exit exceptions that might cause server shutdown
        return f"Help for {target or 'general'} (Click exit handled safely)"
    except click.ClickException as e:
        return f"Help for {target or 'general'} (Click error handled safely): {e}"
    except Exception as e:
        return f"Help for {target or 'general'} (Error handled safely): {e}"
