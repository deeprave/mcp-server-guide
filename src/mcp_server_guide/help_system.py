"""Help system for MCP server."""

from typing import Optional
import click
from .logging_config import get_logger

logger = get_logger()


async def format_guide_help() -> str:
    """Format comprehensive help content for the guide system."""
    from .naming import MCP_GUIDE_VERSION
    from .cli_parser_click import generate_cli_help

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

**How to interact effectively:**
- Use @guide [category] for broad topic areas
- Use @guide [category/document] for specific documents
- Use guide://help resource for complete server capabilities
- Check available categories first with list operations

**CLI Interface:**
- Use @guide --help for complete CLI documentation
- Use @guide --[target] --help for context-specific help
- Phase commands: @guide discuss, @guide plan, @guide implement, @guide check
- CRUD operations: @guide category list, @guide category add name patterns""")

    # Auto-generated CLI Help section
    help_sections.append("## Complete CLI Interface")
    try:
        cli_help = generate_cli_help()
        help_sections.append(f"```\n{cli_help}\n```")
    except (ImportError, AttributeError, TypeError) as e:
        help_sections.append(f"*Error generating CLI help: {e}*")
    except (SystemExit, click.exceptions.Exit):
        # Catch Click exit exceptions that might cause server shutdown
        help_sections.append("*CLI help generation handled safely (Click exit caught)*")
    except Exception as e:
        # Fallback for unexpected errors
        help_sections.append(f"*Error generating CLI help: {e}*")

    # Available Prompts section
    try:
        from .tools.prompt_tools import list_prompts

        prompts_result = await list_prompts()
        if prompts_result.get("success"):
            prompts = prompts_result.get("prompts", [])
            if prompts:
                help_sections.append("## Available Prompts")
                for prompt in prompts:
                    args = prompt.get("arguments", [])
                    args_info = f" ({', '.join(arg['name'] for arg in args)})" if args else ""
                    help_sections.append(f" - **{prompt['name']}**{args_info}: {prompt.get('description', '')}")
            else:
                help_sections.append("## Available Prompts")
                help_sections.append(" *No prompts available*")
        else:
            help_sections.append("## Available Prompts")
            help_sections.append(f" *Error loading prompts: {prompts_result.get('error', 'Unknown error')}*")
    except (ImportError, AttributeError, TypeError) as e:
        help_sections.append("## Available Prompts")
        help_sections.append(f" *Error loading prompts: {e}*")
    except Exception as e:
        # Fallback for unexpected errors
        help_sections.append("## Available Prompts")
        help_sections.append(f" *Error loading prompts: {e}*")

    # Categories and Collections section
    try:
        from .tools.category_tools import list_categories

        categories_result = await list_categories(verbose=True)
        if categories_result.get("success"):
            categories = categories_result.get("categories", {})
            if categories:
                help_sections.append("## Categories and Collections")
                for cat_name, cat_info in categories.items():
                    collections = cat_info.get("collections", [])
                    collections_text = f" (in collections: {', '.join(collections)})" if collections else ""
                    help_sections.append(f" - **{cat_name}**{collections_text}: {cat_info.get('description', '')}")
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

    # Resources section
    help_sections.append("""## Available Resources

Access project content through these guide:// resources:

- **guide://help** - This comprehensive help documentation
- **guide://category/[name]** - Content from specific categories
- **guide://collection/[name]** - Content from specific collections

### Resource Access Patterns

```
# Access category content
guide://category/architecture
guide://category/coding-standards

# Access collection content
guide://collection/backend-docs
guide://collection/frontend-guides
```""")

    # Context-Sensitive Help section
    help_sections.append("""## Context-Sensitive Help

Get targeted help for specific operations:

```bash
# General help
@guide --help

# Target-specific help
@guide category --help
@guide collection --help
@guide document --help

# Operation-specific help
@guide category add --help
@guide collection list --help
```""")

    # Troubleshooting section
    help_sections.append("""## Troubleshooting

### Common Issues

**"Category not found"**
- Check available categories with: `@guide category list`
- Verify category name spelling and case

**"No content found"**
- Ensure category has valid patterns
- Check if files exist in the specified paths
- Use `@guide category list --verbose` for detailed info

**"Permission denied"**
- Verify file permissions in project directories
- Check if paths are accessible to the MCP server

### Debug Commands

```bash
# List all available categories
@guide category list --verbose

# Check specific category content
@guide [category-name]

# View server status
@guide status
```""")

    return "\n\n".join(help_sections)


def generate_context_help(target: Optional[str] = None, operation: Optional[str] = None) -> str:
    """Generate context-sensitive help for specific operations."""
    from .cli_parser_click import generate_context_help as click_context_help
    import click

    try:
        return click_context_help(target, operation)
    except (ImportError, AttributeError, TypeError, click.ClickException) as e:
        logger.error(f"Error generating context help: {e}")
        return f"Error generating help for {target or 'general'}: {e}"
    except (SystemExit, click.exceptions.Exit) as e:
        # Catch Click exit exceptions that might cause server shutdown
        logger.warning(f"Click exit exception caught in context help generation: {e}")
        return f"Help for {target or 'general'} (exit exception handled safely)"
    except Exception as e:
        # Fallback for unexpected errors
        logger.error(f"Unexpected error generating context help: {e}")
        return f"Error generating help for {target or 'general'}: {e}"
