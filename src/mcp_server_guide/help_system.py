"""Help system for MCP server."""

from .logging_config import get_logger

logger = get_logger()


async def format_guide_help() -> str:
    """Format comprehensive help content for the guide system."""
    from .naming import MCP_GUIDE_VERSION

    help_sections = []

    help_sections.append(f"""# MCP Server Guide Help

**Version:** {MCP_GUIDE_VERSION}
**Description:** Developer guidelines and project rules MCP server

This server provides access to project documentation, categories, collections, and development guidelines through MCP prompts, tools, and resources.""")

    try:
        from .tools import list_prompts

        prompts_result = await list_prompts()
        if prompts_result.get("success"):
            prompts = prompts_result.get("prompts", [])
            if prompts:
                help_sections.append("")
                help_sections.append("## Available Prompts")
                for prompt in prompts:
                    args = prompt.get("arguments", [])
                    args_info = f" ({', '.join(arg['name'] for arg in args)})" if args else ""
                    help_sections.append(f" - **{prompt['name']}**{args_info}: {prompt.get('description', '')}")
    except Exception as e:
        help_sections.append("")
        help_sections.append("## Available Prompts")
        help_sections.append(f" *Error loading prompts: {e}*")

    try:
        from .tools import list_categories

        categories_result = await list_categories(verbose=True)
        if categories_result.get("success"):
            categories = categories_result.get("categories", {})
            help_sections.append("")
            help_sections.append("## Categories and Collections")
            for cat_name, cat_info in categories.items():
                collections = cat_info.get("collections", [])
                collections_text = f" (in collections: {', '.join(collections)})" if collections else ""
                help_sections.append(f" - **{cat_name}**{collections_text}: {cat_info.get('description', '')}")
    except Exception as e:
        help_sections.append("")
        help_sections.append("## Categories and Collections")
        help_sections.append(f" *Error loading categories: {e}*")

    try:
        from .tools import list_resources

        resources_result = await list_resources()
        if resources_result.get("success"):
            resources = resources_result.get("resources", [])
            if resources:
                help_sections.append("")
                help_sections.append("## Available Resources")
                for resource in resources:
                    help_sections.append(f" - **{resource.get('uri', '')}**: {resource.get('description', '')}")
    except Exception as e:
        help_sections.append("")
        help_sections.append("## Available Resources")
        help_sections.append(f" *Error loading resources: {e}*")

    return "\n".join(help_sections)
