"""Click-based CLI parser for guide commands."""

import click
from typing import List, Optional, Any
from dataclasses import dataclass


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
        _set_result(ctx, Command(type="help"))


@guide.command()
@click.pass_context
def help(ctx: click.Context) -> None:
    """Show help information."""
    _set_result(ctx, Command(type="help"))


# Phase commands
@guide.command()
@click.argument("text", nargs=-1)
@click.pass_context
def discuss(ctx: click.Context, text: tuple) -> None:
    """Start discussion phase with optional text."""
    _set_result(ctx, Command(type="discuss", data=" ".join(text) if text else None))


@guide.command()
@click.argument("text", nargs=-1)
@click.pass_context
def plan(ctx: click.Context, text: tuple) -> None:
    """Start planning phase with optional text."""
    _set_result(ctx, Command(type="plan", data=" ".join(text) if text else None))


@guide.command()
@click.argument("text", nargs=-1)
@click.pass_context
def implement(ctx: click.Context, text: tuple) -> None:
    """Start implementation phase with optional text."""
    _set_result(ctx, Command(type="implement", data=" ".join(text) if text else None))


@guide.command()
@click.argument("text", nargs=-1)
@click.pass_context
def check(ctx: click.Context, text: tuple) -> None:
    """Start check phase with optional text."""
    _set_result(ctx, Command(type="check", data=" ".join(text) if text else None))


@guide.command()
@click.argument("text", nargs=-1)
@click.pass_context
def status(ctx: click.Context, text: tuple) -> None:
    """Show status with optional text."""
    _set_result(ctx, Command(type="status", data=" ".join(text) if text else None))


@guide.command()
@click.argument("query", nargs=-1)
@click.pass_context
def search(ctx: click.Context, query: tuple) -> None:
    """Search with query."""
    _set_result(ctx, Command(type="search", data=" ".join(query) if query else None))


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
    _set_result(ctx, Command(type="crud", target="category", operation="list", data={"verbose": verbose}))


@category.command("add")
@click.argument("name")
@click.argument("patterns", nargs=-1, required=True)
@click.option("--description", "-d", help="Category description")
@click.pass_context
def category_add(ctx: click.Context, name: str, patterns: tuple, description: Optional[str]) -> None:
    """Add a new category with patterns."""
    _set_result(
        ctx,
        Command(
            type="crud",
            target="category",
            operation="add",
            data={"name": name, "patterns": list(patterns), "description": description},
        ),
    )


@category.command("remove")
@click.argument("name")
@click.pass_context
def category_remove(ctx: click.Context, name: str) -> None:
    """Remove a category."""
    _set_result(ctx, Command(type="crud", target="category", operation="remove", data={"name": name}))


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
    _set_result(ctx, Command(type="crud", target="category", operation="update", data=data))


@category.command("add-to")
@click.argument("name")
@click.argument("patterns", nargs=-1, required=True)
@click.pass_context
def category_add_to(ctx: click.Context, name: str, patterns: tuple) -> None:
    """Add patterns to existing category."""
    _set_result(
        ctx,
        Command(type="crud", target="category", operation="add-to", data={"name": name, "patterns": list(patterns)}),
    )


@category.command("remove-from")
@click.argument("name")
@click.argument("patterns", nargs=-1, required=True)
@click.pass_context
def category_remove_from(ctx: click.Context, name: str, patterns: tuple) -> None:
    """Remove patterns from existing category."""
    _set_result(
        ctx,
        Command(
            type="crud", target="category", operation="remove-from", data={"name": name, "patterns": list(patterns)}
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
    _set_result(ctx, Command(type="crud", target="collection", operation="list", data={"verbose": verbose}))


@collection.command("add")
@click.argument("name")
@click.argument("categories", nargs=-1, required=True)
@click.option("--description", "-d", help="Collection description")
@click.pass_context
def collection_add(ctx: click.Context, name: str, categories: tuple, description: Optional[str]) -> None:
    """Add a new collection with categories."""
    _set_result(
        ctx,
        Command(
            type="crud",
            target="collection",
            operation="add",
            data={"name": name, "categories": list(categories), "description": description},
        ),
    )


@collection.command("remove")
@click.argument("name")
@click.pass_context
def collection_remove(ctx: click.Context, name: str) -> None:
    """Remove a collection."""
    _set_result(ctx, Command(type="crud", target="collection", operation="remove", data={"name": name}))


@collection.command("update")
@click.argument("name")
@click.option("--description", "-d", help="New description")
@click.pass_context
def collection_update(ctx: click.Context, name: str, description: Optional[str]) -> None:
    """Update a collection description."""
    _set_result(
        ctx,
        Command(type="crud", target="collection", operation="update", data={"name": name, "description": description}),
    )


@collection.command("add-to")
@click.argument("name")
@click.argument("categories", nargs=-1, required=True)
@click.pass_context
def collection_add_to(ctx: click.Context, name: str, categories: tuple) -> None:
    """Add categories to existing collection."""
    _set_result(
        ctx,
        Command(
            type="crud", target="collection", operation="add-to", data={"name": name, "categories": list(categories)}
        ),
    )


@collection.command("remove-from")
@click.argument("name")
@click.argument("categories", nargs=-1, required=True)
@click.pass_context
def collection_remove_from(ctx: click.Context, name: str, categories: tuple) -> None:
    """Remove categories from existing collection."""
    _set_result(
        ctx,
        Command(
            type="crud",
            target="collection",
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
    _set_result(ctx, Command(type="crud", target="document", operation="list"))


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
    _set_result(ctx, Command(type="crud", target="document", operation="create", data=data))


@document.command("update")
@click.argument("name")
@click.argument("content")
@click.pass_context
def document_update(ctx: click.Context, name: str, content: str) -> None:
    """Update an existing document."""
    _set_result(
        ctx, Command(type="crud", target="document", operation="update", data={"name": name, "content": content})
    )


@document.command("delete")
@click.argument("name")
@click.pass_context
def document_delete(ctx: click.Context, name: str) -> None:
    """Delete a document."""
    _set_result(ctx, Command(type="crud", target="document", operation="delete", data={"name": name}))


def detect_help_request(args: List[str]) -> Optional[Command]:
    """Detect help requests before Click processing to avoid exceptions."""
    if not args or not all(isinstance(arg, str) for arg in args):
        return None

    # Pattern: [target] --help/-h
    if len(args) == 2 and args[1] in ["--help", "-h"]:
        target = args[0]
        if target in ["category", "collection", "document"]:
            return Command(type="help", target=target)

    # Pattern: --help/-h (general help)
    if len(args) == 1 and args[0] in ["--help", "-h"]:
        return Command(type="help")

    # Pattern: help [target]
    if len(args) >= 1 and args[0] == "help":
        help_target: Optional[str] = args[1] if len(args) > 1 else None
        if help_target and help_target in ["category", "collection", "document"]:
            return Command(type="help", target=help_target)
        elif len(args) == 1:  # Just "help"
            return Command(type="help")

    return None


def parse_command(args: List[str]) -> Command:
    """Parse command line arguments using Click-based parser."""
    # Validate input arguments
    if args is None:
        return Command(type="help")

    if not args:
        return Command(type="help")

    # Validate all arguments are strings
    if not all(isinstance(arg, str) for arg in args):
        return Command(type="help")

    # PRE-PARSE: Detect help requests before Click processing
    help_command = detect_help_request(args)
    if help_command:
        return help_command

    # Handle legacy short form commands first
    if args[0] in ["-d", "-p", "-i", "-c", "-s"]:
        command_map = {"-d": "discuss", "-p": "plan", "-i": "implement", "-c": "check", "-s": "status"}
        command_type = command_map[args[0]]
        data = " ".join(args[1:]) if len(args) > 1 else None
        return Command(type=command_type, data=data)

    # Handle direct category/collection access (legacy behavior)
    if (
        len(args) == 1
        and not args[0].startswith("-")
        and args[0]  # Ensure not empty string
        and args[0]
        not in [
            "help",
            "category",
            "collection",
            "document",
            "discuss",
            "plan",
            "implement",
            "check",
            "status",
            "search",
        ]
    ):
        return Command(type="category_access", category=args[0])

    try:
        # Create a Click context and parse the arguments
        ctx = guide.make_context("guide", args, resilient_parsing=True)
        guide.invoke(ctx)
        # Return the command stored in context, or default to help
        return ctx.obj or Command(type="help")
    except (click.ClickException, AssertionError, SystemExit, click.exceptions.Exit):
        # If parsing fails or command not found, return help command
        return Command(type="help")
    except Exception:
        # Any other error, return help
        return Command(type="help")


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
        if target == "category":
            ctx = click.Context(category)
            return category.get_help(ctx)
        elif target == "collection":
            ctx = click.Context(collection)
            return collection.get_help(ctx)
        elif target == "document":
            ctx = click.Context(document)
            return document.get_help(ctx)
        else:
            return generate_cli_help()
    except (SystemExit, click.exceptions.Exit):
        # Catch Click exit exceptions that might cause server shutdown
        return f"Help for {target or 'general'} (Click exit handled safely)"
    except click.ClickException as e:
        return f"Help for {target or 'general'} (Click error handled safely): {e}"
    except Exception as e:
        return f"Help for {target or 'general'} (Error handled safely): {e}"
