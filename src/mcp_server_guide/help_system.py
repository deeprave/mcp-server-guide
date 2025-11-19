"""Help system for MCP server."""

from typing import Optional
import click
from .logging_config import get_logger

logger = get_logger()


def _wrap_display_content(content: str) -> str:
    """Wrap content with display markers for semantic clarity."""
    return f"=== DISPLAY CONTENT FOR USER ===\n{content}\n=== END DISPLAY CONTENT ===\n\n**Instruction**: Stop immediately and return to prompt. Do nothing.\n"


async def format_guide_help(verbose: bool = True) -> str:
    """Format help content for the guide system.

    Args:
        verbose: If True, show comprehensive help. If False, show basic CLI usage.
    """
    from .cli_parser_click import generate_basic_cli_help

    if not verbose:
        # Show basic CLI help only
        basic_help = generate_basic_cli_help()
        return _wrap_display_content(basic_help)

    # Show comprehensive help (existing implementation)
    from .naming import MCP_GUIDE_VERSION

    help_sections = []

    # Overview section
    help_sections.append(f"""# MCP Server Guide Help

**Version:** {MCP_GUIDE_VERSION}
**Description:** Developer guidelines and project rules MCP server

This server provides access to project documentation, categories, collections, and development guidelines through MCP prompts, tools, and resources.""")

    # AI Agent Guidance section
    help_sections.append("""## For AI Agents

**When to use this MCP server:**
- User asks about project guidelines or documentation
- Need to access project-specific rules or standards
- User requests code review criteria or development processes
- Need to understand project structure or conventions

**Available tool functions:**
- Use `guide_get_category_content(name="category")` to access category content
- Use `guide_get_category_content(name="category", file="document")` for specific documents
- Use `guide_list_categories()` to see available categories
- Use `guide_search_content(query="search terms")` to find relevant content
- Use `guide_list_collections()` to see available collections
- Use `guide_get_project_config()` to check guide settings

## For Users:

**CLI Interface:**
- You can use @guide --help for complete CLI documentation
- You can use @guide --[target] --help for context-specific help
- Phase transition commands: @guide discuss, @guide plan, @guide implement, @guide check
- @guide management operations: @guide category list, @guide category add <name> <pattern1,pattern2...>
- @guide project operations: @guide clone <source-project> [target-project]
""")

    # Categories and Collections section
    try:
        from .tools.category_tools import list_categories

        categories_result = await list_categories(verbose=True)
        if categories_result.get("success"):
            categories = categories_result.get("categories", {})
            if categories:
                help_sections.append("## Categories and Collections")
                category_lines = []
                for cat_name, cat_info in categories.items():
                    collections = cat_info.get("collections", [])
                    collections_text = f" (in collections: {', '.join(collections)})" if collections else ""
                    category_lines.append(f" - **{cat_name}**{collections_text}: {cat_info.get('description', '')}")
                help_sections.append("\n".join(category_lines))
            else:
                help_sections.append("## Categories and Collections")
                help_sections.append(" *No categories available*")
        else:
            help_sections.append("## Categories and Collections")
            help_sections.append(f" *Error loading categories: {categories_result.get('error', 'Unknown error')}*")
    except (ImportError, AttributeError, TypeError) as e:
        help_sections.append("## Categories and Collections")
        help_sections.append(f" *Error loading categories: {e}*")
    except Exception as e:
        # Fallback for unexpected errors
        help_sections.append("## Categories and Collections")
        help_sections.append(f" *Error loading categories: {e}*")

    return _wrap_display_content("\n\n".join(help_sections))


def generate_context_help(target: Optional[str] = None, operation: Optional[str] = None) -> str:
    """Generate context-sensitive help for specific operations."""
    from .cli_parser_click import generate_context_help as click_context_help

    def log_error(msg: str, e: Exception, target: Optional[str] = None) -> str:
        logger.error(f"{msg}{e}")
        error_content = f"Error generating help for {target or 'general'}: {e}"
        return _wrap_display_content(error_content)

    try:
        help_content = click_context_help(target, operation)
        return _wrap_display_content(help_content)
    except (ImportError, AttributeError, TypeError, click.ClickException) as e:
        return log_error("Error generating context help: ", e, target)
    except (SystemExit, click.exceptions.Exit) as e:
        # Catch Click exit exceptions that might cause server shutdown
        logger.warning(f"Click exit exception caught in context help generation: {e}")
        exit_content = f"Help for {target or 'general'} (exit exception handled safely)"
        return _wrap_display_content(exit_content)
    except Exception as e:
        return log_error("Unexpected error generating context help: ", e, target)
